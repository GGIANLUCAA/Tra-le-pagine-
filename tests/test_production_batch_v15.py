import copy
import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import production_batch_v15 as b
from video_director_v13 import capture,write_json

class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.p=patch.object(b,'ROOT',self.root);self.p.start()
        self.ledger={'schema':'production-ledger-v15','deliveries':[]}
        (self.root/'project.json').write_text('{}')
    def tearDown(self):self.p.stop();self.tmp.cleanup()
    def item(self,n=0):return dict(id=f'job-{n}',content_key=f'original-{n}',project_file='project.json',status='prepared',attempts=0,new_paid_calls_required=False)
    def queue(self,rows):return {'schema':'production-queue-v15','items':rows}
    def test_target_reserves_parallelism_and_empty_is_not_success(self):
        r=b.plan(self.queue([]),self.ledger,'2026-10-22')
        self.assertEqual(r['missing_to_target'],10);self.assertFalse(r['target_met'])
        with patch.object(b,'check',return_value={'blockers':[]}):
            r=b.plan(self.queue([self.item(i) for i in range(20)]),self.ledger,'2026-10-22')
        self.assertEqual(len(r['ready']),12);self.assertEqual(r['max_parallel_renders'],3)
    def test_unready_paid_duplicate_and_exhausted_not_dispatched(self):
        items=[self.item(i) for i in range(4)]
        items[0]['status']='preparing';items[1]['new_paid_calls_required']=None
        items[2]['attempts']=2;items[3]['content_key']=items[0]['content_key']
        with patch.object(b,'check',return_value={'blockers':[]}):r=b.plan(self.queue(items),self.ledger,'2026-10-22')
        self.assertEqual(len(r['ready']),0);self.assertEqual(len(r['blocked']),4)
    def test_ids_and_paths(self):
        with self.assertRaises(ValueError):b.plan(self.queue([self.item(),self.item()]),self.ledger,'2026-10-22')
        with self.assertRaises(ValueError):b.local('../outside')
        with patch.object(b,'check',return_value={'blockers':['missing scene']}):r=b.plan(self.queue([self.item()]),self.ledger,'2026-10-22')
        self.assertIn('missing scene',r['blocked'][0]['blockers'])
    def test_receipt_requires_real_media_reviews_and_matching_recipe(self):
        out=self.root/'delivery';out.mkdir()
        video=out/'video.mp4';cover=out/'cover.jpg'
        subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','color=size=180x320:rate=10','-f','lavfi','-i','sine=frequency=440:sample_rate=24000','-t','1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(video)],check=True)
        Image.new('RGB',(180,320)).save(cover)
        capture('libri','Test di collaudo',video,cover,out)
        receipt=dict(item_id='one',content_key='unique',day='2026-10-22',video_file='delivery/video.mp4',recipe_file='delivery/VIDEO_RECIPE_V13.json',reviews={k:{'status':'passed','notes':'Test fixture, non consegna reale'} for k in b.REVIEWS})
        bad=copy.deepcopy(receipt);bad['reviews']['audio']['status']='pending'
        with self.assertRaises(ValueError):b.record(self.ledger,bad)
        result=b.record(self.ledger,receipt)
        self.assertEqual(b.plan(self.queue([]),result,'2026-10-22')['qualified_today'],1)
        self.assertEqual(b.plan(self.queue([]),result,'2026-10-23')['qualified_today'],0)
        with self.assertRaises(ValueError):b.record(result,{**receipt,'item_id':'two','content_key':'another'})
        video.write_bytes(b'invalid changed file')
        report=b.plan(self.queue([]),result,'2026-10-22')
        self.assertEqual(report['qualified_today'],0);self.assertEqual(report['stale_receipts'],['one'])
    def test_malformed_receipts_do_not_count(self):
        r=b.plan(self.queue([]),{'schema':'production-ledger-v15','deliveries':[{},None]},'2026-10-22')
        self.assertEqual(r['qualified_today'],0)
        self.assertEqual(len(r['stale_receipts']),2)
