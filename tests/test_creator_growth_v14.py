import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from creator_growth_v14 import plan,ROOT
from creator_metrics_v13 import analyze

class GrowthTests(unittest.TestCase):
    def ideas(self):return json.loads((ROOT/'templates/CREATOR_IDEAS_V14.json').read_text())
    def test_capacity_research_and_no_publication(self):
        r=plan(self.ideas(),'2026-10-26')
        self.assertEqual(sum(len(w['ideas']) for w in r['calendar']),8)
        for w in r['calendar']:
            self.assertLessEqual(w['estimated_production_minutes']+w['review_minutes'],r['weekly_minutes'])
            self.assertFalse(w['publication_scheduled'])
            self.assertTrue(all(i['stage']=='research_and_preparation' for i in w['ideas']))
    def test_low_capacity_conserves_all_ideas(self):
        r=plan(self.ideas(),'2026-10-26',100)
        self.assertEqual(len(r['deferred']),8)
        self.assertTrue(all(not w['ideas'] for w in r['calendar']))
    def test_invalid_time_horizon_and_budget(self):
        for v in (0,-1,True,float('inf'),45):
            with self.assertRaises(ValueError):plan(self.ideas(),'2026-10-26',v)
        for v in (0,13,True):
            with self.assertRaises(ValueError):plan(self.ideas(),'2026-10-26',weeks=v)
    def test_duplicates_and_unknown_estimates_not_scheduled(self):
        data=self.ideas();dup=copy.deepcopy(data['ideas'][0]);dup['id']='duplicate'
        data['ideas'].append(dup);data['ideas'][1]['estimated_minutes']=None
        r=plan(data,'2026-10-26')
        self.assertTrue(any(x['id']=='duplicate' for x in r['deferred']))
        self.assertTrue(any(x['id']=='libri-01' for x in r['deferred']))
    def test_inactive_format_and_multi_variable_rejected(self):
        data=self.ideas();data['ideas'][0]['format']='hyperlumen'
        r=plan(data,'2026-10-26');self.assertTrue(any(x['id']=='critico-01' for x in r['deferred']))
        data=self.ideas();data['ideas'][0]['experiment']['variable']=['opening','cover']
        with self.assertRaises(ValueError):plan(data,'2026-10-26')
    def test_growth_metrics_missing_and_replay(self):
        row=dict(video_id='one',platform='youtube',account='mine',format='libri',window_days=7,
                 view_definition='engaged_views',source='export',observed_at='2026-10-21',views=100,
                 followers_gained=2,shares=3,video_seconds=10,watch_seconds=1200)
        result=analyze({'schema':'creator-observations-v13','observations':[row]})['observations'][0]
        self.assertEqual(result['followers_per_1000_views'],20)
        self.assertEqual(result['average_watch_fraction'],1.2)
        self.assertIn('saves',result['missing'])
