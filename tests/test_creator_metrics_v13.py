import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from creator_metrics_v13 import analyze

class MetricsTests(unittest.TestCase):
    def row(self, **changes):
        return dict(video_id='one', platform='youtube', account='mine',format='critico',window_days=7,
          view_definition='views_native',source='studio-export',observed_at='2026-10-21',
          views=100,watch_seconds=1000,net_receipts_eur=20,cash_cost_eur=5,hours=2,**changes)
    def test_missing_is_not_zero_and_margin_is_not_profit(self):
        report=analyze({'schema':'creator-observations-v13','observations':[self.row()]})
        row=report['observations'][0]
        self.assertEqual(row['contribution_per_hour_eur'],7.5)
        self.assertIn('orders',row['missing'])
        self.assertIsNone(report['revenue_forecast'])
    def test_duplicate_rejected_and_windows_separate(self):
        r=self.row()
        with self.assertRaises(ValueError):analyze({'schema':'creator-observations-v13','observations':[r,r]})
        second={**r,'window_days':28}
        self.assertEqual(len(analyze({'schema':'creator-observations-v13','observations':[r,second]})['cohorts']),2)
    def test_unknown_zero_and_invalid(self):
        for value in (float('nan'),-1,True,'100'):
            with self.assertRaises(ValueError):analyze({'schema':'creator-observations-v13','observations':[{**self.row(),'views':value}]})
        r={**self.row(),'views':0,'hours':0,'net_receipts_eur':None}
        d=analyze({'schema':'creator-observations-v13','observations':[r]})['observations'][0]
        self.assertIsNone(d['avg_watch_seconds']);self.assertIsNone(d['cash_contribution_eur'])
    def test_different_denominators_never_ranked_together(self):
        r=self.row();s={**r,'video_id':'two','view_definition':'engaged_views'}
        report=analyze({'schema':'creator-observations-v13','observations':[r,s]})
        self.assertEqual(len(report['cohorts']),2)
        self.assertTrue(all(c['decision']=='raccolta_dati' for c in report['cohorts']))
