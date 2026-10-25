"""Regression tests for requested-format protection and flexible editorial choices."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.editorial_rules import new_contract, new_plan, validate
from src.cinematic_director_v23 import plan as cinematic_plan


def completed_plan():
    # Synthetic metadata, never a real source verification or artistic approval.
    plan = new_plan()
    for key in ('subject_insight', 'opening_promise', 'payoff', 'cover_reason', 'duration_reason', 'mix_reason'):
        plan[key] = 'Fixture: an explicit editorial choice for the subject.'
    plan.update(duration_seconds=83.5, social_languages={'facebook': 'en'},
                sources=[{'reference': 'fixture', 'finding': 'test claim',
                          'verification_notes': 'synthetic unit-test evidence', 'status': 'reviewed'}],
                techniques=[{'id': 'locked_hold', 'reason': 'Show the narrated detail clearly', 'status': 'trial'}])
    # Synthetic discovery record used only for structural tests.
    plan['audience_research'] = {
        'candidates': [
            {'artist': 'Painter A', 'work': 'Work A', 'visual_hook': 'Strong silhouette',
             'human_interest': 'Curiosity', 'historical_anchor': 'Museum context',
             'asset_rights_notes': 'Source and photo license need final clearance',
             'comparison_reason': 'Visually distinct',
             'audience_signal': {'status': 'unavailable', 'reason': 'Unit test offline'}},
            {'artist': 'Painter B', 'work': 'Work B', 'visual_hook': 'Contrasting colors',
             'human_interest': 'Wonder', 'historical_anchor': 'Museum context',
             'asset_rights_notes': 'Photo rights to review',
             'comparison_reason': 'Contrasting mood',
             'audience_signal': {'status': 'unavailable', 'reason': 'Unit test offline'}},
            {'artist': 'Painter C', 'work': 'Work C', 'visual_hook': 'Expressive eyes',
             'human_interest': 'Empathy', 'historical_anchor': 'Museum context',
             'asset_rights_notes': 'Photo rights to review',
             'comparison_reason': 'Different narrative',
             'audience_signal': {'status': 'unavailable', 'reason': 'Unit test offline'}}
        ],
        'selected_work': 'Work A', 'selection_reason': 'Best balance of visual and story',
        'viewer_interest': 'Curiosity about the scene',
        'creative_direction': 'Reveal context after compelling opening',
        'signal_limitations': 'No platform data in offline tests',
        'analytics_feedback': 'not_yet_published'
    }
    return plan


def project(kind='artvision_critico'):
    return {'format': kind, 'subtitles': False, 'editorial_contract': new_contract(kind),
            'editorial_plan': completed_plan()}


class EditorialTests(unittest.TestCase):
    def test_audience_research_is_required_for_artvision(self):
        p = project()
        p['editorial_plan']['audience_research'] = {}
        errors, _ = validate(p)
        self.assertTrue(any('Ricerca pubblico' in e for e in errors))

    def test_unverified_popularity_claim_cannot_pass_as_signal(self):
        p = project()
        p['editorial_plan']['audience_research']['candidates'][0]['audience_signal'] = {
            'status': 'verified', 'observation': 'viral',
        }
        errors, _ = validate(p)
        self.assertTrue(any('senza fonte' in e for e in errors))

    def test_selection_must_match_shortlist(self):
        p = project()
        p['editorial_plan']['audience_research']['selected_work'] = 'Nonexistent work'
        self.assertTrue(any('scegliere esplicitamente' in e for e in validate(p)[0]))

    def test_documented_unavailability_does_not_fabricate_metrics(self):
        p = project()
        self.assertEqual(validate(p)[0], [])
        assert all(c['audience_signal']['status'] == 'unavailable'
                   for c in p['editorial_plan']['audience_research']['candidates'])

    def test_new_plan_is_blocked_until_research_and_choices_are_complete(self):
        p = project(); p['editorial_plan'] = new_plan()
        errors, _ = validate(p)
        self.assertTrue(any('fonti' in e for e in errors))
        self.assertTrue(any('Durata' in e for e in errors))

    def test_completed_critico_preserves_voice_and_is_not_artistically_certified(self):
        p = project()
        errors, warnings = validate(p)
        self.assertEqual(errors, [])
        self.assertTrue(any('solo musica' in w for w in warnings))
        self.assertEqual(p['editorial_plan']['artistic_review'], 'pending')

    def test_relabeling_critico_as_cinema_cannot_drop_requested_voice(self):
        p = project(); p['format'] = 'artvision_cinema'
        p['editorial_contract']['narrated'] = False
        errors, _ = validate(p)
        self.assertTrue(any('senza istruzione esplicita' in e for e in errors))

    def test_an_explicit_format_change_preserves_original_request_and_authorization(self):
        p = project(); p['format'] = 'artvision_cinema'
        p['editorial_contract'].update(narrated=False, voice=None,
            format_change_authorization={'from': 'artvision_critico', 'to': 'artvision_cinema',
                                         'approved_by': 'user', 'instruction': 'Fixture explicit request'})
        p['editorial_plan']['techniques'][0]['id'] = 'static_tableau'
        self.assertEqual(validate(p)[0], [])
        self.assertEqual(p['editorial_contract']['requested_format'], 'artvision_critico')

    def test_music_only_critico_and_voice_substitution_blocked(self):
        p = project(); p['editorial_contract'].update(narrated=False, voice='random robotic voice')
        errors, _ = validate(p)
        self.assertTrue(any('narrato' in e for e in errors))
        self.assertTrue(any('Gacrux' in e for e in errors))

    def test_no_fake_approval_or_unknown_technique(self):
        p = project(); p['editorial_plan']['techniques'][0]['status'] = 'approved_option'
        self.assertTrue(any('non registrata' in e for e in validate(p)[0]))
        p['editorial_plan']['techniques'][0]['id'] = 'made_up_effect'
        self.assertTrue(any('inesistente' in e for e in validate(p)[0]))

    def test_approved_museum_option_has_evidence_but_is_not_mandatory(self):
        p = project()
        p['editorial_plan']['techniques'][0].update(id='gallery_to_canvas_entry', status='approved_option')
        self.assertEqual(validate(p)[0], [])
        self.assertEqual(validate(project())[0], [])

    def test_explicit_mix_is_not_padded_to_eight_techniques(self):
        p = project()
        result = cinematic_plan(p)
        self.assertEqual([x['id'] for x in result['selected']], ['locked_hold'])
        self.assertFalse(result['autopublish'])

    def test_duration_proposal_is_used_but_actual_audio_and_video_take_precedence(self):
        from src.creative_director_v21 import duration_plan
        p = project()
        self.assertEqual(duration_plan(p)['seconds'], 83.5)
        p['voice_duration_seconds'] = 91
        self.assertEqual(duration_plan(p)['seconds'], 91)
        self.assertEqual(duration_plan(p, actual=94)['seconds'], 94)
        self.assertIsNone(duration_plan({'format': 'artvision_cinema'}, cinema_soft_range=False)['creative_window_seconds'])

    def test_policy_changes_do_not_silently_update_project(self):
        p = project(); p['editorial_contract']['policy_sha256'] = 'old'
        self.assertTrue(any('Versione regole cambiata' in e for e in validate(p)[0]))

    def test_nonfinite_and_boolean_duration_blocked(self):
        for value in (True, float('nan'), float('inf'), -1, 0):
            p = project(); p['editorial_plan']['duration_seconds'] = value
            self.assertTrue(any('Durata' in e for e in validate(p)[0]))

    def test_legacy_project_remains_readable_with_honest_migration_warning(self):
        errors, warnings = validate({'format': 'libri'})
        self.assertEqual(errors, [])
        self.assertTrue(any('storica' in w for w in warnings))

    def test_direct_adapter_blocks_format_drift_before_renderer(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
        import production_adapter_v16 as adapter
        import json
        p = project(); p.update(format='artvision_cinema', assets=[])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root/'project.json').write_text(json.dumps(p))
            with patch.object(adapter, 'ROOT', root), patch.object(adapter.subprocess, 'run') as render:
                with self.assertRaisesRegex(ValueError, 'formato richiesto'):
                    adapter.execute({'adapter': 'cinema_v6_vangogh_prepared', 'project_file': 'project.json'}, root/'out')
                render.assert_not_called()


if __name__ == '__main__':
    unittest.main()
