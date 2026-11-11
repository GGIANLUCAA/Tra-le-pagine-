#!/usr/bin/env python3
"""V191: verified REAL I2I source bundle and scene-specific photoreal direction.

Inputs: V190 verified exact-frame ZIP + V189 true moving film artifact ZIP.
Creates a reproducible production handoff with real original frame/clip BYTES.
Does NOT generate photographs or call providers. Never equate 4K export with
native 4K detail, mark spend/review/territorial rights as not verified.
"""
import argparse
import hashlib
import json
import re
import stat
import subprocess
import zipfile
from pathlib import Path

FILM_SHA = "eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9"
PROMPTS = {
    1: "Restore this EXACT 1909 silent-film still as a crisp natural-color historical photograph. An early-twentieth-century businessman in a dark three-piece suit gestures by an office desk with dark wood paneling. Preserve his real head outline, expression, hairline, hand position, pose, lamp and every visible object. Gentle realistic window and practical light, fine textile and skin texture only where source detail supports it.",
    2: "Photorealistic natural-color I2I restoration of the EXACT motion-picture frame: a densely packed early-1900s indoor stock-exchange crowd, men wearing hats and suits, raised arms and animated gestures. Keep all visible bodies, faces, limbs, hats and background architecture in precisely their original places; believable neutral color, not sepia or orange. Do not add or erase people.",
    3: "Convert the EXACT 1909 banquet scene to a credible, beautifully detailed natural-color photograph, preserving the original number, poses and expressions of guests, tablecloth, glassware, flower centerpiece and formal clothing, and the precise deep room geometry. Authentic period materials and subtle lighting. No invented food, people, cutlery or changes to facial identity.",
    4: "Reconstruct this EXACT original 1909 film frame as a clean natural-color photograph of people in rural work clothes standing together outdoors, including a hat-wearing man and the other original figures. Preserve every real figure's position, hands, papers or small objects actually visible, terrain, shadows, framing and camera perspective. Natural skin and fabric tones without idealized replacement faces.",
}
COMMON_NEGATIVE = ("no changed identity; no fabricated eye details; no extra or missing fingers, hands, hats, people, "
                   "teeth, animals, buildings or objects; no plastic skin, CGI, painting, fantasy, sepia, orange "
                   "tint, low contrast, distortion, over-sharpening, text generation, logos or watermark")
VIDU_PROMPT = ("Continue animating the EXACT SAME man in a dark suit and bowler hat standing at a wooden "
               "granary doorway in the historical frame. He makes a single natural emphatic arm gesture, "
               "with his actual body, face, hat, door, panels and camera view continuously matching the "
               "original 1909 film frame. First second: B/W gradually becomes plausible natural color "
               "while true motion continues. Then at least four seconds of genuine photorealistic movement, "
               "no cuts, camera zoom, photo parallax, identity changes or extra objects.")
# Durations are design targets, NOT measured output of a final film.
SCENE_TIMING = (
    {"scene": 1, "bw": 1.35, "freeze": .18, "reveal": .32, "color_hold": 2.05},
    {"scene": 2, "bw": 1.40, "freeze": .18, "reveal": .32, "color_hold": 2.25},
    {"scene": 3, "bw": 1.25, "freeze": .20, "reveal": .35, "color_hold": 2.15},
    {"scene": 4, "bw": 1.45, "freeze": .20, "reveal": .35, "color_hold": 2.25},
    {"scene": 5, "bw": 1.30, "vidu_moving_color": 5.00},
)
FRAME_NAME = re.compile(r"\d{2}_[a-z0-9-]+_last_real_film_frame\.png\Z")
CLIP_NAME = re.compile(r"\d{2}_[a-z0-9-]+_real_film_bw\.mp4\Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_archive(archive, max_bytes=45*1024*1024):
    z = zipfile.ZipFile(archive)
    entries = z.infolist()
    if len(entries) > 25 or sum(f.file_size for f in entries) > max_bytes:
        raise ValueError("UNSAFE_OR_OVERSIZED_INPUT_ARCHIVE")
    names = [f.filename for f in entries]
    if len(names) != len(set(names)):
        raise ValueError("DUPLICATE_ARCHIVE_NAME")
    for f in entries:
        if (f.is_dir() or "/" in f.filename or "\\" in f.filename or
                ".." in f.filename or f.filename.startswith(".") or
                stat.S_IFMT(f.external_attr >> 16) == stat.S_IFLNK):
            raise ValueError("UNSAFE_ARCHIVE_MEMBER")
    return z


def probe_png(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                             "-show_entries", "stream=codec_name,width,height", "-of", "json",
                             str(path)], check=True, capture_output=True, text=True, timeout=45)
    streams = json.loads(result.stdout).get("streams", [])
    if len(streams) != 1 or streams[0]["codec_name"] != "png":
        raise ValueError("INVALID_SOURCE_PNG")
    if [streams[0]["width"], streams[0]["height"]] != [720,1280]:
        raise ValueError("SOURCE_PNG_RASTER_MISMATCH")
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(path),
                    "-f","null","-"],check=True,capture_output=True,timeout=45)


