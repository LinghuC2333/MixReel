import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('media_inspect',ROOT/'skills/reference-replica-video/scripts/media_inspect.py')
media=importlib.util.module_from_spec(spec);spec.loader.exec_module(media)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg/ffprobe unavailable')
class MediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
        cls.clip=cls.root/'synthetic.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=black:s=96x160:r=24:d=1',
                        '-f','lavfi','-i','color=c=white:s=96x160:r=24:d=1',
                        '-filter_complex','[0:v][1:v]concat=n=2:v=1:a=0[v]',
                        '-map','[v]','-c:v','libx264','-pix_fmt','yuv420p',str(cls.clip)],check=True)
        cls.audio=cls.root/'synthetic.wav'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:duration=1',
                        '-f','lavfi','-i','anullsrc=r=44100:cl=mono:d=1',
                        '-filter_complex','[0:a][1:a]concat=n=2:v=0:a=1[a]',
                        '-map','[a]',str(cls.audio)],check=True)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_reference_cut_and_frames(self):
        result=media.reference(self.clip,self.root/'reference',.5,.3)
        self.assertTrue(any(abs(t-1)<.1 for t in result['cut_candidates']))
        self.assertTrue((self.root/'reference/contact.jpg').is_file())
        self.assertEqual(len(result['frames']),4)
    def test_audio_end_silence_detected(self):
        result=media.audio(self.audio,self.root/'audio.json')
        self.assertTrue(any(abs(x['start']-1)<.1 and x['end']>1.9 for x in result['silence_candidates']))
    def test_motion_change_is_candidate(self):
        result=media.motion(self.clip,self.root/'motion.json',12)
        self.assertTrue(any(abs(x['time']-1)<.1 for x in result['change_candidates']))
    def test_no_audio_reports_missing_stream(self):
        with self.assertRaisesRegex(ValueError,'no audio'):media.audio(self.clip,self.root/'absent.json')
    def test_no_overwrite(self):
        target=self.root/'existing.json';target.write_text('original')
        with self.assertRaises(FileExistsError):media.audio(self.audio,target)
        self.assertEqual(target.read_text(),'original')


if __name__=='__main__':unittest.main()
