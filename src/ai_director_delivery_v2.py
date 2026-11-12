#!/usr/bin/env python3
"""AI Director V2: audit actual delivered files, never alter/publish media.

Offline sidecar for Giuliano, ArtVision 4x1, La Storia Rivive and WOW LAB.
No external inference, no TTS/Vidu, no automatic creative approval.
"""
from __future__ import annotations
import argparse
import html
import json
import re
import sys
from pathlib import Path

from ai_director_v1 import make_brief, audit_scenes, base_report, write_reports
from ai_director_bridge_v1 import from_v13, from_four_variants
from ai_director_visual_qa_v1 import inspect as inspect_mp4
from director_reference_v326 import analyze_scenes, inspect_black_tail

FORMATS = ("giuliano", "artvision_4x1", "storia_rivive", "wow_lab", "documentario")
MAX_JSON = 2_000_000
VIDEO_LIMIT = 3_000_000_000
MANIFEST_HINTS = ("PROJECT_V13", "ARTVISION_4X1_PLAN", "EP03_SCRIPT_SHOTMAP",
                  "SHOT_PLAN", "STORYBOARD", "SHOTS_DOCUMENTARY")
VIDEO_MARKERS = ("MASTER", "CINEMATIC", "VIDEO_ANDROID", "ANDROID", "REVIEW")


def _load(path):
    if not path.is_file() or path.stat().st_size > MAX_JSON:
        raise ValueError("Manifest missing or above 2MB")
    d = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict):
        raise ValueError("Manifest is not a JSON object")
    return d


def _timed_brief(data, fmt, subject):
    """Timing from estimated_seconds is marked estimated, never actual audio alignment."""
    b = make_brief(fmt, subject)
    shots = data.get("scenes", data.get("shots", []))
    if not isinstance(shots, list):
        return b
    elapsed = 0.0
    for shot in shots[:120]:
        if not isinstance(shot, dict):
            continue
        seconds = shot.get("duration_seconds", shot.get("estimated_seconds", shot.get("duration")))
        if type(seconds) not in (float, int) or not 0 < seconds < 1800:
            continue
        asset = shot.get("asset_id") or shot.get("source_file") or ""
        narration = shot.get("narration") or shot.get("text") or shot.get("spoken_line") or ""
        b["scenes"].append({"start_s": round(elapsed, 4),
                            "end_s": round(elapsed + seconds, 4),
                            "asset_id": str(asset)[:120],
                            "narration_excerpt": str(narration)[:600],
                            "rights_status": "pending_independent_proof"})
        elapsed += seconds
    b["timecode_provenance"] = "estimated_from_source_manifest_not_recorded_voice"
    return b


def _briefs(data, fmt, subject):
    schema = data.get("schema")
    if schema == "video-project-v13":
        return {"project_v13": from_v13(data)}
    if schema == "artvision-4x1-v1":
        return from_four_variants(data)
    if schema == "ai-director-v1":
        b = dict(data)
        # A checked-in source should not grant artistic/publication permissions.
        b["human_artistic_approval"] = False
        b["publication_authorized"] = False
        return {"editorial": b}
    return {"episode": _timed_brief(data, fmt, subject)}


def _select_video(root, variant=None):
    files = [x for x in root.rglob("*.mp4") if x.is_file() and
             not x.is_symlink() and 100 <= x.stat().st_size <= VIDEO_LIMIT]
    if variant:
        files = [x for x in files if variant.casefold() in x.name.casefold()]
    def preference(p):
        n = p.name.upper()
        return (min((i for i, mark in enumerate(VIDEO_MARKERS) if mark in n), default=9),
                len(p.parts), p.name.casefold())
    return sorted(files, key=preference)[0] if files else None


def _video_report(video):
    if video is None:
        return {"status": "video_unavailable", "issues": [],
                "narration_alignment_verified": False, "human_artistic_approval": False}
    try:
        result = inspect_mp4(video)
        if result.get("status") == "technical_review_only":
            duration = float(result.get("duration_s") or 0)
            notes, facts = inspect_black_tail(video, duration)
            for x in notes:
                result["issues"].append({"code": x["code"], "severity": "warning",
                                         "message": x["message"]})
            result["end_tail"] = facts
        result["video_filename"] = video.name
        return result
    except (OSError, RuntimeError, ValueError) as exc:
        return {"status": "video_unverified", "reason": type(exc).__name__,
                "issues": [], "narration_alignment_verified": False,
                "human_artistic_approval": False}


