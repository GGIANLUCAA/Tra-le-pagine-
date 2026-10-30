#!/usr/bin/env python3
"""Vidu ChatGPT Project Gateway v1.

Reusable from ANY chat with write access to the connected GitHub repository:
  1. Create one unique requests/vidu/<request-id>.json file.
  2. The push workflow discovers exactly that file and runs the requested operation.
  3. Read job artifacts/preview release URLs.

All provider billable operations require a plan-derived approval code plus the
explicit user authorization phrase for ONE clip. Unique GitHub ledger is created
BEFORE the ONE possible POST. Never retry a paid POST, including HTTP timeouts.
No video secrets, private balances or account information in public releases.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.request
import urllib.parse

HERE = pathlib.Path("output/vidu_project_gateway")
API = "https://api.vidu.com"
REPO = os.environ.get("GITHUB_REPOSITORY", "GGIANLUCAA/Tra-le-pagine-")
VIDU_KEY = os.environ.get("VIDU_API_KEY", "")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{7,63}$")
RELEASE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,110}$")
ASSET_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,120}\.(?:png|jpg|jpeg|webp)$", re.I)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COLLECT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,120}$")


class GateError(RuntimeError):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def jdump(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd(args, timeout=90):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise GateError("COMMAND_FAILED " + " ".join(map(str, args[:5])) + " " + result.stderr[-500:])
    return result.stdout


def request_file(path):
    path = pathlib.Path(path)
    if not re.fullmatch(r"requests/vidu/[a-z0-9][a-z0-9-]{7,63}\.json", path.as_posix()):
        raise GateError("ONLY_UNIQUE_REQUEST_FILES_IN_requests/vidu_ALLOWED")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "vidu_project_gateway_v1":
        raise GateError("WRONG_REQUEST_SCHEMA")
    if not ID_RE.fullmatch(data.get("request_id", "")) or path.stem != data["request_id"]:
        raise GateError("REQUEST_FILE_ID_MISMATCH")
    if data.get("mode") not in ("balance", "plan", "generate", "collect"):
        raise GateError("INVALID_MODE")
    return data


def validate_common(data):
    if data["mode"] == "balance":
        return
    if data["mode"] == "collect":
        source_id = data.get("collect_request_id")
        if not isinstance(source_id, str) or not ID_RE.fullmatch(source_id):
            raise GateError("COLLECT_REQUIRES_KNOWN_SOURCE_REQUEST_ID")
        return
    src = data.get("source")
    clip = data.get("clip")
    if not isinstance(src, dict) or not isinstance(clip, dict):
        raise GateError("SOURCE_AND_CLIP_REQUIRED")
    if not RELEASE_RE.fullmatch(src.get("release_tag", "")) or not ASSET_RE.fullmatch(src.get("asset_name", "")):
        raise GateError("SOURCE_MUST_BE_IMAGE_FROM_THIS_REPOSITORY_GITHUB_RELEASE")
    if not SHA_RE.fullmatch(src.get("sha256", "")):
        raise GateError("SOURCE_EXACT_SHA256_REQUIRED")
    if src.get("subject_reviewed_by_user") is not True:
        raise GateError("IMAGE_SUBJECT_MUST_BE_VISUALLY_MATCHED_TO_PROMPT_BEFORE_SPENDING")
    if not isinstance(src.get("provenance_url"), str) or not src["provenance_url"].startswith("https://"):
        raise GateError("IMAGE_PROVENANCE_URL_REQUIRED")
    prompt = clip.get("prompt")
    if not isinstance(prompt, str) or not 45 <= len(prompt.strip()) <= 2900:
        raise GateError("PRECISE_PHYSICAL_MOTION_PROMPT_REQUIRED")
    if clip.get("model") != "viduq2-pro-fast" or clip.get("resolution") != "720p":
        raise GateError("ONLY_VERIFIED_Q2_PRO_FAST_720P_PRESET")
    if type(clip.get("seconds")) is not int or not 2 <= clip["seconds"] <= 8:
        raise GateError("DURATION_MUST_BE_BETWEEN_2_AND_8")
    if clip.get("off_peak") is not False:
        raise GateError("ONLY_NORMAL_PRICING_VERIFIED_IN_V1")
    if clip.get("audio") is not False:
        raise GateError("PAID_AUDIO_NOT_SUPPORTED")
    if clip.get("color_reveal_first_second") not in (True, False):
        raise GateError("EXPLICIT_COLOR_REVEAL_SETTING_REQUIRED")
    format_name = data.get("format")
    if format_name not in ("storia_rivive", "artvision", "tra_le_pagine", "effetti_wow"):
        raise GateError("FORMAT_MUST_BE_EXPLICIT")


def quote(data):
    seconds = data["clip"]["seconds"]
    # Q2 Pro Fast 720p normal rate already confirmed by V84/V86 5s 16 credits.
    return 8 + 2 * (seconds - 1)


def fingerprint(data):
    source = data["source"]
    clip = data["clip"]
    canonical = {
        "source_sha256": source["sha256"],
        "prompt": clip["prompt"],
        "model": clip["model"],
        "resolution": clip["resolution"],
        "seconds": clip["seconds"],
        "off_peak": clip["off_peak"],
        "audio": clip["audio"],
        "color_reveal_first_second": clip["color_reveal_first_second"],
        "credits_estimated": quote(data),
    }
    digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return digest[:12].upper()


def provider(route, body=None, method="GET", timeout=60):
    if not VIDU_KEY:
        raise GateError("VIDU_SECRET_NOT_PRESENT_IN_GITHUB_ACTIONS")
    if not route.startswith("/ent/v2/"):
        raise GateError("UNSUPPORTED_API_ROUTE")
    req = urllib.request.Request(API + route,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Token " + VIDU_KEY,
                 "Accept": "application/json", "Content-Type": "application/json"},
        method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read(1_500_000))


def credit_rows():
    data = provider("/ent/v2/credits")
    rows = data.get("remains", data.get("remaining_credits"))
    if not isinstance(rows, list):
        raise GateError("VIDU_CREDIT_SCHEMA_UNRECOGNIZED_NO_SPEND")
    result = [{"type": str(r.get("type", "credits")),
               "remaining": r.get("credit_remain")} for r in rows if isinstance(r, dict)]
    if not result or any(type(r["remaining"]) not in (int, float) or r["remaining"] < 0 for r in result):
        raise GateError("INVALID_CREDIT_BALANCE_NO_SPEND")
    return result


def source_image(data, output):
    from PIL import Image
    src = data["source"]
    output.mkdir(parents=True, exist_ok=True)
    cmd(["gh", "release", "download", src["release_tag"], "--repo", REPO,
         "-p", src["asset_name"], "-D", str(output)], 150)
    path = output / src["asset_name"]
    if not path.is_file() or not 10_000 <= path.stat().st_size < 9_500_000:
        raise GateError("SOURCE_IMAGE_SIZE_UNEXPECTED")
    if sha256_file(path) != src["sha256"]:
        raise GateError("SOURCE_IMAGE_SHA256_MISMATCH")
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        if min(im.size) < 500 or max(im.size) > 5000 or max(im.size) / min(im.size) > 3:
            raise GateError("SOURCE_IMAGE_NOT_SUITABLE_FOR_VIDEO")
    return path


def ledger_path(request_id):
    if not ID_RE.fullmatch(request_id):
        raise GateError("BAD_LEDGER_IDENTIFIER")
    return "queue/vidu_api_attempts/CHAT_GATEWAY_V1_" + request_id + ".json"


def ledger_create(request_id, data):
    path = ledger_path(request_id)
    payload = base64.b64encode((json.dumps(data, sort_keys=True) + "\n").encode()).decode()
    try:
        cmd(["gh", "api", "-X", "PUT", "repos/" + REPO + "/contents/" + path,
             "-f", "branch=main",
             "-f", "message=Reserve single paid ChatGPT Vidu gateway request " + request_id,
             "-f", "content=" + payload], 65)
    except Exception as exc:
        raise GateError("PAID_REQUEST_LEDGER_ALREADY_EXISTS_OR_UNAVAILABLE_DO_NOT_POST") from exc
    return path


def ledger_read(request_id):
    data = json.loads(cmd(["gh", "api", "repos/" + REPO + "/contents/" + ledger_path(request_id) + "?ref=main"], 45))
    return json.loads(base64.b64decode(data["content"])), data["sha"]


def ledger_update(request_id, doc):
    _, old_sha = ledger_read(request_id)
    content = base64.b64encode((json.dumps(doc, sort_keys=True) + "\n").encode()).decode()
    cmd(["gh", "api", "-X", "PUT", "repos/" + REPO + "/contents/" + ledger_path(request_id),
         "-f", "branch=main", "-f", "sha=" + old_sha,
         "-f", "message=Update existing ChatGPT Vidu task; never submit again",
         "-f", "content=" + content], 65)


def video_processing(original, output, color_reveal):
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(str(original))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width, height = int(cap.get(3)), int(cap.get(4))
    if not (20 <= fps <= 60 and frames > 40 and (width, height) == (720, 1280)):
        raise GateError("PROVIDER_MP4_UNEXPECTED_GEOMETRY_OR_FRAMES")
    process = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-y", "-v", "error",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "720x1280",
         "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)],
        stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    before = None
    changes, sats = [], []
    try:
        for frame in range(frames):
            ok, rgb = cap.read()
            if not ok:
                raise GateError("TRUNCATED_PROVIDER_MP4")
            if color_reveal:
                mono = cv2.cvtColor(cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
                t = frame / fps
                a = max(0, min(1, (t - .04) / .96))
                a = a * a * (3 - 2 * a)
                rgb = cv2.addWeighted(mono, 1 - a, rgb, a, 0)
            process.stdin.write(rgb.tobytes())
            if frame % max(1, round(fps * .45)) == 0:
                small = cv2.cvtColor(cv2.resize(rgb, (180, 320)), cv2.COLOR_BGR2GRAY)
                if before is not None:
                    changes.append({"t": round(frame / fps, 2),
                                    "mean_motion": round(float(np.abs(small.astype("float32") - before.astype("float32")).mean()), 3)})
                before = small
                sats.append({"t": round(frame / fps, 2),
                             "median_saturation": round(float(np.median(cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)[:, :, 1])), 2)})
    finally:
        cap.release()
        process.stdin.close()
        stderr = process.stderr.read().decode(errors="replace")
        if process.wait() != 0:
            raise GateError("VIDEO_ENCODER_FAILED " + stderr[-400:])
    cmd(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(output), "-f", "null", "-"], 150)
    after_1s = [v for v in changes if v["t"] >= 1.1]
    return {"duration": round(frames / fps, 3), "source_frames": frames,
            "color_ramp_applied": color_reveal, "original_motion_not_reconstructed": True,
            "motion_after_first_second_indicated": sum(v["mean_motion"] > .9 for v in after_1s) >= max(3, len(after_1s) // 2),
            "motion_samples": changes, "saturation_samples": sats,
            "human_fidelity_review": "PENDING",
            "technical_review_is_not_artistic_approval": True}


def collect_video(request_id, ledger, output):
    task_id = ledger.get("task_id", "")
    if not isinstance(task_id, str) or not COLLECT_ID_RE.fullmatch(task_id):
        raise GateError("KNOWN_TASK_ID_REQUIRED_TO_COLLECT_WITHOUT_SPENDING")
    response = provider("/ent/v2/tasks/" + task_id + "/creations")
    status = response.get("state")
    if status != "success":
        jdump(output / "PUBLIC_STATUS.json", {
            "mode": "collect", "request_id": request_id,
            "provider_state": status, "new_paid_post": False})
        return False
    creations = response.get("creations") or []
    url = creations[0].get("url") if creations else None
    parsed = urllib.parse.urlparse(url) if isinstance(url, str) else None
    if not parsed or parsed.scheme != "https" or not parsed.netloc:
        raise GateError("VIDU_PROVIDER_HAS_NO_VALID_HTTPS_VIDEO_URL")
    original = output / ("VIDU_" + request_id + "_ORIGINAL.mp4")
    req = urllib.request.Request(url, headers={"User-Agent": "TraLePagineChatViduGateway/1.0"})
    with urllib.request.urlopen(req, timeout=135) as response_file, open(original, "wb") as dest:
        while block := response_file.read(1 << 20):
            dest.write(block)
            if dest.tell() > 80_000_000:
                raise GateError("PROVIDER_VIDEO_EXCEEDS_CAP")
    if original.stat().st_size < 10_000:
        raise GateError("EMPTY_PROVIDER_VIDEO")
    cmd(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(original), "-f", "null", "-"], 150)
    processed = output / ("VIDU_" + request_id + "_COLOR_MOTION.mp4")
    qa = video_processing(original, processed, ledger.get("color_reveal_first_second", True))
    after = credit_rows()
    jdump(output / "PRIVATE_CREDIT_REPORT.json", {
        "request_id": request_id, "task_id": task_id,
        "credit_balance_after": after,
        "provider_reported_credits": response.get("credits", ledger.get("provider_reported_credits")),
        "one_paid_post": True})
    jdump(output / "PUBLIC_STATUS.json", {
        "request_id": request_id, "provider_state": "success",
        "task_id": task_id, "original_video": original.name, "processed_video": processed.name,
        "original_sha256": sha256_file(original), "processed_sha256": sha256_file(processed),
        "review": "TECHNICAL_ONLY_HUMAN_ARTISTIC_QA_REQUIRED", "quality": qa,
        "new_paid_post_during_collection": False})
    ledger["status"] = "video_collected"
    ledger["original_sha256"] = sha256_file(original)
    ledger["processed_sha256"] = sha256_file(processed)
    ledger_update(request_id, ledger)
    print("VIDU_GATEWAY_REAL_VIDEO_DOWNLOADED", request_id, task_id, "5SEC_CLASS_MOTION_QA_READY", flush=True)
    return True


def generate(data, output):
    expected = quote(data)
    spend = data.get("spend")
    if not isinstance(spend, dict) or spend.get("approved_max_credits") != expected:
        raise GateError("EXACT_MAX_CREDIT_APPROVAL_REQUIRED")
    if spend.get("approved_plan_code", "") != fingerprint(data):
        raise GateError("APPROVAL_CODE_MISMATCH_MUST_FIRST_RUN_FREE_PLAN")
    if spend.get("authorization_phrase") != "AUTORIZZO_" + str(expected) + "_CREDITI_VIDU":
        raise GateError("EXPLICIT_SINGLE_TASK_AUTHORIZATION_PHRASE_MISSING")
    if spend.get("user_approved_this_exact_scene") is not True:
        raise GateError("USER_HAS_NOT_AUTHORIZED_THIS_EXACT_SCENE")
    path = source_image(data, output)
    before = credit_rows()
    if not any(x["remaining"] >= expected for x in before):
        raise GateError("INSUFFICIENT_CREDIT_POOL_TO_GENERATE")
    original = {
        "request_id": data["request_id"], "status": "reserved_before_paid_post",
        "paid_post_count": 0, "source_sha256": sha256_file(path),
        "prompt_digest": hashlib.sha256(data["clip"]["prompt"].encode()).hexdigest(),
        "plan_code": fingerprint(data), "model": data["clip"]["model"],
        "max_credits": expected,
        "seconds": data["clip"]["seconds"],
        "color_reveal_first_second": data["clip"]["color_reveal_first_second"],
        "approved_exact_scene": True,
        "created_unix": int(time.time()),
    }
    ledger_create(data["request_id"], original)
    photo = base64.b64encode(path.read_bytes()).decode()
    extension = path.suffix.lower()
    mime = "image/png" if extension == ".png" else "image/webp" if extension == ".webp" else "image/jpeg"
    payload = {
        "model": "viduq2-pro-fast", "resolution": "720p",
        "images": ["data:" + mime + ";base64," + photo],
        "prompt": data["clip"]["prompt"],
        "duration": data["clip"]["seconds"], "off_peak": False,
        "audio": False, "is_rec": False,
        "payload": "chat-gateway-" + data["request_id"]
    }
    # ONE BILLABLE POST. A timeout may mean Vidu accepted it; never retry.
    try:
        submitted = provider("/ent/v2/img2video", payload, "POST", 75)
    except Exception as exc:
        original["status"] = "submission_unknown_NO_PAID_RETRY"
        original["paid_post_count"] = 1
        original["exception_type"] = type(exc).__name__
        ledger_update(data["request_id"], original)
        raise GateError("PAID_SUBMISSION_AMBIGUOUS_STOP_DO_NOT_RESEND") from exc
    original["paid_post_count"] = 1
    task_id = submitted.get("task_id")
    original["status"] = "accepted" if task_id else "provider_no_task_id_NO_PAID_RETRY"
    original["task_id"] = str(task_id or "")
    original["provider_reported_credits"] = submitted.get("credits")
    ledger_update(data["request_id"], original)
    if not task_id:
        raise GateError("VIDU_ACCEPTED_WITHOUT_TASK_ID_DO_NOT_RESUBMIT")
    if type(submitted.get("credits")) not in (float, int) or submitted["credits"] > expected:
        raise GateError("VIDU_BILLING_EXCEEDED_PREAPPROVED_MAX_NO_MORE_POST")
    jdump(output / "PRIVATE_CREDIT_REPORT.json", {
        "request_id": data["request_id"], "task_id": task_id,
        "balance_before": before, "credits_provider": submitted["credits"]})
    print("VIDU_GATEWAY_SUBMITTED_SINGLE", data["request_id"], "task_id", task_id,
          "credits_reported", submitted["credits"], flush=True)
    for attempt in range(55):
        time.sleep(10)
        try:
            state = provider("/ent/v2/tasks/" + str(task_id) + "/creations", timeout=35)
        except Exception:
            continue  # GET-only polling, never another POST
        status = state.get("state")
        if status == "success":
            return collect_video(data["request_id"], original, output)
        if status in ("failed", "cancelled"):
            original["status"] = status
            ledger_update(data["request_id"], original)
            raise GateError("VIDU_GENERATION_FAILED_NO_PAID_RETRY")
    original["status"] = "poll_timeout_GET_COLLECT_LATER_ONLY"
    ledger_update(data["request_id"], original)
    jdump(output / "PUBLIC_STATUS.json", {
        "mode": "generate", "request_id": data["request_id"], "task_id": str(task_id),
        "provider_state": "pending_collect", "no_paid_retry": True})
    print("VIDU_GATEWAY_SUBMITTED_NOT_READY_COLLECT_LATER", data["request_id"], flush=True)
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    options = parser.parse_args()
    data = request_file(options.request)
    validate_common(data)
    output = HERE / data["request_id"]
    output.mkdir(parents=True, exist_ok=True)
    mode = data["mode"]
    public_release = bool(data.get("distribution", {}).get("github_public_preview", False))
    if public_release and mode not in ("generate", "collect"):
        raise GateError("ONLY_VIDEO_GENERATIONS_ALLOW_PREVIEW_RELEASE")
    if mode == "balance":
        values = credit_rows()
        jdump(output / "PRIVATE_CREDIT_REPORT.json", {"pools": values, "mode": "balance"})
        jdump(output / "PUBLIC_STATUS.json", {"mode": "balance", "api_access_ok": True,
                                               "new_credits_spent": 0})
        print("VIDU_GATEWAY_BALANCE_READ_ONLY_OK", flush=True)
    elif mode == "plan":
        path = source_image(data, output)
        info = {"request_id": data["request_id"], "source_image": path.name,
                "source_sha256": sha256_file(path), "model": data["clip"]["model"],
                "seconds": data["clip"]["seconds"],
                "estimated_credits": quote(data),
                "approval_code": fingerprint(data),
                "approval_phrase": "AUTORIZZO_" + str(quote(data)) + "_CREDITI_VIDU",
                "paid_post": False,
                "to_generate": "Create a NEW unique generate request with the exact same source, clip and approval code; only after explicit user authorization"}
        jdump(output / "FREE_PLAN.json", info)
        jdump(output / "PUBLIC_STATUS.json", {"mode": "plan", "planned": True,
                                               "estimated_credits": quote(data),
                                               "new_credits_spent": 0})
        print("VIDU_GATEWAY_FREE_PLAN_READY", info["approval_code"], flush=True)
    elif mode == "generate":
        generate(data, output)
    else:
        source_id = data["collect_request_id"]
        record, _ = ledger_read(source_id)
        collect_video(source_id, record, output)
    jdump(output / "GATEWAY_RUN.json", {
        "schema": data["schema"], "request_id": data["request_id"], "mode": mode,
        "private_credit_report_not_for_public_release": True,
        "github_public_preview_requested": public_release,
        "source_chat_independent": True,
        "user_must_review_ai_semantics": True})
    print("VIDU_GATEWAY_COMPLETE", mode, data["request_id"], flush=True)


if __name__ == "__main__":
    main()