def make_plan(anchors, motion):
    if (anchors.get("version") != "V190_EXACT_FRAME_I2I_VIDU_HANDOFF" or
            anchors.get("status") != "FIVE_REAL_SOURCE_FRAMES_VERIFIED_PROVIDER_BLOCKED" or
            anchors.get("film_sha256") != FILM_SHA or
            motion.get("version") != "V189" or
            motion.get("status") != "REAL_BW_MOTION_PROOF_REVIEW_ONLY" or
            motion.get("source_sha256") != FILM_SHA):
        raise ValueError("SOURCE_HANDOFF_INVALID")
    source_frames = anchors.get("source_frames", [])
    if len(source_frames) != 5 or [x["scene"] for x in source_frames] != [1,2,3,4,5]:
        raise ValueError("FIVE_EXACT_SOURCE_FRAMES_REQUIRED")
    if (anchors.get("photos_generated") != 0 or anchors.get("vidu_clips_generated") != 0 or
            anchors.get("provider_requests_sent") != 0 or
            anchors.get("publication_permitted") is not False or
            anchors.get("rights_italy_verified") is not False or
            motion.get("provider_jobs_may_start") is not False):
        raise ValueError("UNTRUSTED_STATUS_FLAGS")
    if len({x["exact_freeze_sha256"] for x in source_frames}) != 5:
        raise ValueError("DUPLICATED_SOURCE_ANCHOR")
    for i, (anchor, original) in enumerate(zip(source_frames, motion["scenes"]), 1):
        if (anchor["scene"] != original["index"] or
            anchor["exact_freeze_sha256"] != original["exact_last_decoded_frame_sha256"] or
            anchor["real_motion_sha256"] != original["motion_mp4_sha256"] or
            anchor.get("last_decoded_frame_pixel_identical_to_freeze") is not True or
            anchor.get("source_lock_verified") is not True or
            anchor["source_crop_native_px"] != [603,1072] or
            anchor["encoded_raster_px"] != [720,1280]):
            raise ValueError("SOURCE_ANCHOR_MISMATCH_" + str(i))
    entries = []
    running = 0.
    for t in SCENE_TIMING:
        dur = round(sum(v for k,v in t.items() if k!="scene"),2)
        entries.append({"scene":t["scene"],"starts_at_s":round(running,2),
                        "ends_at_s":round(running+dur,2),"seconds":dur,**t})
        running = round(running+dur,2)
    if not 20 <= running <= 26:
        raise ValueError("STORYBOARD_DURATION_INVALID")
    return {
      "version":"V191_TRUE_PHOTOGRAPHIC_I2I_PREPARATION",
      "status":"SOURCE_PACK_READY_REAL_GENERATION_NOT_STARTED",
      "film_title":"A Corner in Wheat (1909) — dramatized historical silent film",
      "film_source_sha256":FILM_SHA,
      "source_raster_effective_unscaled_pixels":[603,1072],
      "source_encoded_pixels":[720,1280],
      "delivery_4k_target_pixels":[2160,3840],
      "4k_is_only_target_not_original_or_achieved":True,
      "target_film_duration_s":running,
      "scene_timing":entries,
      "photo_i2i_jobs":[
        {"scene":a["scene"],"source_file":a["exact_freeze_file"],
         "source_sha256":a["exact_freeze_sha256"],
         "scene_description":PROMPTS[a["scene"]],
         "negative_prompt":COMMON_NEGATIVE,
         "requirements":{"method":"real_guided_generative_image_to_image",
                         "ddcolor_only_forbidden":True,
                         "geometry_and_identity_must_be_visually_verified":True,
                         "native_4k_detail_not_inferred":True},
         "status":"NOT_SUBMITTED",
         "provider":None,"output_photo":None,"output_sha256":None,
         "artistically_approved":False}
         for a in source_frames[:4]],
      "vidu_job":{"scene":5,"source_file":source_frames[4]["exact_freeze_file"],
         "source_sha256":source_frames[4]["exact_freeze_sha256"],
         "motion_source":source_frames[4]["real_motion_file"],
         "prompt":VIDU_PROMPT,
         "status":"NOT_SUBMITTED","free_balance_check_only":True,
         "plan_code":None,"scene_authorization":False,
         "approved_max_credits":None},
      "source_provenance":[{"scene":a["scene"],"original_frame_sha256":a["exact_freeze_sha256"],
                            "original_film_clip_sha256":a["real_motion_sha256"],
                            "source_shot":a["source_shot_png"],
                            "crop_upscaled_in_encoder":True} for a in source_frames],
      "i2i_generated":0,"vidu_generated":0,"provider_calls":0,"credits_spent":0,
      "final_mp4_created":False,"rights_italy_verified":False,
      "artistic_quality_v98_approved":False,"publish_permitted":False,
      "blocked_until":["FOUR_GENUINE_I2I_IMAGES_REVIEWED",
          "VIDU_SCENE_BUDGET_APPROVED_AND_BALANCE_VERIFIED",
          "ITALIAN_TERRITORIAL_RIGHTS_VERIFIED",
          "V91_V94_V96_V99_ON_REAL_FINAL_MP4_PASS"],
    }


