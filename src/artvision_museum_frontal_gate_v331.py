#!/usr/bin/env python3
"""ArtVision V331: fail-closed frontal Museum composition geometry gate.

This is not automatic artwork recognition, restoration, photorealism or owner approval.
A reviewer MUST mark the true four INNER painted-canvas corners on PNG frames
actually extracted from the produced Museum MP4 (entry & return). Geometry alone
cannot certify a credible room or temporal smoothness; review full speed as well.

Usage:
    python src/artvision_museum_frontal_gate_v331.py dossier.json --output gate.json
Exit: 0 frontally acceptable for subsequent human review; 2 rejected; 3 bad evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

SHA256 = re.compile(r"^[0-9a-f]{64}$")
ANGLE_DEG = 1.75
SHEAR_DEG = 2.75
CONVERGENCE = .045
RATIO_ERROR = .045
CENTER_OFFSET = .065


def _length(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def evaluate_quad(corners, width, height, artwork_ratio=None):
    """Corners TL, TR, BR, BL in *pixels of final extracted video frame*."""
    if not isinstance(corners, list) or len(corners) != 4:
        raise ValueError("four_inner_painting_corners_TL_TR_BR_BL_required")
    points = []
    for point in corners:
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError("each_corner_must_be_xy_pair")
        x, y = point
        if not all(type(v) in (int, float) and math.isfinite(v) for v in (x, y)):
            raise ValueError("nonfinite_corner")
        if not (0 <= x <= width and 0 <= y <= height):
            raise ValueError("corner_out_of_frame")
        points.append((float(x), float(y)))
    tl, tr, br, bl = points
    top = _length(tl, tr)
    bottom = _length(bl, br)
    left = _length(tl, bl)
    right = _length(tr, br)
    if min(top, bottom, left, right) < 10:
        raise ValueError("painting_too_small_to_evaluate")
    if tr[0] <= tl[0] or br[0] <= bl[0] or bl[1] <= tl[1] or br[1] <= tr[1]:
        raise ValueError("corners_order_invalid")
    roll = max(abs(math.degrees(math.atan2(tr[1]-tl[1],tr[0]-tl[0]))),
               abs(math.degrees(math.atan2(br[1]-bl[1],br[0]-bl[0]))))
    shear = max(abs(math.degrees(math.atan2(bl[0]-tl[0],bl[1]-tl[1]))),
                abs(math.degrees(math.atan2(br[0]-tr[0],br[1]-tr[1]))))
    convergence_w = abs(top-bottom)/max(top,bottom)
    convergence_h = abs(left-right)/max(left,right)
    center_x = sum(x for x,_ in points)/4
    center_offset = abs(center_x-width/2)/width
    pixel_ratio = ((top+bottom)/2)/((left+right)/2)
    problems=[]
    if roll > ANGLE_DEG:problems.append("picture_is_rolled_relative_to_wall")
    if shear > SHEAR_DEG:problems.append("picture_has_slanted_vertical_edges")
    if convergence_w > CONVERGENCE or convergence_h > CONVERGENCE:
        problems.append("trapezoid_or_oblique_perspective")
    if center_offset > CENTER_OFFSET:problems.append("painting_off_horizontal_center")
    ratio_error=None
    if artwork_ratio is not None:
        if artwork_ratio <= 0 or not math.isfinite(artwork_ratio):
            raise ValueError("invalid_artwork_ratio")
        ratio_error=abs(pixel_ratio/artwork_ratio-1)
        if ratio_error > RATIO_ERROR:
            problems.append("painting_stretched_or_proportions_incorrect")
    return {"passed":not problems,"problems":problems,
            "roll_degrees":round(roll,3),"vertical_shear_degrees":round(shear,3),
            "top_bottom_width_difference":round(convergence_w,5),
            "left_right_height_difference":round(convergence_h,5),
            "horizontal_center_offset_fraction":round(center_offset,5),
            "artwork_apparent_ratio":round(pixel_ratio,5),
            "artwork_ratio_relative_error":None if ratio_error is None else round(ratio_error,5)}


def _sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()


def assess(dossier, base):
    errors=[]
    if dossier.get("schema")!="artvision-museum-frontal-v331":
        errors.append("dossier_schema_invalid")
    if dossier.get("variant") not in ("critico_museum","cinema_museum"):
        errors.append("not_a_museum_variant")
    art=dossier.get("artwork",{})
    try:
        wcm=float(art.get("width_cm",0))
        hcm=float(art.get("height_cm",0))
        if not(wcm>0 and hcm>0):raise ValueError
        ratio=wcm/hcm
    except (TypeError, ValueError):
        errors.append("measured_artwork_cm_required")
        ratio=None
    vid=dossier.get("video",{})
    if not SHA256.fullmatch(str(vid.get("sha256",""))):
        errors.append("real_video_sha256_required")
    # The images are tied to the exact video via a documented full-video digest.
    # For routine QA use a verified mp4 file when available and compare its SHA.
    if vid.get("file"):
        path=(base/vid["file"]).resolve()
        if not path.is_file() or not path.is_relative_to(base.resolve()):
            errors.append("video_file_not_found")
        elif _sha(path)!=vid.get("sha256"):
            errors.append("video_file_hash_mismatch")
    elif vid.get("sha256_attested_by_independent_readback") is not True:
        errors.append("source_video_file_or_independent_readback_required")
    samples=dossier.get("samples")
    if not isinstance(samples,list) or {s.get("role") for s in samples if isinstance(s,dict)} < {"entry_frontal","exit_frontal"}:
        errors.append("both_entry_and_exit_frontal_samples_required")
        samples=[] if not isinstance(samples,list) else samples
    seen=set();records=[]
    for sample in samples:
        if not isinstance(sample,dict) or sample.get("role") not in ("entry_frontal","exit_frontal","approach","withdrawal"):
            errors.append("unknown_sample_role");continue
        role=sample["role"]
        if role in seen and role in ("entry_frontal","exit_frontal"):
            errors.append("duplicate_frontal_role")
        seen.add(role)
        img=sample.get("png")
        if not isinstance(img,str) or Path(img).is_absolute() or ".." in Path(img).parts:
            errors.append(role+"_frame_path_invalid");continue
        im=(base/img).resolve()
        if not im.is_relative_to(base.resolve()) or not im.is_file():
            errors.append(role+"_real_extracted_video_png_not_found");continue
        digest=_sha(im)
        if sample.get("png_sha256")!=digest:
            errors.append(role+"_frame_sha_mismatch");continue
        try:
            from PIL import Image
            with Image.open(im) as pic:
                if pic.format!="PNG":raise ValueError("must_be_png")
                size=pic.size
            if min(size)<320:raise ValueError("sample_resolution_too_low")
            if not isinstance(sample.get("timestamp_s"),(int,float)) or sample["timestamp_s"]<0:
                raise ValueError("sample_timestamp_required")
            m=evaluate_quad(sample.get("painting_inner_corners_px"),*size,artwork_ratio=ratio)
            records.append({"role":role,"timestamp_s":sample["timestamp_s"],
                            "frame_sha256":digest,"image_pixels":size,**m})
            if not m["passed"]:errors.append(role+"_nonfrontal")
        except (ValueError, TypeError, ImportError) as e:
            errors.append(role+"_evaluation_invalid_"+str(e)[:72])
    exc=dossier.get("angled_exception",{})
    exception_requested=isinstance(exc,dict) and exc.get("requested") is True
    if exception_requested:
        if not isinstance(exc.get("artwork_specific_rationale"),str) or len(exc["artwork_specific_rationale"].strip())<30:
            errors.append("angle_exception_requires_specific_storyboard_rationale")
        if exc.get("explicit_owner_artistic_approval") is not True:
            errors.append("angle_exception_not_approved_by_owner")
        if exc.get("preview_viewed_at_full_speed") is not True:
            errors.append("angle_exception_video_review_missing")
        # An exception cannot waive missing real files, dimensions or proven source.
        errors=[x for x in errors if x not in ("entry_frontal_nonfrontal","exit_frontal_nonfrontal",
                                               "approach_nonfrontal","withdrawal_nonfrontal")]
    passed=not errors
    return {"schema":"artvision-museum-frontal-gate-result-v331",
            "passed_geometry_gate":passed,"status":"READY_FOR_ARTISTIC_REVIEW" if passed else "REJECTED",
            "artistic_approval":False,"Gold_V25":False,"publish":False,
            "exception_requested":exception_requested,"samples":records,"errors":list(dict.fromkeys(errors)),
            "thresholds":{"max_roll_degrees":ANGLE_DEG,"max_vertical_shear_degrees":SHEAR_DEG,
                          "max_opposite_edge_convergence_fraction":CONVERGENCE,
                          "max_apparent_artwork_ratio_error":RATIO_ERROR,
                          "max_horizontal_center_offset_fraction":CENTER_OFFSET},
            "disclaimer":"A manual inner-corner annotation on true extracted MP4 frames is required. 2-4 sampled frames do not prove the entire movement stays frontal, or room is authentic. Full speed artistic QA mandatory."}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("dossier",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    try:
        result=assess(json.loads(a.dossier.read_text(encoding="utf8")),a.dossier.parent.resolve())
    except (ValueError, OSError, json.JSONDecodeError) as e:
        result={"status":"INVALID_EVIDENCE","passed_geometry_gate":False,"errors":[str(e)],"artistic_approval":False}
    payload=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output:a.output.write_text(payload,encoding="utf8")
    print(payload)
    raise SystemExit(0 if result.get("passed_geometry_gate") else 2)


if __name__=="__main__":main()
