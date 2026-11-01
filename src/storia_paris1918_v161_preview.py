#!/usr/bin/env python3
"""Render a private archival B/W five-shot preview, never a V98-equivalent master."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile
import zipfile

SOURCE_SHA1 = "aa471da773d14f422d1387654601ca03b5224455"
TIMES = (22.90, 86.80, 132.10, 208.65, 238.90)
STEM = "LA_STORIA_RIVIVE_PARIGI_1918_V161_PROVINO_BN"


def command(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def sha(path, name="sha256"):
    h = hashlib.new(name)
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_name,codec_type,width,height",
        "-of", "json", str(path)], text=True))


def render(source, output, times=TIMES, expected_sha1=SOURCE_SHA1):
    source, output = pathlib.Path(source), pathlib.Path(output)
    if not source.is_file() or sha(source, "sha1") != expected_sha1:
        raise ValueError("SOURCE_SHA1_MISMATCH")
    meta = probe(source)
    duration = float(meta["format"]["duration"])
    if len(times) != 5 or len(set(times)) != 5 or any(t < 0 or t + 3.35 > duration for t in times):
        raise ValueError("INVALID_SHOT_TIMECODES")
    if not any(s.get("codec_type") == "video" for s in meta["streams"]):
        raise ValueError("NO_ARCHIVAL_VIDEO")
    output.mkdir(parents=True, exist_ok=True)
    # Keep authentic 4:3 picture visible; blurred margins only fill the vertical frame.
    vf = ("split=2[bg][fg];[bg]scale=720:1280:force_original_aspect_ratio=increase,"
          "setsar=1,crop=720:1280,boxblur=12:1[blur];"
          "[fg]scale=720:540,setsar=1[sharp];"
          "[blur][sharp]overlay=(W-w)/2:(H-h)/2,format=yuv420p,fps=30")
    with tempfile.TemporaryDirectory() as scratch:
        scratch = pathlib.Path(scratch)
        clips = []
        for index, timestamp in enumerate(times):
            motion = scratch / f"motion{index}.mp4"
            length = 3.35 if index == 4 else 1.40
            command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", str(timestamp), "-i", str(source), "-t", str(length),
                    "-filter_complex", vf, "-an", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "24", "-r", "30", str(motion))
            if float(probe(motion)["format"]["duration"]) < length - .10:
                raise RuntimeError("ARCHIVAL_MOTION_TOO_SHORT")
            clips.append(motion)
            if index < 4:
                frame = scratch / f"freeze{index}.png"
                # Frame 41 is the LAST decoded frame of the 42-frame encoded segment.
                command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(motion), "-vf", r"select=eq(n\,41)",
                        "-vsync", "0", "-frames:v", "1", str(frame))
                if not frame.is_file():
                    raise RuntimeError("FREEZE_NOT_EXACT")
                hold = scratch / f"hold{index}.mp4"
                command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-loop", "1", "-framerate", "30", "-i", str(frame),
                        "-t", "1.95", "-an", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "24", "-pix_fmt", "yuv420p", "-r", "30", str(hold))
                clips.append(hold)
        listing = scratch / "clips.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in clips), encoding="utf-8")
        joined = scratch / "joined.mp4"
        command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(listing),
                "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-pix_fmt", "yuv420p", "-r", "30", str(joined))
        # Original synthetic ambient audio, not a copyrighted music track.
        seconds = float(probe(joined)["format"]["duration"])
        video = output / (STEM + ".mp4")
        tone = ("0.14*sin(2*PI*130.81*t)+0.08*sin(2*PI*196*t)"
                "+0.04*sin(2*PI*261.63*t)")
        command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(joined), "-f", "lavfi", "-i",
                f"aevalsrc={tone}:s=24000:d={seconds}",
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "96k", "-shortest",
                "-movflags", "+faststart", str(video))
        command("ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-f", "null", "-")
        final = probe(video)
        assert 14 <= float(final["format"]["duration"]) <= 35
        assert any(s.get("codec_name") == "h264" and s.get("width") == 720
                   and s.get("height") == 1280 for s in final["streams"])
        assert any(s.get("codec_name") == "aac" for s in final["streams"])
        cover = output / (STEM + "_COVER.jpg")
        command("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", "0.6", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(cover))
    posts = output / "POST_SOCIAL_4.txt"
    posts.write_text(
        "Instagram: PARIGI · 1918. Cinque riprese autentiche, provino B/N. #Storia\n\n"
        "TikTok: Parigi 1918: cinque sguardi dalla pellicola originale. #Archivio\n\n"
        "Facebook: Cinque scene d'archivio del 1918. Anteprima tecnica, non restauro AI.\n\n"
        "YouTube Shorts: Paris 1918 — original archival motion, B/W preview; no I2I or Vidu.\n",
        encoding="utf-8")
    qa = {"status": "RENDERED_NEEDS_REVIEW", "source_sha1": expected_sha1,
          "timecodes_s": list(times), "video_sha256": sha(video),
          "video_bytes": video.stat().st_size,
          "duration_s": float(final["format"]["duration"]),
          "h264_aac_full_decode_pass": True, "five_distinct_shots_visually_approved": False,
          "four_real_i2i": False, "one_real_vidu": False, "v98_technical_pass": False,
          "italian_rights_approved": False, "artistic_qa_approved": False,
          "publish_permitted": False, "credits_spent": 0,
          "note": "Original B/W motion and grayscale freeze only, not restored photographs."}
    report = output / "QA_V161.json"
    report.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    kit = output / (STEM + "_ANDROID_KIT.zip")
    with zipfile.ZipFile(kit, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in (video, cover, posts, report):
            archive.write(path, path.name)
    with zipfile.ZipFile(kit) as archive:
        assert archive.testzip() is None
        assert {video.name, cover.name, posts.name, report.name} <= set(archive.namelist())
    return qa


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.source, args.out), ensure_ascii=False, indent=2))
