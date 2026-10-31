#!/usr/bin/env python3
"""V151: byte-verified native freeze frames for 4 I2I jobs + 1 Vidu anchor.

Only prepares ORIGINAL historical pixels and an editorial contact sheet.
Never generates AI imagery, approves identity/rights, calls a provider, spends
credits, submits a gateway request or grants permission to publish.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

try:
    from src.storia_rivive_v149_authentic_bw_proxy import validate, sha256_file
    from src.storia_rivive_v150_longer_bw_review import EXTRA_MS, STATUS as CLIP_STATUS
    from src.storia_rivive_i2i_prepare_v102 import PROMPT, NEGATIVE
except ModuleNotFoundError:
    from storia_rivive_v149_authentic_bw_proxy import validate, sha256_file
    from storia_rivive_v150_longer_bw_review import EXTRA_MS, STATUS as CLIP_STATUS
    from storia_rivive_i2i_prepare_v102 import PROMPT, NEGATIVE

BATCH_STATUS = "V150_EXTENDED_BW_SOURCE_BATCH_READY"
OUTPUT_STATUS = "V151_FIVE_EXACT_SOURCE_FRAMES_PREPARED_AWAITING_HUMAN_SOURCE_AND_RIGHTS_REVIEW"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def read_verified_inputs(manifest, artifact_root):
    """Fail closed if source frame PNGs were not actually exported from V150."""
    m = json.loads(Path(manifest).read_text(encoding="utf-8"))
    sources = validate(m)
    if (m["photo_i2i_allowed"] is not False or
            m["vidu_allowed"] is not False or m["publish_allowed"] is not False
            or m["artistic_approved"] is not False
            or m["rights_italy_verified"] is not False):
        raise ValueError("V151_UNAUTHORIZED_PRESUMED_APPROVAL")

    root = Path(artifact_root)
    reports = list(root.rglob("V150_BATCH_REPORT.json"))
    if len(reports) != 2:
        raise ValueError("V151_REQUIRES_EXACT_TWO_V150_BATCH_REPORTS")
    batches = {}
    for file in reports:
        if file.is_symlink():
            raise ValueError("V151_SYMLINK_BATCH_REPORT")
        data = json.loads(file.read_text(encoding="utf-8"))
        name = data.get("batch")
        if (name not in ("a", "b") or name in batches
                or data.get("status") != BATCH_STATUS
                or data.get("paid_api_calls") != 0
                or data.get("is_finished_video") is not False
                or data.get("publish_permitted") is not False
                or data.get("artistic_approved") is not False
                or data.get("rights_italy_verified") is not False
                or data.get("real_i2i_generated") != 0
                or data.get("real_vidu_generated") != 0):
            raise ValueError("V151_UNVERIFIED_OR_DUPLICATE_SOURCE_BATCH")
        batches[name] = (file.parent, data)
    if set(batches) != {"a", "b"}:
        raise ValueError("V151_BOTH_SOURCE_BATCHES_REQUIRED")

    checked = []
    for source in sources:
        batch_path, report = batches[source["batch"]]
        rows = [r for r in report.get("sources", [])
                if r.get("scene") == source["scene"]]
        if len(rows) != 1:
            raise ValueError("V151_SOURCE_ROW_MISSING_OR_DUPLICATE")
        row = rows[0]
        index = source["scene"]
        name = f"scene_{index:02d}_V150_BW_LONGER.mp4"
        if (row.get("status") != CLIP_STATUS
                or row.get("id") != source["id"]
                or row.get("source_page") != source["source_page"]
                or row.get("original_sha256") != source["original_sha256"]
                or row.get("freeze_frame_sha256") != source["frame_sha256"]
                or row.get("start_pts") != source["start_pts"] - EXTRA_MS
                or row.get("freeze_pts") != source["freeze_pts"]
                or row.get("time_base") != source["time_base"]
                or row.get("clip_filename") != name
                or row.get("artistic_approved") is not False
                or row.get("rights_italy_verified") is not False
                or row.get("paid_api_calls") != 0
                or not math.isfinite(row.get("seconds", float("nan")))
                or not 2.28 <= row["seconds"] <= 2.53
                or not isinstance(row.get("clip_sha256"), str)
                or not SHA256.fullmatch(row["clip_sha256"])):
            raise ValueError("V151_FRAME_MOVIE_SOURCE_PTS_ROLE_MISMATCH")
        clip = batch_path / "preview" / name
        native = batch_path / "originals" / source["id"] / "EXACT_FREEZE.png"
        for path in (clip, native):
            if not path.is_file() or path.is_symlink():
                raise ValueError("V151_MISSING_REAL_CLIP_OR_EXACT_NATIVE_PNG")
        if sha256_file(clip) != row["clip_sha256"]:
            raise ValueError("V151_REAL_MP4_BYTES_SHA_MISMATCH")
        if sha256_file(native) != source["frame_sha256"]:
            raise ValueError("V151_EXACT_NATIVE_PNG_BYTES_SHA_MISMATCH")
        with Image.open(native) as photo:
            photo.verify()
        with Image.open(native) as photo:
            if photo.format != "PNG":
                raise ValueError("V151_NOT_A_REAL_NATIVE_PNG")
            width, height = photo.size
        if not (width >= 1280 and height >= 720 and width > height):
            raise ValueError("V151_NATIVE_IMAGE_RASTER_INADEQUATE")
        crop_width = (int(height * 9 / 16) // 2) * 2
        if crop_width < 480 or crop_width > width:
            raise ValueError("V151_NATIVE_VERTICAL_CROP_TOO_SMALL")
        checked.append((source, native, clip, (width, height), crop_width))
    if len({source["original_sha256"] for source, *_ in checked}) != 5:
        raise ValueError("V151_NOT_FIVE_REAL_SOURCE_MOVIES")
    return checked


def prepare(manifest, artifact_root, destination):
    frames = read_verified_inputs(manifest, artifact_root)
    out = Path(destination)
    originals = out / "native_frames"
    crops = out / "review_crops"
    originals.mkdir(parents=True, exist_ok=True)
    crops.mkdir(parents=True, exist_ok=True)
    rows = []
    thumbs = []
    for source, native, clip, (width, height), crop_width in frames:
        index = source["scene"]
        original_name = f"scene_{index:02d}_NATIVE_FREEZE.png"
        original_out = originals / original_name
        shutil.copyfile(native, original_out)
        if sha256_file(original_out) != source["frame_sha256"]:
            raise ValueError("V151_COPIED_SOURCE_NATIVE_PNG_CHANGED")
        left = (width - crop_width) // 2
        crop_name = f"scene_{index:02d}_SOURCE_CROP_720x1280.png"
        crop_out = crops / crop_name
        with Image.open(native) as image:
            roi = image.convert("RGB").crop((left, 0, left + crop_width, height))
            roi = roi.resize((720, 1280), Image.Resampling.LANCZOS)
            roi.save(crop_out, format="PNG")
        with Image.open(crop_out) as image:
            image.verify()
        rows.append({
            "scene": index, "role": (
                "I2I_PHOTO_CANDIDATE_NOT_GENERATED" if index <= 4
                else "VIDU_ANCHOR_NOT_SUBMITTED"),
            "source_id": source["id"],
            "source_page": source["source_page"],
            "source_film_sha256": source["original_sha256"],
            "native_original_frame_file": "native_frames/" + original_name,
            "native_original_frame_sha256": source["frame_sha256"],
            "native_original_frame_pts": source["freeze_pts"],
            "native_time_base": source["time_base"],
            "native_raster": [width, height],
            "source_crop_pixels": {"left": left, "width": crop_width,
                                   "top": 0, "height": height},
            "vertical_review_file": "review_crops/" + crop_name,
            "vertical_review_sha256": sha256_file(crop_out),
            "vertical_review_raster": [720, 1280],
            "source_bw_video_sha256": sha256_file(clip),
            "provider": None, "image_to_image_sent": False,
            "image_to_image_output": None, "vidu_request_sent": False,
            "source_subject_artistically_reviewed": False,
            "face_and_object_fidelity_verified": False,
            "rights_italy_verified": False,
            "provider_credit_budget_approved": False,
            "prompt_candidate": PROMPT if index <= 4 else None,
            "negative_prompt_candidate": NEGATIVE if index <= 4 else None,
            "gateway_requires_scene_specific_approval": index == 5,
        })
        with Image.open(crop_out) as im:
            thumbs.append(im.convert("RGB").resize((216, 384), Image.Resampling.LANCZOS))
    sheet = Image.new("RGB", (5 * 216, 420), "white")
    draw = ImageDraw.Draw(sheet)
    for i, image in enumerate(thumbs):
        sheet.paste(image, (i * 216, 0))
        draw.text((i * 216 + 6, 392), f"SCENE {i + 1:02d}  SOURCE ONLY", fill="black")
    sheet.save(out / "V151_FIVE_ORIGINAL_FRAMES_VISUAL_REVIEW.jpg", quality=92)
    result = {
        "version": "V151",
        "status": OUTPUT_STATUS,
        "real_source_frames_sha_verified": 5,
        "candidate_i2i_jobs": 4,
        "vidu_frame_anchors": 1,
        "real_restored_photos_generated": 0,
        "real_vidu_clips_generated": 0,
        "provider_requests_sent": 0,
        "paid_api_calls": 0,
        "source_photography_genuinely_colorized": False,
        "source_subjects_are_a_coherent_single_episode_verified": False,
        "five_different_camera_shots_artistically_verified": False,
        "rights_italy_verified": False,
        "artistic_approved": False,
        "gateway_scene_permission_granted": False,
        "publish_permitted": False,
        "freeze_frames": rows,
        "next_action": "Human visual + territorial rights review; choose one coherent episode; only then genuine I2I/provider and approved Vidu plan."
    }
    (out / "V151_SOURCE_LOCKED_HANDOFF.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", default="config/storia_rivive_v149_five_original_motion_preview.json")
    p.add_argument("--artifacts", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    report = prepare(args.manifest, args.artifacts, args.out)
    print("V151", report["status"], "frames", report["real_source_frames_sha_verified"],
          "paid", 0, "AI_photos", 0, "Vidu", 0, "published", False)
