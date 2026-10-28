import importlib.util, tempfile, unittest
from pathlib import Path
import cv2, numpy as np
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("v66",ROOT/"src/storia_rivive_v66_photo_guard.py")
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)

class PhotoFidelityV66(unittest.TestCase):
    def test_new_sharp_image_must_not_be_called_archival_restoration(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);rng=np.random.default_rng(42)
            src=np.zeros((400,250,3),dtype=np.uint8)
            cv2.rectangle(src,(40,10),(190,380),(180,180,180),-1)
            cv2.circle(src,(105,180),58,(60,60,60),-1)
            cv2.rectangle(src,(25,240),(210,350),(115,115,115),-1)
            original=folder/"original.png";cv2.imwrite(str(original),src)
            faithful=src.copy();faithful[:,:,1]=np.clip(faithful[:,:,1].astype(int)+12,0,255)
            cv2.imwrite(str(folder/"faithful.png"),faithful)
            unrelated=rng.integers(0,255,(400,250,3),dtype=np.uint8)
            cv2.imwrite(str(folder/"fabricated.png"),unrelated)
            good=mod.compare(original,folder/"faithful.png")
            self.assertTrue(good["geometry_compatible"])
            self.assertEqual(good["status"],"PENDING_HUMAN_FIDELITY_AND_IMAGE_QUALITY_REVIEW")
            fake=mod.compare(original,folder/"fabricated.png")
            self.assertEqual(fake["status"],"REJECT_NOT_SOURCE_FAITHFUL")
            all_reviewer_approvals={k:True for k in mod.REQUIRED}
            self.assertEqual(mod.compare(original,folder/"faithful.png",all_reviewer_approvals)["status"],
                "ART_DIRECTOR_APPROVED")
            self.assertEqual(mod.compare(original,folder/"fabricated.png",all_reviewer_approvals)["status"],
                "REJECT_NOT_SOURCE_FAITHFUL")

if __name__=="__main__":unittest.main()
