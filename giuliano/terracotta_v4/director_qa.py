#!/usr/bin/env python3
"""Read-only documentary director gate. Warnings require human visual review."""
import argparse, json, statistics
from pathlib import Path

def audit(qa):
    scenes=qa.get("scene_to_sentence_alignment") or []
    if not scenes: raise ValueError("Missing timed scene alignment")
    issues=[]; durations=[]
    for i,s in enumerate(scenes,1):
        dur=float(s["visual_end_sec"])-float(s["visual_start_sec"])
        durations.append(dur)
        if dur>5:issues.append({"scene":i,"code":"LONG_HOLD","seconds":round(dur,2),"severity":"warning"})
        if dur<1.1:issues.append({"scene":i,"code":"FLASH_CUT","seconds":round(dur,2),"severity":"warning"})
        if s.get("same_subject_fallback"):issues.append({"scene":i,"code":"FALLBACK_IMAGE","severity":"warning"})
        text=s.get("sentence","").lower(); subject=s.get("subject","").lower()
        semantic={"scarpe":["footwear","shoes","feet"],"frecce":["weapons","arrow"],
                  "arcieri":["archer"],"cavalli":["horse","chariot"],
                  "mausoleo":["mound","tomb","pit"],"colori":["pigment","reconstruction"],
                  "volti":["portrait","officer","armour"]}
        for word,accepted in semantic.items():
            if word in text and not any(a in subject for a in accepted):
                issues.append({"scene":i,"code":"SEMANTIC_REVIEW","spoken_term":word,
                               "visual_label":subject,"severity":"review"})
    if not any(s.get("subject") in ("formation","pit","wide_hook") for s in scenes[:3]):
        issues.append({"scenes":[1,2,3],"code":"HOOK_NO_ARMY_WIDE","severity":"critical"})
    return {"status":"ARTISTIC_REVIEW_REQUIRED","scene_count":len(scenes),
            "duration_seconds":round(float(scenes[-1]["visual_end_sec"]),2),
            "mean_shot_seconds":round(statistics.mean(durations),2),
            "median_shot_seconds":round(statistics.median(durations),2),
            "long_holds_over_5s":sum(d>5 for d in durations),
            "issues":issues,"critical_count":sum(x["severity"]=="critical" for x in issues),
            "warning_count":sum(x["severity"]=="warning" for x in issues),
            "review_count":sum(x["severity"]=="review" for x in issues),
            "caveat":"Heuristic checks do not verify actual photo contents or artistic impact."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("qa_json",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    result=audit(json.loads(args.qa_json.read_text(encoding="utf8")))
    output=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.out:args.out.write_text(output,encoding="utf8")
    print(output)
    return 2 if result["critical_count"] else 0

if __name__=="__main__":
    raise SystemExit(main())
