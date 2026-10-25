import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_package import check_collection, MANIFEST
from install_collection import install


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dest = Path(self.temp.name).resolve() / 'installed'

    def test_complete_install_is_self_contained(self):
        result = install(self.dest)
        self.assertEqual(len(result['installed']), 7)
        self.assertEqual(result['network_requests'], 0)
        self.assertEqual(check_collection(self.dest), [])
        for name in result['installed']:
            self.assertTrue((self.dest / name / 'SKILL.md').is_file())
        # Resolve and execute common helpers from the installed copy, outside checkout.
        validate = self.dest / 'mixreel/scripts/validate_plan.py'
        example = self.dest / 'mixreel/assets/plan.example.json'
        run = subprocess.run([sys.executable, str(validate), str(example)],
                             cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        config = Path(self.temp.name).resolve() / 'private-config'
        run = subprocess.run([sys.executable, str(self.dest / 'mixreel/scripts/init_config.py'),
                              '--directory', str(config)], cwd=self.temp.name,
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue((config / 'credentials.json').is_file())

    def test_existing_install_is_not_overwritten(self):
        install(self.dest)
        entry = self.dest / 'mixreel-script/SKILL.md'
        entry.write_text('local user changes')
        with self.assertRaises(ValueError):
            install(self.dest)
        self.assertEqual(entry.read_text(), 'local user changes')

    def test_partial_collision_leaves_other_files_untouched(self):
        self.dest.mkdir()
        existing = self.dest / 'mixreel-review'
        existing.mkdir()
        (existing / 'personal.txt').write_text('keep')
        with self.assertRaises(ValueError):
            install(self.dest)
        self.assertEqual(list(self.dest.iterdir()), [existing])
        self.assertEqual((existing / 'personal.txt').read_text(), 'keep')

    def test_missing_shared_dependency_is_detected(self):
        install(self.dest)
        shutil.rmtree(self.dest / 'mixreel')
        errors = check_collection(self.dest)
        self.assertTrue(any('missing skill entry: mixreel' in e for e in errors))
        self.assertTrue(any('broken collection link' in e for e in errors))

    def test_external_dependency_is_detected(self):
        install(self.dest)
        external = Path(self.temp.name).resolve() / 'external.md'
        external.write_text('not shipped')
        with (self.dest / 'mixreel-script/SKILL.md').open('a') as f:
            f.write('\n[External dependency](../../external.md)\n')
        self.assertTrue(any('broken collection link' in e for e in check_collection(self.dest)))

    def test_orphaned_reference_is_detected(self):
        install(self.dest)
        (self.dest / 'mixreel-script/references/lost.md').write_text('# Important rule\n')
        self.assertTrue(any('unrouted reference' in e for e in check_collection(self.dest)))

    def test_symlink_destination_rejected(self):
        real = Path(self.temp.name).resolve() / 'real'
        real.mkdir()
        self.dest.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ValueError):
            install(self.dest)
        self.assertEqual(list(real.iterdir()), [])

    def test_invalid_manifest_does_not_install(self):
        source = Path(self.temp.name).resolve() / 'source'
        shutil.copytree(ROOT / 'skills', source)
        (source / MANIFEST).write_text(json.dumps({'version': 1, 'core': 'mixreel', 'skills': ['../escape']}))
        with self.assertRaises(ValueError):
            install(self.dest, source)
        self.assertFalse(self.dest.exists())

    def test_source_symlink_is_rejected(self):
        source = Path(self.temp.name).resolve() / 'source'
        shutil.copytree(ROOT / 'skills', source)
        (source / 'mixreel-script/references/shortcut.md').symlink_to(
            source / 'mixreel-script/references/ad-script.md')
        with self.assertRaises(ValueError):
            install(self.dest, source)
        self.assertFalse(self.dest.exists())

    def test_unlisted_skill_is_detected(self):
        install(self.dest)
        extra = self.dest / 'mixreel-unlisted'
        extra.mkdir()
        (extra / 'SKILL.md').write_text('# extra')
        self.assertTrue(any('unlisted skill' in e for e in check_collection(self.dest)))


if __name__ == '__main__':
    unittest.main()
