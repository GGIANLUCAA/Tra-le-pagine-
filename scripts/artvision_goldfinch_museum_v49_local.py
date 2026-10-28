from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
from pathlib import Path
import subprocess,shutil,hashlib,json,zipfile
ROOT=Path('/mnt/data')
ORIG=ROOT/'ArtVision_Goldfinch_S01.mp4'
SRC=ROOT/'GOLDFINCH_S01_FULL'
ART=Image.open(SRC/'ORIGINAL_ARTWORK.jpg').convert('RGB'); ART.thumbnail((1200,1832),Image.Resampling.LANCZOS)
BG=Image.open(ROOT/'interior_museum_gallery_scene_moody_warm_lighting.png').convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
W,H,FPS=1080,1920,24
DIR=ROOT/'GOLDFINCH_S01_V49_WORK';DIR.mkdir(exist_ok=True)
F1='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf';F2='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
TITLE='THE GOLDFINCH';ARTIST='CAREL FABRITIUS'

def brand(frame,alpha=1):
    base=frame.convert('RGBA');layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,round(210*alpha)))
    f=ImageFont.truetype(F1,65);w=d.textbbox((0,0),TITLE,font=f)[2]
    d.text(((W-w)/2,1371),TITLE,font=f,fill=(255,251,243,round(255*alpha)))
    d.line((130,1495,950,1495),fill=(218,198,168,round(186*alpha)),width=2)
    f=ImageFont.truetype(F2,34);w=d.textbbox((0,0),ARTIST,font=f)[2]
    d.text(((W-w)/2,1521),ARTIST,font=f,fill=(255,251,243,round(255*alpha)))
    return Image.alpha_composite(base,layer).convert('RGB')

def gallery(z):
    z=max(1.,min(3.5,z));cw=W/z;ch=H/z
    x0=max(0,min(W-cw,700-cw/2));y0=max(0,min(H-ch,620-ch/2))
    bg=BG.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H),Image.Resampling.BICUBIC)
    cx=(700-x0)*z;cy=(620-y0)*z
    pw=round(148*z);ph=round(pw*33.5/22.8)
    x=round(cx-pw/2);y=round(cy-ph/2);t=max(3,round(9*z))
    # Physically nested wooden frame: artwork is behind its inner lip.
    sh=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((x-t+6*z,y-t+10*z,x+pw+t+6*z,y+ph+t+10*z),radius=3,fill=(0,0,0,90))
    sh=sh.filter(ImageFilter.GaussianBlur(max(3,round(6*z))))
    bg=Image.alpha_composite(bg.convert('RGBA'),sh).convert('RGB')
    d=ImageDraw.Draw(bg)
    d.rectangle((x-t,y-t,x+pw+t,y+ph+t),fill=(40,29,20))
    d.rectangle((x-t+2,y-t+2,x+pw+t-2,y+ph+t-2),outline=(152,124,79),width=max(2,round(2*z)))
    art=ART.resize((pw,ph),Image.Resampling.LANCZOS)
    bg.paste(art,(x,y))
    d=ImageDraw.Draw(bg)
    inner=max(2,round(3*z))
    d.rectangle((x-inner,y-inner,x+pw+inner,y+ph+inner),outline=(31,25,20),width=inner)
    d.line((x-inner,y-inner,x+pw+inner,y-inner),fill=(194,163,106),width=max(1,round(1.5*z)))
    d.line((x-inner,y-inner,x-inner,y+ph+inner),fill=(162,132,91),width=max(1,round(1.5*z)))
    return bg

def call(args):subprocess.run(args,check=True)
frames_per=[134,122,130,127,122,122,125,130,122,187]
ranges={0:(1,1.25),1:(1.25,2.2),2:(2.2,3.5),8:(3.5,2.2),9:(2.2,1)}
for idx,(a,b) in ranges.items():
    d=DIR/f'frames_{idx:02d}';d.mkdir(exist_ok=True)
    for n in range(frames_per[idx]):
        t=n/max(1,frames_per[idx]-1);smooth=t*t*(3-2*t);z=a+(b-a)*smooth
        frame=gallery(z)
        if idx==0:
            seconds=n/FPS
            opacity=1 if seconds<=2.9 else max(0,1-(seconds-2.9)/.55)
            frame=brand(frame,opacity)
        frame.save(d/f'f{n:04d}.jpg',quality=91,subsampling=0)
    call(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(d/'f%04d.jpg'),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(DIR/f'clip_{idx:02d}.mp4')])
    shutil.rmtree(d)
    print('GALLERY_SCENE',idx,flush=True)
