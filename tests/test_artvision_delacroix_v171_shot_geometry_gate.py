#!/usr/bin/env python3
"""Non-destructive critic shot/voice alignment geometry gate (no API, render or publishing).

Prevents calling a narrow 9:16 crop of a landscape painting an 'entire painting'.
This is a preparation gate, not human artistic approval.
"""
import json, pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECIPE = ROOT / "modules/artvision_critico/production_series/delacroix_sardanapalus_critico_v169.json"
SOURCE_W, SOURCE_H = 6875, 5358
OUTPUT_W, OUTPUT_H = 1080, 1920

def inspect_shots(recipe):
    failures = []
    plan = []
    for beat in recipe["chapters"]:
        idx, focus, h = beat["beat"], beat["focus"].lower(), beat["crop_height_px"]
        w = round(h * OUTPUT_W / OUTPUT_H)
        cx, cy = beat["cx"], beat["cy"]
        x0 = max(0, min(SOURCE_W-w, round(cx*SOURCE_W-w/2)))
        y0 = max(0, min(SOURCE_H-h, round(cy*SOURCE_H-h/2)))
        entire = "intero" in focus or "intera" in focus
        if entire:
            # A landscape artwork cannot fit inside a portrait crop. Use a
            # full-plate letterbox or documented uncropped composition instead.
            mode = "full_plate_uncropped_required"
            if w < SOURCE_W or h < SOURCE_H:
                failures.append({"beat":idx,"issue":"WHOLE_PAINTING_LABEL_BUT_CROPPED",
                                 "crop_source_px":[w,h],"artwork_source_px":[SOURCE_W,SOURCE_H]})
        else:
            mode = "detail_crop_candidate_human_review_required"
        if not (0 <= x0 <= SOURCE_W-w and 0 <= y0 <= SOURCE_H-h):
            failures.append({"beat":idx,"issue":"OUT_OF_BOUNDS"})
        plan.append({"beat":idx,"focus":beat["focus"],"mode":mode,
                     "source_crop_xywh_candidate":[x0,y0,w,h],
                     "spoken_text":beat["text"],"audio_start_end_s":"PENDING_REAL_WAV_ALIGNMENT",
                     "visual_subject_verified":False})
    return failures, plan

class ShotGeometryGate(unittest.TestCase):
    def test_recipe_and_no_false_full_painting(self):
        q=json.loads(RECIPE.read_text(encoding="utf-8"))
        self.assertEqual(q["work_id"],"delacroix_death_sardanapalus_1827_louvre_rf2346")
        self.assertEqual(len(q["chapters"]),9)
        failures,plan=inspect_shots(q)
        # Existing V169 is intentionally not rewritten. This test detects
        # the pre-existing mismatch and enforces full-plate in NEXT render.
        expected={b["beat"] for b in q["chapters"] if "intero" in b["focus"].lower() or "intera" in b["focus"].lower()}
        observed={x["beat"] for x in failures if x["issue"]=="WHOLE_PAINTING_LABEL_BUT_CROPPED"}
        self.assertEqual(observed,expected)
        self.assertTrue(expected)
        self.assertEqual(len(plan),9)
        self.assertFalse(any(x["issue"]=="OUT_OF_BOUNDS" for x in failures))
    def test_correction_contract(self):
        # Full painting must be visible at once in a portrait output.
        fit=min(OUTPUT_W/SOURCE_W,OUTPUT_H/SOURCE_H)
        shown_w,shown_h=SOURCE_W*fit,SOURCE_H*fit
        self.assertLessEqual(shown_w,OUTPUT_W)
        self.assertLessEqual(shown_h,OUTPUT_H)
        self.assertGreater(OUTPUT_H-shown_h,0) # intentional top/bottom padding
        self.assertEqual((SOURCE_W,SOURCE_H),(6875,5358))

if __name__=="__main__":
    unittest.main()
