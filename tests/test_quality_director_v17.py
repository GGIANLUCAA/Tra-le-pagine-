"""Regression tests: safety, category routing, real MP4, no paid calls."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import quality_director_v17 as qa


class QualityDirectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        (self.base/'assets').mkdir()
        Image.new('RGB',(1600,2200),(130,80,35)).save(self.base/'assets'/'scene.jpg')
        (self.base/'script.txt').write_text('Il protagonista cammina al fiume.',encoding='utf-8')
        self.file = self.base/'PROJECT_V13.json'

    def project(self,**override):
        data={'schema':'video-project-v13','format':'libri','script':'script.txt',
              'assets':[{'id':'scene1','role':'visual','file':'assets/scene.jpg','rights':'verificati'}],
              'scenes':[{'asset_id':'scene1','description':'Il protagonista cammina verso il fiume al tramonto',
                         'reason':'La scena illustra il viaggio','narration_anchor':'Il protagonista cammina al fiume.'}]}
        data.update(override)
        self.file.write_text(json.dumps(data),encoding='utf-8')

    def test_no_cost_and_no_auto_certification(self):
        self.project()
        r=qa.inspect(project=self.file,out=self.base/'result')
        self.assertEqual(r['status'],'needs_artistic_review')
        self.assertEqual(r['paid_calls'],0)
        self.assertFalse(r['published'])
        self.assertTrue((self.base/'result'/'QUALITY_REVIEW_V17.html').is_file())

    def test_duplicate_and_missing_anchor_are_warnings(self):
        self.project(scenes=[{'asset_id':'scene1','description':'La scena iniziale mostra il fiume','reason':'Scena di apertura'},
                             {'asset_id':'scene1','description':'Il protagonista continua a camminare','reason':'Segue il viaggio',
                              'narration_anchor':'Il protagonista cammina al fiume.'}])
        r=qa.inspect(project=self.file,out=self.base/'warnings')
        codes={n['code'] for n in r['warnings']}
        self.assertIn('MISSING_ANCHOR',codes)
        self.assertIn('SIMILAR_ADJACENT_SCENES',codes)
        self.assertFalse(r['blocking'])

    def test_unsafe_path_is_rejected(self):
        self.project(script='../private.txt',assets=[{'id':'p','file':'../secret.jpg','role':'visual'}])
        r=qa.inspect(project=self.file,out=self.base/'unsafe')
        self.assertIn('UNSAFE_SCRIPT_PATH',[x['code'] for x in r['blocking']])
        self.assertIn('UNSAFE_ASSET_PATH',[x['code'] for x in r['warnings']])

    def test_html_escapes_user_text(self):
        report={'format':'<script>alert(1)</script>','status':'needs_artistic_review','blocking':[],
                'warnings':[{'code':'x','message':'<img onerror=alert(1)>'}],
                'artistic_review_questions':['<script>']}
        page=qa.render_html(report,self.base)
        self.assertNotIn('<script>',page)
        self.assertIn('&lt;script&gt;',page)
        self.assertIn('viewport',page)

    def test_all_six_format_profiles(self):
        policy=json.loads((ROOT/'config'/'quality_director_v17.json').read_text(encoding='utf-8'))
        self.assertEqual(set(policy['formats']),{'libri','artvision_cinema','artvision_critico','controluce','visual_music','hyperlumen'})

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg/ffprobe missing')
    def test_real_video_and_black_preview(self):
        self.project()
        v=self.base/'test.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=white:s=720x1280:r=5',
                        '-f','lavfi','-i','sine=frequency=440:sample_rate=16000','-t','2',
                        '-c:v','mpeg4','-q:v','15','-c:a','aac','-y',str(v)],check=True,timeout=40)
        out=self.base/'video_report'
        out.mkdir()
        Image.new('RGB',(270,480),(0,0,0)).save(out/'REVIEW_FRAME_00.jpg')
        result=qa.inspect(video=v,project=self.file,out=out)
        self.assertFalse(result['blocking'])
        self.assertIn('DARK_SAMPLES',[x['code'] for x in result['warnings']])
        self.assertTrue(any('long_silences_detected' in row for row in result['findings']))
        self.assertTrue((out/'QUALITY_REPORT_V17.json').is_file())


if __name__ == '__main__':
    unittest.main()
