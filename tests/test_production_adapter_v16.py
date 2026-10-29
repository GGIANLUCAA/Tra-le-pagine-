import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import production_adapter_v16 as a
import gemini_voice as voice

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.p=patch.object(a,'ROOT',self.root);self.p.start()
    def tearDown(self):self.p.stop();self.tmp.cleanup()
    def test_voice_cache_exact_hash_text_and_alignment_required(self):
        cache=self.root/'cache';cache.mkdir();out=self.root/'out';script='Test tecnico.'
        sf.write(cache/'VOCE.wav',np.zeros(24000,dtype='float32'),24000)
        # Synthetic fixture is for cache integrity only, not a Google voice claim.
        entry={'cache_key':voice.cache_key(script),'wav_sha256':voice._sha(cache/'VOCE.wav'),'timed':[[script,0,1]],'alignment':{'method':'fixture_only'}}
        (cache/'VOICE_CACHE_V13.json').write_text(json.dumps(entry))
        a.cache(script,'cache',out)
        self.assertEqual((out/'VOCE.wav').read_bytes(),(cache/'VOCE.wav').read_bytes())
        with self.assertRaises(ValueError):a.cache('Changed text.','cache',self.root/'bad')
        entry['timed']=None;(cache/'VOICE_CACHE_V13.json').write_text(json.dumps(entry))
        with self.assertRaises(ValueError):a.cache(script,'cache',self.root/'bad')
    def test_format_mismatch_and_unapproved_adapter(self):
        p=self.root/'project.json';p.write_text(json.dumps({'format':'libri','assets':[]}))
        with self.assertRaises(ValueError):a.execute({'adapter':'critico_v2_prepared','project_file':'project.json'},self.root/'out')
        with self.assertRaises(ValueError):a.execute({'adapter':'run_arbitrary_command'},self.root/'out')
    def test_serial_4x1_cannot_bypass_preflight_at_adapter(self):
        group=self.root/'group';variant=group/'cinema_standard'
        variant.mkdir(parents=True)
        (group/'ARTVISION_4X1_PLAN.json').write_text('{}')
        (variant/'project.json').write_text(json.dumps({
            'format':'artvision_cinema','assets':[],
            'serial_mode':'artvision_4x1',
            'artvision_4x1_plan':'../ARTVISION_4X1_PLAN.json'}))
        # Isolate the V13 gate in this unit test; actual production keeps the pilot lock.
        with patch('artvision_pilot_guard_v58.enforce_pilot_project'):
            with patch.object(a,'check_project',return_value={
                'ready':False,'blockers':['Storyboard emotivo non compilato']
            }) as preflight:
                with patch.object(a.subprocess,'run') as renderer:
                    with self.assertRaisesRegex(ValueError,'ArtVision 4x1 preflight'):
                        a.execute({'adapter':'cinema_v6_vangogh_prepared',
                                   'project_file':'group/cinema_standard/project.json'},
                                  self.root/'out')
                    renderer.assert_not_called()
                    preflight.assert_called_once()

    def test_script_mismatch_before_any_renderer(self):
        ep=self.root/'episodes/test';ep.mkdir(parents=True);(ep/'testo.txt').write_text('Actual words.')
        (self.root/'script.txt').write_text('Other words.')
        (self.root/'project.json').write_text(json.dumps({'format':'libri','assets':[],'script':'script.txt'}))
        with patch.object(a.subprocess,'run') as execute:
            with self.assertRaises(ValueError):a.execute({'adapter':'books_gemini_cache','project_file':'project.json','episode':'test'},self.root/'out')
        execute.assert_not_called()


