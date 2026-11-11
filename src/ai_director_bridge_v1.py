#!/usr/bin/env python3
"""Read-only adapter from existing V13 and ArtVision 4x1 plans to AI Director.

Never rewrites source plans, renders video or changes production queues.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from ai_director_v1 import (SCHEMA, audit_scenes, base_report, clean, dashboard,
                            editorial_prompts, make_brief, write_reports, probe_video)
from artvision_learning_loop_v1 import next_lesson

FORMAT_MAP = {
    "artvision_cinema": "artvision_4x1",
    "artvision_critico": "artvision_4x1",
    "libri": "documentario",
    "controluce": "documentario",
    "documentario": "documentario",
    "giuliano": "giuliano",
    "storia_rivive": "storia_rivive",
    "wow_lab": "wow_lab",
}


def read_source(path):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 2_000_000:
        raise ValueError("Existing project JSON missing or oversized")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Source must be an object")
    return data


def _duration(scene):
    d = scene.get("duration_seconds")
    if type(d) in (int, float) and math.isfinite(d) and d > 0:
        return float(d)
    return None


def from_v13(project):
    """Conservative conversion. Without real timing, never manufacture seconds."""
    if project.get("schema") != "video-project-v13":
        raise ValueError("Not a V13 project")
    fmt = FORMAT_MAP.get(project.get("format"))
    if not fmt:
        raise ValueError("Unrecognized V13 production format")
    b = make_brief(fmt, str(project.get("topic") or ""))
    assets = {a.get("id"): a for a in project.get("assets", [])
              if isinstance(a, dict) and a.get("id")}
    sources = []
    for asset in assets.values():
        link = clean(asset.get("source"), 500)
        if link.startswith("https://"):
            sources.append({"url": link, "observation": clean(asset.get("description") or
                                                             asset.get("id"), 250),
                            "license": clean(asset.get("rights"), 120)})
    b["source_notes"] = sources[:60]
    scenes = project.get("scenes", [])
    if not isinstance(scenes, list):
        scenes = []
    start = 0.
    if scenes and all(isinstance(x, dict) and _duration(x) for x in scenes):
        for x in scenes[:120]:
            dur = _duration(x)
            aid = clean(x.get("asset_id"), 120)
            asset = assets.get(aid, {})
            b["scenes"].append({
                "start_s": round(start, 3), "end_s": round(start + dur, 3),
                "asset_id": aid, "visual_detail_id": clean(x.get("detail_id"), 100),
                "spoken_detail_id": clean(x.get("spoken_detail_id"), 100),
                "narration_excerpt": clean(x.get("narration_anchor"), 600),
                "rights_status": "unverified_by_ai_director",
            })
            start += dur
    # If V13 lacks exact timings, preserve no timing rather than guessing.
    b["source_format"] = "video-project-v13"
    b["timecodes_available"] = bool(b["scenes"])
    return b


def from_four_variants(plan):
    if plan.get("schema") != "artvision-4x1-v1":
        raise ValueError("Not an ArtVision 4x1 plan")
    variants = plan.get("variants")
    if not isinstance(variants, dict) or set(variants) != {
        "critico_standard", "critico_museum", "cinema_standard", "cinema_museum"
    }:
        raise ValueError("A 4x1 group must have exactly four variants")
    result = {}
    for variant_id, variant in variants.items():
        if not isinstance(variant, dict):
            raise ValueError("Variant is not an object")
        b = make_brief("artvision_4x1", str(plan.get("topic") or ""))
        b["variant"] = variant_id
        b["artist"] = clean(plan.get("artist"), 200)
        b["source_format"] = "artvision-4x1-v1"
        museum = variant.get("museum") if isinstance(variant.get("museum"), dict) else {}
        evidence = [museum.get("dimensions_source"), museum.get("gallery_id"),
                    museum.get("frame_status")]
        museum_source = " | ".join(clean(x, 240) for x in evidence if clean(x))
        start = 0.
        lines = []
        timed = True
        for scene in variant.get("scenes", []):
            if not isinstance(scene, dict) or _duration(scene) is None:
                timed = False
                break
        if timed:
            for x in variant.get("scenes", [])[:120]:
                dur = _duration(x)
                spoken = clean(x.get("spoken_line"), 1500)
                if spoken:
                    lines.append(spoken)
                detail = clean(x.get("detail_id"), 100)
                b["scenes"].append({
                    "start_s": round(start, 3), "end_s": round(start + dur, 3),
                    "kind": clean(x.get("kind"), 80) or "detail",
                    "asset_id": detail or clean(museum.get("gallery_id"), 100),
                    "visual_detail_id": detail, "spoken_detail_id": detail if spoken else "",
                    "narration_excerpt": spoken, "rights_status": "unverified_by_ai_director",
                    "gallery_scale_evidence": museum_source if
                        all(type(museum.get(k)) in (int, float) and museum.get(k) > 0
                            for k in ("width_cm", "height_cm")) else "",
                })
                start += dur
        b["narration"] = "\n".join(lines) if variant_id.startswith("critico") else ""
        b["timecodes_available"] = timed and bool(b["scenes"])
        result[variant_id] = b
    return result


def enrich_report(report, lesson):
    # Lessons are proposals for ONE measured future experiment, never auto-edits.
    report["learning"] = lesson
    report["learning_applied_to_video"] = False
    report["master_modified"] = False
    report["automatic_publish"] = False
    return report


def bridge(source, out, *, ledger=None):
    obj = read_source(source)
    if obj.get("schema") == "video-project-v13":
        briefs = {"project_v13": from_v13(obj)}
    elif obj.get("schema") == "artvision-4x1-v1":
        briefs = from_four_variants(obj)
    else:
        raise ValueError("Input is not V13 or 4x1 plan")
    lesson = (next_lesson(Path(ledger)) if ledger else
              {"status": "not_requested", "suggestion": None})
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for name, b in briefs.items():
        report = base_report(b, audit_scenes(b), {"status": "not_checked"})
        report["variant"] = name
        report["timecodes_available"] = b["timecodes_available"]
        report["source_format"] = b["source_format"]
        if not b["timecodes_available"]:
            report["issues"].append({
                "code": "TIMING_NOT_SUPPLIED", "severity": "warning",
                "message": "Actual scene times missing; no fabricated timecodes",
            })
        enrich_report(report, lesson)
        folder = out / name
        # Inputs already exist in public project; do not export private paths or secrets.
        write_reports(folder, report)
        results.append({"variant": name, "status": report["status"],
                        "issues": len(report["issues"]), "report_path": name + "/ANDROID_REPORT.html"})
    index = {"schema": SCHEMA, "source_schema": obj["schema"],
             "status": "advisory_review_only", "variants": results, "learning": lesson,
             "video_watched": False, "automatic_publish": False, "render_performed": False}
    (out / "INDEX.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    import html
    links = "".join('<li style="padding:12px"><a href="' + html.escape(x["report_path"], quote=True)
                    + '">' + html.escape(x["variant"]) + '</a> — '
                    + str(x["issues"]) + ' segnalazioni</li>' for x in results)
    (out / "INDEX.html").write_text(
        '<!doctype html><html lang="it"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta charset="utf-8"><title>AI Director 4x1</title>'
        '<body style="max-width:700px;margin:auto;padding:20px;font:16px system-ui">'
        '<h1>AI Director · Report per Android</h1><p>Analisi da dossier reali: '
        'non implica visione MP4, approvazione o pubblicazione.</p><ul>' + links + '</ul></body></html>',
        encoding="utf-8")
    return index


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path,
                   help="Existing PROJECT_V13.json or ARTVISION_4X1_PLAN.json")
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--learning-ledger", type=Path)
    o = p.parse_args(argv)
    report = bridge(o.source, o.out_dir, ledger=o.learning_ledger)
    print("AI_DIRECTOR_READ_ONLY_BRIDGE", report["source_schema"],
          "variants=", len(report["variants"]), "automatic_publish=FALSE")


if __name__ == "__main__":
    main()
