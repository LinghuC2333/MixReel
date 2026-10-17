import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'skills/reference-replica-video/scripts/beat_grid.py'
HAS_LIBROSA=importlib.util.find_spec('librosa') is not None and importlib.util.find_spec('numpy') is not None


class BeatGridTests(unittest.TestCase):
    @unittest.skipUnless(HAS_LIBROSA,'librosa unavailable')
    def test_click_track_tempo(self):
        import numpy as np, wave
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sr=22050;y=np.zeros(sr*8,dtype=np.float32)
            for k in range(16):
                start=int(k*0.5*sr);y[start:start+400]=np.hanning(400)
            with wave.open(str(root/'click.wav'),'wb') as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((y*30000).astype('<i2').tobytes())
            result=subprocess.run(['python3',str(SCRIPT),str(root/'click.wav'),str(root/'beats.json'),'--bpm','120'],
                                  capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertAlmostEqual(json.loads((root/'beats.json').read_text())['bpm'],120,delta=2)
    def test_missing_input_exits_cleanly(self):
        result=subprocess.run(['python3',str(SCRIPT),'/nonexistent.wav','out.json'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)


if __name__=='__main__':unittest.main()
