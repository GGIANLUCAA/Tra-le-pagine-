import copy
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import production_runner_v16 as r
import production_batch_v15 as b
from video_director_v13 import write_json

FIXTURE='''import argparse,json,hashlib,subprocess,os
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--job');p.add_argument('--out');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
assert not os.environ.get('GEMINI_API_KEY')
assert not os.environ.get('GITHUB_TOKEN')
v=out/'MASTER.mp4';c=out/'COVER.jpg'
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','color=size=180x320:rate=10','-f','lavfi','-i','sine=frequency=440:sample_rate=24000','-t','1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(v)],check=True)
Image.new('RGB',(180,320)).save(c)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
recipe={'schema':'video-recipe-v13','video':{'file':v.name,'sha256':h(v)},'cover':{'file':c.name,'sha256':h(c)},'sources':[]}
f=out/'VIDEO_RECIPE_V13.json';f.write_text(json.dumps(recipe))
(out/'ADAPTER_RESULT_V16.json').write_text(json.dumps({'video':str(v),'recipe':str(f)}))
'''

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.patches=[patch.object(r,'ROOT',self.root),patch.object(b,'ROOT',self.root)]
        for p in self.patches:p.start()
        (self.root/'src').mkdir();(self.root/'src/production_adapter_v16.py').write_text(FIXTURE)
        (self.root/'prepared').mkdir();Image.new('RGB',(100,100)).save(self.root/'prepared/scene.jpg')
        (self.root/'prepared/script.txt').write_text('Una storia originale.')
        project={'schema':'video-project-v13','format':'libri','topic':'Collaudo tecnico','preset':'narrative-v12-harmonic-v5','subtitles':False,'script':'script.txt',
            'assets':[{'id':'one','file':'scene.jpg','role':'visual','source':'fixture','rights':'fixture'}],
            'scenes':[{'asset_id':'one','description':'Fixture','reason':'Collaudo','narration_anchor':'Una storia originale.'}],
            'reviews':{n:{'status':'passed','notes':'Test fixture'} for n in ('story','visuals','rights')}}
        write_json(self.root/'prepared/project.json',project)
        ep=self.root/'episodes/test';ep.mkdir(parents=True);(ep/'testo.txt').write_text('Una storia originale.')
        cache=self.root/'voice';cache.mkdir();(cache/'VOCE.wav').write_bytes(b'fixture validated separately');(cache/'VOICE_CACHE_V13.json').write_text('{}')
        self.job={'id':'test-one','content_key':'test-original','project_file':'prepared/project.json','status':'prepared','attempts':0,'new_paid_calls_required':False,'adapter':'books_gemini_cache','episode':'test','voice_cache_dir':'voice'}
        self.queue=self.root/'queue.json';self.write_queue([self.job]);self.workspace=self.root/'output/work'
        self.tracked=[self.root/'src/production_adapter_v16.py']
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def write_queue(self,items):write_json(self.queue,{'schema':'production-queue-v15','items':items})
    def run_batch(self,**kwargs):
        with patch.object(r,'tracked_files',return_value=self.tracked):return r.run(self.queue,self.workspace,**kwargs)
    def test_real_subprocess_render_review_pack_restore_idempotency_and_qualification(self):
        with patch.dict(os.environ,{'GEMINI_API_KEY':'not-forwarded','GITHUB_TOKEN':'not-forwarded'}):result=self.run_batch()
        self.assertEqual(result['states']['test-one'],'rendered_needs_review')
        self.assertEqual(result['qualified_today'],0)
        stage=self.workspace/'jobs/test-one/repo/output/final'
        self.assertTrue((stage/'REVIEW_CONTACT.jpg').is_file());self.assertTrue((stage/'REVIEW_AUDIO.mp3').is_file())
        pack_file=stage/'CREATIVE_PACKAGE_V21.json'
        error_file=stage/'CREATIVE_V21_ERROR.txt'
        self.assertTrue(pack_file.is_file(),error_file.read_text() if error_file.is_file() else 'V21 pack absent')
        self.assertTrue((stage/'APERTURA_0_7_V21.jpg').is_file())
        state=json.loads((self.workspace/'state.json').read_text());self.assertEqual(state['jobs']['test-one']['attempts'],1)
        self.assertEqual(self.run_batch()['started'],0)
        archive=self.root/'checkpoint.tar';r.pack(self.workspace,archive)
        import shutil;shutil.rmtree(self.workspace);r.restore(archive,self.workspace)
        self.assertEqual(self.run_batch()['started'],0)
        reviews=self.root/'reviews.json';write_json(reviews,{k:{'status':'passed','notes':'Test fixture review, no artistic claim'} for k in b.REVIEWS})
        requests=self.root/'reviews';requests.mkdir()
        current=r.load_state(self.workspace/'state.json')['jobs']['test-one']
        request={'item_id':'test-one','video_sha256':'wrong','recipe_sha256':current['recipe_sha256'],'reviews':json.loads(reviews.read_text())}
        write_json(requests/'one.json',request)
        self.assertEqual(r.apply_reviews(self.workspace,requests,None)[0]['status'],'not_applied')
        request['video_sha256']=current['video_sha256'];write_json(requests/'one.json',request)
        self.assertEqual(r.apply_reviews(self.workspace,requests,None)[0]['status'],'qualified')
        self.assertEqual(r.apply_reviews(self.workspace,requests,None),[])
        self.assertEqual(self.run_batch()['qualified_today'],1)
        state=json.loads((self.workspace/'state.json').read_text())
        Path(self.root/state['jobs']['test-one']['video_file']).write_bytes(b'changed')
        report=self.run_batch();self.assertEqual(report['started'],0);self.assertTrue(report['runner_blocked'])
    def test_failed_job_isolated_and_attempts_bounded(self):
        second={**self.job,'id':'test-two','content_key':'test-second'};self.write_queue([self.job,second])
        with patch.object(r,'spawn',side_effect=RuntimeError('fixture fail')):
            first=self.run_batch();second_report=self.run_batch();third=self.run_batch()
        self.assertEqual(first['started'],2);self.assertEqual(second_report['started'],2);self.assertEqual(third['started'],0)
    def test_changed_inputs_not_overwritten(self):
        with patch.object(r,'spawn',side_effect=RuntimeError('fixture fail')):self.run_batch()
        (self.root/'episodes/test/testo.txt').write_text('Changed creative input')
        with patch.object(r,'spawn') as spawn:report=self.run_batch()
        spawn.assert_not_called();self.assertTrue(report['runner_blocked'])
    def test_archive_traversal_and_symlink_rejected(self):
        for name,kind in [('../escape',tarfile.REGTYPE),('link',tarfile.SYMTYPE)]:
            target=self.root/'bad.tar'
            with tarfile.open(target,'w') as archive:
                info=tarfile.TarInfo(name);info.type=kind;info.size=0;info.linkname='/tmp/outside';archive.addfile(info,io.BytesIO())
            with self.assertRaises(ValueError):r.restore(target,self.root/'restore')
    def test_newer_durable_state_beats_old_archive(self):
        one=self.root/'old.json';two=self.root/'new.json'
        write_json(one,{'schema':r.SCHEMA,'jobs':{'one':{'status':'failed','attempts':1,'finished_utc':'2026-10-21T08:00:00'}}})
        write_json(two,{'schema':r.SCHEMA,'jobs':{'one':{'status':'rendered_needs_review','attempts':2,'finished_utc':'2026-10-21T09:00:00'}}})
        self.assertEqual(r.load_state(one,two)['jobs']['one']['attempts'],2)
    def test_unknown_adapter_and_escape_rejected(self):
        with self.assertRaises(ValueError):r.inputs({**self.job,'adapter':'arbitrary_shell'})
        with self.assertRaises(ValueError):r.inside('../outside')
