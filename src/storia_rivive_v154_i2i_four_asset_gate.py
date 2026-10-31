#!/usr/bin/env python3
"""V154: offline byte/provenance preflight for four source-locked I2I photos.

This is an ingestion gate, NOT an image generator, provider receipt verifier,
visual identity judge, license clearance or approval. All four files can pass
mechanical checks while the episode remains blocked for editorial/human QA.
No network, provider calls, tokens or publishing operations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

SHA = re.compile(r"[0-9a-f]{64}\Z")
EXPECTED_EDITORIAL = "V152_EDITORIAL_SOURCE_COHERENCE_BLOCKED"
KNOWN_BAD_VERSION = "V153_KNOWN_I2I_ARTISTIC_REJECTS_V1"


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_file(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise ValueError("V154_UNSAFE_ASSET_PATH")
    parts = Path(rel).parts
    if any(p in ("..", ".") for p in parts):
        raise ValueError("V154_UNSAFE_ASSET_PATH")
    path = root.joinpath(*parts)
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file() or path.is_symlink():
        raise ValueError("V154_MISSING_OR_UNSAFE_REAL_ASSET")
    return path


def _verified_png(root: Path, rel: str, sha: str, expected_size: tuple[int, int]) -> Path:
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ValueError("V154_INVALID_SHA256")
    path = _safe_file(root, rel)
    if _digest(path) != sha:
        raise ValueError("V154_REAL_IMAGE_BYTES_SHA_MISMATCH")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.format != "PNG" or image.size != expected_size:
            raise ValueError("V154_NOT_EXPECTED_REAL_PNG_RASTER")
    return path


def _source_structure_correlation(original: Image.Image, restored: Image.Image) -> float:
    """Cheap rejection of flat images or unrelated compositions, NOT I2I proof.

    Low-resolution luminance preserves major shapes while ignoring hue changes.
    Genuine restorations still require a separate human review of identity.
    """
    size = (64, 64)
    source = list(original.convert("L").resize(size, Image.Resampling.BILINEAR).getdata())
    result = list(restored.convert("L").resize(size, Image.Resampling.BILINEAR).getdata())
    n = len(source)
    mean_source = sum(source) / n
    mean_result = sum(result) / n
    centered_source = [v - mean_source for v in source]
    centered_result = [v - mean_result for v in result]
    variance_source = sum(v * v for v in centered_source)
    variance_result = sum(v * v for v in centered_result)
    if variance_source / n < 16:
        raise ValueError("V155_LOW_DETAIL_SOURCE_NEEDS_REVIEW")
    if variance_result / n < 64:
        raise ValueError("V155_LOW_DETAIL_OR_FLAT_OUTPUT")
    covariance = sum(a * b for a, b in zip(centered_source, centered_result))
    correlation = covariance / (variance_source * variance_result) ** 0.5
    if correlation < 0.25:
        raise ValueError("V155_SOURCE_STRUCTURE_MISMATCH")
    return round(correlation, 4)


def audit(handoff: dict, candidates: dict, root: str | Path, negatives: dict) -> dict:
    root = Path(root)
    if (handoff.get("version") != "V151" or handoff.get("real_source_frames_sha_verified") != 5
            or handoff.get("candidate_i2i_jobs") != 4 or handoff.get("vidu_frame_anchors") != 1
            or any(handoff.get(k) != 0 for k in ("real_restored_photos_generated",
                                                 "real_vidu_clips_generated", "provider_requests_sent", "paid_api_calls"))
            or any(handoff.get(k) is not False for k in ("rights_italy_verified", "artistic_approved", "publish_permitted"))):
        raise ValueError("V154_UNTRUSTED_V151_SOURCE_HANDOFF")
    editorial = handoff.get("editorial_preflight")
    if (not isinstance(editorial, dict) or editorial.get("version") != "V152"
            or editorial.get("status") != EXPECTED_EDITORIAL
            or editorial.get("provider_jobs_may_start") is not False
            or editorial.get("rights_italy_verified") is not False):
        raise ValueError("V154_EDITORIAL_PREFLIGHT_NOT_VERIFIED")
    if (negatives.get("version") != KNOWN_BAD_VERSION
            or negatives.get("not_a_user_approval") is not True
            or negatives.get("production_rights_italy_verified") is not False
            or not isinstance(negatives.get("entries"), list)):
        raise ValueError("V154_NEGATIVE_REGISTRY_NOT_VALID")
    rejected = set()
    for entry in negatives["entries"]:
        if (entry.get("pilot_reuse_permitted") is not False
                or entry.get("serial_production_permitted") is not False
                or entry.get("social_or_site_publication_permitted") is not False
                or not isinstance(entry.get("ai_photo_sha256"), str)
                or not SHA.fullmatch(entry["ai_photo_sha256"])):
            raise ValueError("V154_NEGATIVE_REGISTRY_ENTRY_INVALID")
        rejected.add(entry["ai_photo_sha256"])
    if (candidates.get("version") != "V154" or candidates.get("source_handoff_version") != "V151"
            or any(candidates.get(k) is not False for k in ("rights_italy_verified",
                                                        "human_artistic_approval", "publish_permitted"))):
        raise ValueError("V154_CANDIDATE_CLAIMS_UNVERIFIED_APPROVAL")
    rows = handoff.get("freeze_frames")
    if (not isinstance(rows, list) or len(rows) != 5
            or [r.get("scene") for r in rows] != [1, 2, 3, 4, 5]):
        raise ValueError("V154_INVALID_FIVE_FRAME_HANDOFF")
    for row in rows:
        expected_role = "I2I_PHOTO_CANDIDATE_NOT_GENERATED" if row["scene"] <= 4 else "VIDU_ANCHOR_NOT_SUBMITTED"
        if (row.get("role") != expected_role or not isinstance(row.get("source_id"), str)
                or any(row.get(k) is not False for k in ("image_to_image_sent", "vidu_request_sent",
                                                           "source_subject_artistically_reviewed",
                                                           "face_and_object_fidelity_verified", "rights_italy_verified"))):
            raise ValueError("V154_UNVERIFIED_SOURCE_ROLE_OR_APPROVAL")
        raster = row.get("native_raster")
        if not (isinstance(raster, list) and len(raster) == 2
                and all(type(n) is int and n > 0 for n in raster)):
            raise ValueError("V154_NATIVE_RASTER_NOT_DOCUMENTED")
        _verified_png(root, row["native_original_frame_file"], row["native_original_frame_sha256"], tuple(raster))
        _verified_png(root, row["vertical_review_file"], row["vertical_review_sha256"], (720, 1280))
    jobs = candidates.get("jobs")
    if not isinstance(jobs, list) or len(jobs) > 4:
        raise ValueError("V154_MAX_FOUR_I2I_JOBS")
    if len({j.get("scene") for j in jobs if isinstance(j, dict)}) != len(jobs):
        raise ValueError("V154_DUPLICATE_I2I_SCENE")
    seen_photo_shas = set()
    seen_paths = set()
    completed = []
    for job in jobs:
        if not isinstance(job, dict) or type(job.get("scene")) is not int or job["scene"] not in (1, 2, 3, 4):
            raise ValueError("V154_INVALID_I2I_SCENE")
        row = rows[job["scene"] - 1]
        if (job.get("source_id") != row["source_id"]
                or job.get("source_frame_sha256") != row["native_original_frame_sha256"]
                or job.get("source_crop_sha256") != row["vertical_review_sha256"]
                or job.get("source_crop_file") != row["vertical_review_file"]):
            raise ValueError("V154_I2I_INPUT_SOURCE_FRAME_MISMATCH")
        if (job.get("method") != "generative_image_to_image"
                or not isinstance(job.get("model"), str) or not job["model"].strip()
                or "ddcolor" in job["model"].lower()
                or not isinstance(job.get("provider_request_reference"), str)
                or not job["provider_request_reference"].strip()
                or job.get("human_visual_review") != "pending"
                or job.get("rights_italy_verified") is not False
                or job.get("artistically_approved") is not False):
            raise ValueError("V154_I2I_METHOD_OR_REVIEW_PROVENANCE_INSUFFICIENT")
        photo_rel = job.get("restored_photo_file")
        photo_sha = job.get("restored_photo_sha256")
        if not isinstance(photo_sha, str) or not SHA.fullmatch(photo_sha):
            raise ValueError("V154_INVALID_OUTPUT_SHA")
        photo = _verified_png(root, photo_rel, photo_sha, (720, 1280))
        if photo_rel in seen_paths or photo_sha in seen_photo_shas:
            raise ValueError("V154_DUPLICATE_RESTORED_PHOTO")
        seen_paths.add(photo_rel)
        seen_photo_shas.add(photo_sha)
        if photo_sha in rejected:
            raise ValueError("V154_KNOWN_ARTISTICALLY_REJECTED_I2I_SHA")
        source = _safe_file(root, row["vertical_review_file"])
        with Image.open(photo) as restored, Image.open(source) as original:
            rgb = restored.convert("RGB")
            if ImageChops.difference(rgb, original.convert("RGB")).getbbox() is None:
                raise ValueError("V154_PHOTO_IS_UNCHANGED_SOURCE_NOT_I2I")
            stats = ImageStat.Stat(rgb)
            if max(stats.mean) - min(stats.mean) < 2.0:
                raise ValueError("V154_OUTPUT_STILL_GRAYSCALE")
            structure_corr = _source_structure_correlation(original, rgb)
        completed.append({"scene": job["scene"], "source_frame_sha256": row["native_original_frame_sha256"],
                          "actual_photo_sha256": photo_sha, "provider_reference_is_self_reported": True,
                          "source_structure_correlation": structure_corr, "human_identity_review_still_required": True})
    missing = sorted(set(range(1, 5)) - {j["scene"] for j in jobs})
    # V152 source selection is still blocked. Even four technically valid files
    # cannot turn it into a coherent, rights-cleared, artistically approved film.
    return {"version": "V154", "status": "V154_SOURCE_EDITORIAL_BLOCKED" if not missing else "V154_I2I_ASSETS_PENDING_AND_EDITORIAL_BLOCKED",
            "real_i2i_photo_files_sha_verified": len(completed), "missing_i2i_scenes": missing,
            "verified_byte_evidence": completed, "model_invocation_independently_verified": False,
            "five_shot_coherence_verified": False, "rights_italy_verified": False,
            "face_object_identity_verified": False, "human_artistic_approval": False,
            "vidu_clip_generated": False, "master_eligible": False,
            "provider_jobs_may_start": False, "publish_permitted": False,
            "provider_requests_made_by_this_audit": 0, "credits_spent_by_this_audit": 0}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--handoff", required=True)
    p.add_argument("--candidates", required=True)
    p.add_argument("--assets", required=True)
    p.add_argument("--reject-registry", default="config/storia_rivive_v153_rejected_i2i_samples.json")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = audit(json.loads(Path(args.handoff).read_text(encoding="utf-8")),
                   json.loads(Path(args.candidates).read_text(encoding="utf-8")),
                   args.assets, json.loads(Path(args.reject_registry).read_text(encoding="utf-8")))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["status"], "verified_i2i_files", result["real_i2i_photo_files_sha_verified"],
          "master_eligible", False, "paid", 0)
