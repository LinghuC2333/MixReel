import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/mixreel'
spec = importlib.util.spec_from_file_location('plan_v3_validator', SKILL / 'scripts/validate_plan.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
EXAMPLE = json.loads((SKILL / 'assets/plan.v3.example.json').read_text())


class PlanVersion3Tests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(EXAMPLE)

    def errors(self):
        return '\n'.join(validator.validate(self.plan))

    def test_example_is_valid(self):
        self.assertEqual(validator.validate(self.plan), [])

    def test_generated_score_needs_no_track(self):
        self.assertNotIn('asset', self.plan['music'])
        self.plan['music']['source'] = 'none'
        self.assertEqual(validator.validate(self.plan), [])
        self.plan['music']['source'] = 'radio'
        self.assertIn('expected track, generated or none', self.errors())

    def test_track_still_needs_its_file_and_range(self):
        self.plan['music'] = {'source': 'track', 'events': []}
        self.assertIn('music.asset', self.errors())

    def test_earlier_versions_reject_new_layers(self):
        plan = json.loads((SKILL / 'assets/plan.example.json').read_text())
        plan['overlays'] = []
        self.assertIn('use version 3', '\n'.join(validator.validate(plan)))

    def test_audio_source_range_is_checked(self):
        self.plan['shots'][1]['audio']['in'] = 5.0
        self.assertIn('audio source lacks requested range', self.errors())
        self.plan['shots'][1]['audio'] = {'from': 'radio'}
        self.assertIn('expected clip, asset or none', self.errors())

    def test_repair_clip_is_exempt_from_shared_source_rule(self):
        del self.plan['shots'][1]['clip']['repair']
        self.assertIn('member clips must use the same selected source asset', self.errors())

    def test_repair_needs_version_3(self):
        plan = json.loads((SKILL / 'assets/plan.example.json').read_text())
        plan['shots'][0]['clip'] = {'asset': 'a.mp4', 'in': 0, 'duration': 6, 'speed': 1, 'repair': 'x'}
        self.assertIn('use version 3 for repair clips', '\n'.join(validator.validate(plan)))

    def test_continuation_must_follow_an_earlier_group(self):
        link = self.plan['generation_groups'][1]['continues_from']
        link['group'] = 'sequence-9'
        self.assertIn('must name an earlier generation group', self.errors())
        link['group'] = 'sequence-1'
        link['tail'] = 9.0
        self.assertIn('longer than the earlier request', self.errors())

    def test_continuation_needs_version_3(self):
        plan = json.loads((SKILL / 'assets/plan.example.json').read_text())
        plan['generation_groups'][0]['continues_from'] = {'group': 'sequence-1', 'tail': 2}
        self.assertIn('use version 3 for continuations', '\n'.join(validator.validate(plan)))

    def test_overlay_must_sit_inside_timeline(self):
        self.plan['overlays'][0]['end'] = 9.0
        self.assertIn('overlay outside timeline', self.errors())
        self.plan['overlays'][0]['end'] = 2.5
        del self.plan['overlays'][0]['fps']
        self.assertIn('image sequence needs fps', self.errors())

    def test_holds_cannot_exceed_fps(self):
        self.plan['shots'][0]['holds'] = 30
        self.assertIn('cannot exceed fps', self.errors())

    def test_ducking_only_lowers_music(self):
        self.plan['sound']['ducking'] = [{'start': 1, 'end': 2, 'gain': 1.5}]
        self.assertIn('ducking gain must be at most 1', self.errors())


if __name__ == '__main__':
    unittest.main()
