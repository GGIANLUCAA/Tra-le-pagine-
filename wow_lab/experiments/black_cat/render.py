#!/usr/bin/env python3
"""WOW LAB / Zhu Ling / Black Cat. CC0 authentic Met source, isolated experiment.
One clean silhouette + ink-to-depth, no narcissus extraction, no paid APIs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,cv2,subprocess,hashlib,json,wave,math,zipfile
R=Path(__file__).resolve().parent;O=R/'RENDER';O.mkdir(exist_ok=True)
SRC=R/'CAT_WORK.png';ORIGINAL=R/'CAT_ORIGINAL.jpg';PROV=R/'PROVENANCE.json'
W,H,FPS,DUR=720,1280,24,12.0
CROP=(15,230,755,1200);PW,PH=515,round((CROP[3]-CROP[1])*515/(CROP[2]-CROP[0]));PX,PY=103,285
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf';SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(s,serif=True):return ImageFont.truetype(FONT if serif else SANS,s)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def env(t):
    if t<1:return 0.
    if t<3:return ease((t-1)/2)
    if t<7.4:return 1.
    if t<10:return 1-ease((t-7.4)/2.6)
    return 0.
def analyze_mask(source):
    im=np.array(source);h,w=im.shape[:2]
    r,g,b=[im[:,:,i].astype('int16') for i in range(3)]
    region=np.zeros((h,w),np.uint8);region[410:918,75:715]=255
    dark=((r<142)&(g<147)&(b<153)&(abs(r-b)<42))&(region>0)
    raw=np.uint8(dark)*255
    closed=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(27,27)))
    n,labels,stats,_=cv2.connectedComponentsWithStats(closed,8)
    keep=np.zeros_like(closed)
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]>30000:keep[labels==i]=255
    cont,_=cv2.findContours(keep,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if len(cont)!=1:raise RuntimeError(f'CAT MASK REJECT: {len(cont)} foreground regions')
    mask=np.zeros_like(keep);cv2.drawContours(mask,cont,-1,255,cv2.FILLED)
    yy,xx=np.mgrid[:h,:w]
    # The real cat ends above this rock: prevent dark landscape from moving.
    # Curve of the physical lower cat silhouette, not a flat rectangular cutoff.
    xs=np.array([0,100,135,170,235,305,370,440,510,575,635,685,730,945],float)
    lows=np.array([750,775,837,859,862,872,895,906,905,896,865,807,742,742],float)
    cat_floor=np.interp(np.arange(w),xs,lows)[None,:]
    mask=np.where(yy<=cat_floor,mask,0).astype('uint8')
    mask[(xx<109)&(yy>745)]=0
    # v4 visual QA: exclude the thin horizontal rock ink stroke to the
    # left of the animal, without removing its actual neck / ear shapes.
    # This is artwork-specific; the broad automatic mask missed this flaw.
    mask[(xx<119)&(yy>=565)&(yy<760)]=0
    # Remove beige halo around the body ONLY; do not blunt the ear tips.
    thin=cv2.erode(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    mix=np.clip((yy-690)/55,0,1).astype('float32')
    mask=np.uint8(mask*(1-mix)+thin*mix)
    mask=cv2.GaussianBlur(mask,(5,5),.85)
    region_ratio=float(np.mean(mask[410:918,75:715]>128))
    if not (.58<region_ratio<.71):raise RuntimeError(f'CAT MASK REJECT ratio={region_ratio:.3f}')
    n,labels,stats,_=cv2.connectedComponentsWithStats(np.uint8(mask>127),8)
    biggest=max([stats[i,cv2.CC_STAT_AREA] for i in range(1,n)],default=0)
    if biggest<160000:raise RuntimeError('CAT MASK REJECT: main silhouette incomplete')
    return mask,region_ratio

def compose_source():
    meta=json.loads(PROV.read_text())
    assert meta['object_id']==36075 and meta['is_public_domain'] and meta['license']=='Met Open Access CC0'
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==meta['sha256']
    original=Image.open(SRC).convert('RGB')
    mask,ratio=analyze_mask(np.array(original))
    # One continuous real feline silhouette, including both ears and tail.
    source=np.asarray(original)
    audit=source.astype('float32')
    fac=mask.astype('float32')/255
    audit[:,:,0]=audit[:,:,0]*(1-fac*.15)+fac*230*.15
    audit[:,:,1]=audit[:,:,1]*(1-fac*.28)
    audit[:,:,2]=audit[:,:,2]*(1-fac*.37)
    Image.fromarray(audit.astype('uint8')).resize((390,992)).save(O/'MASK_AUDIT.jpg',quality=93)
    Image.fromarray(mask).save(O/'CAT_MASK.png')
    cx1,cy1,cx2,cy2=CROP
    cutmask=Image.fromarray(mask).crop(CROP).resize((PW,PH),Image.Resampling.LANCZOS)
    art=original.crop(CROP).resize((PW,PH),Image.Resampling.LANCZOS)
    # Genuine pigment in the moving layer. No new cat anatomy created.
    sprite=art.convert('RGBA');sprite.putalpha(cutmask)
    # In the void where the cat once rested, old parchment remains. A smooth
    # ink-bleach gradient, not falsely labeled as restoration of hidden art.
    paper=np.asarray(art).astype('float32')
    paint=np.zeros_like(paper)
    yy,xx=np.mgrid[:PH,:PW]
    light=np.exp(-((xx-PW*.55)/(PW*.9))**2-((yy-PH*.42)/(PH*.7))**2)
    for k,(base,hi) in enumerate([(207,9),(191,12),(162,13)]):
        paint[:,:,k]=base+hi*light
    a=(np.asarray(cutmask).astype('float32')/255)[:,:,None]
    void=Image.fromarray(np.uint8(np.clip(paper*(1-a)+paint*a,0,255)),'RGB').convert('RGBA')
    # Keep crop and sprite aligned in source coordinates.
    return art.convert('RGBA'),void,sprite,ratio,meta

def stage():
    y,x=np.mgrid[:H,:W];glow=np.exp(-((x-W*.5)/(W*.65))**2-((y-H*.33)/(H*.8))**2)
    no=np.random.default_rng(36075).normal(0,.6,(H,W))
    bg=np.zeros((H,W,3),'uint8')
    for c,(b,p) in enumerate([(19,20),(24,23),(22,17)]):bg[:,:,c]=np.clip(b+p*glow+no,0,255)
    im=Image.fromarray(bg,'RGB').convert('RGBA')
    d=ImageDraw.Draw(im)
    d.text((W//2,73),'ARTVISION  ·  WOW LAB',font=f(22,False),fill=(205,193,158),anchor='mm')
    d.text((W//2,126),'THE INK CAT',font=f(51),fill=(245,237,218),anchor='mm')
    d.text((W//2,170),'BLACK CAT AND NARCISSUS',font=f(19,False),fill=(180,200,193),anchor='mm')
    d.rectangle((0,1080,W,H),fill=(12,18,17))
    shade=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shade)
    sd.rectangle((PX-25,PY-25,PX+PW+26,PY+PH+29),fill=(0,0,0,145))
    im=Image.alpha_composite(im,shade.filter(ImageFilter.GaussianBlur(20)))
    d=ImageDraw.Draw(im)
    # A simple graphic presentation frame: no false claim about real mounting.
    for off,col,w in [(14,(56,66,60),4),(10,(113,124,99),3),(5,(180,182,149),2),(1,(79,91,70),2)]:
        d.rectangle((PX-off,PY-off,PX+PW+off,PY+PH+off),outline=col,width=w)
    d.text((W//2,1119),'ZHU LING  ·  19TH CENTURY',font=f(20,False),fill=(207,206,178),anchor='mm')
    d.text((W//2,1158),'THE MET · CC0 ORIGINAL',font=f(18,False),fill=(163,181,170),anchor='mm')
    d.text((W//2,1194),'WHEN INK BECOMES SHADOW',font=f(19),fill=(219,208,169),anchor='mm')
    return im

def render(t,source,void,sprite,wall):
    p=env(t)
    image=wall.copy()
    image.alpha_composite(Image.blend(source,void,p),(PX,PY))
    if p>.001:
        # The cat leaves the original sheet as one complete silhouette,
        # with no fragile flower/leaf masks. Slow breathing creates life.
        z=1+.34*p+0.007*math.sin(t*2.7)*p
        size=(round(PW*z),round(PH*z))
        fig=sprite.resize(size,Image.Resampling.BICUBIC)
        anchorx=PX+PW*.48;anchory=PY+PH*.54
        px=round(anchorx+(PX-anchorx)*z+2*p)
        py=round(anchory+(PY-anchory)*z-37*p+4*math.sin(t*1.8)*p)
        alpha=fig.getchannel('A')
        shadow=Image.new('RGBA',(W,H))
        dark=Image.new('RGBA',fig.size,(5,8,7,0))
        dark.putalpha(alpha.point(lambda v:round(v*.46*p)))
        shadow.paste(dark,(px+round(21*p),py+round(25*p)))
        image=Image.alpha_composite(image,shadow.filter(ImageFilter.GaussianBlur(18)))
        image.alpha_composite(fig,(px,py))
    return image.convert('RGB')

def make_audio(path):
    sr=24000;t=np.arange(round(sr*DUR))/sr
    rng=np.random.default_rng(36075)
    hiss=np.convolve(rng.normal(0,1,len(t)),np.ones(21)/21,mode='same')
    sound=.022*hiss
    for start,frq,vol in [(1.25,173,.045),(2.7,127,.046),(7.6,98,.035)]:
        k=t-start; e=np.where(k>=0,np.exp(-np.maximum(k,0)*1.9),0)
        sound+=vol*np.sin(2*np.pi*(frq*k-2*k*k))*e
    sound+=.026*np.sin(2*np.pi*110*t)*np.exp(-((t-5)/3.1)**2)
    sound*=np.minimum(1,np.minimum(t/.55,(DUR-t)/.7))
    with wave.open(str(path),'wb') as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr)
        wf.writeframes(np.int16(np.clip(sound,-.8,.8)*32767).tobytes())

def main():
    orig,void,cat,ratio,meta=compose_source();base=stage()
    snaps={}
    for name,t in [('BEFORE',.4),('CAT_RELEASE',2.5),('WOW_MOMENT',5),('RETURN',10.8)]:
        fr=render(t,orig,void,cat,base);fr.save(O/f'{name}.jpg',quality=92);snaps[name]=fr
    side=Image.new('RGB',(2*W,H));side.paste(snaps['BEFORE'],(0,0));side.paste(snaps['WOW_MOMENT'],(W,0))
    side.save(O/'BEFORE_AFTER.jpg',quality=92)
    aud=O/'ORIGINAL_AUDIO.wav';make_audio(aud)
    video=O/'ZHU_LING_INK_CAT_V4_WOW_ANDROID.mp4'
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
      '-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-i',str(aud),
      '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
      '-c:a','aac','-b:a','128k','-movflags','+faststart','-t',str(DUR),str(video)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(int(FPS*DUR)):
            p.stdin.write(np.asarray(render(i/FPS,orig,void,cat,base)).tobytes())
        p.stdin.close();err=p.stderr.read().decode(errors='replace')
        if p.wait()!=0:raise RuntimeError(err[-900:])
    except BaseException:
        p.kill();raise
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'],check=True,timeout=120)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height:format=duration','-of','json',str(video)],text=True))
    codec=[s['codec_name'] for s in probe['streams']]
    assert 'h264' in codec and 'aac' in codec and video.stat().st_size>100000 and float(probe['format']['duration'])>11.9
    qa={'status':'experimental_needs_art_review','technical_pass':True,'object_id':36075,
        'title':meta['title'],'artist':meta['artist'],'source_license':'Met CC0',
        'source_sha256':meta['sha256'],'mask_area_ratio':round(ratio,4),
        'main_subject':'complete original black cat silhouette','flowers_extracted':False,
        'duration_seconds':DUR,'resolution':[W,H],'fps':FPS,'codecs':codec,
        'effect':'Ink-to-depth full cat matte, hand-refined stray-edge cleanup (2.5D, NOT 3D)','paid_api_spend':0,
        'real_museum_frame_reproduced':False,'auto_social_posting':False}
    (O/'QA.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False))
    (O/'SOCIAL_DRAFT.txt').write_text('Un gatto dipinto a inchiostro sembra staccarsi da una pittura cinese dell’Ottocento. Zhu Ling — Black Cat and Narcissus. Opera originale: The Metropolitan Museum of Art, Open Access CC0. Esperimento di illusione 2.5D; presentazione virtuale. #ArtVision #WowLab #ArtHistory\n')
    kit=O/'ZHU_LING_INK_CAT_V4_ANDROID_KIT.zip'
    names=[video.name,'BEFORE.jpg','WOW_MOMENT.jpg','CAT_RELEASE.jpg','RETURN.jpg','BEFORE_AFTER.jpg','MASK_AUDIT.jpg','QA.json','SOCIAL_DRAFT.txt']
    with zipfile.ZipFile(kit,'w',zipfile.ZIP_DEFLATED) as z:
        for name in names:z.write(O/name,name)
    with zipfile.ZipFile(kit) as z:assert z.testzip() is None
    print(json.dumps({'video':str(video),'kit':str(kit),'qa':qa},ensure_ascii=False))
if __name__=='__main__':main()