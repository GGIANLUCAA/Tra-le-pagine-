"""Regression checks for V18 prelaunch desk and V13 recipe archive."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import prelaunch_editor_v18 as editor
import creative_memory_v18 as memory


class PrelaunchTests(unittest.TestCase):
    def setUp(self):
        self.old = editor.load(ROOT / 'templates' / 'CREATOR_IDEAS_V14.json')
        self.new = editor.load(ROOT / 'templates' / 'PRELAUNCH_ADDITIONS_V18.json')
        self.lessons = editor.load(ROOT / 'templates' / 'CREATOR_LEARNING_V14.json')

    def test_combines_old_and_new_without_inventing_finished_videos(self):
        result = editor.plan(self.old, self.new, self.lessons)
        self.assertEqual(result['count_original_v14'], 8)
        self.assertEqual(result['count_added_v18'], 16)
        self.assertEqual(result['count_ideas'], 24)
        self.assertEqual(result['count_verified_final_mp4'], 0)
        self.assertEqual(result['count_social_metrics'], 0)
        self.assertEqual(result['count_confirmed_lessons'], 0)
        self.assertTrue(result['zero_paid_api_calls'])
        self.assertFalse(result['published'])
        self.assertTrue(all(x['stage'] in ('idea_to_research','editorial_lab') for x in result['ideas']))

    def test_uses_preexisting_policies_not_false_viral_scores(self):
        result = editor.plan(self.old, self.new, self.lessons)
        for row in result['ideas']:
            self.assertIsNone(row['priority_forecast'])
            self.assertIsNone(row['editorial_score_manual_12'])
            self.assertGreaterEqual(len(row['questions']), 3)
            self.assertFalse(row['verified_final_mp4'])
        self.assertIn('Cinema', next(x for x in result['ideas'] if x['format']=='artvision_cinema')['format_label'])

    def test_duplicates_are_flagged_but_other_angles_not_deleted(self):
        new = copy.deepcopy(self.new)
        duplicate = copy.deepcopy(new['ideas'][0])
        duplicate['id'] = 'critico-copy'
        new['ideas'].append(duplicate)
        result = editor.plan(self.old,new,self.lessons)
        item = next(x for x in result['ideas'] if x['id']=='critico-copy')
        self.assertEqual(item['stage'],'duplicate_review')
        new['ideas'][-1]['original_angle'] = 'Un angolo davvero differente, nuova osservazione'
        item = next(x for x in editor.plan(self.old,new,self.lessons)['ideas'] if x['id']=='critico-copy')
        self.assertNotEqual(item['stage'],'duplicate_review')

    def test_score_only_when_manual_and_transparent(self):
        add=copy.deepcopy(self.new)
        row=add['ideas'][0]
        row['editorial_review']={'reviewer':'regista','reason':'Prova motivata',
                                 'visual_impact':3,'story_payoff':2,'originality':1,'asset_feasibility':0}
        selected=next(x for x in editor.plan(self.old,add,self.lessons)['ideas'] if x['id']==row['id'])
        self.assertEqual(selected['editorial_score_manual_12'],6)
        row['editorial_review']['visual_impact']=4
        with self.assertRaises(ValueError):
            editor.plan(self.old,add,self.lessons)

    def test_html_escapes_and_file_outputs_never_overwrite(self):
        add=copy.deepcopy(self.new)
        add['ideas'][0]['topic']='<script>alert(1)</script>'
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'report'
            data=editor.run(out=output, existing=self.old, additions=add, lessons=self.lessons)
            page=(output/'PRELAUNCH_DASHBOARD_V18.html').read_text()
            self.assertNotIn('<script>alert(1)</script>',page)
            self.assertIn('&lt;script&gt;',page)
            self.assertEqual(data['count_ideas'],24)
            with self.assertRaises(ValueError):
                editor.run(out=output, existing=self.old, additions=add, lessons=self.lessons)

    def test_missing_evidence_flag_is_not_considered_verified(self):
        add=copy.deepcopy(self.new)
        row=add['ideas'][0]
        row.update({'sources_checked':True,'rights_checked':True,'visual_plan_checked':True})
        result=editor.plan(self.old,add,self.lessons)
        item=next(x for x in result['ideas'] if x['id']==row['id'])
        self.assertEqual(item['stage'],'idea_to_research')
        self.assertTrue(any('riferimento verificabile mancant' in x for x in item['issues']))


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'archive'/'film').mkdir(parents=True)
        self.folder=self.root/'archive'/'film'
        (self.folder/'film.mp4').write_bytes(b'fake mp4 test payload')
        (self.folder/'cover.jpg').write_bytes(b'fake image test payload')

    def entry(self,name):
        file=self.folder/name
        return {'file':name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}

    def save(self):
        value={'schema':'video-recipe-v13','topic':'Test ricetta autentica','format':'libri',
               'video':self.entry('film.mp4'),'cover':self.entry('cover.jpg'),'sources':[]}
        (self.folder/'VIDEO_RECIPE_V13.json').write_text(json.dumps(value))
        return value

    def test_verifies_hashes_and_never_claims_artistic_approval(self):
        self.save()
        result=memory.scan(['archive'],root=self.root)
        self.assertEqual(result['count'],1)
        self.assertEqual(result['packages_with_verified_assets'],1)
        self.assertFalse(result['artistic_approval_proven'])
        self.assertFalse(result['references'][0]['artistic_approval_proven'])
        (self.folder/'cover.jpg').write_bytes(b'changed')
        result=memory.scan(['archive'],root=self.root)
        self.assertEqual(result['packages_with_verified_assets'],0)
        self.assertEqual(result['references'][0]['reference_status'],'incomplete_package')

    def test_ignores_recipes_outside_root_and_rejects_traversal(self):
        self.save()
        result=memory.scan(['../'],root=self.root)
        self.assertEqual(result['count'],0)
        self.assertFalse(memory.safe_entry(self.folder, {'file':'../../../outside','sha256':'0'*64}))

    def test_html_export_is_safe(self):
        value=self.save()
        value['topic']='<script>alert(1)</script>'
        (self.folder/'VIDEO_RECIPE_V13.json').write_text(json.dumps(value))
        report=memory.scan(['archive'],root=self.root)
        memory.export(report,self.root/'result')
        page=(self.root/'result'/'CREATIVE_MEMORY_V18.html').read_text()
        self.assertIn('&lt;script&gt;',page)
        self.assertNotIn('<script>alert(1)</script>',page)
        with self.assertRaises(ValueError):
            memory.export(report,self.root/'result')


if __name__ == '__main__':
    unittest.main()
