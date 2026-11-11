#!/usr/bin/env python3
"""AI Director V1: optional editorial co-pilot for Tra le Pagine.

Pure-stdlib offline preflight, scenario review, safe OpenRouter free-only
comparison, and Android-readable report. Never renders, publishes, approves
artistic quality, or changes another project's output.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

from free_llm_zero_cost_v1 import ZeroCostPolicyError, admit, load_policy

SCHEMA = "ai-director-v1"
FORMATS = ("artvision_4x1", "storia_rivive", "wow_lab", "documentario", "giuliano")
ISSUE_LEVELS = ("blocking", "warning", "info")
ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT = 18_000
MAX_OUTPUT = 250_000
MAX_SCENES = 120
VIDEO_EXT = {".mp4", ".mov"}
MODEL_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/+-]{1,140}$")

SYSTEM = (
    "You are a professional documentary film editor working in a historical "
    "video studio. Produce an UNAPPROVED DRAFT, not an approved film. "
    "Base claims only on the supplied source notes. Clearly mark uncertain "
    "facts and do not fabricate citations, image rights, museum installation, "
    "footage or human approvals. Narration and images must correspond precisely. "
    "Make scene durations meaningful, avoid flashes under one second, repeated "
    "generic zooms, AI-style moralizing questions, and interchangeable conclusions. "
    "Don't claim you watched footage or heard audio. Preserve existing 4x1 "
    "variants, genuine museum scale, natural storytelling and documentary truth."
)

FORMAT_GUIDANCE = {
    "artvision_4x1": (
        "Keep exactly four variants: critico_standard, critico_museum, "
        "cinema_standard, cinema_museum. Critico variants share narration. "
        "Document physical canvas dimensions, frame and gallery provenance "
        "before proposing a Museum scene; never invent a museum installation."
    ),
    "storia_rivive": (
        "Storyboard documentary silent historical footage with a real "
        "black-and-white to credible color transition. Avoid fake restoration, "
        "wrong-perspective Vidu shots, invented faces, and blink-and-you-miss-it stills. "
        "Historic film and generated motion must be clearly distinguished."
    ),
    "wow_lab": "Favor source fidelity, meaningful camera movement and striking but plausible visuals.",
    "documentario": "Write concrete informative narration with semantically synchronized shots.",
    "giuliano": "Use diverse documentary images with enough screen time to be perceptible; avoid micro-flashes.",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def issue(code, level, message, scene=None):
    item = {"code": code, "severity": level, "message": message}
    if scene is not None:
        item["scene"] = str(scene)
    return item


def load_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 2_000_000:
        raise ValueError("Input JSON file missing or exceeds 2MB")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    return data


def clean(value, maxlen=MAX_INPUT):
    if not isinstance(value, str):
        return ""
    return value.strip()[:maxlen]


def make_brief(fmt, subject):
    if fmt not in FORMATS:
        raise ValueError("Unknown video format")
    subject = clean(subject, 250)
    if len(subject) < 3:
        raise ValueError("Subject must be at least three characters")
    return {
        "schema": SCHEMA, "format": fmt, "subject": subject,
        "source_notes": [], "narration": "",
        "scenes": [], "video_path": "",
        "status": "draft_unreviewed",
        "human_artistic_approval": False, "publication_authorized": False,
    }


def validate_brief(brief):
    if brief.get("schema") != SCHEMA:
        raise ValueError("Unsupported brief schema")
    if brief.get("format") not in FORMATS or len(clean(brief.get("subject"), 250)) < 3:
        raise ValueError("Valid subject and format required")
    if not isinstance(brief.get("source_notes"), list) or len(brief["source_notes"]) > 60:
        raise ValueError("source_notes must be an array, maximum 60 items")
    if not isinstance(brief.get("scenes"), list) or len(brief["scenes"]) > MAX_SCENES:
        raise ValueError("scenes must be an array, maximum 120")
    if brief.get("human_artistic_approval") is True or brief.get("publication_authorized") is True:
        raise ValueError("AI Director does not accept approval or publication claims")
    return brief


def editorial_prompts(brief):
    validate_brief(brief)
    source_notes = brief["source_notes"]
    verified = []
    for x in source_notes:
        if not isinstance(x, dict):
            continue
        if clean(x.get("url"), 500).startswith("https://") and clean(x.get("observation"), 1500):
            verified.append({"url": clean(x["url"], 500), "observation": clean(x["observation"], 1500),
                             "license": clean(x.get("license"), 120) or "UNVERIFIED"})
    payload = json.dumps({
        "format": brief["format"], "subject": brief["subject"],
        "source_notes_user_supplied_unverified": verified[:30],
        "narration_user_supplied": clean(brief.get("narration"), 6000),
        "scenes_user_supplied": brief["scenes"][:50],
    }, ensure_ascii=False)
    prompt = (FORMAT_GUIDANCE[brief["format"]] + "\nOnly use user-provided evidence. "
              "Provide: 1) the unique dramatic premise, 2) scene-by-scene storyboard "
              "with meaningful timing and visual/voice alignment, 3) uncertain claims "
              "requiring independent sources, 4) a sober specific ending. "
              "Do not invent asset files or image rights.\nINPUT:\n" + payload)
    if len(prompt) > MAX_INPUT:
        raise ValueError("Editorial input exceeds 18k characters; reduce sources")
    return {
        "director": SYSTEM + "\nROLE: Film director. " + prompt,
        "critic": SYSTEM + "\nROLE: Skeptical continuity and naturalness editor. "
                  "Find specific flaws and suggest corrections, not generic praise. " + prompt,
    }


def audit_scenes(brief):
    """Offline evidence-based scene checks. NEVER visual or audio perception."""
    validate_brief(brief)
    result = []
    scenes = brief.get("scenes", [])
    if not scenes:
        result.append(issue("NO_STORYBOARD", "info", "No timed scene manifest supplied; cannot check timing"))
        return result
    previous_end = None
    visual_ids = []
    narration = clean(brief.get("narration"), 12000)
    for idx, sc in enumerate(scenes, 1):
        if not isinstance(sc, dict):
            result.append(issue("SCENE_INVALID", "blocking", "Scene is not an object", idx))
            continue
        start, end = sc.get("start_s"), sc.get("end_s")
        if (isinstance(start, bool) or isinstance(end, bool) or
            not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or
            not math.isfinite(start) or not math.isfinite(end) or start < 0 or end <= start):
            result.append(issue("BAD_TIMECODE", "blocking", "start_s/end_s must be increasing finite seconds", idx))
            continue
        duration = end - start
        if duration < 0.95:
            result.append(issue("MICRO_FLASH", "blocking", "Scene shorter than 0.95s; check for unintended flash", idx))
        elif duration < 1.5:
            result.append(issue("SHORT_HOLD_REVIEW", "warning", "Scene under 1.5s; confirm perceptual readability", idx))
        if previous_end is not None:
            if start < previous_end - 0.06:
                result.append(issue("SCENE_OVERLAP", "blocking", "Scene overlaps previous shot", idx))
            elif start > previous_end + 0.20:
                result.append(issue("UNEXPLAINED_GAP", "warning", "Unaccounted gap between shots", idx))
        previous_end = end
        asset_id = clean(sc.get("asset_id"), 120)
        if not asset_id:
            result.append(issue("NO_ASSET", "warning", "Scene has no grounded media asset ID", idx))
        visual_ids.append(asset_id)
        if brief["format"] in {"artvision_4x1", "documentario", "giuliano"}:
            spoken = clean(sc.get("spoken_detail_id"), 100)
            shown = clean(sc.get("visual_detail_id"), 100)
            if spoken and (not shown or spoken != shown):
                result.append(issue("VOICE_VISUAL_MISMATCH", "blocking", "Spoken detail does not match visual detail", idx))
            if narration and not sc.get("narration_excerpt"):
                result.append(issue("NO_VOICE_ALIGNMENT", "warning", "No narration excerpt/time alignment for this shot", idx))
        if clean(sc.get("rights_status"), 80) not in ("verified", "public_domain", "licensed"):
            result.append(issue("RIGHTS_NOT_PROVEN", "warning", "Licensing/provenance requires separate verification", idx))
        if brief["format"] == "artvision_4x1" and sc.get("kind") in ("gallery_entry", "gallery_exit"):
            if not sc.get("gallery_scale_evidence"):
                result.append(issue("MUSEUM_SCALE_UNVERIFIED", "blocking", "Gallery scale/canvas placement evidence missing", idx))
    if len(visual_ids) > 2 and len(set(x for x in visual_ids if x)) < max(2, len(visual_ids) // 3):
        result.append(issue("ASSET_REPETITION", "warning", "Very limited visual variety across scenes"))
    if narration and re.search(r"(il quadro ci lascia una domanda|l'opera ci invita a riflettere|forse il vero mistero)", narration[-400:], re.I):
        result.append(issue("STOCK_ENDING", "blocking", "Generic AI-style philosophical ending found"))
    return result


def probe_video(path):
    """Real ffprobe codec + SHA check; NOT a claim of artistic viewing."""
    if not path:
        return {"status": "not_checked", "reason": "No MP4 supplied"}
    p = Path(path)
    if p.suffix.lower() not in VIDEO_EXT or not p.is_file() or p.stat().st_size <= 0:
        return {"status": "not_checked", "reason": "No accessible nonempty video file"}
    try:
        proc = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_name,codec_type,width,height", "-of", "json", str(p)
        ], capture_output=True, text=True, check=True, timeout=25)
        meta = json.loads(proc.stdout)
        sha = hashlib.sha256()
        with p.open("rb") as f:
            for buf in iter(lambda: f.read(1024 * 1024), b""):
                sha.update(buf)
        return {"status": "metadata_only_not_artistic_qa", "sha256": sha.hexdigest(),
                "size_bytes": p.stat().st_size, "ffprobe": meta}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {"status": "unverified", "reason": "ffprobe or media verification failed"}


def base_report(brief, findings, video):
    return {
        "schema": SCHEMA, "generated_utc": utc_now(), "format": brief["format"],
        "subject": brief["subject"], "mode": "offline_preflight",
        "status": "needs_artistic_review", "sources_verified": False,
        "rights_verified": False, "video_seen_by_ai": False, "audio_listened_by_ai": False,
        "human_artistic_approval": False, "publication_authorized": False,
        "scene_count": len(brief.get("scenes", [])),
        "issues": findings, "video_probe": video, "model_calls": 0, "billing_actions": 0,
    }


def _approved_models(models, policy):
    if len(models) not in (2, 3) or len(set(models)) != len(models):
        raise ValueError("Select two distinct draft models and optional third independent critic")
    for model in models:
        if not MODEL_RE.fullmatch(model) or not model.endswith(":free"):
            raise ValueError("Explicitly named :free model required; no auto/free router")
        approved = admit(model, policy)
        if approved["provider"] != "openrouter":
            raise ValueError("Approved route must be OpenRouter")
    return models


def _ask_openrouter(model, prompt, key):
    if len(prompt) > MAX_INPUT:
        raise ValueError("Prompt exceeds safety cap")
    payload = {"model": model, "messages": [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}], "temperature": 0.45,
               "max_tokens": 1100, "stream": False,
               "provider": {"max_price": {"prompt": 0, "completion": 0},
                            "allow_fallbacks": False}}
    req = request.Request("https://openrouter.ai/api/v1/chat/completions",
                          method="POST",
                          data=json.dumps(payload, ensure_ascii=False).encode(),
                          headers={"Authorization": "Bearer " + key,
                                   "Content-Type": "application/json",
                                   "X-Title": "Tra-le-Pagine-AI-Director-V1"})
    try:
        with request.urlopen(req, timeout=35) as response:
            body = response.read(MAX_OUTPUT + 1)
    except error.HTTPError as exc:
        raise RuntimeError("OpenRouter rejected request (HTTP " + str(exc.code) + ")") from None
    except (error.URLError, TimeoutError, OSError):
        raise RuntimeError("OpenRouter unavailable; never automatically retry") from None
    if len(body) > MAX_OUTPUT:
        raise RuntimeError("OpenRouter result exceeded response limit")
    try:
        data = json.loads(body)
        text = data["choices"][0]["message"]["content"]
        routed = data.get("model")
        if not isinstance(text, str) or not text.strip() or len(text) > 25_000:
            raise ValueError("Empty/oversized reply")
        if not isinstance(routed, str) or routed != model:
            raise ValueError("Reported model differs from approved :free model")
        return text.strip()
    except (ValueError, KeyError, IndexError, TypeError):
        raise RuntimeError("Model result unusable or route not verified") from None


def compare(brief, models, policy_path, *, execute=False, environ=None, transport=None):
    """Default dry-run; at most 3 explicit free-only calls, no retries."""
    prompts = editorial_prompts(brief)
    policy = load_policy(policy_path)
    _approved_models(models, policy)  # ALL checks before any request
    meta = {"status": "dry_run" if not execute else "draft_unreviewed",
            "models": models, "model_calls": 0, "billing_actions": 0,
            "human_artistic_approval": False, "publication_authorized": False}
    if not execute:
        meta["message"] = "All models admitted by local evidence, network disabled by default"
        return meta
    env = os.environ if environ is None else environ
    if env.get("AI_DIRECTOR_ALLOW_FREE_CALLS") != "1":
        raise RuntimeError("Explicit opt-in AI_DIRECTOR_ALLOW_FREE_CALLS=1 required")
    key = env.get("OPENROUTER_API_KEY", "")
    if not key or "\n" in key or "\r" in key or len(key) > 600:
        raise RuntimeError("OPENROUTER_API_KEY missing or invalid")
    ask = transport or _ask_openrouter
    outputs = []
    try:
        for idx, model in enumerate(models[:2]):
            # Count attempts before calls, including timeouts/failures.
            meta["model_calls"] += 1
            result = ask(model, prompts["director" if idx == 0 else "critic"], key)
            outputs.append({"model": model, "text": result, "approval": False})
        meta["candidates"] = outputs
        if len(models) == 3:
            judge_input = ("Compare these TWO unapproved creative treatments. "
                           "Give a skeptical comparison of factual provenance, "
                           "specificity, camera, timing, narration-to-scene mapping, "
                           "naturalness and repeatability. No invented scores or human "
                           "approval. Cite actual flaws visible in the text. "
                           "Candidate texts:\n" + json.dumps(outputs, ensure_ascii=False))
            if len(judge_input) > MAX_INPUT:
                raise ValueError("Judge input too long")
            meta["model_calls"] += 1
            meta["judge_notes_unverified"] = ask(models[2], judge_input, key)
        return meta
    except Exception as exc:
        # No key, prompt or provider body in error report.
        meta["status"] = "partial_failed_no_retry"
        meta["candidates"] = outputs
        meta["error"] = str(exc) if isinstance(exc, (RuntimeError, ValueError)) else "Unexpected provider failure"
        return meta


def dashboard(report):
    entries = report.get("issues", [])
    pieces = []
    for i in entries:
        severity = i.get("severity", "info")
        color = {"blocking": "#bb3f46", "warning": "#a17a31", "info": "#497a94"}.get(severity, "#497a94")
        pieces.append(
            '<article style="border-left:4px solid ' + color + ';padding:12px 14px;'
            'background:#f5f6f7;border-radius:8px;margin:8px 0">'
            '<strong>' + html.escape(i.get("code", "")) + '</strong> · ' +
            html.escape(severity) + '<p>' + html.escape(i.get("message", "")) +
            '</p></article>'
        )
    counts = {level: sum(i.get("severity") == level for i in entries) for level in ISSUE_LEVELS}
    title = html.escape(report.get("subject", "AI Director"))
    body = "".join(pieces) or '<p>Nessun difetto strutturale rilevato nei dati forniti. Non e una revisione artistica.</p>'
    return ('<!doctype html><html lang="it"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>AI Director - ' + title + '</title>'
            '<style>body{font:16px system-ui;margin:auto;max-width:760px;padding:20px;'
            'line-height:1.55;color:#182026;background:#fff}header{padding:16px 0;'
            'border-bottom:1px solid #ddd}small{color:#667085}.summary{display:flex;'
            'gap:10px;flex-wrap:wrap}.summary span{padding:7px 10px;background:#eee;'
            'border-radius:8px}article p{margin:4px 0 0}h1{font-size:1.65rem}'
            '</style><header><small>TRA LE PAGINE · Studio quality / offline evidence</small>'
            '<h1>' + title + '</h1><p><strong>Da revisionare:</strong> nessuna approvazione '
            'artistica o pubblicazione automatica.</p></header><main>'
            '<p><strong>Formato:</strong> ' + html.escape(report.get("format", "")) + '</p>'
            '<div class="summary"><span>Scene: ' + str(report.get("scene_count", 0)) +
            '</span><span>Blocchi: ' + str(counts["blocking"]) +
            '</span><span>Avvisi: ' + str(counts["warning"]) +
            '</span><span>Modelli chiamati: ' + str(report.get("model_calls", 0)) +
            '</span></div><h2>Problemi da verificare</h2>' + body +
            '<p><small>Controllo basato su manifest e metadati, NON sulla visione o '
            'ascolto del filmato. Fonti, diritti, V80/V94/V96/V99, MP4 reale e '
            'approvazione umana rimangono obbligatori.</small></p></main></html>')


def write_reports(outdir, report, prompts=None):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (outdir / "ANDROID_REPORT.html").write_text(dashboard(report), encoding="utf-8")
    if prompts is not None:
        (outdir / "EDITORIAL_PROMPTS.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    p = argparse.ArgumentParser(description="AI Director V1: fail-closed, no automatic rendering or costs")
    p.add_argument("--format", choices=FORMATS, default="documentario")
    p.add_argument("--subject", default="Esempio offline per revisione")
    p.add_argument("--brief", type=Path)
    p.add_argument("--video", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("output/ai_director_v1"))
    p.add_argument("--mode", choices=("plan", "audit", "compare"), default="plan")
    p.add_argument("--model", action="append", default=[], help="2 or 3 exact verified :free IDs")
    p.add_argument("--execute", action="store_true", help="Explicitly allow free API calls after policy checks")
    p.add_argument("--policy", type=Path, default=ROOT / "config/free_llm_zero_cost_v1.json")
    opts = p.parse_args(argv)
    if opts.execute and opts.mode != "compare":
        p.error("--execute only valid with --mode compare")
    brief = load_json(opts.brief) if opts.brief else make_brief(opts.format, opts.subject)
    findings = audit_scenes(brief)
    video = probe_video(opts.video) if opts.video else {"status": "not_checked"}
    visual_review = None
    if opts.video:
        from ai_director_visual_qa_v1 import inspect as inspect_real_mp4
        try:
            visual_review = inspect_real_mp4(opts.video)
            findings.extend(visual_review["issues"])
        except (RuntimeError, ValueError, OSError) as exc:
            visual_review = {"status": "unverified", "reason": str(exc),
                             "human_artistic_approval": False, "issues": []}
            findings.append(issue("REAL_MP4_SCAN_NOT_AVAILABLE", "warning",
                                  "Actual frame-timing scan unavailable; no artistic conclusion"))
    report = base_report(brief, findings, video)
    if visual_review is not None:
        report["real_mp4_technical_diagnostics"] = visual_review
    prompts = editorial_prompts(brief)
    if opts.mode == "compare":
        if not opts.model:
            p.error("--mode compare requires --model twice (third is optional)")
        try:
            comparison = compare(brief, opts.model, opts.policy, execute=opts.execute)
        except (ZeroCostPolicyError, RuntimeError, ValueError, OSError) as exc:
            comparison = {"status": "blocked_no_calls", "error": str(exc), "model_calls": 0}
        report["comparison"] = comparison
        report["model_calls"] = comparison.get("model_calls", 0)
        report["mode"] = "comparison_requested"
    elif opts.mode == "audit":
        report["mode"] = "storyboard_evidence_audit"
    write_reports(opts.out_dir, report, prompts if opts.mode == "plan" else None)
    print("AI_DIRECTOR_V1", report["mode"], "issues=", len(findings),
          "calls=", report["model_calls"], "approval=FALSE", "files=", opts.out_dir)
    return 0 if not any(x["severity"] == "blocking" for x in findings) else 2


if __name__ == "__main__":
    sys.exit(main())
