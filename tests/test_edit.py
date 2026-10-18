import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'skills/mixreel/scripts/render_edit.py'
FIXTURE=json.loads((ROOT/'tests/fixtures/valid_plan.json').read_text())


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg/ffprobe unavailable')
class RenderEditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'media').mkdir()
        for name,colour in (('a','red'),('b','blue')):
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i',f'color=c={colour}:s=90x160:r=24:d=4',
                            '-c:v','libx264','-pix_fmt','yuv420p',str(self.root/f'media/{name}.mp4')],check=True)
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=220:duration=10',
                        str(self.root/'media/music.wav')],check=True)
        self.plan=copy.deepcopy(FIXTURE)
        for shot,name in zip(self.plan['shots'],('a','b')):
            shot['clip']={'asset':f'media/{name}.mp4','in':0.5,'duration':4.0,'speed':1.0}
    def tearDown(self):self.tmp.cleanup()
    def render(self,plan,*extra):
        path=self.root/'plan.json';path.write_text(json.dumps(plan))
        return subprocess.run(['python3',str(SCRIPT),str(path),str(self.root/'out.mp4'),'--size','90x160',*extra],
                              capture_output=True,text=True)
    def duration(self):
        out=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',
                            str(self.root/'out.mp4')],capture_output=True,text=True,check=True).stdout
        return float(out)
    def test_cut_matches_plan_duration(self):
        result=self.render(self.plan,'--holds','12')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertAlmostEqual(self.duration(),self.plan['duration'],delta=0.1)
    def test_dissolve_keeps_plan_duration(self):
        plan=copy.deepcopy(self.plan);plan['shots'][1]['transition']={'type':'dissolve','duration':0.5}
        result=self.render(plan)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertAlmostEqual(self.duration(),plan['duration'],delta=0.1)
    def test_missing_clip_range_is_rejected(self):
        plan=copy.deepcopy(self.plan);plan['shots'][0]['clip']['in']=3.5
        result=self.render(plan)
        self.assertEqual(result.returncode,2)
        self.assertIn('lacks requested range',result.stderr)
    def test_refuses_overwrite(self):
        (self.root/'out.mp4').write_text('keep')
        result=self.render(self.plan)
        self.assertEqual(result.returncode,2)
        self.assertEqual((self.root/'out.mp4').read_text(),'keep')


if __name__=='__main__':unittest.main()
