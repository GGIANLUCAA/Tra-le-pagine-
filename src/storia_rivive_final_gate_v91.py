#!/usr/bin/env python3
"""V91: artistic delivery gate for La Storia Rivive.
Fail closed; does NOT pretend to judge face identity or narrative wow automatically.
A human/visual-reviewer signed manifest is required before declaring 'final'.
Usage: python src/storia_rivive_final_gate_v91.py --video out.mp4 --manifest final_qa.json
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

def validate(manifest, video_info):
    failures=[]
    def need(ok,why):
        if not ok: failures.append(why)
    duration = video_info.get("duration_s")
    need(isinstance(duration,(int,float)) and 14 <= duration <= 35,"duration outside 14–35s")
    need(video_info.get("valid_h264_aac") is True,"missing tested H264/AAC streams")
    need(manifest.get("historic_source_rights_verified") is True,"archival source rights unverified")
    need(manifest.get("actual_frame_to_photo_geometry_verified") is True,"source-to-photo geometry unverified")
    scenes=manifest.get("scenes")
    need(isinstance(scenes,list) and len(scenes)>=4,"not enough approved independent meaningful scenes")
    if not isinstance(scenes,list): scenes=[]
    ids=[x.get("event_id") for x in scenes if isinstance(x,dict)]
    need(bool(ids) and len(ids)==len(scenes) and len(set(ids))==len(ids),
         "duplicate or missing historical source events")
    for i,scene in enumerate(scenes,1):
        if not isinstance(scene,dict):
            failures.append(f"scene {i}: invalid record");continue
        need(scene.get("source_frame_checked") is True,f"scene {i}: true freeze frame not checked")
        need(scene.get("historical_scene_fidelity_approved") is True,f"scene {i}: fidelity not approved")
        need(scene.get("photo_looks_naturally_restored") is True,f"scene {i}: photo visual grade unapproved")
        need(isinstance(scene.get("visual_distinction"),str) and len(scene["visual_distinction"])>=15,
             f"scene {i}: distinct visual contribution not documented")
    need(manifest.get("opening_hook_approved") is True,"opening 0–3s not artistically approved")
    need(manifest.get("strong_ending_approved") is True,"ending: final 2–3s lacks reviewed payoff")
    need(manifest.get("full_reel_watched_with_audio") is True,"entire reel not watched with audio")
    need(manifest.get("rhythm_nonrepetitive_approved") is True,"visual rhythm not approved")
    need(manifest.get("full_video_human_artistic_approval") is True,
         "technical render is not artistic approval")
    if isinstance(duration,(int,float)) and duration < 20:
        need(manifest.get("short_form_exception_approved") is True,
             "14–19.99s may be delivered only as deliberate high-impact short form")
        reason=manifest.get("short_form_justification")
        need(isinstance(reason,str) and len(reason.strip()) >= 50,
             "short reel lacks persuasive documented artistic reason")
    # Most important protection after the failed V90: removing a bad paid AI
    # sequence must trigger a NEW editorial plan, not silently shorten the reel.
    if manifest.get("material_scene_removed_after_plan") is True:
        need(manifest.get("timeline_replanned_after_removal") is True,
             "critical scene cut without redesigning the full storyboard")
        need(manifest.get("new_timeline_artistic_review") is True,
             "shortened master not reapproved after cut")
        need(manifest.get("replacement_or_new_story_approved") is True,
             "rejected scene has no justified replacement or new narrative ending")
    if manifest.get("paid_ai_generation_used") is True:
        need(manifest.get("paid_ai_generation_source_identity_reviewed") is True,
             "charged AI movement lacked human identity/source comparison")
        if manifest.get("paid_ai_scene_rejected") is True:
            need(manifest.get("paid_ai_scene_removed_from_final") is True,
                 "rejected Vidu scene still appears in final")
            need(manifest.get("timeline_replanned_after_removal") is True,
                 "rejected Vidu scene was removed without re-planning")
    need(manifest.get("four_social_posts_present") is True,"4 platform posts missing")
    need(manifest.get("cover_present") is True,"cover missing")
    need(manifest.get("zip_verified") is True,"ZIP not verified")
    # V94 applies only to NEW history reels, not legacy review clips or ArtVision 4x1.
    # No custom renderer may claim 'final' without a real Vidu clip and source-faithful faces.
    import importlib.util
    module_path = Path(__file__).with_name("storia_rivive_quality_gate_v94.py")
    if module_path.is_file():
        spec = importlib.util.spec_from_file_location("storia_quality_v94", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        failures.extend(module.inspect(manifest, phase="delivery"))
        # New 4+1 history reels must pass the *additional* concrete source/photo/Vidu
        # sequencing gate. V95 was allowed through an unrelated legacy exception;
        # never let an H264/AAC or saturation check waive artistic delivery rules.
        if module.is_new_storia(manifest):
            if manifest.get("project_format") == "4classic_1vidu":
                v96_path = Path(__file__).with_name("storia_rivive_v96_guard.py")
                if not v96_path.is_file():
                    failures.append("V96_QUALITY_GATE_NOT_INSTALLED")
                else:
                    v96_spec = importlib.util.spec_from_file_location("storia_quality_v96", v96_path)
                    v96 = importlib.util.module_from_spec(v96_spec)
                    v96_spec.loader.exec_module(v96)
                    new_errors, _ = v96.inspect(manifest, actual_duration=duration)
                    failures.extend("V96: " + e for e in new_errors)
                # V99 reads ACTUAL MP4/source assets independently and compares against
                # immutable, user-accepted SF1906 V98. No boolean-only waiver.
                evidence = manifest.get("v99_benchmark_evidence")
                if not isinstance(evidence, dict) or evidence.get("version") != "V99_GOLDEN_V98_REGRESSION_GATE":
                    failures.append("V99_BENCHMARK_REAL_MP4_REPORT_MISSING")
                else:
                    if evidence.get("passed") is not True:
                        failures.append("V99_BENCHMARK_TECHNICAL_REGRESSION_REJECTED")
                    if evidence.get("reference_sha256") != "b20726893e067bbae493859ae1c51379c4abab8c2c8768d5c6f2d4ab324b47a8":
                        failures.append("V99_APPROVED_GOLDEN_REFERENCE_SHA_NOT_MATCHED")
                    if evidence.get("actual_video_sha256") != video_info.get("sha256"):
                        failures.append("V99_REPORT_NOT_BOUND_TO_THE_EXACT_FINAL_MP4")
            else:
                # Explicitly recorded alternative formats need a dedicated gate;
                # otherwise an unlabelled job can silently skip 4+1 QA again.
                failures.append("V96_EXPLICIT_4CLASSIC_1VIDU_EDITORIAL_PRESET_REQUIRED")
    return failures

def probe(path):
    try:
        d=json.loads(subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name",
             "-of","json",str(path)],capture_output=True,text=True,timeout=30,check=True).stdout)
        codecs={x.get("codec_name") for x in d.get("streams",[])}
        return {"duration_s":float(d["format"]["duration"]),
                "valid_h264_aac":"h264" in codecs and "aac" in codecs}
    except (ValueError,KeyError,subprocess.SubprocessError) as e:
        return {"duration_s":None,"valid_h264_aac":False,"probe_error":str(e)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--video",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--v99-golden-reference",help="Actual immutable V98 video from GitHub release")
    ap.add_argument("--v99-source-assets",help="Directory of actual source film, all 4 I2I photos and the Vidu clip")
    args=ap.parse_args()
    p=Path(args.video);m=Path(args.manifest)
    if not p.is_file() or not m.is_file():
        print(json.dumps({"approved":False,"failures":["video or manifest missing"]}));return 2
    try: data=json.loads(m.read_text(encoding="utf-8"))
    except (ValueError,UnicodeError) as e:
        print(json.dumps({"approved":False,"failures":["manifest invalid: "+str(e)]}));return 2
    # Recalculate V99 against ACTUAL MP4 bytes on every new delivery.
    # Never trust a manifest that merely claims V99 'passed'.
    import hashlib, importlib.util
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    info=probe(p)
    info["sha256"]=h.hexdigest()
    new_storia=(str(data.get("format","")).lower().strip()=="storia_rivive" and
                data.get("project_format")=="4classic_1vidu" and
                (data.get("quality_policy_version")=="V94" or
                 not data.get("production_date") or
                 str(data.get("production_date"))>="2026-10-30"))
    if new_storia:
        if not args.v99_golden_reference or not args.v99_source_assets:
            data["v99_benchmark_evidence"]={"version":"V99_GOLDEN_V98_REGRESSION_GATE",
                "passed":False,"error":"MISSING_REAL_GOLDEN_OR_SOURCE_ASSETS"}
        else:
            try:
                module_path=Path(__file__).with_name("storia_rivive_v99_golden_benchmark.py")
                spec=importlib.util.spec_from_file_location("storia_golden_v99",module_path)
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                baseline=module.approved_reference(args.v99_golden_reference)
                data["v99_benchmark_evidence"]=module.evaluate(p,data,args.v99_source_assets,baseline)
            except Exception as exc:
                data["v99_benchmark_evidence"]={"version":"V99_GOLDEN_V98_REGRESSION_GATE",
                    "passed":False,"error":"V99_REAL_EVIDENCE_ERROR "+type(exc).__name__+": "+str(exc)[:250]}
    fails=validate(data,info)
    print(json.dumps({"approved":not fails,"duration_s":info["duration_s"],
                      "failures":fails},ensure_ascii=False,indent=2))
    return 2 if fails else 0

if __name__=="__main__":
    raise SystemExit(main())