# Keep original artwork-detail footage intact, preserving exact frame indices.
call(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(ORIG),'-vf','trim=start_frame=386:end_frame=1012,setpts=PTS-STARTPTS','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(DIR/'details.mp4')])
clips=[DIR/'clip_00.mp4',DIR/'clip_01.mp4',DIR/'clip_02.mp4',DIR/'details.mp4',DIR/'clip_08.mp4',DIR/'clip_09.mp4']
(DIR/'concat.txt').write_text(''.join("file '"+str(p.resolve())+"'\n" for p in clips))
call(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(DIR/'concat.txt'),'-c:v','copy',str(DIR/'silent.mp4')])
FINAL=ROOT/'ArtVision_Goldfinch_Museum_V49_REVIEW.mp4'
call(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(DIR/'silent.mp4'),'-i',str(ORIG),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-shortest','-movflags','+faststart',str(FINAL)])
COVER=ROOT/'ArtVision_Goldfinch_Museum_V49_Cover.jpg';brand(gallery(1),1).save(COVER,quality=95,subsampling=0)
FIRST=DIR/'QA_FIRST_FRAME_V49.jpg'
call(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(FINAL),'-frames:v','1',str(FIRST)])
with Image.open(FIRST) as a,Image.open(COVER) as b:
    assert a.size==b.size==(1080,1920)
    mad=float(np.mean(np.abs(np.asarray(a,dtype=np.int16)[1340:1590]-np.asarray(b,dtype=np.int16)[1340:1590])))
    assert mad<15,('cover mismatch',mad)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height','-of','json',str(FINAL)]))
assert any(s.get('codec_name')=='h264' and s.get('width')==1080 and s.get('height')==1920 for s in probe['streams'])
assert any(s.get('codec_name')=='aac' for s in probe['streams'])
call(['ffmpeg','-hide_banner','-loglevel','error','-xerror','-i',str(FINAL),'-f','null','-'])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Copy original full dossier, replace the video and cover, add provenance and revision.
PACK=ROOT/'GOLDFINCH_S01_V49_PACKAGE';shutil.copytree(SRC,PACK,dirs_exist_ok=True)
shutil.copy2(FINAL,PACK/'VIDEO_MASTER.mp4');shutil.copy2(COVER,PACK/'COPERTINA.jpg')
shutil.copy2(FIRST,PACK/'QA_FIRST_FRAME_V49.jpg')
shutil.copy2(ROOT/'interior_museum_gallery_scene_moody_warm_lighting.png',PACK/'ILLUSTRATIVE_GALLERY_BACKGROUND.png')
recipe=json.loads((PACK/'VIDEO_RECIPE_V13.json').read_text())
recipe.update({'revision':'V49','renderer':'local original-asset remount /mnt/data/make_goldfinch_v49.py',
 'museum_scene':'AI-created illustrative gallery, not Mauritshuis room 14',
 'new_scene_background':'ILLUSTRATIVE_GALLERY_BACKGROUND.png',
 'museum_scale':'panel 33.5 x 22.8 cm, woman approximately 1.7m; gallery scene 148x217 px at wide view',
 'source_video_sha256':sha(ORIG),'new_video_sha256':sha(FINAL),'status':'rendered_needs_review','human_approved':False})
(PACK/'VIDEO_RECIPE_V13.json').write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n')
qa=json.loads((PACK/'TECHNICAL_QA_V30.json').read_text())
qa.update({'revision':'V49','video_sha256':sha(FINAL),'cover_first_frame_band_mad':mad,
 'qa_ffprobe':probe,'full_decode':True,'cover_and_first_frame':{'title':TITLE,'artist':ARTIST,'visual_checked':True},
 'gallery_reconstruction':'New generated photorealistic background; NOT documentary photograph of Mauritshuis',
 'v44_status':'rendered_needs_review','human_artistic_approval':False,
 'prior_defect':'The Temptation of Saint Anthony omitted mandatory opening title/artist; both checked in V49',
 'self_critique':['Photo gallery is stronger than V48 vector room; must review frame integration at 24fps',
                 'Detail section retains previous crop choices and might not show bird eye as long as intended',
                 'No human full-speed listening signoff; do not publish or call Gold Master']})
(PACK/'TECHNICAL_QA_V30.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
(PACK/'SOURCES_AND_RIGHTS.md').open('a').write('\nV49 gallery background: newly generated original illustrative scene. Not a real Mauritshuis photograph; woman is fictional. Painting and music sources/rights remain as previously recorded. No paid video API used.\n')
(PACK/'RELEASE_STATUS.json').write_text(json.dumps({'state':'rendered_needs_review','video_sha256':sha(FINAL),'human_approved':False,'social_published':False,'rights_recheck_required':True},indent=2)+'\n')
(PACK/'REVISION_V49.md').write_text('# Goldfinch Museum V49\n\nReplaced flat vector museum background with an original photographic-style gallery illustration. The museum is fictional and not a Mauritshuis room. Physical painting size is 33.5 × 22.8 cm, proportioned against an adult visitor. Real original artwork and licensed Water Lily recording preserved. V44 status rendered_needs_review.\n')
ZIP=ROOT/'ArtVision_Goldfinch_Museum_V49_Complete.zip'
with zipfile.ZipFile(ZIP,'w',allowZip64=True) as z:
    for p in PACK.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(PACK),compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ('.mp4','.jpg','.mp3','.png') else zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(ZIP) as z:assert z.testzip() is None
print('V49_COMPLETE',json.dumps({'sha256':sha(FINAL),'seconds':probe['format']['duration'],'bytes':FINAL.stat().st_size,'zip_bytes':ZIP.stat().st_size,'cover_diff':mad,'status':'rendered_needs_review'}),flush=True)