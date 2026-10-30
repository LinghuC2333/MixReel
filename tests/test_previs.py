import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/mixreel-script'
sys.path.insert(0, str(SKILL / 'scripts'))
EXAMPLE = SKILL / 'assets/previs-scene.example.json'

try:
    import numpy  # noqa: F401
    import PIL  # noqa: F401
    HAVE_IMAGING = True
except ImportError:
    HAVE_IMAGING = False


@unittest.skipUnless(HAVE_IMAGING, 'numpy/Pillow unavailable')
class PrevisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_raster_backend_renders_plan_frames_and_sheets(self):
        out = self.root / 'out'
        run = subprocess.run([sys.executable, str(SKILL / 'scripts/previs.py'), str(EXAMPLE), '--out', str(out),
                              '--backend', 'raster', '--shots', 'S02,S03'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        for name in ['plan.png', 'storyboard.png', 'review.png', 'shots/S02_start.png', 'shots/S03_end.png']:
            self.assertTrue((out / name).is_file(), name)
        manifest = json.loads((out / 'previs.json').read_text())
        self.assertEqual(manifest['backend'], 'raster')
        self.assertTrue(manifest['rough'])
        self.assertEqual([f['shot'] for f in manifest['frames']], ['S02', 'S02', 'S03', 'S03'])

    def test_auto_stops_when_blender_is_missing(self):
        import previs
        original = previs.find_blender
        previs.find_blender = lambda *a: None
        argv = sys.argv
        sys.argv = ['previs.py', str(EXAMPLE), '--out', str(self.root / 'out')]
        try:
            with self.assertRaises(SystemExit) as stop:
                previs.main()
            self.assertEqual(stop.exception.code, 3)
        finally:
            previs.find_blender = original
            sys.argv = argv

    def test_keys_carry_over_and_gaze_turns_the_actor(self):
        import previs_scene as ps
        scene = ps.load(EXAMPLE)
        mia = ps.states(scene, 6.0)['Mia']
        self.assertAlmostEqual(mia['pos'][1], 0.5)
        barista = ps.states(scene, 6.0)['Barista']['pos']
        # Facing the barista means the local +Y axis points at the barista.
        yaw = ps._yaw_toward(mia['pos'], barista)
        self.assertAlmostEqual(mia['yaw'], yaw, places=4)

    def test_film_places_every_piece_as_the_renders_do(self):
        import numpy as np
        import previs_scene as ps
        scene = ps.load(EXAMPLE)
        fps, count, pieces, cameras = ps.film(scene)
        self.assertEqual(count, 168)
        self.assertEqual([k for k, _ in cameras['S03']][0], 120)

        def rows(meshes):
            v = np.concatenate([m for m in meshes]).round(6)
            return v[np.lexsort(v.T[::-1])]

        # Frame 130 is inside S03, the barista's point of view.
        for k, pov in [(80, None), (130, 'Barista')]:
            placed = [p['vertices'] @ p['matrices'][k][:3, :3].T + p['matrices'][k][:3, 3]
                      for p in pieces.values() if p['matrices'][k] is not None]
            expected = [v for _, v, _, _ in ps.scene_meshes(scene, k / fps, pov=pov)]
            np.testing.assert_allclose(rows(placed), rows(expected), atol=1e-6)

    def test_duplicate_ids_are_rejected(self):
        import previs_scene as ps
        scene = json.loads(EXAMPLE.read_text())
        scene['props'].append(dict(scene['props'][0]))
        with self.assertRaises(ps.SceneError):
            ps.check(scene)


if __name__ == '__main__':
    unittest.main()
