import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v254_fiesole_local_cpu_photo as mod

def make_source(tmp:Path):
    payload={}
    for index in range(1,6):
        b=io.BytesIO()
        Image.new("RGB",(1920,1080),(index*30,index*30,index*30)).save(b,format="PNG")
        payload[f"frame_{index:02d}.png"]=b.getvalue()
    manifest={"version":"V251_FIESOLE_SOURCE_LOCKED_PHOTO_HANDOFF",
              "episode":mod.EPISODE,"source_film_sha256":"synthetic-film-sha",
              "status":"SOURCE_FRAMES_FOR_FOUR_I2I_AND_ONE_VIDU_NOT_FINAL",
              "shots":[]}
    for index in range(1,6):
        name=f"frame_{index:02d}.png"
        manifest["shots"].append({"shot":index,
            "role":"I2I_PHOTO_SOURCE" if index<5 else "VIDU_SOURCE_FRAME",
            "original_frame":name,"source_frame_locked":True,
            "archive_filename":f"original_shot_{index:02d}_{name}",
            "original_sha256":hashlib.sha256(payload[name]).hexdigest(),
            "source_time_s":float(index)})
    path=tmp/"V251.zip"
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("V251_SOURCE_MANIFEST_NOT_FINAL.json",json.dumps(manifest))
        z.writestr("FIESOLE_V251_FIVE_SHOT_REVIEW_CONTACT_SHEET.png",b"sheet")
        for shot in manifest["shots"]:
            z.writestr(shot["archive_filename"],payload[shot["original_frame"]])
    mapping=[(name,hashlib.sha256(blob).hexdigest()) for name,blob in payload.items()]
    return path,mapping

class V254SourceOnlyTests(unittest.TestCase):
    def test_sha_bound_offline_trial_does_not_generate_or_approve(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            archive,candidates=make_source(root)
            with patch.object(mod,"FILM_SHA","synthetic-film-sha"),patch.object(mod,"CANDIDATES",candidates):
                result=mod.run(archive,root/"out",offline=True)
            self.assertEqual(result["status"],"SOURCE_SHA_LOCKED_NO_GENERATION")
            self.assertEqual(result["new_generated_i2i"],0)
            self.assertFalse(result["final_mp4"])
            self.assertFalse(result["human_artistic_approved"])
            self.assertFalse(result["italian_rights_verified"])
            self.assertFalse(result["vidu_generated"])
            self.assertEqual(result["shot_index"],2)
            with Image.open(root/"out"/"V254_FIESOLE_ORIGINAL_PORTRAIT_CROP.png") as pic:
                self.assertEqual(pic.size,mod.TARGET_SIZE)

    def test_no_unverified_original_pixel_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            archive,candidates=make_source(root)
            candidates[1]=(candidates[1][0],"0"*64)
            with patch.object(mod,"FILM_SHA","synthetic-film-sha"),patch.object(mod,"CANDIDATES",candidates):
                with self.assertRaisesRegex(ValueError,"UNVERIFIED_FRAME_IDENTITY"):
                    mod.extract_source(archive,root/"out")
            self.assertFalse((root/"out"/"V254_FIESOLE_ORIGINAL_PORTRAIT_CROP.png").exists())

    def test_wrong_film_fails_before_any_inference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            archive,candidates=make_source(root)
            with patch.object(mod,"CANDIDATES",candidates):
                with self.assertRaisesRegex(ValueError,"WRONG_SOURCE_MANIFEST"):
                    mod.run(archive,root/"out",offline=False)
            report=json.loads((root/"out"/"V254_REAL_PHOTO_CANDIDATE_STATUS.json").read_text())
            self.assertEqual(report["new_generated_i2i"],0)
            self.assertEqual(report["provider_requests"],0)
            self.assertFalse(report["publish_allowed"])

    def test_refuse_vidu_anchor_as_four_photographs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            archive,candidates=make_source(root)
            with patch.object(mod,"FILM_SHA","synthetic-film-sha"),patch.object(mod,"CANDIDATES",candidates):
                with self.assertRaisesRegex(ValueError,"SOURCE_ARCHIVE_OR_SHOT_INVALID"):
                    mod.extract_source(archive,root/"out",shot_index=5)

if __name__=="__main__":
    unittest.main()
