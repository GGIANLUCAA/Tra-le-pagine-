#!/usr/bin/env python3
"""Giuliano: preproduction bridge to existing G0DM0D3-inspired AI Director V1.

Uses existing local AI Director prompts + audit: no G0DM0D3 website requests,
OpenRouter inference, credentials, automatic voice credits, MP4 or publication.
Separate optional 'render' gate requires REAL assets+checksums.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from ai_director_v1 import audit_scenes, editorial_prompts, load_json

SCHEMA = "giuliano-antikythera-preflight-v1"
ALLOWED = {"photo", "reconstruction_video", "original_diagram"}
MAX_WORDS_PER_SECOND = 3.1
VIDEO_TYPES = {"reconstruction_video"}


def problem(code, message, scene=None):
    d = {"code": code, "message": message, "severity": "blocking"}
    if scene is not None:
        d["scene"] = scene
    return d


def inspect(brief, asset_dir=None, phase="plan"):
    if brief.get("schema") != "ai-director-v1" or brief.get("format") != "giuliano":
        raise ValueError("Expected existing AI Director V1 Giuliano brief")
    shots = brief.get("scenes", [])
    narration = [x.strip() for x in brief.get("narration", "").splitlines() if x.strip()]
    issues = []
    if len(shots) < 18 or len(shots) > 45 or len(shots) != len(narration):
        issues.append(problem("SHOTS_AND_VOICE", "Every voiced line needs its own marked scene"))
    previous = 0.0
    generated_footage = 0.0
    photos = 0
    assets = brief.get("asset_catalog", {})
    for i, shot in enumerate(shots):
        sid = shot.get("id", "?")
        start, end = shot.get("start_s"), shot.get("end_s")
        if not isinstance(start, (int,float)) or not isinstance(end,(int,float)) or abs(start-previous)>0.001 or end<=start:
            issues.append(problem("TIMELINE_GAP_OR_OVERLAP", "Timecodes must exactly follow one another", sid))
            continue
        duration = end-start
        previous = end
        if duration < 3.5:
            issues.append(problem("MICRO_HOLD", "Photo/diagram scene is too short", sid))
        spoken = shot.get("narration_excerpt", "").strip()
        if i < len(narration) and spoken != narration[i]:
            issues.append(problem("VOICE_TEXT_MISMATCH", "Spoken line differs from narrated sequence", sid))
        words = len(spoken.split())
        if words/duration > MAX_WORDS_PER_SECOND:
            issues.append(problem("TOO_FAST_FOR_NATURAL_VOICE", "Voice pacing above 186 words/min", sid))
        if not shot.get("spoken_detail_id") or shot.get("spoken_detail_id") != shot.get("visual_detail_id"):
            issues.append(problem("SEMANTIC_MISMATCH", "Spoken and shown detail are not explicitly matched", sid))
        if shot.get("visual_kind") not in ALLOWED or shot.get("asset_id") not in assets:
            issues.append(problem("UNKNOWN_SOURCE", "Scene media not declared in exact source catalog", sid))
        kind = shot.get("visual_kind")
        if kind == "photo":
            photos += 1
            if not str(shot.get("source","")).startswith("https://commons.wikimedia.org/"):
                issues.append(problem("PHOTO_NOT_GROUNDED", "Museum source must have real Commons file page", sid))
        if kind == "reconstruction_video":
            generated_footage += duration
            if not shot.get("visual_direction","").lower().find("modern") >= 0:
                issues.append(problem("UNLABELED_RECONSTRUCTION", "No original recording should be implied", sid))
        if shot.get("rights_status") not in ("verified", "licensed", "public_domain", "original"):
            issues.append(problem("UNVERIFIED_RIGHTS", "Source rights not checked", sid))
        if phase == "render":
            if not shot.get("asset_checksum_verified") or not shot.get("asset_download_verified"):
                issues.append(problem("NOT_READY_FOR_RENDER", "Source file/hash not yet verified; no false MP4", sid))
            else:
                target = shot.get("local_asset", "")
                digest = shot.get("asset_sha256", "")
                if not target or not re.fullmatch(r"[a-f0-9]{64}", digest):
                    issues.append(problem("BAD_ASSET_HASH", "Exact local asset and SHA256 required", sid))
                elif asset_dir:
                    p = (Path(asset_dir)/target).resolve()
                    root = Path(asset_dir).resolve()
                    if root not in p.parents or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
                        issues.append(problem("ASSET_FILE_MISMATCH", "Source file missing, unsafe or SHA changed", sid))
    if abs(previous-brief.get("target_duration_seconds",0))>0.05:
        issues.append(problem("DURATION_MISMATCH", "Scene timings don't cover claimed target duration"))
    if not 125 <= previous <= 165:
        issues.append(problem("EPISODE_TOO_LONG", "Approved short Antikythera episode requires 2m05s–2m45s"))
    if generated_footage < 25:
        issues.append(problem("MOTION_INSUFFICIENT", "Need enough real movement of licensed reconstruction"))
    if photos < 7:
        issues.append(problem("MUSEUM_EVIDENCE_INSUFFICIENT", "Need real photographed artifact repeated at key milestones"))
    if brief.get("publication_authorized") or brief.get("human_artistic_approval"):
        issues.append(problem("FABRICATED_APPROVAL", "Research cannot assert human approval/publication"))
    try:
        advisory = audit_scenes(brief)
    except ValueError as exc:
        # Reject malicious/accidental claimed approvals without crashing the safe review.
        advisory = []
        if not any(x["code"] == "FABRICATED_APPROVAL" for x in issues):
            issues.append(problem("INVALID_DIRECTOR_BRIEF", str(exc)))
    report = {
        "schema": SCHEMA, "status": "blocked" if issues else ("ready_for_asset_acquisition" if phase=="plan" else "ready_for_render_preflight"),
        "phase":phase,"target_seconds":previous,"scene_count":len(shots),"spoken_word_count":len(brief.get("narration","").split()),
        "modern_3d_seconds":round(generated_footage,2),"museum_photo_scenes":photos,
        "unverified_binary_asset_count":sum(not sc.get("asset_checksum_verified",False) for sc in shots),
        "g0dm0d3_integration":"existing local AI Director V1 director/critic structured comparison only",
        "live_multi_model_calls":0,"openrouter_cost_eur":0,
        "ready_for_voice_or_render":phase=="render" and not issues,
        "script_audio_alignment_measured":False,
        "real_video_frame_scan_performed":False,"human_approval":False,"published":False,
        "issues":issues,
        "ai_director_advisory":advisory
    }
    return report


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--brief",required=True)
    p.add_argument("--output-dir",required=True)
    p.add_argument("--phase",choices=("plan","render"),default="plan")
    p.add_argument("--asset-dir")
    opt=p.parse_args(argv)
    b=load_json(opt.brief)
    report=inspect(b, opt.asset_dir, opt.phase)
    prompts=editorial_prompts(b)
    out=Path(opt.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    (out/"G0DM0D3_DIRECTOR_REVIEW.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"DIRECTOR_AND_CRITIC_PROMPTS.json").write_text(json.dumps({
        "director":prompts["director"],"critic":prompts["critic"],
        "note":"Prompts prepared using existing integrated AI Director; not submitted to any model, no fake debate answers."
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    status=html.escape(report["status"])
    rows="".join(f"<tr><td>{html.escape(s.get('id',''))}</td><td>{s['start_s']:.1f}–{s['end_s']:.1f}s</td><td>{html.escape(s['narration_excerpt'])}</td><td>{html.escape(s['visual_direction'])}</td></tr>" for s in b["scenes"])
    err="".join("<li>"+html.escape(x["code"]+": "+x["message"])+"</li>" for x in report["issues"])
    page=f"""<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Giuliano Anticitera · Regia</title><style>body{{max-width:980px;margin:auto;padding:20px;font:15px system-ui;background:#121922;color:#f7f4ec}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #405062;padding:10px;vertical-align:top}}tr:nth-child(odd){{background:#222c36}}h1{{color:#eacb8d}}p{{line-height:1.6}}a{{color:#eacb8d}}</style>
<h1>GIULIANO · THE ANCIENT COMPUTER</h1><p>Rassegna regia e prove · {status} · 2 min 34 s previsti.</p>
<p>Metodo G0DM0D3: confronto regista/critico tramite AI Director V1 già integrato.
 Nessuna inferenza inviata, nessun credito speso, nessun MP4 generato.</p>
<p><strong>Prima di produrre:</strong> acquisire media e licenze, verificare SHA-256, creare voce italiana,
 allineare scene all'ASR reale, controllare il video finale fotogramma per fotogramma e ottenere revisione artistica.</p>
<ul>{err}</ul><table><tr><th>Scena</th><th>Tempo provvisorio</th><th>Voce</th><th>Immagine richiesta</th></tr>{rows}</table></html>"""
    (out/"SCALLETTA_ANDROID.html").write_text(page,encoding="utf-8")
    print("GIULIANO_G0DM0D3_PREPROD",report["status"],"scenes",report["scene_count"],"issues",len(report["issues"]),"calls",0,flush=True)
    return 2 if report["issues"] else 0


if __name__=="__main__":sys.exit(main())
