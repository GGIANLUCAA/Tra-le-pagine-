#!/usr/bin/env python3
"""V163: Source-locked, *photo-guided* restoration of real 1918 archival motion.

Propagates pre-existing real I2I photograph color/detail to SOURCE footage using
current->freeze optical flow, conservative residual transfer, and occlusion
confidence. This is NOT framewise generative I2I nor Vidu animation.

No network/API calls; asserts exact V162 inputs and produces review-only MP4/ZIP.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil, subprocess, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(os.environ.get('STORIA_V163_INPUT_ROOT', '.'))
BASE=ROOT/'source_v162'
PHOTO=ROOT/'photos_v162'
FILENAME='LA_STORIA_RIVIVE_PARIGI_1918_V163_MOVIMENTO_FOTO_GUIDATO_REVIEW.mp4'
FPS=30;W=720;H=1280
SCENES=[('01','La Gare',1.75,108),('02','Les cinémas',1.95,98),('03','Les rues',1.85,91),('04','Les passants',1.90,102),('05','Les journaux',3.15,105)]
SOURCE_FREEZE_SHA={1:'9dca53726983e4f794fcc5aecf99a77d6f57f4bdf946c08ec1942d7ea59cc4d0',2:'f724be55e7d8c418c492e0db068eb982ff6c5f8a342f11e4cf906afd9e85ab56',3:'29e1172fd588a072d9029e8cec39285df6583cda27867059ebefbd868103b066',4:'6d49f9d560ac91cee786e30940c4c9a8d09bcfa8e2a399b0cc1961b7a1aa2459',5:'9b173f8727c0dbfb70897a46be3c6d0bd486b8620e21845df9eb5dad89d1c3db'}
DDCOLOR_SHA={4:'0cbf5919331bd14013349ea7d96289c04b355d2b9e792c0da536d7742b15fa59',5:'934ce5f2bfe250960635bda8b2569e5db20e36999cb26440bc235c6a66b1ad3a'}
PHOTO_SHA={1:'5648bc952703a31dfbfec7501be04ff34a9297437a180cfd73a2f12258f7f64c',2:'fd6eaee3c6e4ba070b4f6ffeb357284360b102d3c2e9a2b47daa282a2e7e1fc0',3:'d2d1d0eef1c2fd0bd195c914d45652345c2c5282d7f2bbcefee7fb133c81d442'}

# V164: the five *moving* original clips are immutable, not merely their last
# frozen frame. Without these locks a substituted/zoomed clip ending on the
# same photograph would pass SOURCE_FREEZE_SHA and look historically authentic.
# These hashes were measured from V162 real_original_motion.mp4 byte files.
MOTION_CLIP_SHA = {
    'scene_01/real_original_motion.mp4': 'e459da56b86fa6d45fc21e764bc490cc40d610ff35814faa3ee2c0c97a80e45a',
    'scene_02/real_original_motion.mp4': '07b7714c856830f02da8d6cd7f2438a50ce01b18a5853cfb070f46b37aafb3b0',
    'scene_03/real_original_motion.mp4': '8208d4c96c9798db986b1642d4c99cda68d705bdcef9559953a152a38a154863',
    'scene_04/real_original_motion.mp4': '471b2f96580ccbdb0ba5ea5c019ee76b795acf5ccd0cf917c2006dbde4464a0b',
    'scene_05/real_original_motion.mp4': 'feedb65f0160fe77f5aaddc27acc14138af3672648de5bb17dbb0052f13f449f',
    'scene_05/real_original_after_freeze.mp4': '82b45d1ee65726355f169328738cbd3091da9fa14cb44ea9f5352f4296145bfe',
}


def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def verify_motion_clips(base, expected=None):
    """Fail closed before decoding/rendering if ANY actual motion bytes change.

    `expected` is injectable solely to unit-test the verifier without shipping
    the copyrighted archival source clips in the GitHub repository. Production
    always uses MOTION_CLIP_SHA, which is immutable in the renderer.
    """
    expected = MOTION_CLIP_SHA if expected is None else expected
    if len(expected) != 6 or len(set(expected.values())) != 6:
        raise ValueError('SOURCE_MOTION_FINGERPRINT_MANIFEST_INVALID')
    verified = {}
    for rel, digest in sorted(expected.items()):
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('SOURCE_MOTION_FINGERPRINT_INVALID')
        if Path(rel).is_absolute() or '..' in Path(rel).parts:
            raise ValueError('SOURCE_MOTION_PATH_UNSAFE')
        path = Path(base) / rel
        if not path.is_file() or path.is_symlink():
            raise ValueError('SOURCE_MOTION_CLIP_MISSING_OR_LINK: ' + rel)
        actual = sha(path)
        if actual != digest:
            raise ValueError('SOURCE_MOTION_SHA_CHANGED: ' + rel)
        verified[rel] = actual
    return verified


def ff(args,timeout=150):
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if r.returncode:raise RuntimeError('ffmpeg failed '+r.stderr[-1200:])
    return r.stdout


def grade(frame):
    # Identical to V162, so the freeze used for I2I is pixel-aligned.
    bgr=cv2.cvtColor(frame,cv2.COLOR_BGR2LAB)
    l,a,b=cv2.split(bgr)
    smooth=cv2.createCLAHE(clipLimit=1.12,tileGridSize=(8,8)).apply(l)
    l=cv2.addWeighted(l,.82,smooth,.18,0)
    return cv2.cvtColor(cv2.merge((l,a,b)),cv2.COLOR_LAB2BGR)


def load_clip(path):
    cap=cv2.VideoCapture(str(path)); frames=[]
    while True:
        ok,fr=cap.read()
        if not ok:break
        assert fr.shape[:2]==(576,720),f'Unexpected source geometry {fr.shape}'
        frames.append(grade(fr))
    cap.release()
    if len(frames)<30:raise ValueError('NO_ACTUAL_MOVING_FRAMES')
    return frames


def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)


def warp_map(current,anchor,flow):
    """flow grid was computed at 360x288: from current frame to source freeze."""
    displacement=cv2.resize(flow,(720,576),interpolation=cv2.INTER_LINEAR)*2.0
    yy,xx=np.indices((576,720),dtype=np.float32)
    mx=xx+displacement[...,0];my=yy+displacement[...,1]
    valid=(mx>=1)&(mx<719)&(my>=1)&(my<575)
    return mx,my,valid


def transfer_color_motion(current,anchor,photograph,flow_engine,near_anchor=False,photo_strength=1.0):
    """Texture-aware *motion-guided color* only; geometry remains original film.

    Brightness and moving edges stay current-source based; color and a bounded
    luminance residual from the source-matched I2I image are flow-propagated.
    Uncertain/occluded areas fall back to monochrome/lower chroma.
    """
    if any(x is None or x.shape!=(576,720,3) for x in (current,anchor,photograph)):
        raise ValueError('SOURCE_OR_PHOTO_GEOMETRY_MISMATCH')
    small=lambda f:cv2.resize(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(360,288),interpolation=cv2.INTER_AREA)
    if near_anchor:
        flow=np.zeros((288,360,2),np.float32)
    else:
        f=small(current);a=small(anchor)
        flow=flow_engine.calc(cv2.GaussianBlur(f,(5,5),0),cv2.GaussianBlur(a,(5,5),0),None)
    mx,my,valid=warp_map(current,anchor,flow)
    wp=cv2.remap(photograph,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT101)
    wa=cv2.remap(anchor,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT101)
    source_lab=cv2.cvtColor(current,cv2.COLOR_BGR2LAB).astype(np.float32)
    warp_lab=cv2.cvtColor(wp,cv2.COLOR_BGR2LAB).astype(np.float32)
    anchor_lab=cv2.cvtColor(wa,cv2.COLOR_BGR2LAB).astype(np.float32)
    # Reliability of the spatial correspondence. Strict at occlusion edges.
    mismatch=cv2.absdiff(cv2.GaussianBlur(source_lab[...,0],(7,7),0),cv2.GaussianBlur(anchor_lab[...,0],(7,7),0))
    confidence=np.clip((43.0-mismatch)/43.0,0,1)**1.3
    confidence *= valid.astype(np.float32)
    # Sharpen only the real film detail, not interpolation noise.
    l=source_lab[...,0]
    base=cv2.bilateralFilter(l,5,15,3)
    high=cv2.subtract(base,cv2.GaussianBlur(base,(0,0),.74))
    l=base+high*.29
    # The matched photo contributes only *bounded* brightness and fine texture.
    delta=np.clip(warp_lab[...,0]-anchor_lab[...,0],-35,35)
    l+=photo_strength*.76*confidence*delta
    a=128+(warp_lab[...,1]-128)*(.70+.25*confidence)*photo_strength
    b=128+(warp_lab[...,2]-128)*(.70+.25*confidence)*photo_strength
    out=np.empty_like(source_lab)
    out[...,0]=np.clip(l,0,255)
    out[...,1]=np.clip(128+(a-128)*confidence,0,255)
    out[...,2]=np.clip(128+(b-128)*confidence,0,255)
    return cv2.cvtColor(out.astype(np.uint8),cv2.COLOR_LAB2BGR),float(np.mean(confidence)),float(np.mean(mismatch))


def background(anchor,photo,scene):
    # Backdrop from the ACTUAL same scene, two states for coherent reveal.
    color=cv2.resize(photo,(720,1280),interpolation=cv2.INTER_LINEAR)
    gray=cv2.resize(anchor,(720,1280),interpolation=cv2.INTER_LINEAR)
    def tone(x):
        x=cv2.GaussianBlur(x,(0,0),24).astype(np.float32)*.32
        x=x*.65+np.asarray([12,15,19],np.float32)[None,None,:]*.35
        return np.clip(x,0,255).astype(np.uint8)
    return tone(gray),tone(color)


def overlay_base(gray_bg,color_bg,base_alpha):
    return cv2.addWeighted(gray_bg,1-base_alpha,color_bg,base_alpha,0)


def composer(frame,gray_bg,color_bg,alpha,label):
    # Expand visual real estate from old 540 px to 768 px high: 42% -> 60%.
    bg=overlay_base(gray_bg,color_bg,alpha)
    # Crop is THE SAME for source and restored frame; chosen to retain the key crowd.
    x0={'01':70,'02':78,'03':90,'04':94,'05':90}[label]
    cropped=frame[:,x0:x0+540]
    assert cropped.shape[:2]==(576,540)
    shown=cv2.resize(cropped,(720,768),interpolation=cv2.INTER_CUBIC)
    y0=256
    bg[y0:y0+768]=shown
    cv2.line(bg,(0,y0),(719,y0),(155,148,131),1)
    cv2.line(bg,(0,y0+767),(719,y0+767),(155,148,131),1)
    return bg


def title_frame(frame):
    img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    draw=ImageDraw.Draw(img)
    fpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    fbold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    title='PARIGI  ·  1918'
    font=ImageFont.truetype(fbold,36)
    area=draw.textbbox((0,0),title,font=font)
    draw.text(((720-area[2]+area[0])/2,126),title,font=font,fill=(240,237,230))
    draw.text((44,1121),'MUSÉE ALBERT-KAHN  ·  ARCHIVIO CC0',font=ImageFont.truetype(fpath,17),fill=(202,200,193))
    return cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)


def audio(duration,path):
    # Reuse V162 original music without remixing, appropriate for A/B comparability.
    inp=BASE/'MUSICA_ORIGINALE.wav'
    if not inp.is_file():raise ValueError('V162 audio missing')
    shutil.copy2(inp,path)


def main():
    global BASE, PHOTO
    pa=argparse.ArgumentParser()
    pa.add_argument('--source-v162-dir',default=str(BASE))
    pa.add_argument('--photos-v162-dir',default=str(PHOTO))
    pa.add_argument('--out',default='output/storia_paris_v163_photo_guided')
    a=pa.parse_args()
    BASE=Path(a.source_v162_dir); PHOTO=Path(a.photos_v162_dir)
    # Check the six full motion clips before any output directory is created.
    verified_motion_sha=verify_motion_clips(BASE)
    dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    for i,expected in PHOTO_SHA.items():
        p=PHOTO/f'PHOTO_I2I_{i:02d}.png'
        assert p.is_file() and sha(p)==expected,f'Exact V162 I2I photo lost or changed: scene {i}'
    tracks=[];qa_scenes=[];sample=[]
    engine=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    engine.setFinestScale(1)
    for i,(scene,label,hold,_) in enumerate(SCENES,1):
        real_frames=load_clip(BASE/f'scene_{scene}'/'real_original_motion.mp4')
        archive_anchor=real_frames[-1]
        exact=BASE/f'scene_{scene}'/'EXACT_MP4_LAST_MOTION_FRAME.png'
        # exact PNG equality with the film's last frame after V162 grade
        assert sha(exact)==SOURCE_FREEZE_SHA[i], f'SOURCE_FREEZE_SHA_CHANGED_{scene}'
        assert np.mean(np.abs(archive_anchor.astype(np.int16)-cv2.imread(str(exact)).astype(np.int16)))<.05, f'SOURCE_FREEZE_DISAGREES_{scene}'
        orig_anchor_sha=sha(exact)
        if i<=3:
            photo=cv2.imread(str(PHOTO/f'PHOTO_I2I_{i:02d}.png'))
            photo_method='REAL_FINEGRAIN_I2I_V162_REUSED'
        else:
            reference=PHOTO/f'NEURAL_DDCOLOR_{i:02d}.png'
            assert sha(reference)==DDCOLOR_SHA[i], f'NEURAL_ANCHOR_SHA_CHANGED_{scene}'
            photo=cv2.imread(str(reference))
            photo_method='DDCOLOR_ONLY_NO_GENERATIVE_I2I'
            # Avoid artificial neon-magenta on scene 4 and 5, conservatively.
            hsv=cv2.cvtColor(photo,cv2.COLOR_BGR2HSV)
            hsv[...,1]=np.clip(hsv[...,1].astype(np.float32)*(.50 if i==4 else .64),0,255).astype(np.uint8)
            photo=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
        gray_bg,color_bg=background(archive_anchor,photo,scene)
        whole=[];conf=[];err=[];movement=[];colored_frames=0
        for k,frame in enumerate(real_frames):
            colorized,confidence,mismatch=transfer_color_motion(frame,archive_anchor,photo,engine,near_anchor=(k==len(real_frames)-1))
            conf.append(confidence);err.append(mismatch)
            t=k/FPS
            alpha=float(smooth((t-.17)/.46))
            if alpha>.4:colored_frames+=1
            current=cv2.addWeighted(frame,1-alpha,colorized,alpha,0)
            # Guide the end of the moving shot into EXACT same source photo,
            # with 0.10s crossfade, not artificial extra camera motion.
            end_t=(len(real_frames)-1-k)/FPS
            final_fade=float(smooth((.12-end_t)/.12))
            if final_fade>0:
                current=cv2.addWeighted(current,1-final_fade,photo,final_fade,0)
            shown=composer(current,gray_bg,color_bg,max(alpha,final_fade),scene)
            whole.append(shown)
            if len(whole)>1:
                # Visual motion sanity: real changes in content, excludes static zoom.
                prev=whole[-2][300:980];now=shown[300:980]
                movement.append(float(np.mean(cv2.absdiff(cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY),cv2.cvtColor(now,cv2.COLOR_BGR2GRAY)))))
        # Source-locked photograph, with same composition and no invented motion.
        if i<5:
            n=int(round(hold*FPS))
            for k in range(n):
                frozen=composer(photo,gray_bg,color_bg,1.,scene)
                whole.append(frozen)
        else:
            # Genuine *moving* archive post-freeze; source matched, never claim Vidu.
            after_frames=load_clip(BASE/f'scene_{scene}'/'real_original_after_freeze.mp4')
            for k,frame in enumerate(after_frames):
                # Calculate actual dense current-to-anchor flow (motion remains source film).
                colorized,confidence,mismatch=transfer_color_motion(frame,archive_anchor,photo,engine)
                conf.append(confidence);err.append(mismatch)
                shown=composer(colorized,gray_bg,color_bg,1,scene)
                if whole:
                    prev=whole[-1][300:980];now=shown[300:980]
                    movement.append(float(np.mean(cv2.absdiff(cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY),cv2.cvtColor(now,cv2.COLOR_BGR2GRAY)))))
                whole.append(shown)
        # Add clean but non-intrusive text on every frame, small text only.
        tracks.extend(title_frame(f) for f in whole)
        # sample exact actual source moment and its matched color motion, plus photo.
        sample.append((scene,cv2.resize(whole[0],(360,640)),cv2.resize(whole[min(len(real_frames)-1,28)],(360,640)),cv2.resize(whole[-1],(360,640))))
        qa_scenes.append({'scene':i,'original_freeze_sha256':orig_anchor_sha,'photo_sha256':PHOTO_SHA.get(i,sha(PHOTO/f'NEURAL_DDCOLOR_{i:02d}.png')),
                          'photo_kind':photo_method,'original_moving_frames':len(real_frames),'full_color_motion_frames_over_40pct_reveal':colored_frames,
                          'mean_flow_match_confidence':round(float(np.mean(conf)),4),'mean_source_motion_delta_gray':round(float(np.mean(movement)),3),
                          'photo_motion_color_transferred':i<=3,'fifth_after_freeze_real_motion_frames':len(after_frames) if i==5 else 0,
                          'QA_status':'REVIEW_REQUIRED'})
        print('V163_SCENE',i,'FRAMES',len(whole),'PHOTO',photo_method,'CONF',qa_scenes[-1]['mean_flow_match_confidence'],flush=True)
    # With 5 scenes, 17 seconds at 30fps; the new motion color does not change length.
    nframes=len(tracks);duration=nframes/FPS
    assert 14<=duration<=35
    raw=dest/'V163_RENDER_VIDEO_ONLY.mp4'
    proc=subprocess.Popen(['ffmpeg','-nostdin','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','720x1280','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(raw)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for frame in tracks:
            proc.stdin.write(np.ascontiguousarray(frame).tobytes())
    finally:
        proc.stdin.close();error=proc.stderr.read().decode(errors='replace');rc=proc.wait()
    if rc:raise RuntimeError('Encoding failed '+error[-500:])
    wav=dest/'MUSICA_ORIGINALE_V162_REUSED.wav';audio(duration,wav)
    movie=dest/FILENAME
    ff(['ffmpeg','-nostdin','-y','-v','error','-i',str(raw),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(movie)])
    ff(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(movie),'-f','null','-'],timeout=200)
    probe=json.loads(ff(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height','-of','json',str(movie)]))
    assert any(s.get('codec_name')=='h264' and s.get('width')==W and s.get('height')==H for s in probe['streams'])
    assert any(s.get('codec_name')=='aac' for s in probe['streams'])
    # Contact sheet documents changes in real pixels (not an invented image).
    board=Image.new('RGB',(1080,5*640),(16,16,18));d=ImageDraw.Draw(board)
    for ri,(scene,first,colored,last) in enumerate(sample):
        for ci,f in enumerate([first,colored,last]):
            board.paste(Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)),(ci*360,ri*640))
        d.text((8,ri*640+8),f'SCENA {scene} - B/N originale',fill='white')
        d.text((368,ri*640+8),f'SCENA {scene} - movimento restaurato',fill='white')
        d.text((728,ri*640+8),f'SCENA {scene} - finale',fill='white')
    board.save(dest/'V163_SCENE_REALI_CONFRONTO.jpg',quality=89)
    cover=dest/'V163_COPERTINA.jpg';Image.fromarray(cv2.cvtColor(tracks[23],cv2.COLOR_BGR2RGB)).save(cover,quality=92)
    qa={'version':'V163','video_status':'rendered_rejected_artistic_quality','focus':'improved moving-shot color and source photo guided transfer, never imaginary animation',
        'source_origin':'Musee Albert-Kahn / Wikimedia Commons original AI139599 verified in V160/V162','source_sha1':'aa471da773d14f422d1387654601ca03b5224455',
        'source_PTS_and_shot_selection_unchanged':True,'verified_six_motion_clips_sha256':verified_motion_sha,
        'v162_same_three_i2i_photos_reused_byte_exact':True,'photographs_changed_or_regenerated':False,
        'generative_photo_i2i_count':3,'true_frame_by_frame_generative_i2i':0,'real_vidu_clip_count':0,'paid_credits_consumed':0,
        'optical_flow_method':'OpenCV DIS current-to-exact freeze, bounded luminance residual & occlusion-aware chroma; no invented motion',
        'new_photo_guided_real_moving_shots':3,'ddcolor_derived_color_moving_shots':2,'scene_raster_720x576_source_encoded_sar_non_square':True,
        'display_main_subject_area':'720x768 cropped from 540px width, vertical composition, full source available separately',
        'scenes':qa_scenes,'movie_file':movie.name,'movie_sha256':sha(movie),'bytes':movie.stat().st_size,
        'duration_seconds':duration,'frames':nframes,'codec':'H264/AAC','full_ffmpeg_decode':'PASS','sha256_source_photos':[PHOTO_SHA[i] for i in sorted(PHOTO_SHA)],
        'fourth_i2i_status':'MISSING_PREEXISTING_FREE_PROVIDER_FAILURE','fifth_real_vidu':'MISSING_NO_CREDIT_SPENT',
        'V99_final_gate':'NOT_PASSED_NO_REAL_VIDU_OR_FOURTH_I2I','italian_rights_review':'PENDING','human_artistic_QA':'REJECTED_USER_REFERENCES_43055_43056',
        'moving_restoration_photoreal_target_met':False,
        'quality_ref_v165':'docs/LA_STORIA_RIVIVE_V165_BENCHMARK_VISIVO_43055_43056.md','published':False}
    (dest/'V163_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (dest/'V163_POST_SOCIAL_BOZZE.txt').write_text('FACEBOOK: Parigi, 1918: pellicola originale e ricostruzione cromatica guidata da vere foto restaurate. Prova in revisione, non pubblicata.\nINSTAGRAM: PARIGI · 1918. Una città che torna a muoversi a colori. Ricostruzione artistica digitale in revisione.\nTIKTOK: Fotogrammi veri. Colori e dettagli ricostruiti. Movimento originale del 1918.\nYOUTUBE SHORTS: Parigi 1918 · Pellicola originale in movimento, fotografia AI e ricostruzione cromatica.\n',encoding='utf-8')
    pkg=dest/'LA_STORIA_RIVIVE_PARIGI_1918_V163_KIT_ANDROID.zip'
    with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in [movie,cover,dest/'V163_SCENE_REALI_CONFRONTO.jpg',dest/'V163_QA.json',dest/'V163_POST_SOCIAL_BOZZE.txt']:
            z.write(p,p.name)
    with zipfile.ZipFile(pkg) as z:assert z.testzip() is None
    print('V163_SUCCESS',movie.name,movie.stat().st_size,sha(movie),'ZIP',pkg.stat().st_size,'SEC',duration,flush=True)

if __name__=='__main__':main()