def _one(brief, out, video, *, fmt, label):
    issue_list = audit_scenes(brief)
    # V326 notes are advisory; don't turn heuristics into proof of artistic failure.
    adapted = [{"start": x["start_s"], "end": x["end_s"],
                "visual_anchor": x.get("visual_detail_id", ""),
                "spoken_anchor": x.get("spoken_detail_id", "")}
               for x in brief.get("scenes", [])
               if isinstance(x, dict) and type(x.get("start_s")) in (int, float)
               and type(x.get("end_s")) in (int, float)]
    v326_block, v326_notes, v326_facts = analyze_scenes(adapted, short=fmt == "storia_rivive")
    for row in v326_block:
        issue_list.append({"code": "V326_" + row["code"], "severity": "blocking",
                           "message": row["message"]})
    for row in v326_notes:
        issue_list.append({"code": "V326_" + row["code"], "severity": "warning",
                           "message": row["message"]})
    movie = _video_report(video)
    report = base_report(brief, issue_list, {"status": movie.get("status")})
    report.update({"schema": "ai-director-delivery-v2", "mode": "offline_actual_artifact_review",
                   "format": fmt, "variant": label,
                   "timecode_provenance": brief.get("timecode_provenance",
                                                   "provided_in_manifest_not_necessarily_asr"),
                   "visual_diagnostics": movie, "v326_timing": v326_facts,
                   "technical_video_checked": movie.get("status") == "technical_review_only",
                   "automatic_creative_correction": False, "finished_video_claim": False,
                   "human_artistic_approval": False, "publication_authorized": False,
                   "model_calls": 0, "billing_actions": 0})
    # A technical check is never the same as human review, licensing, or ASR sync.
    write_reports(out, report)
    html_path = out / "ANDROID_REPORT.html"
    content = html_path.read_text(encoding="utf-8")
    issues = movie.get("issues", [])
    detail = "<h2>Prova MP4 reale</h2><p><strong>" + html.escape(str(movie["status"])) + "</strong></p>"
    if video is not None:
        detail += "<p>File: " + html.escape(video.name) + "</p>"
    if issues:
        detail += "<ul>" + "".join("<li>" + html.escape(str(x.get("code"))) + ": " +
                                html.escape(str(x.get("message", ""))) + "</li>"
                                for x in issues[:80]) + "</ul>"
    detail += ("<p>Le scansioni sono indizi tecnici, NON ascolto della voce, verifica semantica, "
               "diritti o approvazione artistica. Nessun master modificato.</p>")
    html_path.write_text(content.replace("</main>", detail + "</main>"), encoding="utf-8")
    return {"variant": label, "video_checked": report["technical_video_checked"],
            "video_filename": movie.get("video_filename"),
            "manifest_findings": len(issue_list), "video_findings": len(issues),
            "report": str((out / "ANDROID_REPORT.html").name),
            "status": "technical_review_only" if report["technical_video_checked"]
                      else "awaiting_real_video"}


def review(input_dir, output_dir, *, fmt, subject, manifest=None, video=None):
    if fmt not in FORMATS:
        raise ValueError("Unknown format")
    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if not input_dir.is_dir():
        raise ValueError("Input directory missing")
    if input_dir == output_dir or input_dir in output_dir.parents:
        # Output may be a sibling, not nested within download to avoid recursion.
        raise ValueError("Keep reports outside the input directory")
    if manifest is None:
        candidates = [p for p in input_dir.rglob("*.json") if p.is_file()
                      and any(t in p.name.upper() for t in MANIFEST_HINTS)]
        manifest = sorted(candidates, key=lambda x: x.name)[0] if candidates else None
    else:
        manifest = Path(manifest).resolve()
        if not manifest.is_relative_to(input_dir):
            raise ValueError("Manifest must be inside input directory")
    source = _load(manifest) if manifest else None
    briefs = _briefs(source, fmt, subject) if source else {"episode": make_brief(fmt, subject)}
    if video is not None:
        video = Path(video).resolve()
        if not video.is_relative_to(input_dir) or not video.is_file():
            raise ValueError("Video must exist inside input directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    statuses = []
    for label, brief in briefs.items():
        selected = video if video is not None else _select_video(input_dir,
                    variant=label if len(briefs) > 1 else None)
        out = output_dir / re.sub(r"[^A-Za-z0-9_-]", "_", label)[:60]
        statuses.append(_one(brief, out, selected, fmt=fmt, label=label))
    index = {"schema": "ai-director-delivery-v2", "format": fmt,
             "manifest_used": manifest.name if manifest else None,
             "status": "advisory_only_not_approved", "artistic_review_required": True,
             "source_rights_verified": False, "narration_alignment_verified": False,
             "automatic_publication": False, "automatic_paid_calls": 0,
             "variants": statuses}
    (output_dir / "INDEX.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    links = "".join('<li><a href="' + html.escape(x["variant"] + "/ANDROID_REPORT.html",
                                                  quote=True) + '">' +
                    html.escape(x["variant"]) + "</a> — " +
                    html.escape(x["status"]) + "</li>" for x in statuses)
    (output_dir / "INDEX.html").write_text(
        '<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" '
        'content="width=device-width,initial-scale=1"><title>AI Director V2</title>'
        '<body style="max-width:720px;margin:auto;padding:20px;font:16px system-ui">'
        '<h1>AI Director V2 · Rapporto Android</h1><p>Analisi tecnica: nessuna '
        'approvazione artistica, generazione, spesa o pubblicazione.</p><ul>' +
        links + '</ul></body></html>', encoding="utf-8")
    return index


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--format", choices=FORMATS, required=True)
    p.add_argument("--subject", default="Revisione video reale")
    p.add_argument("--manifest", type=Path)
    p.add_argument("--video", type=Path)
    args = p.parse_args(argv)
    summary = review(args.input_dir, args.out, fmt=args.format,
                     subject=args.subject, manifest=args.manifest, video=args.video)
    print("AI_DIRECTOR_V2_REVIEW", json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
