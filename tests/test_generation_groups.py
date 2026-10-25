import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/mixreel'
spec = importlib.util.spec_from_file_location('group_validator', SKILL / 'scripts/validate_plan.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class GenerationGroupTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((SKILL / 'assets/plan.example.json').read_text())

    def errors(self):
        return '\n'.join(validator.validate(self.plan))

    def test_two_shots_one_request_one_image(self):
        self.assertEqual(validator.validate(self.plan), [])
        self.assertEqual(len(self.plan['shots']), 2)
        self.assertEqual(len(self.plan['generation_groups']), 1)
        self.assertEqual(self.plan['illustration_count'], 1)

    def test_no_new_images_when_existing_inputs_suffice(self):
        for shot in self.plan['shots']:
            shot['keyframes'] = []
        self.plan['illustration_count'] = 0
        self.assertEqual(validator.validate(self.plan), [])

    def test_shared_keyframe_is_counted_once(self):
        self.plan['shots'][1]['keyframes'] = ['frame-1']
        self.assertEqual(validator.validate(self.plan), [])
        self.plan['illustration_count'] = 2
        self.assertIn('expected 1 unique images', self.errors())

    def test_missing_generation_groups_is_rejected(self):
        del self.plan['generation_groups']
        self.assertIn('nonempty list required', self.errors())

    def test_unknown_shot_is_rejected(self):
        self.plan['generation_groups'][0]['shot_ids'] = ['unknown']
        self.assertIn('unknown shot unknown', self.errors())

    def test_duplicate_membership_is_rejected(self):
        self.plan['generation_groups'][0]['shot_ids'].append('shot-1')
        self.assertIn('shot assigned more than once', self.errors())

    def test_missing_or_reordered_shots_are_rejected(self):
        for ids in (['shot-1'], ['shot-2', 'shot-1']):
            with self.subTest(ids=ids):
                self.plan['generation_groups'][0]['shot_ids'] = ids
                self.assertIn('timeline order', self.errors())

    def test_split_groups_need_distinct_ids_and_complete_order(self):
        first = self.plan['generation_groups'][0]
        second = copy.deepcopy(first)
        first['shot_ids'] = ['shot-1']
        first['requested_duration'] = 3
        second.update(id='sequence-2', shot_ids=['shot-2'], requested_duration=3)
        self.plan['generation_groups'].append(second)
        self.assertEqual(validator.validate(self.plan), [])
        second['id'] = first['id']
        self.assertIn('duplicate generation group id', self.errors())

    def test_request_duration_must_cover_planned_sequence(self):
        group = self.plan['generation_groups'][0]
        group['requested_duration'] = 5
        self.assertIn('5s cannot cover the 6s timeline span', self.errors())
        group['requested_duration'] = 8
        self.assertEqual(validator.validate(self.plan), [])

    def test_group_preserves_member_bindings(self):
        self.plan['generation_groups'][0]['bindings'].remove('style-a')
        self.assertIn('missing a member shot reference', self.errors())

    def test_unknown_or_duplicate_group_binding_is_rejected(self):
        group = self.plan['generation_groups'][0]
        group['bindings'].append('unknown')
        self.assertIn('unknown reference unknown', self.errors())
        group['bindings'][-1] = 'style-a'
        self.assertIn('duplicate binding', self.errors())

    def test_media_type_must_be_explicit(self):
        del self.plan['references'][1]['media_type']
        self.assertIn('expected image, video or audio', self.errors())

    def test_group_cannot_silently_use_two_generated_results(self):
        for i, shot in enumerate(self.plan['shots']):
            shot['clip'] = {'asset': 'sequence.mp4', 'in': i * 3, 'duration': 6, 'speed': 1}
        self.assertEqual(validator.validate(self.plan), [])
        self.plan['shots'][1]['clip']['asset'] = 'another.mp4'
        self.assertIn('same selected source asset', self.errors())

    def test_shared_source_duration_must_agree(self):
        for i, shot in enumerate(self.plan['shots']):
            shot['clip'] = {'asset': 'sequence.mp4', 'in': i * 3, 'duration': 6 + i, 'speed': 1}
        self.assertIn('agree on total source duration', self.errors())

    def test_malformed_group_fields_report_errors(self):
        base = copy.deepcopy(self.plan)
        for key, value in [('shot_ids', {}), ('bindings', [None]), ('requested_duration', float('nan')),
                           ('requested_duration', True), ('reason', ''), ('continuity', None),
                           ('provider_prompt', 42), ('id', [])]:
            with self.subTest(key=key, value=value):
                self.plan = copy.deepcopy(base)
                self.plan['generation_groups'][0][key] = value
                self.assertTrue(validator.validate(self.plan))
        for groups in ({}, [None], []):
            self.plan = copy.deepcopy(base)
            self.plan['generation_groups'] = groups
            self.assertTrue(validator.validate(self.plan))

    def test_legacy_plan_does_not_silently_ignore_groups(self):
        self.plan['version'] = 1
        self.assertIn('use version 2 for grouped generation', self.errors())


if __name__ == '__main__':
    unittest.main()
