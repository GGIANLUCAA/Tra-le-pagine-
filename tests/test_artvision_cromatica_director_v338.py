#!/usr/bin/env python3
"""Regression gate for V338: every owner-selected artwork must have a distinct editorial structure."""
import ast, json, pathlib, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"tools"))
from artvision_cromatica_director_v338 import DIRECTION,shot_plan_for,audit_uniqueness

works=[{"slug":slug,"focus":[(.2,.2),(.4,.7),(.8,.25),(.6,.55),(.3,.85),(.77,.8)]} for slug in DIRECTION]
report=audit_uniqueness(works)
assert report["plans"]==7, report
assert report["unique_signatures"]==report["plans"], report
assert len(report["unique_shot_counts"])>=3, report
assert len(report["openings"])>=2 and len(report["finales"])>=2, report
assert report["duration_range_seconds"][1]-report["duration_range_seconds"][0]>=5.0,report
assert report["minimum_entire_work_seconds"]>=7.0,report
plans=[shot_plan_for(work) for work in works]
for p in plans:
    assert p["concept"] and p["whole_seconds"]>=7
    assert 7<=len(p["shots"])<=15
    assert any(s["kind"]=="detail" and s["a"]!=s["b"] for s in p["shots"])
    assert any(s["kind"]=="detail" and s["a"]==s["b"] for s in p["shots"])
    assert all(s["why"] for s in p["shots"])
    assert len(set((s["kind"],round(s["dur"],1)) for s in p["shots"]))>=5
# The V338 script is parseable and isolated from the V337 originals.
script=pathlib.Path("tools/artvision_owner30_cromatica_reels_v338.py")
ast.parse(script.read_text(encoding="utf8"))
s=script.read_text(encoding="utf8")
assert 'from artvision_cromatica_director_v338 import shot_plan_for' in s
assert 'output/artvision_owner30_cromatica_v338' in s
assert 'output/artvision_owner30_cromatica")' not in s
assert 'DIRECTOR["shots"]' in s and 'DIRECTOR["title_mode"]' in s
assert 'tweak=[rng.choice' not in s and 'D(3.6,0)' not in s
result={"status":"PASS","editorial_diversity":report,
        "source_master_preserved":True,
        "pending_artistic_review":True,
        "new_master_rendered_in_this_test":False,
        "examples":[{"slug":p["slug"],"concept":p["concept"],"duration":p["duration"],
                     "n_shots":len(p["shots"]),"full_image_seconds":p["whole_seconds"],
                     "opening":p["editing_signature"][0],
                     "closing":p["editing_signature"][-1]} for p in plans]}
out=pathlib.Path("output/artvision_v338");out.mkdir(parents=True,exist_ok=True)
(out/"EDITORIAL_DIVERSITY_TEST.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