def run(v190_zip, v189_zip, output_dir):
    output = Path(output_dir)
    if output.exists() or any(p.is_symlink() for p in output.parents):
        raise ValueError("OUTPUT_EXISTS_OR_SYMLINK")
    with read_archive(v190_zip) as z190, read_archive(v189_zip) as z189:
        anchors = json.loads(z190.read("V190_I2I_VIDU_SOURCE_HANDOFF.json"))
        motion = json.loads(z189.read("V189_REAL_MOTION_PROOF_REPORT.json"))
        plan = make_plan(anchors,motion)
        output.mkdir(parents=True)
        for anchor in anchors["source_frames"]:
            filename = anchor["exact_freeze_file"]
            if not FRAME_NAME.fullmatch(filename):
                raise ValueError("UNSAFE_ANCHOR_NAME")
            raw=z190.read(filename)
            if digest(raw)!=anchor["exact_freeze_sha256"] or digest(raw)!=motion["scenes"][anchor["scene"]-1]["exact_last_decoded_frame_sha256"]:
                raise ValueError("FREEZE_BYTES_NOT_AUTHENTIC")
            output.joinpath(filename).write_bytes(raw)
            probe_png(output/filename)
            clip_name=anchor["real_motion_file"]
            if not CLIP_NAME.fullmatch(clip_name):
                raise ValueError("UNSAFE_CLIP_NAME")
            clip=z189.read(clip_name)
            if digest(clip)!=anchor["real_motion_sha256"]:
                raise ValueError("ORIGINAL_MOVING_FILM_SHA_CHANGED")
            output.joinpath(clip_name).write_bytes(clip)
        (output/"V191_PRODUCTION_HANDOFF.json").write_text(
          json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return plan


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v190-artifact",required=True)
    p.add_argument("--v189-artifact",required=True)
    p.add_argument("--out-dir",required=True)
    args=p.parse_args()
    plan=run(args.v190_artifact,args.v189_artifact,args.out_dir)
    print(json.dumps({"status":plan["status"],"scene_count":5,
       "source_sha_locked":True,"target_s":plan["target_film_duration_s"],
       "real_photos":plan["i2i_generated"],"vidu":plan["vidu_generated"],
       "credits":0,"master":False}))

if __name__=="__main__":
    main()
