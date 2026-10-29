#!/usr/bin/env python3
"""Original Hokusai Cinema Museum V55: documented print, reconstructed display.

Prepared via the existing Hokusai Met JP1847 downloader and V54/V13 preflight.
The display room is an original modern reconstruction, NEVER a photograph of
the Met galleries or an original historical frame. No AI video or paid APIs.
Review-only output; no autonomous archive import or social publication.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
import artvision_hokusai_cinema_v55 as previous
from video_director_v13 import read_json, write_json, check, capture, digest
from artvision_delivery_v55 import pack

OUT=ROOT/'output/artvision-hokusai-cinema-museum-v55b'
W,H,FPS=1080,1920,24
TITLE='The Great Wave'
ARTIST='Katsushika Hokusai'
MUSEUM_PAGE='https://www.metmuseum.org/art/collection/search/45434'
MET_IMAGE='https://images.metmuseum.org/CRDImages/as/original/DP130155.jpg'
PAPER_CM=(37.9,25.7)
FRAME_NOTE='Contemporary neutral conservation-style reconstruction; NOT historical or a photograph of a Met gallery.'
SLUG='ARTVISION_KATSUSHIKA_HOKUSAI_CINEMA_MUSEUM_V55B_REVIEW'

def font(size,serif=False):
    paths=('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf' if serif else
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(paths,size)

def draw_text(d,xy,label,size,fill,anchor=None,serif=False):
    d.text(xy,label,font=font(size,serif),fill=fill,anchor=anchor)

def real_print_bounds(art_width):
    """Dimensions: documented paper 37.9x25.7cm; white paper shown undistorted."""
    return (int(art_width),round(art_width*PAPER_CM[1]/PAPER_CM[0]))

def gallery(art):
    """A labeled display reconstruction on a softly lit wall, NOT a fake Met photo."""
    w,h=2160,3840
    # Wall is gently uneven in luminance and warm in colour. No copied artwork pixels.
    xs=np.linspace(-1,1,w,dtype=np.float32)[None,:]
    ys=np.linspace(-1,1,h,dtype=np.float32)[:,None]
    glow=17*np.exp(-((xs*.9)**2+(ys+.23)**2)*1.9)
    spatial=2.7*np.sin(xs*12+ys*5)+1.7*np.sin(ys*16-xs*8)
    base=(199+glow+spatial-8*ys).clip(0,255).astype(np.uint8)
    wall=np.empty((h,w,3),dtype=np.uint8)
    wall[:,:,0]=base
    wall[:,:,1]=(base.astype(np.int16)-8).clip(0,255)
    wall[:,:,2]=(base.astype(np.int16)-18).clip(0,255)
    room=Image.fromarray(wall,'RGB')
    del wall,base
    d=ImageDraw.Draw(room)
    # Restful wall material and architectural reveal; never an empty corridor.
    d.rectangle((0,3100,w,3130),fill=(111,104,96))
    d.rectangle((0,3130,w,3200),fill=(154,145,132))
    d.rectangle((0,3200,w,h),fill=(112,105,98))
    for y in range(3210,h,85):
        d.line((0,y,w,y),fill=(116,109,101),width=2)
    # Print width 780 px on a 2160 px wall, so exact paper/room scale is plausible.
    paper_w,paper_h=real_print_bounds(780)
    x0=(w-paper_w)//2
    y0=1510-paper_h//2
    image=ImageOps.exif_transpose(art).convert('RGB')
    image=image.resize((paper_w,paper_h),Image.Resampling.LANCZOS)
    # Modern display: no undocumented antique gold frame. Matte 82px and wood edge 20px.
    mount=92
    border=24
    mat_box=(x0-mount,y0-mount,x0+paper_w+mount,y0+paper_h+mount)
    box=(mat_box[0]-border,mat_box[1]-border,mat_box[2]+border,mat_box[3]+border)
    # Soft contact shadow for a physical object mounted in the room.
    shadow=Image.new('RGBA',(w,h),(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((box[0]+22,box[1]+30,box[2]+26,box[3]+34),radius=7,fill=(26,23,22,132))
    shadow=shadow.filter(ImageFilter.GaussianBlur(43))
    room=Image.alpha_composite(room.convert('RGBA'),shadow)
    d=ImageDraw.Draw(room)
    d.rounded_rectangle(box,radius=6,fill=(58,48,36,255))
    d.rectangle((box[0]+7,box[1]+7,box[2]-7,box[3]-7),outline=(132,116,95,255),width=10)
    d.rectangle(mat_box,fill=(234,227,211,255))
    d.rectangle((mat_box[0]+6,mat_box[1]+6,mat_box[2]-6,mat_box[3]-6),
                outline=(211,203,189,255),width=5)
    d.rectangle((x0-4,y0-4,x0+paper_w+4,y0+paper_h+4),fill=(86,81,73,255))
    room.paste(image,(x0,y0))
    # Subtle exhibition label, outside the print, never implying this room is real.
    d=ImageDraw.Draw(room)
    px=box[2]+65
    py=y0+50
    d.line((px,py,px+265,py),fill=(124,114,104,255),width=2)
    draw_text(d,(px,py+26),'KATSUSHIKA HOKUSAI',26,(54,51,48,255))
    draw_text(d,(px,py+70),'The Great Wave',28,(45,44,42,255),serif=True)
    draw_text(d,(px,py+115),'c. 1830–32  |  JP1847',19,(70,65,59,255))
    draw_text(d,(px,py+149),'25.7 x 37.9 cm',20,(70,65,59,255))
    draw_text(d,(px,py+191),'DISPLAY RECONSTRUCTION',17,(96,85,76,255))
    return room.convert('RGB'),(x0,y0,x0+paper_w,y0+paper_h),box

def branding(original):
    img=original.convert('RGBA')
    layer=Image.new('RGBA',img.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    w,h=img.size
    draw.rounded_rectangle((110,h-860,w-110,h-270),radius=36,fill=(10,14,19,221))
    title_font=font(94,serif=True)
    while draw.textbbox((0,0),TITLE,font=title_font)[2] > w-330 and title_font.size>50:
        title_font=font(title_font.size-2,serif=True)
    draw_text(draw,(w//2,h-670),TITLE,title_font.size,(245,241,231,255),anchor='mm',serif=True)
    draw.line((240,h-555,w-240,h-555),fill=(195,175,139,255),width=6)
    draw_text(draw,(w//2,h-445),ARTIST.upper(),49,(234,224,206,255),anchor='mm')
    return Image.alpha_composite(img,layer).convert('RGB')

def secure_detail(art,focus,mode='detail'):
    im=ImageOps.exif_transpose(art).convert('RGB')
    if mode=='whole':
        out=Image.new('RGB',(W,H),(19,23,27))
        im.thumbnail((W-70,H-300),Image.Resampling.LANCZOS)
        out.paste(im,((W-im.width)//2,(H-im.height)//2))
        return out
    ratio=W/H
    iw,ih=im.size
    if min(iw,ih)<800:raise ValueError('Met original too small for close detail')
    # Preserve source pixels and legitimate crops only.
    crop_h=min(ih,int(iw/ratio));crop_w=min(iw,int(crop_h*ratio))
    cx,cy=focus
    x=max(0,min(iw-crop_w,int(cx*iw-crop_w/2)))
    y=max(0,min(ih-crop_h,int(cy*ih-crop_h/2)))
    return im.crop((x,y,x+crop_w,y+crop_h)).resize((W,H),Image.Resampling.LANCZOS)

def prepare():
    if OUT.exists():raise RuntimeError('Existing Museum output; do not overwrite')
    previous.DEST=OUT
    dossier,std_folder,assets,art,music,url=previous.prep()
    previous.make_four(dossier)
    previous.make_project(std_folder,dossier,art,music,url)
    museum_folder=OUT/'cinema_museum'
    (museum_folder/'assets').mkdir(exist_ok=True)
    for p in assets.iterdir():
        if p.is_file():shutil.copy2(p,museum_folder/'assets'/p.name)
    project=read_json(std_folder/'PROJECT_V13.json')
    project['artvision_4x1_variant']='cinema_museum'
    project['status']='prepared'
    project['assets']=[{**a,'file':'assets/'+Path(a['file']).name} for a in project['assets']]
    project['scenes']=[
      {'asset_id':'met_art',
       'description':'Opening in a deliberately reconstructed museum display, with the exact Met original visibly framed at real aspect.',
       'reason':'Make the artwork physical scale clear before entering the immense printed wave.'},
      *project['scenes'],
      {'asset_id':'met_art','description':'Return to the exact same virtual wall and modern frame seen at the start.',
       'reason':'Conclude with the contrast between the small physical print and the emotional vastness of its image.'},
    ]
    project['editorial_plan']['subject_insight']='Museum fiction is explicitly labeled and the exact 25.7x37.9cm physical print scale drives the room; not a Met gallery photograph.'
    project['editorial_plan']['mix_reason']='Start at a consistent constructed gallery, enter original print details then return to the identical display, music only.'
    write_json(museum_folder/'PROJECT_V13.json',project)
    state=check(museum_folder/'PROJECT_V13.json')
    if not state['ready']:raise RuntimeError('Museum V13 preflight: '+json.dumps(state['blockers'],ensure_ascii=False))
    subprocess.run([sys.executable,'src/video_director_v13.py','four-check','--plan',str(dossier)],
                   cwd=ROOT,check=True)
    return dossier,museum_folder,museum_folder/'assets'/art.name,museum_folder/'assets'/music.name

def encode(out,stills,music,scene):
    """Each shot has unique, purposeful source still and motion range."""
    durations=[s['duration'] for s in scene]
    args=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y']
    for p,s in zip(stills,scene):
        args += ['-loop','1','-framerate',str(FPS),'-t',str(s['duration']),'-i',str(p)]
    args += ['-stream_loop','-1','-i',str(music)]
    filters=[]
    for i,s in enumerate(scene):
        dur=s['duration'];za,zb=s['zoom']
        # zoompan uses current *output* frame index, with a subtle ease.
        z=f"({za}+({zb}-{za})*on/{max(1,round(dur*FPS)-1)})"
        # Museum camera must approach the *painting centre*, not an empty
        # geometric wall centre. The same anchor is used on retreat.
        yexpr=('max(0,min(ih-ih/zoom,1510-ih/zoom/2))'
               if s['name'].startswith('museum_') else 'ih/2-ih/zoom/2')
        filters.append(f'[{i}:v]scale=2160:3840:flags=lanczos,zoompan=z=\'{z}\':x=\'iw/2-iw/zoom/2\':y=\'{yexpr}\':d=1:fps={FPS}:s={W}x{H},trim=duration={dur},setpts=PTS-STARTPTS[v{i}]')
    filters.append(''.join(f'[v{i}]' for i in range(len(scene)))+f'concat=n={len(scene)}:v=1:a=0[v]')
    total=sum(durations)
    args += ['-filter_complex',';'.join(filters),'-map','[v]','-map',f'{len(scene)}:a:0',
             '-t',str(total),'-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','21',
             '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
             '-af',f'afade=t=in:st=0:d=0.25,afade=t=out:st={total-1.7}:d=1.7',
             '-movflags','+faststart',str(out)]
    subprocess.run(args,check=True,timeout=2400)
    return total

def verify(video,cover,out,paper,met_sha):
    from artvision_delivery_v55 import inspect_video
    info=inspect_video(video)  # full decode 0 errors
    assert (info['width'],info['height'])==(1080,1920)
    if digest(video)==previous.MUSIC_SHA or digest(video)==met_sha:
        raise RuntimeError('Video is not an original render')
    # Only demonstrates the stored gallery source, not full artistic review.
    test=Image.open(out/'GALLERY_RECONSTRUCTION_ORIGINAL.jpg')
    if test.size!=(2160,3840):raise RuntimeError('Room construction wrong resolution')
    for t in (0.1,1,3,5,7):
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(t),'-i',str(video),
                        '-frames:v','1',str(out/f'FRAME_{str(t).replace(".","_")}S.jpg')],
                       check=True,timeout=60)
    return info

def outputs(dossier,folder,art_file,music_file):
    out=OUT/'rendered'
    out.mkdir(exist_ok=False)
    with Image.open(art_file) as image:
        art=image.convert('RGB')
    real_ratio=art.width/art.height
    if abs(real_ratio-(PAPER_CM[0]/PAPER_CM[1]))>.09:
        # Some museum scans include margins; resize without changing painting content.
        raise RuntimeError('Met image aspect unexpectedly differs from documented print')
    room,paper,outer=gallery(art)
    room.save(out/'GALLERY_RECONSTRUCTION_ORIGINAL.jpg',quality=94,subsampling=0)
    frames=out/'SCENE_IMAGES'
    frames.mkdir()
    pictures=[
       branding(room),
       room,
       secure_detail(art,(.28,.38)),
       secure_detail(art,(.32,.72)),
       secure_detail(art,(.57,.74)),
       secure_detail(art,(.58,.27)),
       secure_detail(art,(.50,.50),'whole'),
       room,
       room,
    ]
    scene=[
      {'name':'museum_open_title','duration':3.4,'zoom':(1.10,1.16)},
      {'name':'museum_real_scale_approach','duration':4.8,'zoom':(1.16,2.22)},
      {'name':'crest_blue_foam','duration':4.8,'zoom':(1.0,1.025)},
      {'name':'boats_under_wave','duration':5.4,'zoom':(1.0,1.026)},
      {'name':'mount_fuji','duration':5.1,'zoom':(1.015,1.0)},
      {'name':'crest_revisit','duration':4.7,'zoom':(1.0,1.03)},
      {'name':'full_authentic_print','duration':5.7,'zoom':(1.0,1.0)},
      {'name':'museum_return_same_room','duration':5.0,'zoom':(2.22,1.16)},
      {'name':'museum_exit_original_view','duration':3.8,'zoom':(1.16,1.10)},
    ]
    paths=[]
    for i,img in enumerate(pictures):
        p=frames/f'{i:02}.jpg';img.save(p,quality=93,subsampling=0);paths.append(p)
    cover=out/'COPERTINA.jpg'
    with Image.open(paths[0]) as opening:
        opening.resize((W,H),Image.Resampling.LANCZOS).save(cover,quality=96,subsampling=0)
    film=out/(SLUG+'.mp4')
    duration=encode(film,paths,music_file,scene)
    info=verify(film,cover,out,paper,digest(art_file))
    rights=out/'SOURCES_AND_RIGHTS.md'
    rights.write_text(
      '# Katsushika Hokusai — The Great Wave, Cinema Museum V55\n\n'
      'Authentic printed artwork: The Metropolitan Museum of Art, JP1847 (c.1830–32), '
      'Open Access / public domain, official https://www.metmuseum.org/art/collection/search/45434. '
      'Exact original image URL: '+MET_IMAGE+'.\n'
      'Downloaded exact bytes SHA256: '+digest(art_file)+'.\n'
      'Documented paper size: 25.7 × 37.9 cm, horizontal. '
      'Modern neutral conservation-style frame and warm museum room are ORIGINAL ARTISTIC RECONSTRUCTIONS, '
      'not an actual photograph or a historical frame. The actual historical frame is undocumented. '
      'No location at the Met is depicted or asserted. '
      'Opening and ending use the same reconstructed wall, neutral mat and print.\n\n'
      'Music: Water Lily, Kevin MacLeod (ISRC USUAN1400035), original recording '
      'https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035. '
      'CC BY 4.0 https://creativecommons.org/licenses/by/4.0/. '
      'Exact original audio SHA256 '+digest(music_file)+'.\n'
      'Territorial rights/platform copyright review pending before release.\n',encoding='utf8')
    captions={
      'facebook':'Quanto può essere grande un quadro piccolo? The Great Wave di Katsushika Hokusai misura, in questa stampa del Met, appena 25,7 × 37,9 cm. In questa interpretazione Cinema Museum entriamo in una sala immaginata, osserviamo la stampa e attraversiamo dettagli originali: l’onda, le barche, il Fuji lontano. Sala e cornice moderne sono ricostruzioni, non la sala reale del museo. Opera: Met JP1847, pubblico dominio. Musica: Water Lily di Kevin MacLeod, CC BY 4.0.',
      'instagram':'🌊 Un foglio di carta largo 37,9 cm. Un oceano impossibile da contenere. Nel nostro Cinema Museum di Hokusai partiamo dalla scala reale della stampa, poi scopriamo le barche, la schiuma e il piccolo Monte Fuji. Sala e cornice ricostruite artisticamente; immagine originale The Great Wave, Met Open Access JP1847. 🎵 Water Lily — Kevin MacLeod, CC BY 4.0 (incompetech.com). #Hokusai #MuseumImmersion #LaGrandeOnda #ArtVision',
      'tiktok':'Un oceano dentro una stampa di 38 centimetri? 👀 Ingresso nella sala museale ricostruita, poi nei dettagli autentici della Grande onda di Hokusai. Guarda dove si nasconde il Fuji! Il museo in video è una ricostruzione, non una ripresa del Met. Stampa JP1847, Metropolitan Museum Open Access / pubblico dominio. Water Lily — Kevin MacLeod, CC BY 4.0, incompetech.com. #ArtTok #Hokusai #TheGreatWave',
      'youtube':'The Great Wave — Katsushika Hokusai | Cinema Museum Immersion. Questa versione propone una prospettiva museale originale sulla stampa del Metropolitan Museum of Art JP1847 (c.1830–1832, 25,7 × 37,9 cm): ingresso nella sala ricostruita, osservazione della scala fisica, scoperta dei tre battelli sotto l’onda e uscita dalla stessa parete. Sala, supporto e cornice moderna NON sono fotografie o elementi storici documentati. L’immagine dell’opera è autentica (Met Open Access, pubblico dominio). Colonna musicale: Water Lily di Kevin MacLeod, registrazione CC BY 4.0, fonte incompetech.com, licenza creativecommons.org/licenses/by/4.0/. Nessuna ricostruzione è presentata come prova storica.'
    }
    postfiles={}
    for key,txt in captions.items():
        p=out/('POST_'+key.upper()+'.txt');p.write_text(txt+'\n',encoding='utf8');postfiles[key]=p
    recipe=capture('artvision_cinema',TITLE,film,cover,out,
      sources=[art_file,music_file,dossier,folder/'PROJECT_V13.json',rights,
               ROOT/'scripts/artvision_hokusai_cinema_museum_v55.py'])
    rpath=out/'VIDEO_RECIPE_V13.json'
    recipe.update({'variant':'cinema_museum','review_state':'rendered_needs_review',
      'gallery_kind':'artistically reconstructed, not actual Met gallery',
      'room_image_sha256':digest(out/'GALLERY_RECONSTRUCTION_ORIGINAL.jpg'),
      'physical_print_cm':{'width':37.9,'height':25.7},
      'frame_status':FRAME_NOTE,
      'opening_and_exit_share_identical_room_image':True,
      'scene_timeline':scene,'music_sha256':digest(music_file),
      'artistic_review':'pending_normal_speed_watch_and_listen','V25_approved':False,
      'site_status':'archive_sync_pending',
      'technical_decode':info})
    write_json(rpath,recipe)
    packdir=OUT/'V55_DELIVERY'
    package=pack(film,cover,postfiles,rights,rpath,packdir)
    android=packdir/(SLUG+'_ANDROID_ONLY.zip')
    with zipfile.ZipFile(android,'w',allowZip64=True) as z:
        z.write(film,film.name,compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(android) as z:
        if z.testzip() is not None:raise RuntimeError('Android ZIP CRC failed')
    release={'state':'rendered_needs_review','sha256':digest(film),'size_bytes':film.stat().st_size,
             'duration_seconds':duration,'technical':info,
             'gallery_reconstructed':True,'archived':False,'V25_approved':False,
             'human_full_speed_watch':False,'social_published':False,'paid_video_credits':0,
             'delivery':package}
    write_json(OUT/'RELEASE_STATE_V55.json',release)
    print('HOKUSAI_CINEMA_MUSEUM_REAL_MP4',json.dumps(
        {'video':str(film),'video_sha256':digest(film),
         'bytes':film.stat().st_size,'duration':duration,
         'review':'rendered_needs_review','new_distinct_variant':True,
         'zero_paid_services':True,'archive':'archive_sync_pending'},ensure_ascii=False),flush=True)
    return film

def main():
    dossier,folder,art,music=prepare()
    outputs(dossier,folder,art,music)

if __name__=='__main__':
    main()
