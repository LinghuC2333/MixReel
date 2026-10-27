import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/mixreel'
spec = importlib.util.spec_from_file_location('qa_check', SKILL / 'scripts/qa_check.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg/ffprobe unavailable')
class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def joined(self, name, parts):
        # Concatenate coloured segments, each (colour, seconds), with a steady tone underneath.
        video = self.root / name
        total = sum(d for _, d in parts)
        args = []
        for colour, seconds in parts:
            args += ['-f', 'lavfi', '-i', f'color=c={colour}:s=90x160:r=24:d={seconds}']
        args += ['-f', 'lavfi', '-i', f'sine=frequency=440:duration={total}']
        chain = ''.join(f'[{i}:v]' for i in range(len(parts))) + f'concat=n={len(parts)}:v=1:a=0[v]'
        ffmpeg(*args, '-filter_complex', chain, '-map', '[v]', '-map', f'{len(parts)}:a',
               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', video)
        return video

    def plan(self, cut):
        shot = lambda sid, a, b: {'id': sid, 'start': a, 'end': b, 'transition': {'type': 'cut', 'duration': 0}}
        return {'duration': 4.0, 'shots': [shot('one', 0.0, cut), shot('two', cut, 4.0)]}

    def test_frames_of_the_next_shot_before_a_planned_cut(self):
        video = self.joined('early.mp4', [('red', 1.875), ('blue', 2.125)])
        report = qa.check(video, self.plan(2.0))
        self.assertEqual(report['cut_checks'][0]['frames_like_next_shot_before_cut'], 3)
        self.assertIn('frames from the neighbouring shot', '\n'.join(report['issues']))

    def test_clean_cut_passes(self):
        video = self.joined('clean.mp4', [('red', 2.0), ('blue', 2.0)])
        report = qa.check(video, self.plan(2.0))
        self.assertEqual(report['issues'], [])

    def test_unplanned_changes_are_candidates_only(self):
        video = self.joined('flash.mp4', [('red', 2.0), ('blue', 0.125), ('red', 2.0)])
        report = qa.check(video)
        self.assertEqual([r['frames'] for r in report['short_runs_between_changes']], [3])
        self.assertTrue(report['unplanned_changes'])
        self.assertEqual(report['issues'], [])

    def test_silence_and_missing_audio(self):
        video = self.root / 'quiet.mp4'
        ffmpeg('-f', 'lavfi', '-i', 'color=c=red:s=90x160:r=24:d=3', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo:d=3',
               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', video)
        self.assertTrue(qa.check(video)['silences'])
        mute = self.root / 'mute.mp4'
        ffmpeg('-f', 'lavfi', '-i', 'color=c=red:s=90x160:r=24:d=2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', mute)
        self.assertIn('no audio stream', qa.check(mute)['issues'])

    def test_rendered_example_passes_its_planned_cuts(self):
        media = self.root / 'media'
        (media / 'ui').mkdir(parents=True)
        for name, colour, seconds, tone in (('sequence-1', 'red', 6, 300), ('repair-shot-2', 'blue', 4, 1200),
                                            ('sequence-2', 'green', 5, 600)):
            ffmpeg('-f', 'lavfi', '-i', f'color=c={colour}:s=90x160:r=24:d={seconds}', '-f', 'lavfi',
                   '-i', f'sine=frequency={tone}:duration={seconds}', '-c:a', 'aac', '-shortest',
                   '-c:v', 'libx264', '-pix_fmt', 'yuv420p', media / f'{name}.mp4')
        ffmpeg('-f', 'lavfi', '-i', 'color=c=white:s=90x160:r=24:d=1.5', '-start_number', '0', media / 'ui/%03d.png')
        ffmpeg('-f', 'lavfi', '-i', 'sine=frequency=2000:duration=0.05', media / 'tap.wav')
        example = json.loads((SKILL / 'assets/plan.v3.example.json').read_text())
        (self.root / 'plan.json').write_text(json.dumps(example))
        out = self.root / 'out.mp4'
        subprocess.run(['python3', str(SKILL / 'scripts/render_edit.py'), str(self.root / 'plan.json'), str(out),
                        '--size', '90x160'], check=True, capture_output=True)
        report = qa.check(out, example)
        self.assertEqual([c['cut'] for c in report['cut_checks']], [3.0, 5.0])
        for c in report['cut_checks']:
            self.assertEqual(c['frames_like_next_shot_before_cut'], 0)
            self.assertEqual(c['frames_like_previous_shot_after_cut'], 0)


if __name__ == '__main__':
    unittest.main()
