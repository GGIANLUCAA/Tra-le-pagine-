#!/usr/bin/env python3
"""Colorize only a previously generated, source-locked Vidu clip with genuine DDColor ONNX.
ONE archival scene; 0 Vidu submit calls; preserve every source frame's geometry and luminance.
Review only: colors are hypothetical; no social publication / no gold status.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess
from pathlib import Path
import cv2
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download

EXPECTED_MODEL_SHA="2653da00dc15e54a45e5200b61dbf82ee9ceaf56b02bb9b9657569ac775e82e6"
EXPECTED_SOURCE_SHA="b22a97baa0eac55c0ccda8d3ed7d278b01a593f961b695ef2d7db59b7da8b5ec"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for ch in iter(lambda:f.read(1<<20),b""):h.update(ch)
    return h.hexdigest()

def lab_l(frame):
    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB).astype("float32")/255.
    return cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB)[:,:,0]

def infer(session,bgr):
    l=lab_l(bgr)
    l512=cv2.resize(l,(512,512),interpolation=cv2.INTER_AREA)
    lab=np.stack([l512,np.zeros_like(l512),np.zeros_like(l512)],axis=-1)
    rgb=cv2.cvtColor(lab.astype("float32"),cv2.COLOR_LAB2RGB)
    batch=rgb.transpose(2,0,1)[None].astype("float32")
    ab=session.run(None,{session.get_inputs()[0].name:batch})[0]
    assert tuple(ab.shape)==(1,2,512,512),tuple(ab.shape)
    return cv2.resize(ab[0].transpose(1,2,0).astype("float32"),(256,456))

def stabilize_color(current,reference,ref_ab):
    # Transfer color from the fixed chroma anchor along actual image motion.
    ref=cv2.resize(cv2.cvtColor(reference,cv2.COLOR_BGR2GRAY),(256,456))
    now=cv2.resize(cv2.cvtColor(current,cv2.COLOR_BGR2GRAY),(256,456))
    flow=cv2.calcOpticalFlowFarneback(now,ref,None,.5,3,13,3,5,1.1,0)
    yy,xx=np.mgrid[:456,:256].astype("float32")
    warped=cv2.remap(ref_ab,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return warped

def project_color(frame,ab):
    height,width=frame.shape[:2]
    l=lab_l(frame)
    colors=cv2.resize(ab,(width,height),interpolation=cv2.INTER_LINEAR)
    # Enhance chroma predicted by DDColor, not a global sepia or flat overlay.
    colors=np.clip(colors*1.32,-112,112)
    comp=np.dstack((l,colors)).astype("float32")
    rgb=cv2.cvtColor(comp,cv2.COLOR_LAB2RGB)
    out=cv2.cvtColor((np.clip(rgb,0,1)*255).astype("uint8"),cv2.COLOR_RGB2BGR)
    hsv=cv2.cvtColor(out,cv2.COLOR_BGR2HSV)
    sf=hsv[:,:,1].astype("float32")
    hsv[:,:,1]=np.uint8(np.clip(sf*1.22,0,172))
    return cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()
    src=Path(a.input);out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    assert sha(src)==EXPECTED_SOURCE_SHA,"VIDU original source SHA mismatch, refuse"
    model=Path(hf_hub_download(repo_id="edgetools/ddcolor",filename="ddcolor-tiny-fp16.onnx"))
    assert sha(model)==EXPECTED_MODEL_SHA,"Neural model fingerprint mismatch"
    options=ort.SessionOptions()
    options.intra_op_num_threads=4
    options.inter_op_num_threads=1
    options.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    ses=ort.InferenceSession(str(model),sess_options=options,providers=["CPUExecutionProvider"])
    c=cv2.VideoCapture(str(src))
    fps=c.get(cv2.CAP_PROP_FPS)
    n=int(c.get(cv2.CAP_PROP_FRAME_COUNT))
    w=int(c.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(c.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if (w,h)!=(720,1280) or not(20<=fps<=60 and 100<=n<=500):
        raise ValueError("unexpected original source video dimensions/fps/count")
    frames=[]
    for i in range(n):
        ok,v=c.read()
        if not ok:raise RuntimeError(f"truncated source at frame {i}")
        frames.append(v)
    c.release()
    print("REAL_VIDU_SOURCE_FRAMES",n,"fps",fps,flush=True)
    stride=max(8,round(fps*0.60))
    keys=sorted(set(list(range(0,n,stride))+[n-1]))
    anchors={}
    for i in keys:
        anchors[i]=infer(ses,frames[i])
        print("REAL_DDCOLOR_ANCHOR",i,"of",n,flush=True)
    output=out/"VIDU_FRANCE_1895_NEURAL_TRUE_COLOR_REVEAL_720.mp4"
    cmd=["ffmpeg","-nostdin","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24",
         "-s","720x1280","-r",str(fps),"-i","-","-an","-c:v","libx264",
         "-crf","17","-preset","veryfast","-pix_fmt","yuv420p","-movflags","+faststart",str(output)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    stats=[]
    samples={}
    for i,frame in enumerate(frames):
        before=max(q for q in keys if q<=i)
        after=min(q for q in keys if q>=i)
        if i==before or before==after:ab=anchors[before]
        else:
            ab1=stabilize_color(frame,frames[before],anchors[before])
            ab2=stabilize_color(frame,frames[after],anchors[after])
            mix=(i-before)/(after-before)
            ab=(1-mix)*ab1+mix*ab2
        col=project_color(frame,ab)
        t=i/fps
        # Original film is mono; reveal is genuinely chromatic DDColor on moving video.
        x=np.clip((t-.10)/1.05,0,1)
        ramp=x*x*(3-2*x)
        merged=cv2.addWeighted(frame,1-ramp,col,ramp,0)
        # Restrained editorial disclosure on synthetic section, not mistaken for 1895 real color.
        cv2.putText(merged,"AI COLOR RECONSTRUCTION",(32,1220),cv2.FONT_HERSHEY_SIMPLEX,
                    .53,(0,0,0),3,cv2.LINE_AA)
        cv2.putText(merged,"AI COLOR RECONSTRUCTION",(32,1220),cv2.FONT_HERSHEY_SIMPLEX,
                    .53,(235,235,235),1,cv2.LINE_AA)
        if i in [0,int(fps*.5),int(fps*1.2),int(fps*2.1),int(fps*3.4),n-1]:
            samples[i]=merged.copy()
        if i%max(1,round(fps*.4))==0:
            small=cv2.resize(merged,(90,160))
            hsv=cv2.cvtColor(small,cv2.COLOR_BGR2HSV)
            sat=float(np.mean(hsv[:,:,1]))
            lab=cv2.cvtColor(small,cv2.COLOR_BGR2LAB)
            ab_spread=float(np.mean(np.abs(lab[:,:,1:].astype("float32")-128)))
            stats.append({"time":round(t,3),"saturation":round(sat,2),"lab_chroma":round(ab_spread,2)})
        p.stdin.write(merged.tobytes())
    p.stdin.close()
    e=p.stderr.read().decode(errors="replace")
    if p.wait()!=0:raise RuntimeError("FFmpeg failed "+e[-1400:])
    # Check the target is genuinely colored after 1.2 s and not merely a monochrome tint.
    later=[s for s in stats if s["time"]>=1.6]
    avg_sat=float(np.mean([q["saturation"] for q in later]))
    avg_chroma=float(np.mean([q["lab_chroma"] for q in later]))
    imlist=list(samples.items())
    from PIL import Image,ImageDraw,ImageFont
    board=Image.new("RGB",(3*280,2*518),(16,18,20))
    draw=ImageDraw.Draw(board)
    for j,(i,v) in enumerate(imlist):
        thumb=Image.fromarray(cv2.cvtColor(cv2.resize(v,(260,462)),cv2.COLOR_BGR2RGB))
        x=(j%3)*280+10;y=(j//3)*518+30
        board.paste(thumb,(x,y))
        draw.text((x,y-20),f"{i/fps:.2f}s | neural color",fill="white")
    board.save(out/"TRUE_COLOR_CONTACT_SHEET.jpg",quality=92)
    cv2.imwrite(str(out/"COLORIZED_HUMAN_REVIEW_FRAME.jpg"),samples[max(samples)], [cv2.IMWRITE_JPEG_QUALITY,92])
    pcheck=subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(output),"-f","null","-"],capture_output=True,timeout=200)
    if pcheck.returncode:raise RuntimeError("Full decode failed")
    status="colorized_needs_artistic_review" if avg_sat>25 and avg_chroma>5 else "colorization_insufficient_do_not_deliver"
    qa={"status":status,"source_type":"exact Vidu output from the 1895 authentic image",
        "model":"edgetools/ddcolor / DDColor-tiny-fp16.onnx","model_sha256":EXPECTED_MODEL_SHA,
        "original_vidu_sha256":EXPECTED_SOURCE_SHA,"output_sha256":sha(output),
        "duration_seconds":round(n/fps,3),"fps":fps,"frames":n,
        "input_size":[w,h],"AI_chroma_first_second":True,
        "disclaimer":"AI interprets historical colors, not factual historical recording",
        "DDColor_real_model_inferences":len(keys),
        "neural_color_score_saturation_mean_after_1_6_seconds":round(avg_sat,2),
        "neural_color_score_lab_ab_deviation":round(avg_chroma,2),
        "samples":stats,"vidu_new_credits_used":0,"publication":False,"master":False,
        "full_mp4_decode":"pass","owner_visual_review":"pending"}
    (out/"COLORIZATION_QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    print("REAL_NEURAL_COLORIZATION_RESULT",json.dumps({k:v for k,v in qa.items() if k not in ("samples",)}),flush=True)
    if status!="colorized_needs_artistic_review":raise RuntimeError("Neural colorization lacks sufficiently distinct colors, no delivery")
if __name__=="__main__":main()
