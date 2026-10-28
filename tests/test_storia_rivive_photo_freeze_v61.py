import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v61",ROOT/"src/storia_rivive_photo_freeze_v61.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestStoriaPhotoFreezeV61(unittest.TestCase):
    def sample(self,folder):
        video=folder/"archival_TEST_ONLY.mp4"
        subprocess.run(["ffmpeg","-y","-nostdin","-loglevel","error",
            "-f","lavfi","-i","testsrc2=size=320x240:rate=30",
            "-t","3.5","-vf","format=gray","-pix_fmt","yuv420p",
            "-c:v","libx264",str(video)],check=True,timeout=90)
        photograph=folder/"photo_FAKE_TEST_NOT_AI.png"
        img=np.zeros((640,360,3),dtype=np.uint8)
        img[:,:,:]=(145,60,30)
        cv2.circle(img,(170,220),75,(13,175,235),-1)
        cv2.imwrite(str(photograph),img)
        scene={"archive_video":str(video),"ai_photo":str(photograph),
            "archive_license":"CC0","source_page":"https://commons.wikimedia.org/wiki/File:TEST_ONLY",
            "rights_checked":True,"start_s":.2,"motion_s":.85,
            "transition_s":.25,"photo_hold_s":.9,
            "framing":"contain","crop_faces_reviewed":True,"virtual_photo_zoom":0}
        return {"test_only":True,"width":360,"height":640,"fps":30,
                "shots":[scene],"audio":{}}

    def test_photo_requires_real_ai_and_qa_in_non_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan=self.sample(Path(tmp))
            plan.update(test_only=False,width=720,height=1280)
            errors,_=mod.validate(plan)
            self.assertTrue(any("AI" in x for x in errors))
            self.assertTrue(any("approvato" in x for x in errors))

    def test_non_pd_original_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan=self.sample(Path(tmp))
            plan["shots"][0]["archive_license"]="CC BY-NC"
            errors,_=mod.validate(plan)
            self.assertTrue(any("CC0/PD" in x for x in errors))

    def test_no_overlap_same_historical_clip(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan=self.sample(Path(tmp))
            plan["shots"].append(dict(plan["shots"][0]))
            errors,_=mod.validate(plan)
            self.assertTrue(any("sovrapposto" in x for x in errors))

    def test_real_video_motion_then_photo_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            plan=self.sample(folder)
            errors,_=mod.validate(plan)
            self.assertEqual(errors,[])
            output=folder/"V61_TECHNICAL_TEST_ONLY.mp4"
            qa=mod.render(plan,output)
            self.assertTrue(output.exists())
            self.assertEqual(qa["quality_status"],"TEST_ONLY_NO_AI")
            self.assertEqual(len(qa["sha256"]),64)
            self.assertTrue((folder/(output.name+".qa.json")).exists())
            cap=cv2.VideoCapture(str(output))
            frames=[]
            for s in (.15,.35,.65,1.4,1.55,1.75,1.9):
                cap.set(cv2.CAP_PROP_POS_MSEC,s*1000)
                ok,img=cap.read()
                self.assertTrue(ok)
                frames.append(cv2.resize(img,(100,180)))
            cap.release()
            def motion(a,b):
                return np.mean(abs(a.astype(np.float32)-b.astype(np.float32)))
            # Real video is different frames, while color photo holds still.
            self.assertGreater(motion(frames[0],frames[1]),2.0)
            self.assertLess(motion(frames[3],frames[4]),.75)
            self.assertLess(motion(frames[5],frames[6]),.75)
            first_sat=cv2.cvtColor(frames[1],cv2.COLOR_BGR2HSV)[:,:,1].mean()
            last_sat=cv2.cvtColor(frames[4],cv2.COLOR_BGR2HSV)[:,:,1].mean()
            self.assertGreater(last_sat,first_sat+35)

if __name__=="__main__":
    unittest.main()
