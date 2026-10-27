import array
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/mixreel'
RENDER = SKILL / 'scripts/render_edit.py'
EXAMPLE = json.loads((SKILL / 'assets/plan.v3.example.json').read_text())


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def clip(path, colour, seconds, tone=None):
    # Coloured picture with an optional sine tone, so picture and sound sources can be told apart.
    args = ['-f', 'lavfi', '-i', f'color=c={colour}:s=90x160:r=24:d={seconds}']
    if tone:
        args += ['-f', 'lavfi', '-i', f'sine=frequency={tone}:duration={seconds}', '-c:a', 'aac', '-shortest']
    ffmpeg(*args, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', path)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'json',
                          str(path)], check=True, capture_output=True, text=True).stdout
    data = json.loads(out)
    return {'duration': float(data['format']['duration']),
            'audio': any(s.get('codec_type') == 'audio' for s in data['streams'])}


def pixel(path, at):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(at), '-i', str(path), '-frames:v', '1', '-vf', 'scale=1:1',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], check=True, capture_output=True).stdout
    return tuple(out)


def tone_at(path, start, length=0.6):
    # Estimate the dominant frequency from zero crossings of a mono excerpt.
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(length), '-i', str(path), '-vn',
                          '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], check=True, capture_output=True).stdout
    samples = array.array('h', raw)
    crossings = sum(1 for a, b in zip(samples, samples[1:]) if (a < 0) != (b < 0))
    return crossings / (2 * length)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg/ffprobe unavailable')
class RenderVersion3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        media = cls.root / 'media'
        (media / 'ui').mkdir(parents=True)
        clip(media / 'sequence-1.mp4', 'red', 6, tone=300)
        clip(media / 'repair-shot-2.mp4', 'blue', 4, tone=1200)
        clip(media / 'sequence-2.mp4', 'green', 5, tone=600)
        ffmpeg('-f', 'lavfi', '-i', 'color=c=white:s=90x160:r=24:d=1.5', '-start_number', '0', media / 'ui/%03d.png')
        ffmpeg('-f', 'lavfi', '-i', 'sine=frequency=2000:duration=0.05', media / 'tap.wav')
        plan = copy.deepcopy(EXAMPLE)
        (cls.root / 'plan.json').write_text(json.dumps(plan))
        cls.out = cls.root / 'out.mp4'
        cls.result = subprocess.run(['python3', str(RENDER), str(cls.root / 'plan.json'), str(cls.out), '--size', '90x160'],
                                    capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_renders_full_length_without_a_music_track(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertAlmostEqual(probe(self.out)['duration'], 8.0, delta=0.1)

    def test_overlay_covers_its_interval_only(self):
        self.assertGreater(min(pixel(self.out, 1.6)), 200)
        red = pixel(self.out, 0.5)
        self.assertGreater(red[0], 200)
        self.assertLess(red[2], 60)

    def test_repair_replaces_picture_and_keeps_original_sound(self):
        blue = pixel(self.out, 4.0)
        self.assertGreater(blue[2], 200)
        self.assertLess(blue[0], 60)
        self.assertAlmostEqual(tone_at(self.out, 3.6), 300, delta=40)

    def test_each_shot_keeps_its_own_sound(self):
        self.assertAlmostEqual(tone_at(self.out, 0.2), 300, delta=40)
        self.assertAlmostEqual(tone_at(self.out, 6.5), 600, delta=60)

    def test_missing_audio_stream_is_reported(self):
        silent = self.root / 'media/silent.mp4'
        clip(silent, 'black', 6)
        plan = copy.deepcopy(EXAMPLE)
        plan['shots'][0]['clip']['asset'] = 'media/silent.mp4'
        path = self.root / 'silent-plan.json'
        path.write_text(json.dumps(plan))
        result = subprocess.run(['python3', str(RENDER), str(path), str(self.root / 'silent-out.mp4'), '--size', '90x160'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('has no audio', result.stderr)

    def render_variant(self, name, change):
        plan = copy.deepcopy(EXAMPLE)
        change(plan)
        path = self.root / f'{name}.json'
        path.write_text(json.dumps(plan))
        out = self.root / f'{name}.mp4'
        result = subprocess.run(['python3', str(RENDER), str(path), str(out), '--size', '90x160'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return out

    def test_track_music_is_ducked_and_mixed(self):
        ffmpeg('-f', 'lavfi', '-i', 'sine=frequency=100:duration=12', self.root / 'media/music.wav')
        def change(plan):
            plan['music'].update(source='track', asset='media/music.wav', duration=12.0, offset=1.0)
            plan['sound']['ducking'] = [{'start': 0.0, 'end': 8.0, 'gain': 0.0}]
        out = self.render_variant('track', change)
        self.assertAlmostEqual(probe(out)['duration'], 8.0, delta=0.1)
        self.assertAlmostEqual(tone_at(out, 0.2), 300, delta=40)

    def test_dissolve_keeps_length_with_sound(self):
        def change(plan):
            plan['shots'][2]['transition'] = {'type': 'dissolve', 'duration': 0.5}
        out = self.render_variant('dissolve', change)
        self.assertAlmostEqual(probe(out)['duration'], 8.0, delta=0.1)
        self.assertTrue(probe(out)['audio'])



if __name__ == '__main__':
    unittest.main()
