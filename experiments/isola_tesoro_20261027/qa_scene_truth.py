"""Optional QA for new book-video editorial plans. Leaves approved pipelines untouched.

Usage:
 python experiments/isola_tesoro_20261027/qa_scene_truth.py REGIA_SCENE.json
This gate validates metadata honesty and evidence-based scene cue mapping,
not artistic excellence or actual ASR accuracy.
"""
import json,sys
from pathlib import Path

ALLOWED_EFFECTS={"none","character_stroke","object_stroke","layered_ink","color_bloom","light_reveal","environment_pan","static"}
def validate(plan):
    problems=[]
    if plan.get("estimated_timing") is True:
        problems.append("VOICE_NOT_ALIGNED: voice timing is estimated, not verified")
    scenes=plan.get("scenes",[])
    if not scenes:
        problems.append("SCENES_MISSING")
    last=0.0
    image_use={}
    for i,s in enumerate(scenes):
        at=f"scene[{i}]"
        for field in ("spoken_phrase","visual_subject","depicted_action","image","source","asset_checked"):
            if s.get(field) in (None,"",False):
                problems.append(f"{at} MISSING_{field.upper()}")
        if not (isinstance(s.get("start"),(int,float)) and isinstance(s.get("end"),(int,float))):
            problems.append(f"{at} TIMING_MISSING")
        else:
            if s["start"] < last or s["end"] <= s["start"]:
                problems.append(f"{at} TIMING_INVALID")
            last=s["end"]
        if s.get("effect") not in ALLOWED_EFFECTS:
            problems.append(f"{at} EFFECT_NOT_SEMANTIC: {s.get('effect')!r}")
        if s.get("effect") not in (None,"none","static") and not s.get("effect_subject"):
            problems.append(f"{at} EFFECT_SUBJECT_MISSING")
        key=s.get("image")
        if key is not None:
            if key in image_use and not s.get("reuse_reason"):
                problems.append(f"{at} IMAGE_REUSED_WITHOUT_REASON: source previously in scene[{image_use[key]}]")
            image_use.setdefault(key,i)
        if s.get("storyboard_crop") is True:
            problems.append(f"{at} STORYBOARD_CROP_FORBIDDEN")
    return problems
def main():
    plan=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errors=validate(plan)
    if errors:
        for e in errors:print("NOT_READY:",e)
        raise SystemExit(2)
    print("METADATA_CHECK_PASSED; manual voice/visual review still required")
if __name__=="__main__":
    main()
