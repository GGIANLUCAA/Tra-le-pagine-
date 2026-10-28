#!/usr/bin/env python3
"""V56: preflight conservativo, offline, nessuna rete o API a pagamento.
Convalida fatti/diritti/realta delle consegne; NON valuta bellezza o verita delle fonti.
python src/storia_rivive_preflight_v56.py --plan templates/STORIA_RIVIVE_V56_EPISODE.json --stage source
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

PLATFORMS = ("facebook", "instagram", "tiktok", "youtube")
ALLOWED_COLOR = ("bw_original", "sepia_tint", "ai_colorized")


def nonblank(v):
    return isinstance(v, str) and bool(v.strip()) and "TODO" not in v.upper() and "DA VERIFICARE" not in v.upper()


def filehash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def media_probe(path):
    if not shutil.which("ffprobe"):
        raise ValueError("ffprobe non disponibile")
    p = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                        "-show_streams", "-show_format", str(path)],
                       capture_output=True, text=True, timeout=45)
    if p.returncode:
        raise ValueError("ffprobe: " + p.stderr[:300])
    return json.loads(p.stdout)


def evaluate(plan, stage="source"):
    errors, warnings = [], []
    source = plan.get("source", {})
    rights = plan.get("rights", {})
    editorial = plan.get("editorial", {})
    review = plan.get("review", {})
    color = plan.get("colorization", {})
    cost = plan.get("cost", {})
    audio = plan.get("audio", {})
    delivery = plan.get("delivery", {})
    def need(ok, msg):
        if not ok:
            errors.append(msg)
    need(plan.get("format") == "storia_rivive", "Formato non storia_rivive")
    need(nonblank(source.get("title")), "Titolo sorgente mancante")
    need(nonblank(source.get("file_page_url")) and str(source.get("file_page_url", "")).startswith("https://"),
         "URL pagina sorgente HTTPS mancante")
    need(nonblank(source.get("archive_or_author")), "Archivio/autore mancante")
    need(nonblank(source.get("location")), "Luogo non confermato")
    need(isinstance(source.get("year"), int) and 1850 <= source.get("year", 0) <= 1950,
         "Anno storico non confermato")
    license_name = rights.get("license")
    need(nonblank(license_name), "Licenza singolo file mancante")
    need(nonblank(rights.get("reviewed_on")), "Data controllo diritti mancante")
    need(rights.get("reviewed_by_human") is True, "Verifica dei diritti non confermata")
    if license_name and license_name.upper() not in ("CC0", "CC0 1.0"):
        need(rights.get("jurisdiction_reviewed") is True,
             "Licenza non CC0: necessaria verifica giurisdizione/termini")
    need(rights.get("source_rights_clear_for_commercial_reuse") is True,
         "Diritti di riuso commerciale non verificati")
    need(cost.get("approved_max_eur", 0) == 0 or cost.get("per_clip_authorization") is True,
         "Crediti/spesa non autorizzati per la clip specifica")
    need(cost.get("vidu_calls_planned", 0) == 0 or cost.get("per_clip_authorization") is True,
         "Chiamate Vidu senza autorizzazione per clip")
    need(cost.get("automatic_paid_retry") is not True, "Retry a pagamento vietato")
    need(delivery.get("social_autopublish") is not True, "Pubblicazione social automatica vietata")
    if stage in ("pre-render", "delivery"):
        need(isinstance(source.get("start_sec"), (int, float)) and source.get("start_sec", -1) >= 0,
             "Timecode iniziale non verificato")
        need(isinstance(source.get("end_sec"), (int, float)) and
             source.get("end_sec", 0) > source.get("start_sec", 10**10),
             "Timecode finale non verificato")
        need(nonblank(editorial.get("opening_0_3")), "Gancio 0–3 s non studiato")
        need(nonblank(editorial.get("reveal_3_7")), "Rivelazione 3–7 s non studiata")
        need(nonblank(editorial.get("framing_reason")), "Crop/letterbox non motivato")
        need(editorial.get("no_faces_cut_reviewed") is True, "Revisione volti/soggetti non fatta")
        need(editorial.get("first_frame_location_year_verified") is True,
             "Primo frame luogo/anno da verificare")
        need(color.get("mode") in ALLOWED_COLOR, "Tipo di colore non dichiarato")
        if color.get("mode") == "ai_colorized":
            need(color.get("same_source_frames") is True, "AI: fotogrammi differenti dall'originale")
            need(color.get("temporal_stability_reviewed") is True, "AI: stabilita temporale non esaminata")
            need(nonblank(color.get("model_and_version")), "AI: modello/versione mancante")
        if color.get("mode") == "sepia_tint":
            need(color.get("described_as_ai_colorized") is not True, "Sepia spacciata per colorizzazione AI")
        if audio.get("has_music") is True:
            need(nonblank(audio.get("music_source")) and nonblank(audio.get("music_license")),
                 "Musica e relativi diritti non verificati")
    if stage == "delivery":
        paths = delivery.get("files", {})
        required = ["mp4", "cover_jpg", "rights_json", "recipe_json",
                    "qa_json", "complete_zip"]
        for key in required:
            f = paths.get(key)
            need(nonblank(f) and Path(f).is_file() and Path(f).stat().st_size > 0,
                 "File V55 mancante: " + key)
        social = delivery.get("social_posts", {})
        for k in PLATFORMS:
            f = social.get(k)
            need(nonblank(f) and Path(f).is_file() and Path(f).stat().st_size > 30,
                 "Post V28 mancante: " + k)
        names = [Path(social[k]).read_text(encoding="utf-8").strip().casefold()
                 for k in PLATFORMS if nonblank(social.get(k)) and Path(social[k]).is_file()]
        need(len(set(names)) == 4, "Post social mancanti o identici")
        need(review.get("watched_and_listened_full_video") is True, "Film non realmente visto/ascoltato")
        need(review.get("opening_0_1_3_5_7_reviewed") is True, "Apertura 0/1/3/5/7s non controllata")
        need(review.get("crop_faces_color_audio_checked") is True, "Review di crop/colore/audio assente")
        need(review.get("source_facts_matched_to_video") is True, "Fatti non verificati con le scene")
        need(nonblank(review.get("timecoded_notes")), "Note QA con timecode assenti")
        if nonblank(paths.get("mp4")) and Path(paths["mp4"]).is_file():
            try:
                meta = media_probe(paths["mp4"])
                streams = meta.get("streams", [])
                vs = next((s for s in streams if s.get("codec_type") == "video"), {})
                need(vs.get("codec_name") == "h264", "MP4 non H264")
                need(vs.get("width", 0) * 16 == vs.get("height", 0) * 9, "Aspect ratio non 9:16")
                if audio.get("has_music") or audio.get("has_voice"):
                    need(any(s.get("codec_type") == "audio" and s.get("codec_name") == "aac"
                             for s in streams), "AAC audio mancante")
                recorded = delivery.get("mp4_sha256")
                need(nonblank(recorded) and filehash(paths["mp4"]) == recorded,
                     "SHA256 MP4 mancante/discordante")
            except (ValueError, subprocess.TimeoutExpired, OSError) as exc:
                errors.append("Probe MP4 fallito: " + str(exc))
        if not delivery.get("chatgpt_android_download_tested"):
            warnings.append("chatgpt_android_download_pending")
        if not delivery.get("archive_catalog_playback_cover_social_zip_tested"):
            warnings.append("archive_sync_pending")
        if not delivery.get("zip_crc_checked"):
            errors.append("CRC ZIP non controllato (usare artvision_delivery_v55.py pack)")
    return {"ok": not errors, "stage": stage, "errors": errors,
            "warnings": warnings, "technical_not_artistic_approval": True}


def main():
    p = argparse.ArgumentParser(description="Gate V56 Storia Rivive (offline)")
    p.add_argument("--plan", required=True)
    p.add_argument("--stage", choices=["source", "pre-render", "delivery"], default="source")
    p.add_argument("--report", help="Percorso JSON opzionale")
    args = p.parse_args()
    try:
        result = evaluate(json.loads(Path(args.plan).read_text(encoding="utf-8")), args.stage)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"ok": False, "stage": args.stage, "errors": [str(exc)], "warnings": []}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.report:
        dest = Path(args.report)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(output + "\n", encoding="utf-8")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
