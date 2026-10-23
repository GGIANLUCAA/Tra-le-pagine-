#!/usr/bin/env python3
"""ArtVision V25 contract gate: preflight and finished-media audit.

Additive checker. Does not render, publish, rewrite media, or certify aesthetics.
Usage: python src/artvision_contract_gate_v25.py --manifest path/ARTVISION_CONTRACT_V25.json --stage preflight|final
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "artvision_contract_v25.json"
TECHNIQUES = ROOT / "config" / "cinematic_techniques_v23.json"
FIELDS = {
    "video": "VIDEO_MASTER.mp4",
    "cover": "COPERTINA.jpg",
    "facebook": "POST_FACEBOOK.txt",
    "instagram": "POST_INSTAGRAM.txt",
    "tiktok": "POST_TIKTOK.txt",
    "youtube": "POST_YOUTUBE.txt",
    "recipe": "VIDEO_RECIPE_V13.json",
    "techniques": "TECNICHE_REGIA.md",
    "replication": "ISTRUZIONI_REPLICA.md",
    "rights": "SOURCES_AND_RIGHTS.md",
    "music_manifest": "MUSIC_RELEASE_V20.json",
}
REVIEW_KEYS = ("opening", "visual", "cover", "music", "rights", "full_watch", "replicability")
REVIEW_SECONDS = (0, 1, 3, 5, 7)
VALID_SHOTS = ("wide", "medium", "detail", "macro", "texture", "tableau", "full", "portrait", "landscape")
VALID_MOTIONS = ("locked", "slow_push", "slow_pull", "slow_pan_x", "slow_pan_y")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def filled(x, minimum=3):
    return isinstance(x, str) and len(x.strip()) >= minimum and not x.strip().startswith("REPLACE_")


def load_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def scaffold_from_brief(brief, output_dir):
    """Create an UNAPPROVED V25 manifest alongside a V21 Cinema package.

    Does not guess rights, camera, musician, licenses or actual video quality.
    Idempotent: never edits a person's work in an existing manifest.
    """
    if not isinstance(brief,dict):
        raise ValueError("Brief per manifesto V25 deve essere un oggetto")
    path = Path(output_dir) / "ARTVISION_CONTRACT_V25.json"
    if path.exists():
        return path
    template = ROOT / "templates" / "ARTVISION_CONTRACT_V25.json"
    data = load_json(template)
    unique = brief.get("project_id") or brief.get("id") or brief.get("video_id")
    if filled(unique):
        data["video_id"] = str(unique)
    artist = brief.get("artist") or brief.get("artist_name")
    if filled(artist):
        data["artwork"]["artist"] = str(artist).upper()
        data["opening"]["artist_text"] = str(artist).upper()
        data["cover"]["artist"] = str(artist).upper()
        data["on_screen_text"][0]["text"] = str(artist).upper()
    title = brief.get("artwork_title_en") or brief.get("painting_title_en")
    if filled(title):
        data["artwork"]["title_en"] = str(title)
        data["cover"]["title_en"] = str(title)
    # Keep source rights, score composer and artistic checkboxes NOT VERIFIED.
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return path


def check_preflight(data, catalog=None):
    errors = []
    add = errors.append
    if data.get("schema") != "artvision-release-contract-v25":
        add("Schema V25 assente o errato.")
    if data.get("format") != "artvision_cinema":
        add("Questo gate specifico richiede format artvision_cinema; altri format mantengono i loro preset.")
    if not filled(data.get("video_id")):
        add("video_id unico mancante.")
    artwork = data.get("artwork") or {}
    artist = artwork.get("artist")
    title = artwork.get("title_en")
    if not filled(artist) or not filled(title):
        add("Nome artista e titolo dell'opera in inglese obbligatori.")
    if artwork.get("title_language") != "en":
        add("Titolo opera: codice lingua en obbligatorio.")
    if not filled(artwork.get("identity_source")):
        add("Manca URL/fonte identificativa dell'opera.")
    if data.get("approved_baseline") != "cinema_v6":
        add("Manca la baseline immutabile Cinema V6.")

    opening = data.get("opening") or {}
    signature = "modules/artvision/IDENTITA_VISIVA_FISSA_V6.json"
    if opening.get("identity_preset") != signature or opening.get("artist_text") != artist:
        add("La firma iniziale deve riusare esattamente identita V6 + artista.")
    if not filled(opening.get("composer")) or opening.get("music_credit_text") != "MUSIC BY " + str(opening.get("composer", "")).upper():
        add("Firma musicale deve essere MUSIC BY + compositore (nome reale, non un placeholder).")

    cover = data.get("cover") or {}
    if cover.get("identity_family") != "cinema_v6" or cover.get("title_en") != title or cover.get("artist") != artist:
        add("Copertina: identita famiglia Cinema V6, titolo EN e nome artista esatti.")
    if cover.get("language") != "en" or cover.get("existing_design_unchanged") is not True:
        add("Copertina EN, stessa identita e Gold Master storico invariato.")

    texts = data.get("on_screen_text") or []
    expected = {("opening_artist", str(artist)), ("opening_music", str(opening.get("music_credit_text")))}
    try:
        got = {(x["role"], x["text"]) for x in texts}
    except (TypeError, KeyError):
        got = set()
    if got != expected:
        add("Nel film Cinema soltanto firma V6: artista + MUSIC BY compositore; niente altri testi/lingue/CTA.")
    if data.get("voice") is not False or data.get("subtitles") is not False:
        add("Cinema: nessuna voce o sottotitoli.")

    first = data.get("first_seven_seconds") or []
    try:
        seconds = {x["second"] for x in first}
    except (KeyError, TypeError):
        seconds = set()
    if seconds != set(REVIEW_SECONDS) or len(first) != len(REVIEW_SECONDS):
        add("Pianificare fotogrammi reali e scopo a 0/1/3/5/7 secondi.")
    for x in first:
        if not filled(x.get("what_visible"), 14) or not filled(x.get("why"), 14):
            add("Ogni checkpoint iniziale richiede soggetto visibile e motivazione concreta.")
            break

    scenes = data.get("scenes") or []
    if len(scenes) < 8:
        add("Almeno 8 scelte di regia motivate; non basta una successione generica di slide.")
    used = set()
    for i, s in enumerate(scenes):
        if any(not filled(s.get(k), 8) for k in ("subject", "purpose", "source_id")):
            add(f"Inquadratura {i+1}: soggetto, ragione e fonte specifici obbligatori.")
        shot = s.get("shot")
        if shot not in VALID_SHOTS:
            add(f"Inquadratura {i+1}: tipo di shot non definito.")
        used.add(shot)
        if s.get("motion") not in VALID_MOTIONS:
            add(f"Inquadratura {i+1}: moto macchina non permesso.")
        if not isinstance(s.get("duration_seconds"), (float,int)) or s["duration_seconds"] <= 0:
            add(f"Inquadratura {i+1}: durata positiva mancante.")
    if len(used.intersection(VALID_SHOTS)) < 3:
        add("Servono almeno tre famiglie di inquadratura, senza schemi ripetuti.")

    transitions = data.get("transition_reviews_plan") or []
    if len(transitions) < 3 or any(not filled(x.get("why"), 15) for x in transitions):
        add("Motivare almeno tre transizioni centrali; niente tagli meccanici.")
    cues = data.get("music_cues") or []
    if len(cues) < 3 or any(not filled(x.get("reason"), 12) for x in cues):
        add("Tre cue musicali effettivi con motivazione (intro, sviluppo, finale).")
    if not filled(data.get("duration_reason"), 25):
        add("Durata motivata dal contenuto, non da timer fisso.")
    tt = data.get("selected_techniques") or []
    if not 3 <= len(tt) <= 8 or any(not filled(x.get("why"), 12) for x in tt):
        add("Selezionare 3-8 tecniche V23 con ragione individuale.")
    if catalog is None:
        try:
            catalog = {x["id"] for x in load_json(TECHNIQUES)["techniques"]}
        except (OSError, ValueError, KeyError):
            catalog = set()
    for item in tt:
        if item.get("id") not in catalog:
            add("Tecnica V23 inesistente: " + str(item.get("id")))
    if len({x.get("id") for x in tt}) != len(tt):
        add("Tecniche V23 duplicate.")

    sources = data.get("sources") or []
    if not sources or any(not all(filled(s.get(k)) for k in ("id","url","license","credit")) or
                          s.get("status") != "verified" for s in sources):
        add("Fonte visiva: URL, identita, licenza, credito e verifica obbligatori.")
    music = data.get("music") or {}
    if not all(filled(music.get(k)) for k in ("title","composer","origin","license","evidence","emotional_arc")) or music.get("rights_status") != "verified":
        add("Musica: origine, autore, registrazione, licenza, prova e arco emotivo verificati.")
    if music.get("composer") != opening.get("composer"):
        add("Compositore mostrato in apertura diverso da quello documentato.")
    if not (data.get("copy_languages") or {}).get("facebook") == "it":
        add("Descrizione Facebook italiana esterna obbligatoria.")
    if data.get("archive_only_after_authorization") is not True or data.get("social_autopublish") is not False:
        add("Archivio video e pubblicazione social sono autorizzazioni separate.")
    return errors


def probe(path):
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe mancante: non certificare MP4.")
    cmd = ["ffprobe","-v","error","-show_entries","format=duration,size",
           "-show_entries","stream=codec_type,codec_name,width,height","-of","json",str(path)]
    return json.loads(subprocess.check_output(cmd, stderr=subprocess.STDOUT,timeout=40))


def check_final(data, base: Path):
    errors = check_preflight(data)
    info = {"video_sha256": None,"duration": None,"frame_review_dir": None}
    paths = {}
    outs = data.get("outputs") or {}
    root = base.resolve()
    for key, expected in FIELDS.items():
        raw = outs.get(key)
        if raw != expected:
            errors.append(f"Output {key} deve chiamarsi {expected}.")
            continue
        path = (root / raw).resolve()
        if root not in path.parents:
            errors.append(f"Percorso output {key} fuori dalla cartella episodio.")
            continue
        if not path.is_file() or path.stat().st_size < 32:
            errors.append(f"File finale mancante/vuoto: {expected}.")
            continue
        paths[key] = path
    if "video" in paths:
        info["video_sha256"] = sha256(paths["video"])
        try:
            facts = probe(paths["video"])
            streams = facts.get("streams", [])
            duration = float(facts["format"]["duration"])
            info["duration"] = duration
            if duration < 20:
                errors.append("MP4 troppo corto per il Cinema V6 previsto; motivare una eccezione.")
            if not any(s.get("codec_type") == "video" and s.get("width") == 1080 and s.get("height") == 1920 and s.get("codec_name") == "h264" for s in streams):
                errors.append("MP4: video H264 verticale 1080x1920 assente.")
            if not any(s.get("codec_type") == "audio" and s.get("codec_name") == "aac" for s in streams):
                errors.append("MP4: audio AAC assente.")
            if any(s.get("codec_type") == "subtitle" for s in streams):
                errors.append("MP4 contiene sottotitoli non permessi.")
        except (KeyError, ValueError, subprocess.SubprocessError, OSError, RuntimeError) as exc:
            errors.append(f"ffprobe non valido: {exc}")
        if data.get("review_video_sha256") != info["video_sha256"]:
            errors.append("Revisione artistica non legata all'hash del MP4 esatto.")
        if shutil.which("ffmpeg"):
            review_dir = root / "QA_V25"
            review_dir.mkdir(exist_ok=True)
            for s in REVIEW_SECONDS:
                frame = review_dir / f"FRAME_{s:02d}.jpg"
                if not frame.is_file():
                    result = subprocess.run(
                        ["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(s),"-i",str(paths["video"]),
                         "-frames:v","1","-q:v","3",str(frame)],
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
                    if result.returncode or not frame.is_file():
                        errors.append(f"Impossibile estrarre fotogramma autentico {s}s.")
            info["frame_review_dir"] = str(review_dir)
        else:
            errors.append("ffmpeg mancante: campioni reali 0/1/3/5/7 non estraibili.")
    if "cover" in paths:
        try:
            from PIL import Image
            with Image.open(paths["cover"]) as im:
                im.verify()
            with Image.open(paths["cover"]) as im:
                if im.width != 1080 or im.height != 1920:
                    errors.append("Copertina: formato 1080x1920 richiesto.")
        except (ImportError, OSError, ValueError) as exc:
            errors.append("Copertina JPEG non verificata: " + str(exc))
    for key in ("facebook","instagram","tiktok","youtube"):
        if key in paths:
            content = paths[key].read_text(encoding="utf-8")
            if len(content.strip()) < 110 or len(re.findall(r"#[A-Za-zÀ-ÿ0-9_]+",content)) < 2:
                errors.append(f"Post {key} incompleto (testo pertinente, crediti, 2-5 hashtag).")
            tags = re.findall(r"#[A-Za-zÀ-ÿ0-9_]+",content)
            if len(tags) > 5:
                errors.append(f"Post {key}: evitare hashtag eccessivi.")
            artist = str((data.get("artwork") or {}).get("artist") or "").strip().casefold()
            composer = str((data.get("music") or {}).get("composer") or "").strip().casefold()
            if not artist or artist not in content.casefold():
                errors.append(f"Post {key}: manca credito al vero artista.")
            if not composer or composer not in content.casefold():
                errors.append(f"Post {key}: manca credito musicale al compositore.")
            if not any(token in content.casefold() for token in ("fonte:", "fonti:", "source:", "sources:")):
                errors.append(f"Post {key}: manca sezione fonti verificabili.")
    for key in ("recipe","music_manifest"):
        if key in paths:
            try:
                parsed = load_json(paths[key])
                if not isinstance(parsed,dict):
                    errors.append(f"{key}: JSON oggetto non valido.")
            except (ValueError,OSError) as exc:
                errors.append(f"{key}: JSON illeggibile: {exc}")
    if "recipe" in paths and info["video_sha256"]:
        recipe = load_json(paths["recipe"])
        if recipe.get("sha256_mp4") != info["video_sha256"]:
            errors.append("Ricetta senza hash SHA256 effettivo del master.")
        if not filled(recipe.get("renderer"), 8) or not filled(recipe.get("replication_command"), 8):
            errors.append("Ricetta priva di motore e comando concreto per replicare.")
    reviews = data.get("reviews") or {}
    for key in REVIEW_KEYS:
        check = reviews.get(key) or {}
        if check.get("passed") is not True or not filled(check.get("notes"), 30):
            errors.append(f"Review artistica {key} non superata o priva di prova descrittiva.")
    if (data.get("publication") or {}).get("status") not in ("not_published","library_only","social_authorized"):
        errors.append("Stato pubblicazione: distinguere archivio, social e non pubblicato.")
    return errors, info


def pack_delivery(manifest: Path, data, info):
    """Assemble finished media with captions/replication files after successful final gate.

    The caller must enforce final validation. Never overwrite prior bundles.
    Does not send or publish anything.
    """
    root = manifest.parent
    slug = re.sub(r"[^a-z0-9_-]+","-",str(data["video_id"]).lower()).strip("-")[:72]
    if not slug:
        raise ValueError("Video ID non valido per pacchetto")
    fingerprint = str(info["video_sha256"])[:12]
    dest = root / f"ARTVISION_{slug}_{fingerprint}_PACCHETTO_CONSEGNA.zip"
    if dest.exists():
        return dest
    files = [(manifest,manifest.name)]
    for key, filename in FIELDS.items():
        files.append((root / filename, filename))
    frames=root/"QA_V25"
    for second in REVIEW_SECONDS:
        files.append((frames / f"FRAME_{second:02d}.jpg",
                      f"QA_V25/FRAME_{second:02d}.jpg"))
    for src, _ in files:
        if not src.is_file() or src.stat().st_size <= 0:
            raise FileNotFoundError("File del pacchetto mancante: "+str(src))
    try:
        with zipfile.ZipFile(dest,"x") as out:
            for src,name in files:
                compress=(zipfile.ZIP_STORED if src.suffix.lower() in
                          (".mp4",".jpg",".jpeg",".png",".mp3",".wav") else zipfile.ZIP_DEFLATED)
                out.write(src,arcname=name,compress_type=compress)
    except Exception:
        if dest.exists():
            dest.unlink()
        raise
    return dest


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--stage",choices=("preflight","final"),required=True)
    parser.add_argument("--out",default=None)
    parser.add_argument("--bundle",action="store_true",help="Create social/replication ZIP only after final gate passes.")
    args=parser.parse_args(argv)
    manifest=Path(args.manifest).resolve()
    try:
        data=load_json(manifest)
        if args.stage=="preflight":
            errors=check_preflight(data)
            info={}
        else:
            errors,info=check_final(data,manifest.parent)
        if args.bundle:
            if args.stage != "final":
                errors.append("Il pacchetto di consegna si crea soltanto con --stage final.")
            elif not errors:
                try:
                    info["delivery_bundle"] = str(pack_delivery(manifest,data,info))
                except (OSError,ValueError,zipfile.BadZipFile) as exc:
                    errors.append("Creazione ZIP di consegna fallita: " + str(exc))
        report={"schema":"artvision-v25-gate-report","stage":args.stage,
                "status":"BLOCKED" if errors else "PASS_DOCUMENTAL_REVIEW_REQUIRED",
                "errors":errors,"info":info,
                "caveat":"Il gate non verifica automaticamente la bellezza, la fedelta delle opere, la lingua reale del testo o i diritti. Serve osservazione umana. Nessuna pubblicazione automatica."}
    except Exception as exc:
        report={"schema":"artvision-v25-gate-report","stage":args.stage,"status":"BLOCKED",
                "errors":[f"Manifest non leggibile: {type(exc).__name__}: {exc}"]}
    if args.out:
        out=Path(args.out)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if report["errors"] else 0


if __name__=="__main__":
    sys.exit(main())
