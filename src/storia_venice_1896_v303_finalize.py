#!/usr/bin/env python3
"""V303: finalize REAL Venice 1896 four-photo reel from V302 verified original frames.
NO generation, NO credits, NO fake Vidu, NO social/site publication.
"""
from __future__ import annotations
import json,hashlib,subprocess,zipfile,shutil
from pathlib import Path
import storia_v80_new_york_venice as v80
import storia_rivive_v295_photo_identity_gate as gate

OUT=v80.OUT/"VENICE_1896"
META=dict(v80.FILMS["VENICE_1896"])
META["shots"]=[
    {"t":6.3,"center":632,"length":1.65,"tag":"Gondolier, old palaces and authentic canal motion"},
    {"t":14.1,"center":678,"length":1.65,"tag":"Gondolas beneath Venice 1896 stone facades"},
    {"t":32.6,"center":670,"length":1.65,"tag":"Venetian historic waterfront and architecture"},
    {"t":44.3,"center":725,"length":1.65,"tag":"Canal reflections and authentic Venice late 19th century"},
]
def filehash(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    state={"version":"V303_REUSE_FOUR_SOURCE_LOCKED_I2I","format":"storia_rivive",
       "status":"PREPARED","subject":"VENICE · 1896 · alternate four moving scenes",
       "paid_provider_calls":0,"new_Vidu_clip":False,"artistic_approval":False,
       "final_video_approved":False,"site_published":False,"social_published":False,
       "territorial_rights_italy_verified":False}
    try:
        trial=json.loads((OUT/"V302_PHOTO_TRIAL.json").read_text())
        entries=trial["photos"]
        indexed={x["scene"]:x for x in entries}
        if set(indexed)!={1,2,3,4}:
            raise RuntimeError("FOUR_PROVEN_PHOTOS_REQUIRED")
        archive,info=v80.acquire(META,OUT)
        frames=v80.grab_stills(archive,META,OUT)
        photos=[]
        for f in frames:
            n=f["scene"];r=indexed[n]
            file=OUT/f"V302_TRUE_I2I_PHOTO_{n:02d}.png"
            if not file.is_file():raise RuntimeError("PHOTO_MISSING_"+str(n))
            if f["sha256"]!=r["source_sha256"] or filehash(file)!=r["photo_sha256"]:
                raise RuntimeError("PHOTO_OR_MOVING_SOURCE_CHANGED_"+str(n))
            qa=gate.evaluate(OUT/f["source_frame"],file)
            if not qa["ready_for_artistic_review"] or qa["metrics"]["structure_correlation"]<.85:
                raise RuntimeError("PHOTO_COLOR_OR_GEOMETRY_REJECTED_"+str(n))
            if r["status"] not in ("PREVIOUS_SOURCE_LOCKED_REAL_I2I_REUSED_VERIFIED",
                                    "GENUINE_I2I_TECHNICAL_QA_PASS_ARTISTIC_REVIEW_PENDING"):
                raise RuntimeError("PHOTO_NOT_PREVIOUSLY_VERIFIED_"+str(n))
            item={**f,"photo_file":file.name,"photo_sha256":filehash(file),
                    "geom_corr":round(qa["metrics"]["structure_correlation"],4),
                    "sat":round(qa["metrics"]["mean_saturation_0_255"],2),
                    "model":"Finegrain Free real color-guided image-to-image",
                    "new_detail_generation":True,"historical_hues_accurate":"NOT_KNOWN",
                    "source_locked_semantic_review":"PENDING_FULL_ARTISTIC"}
            photos.append(item)
        (OUT/"PHOTO_QA.json").write_text(json.dumps(photos,indent=2,ensure_ascii=False)+"\n")
        print("V303_FOUR_PHOTOS_ACTUAL_SHA_VERIFIED",flush=True)
        v80.render(META,archive,photos,OUT,info)
        internal=OUT/"LA_STORIA_RIVIVE_VENICE_1896_V80.mp4"
        dest=OUT/"VENICE_1896_V303_FOUR_TRUE_I2I_NO_VIDU_REVIEW.mp4"
        shutil.copyfile(internal,dest)
        subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(dest),"-f","null","-"],
                        check=True,timeout=150)
        raw=subprocess.check_output(["ffprobe","-v","error","-show_entries",
                                    "format=duration,size:stream=codec_name,width,height",
                                    "-of","json",str(dest)],text=True)
        probe=json.loads(raw)
        codecs={x["codec_name"] for x in probe["streams"]}
        assert {"h264","aac"}<=codecs and 19<=float(probe["format"]["duration"])<=35
        state.update({"status":"REAL_MP4_FOUR_PHOTOS_CREATED_NO_VIDU_NOT_FINAL",
            "new_real_video_file_created":True,"reused_old_photo_count":2,
            "new_V302_photo_count":2,"source_sha256":filehash(archive),
            "mp4":dest.name,"mp4_sha256":filehash(dest),
            "mp4_bytes":dest.stat().st_size,"ffprobe":probe,
            "source_b_w_to_real_I2I_freeze_scenes":4,
            "V94_full_master_gate":False})
        (OUT/"V303_DELIVERY_QA.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
        kit=OUT/"VENICE_1896_V303_FOUR_REAL_PHOTOS_VIDEO_COVER_QA.zip"
        files=[dest,OUT/"COVER.jpg",OUT/"BEFORE_AFTER_ACTUAL_GENERATED.jpg",
               OUT/"V303_DELIVERY_QA.json",OUT/"PHOTO_QA.json",
               OUT/"SOURCE_QA.json",OUT/"REAL_FILM_SCENES.jpg",
               *sorted(OUT.glob("POST_*.txt"))]
        with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for p in files:
                if not p.is_file():raise RuntimeError("PACKAGE_FILE_MISSING_"+p.name)
                z.write(p,p.name)
        with zipfile.ZipFile(kit) as z:
            if z.testzip() is not None: raise RuntimeError("ZIP_CRC_ERROR")
        state.update({"package":kit.name,"package_sha256":filehash(kit),
                      "package_bytes":kit.stat().st_size})
        print("V303_ACTUAL_RESTORED_MP4",dest.name,"SECS",probe["format"]["duration"],
              "BYTES",dest.stat().st_size,"REAL_VIDU",False,"FINAL_APPROVED",False,flush=True)
    except Exception as e:
        state.update({"status":"V303_REAL_RENDER_OR_PACKAGE_BLOCKED",
                      "exception_type":type(e).__name__,"error":str(e)[:400]})
        print("V303_FAILED",type(e).__name__,str(e)[:300],flush=True)
    finally:
        (OUT/"V303_DELIVERY_QA.json").write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n")

if __name__=="__main__":main()
