import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from artvision_next_render_v55 import choose

class ArtVisionNextRenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'queue').mkdir()
        self.variants={
          'critico_standard':{'status':'blocked'},
          'critico_museum':{'status':'blocked'},
          'cinema_standard':{'status':'rendered_needs_review'},
          'cinema_museum':{'status':'rendered_needs_review'}}
        self.write([])

    def tearDown(self):self.tmp.cleanup()

    def write(self,items):
        (self.root/'queue/production_v15.json').write_text(json.dumps({'items':items}))
        (self.root/'queue/artvision_four_variants_s01_20261028.json').write_text(
            json.dumps({'groups':[{'group_id':'existing_work','variants':self.variants}]}))

    def test_all_cinema_rendered_requires_new_work_not_more_critico_audits(self):
        data=choose(self.root)
        self.assertEqual(data['status'],'new_artwork_preparation_required')
        self.assertTrue(data['new_artwork_required'])
        self.assertEqual(len(data['blockers']),2)
        self.assertTrue(all(b['reason']=='verified_gacrux_cache_required' for b in data['blockers']))

    def test_missing_museum_renderer_does_not_make_fake_job(self):
        self.variants['cinema_museum']={'status':'planned'}
        self.write([])
        data=choose(self.root)
        self.assertEqual(data['status'],'missing_cinema_input_or_renderer')
        self.assertFalse(data['new_artwork_required'])
        self.assertEqual([b['reason'] for b in data['blockers'] if b['variant']=='cinema_museum'],['no_verified_generic_museum_renderer'])

    def test_existing_queue_keeps_only_one_production_owner(self):
        self.write([{'id':'existing_job'}])
        data=choose(self.root)
        self.assertEqual(data['status'],'existing_jobs_take_priority')
        self.assertEqual(data['count'],1)

if __name__=='__main__': unittest.main()
