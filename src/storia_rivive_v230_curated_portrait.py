#!/usr/bin/env python3
"""V230: review SHA-locked 9:16 reframing of genuine historical film footage.

Research-only source motion, never AI restoration, Vidu generation or FINAL.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from PIL import Image

READY = "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"
NO_PERMISSION = ("credit_spend_allowed", "publish_allowed", "italian_rights_approved")
FRAME = re.compile(r"frame_(0[1-9]|1[0-2])\.png\Z")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(config: dict, selection: dict, scout: dict, source: Path, episode: str) -> dict | None:
    if (config.get("version") != "V230_SHA_LOCKED_PORTRAIT_SOURCE_REVIEW"
            or any(config.get(key) is not False for key in NO_PERMISSION)):
        raise ValueError("V230_UNSAFE_CONFIG")
    entries = config.get("sources")
    if (not isinstance(entries, list) or any(not isinstance(x, dict) for x in entries)
            or len({x.get("episode_id") for x in entries}) != len(entries)):
        raise ValueError("V230_INVALID_SOURCE_LIST")
    matches = [x for x in entries if x.get("episode_id") == episode]
    if not matches:
        return None
    item = matches[0]
    if (selection.get("status") != READY or len(selection.get("preselected", [])) != 5
            or len(selection.get("candidate_segment_times_s", [])) != 5
            or scout.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"):
        raise ValueError("V230_SOURCE_NOT_QUALIFIED")
    expected = item.get("original_sha256")
    film = source / "ORIGINAL_ARCHIVE.webm"
    if (not isinstance(expected, str) or not re.fullmatch("[0-9a-f]{64}", expected)
            or scout.get("original_sha256") != expected or film.is_symlink()
            or not film.is_file() or digest(film) != expected):
        raise ValueError("V230_SOURCE_FILM_HASH_MISMATCH")
    rows = item.get("frames")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("V230_FIVE_SHOTS_REQUIRED")
    width, height = item.get("raster_px", (0, 0))
    cw = item.get("crop_width_px")
    if (not all(type(v) is int and v > 0 for v in (width, height, cw))
            or cw % 2 or abs(cw / height - 9 / 16) > .006):
        raise ValueError("V230_INVALID_CROP_GEOMETRY")
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError("V230_INVALID_ROW")
        name, sha, left = row.get("filename"), row.get("source_frame_sha256"), row.get("left_px")
        if (not isinstance(name, str) or not FRAME.fullmatch(name)
                or selection["preselected"][i].get("filename") != name
                or not isinstance(sha, str) or not re.fullmatch("[0-9a-f]{64}", sha)
                or type(left) is not int or left % 2 or left < 0 or left + cw > width):
            raise ValueError("V230_FRAME_OR_BOUNDS_CHANGED")
        frame = source / "original_frames" / name
        if frame.is_symlink() or not frame.is_file() or digest(frame) != sha:
            raise ValueError("V230_FRAME_SHA_CHANGED")
        with Image.open(frame) as image:
            if image.format != "PNG" or image.size != (width, height):
                raise ValueError("V230_FRAME_RASTER_CHANGED")
            image.verify()
        timecode = selection["candidate_segment_times_s"][i]
        if (isinstance(timecode, bool) or not isinstance(timecode, (int, float))
                or not 1.2 <= timecode < scout.get("duration_s", 0)):
            raise ValueError("V230_INVALID_TIMECODE")
    return item


def create(source: Path, output: Path, selection: dict, entry: dict) -> dict:
    from storia_rivive_v217_four_pilot_source_review import endpoint_alignment
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    for i, (row, t) in enumerate(zip(entry["frames"], selection["candidate_segment_times_s"]), 1):
        frame = source / "original_frames" / row["filename"]
        left, cw = row["left_px"], entry["crop_width_px"]
        height = entry["raster_px"][1]
        cropped = output / row["filename"]
        with Image.open(frame) as image:
            image.convert("RGB").crop((left, 0, left + cw, height)).save(cropped)
        clip = output / ("SOURCE_REFRAMED_%02d.mp4" % i)
        vf = f"crop={cw}:{height}:{left}:0,scale=720:1280:flags=lanczos,format=gray,format=yuv420p,fps=24"
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-v","error","-y",
                        "-ss",f"{t-1.2:.3f}","-i",str(source / "ORIGINAL_ARCHIVE.webm"),
                        "-t","1.2","-an","-vf",vf,"-c:v","libx264","-preset","veryfast",
                        "-crf","23","-movflags","+faststart",str(clip)],
                       check=True, capture_output=True, timeout=95)
        check = endpoint_alignment(clip, cropped)
        if not check["endpoint_visually_aligned"]:
            raise ValueError("V230_SOURCE_REFRAME_ENDPOINT_MISMATCH")
        checks.append({**check,"timecode_s":t,"crop_left_px":left,
                       "crop_width_px":cw,"source_original_sha256":row["source_frame_sha256"],
                       "cropped_reference_sha256":digest(cropped),"clip_sha256":digest(clip)})
    concat = output / "concat.txt"
    concat.write_text("".join("file 'SOURCE_REFRAMED_%02d.mp4'\n" % i for i in range(1,6)))
    preview = output / "PORTRAIT_SOURCE_PREVIEW_NOT_FINAL.mp4"
    subprocess.run(["ffmpeg","-nostdin","-hide_banner","-v","error","-y",
                    "-f","concat","-safe","0","-i",str(concat.resolve()),
                    "-c:v","copy","-movflags","+faststart",str(preview.resolve())],
                   check=True,capture_output=True,timeout=50,cwd=output)
    proc = subprocess.run(["ffprobe","-v","error","-show_entries",
                           "stream=codec_name,width,height:format=duration","-of","json",
                           str(preview)],check=True,capture_output=True,text=True,timeout=20)
    probe = json.loads(proc.stdout)
    video = next((s for s in probe.get("streams",[]) if s.get("codec_name") == "h264"), {})
    seconds = float(probe.get("format",{}).get("duration",0))
    if video.get("width") != 720 or video.get("height") != 1280 or not 5 <= seconds <= 7.5:
        raise ValueError("V230_REFRAMED_VIDEO_QA_FAILED")
    return {"version":"V230_SHA_LOCKED_PORTRAIT_SOURCE_REVIEW",
            "status":"SOURCE_REFRAMING_QA_PENDING","episode_id":entry["episode_id"],
            "five_true_camera_shots_approved":False,"historical_rights_italy_verified":False,
            "real_i2i_photos":0,"vidu_clips":0,"finished_mp4":False,"finished_zip":False,
            "publish_allowed":False,"five_source_reframed_clips":5,
            "source_preview_mp4":preview.name,"source_preview_duration_s":round(seconds,3),
            "checks":checks}


def main():
    parser = argparse.ArgumentParser()
    for field in ("config","selection","scout","source","out"):
        parser.add_argument("--"+field,required=True,type=Path)
    parser.add_argument("--episode",required=True)
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    selection=json.loads(args.selection.read_text())
    scout=json.loads(args.scout.read_text())
    entry=validate(config,selection,scout,args.source,args.episode)
    if entry is None:
        print("V230_NOT_CONFIGURED_RESEARCH_ONLY",args.episode)
        return
    report=create(args.source,args.out,selection,entry)
    (args.out/"PORTRAIT_SOURCE_REFRAME_V230.json").write_text(json.dumps(report,indent=2)+"\n")
    print(report["status"],"NO_I2I_NO_FINAL",args.episode)


if __name__ == "__main__":
    main()
