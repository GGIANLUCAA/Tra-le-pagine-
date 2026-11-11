"""Offline tests: scene meaning, timing, safety and unmodified sources."""
import copy, hashlib, json, shutil, sys, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from narrative_reveal_director_v3 import plan, roi_check
from narrative_reveal_renderer_v3 import render_scene

BASE={'schema':'narrative-reveal-story-v3','format':'libri','title':'Test',
 'scenes':[
 {'id':'inizio','start_s':0,'end_s':7,'intent':'hook',
  'narration_anchor':'Era già notte','anchor_offset_s':.8,'visual_reason':'Contesto immediato',
  'visual_mode':'illustration','rights_review':'approved','visual_review':'approved'},
 {'id':'indizio','start_s':7,'end_s':15,'intent':'indizio',
  'narration_anchor':'La chiave','anchor_offset_s':2.5,'visual_reason':'Evidenziare solo la chiave',
  'visual_mode':'illustration','focus_roi':[.2,.3,.4,.4],
  'rights_review':'approved','visual_review':'approved'},
 {'id':'finale','start_s':15,'end_s':25,'intent':'finale',
  'narration_anchor':'Tutto si fermò','anchor_offset_s':1.,'visual_reason':'Pausa conclusiva',
  'visual_mode':'illustration','rights_review':'approved','visual_review':'approved'}]}

class NarrativeV3(unittest.TestCase):
    def test_narrative_choices(self):
        p=plan(copy.deepcopy(BASE))
        self.assertEqual([s['effect'] for s in p['scenes']],['none','color_accent','none'])
        self.assertFalse(p['can_claim_voice_sync'])
        self.assertFalse(p['global_effect_rule'])
        self.assertGreater(p['scenes'][1]['effect_start_s'],0)
        self.assertGreater(p['scenes'][1]['visible_hold_s'],2)
        self.assertEqual(p['api_calls'],0)

    def test_missing_roi_falls_back(self):
        s=copy.deepcopy(BASE);s['scenes'][1].pop('focus_roi')
        self.assertEqual(plan(s)['scenes'][1]['effect'],'none')

    def test_authentic_art_is_not_repainted(self):
        s=copy.deepcopy(BASE);s['format']='artvision_cinema'
        s['scenes'][1]['effect_override']='director_mix'
        self.assertTrue(all(row['effect']=='none' for row in plan(s)['scenes']))

    def test_invalid_cues_and_roi(self):
        s=copy.deepcopy(BASE);s['scenes'][1]['start_s']=3
        with self.assertRaises(ValueError):plan(s)
        s=copy.deepcopy(BASE);s['scenes'][1]['focus_roi']=[.3,.3,float('nan'),.2]
        with self.assertRaises(ValueError):plan(s)
        self.assertFalse(roi_check([.8,.8,.4,.3]))

    def test_short_scene_does_not_force_effect(self):
        s=copy.deepcopy(BASE)
        s['scenes'][1]['end_s']=8.3
        s['scenes'][1]['anchor_offset_s']=.5
        s['scenes'][2]['start_s']=8.3
        self.assertEqual(plan(s)['scenes'][1]['effect'],'none')

    def test_storyboard_mock_is_not_rights_approval(self):
        s=copy.deepcopy(BASE);s['scenes'][1]['visual_review']='editorial_mock'
        p=plan(s)
        self.assertEqual(p['scenes'][1]['effect'],'color_accent')
        self.assertFalse(p['scenes'][1]['rights_and_visuals_ready'])

    @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg not installed')
    def test_only_single_still_and_no_master_changes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'src.png'
            image=Image.new('RGB',(180,320),(251,248,241))
            d=ImageDraw.Draw(image)
            d.ellipse((27,88,98,160),fill='#d2ae85',outline='#333c4c',width=4)
            image.save(source)
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            p=plan(copy.deepcopy(BASE))
            p['scenes'][1].update(duration_s=2.4,effect_start_s=.3,effect_duration_s=1.)
            plan_path=root/'plan.json';plan_path.write_text(json.dumps(p))
            out=root/'preview.mp4'
            report=render_scene(plan_path,'indizio',source,out,width=180,height=320,fps=12)
            self.assertEqual(report['effect_applied'],'color_accent')
            self.assertEqual(report['ai_api_calls'],0)
            self.assertTrue(out.stat().st_size>1000)
            self.assertEqual(digest,hashlib.sha256(source.read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):
                render_scene(plan_path,'indizio',source,out,width=180,height=320,fps=12)

    @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg not installed')
    def test_dark_image_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'dark.png'
            Image.new('RGB',(180,320),(19,30,47)).save(source)
            s=copy.deepcopy(BASE);s['scenes'][1]['effect_override']='director_mix'
            p=plan(s)
            p['scenes'][1].update(duration_s=.5,effect_start_s=0,effect_duration_s=.4)
            f=root/'plan.json';f.write_text(json.dumps(p))
            r=render_scene(f,'indizio',source,root/'preview.mp4',width=180,height=320,fps=12)
            self.assertEqual(r['effect_applied'],'none')
            self.assertTrue(r['safety_fallback'])

if __name__=='__main__':unittest.main()
