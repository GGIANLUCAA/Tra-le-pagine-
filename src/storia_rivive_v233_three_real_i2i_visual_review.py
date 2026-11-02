#!/usr/bin/env python3
"""V233: make a REAL 28.5s review from 3 source-locked I2I, never a final 4+1."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path
from PIL import Image
SCENE,LEAD,HOLD,OUTRO=5.2,2.4,.2,2.5
PHOTO=SCENE-LEAD-HOLD
DURATION=5*SCENE+OUTRO

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for part in iter(lambda:f.read(1048576),b""):h.update(part)
    return h.hexdigest()

def cmd(args,timeout=180):
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if p.returncode:raise RuntimeError("FFMPEG_FAILED: "+p.stderr[-900:])
    return p.stdout

def verify(video,report,lock,results,root):
    if sha(video)!=report.get("video_sha256"):raise ValueError("V231_SOURCE_VIDEO_SHA_CHANGED")
    if report.get("film_sha256")!=lock.get("film_sha256"):raise ValueError("FILM_SHA_MISMATCH")
    if len(report.get("source_starts_s",[]))!=5 or len(lock.get("frames",[]))!=4:
        raise ValueError("SOURCE_SCENE_LAYOUT_INVALID")
    if report.get("episode_id")!=lock.get("episode_id") or lock.get("episode_id")!=results.get("episode_id"):
        raise ValueError("EPISODE_ID_MISMATCH")
    if (results.get("real_i2i_candidates")!=3 or results.get("target_photos")!=4
        or results.get("vidu_clips")!=0 or results.get("final_4_plus_1_mp4") is not False
        or lock.get("italian_rights_approved") is not False):
        raise ValueError("UNSAFE_REVIEW_STATE")
    outcomes={r["frame"]:r for r in results["outcomes"]}
    good={}
    for i,row in enumerate(lock["frames"]):
        name=row["frame"]
        if name!=f"frame_{i+8:02d}.png" or row["job_index"]!=i:
            raise ValueError("FRAME_SEQUENCE_CHANGED")
        if abs(float(row["source_timecode_s"])-float(report["source_starts_s"][i])-2.55)>.02:
            raise ValueError("SOURCE_TIMECODE_ALIGNMENT_FAILED")
        crop=root/"FOUR_SOURCE_LOCKED_INPUTS"/name
        if sha(crop)!=row["crop_sha256"]:raise ValueError("SOURCE_CROP_SHA_CHANGED")
        outcome=outcomes.get(name,{})
        if outcome.get("status")!="REAL_I2I_CANDIDATE_PENDING_ARTISTIC_QA":continue
        photo=root/"I2I_CANDIDATES"/name[:-4]/"FOTO_RICOSTRUITA_V77_DA_VERIFICARE.png"
        if not photo.is_file() or sha(photo)!=outcome["photo_sha256"]:
            raise ValueError("I2I_PHOTO_SHA_CHANGED")
        if outcome["source_crop_sha256"]!=row["crop_sha256"]:
            raise ValueError("I2I_NOT_SOURCE_LOCKED")
        with Image.open(photo) as im:
            if im.width<300 or im.height<600:raise ValueError("I2I_TOO_SMALL")
        good[i]=(crop,photo,name)
    if sorted(good)!=[1,2,3]:raise ValueError("EXPECTED_EXACTLY_THREE_REAL_I2I")
    return good

def render(video,report,lock,results,root,out):
    good=verify(video,report,lock,results,root)
    out.mkdir(parents=True,exist_ok=True)
    clips=[]
    def encode(args,path):
        cmd(["ffmpeg","-nostdin","-hide_banner","-v","error","-y",*args,
             "-an","-c:v","libx264","-preset","veryfast","-crf","21",
             "-r","30","-pix_fmt","yuv420p",str(path)],120)
        clips.append(path)
    for i in range(5):
        start=round(i*SCENE,3)
        if i in good:
            crop,photo,_=good[i]
            encode(["-ss",str(start),"-i",str(video),"-t",str(LEAD)],out/f"scene_{i+1}_bw.mp4")
            encode(["-loop","1","-framerate","30","-i",str(crop),"-t",str(HOLD),
                    "-vf","scale=720:1280:flags=lanczos"],out/f"scene_{i+1}_authentic_frame.mp4")
            encode(["-loop","1","-framerate","30","-i",str(photo),"-t",str(PHOTO),
                    "-vf","scale=720:1280:flags=lanczos"],out/f"scene_{i+1}_real_i2i.mp4")
        else:
            encode(["-ss",str(start),"-i",str(video),"-t",str(SCENE)],out/f"scene_{i+1}_bw_only.mp4")
    encode(["-ss",str(5*SCENE),"-i",str(video),"-t",str(OUTRO)],out/"closing_title.mp4")
    listing=out/"CONCAT.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in clips))
    result=out/"V233_THREE_REAL_I2I_28S_REVIEW_NOT_FINAL.mp4"
    cmd(["ffmpeg","-nostdin","-hide_banner","-v","error","-y","-f","concat","-safe","0",
         "-i",str(listing),"-i",str(video),"-map","0:v:0","-map","1:a:0",
         "-vf","drawtext=text='I2I TEST - NON FINALE':fontcolor=white@0.8:fontsize=22:x=(w-text_w)/2:y=h-50:box=1:boxcolor=black@0.45:boxborderw=8",
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","160k","-t",str(DURATION),"-movflags","+faststart",str(result)],180)
    probe=json.loads(cmd(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(result)],30))
    duration=float(probe["format"]["duration"])
    v=[s for s in probe["streams"] if s.get("codec_type")=="video"]
    a=[s for s in probe["streams"] if s.get("codec_type")=="audio"]
    if not 28.3<=duration<=28.7 or not v or not a or (v[0]["width"],v[0]["height"])!=(720,1280):
        raise ValueError("OUTPUT_MEDIA_OR_DURATION_INVALID")
    cmd(["ffmpeg","-nostdin","-hide_banner","-v","error","-xerror","-i",str(result),"-f","null","-"],180)
    qa={"version":"V233_THREE_REAL_I2I_VISUAL_REVIEW","duration_s":duration,
        "video_sha256":sha(result),"original_film_sha256":lock["film_sha256"],
        "real_source_locked_i2i_candidates_used":3,"required_i2i":4,
        "source_frames_used":[good[i][2] for i in sorted(good)],
        "black_and_white_only_frames":["frame_08.png","frame_12.png"],
        "real_vidu_clips":0,"required_vidu_clips":1,
        "freeze_exact_motion_frame_certified":False,
        "technical_mp4_decoded":True,"italian_rights_verified":False,
        "human_artistic_approval":False,"quality_v98_passed":False,
        "v91_v94_v96_v99_final_qa_passed":False,"publish_allowed":False,
        "final_episode":False,"new_final_episodes_delivered":0,
        "warning":"3 weak I2I, fourth photo and Vidu missing; rights pending. Never publish."}
    report_path=out/"V233_QA_NOT_FINAL.json"
    report_path.write_text(json.dumps(qa,indent=2)+"\n")
    with zipfile.ZipFile(out/"V233_ANDROID_VISUAL_REVIEW_ONLY.zip","w",zipfile.ZIP_DEFLATED) as z:
        z.write(result,result.name);z.write(report_path,report_path.name)
    print("V233_3_REAL_I2I_SOURCE_LOCKED_REVIEW_ONLY",duration,sha(result))
    return qa

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for name in ("source-mp4","source-report","lock","results","i2i-root","out"):
        ap.add_argument("--"+name,type=Path,required=True)
    x=ap.parse_args()
    render(x.source_mp4,json.loads(x.source_report.read_text()),
           json.loads(x.lock.read_text()),json.loads(x.results.read_text()),x.i2i_root,x.out)
