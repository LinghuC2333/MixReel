import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('init_config', ROOT / 'skills/mixreel/scripts/init_config.py')
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


class LocalConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.directory = self.root / 'config'

    def test_blank_matching_roles_and_permissions(self):
        config.initialize(self.directory)
        providers = json.loads((self.directory / 'providers.json').read_text())
        credentials = json.loads((self.directory / 'credentials.json').read_text())
        self.assertEqual(set(providers['profiles']), set(credentials['keys']))
        self.assertTrue(all(value == '' for value in credentials['keys'].values()))
        if os.name == 'posix':
            self.assertEqual(stat.S_IMODE(self.directory.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((self.directory / 'credentials.json').stat().st_mode), 0o600)

    def test_repeated_init_preserves_user_values(self):
        config.initialize(self.directory)
        target = self.directory / 'credentials.json'
        original = json.dumps({'version': 1, 'keys': {'image_generation': 'synthetic-local-value'}})
        target.write_text(original)
        self.assertEqual(config.initialize(self.directory)['credentials'], 'preserved')
        self.assertEqual(target.read_text(), original)

    def test_reject_git_directory(self):
        (self.root / '.git').mkdir()
        with self.assertRaises(ValueError):
            config.initialize(self.directory)
        self.assertFalse(self.directory.exists())

    def test_reject_symlink_directory(self):
        self.directory.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            config.initialize(self.directory)

    def test_reject_symlink_file(self):
        self.directory.mkdir(mode=0o700)
        target = self.root / 'untouched'
        target.write_text('synthetic-local-value')
        (self.directory / 'credentials.json').symlink_to(target)
        with self.assertRaises(ValueError):
            config.initialize(self.directory)
        self.assertEqual(target.read_text(), 'synthetic-local-value')

    @unittest.skipUnless(os.name == 'posix', 'POSIX permissions')
    def test_reject_readable_credentials(self):
        config.initialize(self.directory)
        (self.directory / 'credentials.json').chmod(0o644)
        with self.assertRaises(ValueError):
            config.initialize(self.directory)


if __name__ == '__main__':
    unittest.main()
