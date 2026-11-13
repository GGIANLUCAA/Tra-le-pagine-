#!/usr/bin/env python3
"""Second zero-paid generative photo attempt on a TRUE NEW 1910 film episode.
Use previously preserved Finegrain image, NOT a second Finegrain call; no Vidu.
No approval or public/social release on artistic fail.
"""
import cv2, numpy as np, pathlib, json, shutil, sys
from PIL import Image
from gradio_client import Client, handle_file
import storia_milk_1910_photo_owner_review as pilot
import storia_cinema_magicien_1898_visual_social_v1 as m

OUT=pilot.OUT
PREVIOUS=pathlib.Path("output/storia_milk_1910_previous")
def log(name,x):
    (OUT/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def qwen_edit():
    original=PREVIOUS/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
    assert original.is_file() and original.stat().st_size>300000,"ORIGINAL_FREE_I2I_CANDIDATE_NOT_AVAILABLE"
    img=cv2.imread(str(original))
    assert img is not None and img.shape==(720,960,3)
    prompt=("Create an exquisitely lifelike MODERN COLOR photograph by faithful image-to-image editing "
      "of the exact image supplied. This is an authentic historical 1910 film frame with a young "
      "woman standing in an open doorway, and a seated man in a broad period hat at left. "
      "The previous version has an UNNATURAL uniform orange sepia cast: REMOVE ALL SEPIA. "
      "Modern daylight color science with neutral light, cool grayish faded wood siding and "
      "weathered taupe wooden door, deep neutral brown man's jacket and hat, a muted burgundy "
      "cardigan over a natural off-white/cream period dress on the woman, subdued natural green "
      "foliage ONLY where actually present, warm lifelike human complexion without orange skin. "
      "Visible, believable skin pores, detailed eyes, authentic hair strands, crisp real-world "
      "textures and shadows like a high-end real documentary camera photograph today. "
      "The SAME two people, original face shapes and expression, location, body positions, "
      "precise number of fingers and limbs, door and all furnishings and layout MUST BE unchanged. "
      "NO third person, no invented objects, no extra teeth, no new text, no beautification. "
      "Do not transform it into a painting or cinematic illustration.")
    report={"provider":"Qwen/Qwen-Image-Edit-2509","free_public_attempt":True,
      "source_image":"original Finegrain source-locked 1910 photograph",
      "paid_calls":0,"vidu_posts":0,"approval":False,"status":"REQUEST_NOT_SENT"}
    log("QWEN_TRIAL.json",report)
    try:
        client=Client("Qwen/Qwen-Image-Edit-2509",verbose=False)
        result=client.predict([[handle_file(str(original)),None]],prompt,42,False,4.0,24,720,960,False,api_name="/infer")
        gallery=result[0] if isinstance(result,(tuple,list)) else result
        if isinstance(gallery,list): gallery=gallery[0]
        if isinstance(gallery,(tuple,list)):gallery=gallery[0]
        if isinstance(gallery,dict):
            gallery=gallery.get("image",gallery)
            if isinstance(gallery,dict):gallery=gallery.get("path",gallery.get("name"))
        new=cv2.imread(str(gallery))
        if new is None or new.size<100000:raise RuntimeError("QWEN_NO_REAL_GENERATED_IMAGE")
        new=cv2.resize(new,(960,720))
        dest=OUT/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"
        cv2.imwrite(str(dest),new)
        report.update({"status":"OUTPUT_IMAGE_RECEIVED_UNREVIEWED",
            "output_sha256":pilot.sha(dest)})
        log("QWEN_TRIAL.json",report)
        return new
    except Exception as e:
        report.update({"status":"FREE_PROVIDER_FAILED","error_type":type(e).__name__,
          "error_summary":str(e)[:220]})
        log("QWEN_TRIAL.json",report)
        raise
def photogate(pic,orig,previous):
    baseh=cv2.cvtColor(pic,cv2.COLOR_BGR2HSV)
    oh=cv2.cvtColor(previous,cv2.COLOR_BGR2HSV)
    sat=float(baseh[:,:,1].mean())
    hue=baseh[:,:,0][baseh[:,:,1]>40]
    hue_hist=np.bincount((hue//10).astype("int"),minlength=18)/max(1,hue.size)
    entropy=float(-np.sum(hue_hist*np.log2(np.maximum(1e-8,hue_hist))))
    change=float(np.mean(cv2.absdiff(pic,previous)))
    corr=m.corr(orig,pic)
    report={"source_to_generated_structure_correlation":round(corr,4),
      "saturation":round(sat,2),"color_hue_entropy":round(entropy,3),
      "pixel_delta_from_old_sepia":round(change,2),
      "old_photo_saturation":round(float(oh[:,:,1].mean()),2),
      "faces_human_review":"PENDING","real_new_photo_from_Qwen":True,
      "proceed_only_if_all_checks_pass":True}
    checks={"retains_frame_geometry":corr>=.79,
       "natural_color_saturation":20<=sat<=130,
       "multiple_photographic_hues_not_uniform_sepia":entropy>=1.4,
       "is_meaningfully_different_from_rejected_photo":change>=7}
    report["checks"]=checks
    log("V2_PHOTO_QUALITY_GATE.json",report)
    if not all(checks.values()):raise RuntimeError("V2_PHOTO_NOT_REALISTIC_ENOUGH_FOR_VIDEO")
def main():
    try:
        src,meta=pilot.download_verified_source()
        prev=json.loads((PREVIOUS/"HUMAN_FACE_SOURCE_SCOUT.json").read_text())
        (OUT/"HUMAN_FACE_SOURCE_SCOUT.json").write_text(
            (PREVIOUS/"HUMAN_FACE_SOURCE_SCOUT.json").read_text(),encoding="utf8")
        chosen=prev["top"][0]
        assert round(chosen["time_s"])==697
        m.OUT=OUT;m.SOURCE=src;m.CLIP=OUT/"REAL_SOURCE_EXCERPT_1910.mp4"
        m.MOVIE=OUT/"MILK_1910_NEW_PHOTO_REVIEW.mp4"
        m.ZIP=OUT/"MILK_1910_NEW_VIDEO_COVER_SOCIAL.zip"
        m.START=chosen["time_s"]-4.2;m.DURATION=17;m.ANCHOR=round(4.2*m.FPS)
        m.run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(m.START),"-i",str(src),
             "-t",str(m.DURATION),"-vf",f"fps={m.FPS},scale=960:720",
             "-an","-c:v","libx264","-preset","veryfast","-crf","18",
             "-pix_fmt","yuv420p",str(m.CLIP)],240)
        original=m.readframe(m.ANCHOR)
        prevpic=cv2.imread(str(PREVIOUS/"GENERATIVE_PHOTO_REAL_CANDIDATE.png"))
        assert prevpic is not None
        assert m.corr(original,prevpic)>=.98,"PREVIOUS_REAL_PHOTO_DIFFERENT_FRAME_STOP"
        pic=qwen_edit()
        photogate(pic,original,prevpic)
        model,info=m.dd.download_model()
        log("COLOR_MODEL_QA.json",info)
        canvas=m.frame_canvas
        def frame_canvas(frame,title="",small=""):
            if "LE MAGICIEN" in title:title="ALL ON ACCOUNT OF THE MILK · 1910"
            if "MÉLIÈS" in small:small="AUTHENTIC 1910 MOVING FILM"
            return canvas(frame,title,small)
        m.frame_canvas=frame_canvas
        # Qwen image visually gated; visual comparison to source still requires owner review.
        (OUT/"PHOTO_QA.json").write_text((OUT/"V2_PHOTO_QUALITY_GATE.json").read_text())
        report=m.export(pic,model)
        pilot.add_original_music_and_package(m,report,meta)
        print("NEW_1910_QWEN_COLOR_IMAGE_REAL_VIDEO_REVIEW",pilot.sha(m.MOVIE),flush=True)
    except Exception as e:
        log("V2_FAILURE.json",{"status":"NO_NEW_VIDEO_DELIVERED",
            "reason":type(e).__name__+": "+str(e)[:250],
            "paid_calls":0,"vidu_posts":0,"published":False})
        raise
if __name__=="__main__":main()