class PreparedCinemaV55Tests(unittest.TestCase):
    """Synthetic fixtures prove the offline mechanism, never an art deliverable."""
    def setUp(self):
        from PIL import Image, ImageDraw
        import subprocess
        import artvision_cinema_prepared_v55 as cinema
        self.cinema=cinema
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.assets=self.root/'assets'
        self.assets.mkdir()
        self.image=self.assets/'authentic-fixture.jpg'
        im=Image.new('RGB',(1400,1000),'#3a4d57')
        draw=ImageDraw.Draw(im)
        for i in range(6):
            draw.ellipse((i*160+50,80,i*160+190,520),fill=(90+i*20,70+i*10,115))
        im.save(self.image)
        self.music=self.assets/'music.wav'
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',
                        '-f','lavfi','-i','sine=frequency=440:duration=8',
                        '-c:a','pcm_s16le',str(self.music)],check=True,timeout=30)
        ref=lambda p:{'file':p.name,'sha256':cinema.sha256(p)}
        self.plan={
            'schema':cinema.SCHEMA,'variant':'cinema_standard',
            'title':'An Example Artwork','artist':'Example Artist',
            'music':{**ref(self.music),'license':'CC0','recording_title':'Fixture test tone',
                     'recording_artist':'FFmpeg fixture','source_url':'https://example.org/test',
                     'license_url':'https://creativecommons.org/publicdomain/zero/1.0/'},
            'shots':[{**ref(self.image),'duration_seconds':1.5,
                      'mode':'detail' if i<3 else 'whole',
                      'focus':[0.2+i*.2,0.2+i*.2],
                      'purpose':'Distinct synthetic scene for technical render number '+str(i),
                      'detail_id':'fixture-detail-'+str(i)} for i in range(4)]}
        self.approved={self.image.resolve(),self.music.resolve()}

    def tearDown(self):
        self.tmp.cleanup()

    def test_generic_renderer_rejects_fake_museum_missing_rights_and_bad_hash(self):
        from copy import deepcopy
        for mutate in (
            lambda p:p.update(variant='cinema_museum'),
            lambda p:p['music'].update(license='unknown'),
            lambda p:p['shots'][0].update(sha256='0'*64),
            lambda p:p['shots'][1].update(purpose='zoom'),
            lambda p:p['shots'][1].update(file='../outside.jpg'),
        ):
            candidate=deepcopy(self.plan)
            mutate(candidate)
            with self.assertRaises(ValueError):
                self.cinema.validate(candidate,self.assets,self.approved)

    def test_real_six_second_h264_aac_render_and_full_decode(self):
        import subprocess
        video,cover=self.cinema.render(self.plan,self.assets,self.approved,self.root/'out')
        self.assertTrue(video.is_file() and cover.is_file())
        self.assertGreater(video.stat().st_size,100000)
        probe=subprocess.check_output(['ffprobe','-v','error','-show_entries',
                                       'stream=codec_name,width,height','-of','json',str(video)])
        streams=json.loads(probe)['streams']
        self.assertTrue(any(s.get('codec_name')=='h264' and s.get('width')==1080 and s.get('height')==1920 for s in streams))
        self.assertTrue(any(s.get('codec_name')=='aac' for s in streams))
        subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(video),'-f','null','-'],
                       check=True,timeout=120)
        with self.assertRaisesRegex(ValueError,'exists'):
            self.cinema.render(self.plan,self.assets,self.approved,self.root/'out')

    def test_runner_prepared_cinema_requires_no_fake_gacrux_cache(self):
        import production_runner_v16 as runner
        project=self.root/'project'
        project.mkdir()
        (project/'art.jpg').write_bytes(self.image.read_bytes())
        (project/'music.wav').write_bytes(self.music.read_bytes())
        (project/'PROJECT_V13.json').write_text(json.dumps({
            'format':'artvision_cinema',
            'assets':[{'file':'art.jpg'},{'file':'music.wav'}]}))
        (self.assets/'plan.json').write_text(json.dumps(self.plan))
        with patch.object(runner,'ROOT',self.root):
            files=runner.inputs({'adapter':'cinema_v55_prepared',
                                 'project_file':'project/PROJECT_V13.json',
                                 'assets_dir':'assets','cinema_plan_file':'assets/plan.json'})
        self.assertIn(self.assets/'plan.json',files)
        self.assertNotIn(self.root/'missing_gacrux_cache',files)
