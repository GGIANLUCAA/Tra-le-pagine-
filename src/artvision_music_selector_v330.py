#!/usr/bin/env python3
"""ArtVision V330: curated reusable 20-recording music palette.

Selection is artwork/mood first, repeat avoidance second. Actual audio is
fetched from the composer's catalogue ONLY when explicitly preparing a
private review; no speculative use of a URL as evidence of a valid recording.
Master videos are never changed in place. No billed APIs, publishing, or Gold.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, subprocess, urllib.request
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "artvision_music_20_v1.json"
FALLBACK_CACHE = ROOT / "output" / "artvision-music-v330" / "recordings"
OFFICIAL_DOMAIN = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
CREDIT_LICENSE = "https://creativecommons.org/licenses/by/4.0/"
MOODS = frozenset({
    "adventure", "battle", "bright", "calm", "contemplative", "dark",
    "dramatic", "dreamlike", "eerie", "epic", "ghostly", "grief",
    "grotesque", "heroic", "hopeful", "magical", "melancholic",
    "mysterious", "mystical", "noir", "ominous", "reflective",
    "romantic", "solemn", "somber", "suspense", "tender",
    "uplifting", "whimsical"
})

# Only an editorial guide: unlike a human, lexical parsing cannot see the
# painting or hear the track. The user/editor may override with --moods.
LEXICAL_MOODS = {
    "death": ("grief", "somber", "dark"),
    "dead": ("grief", "melancholic", "somber"),
    "mother": ("tender", "grief"),
    "child": ("tender", "reflective"),
    "vampire": ("dark", "eerie", "mysterious"),
    "ghost": ("ghostly", "eerie", "mysterious"),
    "siren": ("magical", "mysterious", "epic"),
    "mermaid": ("magical", "dreamlike", "romantic"),
    "sleeping": ("dreamlike", "tender", "magical"),
    "beauty": ("romantic", "magical"),
    "fairy": ("magical", "whimsical", "dreamlike"),
    "witch": ("eerie", "magical", "dark"),
    "horror": ("dark", "grotesque"),
    "triumph": ("epic", "dramatic"),
    "hunt": ("epic", "heroic", "mystical"),
    "odin": ("epic", "mystical", "heroic"),
    "battle": ("battle", "epic", "dramatic"),
    "pompeii": ("epic", "dramatic", "ominous"),
    "war": ("battle", "epic"),
    "storm": ("dramatic", "mystical"),
    "shipwreck": ("dramatic", "somber"),
    "alchemist": ("mysterious", "contemplative"),
    "forest": ("magical", "mysterious"),
    "garden": ("magical", "calm"),
    "dream": ("dreamlike", "tender"),
    "sunrise": ("bright", "hopeful"),
    "love": ("romantic", "tender"),
    "night": ("mysterious", "noir"),
    "stairs": ("magical", "dreamlike"),
    "intrigue": ("noir", "mysterious"),
    "fun": ("whimsical", "bright"),
    "divine": ("solemn", "mystical"),
    # Simple Italian nouns from owner briefs:
    "morte": ("grief", "somber", "dark"),
    "madre": ("tender", "grief"),
    "bambina": ("grief", "tender"),
    "caccia": ("epic", "heroic"),
    "battaglia": ("battle", "epic"),
    "sirena": ("dreamlike", "magical"),
    "sirene": ("magical", "mysterious"),
    "fiaba": ("dreamlike", "magical"),
    "tempesta": ("dramatic", "mystical"),
    "bosco": ("magical", "mysterious")
}
# Four versions of the same painting must never count as four successive
# distinct works for recency.
RECENT_DIFFERENT_WORKS = 3

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for b in iter(lambda: source.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def run(command: list[str]) -> bytes:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=240, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace")[-1800:])
    return result.stdout

def probe(path: Path) -> dict:
    return json.loads(run(["ffprobe", "-v", "error", "-show_format",
                           "-show_streams", "-of", "json", str(path)]))

def recording_metadata(path: Path) -> dict:
    data = probe(path)
    audio = [x for x in data.get("streams", []) if x.get("codec_type") == "audio"]
    if not audio or float(data["format"].get("duration") or 0) < 30:
        raise ValueError("File is not a playable, sufficiently long soundtrack")
    if any(a.get("codec_name") not in ("mp3", "aac", "flac", "vorbis", "pcm_s16le",
                                      "pcm_s24le") for a in audio):
        raise ValueError("Unknown / unexpected audio codec")
    return {
        "seconds": float(data["format"]["duration"]),
        "codec": audio[0]["codec_name"],
        "bitrate": int(audio[0].get("bit_rate") or data["format"].get("bit_rate") or 0),
        "channels": int(audio[0].get("channels") or 0),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }

def load_catalog(path: Path = CATALOG) -> dict:
    data = json.loads(path.read_text(encoding="utf8"))
    tracks = data.get("tracks")
    if data.get("schema") != "artvision-fixed-20-music-library-v1" or \
       data.get("fixed_slots") != 20 or not isinstance(tracks, list) or len(tracks) != 20:
        raise ValueError("V330 catalog must have exactly 20 stable entries")
    ids, isrcs, urls = set(), set(), set()
    for num, track in enumerate(tracks, 1):
        if track.get("slot") != num or not all(track.get(x) for x in
            ("id", "title", "composer", "isrc", "source_url", "download_url",
             "license", "license_url", "editorial_moods")):
            raise ValueError("Invalid V330 music slot " + str(num))
        if track["id"] in ids or track["isrc"] in isrcs or track["download_url"] in urls:
            raise ValueError("Duplicate musical recording in the fixed 20")
        ids.add(track["id"]); isrcs.add(track["isrc"]); urls.add(track["download_url"])
        if track["license"] != "CC BY 4.0" or track["license_url"] != CREDIT_LICENSE:
            raise ValueError("Unapproved license / missing attribution")
        if not track["download_url"].startswith(OFFICIAL_DOMAIN):
            raise ValueError("Only official composer download URLs allowed")
        if not all(m in MOODS for m in track["editorial_moods"]):
            raise ValueError("Invalid mood in curated catalog")
        if float(track.get("duration_seconds") or 0) < 60:
            raise ValueError("Track duration in catalog implausible")
    return data

def canon_work(title: str, artist: str) -> str:
    raw = (title + " | " + artist).casefold()
    return re.sub(r"[^a-z0-9]+", "-", raw).strip("-")

def infer_moods(text: str) -> list[str]:
    raw = text.casefold()
    found = []
    # Word-boundaries avoid "death" matching unrelated text.
    for token, moods in LEXICAL_MOODS.items():
        if re.search(r"(?<!\w)" + re.escape(token) + r"(?!\w)", raw):
            for mood in moods:
                if mood not in found: found.append(mood)
    return found[:6]

def _history_recent(history: list[dict], work_id: str) -> list[str]:
    out, seen = [], set()
    for e in reversed(history):
        if not isinstance(e, dict): continue
        key = str(e.get("work_id") or e.get("work") or "")
        if not key or key == work_id or key in seen: continue
        seen.add(key)
        song = str(e.get("track_id") or e.get("track") or "")
        if song: out.append(song)
        if len(out) >= RECENT_DIFFERENT_WORKS: break
    return out

def select_music(*, title: str, artist: str = "", moods: list[str] | None = None,
                 synopsis: str = "", history: list[dict] | None = None,
                 pinned_track_id: str | None = None, duration: float | None = None,
                 catalog: dict | None = None) -> dict:
    data = catalog or load_catalog()
    work_id = canon_work(title, artist)
    explicit = [m.strip().casefold() for m in (moods or []) if m.strip()]
    invalid = [m for m in explicit if m not in MOODS]
    if invalid: raise ValueError("Unknown moods " + ", ".join(invalid))
    tags = list(dict.fromkeys(explicit or infer_moods(title + " " + synopsis)))
    recent = _history_recent(history or [], work_id)
    if duration is not None and (not math.isfinite(float(duration)) or duration <= 0):
        raise ValueError("Bad video length")
    ranked = []
    for t in data["tracks"]:
        if duration and float(t["duration_seconds"]) < duration + 2.0: continue
        if pinned_track_id and t["id"] != pinned_track_id: continue
        editorial_moods = t["editorial_moods"]
        score = 0
        reasons = []
        for i, mood in enumerate(tags):
            if mood in editorial_moods:
                w = max(3, 11 - i * 2)
                score += w
                reasons.append("mood:" + mood)
            if mood in [x.casefold() for x in t.get("feel_from_source", [])]:
                score += 1
        visual_text = (title + " " + synopsis).casefold()
        for m in t.get("visual_motifs", []):
            if re.search(r"(?<!\w)" + re.escape(m.casefold()) + r"(?!\w)", visual_text):
                score += 4; reasons.append("visual:" + m)
        if not pinned_track_id and t["id"] in recent:
            score -= 28
            reasons.append("recently_used_other_painting")
        ranked.append({
            "track_id":t["id"], "title":t["title"], "composer":t["composer"],
            "isrc":t["isrc"], "source_url":t["source_url"],
            "download_url":t["download_url"], "license":t["license"],
            "license_url":t["license_url"], "source_duration_seconds":t["duration_seconds"],
            "audio_binary_preverified":bool(t.get("recording_verified")),
            "score":score, "reasons":reasons,
        })
    ranked.sort(key=lambda r: (-r["score"], r["track_id"]))
    if pinned_track_id and not ranked:
        raise ValueError("Pinned song is missing or shorter than video")
    if not ranked: raise ValueError("No suitable verified-metadata track in the 20")
    return {
        "schema":"artvision-v330-track-selection-v1",
        "work_id":work_id, "title":title, "artist":artist,
        "target_moods":tags,
        "mood_source":"editorial_tags" if explicit else ("lexical_hint_needs_review" if tags else "unknown_manual_review_required"),
        "selected":ranked[0], "alternates":ranked[1:3],
        "recent_3_other_works":recent,
        "shared_four_variants":True,
        "license_status":"TRACK_LICENSE_METADATA_DOCUMENTED_RECORDING_BINARY_NOT_YET_VERIFIED",
        "human_listening_review":"PENDING",
        "human_artistic_review":"PENDING",
        "rights_final_commercial":"PENDING_PER_TARGET",
        "published":False,
        "note":"Score is an editorial suggestion, NOT auditory similarity or final clearance. Download, decode, verify real recording and make rights attribution before video work."
    }

def credit(t: dict) -> str:
    return (f'"{t["title"]}" Kevin MacLeod (incompetech.com). '
            f'Licensed under Creative Commons: By Attribution 4.0 License '
            f'{CREDIT_LICENSE}. Music edited: excerpt, volume, fades.')

def acquire_recording(track: dict, cache: Path = FALLBACK_CACHE) -> tuple[Path, dict]:
    """Fetch official MP3 and verify actual audio. Reuse only a checksum-valid cache."""
    cache.mkdir(parents=True, exist_ok=True)
    isrc = track["isrc"]
    path = cache / (isrc + ".mp3")
    proof = cache / (isrc + "_SHA256_RIGHTS.json")
    if path.exists() and proof.exists():
        info = json.loads(proof.read_text("utf8"))
        if info.get("sha256") == sha256_file(path) and info.get("isrc") == isrc:
            meta = recording_metadata(path)
            if meta["sha256"] == info["sha256"] and \
               abs(meta["seconds"] - float(track["source_duration_seconds"])) < 24:
                return path, info
        raise ValueError("Cached recording changed: refuse unsafe reuse")
    url = track["download_url"]
    if not url.startswith(OFFICIAL_DOMAIN):
        raise ValueError("Refusing non-official music source")
    max_bytes = 85 * 1024 * 1024
    req = urllib.request.Request(url, headers={
        "User-Agent":"ArtVision-Music-V330/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; CC BY 4.0 attribution)"})
    with urllib.request.urlopen(req, timeout=100) as resp:
        b = resp.read(max_bytes + 1)
    if not (80_000 < len(b) <= max_bytes):
        raise ValueError("Recording file absent, too short, too large or download failed")
    tmp = path.with_suffix(".part.mp3")
    try:
        tmp.write_bytes(b)
        meta = recording_metadata(tmp)
        if abs(meta["seconds"] - float(track["source_duration_seconds"])) > 24:
            raise ValueError("Unexpected audio duration; possibly wrong music recording")
        if meta["channels"] not in (1, 2):
            raise ValueError("Unexpected channel layout")
        path.write_bytes(b)
        verified = {
            "track_id":track["track_id"], "isrc":isrc,
            "title":track["title"], "composer":track["composer"],
            "page":track["source_url"], "download_url":url,
            "license":"CC BY 4.0", "license_url":CREDIT_LICENSE,
            "credit":credit(track), "rights_basis":"composer_incompetech_CC_BY_4",
            "verified_on":date.today().isoformat(),
            **meta, "real_byte_readback":"PASS",
            "auditory_artistic_review":"PENDING", "commercial_distribution_video":"PENDING_FINAL"
        }
        proof.write_text(json.dumps(verified,ensure_ascii=False,indent=2)+"\n","utf8")
        return path, verified
    finally:
        tmp.unlink(missing_ok=True)

def private_remix(*, source_video: Path, out_video: Path, recording: Path,
                  track: dict, voice_wav: Path | None = None,
                  allow_replace_score: bool = True) -> dict:
    """Create an independent review copy; NEVER change a source master in place.
    Cinema: replace synthetic background with licensed track.
    Critico: requires isolated approved voice WAV; never extract/damage mixed
    voice audio. This is NOT a way to change narration timing.
    """
    source_video = source_video.resolve();out_video = out_video.resolve()
    if source_video == out_video: raise ValueError("Never overwrite the original master")
    if not source_video.is_file(): raise FileNotFoundError(source_video)
    if not recording.is_file(): raise FileNotFoundError(recording)
    if not allow_replace_score: raise ValueError("Music remaster not approved")
    dur = float(probe(source_video)["format"]["duration"])
    rec_meta = recording_metadata(recording)
    if rec_meta["seconds"] < dur + 0.4:
        raise ValueError("Chosen recording too short, avoid poor audible looping")
    source_hash = sha256_file(source_video)
    out_video.parent.mkdir(parents=True,exist_ok=True)
    end = max(0.01,dur-1.8)
    # Licensed recording mix: preserve video bitstream exactly, without image recompression.
    filters = (f"[1:a]atrim=duration={dur:.3f},asetpts=PTS-STARTPTS,"
               f"aresample=48000,loudnorm=I=-17:TP=-2:LRA=9,"
               f"afade=t=in:st=0:d=1.3,afade=t=out:st={end:.3f}:d=1.8")
    args=["ffmpeg","-hide_banner","-loglevel","error","-y",
          "-i",str(source_video),"-i",str(recording)]
    if voice_wav:
        if not voice_wav.is_file():raise FileNotFoundError(voice_wav)
        args.extend(["-i",str(voice_wav)])
        # Conservative loudness and speech sidechain. Separate voice only.
        filters += (f",volume=-17dB[bed];[2:a]aresample=48000,"
                    "loudnorm=I=-16:TP=-2:LRA=8,asplit=2[v1][v2];"
                    "[bed][v1]sidechaincompress=threshold=0.025:ratio=9:"
                    "attack=70:release=480[duck];"
                    "[duck][v2]amix=inputs=2:duration=longest:normalize=0,"
                    "alimiter=limit=0.90[mix]")
    else:
        filters += "[mix]"
    args.extend(["-filter_complex",filters,
        "-map","0:v:0","-map","[mix]","-c:v","copy",
        "-c:a","aac","-b:a","160k","-ac","2",
        "-movflags","+faststart","-t",f"{dur:.3f}",str(out_video)])
    run(args)
    # Decode both audio and video, not just inspect ffprobe tags.
    run(["ffmpeg","-hide_banner","-v","error","-xerror","-i",str(out_video),"-map","0",
         "-f","null","-"])
    if sha256_file(source_video)!=source_hash:
        raise RuntimeError("Input master changed unexpectedly")
    video_meta = probe(out_video)
    if not any(s.get("codec_type")=="video" for s in video_meta.get("streams",[])):
        raise RuntimeError("Video absent from review copy")
    if not any(s.get("codec_type")=="audio" for s in video_meta.get("streams",[])):
        raise RuntimeError("Music absent from review copy")
    report={
        "status":"PRIVATE_REVIEW_NOT_GOLD_NOT_PUBLISHED",
        "source_video":str(source_video), "source_video_sha256":source_hash,
        "review_video":str(out_video), "review_video_sha256":sha256_file(out_video),
        "recording_sha256":rec_meta["sha256"],
        "track_id":track["track_id"], "track_isrc":track["isrc"],
        "music_credit":credit(track),
        "music_type":"licensed_external_real_recording",
        "voice_preserved_separately":bool(voice_wav),
        "full_decode_video_audio":"PASS",
        "human_listening_and_rights_review":"PENDING",
        "published":False,
    }
    out_video.with_suffix(".MUSIC_REPORT_V330.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    return report

def main():
    ap=argparse.ArgumentParser(description="20-track ArtVision music director: source-locked & reuse-safe")
    ap.add_argument("--title",default="");ap.add_argument("--artist",default="")
    ap.add_argument("--moods",default="",help="comma separated mood tags, e.g. grief,melancholic")
    ap.add_argument("--synopsis",default="")
    ap.add_argument("--history",type=Path,help="array of real prior work/track selections")
    ap.add_argument("--pin",default=None,help="reuse the approved track from the same work's 4x1 variants")
    ap.add_argument("--duration",type=float,default=None)
    ap.add_argument("--prepare",action="store_true",help="download official MP3 and verify actual bytes")
    ap.add_argument("--source-video",type=Path)
    ap.add_argument("--voice-wav",type=Path)
    ap.add_argument("--review-video",type=Path)
    ap.add_argument("--out-json",type=Path)
    ap.add_argument("--cache",type=Path,default=FALLBACK_CACHE)
    ap.add_argument("--catalog-only",action="store_true")
    a=ap.parse_args()
    catalog=load_catalog()
    if a.catalog_only:
        print(json.dumps({"slots":len(catalog["tracks"]),
          "unique_isrc":len({x["isrc"] for x in catalog["tracks"]}),
          "binary_status":"verify each exact MP3 on first use"},indent=2))
        return
    if not a.title:ap.error("title required")
    hist=json.loads(a.history.read_text("utf8")) if a.history else []
    if not isinstance(hist,list):ap.error("history JSON must be an array")
    duration=a.duration
    if duration is None and a.source_video:
        duration=float(probe(a.source_video)["format"]["duration"])
    choice=select_music(title=a.title,artist=a.artist,
        moods=[m for m in a.moods.split(",") if m.strip()] or None,
        synopsis=a.synopsis,history=hist,pinned_track_id=a.pin,duration=duration,catalog=catalog)
    picked=choice["selected"]
    if a.prepare or a.review_video:
        path, proof=acquire_recording(picked,a.cache)
        choice["license_status"]="ACTUAL_BINARY_SHA256_FFPROBE_VERIFIED"
        choice["recording_proof"]=proof
        if a.review_video:
            if not a.source_video:ap.error("--review-video requires --source-video")
            choice["review"]=private_remix(source_video=a.source_video,
                out_video=a.review_video, recording=path,track=picked,
                voice_wav=a.voice_wav)
    serialized=json.dumps(choice,ensure_ascii=False,indent=2)+"\n"
    if a.out_json:
        a.out_json.parent.mkdir(parents=True,exist_ok=True)
        a.out_json.write_text(serialized,encoding="utf8")
    print(serialized)

if __name__=="__main__":
    main()
