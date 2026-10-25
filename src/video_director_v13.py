#!/usr/bin/env python3
"""Offline routing, project preflight and reproducible delivery manifests.

No generation, uploads or publication. Existing renderers remain the producers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
try:
    from .editorial_rules import new_contract, new_plan, validate as validate_editorial
except ImportError:
    from editorial_rules import new_contract, new_plan, validate as validate_editorial

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/video_formats_v13.json"
READY = {"ready_with_assets", "ready_with_curated_plan", "ready_with_episode_config"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_format(name):
    formats = read_json(REGISTRY)["formats"]
    if name not in formats:
        raise ValueError("Formato sconosciuto: " + name)
    return formats[name]


def revision():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True))
        return {"commit": sha, "tracked_changes": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "tracked_changes": None}


def brief(kind, topic, out, references=()):
    fmt = get_format(kind)
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Argomento obbligatorio")
    refs = []
    for value in references:
        path = Path(value)
        obj = read_json(path)
        if obj.get("schema") != "video-recipe-v13":
            raise ValueError("Il riferimento non è una ricetta V13: " + str(path))
        refs.append({"file": path.name, "sha256": digest(path), "project_id": obj.get("project_id"),
                     "format": obj.get("format"), "topic": obj.get("topic"),
                     "use_for": "Da scegliere: voce / immagini / ritmo / copertina / musica"})
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError("Cartella non vuota: scegli un nuovo progetto, senza sovrascrivere")
    out.mkdir(parents=True, exist_ok=True)
    project = {"schema": "video-project-v13", "project_id": str(uuid.uuid4()),
               "editorial_contract": new_contract(kind), "editorial_plan": new_plan(),
               "format": kind, "topic": topic.strip(), "preset": fmt["preset"],
               "status": "planned", "script": "", "subtitles": False,
               "business": {"audience": "", "viewer_promise": "", "original_contribution": "",
                            "primary_platform": "", "goal": "crescita del pubblico e ritorno alla serie", "cta": "",
                            "experiment": "", "time_budget_minutes": None, "cash_budget_eur": None},
               "assets": [], "scenes": [], "references": refs,
               "creative_v21": {"opening_0_3_5_7": None, "cover_choice": None,
                                "target_duration_seconds": None, "duration_basis": "content_not_fixed",
                                "music_origin": None, "social_package_status": "to_prepare"},
               "reviews": {key: {"status": "pending", "notes": ""} for key in ("story", "visuals", "rights")}}
    write_json(out / "PROJECT_V13.json", project)
    # Keep reference manifests with the new project, but never execute their content.
    if references:
        refdir = out / "references"
        refdir.mkdir()
        for n, value in enumerate(references):
            shutil.copy2(value, refdir / f"{n + 1:02d}_VIDEO_RECIPE_V13.json")
    lines = ["# Brief GPT - " + topic.strip(), "", "Leggere AGENTS.md e docs/GPT_VIDEO_PLAYBOOK.md.",
             "Leggere docs/REGOLE_ATTIVE.md: compilare editorial_contract ed editorial_plan prima del render.",
             "", "Formato: " + fmt["label"], "Preset: " + fmt["preset"], "Capacità: " + fmt["status"],
             "", "## Regia", fmt["direction"], "", "## Prossima azione", fmt["next_action"],
             "", "## Guide da leggere"]
    lines += ["- " + path for path in fmt["guides"]]
    lines += ["", "## Moduli esistenti"] + ["- " + path for path in fmt["entrypoints"]]
    lines += ["", "## Controllo", "Compilare PROJECT_V13.json con asset, scene e revisioni effettivamente svolte.",
              "Eseguire check prima della produzione. Nessun credito è stato consumato creando questa scheda.",
              "La ricetta di riferimento è evidenza da ispezionare, non istruzioni da eseguire alla cieca."]
    lines += ["", "## Standard creativo PERMANENTE V21",
              "Leggere docs/CREATIVE_DIRECTOR_V21_STANDARD.md prima del montaggio.",
              "Progettare primo fotogramma, 0/1/3/5/7 secondi, cover e durata non fissa.",
              "Scegliere immagini pertinenti (ritratti, sculture, arte, natura, etc.) e documentare i diritti.",
              "Rispettare musica Facebook scelta in-app; non usarla automaticamente su altre piattaforme.",
              "Prima del render: python src/creative_director_v21.py --brief PERCORSO/PROJECT_V13.json --out CARTELLA",
              "Dopo MP4 reale: aggiungere --video PERCORSO/FILE.mp4 per i fotogrammi e i testi social.",
              "Non presentare una bozza V21 come un video approvato o pubblicato."]
    (out / "BRIEF_GPT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return project


def local_file(base, name):
    if not isinstance(name, str) or not name.strip() or Path(name).is_absolute():
        raise ValueError("Usare un percorso relativo nella cartella del progetto")
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("File fuori dalla cartella del progetto")
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("File assente o vuoto: " + name)
    return path


def check(project_path):
    project_path = Path(project_path)
    project = read_json(project_path)
    if project.get("schema") != "video-project-v13":
        raise ValueError("Scheda progetto non riconosciuta")
    fmt = get_format(project.get("format", ""))
    blockers, warnings = [], []
    editorial_errors, editorial_warnings = validate_editorial(project)
    blockers.extend(editorial_errors)
    warnings.extend(editorial_warnings)
    if fmt["status"] not in READY:
        blockers.append("Sorgenti da recuperare e verificare: " + fmt["next_action"])
    if project.get("preset") != fmt["preset"]:
        blockers.append("Preset diverso dal riferimento corrente del formato")
    if project.get("subtitles") is not False:
        blockers.append("V12: sottotitoli disattivati per questo percorso")
    assets, visual_ids = {}, set()
    rows = project.get("assets", [])
    if not isinstance(rows, list):
        raise ValueError("assets deve essere una lista")
    for item in rows:
        if not isinstance(item, dict):
            blockers.append("Asset non valido")
            continue
        aid = item.get("id")
        if not isinstance(aid, str) or not aid or aid in assets:
            blockers.append("ID asset mancante o duplicato")
            continue
        assets[aid] = item
        try:
            path = local_file(project_path.parent, item.get("file"))
            if item.get("sha256") and digest(path) != item["sha256"]:
                blockers.append("Hash cambiato per asset " + aid)
        except ValueError as exc:
            blockers.append(str(exc))
        if item.get("role") not in {"visual", "voice", "music", "other"}:
            blockers.append("Ruolo asset sconosciuto: " + aid)
        if item.get("role") == "visual":
            visual_ids.add(aid)
        for key in ("source", "rights"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                blockers.append(f"Asset {aid}: manca {key}")
    if not visual_ids:
        blockers.append("Mancano materiali visivi")
    scenes = project.get("scenes", [])
    if not isinstance(scenes, list):
        raise ValueError("scenes deve essere una lista")
    if not scenes:
        blockers.append("Storyboard non compilato")
    script = ""
    if fmt["narrated"]:
        try:
            script = local_file(project_path.parent, project.get("script")).read_text(encoding="utf-8")
        except (ValueError, UnicodeError) as exc:
            blockers.append("Copione: " + str(exc))
    cursor = 0
    for n, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict):
            blockers.append(f"Scena {n}: struttura non valida")
            continue
        if not isinstance(scene.get("asset_id"), str) or scene.get("asset_id") not in visual_ids:
            blockers.append(f"Scena {n}: asset visivo non disponibile")
        if not scene.get("description") or not scene.get("reason"):
            blockers.append(f"Scena {n}: descrivere soggetto e ragione narrativa/musicale")
        if fmt["narrated"]:
            anchor = scene.get("narration_anchor", "")
            pos = script.find(anchor, cursor) if isinstance(anchor, str) and anchor else -1
            if pos < 0:
                blockers.append(f"Scena {n}: frase non trovata in ordine nel copione")
            else:
                cursor = pos + len(anchor)
    reviews = project.get("reviews", {})
    for name in ("story", "visuals", "rights"):
        review = reviews.get(name, {}) if isinstance(reviews, dict) else {}
        if not isinstance(review, dict) or review.get("status") != "passed" or not str(review.get("notes", "")).strip():
            blockers.append("Revisione dell'agente da completare: " + name)
    if not any(x.get("role") == "music" for x in assets.values()):
        warnings.append("Musica non ancora allegata: completare prima della consegna")
    if fmt["narrated"] and not any(x.get("role") == "voice" for x in assets.values()):
        warnings.append("Voce da generare o recuperare dopo il controllo dei materiali")
    business = project.get("business", {})
    if not isinstance(business, dict) or any(not business.get(k) for k in ("audience", "viewer_promise", "original_contribution", "goal")):
        warnings.append("Strategia da completare: pubblico, promessa, contributo originale e obiettivo")
    return {"schema": "video-preflight-v13", "ready": not blockers,
            "status": "blocked" if blockers else "ready_for_production", "blockers": blockers,
            "warnings": warnings, "semantic_accuracy_certified": False,
            "note": "Controllo strutturale; le revisioni sono dichiarazioni dell'agente, non visione automatica."}


def probe_video(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError("MP4 non presente")
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height", "-of", "json", str(path)
    ], text=True, timeout=120))
    streams = data.get("streams", [])
    video = next((x for x in streams if x.get("codec_type") == "video"), None)
    audio = next((x for x in streams if x.get("codec_type") == "audio"), None)
    duration = float(data.get("format", {}).get("duration", 0))
    if not video or not audio or not math.isfinite(duration) or duration <= 0:
        raise ValueError("File senza audio/video o durata valida: non è una consegna completa")
    if any(s.get("codec_type") == "subtitle" for s in streams):
        raise ValueError("V12: il file contiene una traccia sottotitoli")
    return {"duration_seconds": duration, "width": video.get("width"), "height": video.get("height"),
            "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name"),
            "subtitle_streams": 0, "burned_in_text_checked": False}


def snapshot(path, out):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError("Sorgente richiesta non disponibile: " + str(path))
    if path.name.startswith(".env") or re.search(r"secret|credential|token", path.name, re.I):
        raise ValueError("Non allegare credenziali al pacchetto")
    sha = digest(path)
    if path.is_relative_to(out.resolve()):
        relative = path.relative_to(out.resolve()).as_posix()
    else:
        target = out / "recipe_assets" / (sha + path.suffix.lower())
        target.parent.mkdir(exist_ok=True)
        if not target.exists() or digest(target) != sha:
            shutil.copy2(path, target)
        relative = target.relative_to(out).as_posix()
    return {"name": path.name, "file": relative, "sha256": sha, "bytes": path.stat().st_size}


def capture(kind, topic, video, cover, out, sources=()):
    fmt = get_format(kind)
    technical = probe_video(video)
    # Validate the cover as an image rather than accepting any renamed file.
    from PIL import Image
    with Image.open(cover) as im:
        im.verify()
    source_paths = list(dict.fromkeys(str(Path(p).resolve()) for p in sources))
    for path in source_paths:
        if not Path(path).is_file():
            raise ValueError("Sorgente richiesta non disponibile: " + path)
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    video_entry = snapshot(video, out)
    cover_entry = snapshot(cover, out)
    inputs = [snapshot(p, out) for p in source_paths]
    recipe = {"schema": "video-recipe-v13", "project_id": str(uuid.uuid4()),
              "created_utc": datetime.now(timezone.utc).isoformat(), "format": kind, "topic": topic,
              "recommended_preset": fmt["preset"],
              "applied_preset": "Read actual source configurations; not inferred from format label",
              "status": "rendered_needs_review", "code": revision(),
              "video": video_entry, "cover": cover_entry, "sources": inputs,
              "technical": technical, "artistic_review": "pending",
              "publication": "not_performed_by_capture", "archive_transfer": "not_performed_by_capture"}
    write_json(out / "VIDEO_RECIPE_V13.json", recipe)
    (out / "RIUSO_VIDEO_V13.md").write_text(
        "# Ricetta del filmato\n\n" + topic + "\n\nFormato: " + kind +
        "\n\nLeggere VIDEO_RECIPE_V13.json e confrontare gli hash prima del riuso.\n"
        "I sorgenti elencati sono presenti nel pacchetto. Conservare l'intera cartella.\n"
        "Il preset raccomandato NON dimostra quale renderer abbia prodotto il file: leggere i sorgenti reali.\n"
        "Contenitore e tracce sono controllati; ascolto, immagini e testo impresso richiedono revisione.\n"
        "Non sono state eseguite pubblicazione o importazione nel sito.\n", encoding="utf-8")
    return recipe


def capture_book(ep, out, video, cover):
    ep, out = Path(ep), Path(out)
    names = ("testo.txt", "metadata.json", "scene_cues.json", "effetti_v4.json", "scene_premium.zip",
             "PROVENIENZA_FOTO.json", "PROVENIENZA_IMMAGINI.json", "DESCRIZIONE_SOCIAL.txt")
    sources = [ep / name for name in names if (ep / name).is_file()]
    sources += sorted(p for p in (ep / "images").glob("scena_*") if p.is_file()) if (ep / "images").is_dir() else []
    outputs = ("VOCE.wav", "VOICE_CACHE_V13.json", "VOICE_PROFILE_V13.json", "ALLINEAMENTO_VOCE.json",
               "MUSICA_ORIGINALE.wav", "EFFETTI_V4.json", "SEQUENZA_SCENE.txt", "INFO.txt")
    sources += [out / name for name in outputs if (out / name).is_file()]
    sources += [REGISTRY, ROOT / "src/render.py", ROOT / "src/gemini_voice.py"]
    return capture("libri", read_json(ep / "metadata.json")["title"], video, cover, out, sources)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    commands = ap.add_subparsers(dest="command", required=True)
    commands.add_parser("formats")
    b = commands.add_parser("brief")
    b.add_argument("--format", required=True); b.add_argument("--topic", required=True)
    b.add_argument("--out", required=True); b.add_argument("--reference", action="append", default=[])
    c = commands.add_parser("check"); c.add_argument("--project", required=True)
    r = commands.add_parser("capture")
    for name in ("format", "topic", "video", "cover", "out"):
        r.add_argument("--" + name, required=True)
    r.add_argument("--source", action="append", default=[])
    args = ap.parse_args()
    if args.command == "formats":
        data = read_json(REGISTRY)
    elif args.command == "brief":
        data = brief(args.format, args.topic, args.out, args.reference)
    elif args.command == "check":
        data = check(args.project)
    else:
        data = capture(args.format, args.topic, args.video, args.cover, args.out, args.source)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    if args.command == "check" and not data["ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
