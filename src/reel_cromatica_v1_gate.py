#!/usr/bin/env python3
"""Gate del profilo `reel_cromatica_v1`: verifica un brief contro il profilo di formato.

Controlli strutturali sul piano di regia (durata, grammatica degli shot, packaging
delle scritte sovrimpresse, diritti dichiarati, assenza di sottotitoli).
NON certifica qualità estetica, retention, licenze reali né approvazione di pubblicazione.
Nessuna spesa, nessun render, nessuna pubblicazione, nessuna modifica ai master.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

try:
    from director_reference_v326 import analyze_scenes
except ImportError:  # CLI: python src/reel_cromatica_v1_gate.py
    from .director_reference_v326 import analyze_scenes

FLAG_RE = re.compile(r"[\U0001F1E6-\U0001F1FF]")
SUBTITLE_KEYS = ("subtitles", "subtitle", "subtitle_track", "subtitle_tracks", "srt", "ass", "burn_in_subtitles")
POST_FILES = {
    "facebook": "POST_FACEBOOK.txt",
    "instagram": "POST_INSTAGRAM.txt",
    "tiktok": "POST_TIKTOK.txt",
    "youtube": "POST_YOUTUBE.txt",
}
SOCIAL_HOSTS = ("youtube.com", "youtu.be", "facebook.com", "instagram.com", "tiktok.com", "drive.google.com")
CTA_PHRASES = (
    "dale like", "dar like", "haz like", "no te olvides de",
    "sigueme", "suscribete", "comenta", "comparte", "escribe en los comentarios",
)
ITA_MARKERS = (" degli ", " delle ", " della ", " dell'", " nel ", " questa ", " perche ", " cosi ", " quindi ", " gli ")
ES_MARKERS = (" el ", " la ", " los ", " las ", " que ", " con ", " por ", " para ", " desde ", " sobre ")
CREDIT_MARKERS = ("cc by", "cc-by", "licencia", "dominio publico", "public domain", "musica", "music")
INTERNAL_MARKERS = ("brief", "storyboard", "template", "json", "shot list", "pipeline", "workflow", "montaje")
TYPO_PATTERNS = (
    (r"\b([a-zA-ZÀ-ÿ]{3,})\s+\1\b", "parola ripetuta"),
    (r"\s+[,.;:]", "spazio prima della punteggiatura"),
    (r"[,.;:][^\s\d#(]", "spazio mancante dopo la punteggiatura"),
    (r"\b(de|a) el\b", "preposizione articolata malformata"),
)
URL_RE = re.compile(r"https?://\S+")
CREDIT_LINE_RE = re.compile(
    r"(cc\s*-?\s*by|licencia|licencias|dominio publico|dominio público|public domain|musica|música|wikimedia)",
    re.IGNORECASE,
)


def _norm(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _fold(text):
    decomposed = unicodedata.normalize("NFD", str(text or ""))
    plain = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return plain.lower()


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", _fold(text)))


def _jaccard(left, right):
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _editorial_body(text):
    """Corpo redazionale del post: senza hashtag e senza righe di credito/licenza.

    Hashtag e crediti sono obbligatori e identici per canale: misurarli come
    somiglianza editoriale gonfierebbe il punteggio e mascherebbe i tagli uguali.
    """
    kept = []
    for line in str(text or "").splitlines():
        stripped = re.sub(r"#\w+", " ", line)
        if CREDIT_LINE_RE.search(stripped):
            continue
        kept.append(stripped)
    return _norm(" ".join(kept))


def _mentions_subject(text, brief):
    blob = _fold(text)
    artist = _norm(brief.get("artist"))
    if artist and _fold(artist.split()[-1]) in blob:
        return True
    title = _norm((brief.get("episode") or {}).get("title"))
    if title and _fold(title) in blob:
        return True
    for shot in brief.get("scenes") or []:
        artwork = _norm(shot.get("artwork"))
        if artwork and _fold(artwork) in blob:
            return True
    return False


def _scene_span(shot):
    if "start" in shot and "end" in shot:
        return float(shot["start"]), float(shot["end"])
    if "duration" in shot:
        start = float(shot.get("start", 0.0))
        return start, start + float(shot["duration"])
    return None, None


def check(brief, profile):
    blockers: list[str] = []
    warnings: list[str] = []

    duration_cfg = profile["delivery"]["duration_seconds"]
    shots_cfg = profile["rhythm"]["target_shots"]
    frames = set(profile["shot_grammar"]["framing"])
    moves = set(profile["shot_grammar"]["movements"])
    systems = {s["id"]: s for s in profile["packaging"]["systems"]}
    allowed_terms = [t.lower() for t in profile["rights"]["allowed_reuse_terms"]]
    forbidden_words = [w.lower() for w in profile["social_posts"]["forbidden_public_words"]]
    forbidden_cliches = [c.lower() for c in profile["social_posts"]["forbidden_cliches"]]
    reference = profile["reference"]["reference_sample_measured"]

    scenes = brief.get("scenes") or []
    if not isinstance(scenes, list) or not scenes:
        return ["Nessuna inquadratura nel brief"], [], {}

    # --- durata e timeline -------------------------------------------------
    total = 0.0
    for index, shot in enumerate(scenes, 1):
        start, end = _scene_span(shot)
        if start is None:
            blockers.append(f"Scena {index}: durata o timecode mancante")
            continue
        if end <= start:
            blockers.append(f"Scena {index}: durata non positiva")
            continue
        if index == 1 and abs(start) > 0.05:
            blockers.append("La prima scena deve partire da 0.0 s")
        if index > 1:
            previous = _scene_span(scenes[index - 2])
            if previous[1] is not None:
                if start < previous[1] - 0.08:
                    blockers.append(f"Scena {index}: sovrapposizione non prevista ({start:.2f} < {previous[1]:.2f})")
                elif start > previous[1] + 0.35:
                    blockers.append(f"Scena {index}: intervallo non coperto (buca fino a {start:.2f} s)")
        total = max(total, end)

    if not duration_cfg["min"] <= total <= duration_cfg["max"]:
        blockers.append(f"Durata totale {total:.2f} s fuori dal range {duration_cfg['min']}–{duration_cfg['max']} s")
    min_delta = float(duration_cfg.get("must_differ_from_reference_by_seconds", 0.0))
    if abs(total - reference["duration_seconds"]) < min_delta:
        blockers.append(
            f"Durata troppo vicina al campione di riferimento ({reference['duration_seconds']} s): "
            f"copierebbe il timing del riferimento"
        )
    if not shots_cfg["min"] <= len(scenes) <= shots_cfg["max"]:
        warnings.append(f"Numero di inquadrature {len(scenes)} fuori dal target {shots_cfg['min']}–{shots_cfg['max']}")

    # --- grammatica dei shot ------------------------------------------------
    previous_move = None
    run = 0
    for index, shot in enumerate(scenes, 1):
        framing = shot.get("framing")
        move = shot.get("move")
        if framing not in frames:
            blockers.append(f"Scena {index}: inquadratura '{framing}' non prevista dal profilo")
        if move not in moves:
            blockers.append(f"Scena {index}: movimento '{move}' non previsto dal profilo")
        if not _norm(shot.get("purpose")):
            warnings.append(f"Scena {index}: manca la motivazione della scelta")
        if not _norm(shot.get("visual_anchor")):
            blockers.append(f"Scena {index}: manca l'ancora visiva")
        reason = _norm(shot.get("camera_reason"))
        if not reason:
            blockers.append(f"Scena {index}: manca la ragione registica")
        elif reason.lower() == "auto_zoom":
            blockers.append(f"Scena {index}: camera_reason 'auto_zoom' non è una ragione registica")
        run = run + 1 if move == previous_move else 1
        if run == 3:
            warnings.append(f"Scena {index}: tre movimenti '{move}' consecutivi")
        previous_move = move
        start, end = _scene_span(shot)
        if start is not None and shot.get("complex_detail") and (end - start) < profile["rhythm"]["variation"]["complex_detail_min_seconds"] and not shot.get("rhythm_justification"):
            warnings.append(f"Scena {index}: dettaglio complesso sotto i {profile['rhythm']['variation']['complex_detail_min_seconds']} s")
        if start is not None and move == "static" and (end - start) > profile["rhythm"]["duration_rules"]["max_static_shot_seconds_in_short"]:
            warnings.append(f"Scena {index}: piano statico troppo lungo per uno short")
    if scenes and not scenes[0].get("visual_hook"):
        warnings.append("Apertura priva di gancio VISIVO motivato")

    rhythm_block, rhythm_warn, rhythm_facts = analyze_scenes(
        scenes, short=brief.get("format") == "artvision_meraviglia_breve")
    blockers.extend(f"Rhythm V326 — {item['message']}" for item in rhythm_block)
    warnings.extend(f"Rhythm V326 — {item['message']}" for item in rhythm_warn)

    # --- packaging delle scritte sovrimpresse -------------------------------
    packaging = brief.get("packaging") or {}
    system_id = packaging.get("system")
    if system_id not in systems:
        blockers.append(f"Packaging: sistema '{system_id}' non previsto dal profilo")
    else:
        used = set()
        for index, shot in enumerate(scenes, 1):
            overlay = shot.get("on_screen_text")
            if not overlay:
                continue
            used.add(overlay.get("system"))
            if overlay.get("system") != system_id:
                blockers.append(f"Scena {index}: overlay di un sistema diverso da quello dichiarato")
            if system_id == "chip":
                rows = overlay.get("rows") or []
                if len(rows) != 3:
                    blockers.append(f"Scena {index}: il chip richiede tre righe")
                else:
                    if not _norm(rows[0].get("text")):
                        blockers.append(f"Scena {index}: la riga 1 del chip è obbligatoria")
                    for row in rows:
                        if not _norm(row.get("text")) or not row.get("background") or not row.get("text_color"):
                            blockers.append(f"Scena {index}: riga del chip incompleta (testo, sfondo o colore)")
                    if not FLAG_RE.search(str(rows[2].get("text", ""))):
                        blockers.append(f"Scena {index}: la riga 3 del chip richiede la bandiera del paese")
            elif system_id == "serif_cartello":
                lines = overlay.get("lines") or []
                if len(lines) != 3:
                    blockers.append(f"Scena {index}: il cartello serif richiede tre righe (nome, anni, paese)")
            elif system_id == "question_hook":
                if not _norm((overlay.get("line_1") or {}).get("text")) or not _norm((overlay.get("line_2") or {}).get("text")):
                    blockers.append(f"Scena {index}: la domanda richiede la frase e la sotto-riga")
        if packaging.get("in_cover_frame") and not scenes[0].get("on_screen_text"):
            blockers.append("Il titolo deve essere dentro il fotogramma di copertina")
        if len(used) > 1:
            blockers.append("Nel reel è ammesso un solo sistema tipografico")

    last_text_free = total - profile["packaging"]["no_text_in_final_seconds"]
    for index, shot in enumerate(scenes, 1):
        if not shot.get("on_screen_text"):
            continue
        start, end = _scene_span(shot)
        if start is None:
            continue
        if end > last_text_free + 0.01:
            blockers.append(f"Scena {index}: testo sovrapposto agli ultimi {profile['packaging']['no_text_in_final_seconds']} s")

    # --- linguaggio pubblico -------------------------------------------------
    public_chunks = [str(shot.get("on_screen_text") or "") for shot in scenes]
    editorial = brief.get("editorial") or {}
    public_chunks += [str(editorial.get(key) or "") for key in ("opening", "body", "question")]
    for row in (packaging.get("rows") or []):
        public_chunks.append(str(row.get("text") or ""))
    for line in (packaging.get("lines") or []):
        public_chunks.append(str(line))
    blob = " ".join(public_chunks).lower()
    for word in forbidden_words:
        if re.search(rf"(?<![a-z0-9áéíóúüñ]){re.escape(word.lower())}(?![a-z0-9áéíóúüñ])", blob):
            blockers.append(f"Testo pubblico: parola vietata '{word}'")
    for cliche in forbidden_cliches:
        if cliche in blob:
            blockers.append(f"Testo pubblico: cliché vietato '{cliche}'")
    if not _norm(editorial.get("opening")) or not _norm(editorial.get("body")):
        warnings.append("Testo editoriale incompleto")
    hashtags = editorial.get("hashtags") or []
    tag_cfg = profile["social_posts"]["hashtags"]
    if not tag_cfg["min"] <= len(hashtags) <= tag_cfg["max"]:
        warnings.append(f"Hashtag: {len(hashtags)}, attesi {tag_cfg['min']}–{tag_cfg['max']}")
    if not editorial.get("fact_sources_checked"):
        warnings.append("Fatti del post ancora da verificare")
    if not brief.get("artistic_review_complete"):
        warnings.append("Revisione artistica completa ancora necessaria")

    # --- quattro post pubblici distinti (V28) --------------------------------
    posts_cfg = profile["social_posts"]
    platforms = posts_cfg["platforms"]
    social = brief.get("social_posts") or {}
    post_texts = {}
    if not social:
        blockers.append("Mancano i quattro post pubblici distinti (V28)")
    else:
        for platform in platforms:
            raw = social.get(platform)
            text = _norm(raw)
            if not text:
                blockers.append(f"Post {platform}: testo mancante o vuoto")
            else:
                post_texts[platform] = raw
        if len(post_texts) == len(platforms):
            bodies = {platform: _editorial_body(text) for platform, text in post_texts.items()}
            names = list(post_texts)
            for index, left in enumerate(names):
                for right in names[index + 1:]:
                    similarity = _jaccard(bodies[left], bodies[right])
                    if similarity >= 0.75:
                        blockers.append(
                            f"Post {left} e {right}: testi quasi identici "
                            f"(somiglianza {similarity:.0%}), V28 richiede versioni distinte"
                        )
                    elif similarity >= 0.6:
                        warnings.append(
                            f"Post {left} e {right}: testi molto vicini "
                            f"(somiglianza {similarity:.0%}), rivedere la differenza di taglio"
                        )
        for platform, text in post_texts.items():
            blob_post = _fold(text)
            for word in forbidden_words:
                if re.search(rf"(?<![a-z0-9]){re.escape(_fold(word))}(?![a-z0-9])", blob_post):
                    blockers.append(f"Post {platform}: parola vietata '{word}'")
            for cliche in forbidden_cliches:
                if _fold(cliche) in blob_post:
                    blockers.append(f"Post {platform}: cliché vietato '{cliche}'")
            for cta in CTA_PHRASES:
                if re.search(rf"(?<![a-z0-9]){re.escape(cta)}(?![a-z0-9])", blob_post):
                    blockers.append(f"Post {platform}: richiesta di interazione non ammessa '{cta}'")
            for marker in INTERNAL_MARKERS:
                if re.search(rf"(?<![a-z0-9]){re.escape(marker)}(?![a-z0-9])", blob_post):
                    blockers.append(f"Post {platform}: termine interno di lavorazione '{marker}'")
            if not _mentions_subject(text, brief):
                blockers.append(f"Post {platform}: il testo non cita l'artista né un'opera del reel")
            tags = re.findall(r"#\w+", text)
            if not tag_cfg["min"] <= len(tags) <= tag_cfg["max"]:
                warnings.append(f"Post {platform}: {len(tags)} hashtag, attesi {tag_cfg['min']}–{tag_cfg['max']}")
            if not any(marker in blob_post for marker in CREDIT_MARKERS):
                warnings.append(f"Post {platform}: crediti musicali e licenze assenti dal testo pubblico")
            if any(marker in blob_post for marker in ITA_MARKERS):
                warnings.append(f"Post {platform}: possibile italiano residuo in un canale spagnolo")
            if not any(marker in blob_post for marker in ES_MARKERS):
                warnings.append(f"Post {platform}: nessun segnale di spagnolo, verificare la lingua")
            for pattern, label in TYPO_PATTERNS:
                if re.search(pattern, URL_RE.sub(" ", text)):
                    warnings.append(f"Post {platform}: {label}")
            if text.count("?") > 1 or text.count("!") > 2:
                warnings.append(f"Post {platform}: troppe domande o punti esclamativi")

    # --- confronto a 3 candidate (V32) --------------------------------------
    research = brief.get("audience_research")
    if not isinstance(research, dict):
        blockers.append("Confronto delle candidate (V32) mancante")
    else:
        candidates = research.get("candidates")
        user_specified = (
            research.get("selection_mode") == "user_specified"
            and _norm(research.get("explicit_user_instruction"))
        )
        minimum = 1 if user_specified else 3
        if research.get("selection_mode") == "user_specified" and not user_specified:
            blockers.append("V32: soggetto imposto senza istruzione esplicita")
        if not isinstance(candidates, list) or len(candidates) < minimum:
            blockers.append(f"V32: confrontare almeno {minimum} opere o temi")
        else:
            seen = set()
            for index, candidate in enumerate(candidates, 1):
                required = ("artist", "work", "visual_hook", "human_interest",
                            "historical_anchor", "asset_rights_notes", "comparison_reason")
                if any(not _norm(candidate.get(key)) for key in required):
                    blockers.append(f"V32: candidato {index} incompleto")
                    continue
                identity = (candidate["artist"], candidate["work"])
                if identity in seen:
                    blockers.append("V32: candidato duplicato")
                seen.add(identity)
                signal = candidate.get("audience_signal")
                if not isinstance(signal, dict) or signal.get("status") not in ("verified", "unavailable"):
                    blockers.append(f"V32: candidato {index} senza segnale dichiarato")
                elif signal["status"] == "verified":
                    if any(not _norm(signal.get(key)) for key in ("reference", "observation", "checked_on")):
                        blockers.append(f"V32: candidato {index} con segnale senza fonte o data")
                elif not _norm(signal.get("reason")):
                    blockers.append(f"V32: candidato {index} senza motivo di indisponibilità")
            selected = _norm(research.get("selected_work"))
            if not selected or selected not in {_norm(item.get("work")) for item in candidates if isinstance(item, dict)}:
                blockers.append("V32: scegliere esplicitamente una delle opere confrontate")
        for key in ("selection_reason", "viewer_interest", "creative_direction", "signal_limitations"):
            if not _norm(research.get(key)):
                blockers.append(f"V32: motivazione mancante: {key}")

    # --- diritti e fonti ------------------------------------------------------
    sources = brief.get("sources") or []
    if not sources:
        blockers.append("Registro fonti mancante")
    known = {}
    for index, source in enumerate(sources, 1):
        artwork = source.get("artwork")
        url = str(source.get("url") or "")
        terms = str(source.get("reuse_terms") or "")
        if not artwork or not url or not terms:
            blockers.append(f"Fonte {index}: compilare opera, URL e condizioni di riuso")
            continue
        if not url.startswith("https://"):
            blockers.append(f"Fonte {index}: URL non valido")
        if terms.lower() not in allowed_terms:
            blockers.append(f"Fonte {index}: condizioni di riuso '{terms}' non ammesse dal profilo")
        if any(host in url.lower() for host in SOCIAL_HOSTS):
            warnings.append(f"Fonte {index}: URL di una piattaforma sociale, non di un archivio museale")
        known.setdefault(artwork, source)
    for index, shot in enumerate(scenes, 1):
        artwork = shot.get("artwork")
        if artwork and artwork not in known:
            blockers.append(f"Scena {index}: opera '{artwork}' non registrata nel registro fonti")
        source = known.get(artwork)
        if source:
            width = source.get("usable_width_px_9_16")
            minimum = profile["shot_grammar"]["crop_rules"]["min_usable_width_px_after_vertical_crop"]
            if isinstance(width, (int, float)) and width < minimum:
                warnings.append(f"Fonte {artwork}: {int(width)} px utili dopo il crop 9:16, sotto i {minimum} px")

    # --- audio ---------------------------------------------------------------
    music = brief.get("music") or {}
    for field in ("title", "composer", "source_url", "license_url"):
        if not _norm(music.get(field)):
            blockers.append(f"Musica: '{field}' mancante")
    if not music.get("instrumental"):
        warnings.append("Musica: brano non dichiarato come strumentale")
    if music.get("recording_verified") is False:
        warnings.append("Musica: registrazione specifica ancora da verificare con ffprobe")

    # --- sottotitoli e materiale del campione ---------------------------------
    for key in SUBTITLE_KEYS:
        if key in brief:
            blockers.append(f"Sottotitoli vietati: il brief contiene '{key}'")
    for index, source in enumerate(sources, 1):
        url = str(source.get("url") or "").lower()
        if any(host in url for host in SOCIAL_HOSTS):
            warnings.append(f"Fonte {index}: possibile materiale del campione, usare solo archivi museali")

    facts = {
        "shots": len(scenes),
        "duration_seconds": round(total, 3),
        "duration_range": [duration_cfg["min"], duration_cfg["max"]],
        "reference_duration_delta_seconds": round(abs(total - reference["duration_seconds"]), 3),
        "packaging_system": system_id,
        "distinct_works": len({s.get("artwork") for s in scenes}),
        "scenes_with_text": sum(1 for s in scenes if s.get("on_screen_text")),
        "rhythm_v326": rhythm_facts,
        "visual_truth_verified": False,
        "rights_cleared": False,
        "artistically_approved": False,
        "automatically_publishable": False,
    }
    return blockers, list(dict.fromkeys(warnings)), facts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--profile", type=Path, default=Path("config/reel_cromatica_v1.json"))
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    brief = json.loads(args.brief.read_text(encoding="utf-8"))
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    blockers, warnings, facts = check(brief, profile)

    report = {
        "schema": "reel-cromatica-v1-gate",
        "profile": str(args.profile),
        "brief": str(args.brief),
        "status": "blocked" if blockers else "profile_compliant_pending_artistic_review",
        "blocking_issues": blockers,
        "warnings": warnings,
        "facts": facts,
        "note": "Controllo strutturale del piano: non certifica qualità estetica, diritti, retention o pubblicazione.",
    }
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "REEL_CROMATICA_V1_GATE.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not blockers:
            social = brief.get("social_posts") or {}
            for platform in profile["social_posts"]["platforms"]:
                text = social.get(platform)
                if text:
                    paragraphs = [" ".join(line.split()) for line in str(text).splitlines()]
                    body = "\n\n".join(part for part in paragraphs if part)
                    (args.out / POST_FILES[platform]).write_text(body + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "blockers": len(blockers), "warnings": len(warnings),
                      "out": str(args.out) if args.out else None}, ensure_ascii=False))
    return int(bool(blockers))


if __name__ == "__main__":
    raise SystemExit(main())
