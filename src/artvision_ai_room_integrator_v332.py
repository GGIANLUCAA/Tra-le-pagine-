#!/usr/bin/env python3
"""ArtVision V332: reuse owner-approved AI gallery *staging* without pretending it is a historical museum.

Uses exact artwork bytes; prefers the actual photographed frame for the exact
specimen. Both Cinema Museum and Critico Museum lock the same room/frame. This
makes a front-on still/proof (and optional silent geometric preview), NOT a
physical 3D room or an artistic/GOLD master. Does not touch original videos.

Example:
 python artvision_ai_room_integrator_v332.py --catalog catalog.json --assets-dir /mnt/data \
   --painting SOURCE.jpg --width-cm 162 --height-cm 117 --moods dramatic,baroque \
   --authentic-frame-photo FRAME.jpg --frame-source-url https://commons.wikimedia.org/wiki/File:... \
   --frame-license 'CC BY 3.0' --variant critico_museum --out-dir /tmp/pilot
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFilter

SCHEMA='artvision-reusable-ai-room-library-v332'
PALETTE={
 'gilt':('#4b3215','#c49a3d','#f1d482','#81602b'),
 'dark_wood':('#241813','#654127','#8d653e','#302016'),
 'bronze':('#262b29','#68665b','#a7a28c','#3d413b'),
 'minimal_black':('#121315','#414244','#747576','#232426'),
}


def sha256_file(path: Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as fh:
        for part in iter(lambda:fh.read(1024*1024),b''):h.update(part)
    return h.hexdigest()


def load_catalog(path):
    data=json.loads(Path(path).read_text(encoding='utf8'))
    if data.get('schema')!=SCHEMA or len(data.get('scenes',[]))<10:
        raise ValueError('Catalog schema or number of rooms invalid')
    return data


def select_gallery(catalog,art_width_cm,art_height_cm,moods,locked_room_id=None,exclude=None):
    """Deterministic, physically sized choice; lock the SAME id for critic/cinema.

    A target room is never automatically 'historically accurate' or 'approved'.
    """
    if min(art_width_cm,art_height_cm)<=0:raise ValueError('Artwork dimensions cm required')
    moods={v.strip().lower() for v in moods if v.strip()}
    exclude=set(exclude or ())
    choices=[]
    for room in catalog['scenes']:
        if room['status']!='candidate_ready_for_compositing_review':continue
        if room.get('frame_in_background'):continue
        if locked_room_id and room['room_id']!=locked_room_id:continue
        # Approximate field of view: no stretching to fit an undersized gallery.
        d=room['design_camera_distance_cm']
        fov=math.radians(room['projection_horizontal_fov_degrees'])
        wall_visible_cm=2*d*math.tan(fov/2)
        width_fraction=art_width_cm*1.13/wall_visible_cm
        safe=room['safe_wall_box_norm']
        if width_fraction>safe[2]-safe[0]+.04:continue
        overlap=len(moods.intersection(room['mood_tags']))
        preferred=[m for m in room['mood_tags'] if m in moods]
        score=overlap*10 - (15 if room['room_id'] in exclude else 0)
        # Minor preference for artwork occupying a convincing portion of the wall.
        score-=abs(width_fraction-.42)*4
        choices.append((score,room['room_id'],room,preferred))
    if not choices:
        raise ValueError('No safe wall size for this painting; use a different calibrated room or camera distance')
    choices.sort(key=lambda t:(-t[0],t[1]))
    return choices[0][2],choices[0][3]


def crop_center_to_aspect(image,width,height):
    """No stretching of architectural features if incoming aspect differs."""
    return ImageOps.fit(image.convert('RGB'),(width,height),Image.Resampling.LANCZOS,centering=(.5,.5))


def recommend_editorial_frame_style(moods):
    """Select a restrained frame family by subject mood when original is absent."""
    moods={str(m).strip().lower() for m in moods}
    if moods.intersection({'modern','minimal','abstract','contemporary'}):
        return 'minimal_black'
    if moods.intersection({'gothic','dark','somber','tragic','grief','horror'}):
        return 'dark_wood'
    if moods.intersection({'mythology','moonlight','dream','mystical','sea'}):
        return 'bronze'
    if moods.intersection({'classical','renaissance','baroque','historic','epic','monumental'}):
        return 'gilt'
    return 'dark_wood'

def color(hexv):return tuple(bytes.fromhex(hexv[1:]))


def make_editorial_frame(painting,style='gilt',border_fraction=.095):
    """An *editorial* frame, explicitly NOT the original frame.

    Reasonably realistic layered bevel. Not a substitute for a genuine framed
    photograph and always requires artistic approval to ship in Museum.
    """
    if style not in PALETTE:raise ValueError('Unknown editorial frame family')
    image=painting.convert('RGB')
    w,h=image.size
    if min(w,h)<100:raise ValueError('Painting too small')
    border=max(10,int(min(w,h)*border_fraction))
    ow,oh=w+2*border,h+2*border
    frame=Image.new('RGB',(ow,oh));dr=ImageDraw.Draw(frame)
    p=PALETTE[style]
    dr.rectangle((0,0,ow-1,oh-1),fill=color(p[0]))
    # Insets model a modest historic profile with side-specific lighting.
    for step,shade in ((0,p[0]),(.18,p[1]),(.33,p[2]),(.52,p[1]),(.75,p[3]),(.90,p[0])):
        j=int(border*step)
        dr.rectangle((j,j,ow-j-1,oh-j-1),outline=color(shade),width=max(2,int(border*.13)))
    frame.paste(image,(border,border))
    return frame


def mount_on_wall(room_image,frame_image,art_cm,frame_cm,room):
    """Stage from documented artwork dimensions, a *design* camera distance and FOV.

    Keeps an exact rectangle and a single central camera axis. These synthetic
    rooms have no calibrated physical floor/wall depth: output is a REVIEW only.
    """
    W,H=room_image.size
    rect=room['safe_wall_box_norm']
    left,top,right,bottom=[int(v*d) for v,d in zip(rect,(W,H,W,H))]
    if right<=left or bottom<=top:raise ValueError('Invalid safe-wall box')
    width_cm,height_cm=frame_cm
    if width_cm<art_cm[0] or height_cm<art_cm[1]:raise ValueError('Outer frame cannot be smaller than painting')
    distance_cm=room['design_camera_distance_cm']
    tan=math.tan(math.radians(room['projection_horizontal_fov_degrees'])/2)
    desired=int(W*width_cm/(2*distance_cm*tan))
    # Real frame/photo aspect is untouched. The source is not stretched to match an invented size.
    aspect=frame_image.width/frame_image.height
    allowed_width=max(1,right-left)
    allowed_height=max(1,bottom-top)
    actual_width=min(desired,allowed_width,int(allowed_height*aspect))
    if actual_width<24:raise ValueError('Frame unworkably tiny at its real scale')
    actual_height=round(actual_width/aspect)
    # An edited viewing distance is always disclosed, not a silent scale distortion.
    effective_distance_cm=round(W*width_cm/(2*actual_width*tan),1)
    fx=(left+right)//2;fy=(top+bottom)//2
    x=fx-actual_width//2;y=fy-actual_height//2
    if x<left or y<top or x+actual_width>right+1 or y+actual_height>bottom+1:
        raise ValueError('Proposed frame intersects architecture or bench')
    patch=frame_image.resize((actual_width,actual_height),Image.Resampling.LANCZOS)
    scene=room_image.convert('RGBA')
    # Soft wall contact shadow, not a virtual second frame.
    shadow=Image.new('RGBA',scene.size,(0,0,0,0))
    sh=Image.new('RGBA',(actual_width,actual_height),(0,0,0,65))
    shadow.paste(sh,(x+7,y+9));shadow=shadow.filter(ImageFilter.GaussianBlur(11))
    scene=Image.alpha_composite(scene,shadow)
    scene.paste(patch,(x,y))
    return scene.convert('RGB'),{'frame_pixel_box':[x,y,x+actual_width,y+actual_height],
        'frontality':'front_facing_non_skewed_rectangle','frame_pixel_ratio':round(actual_width/actual_height,6),
        'estimated_camera_distance_cm':effective_distance_cm,
        'original_design_distance_cm':distance_cm,
        'physical_scale_status':'ESTIMATED_DESIGN_NO_MUSEUM_3D_CALIBRATION',
        'no_permanent_museum_claim':True}


def assemble(catalog_path,assets_dir,painting_path,out_dir,art_width_cm,art_height_cm,moods,
             variant,room_id=None,prev_rooms=None,authentic_frame_photo=None,
             frame_source_url=None,frame_license=None,frame_style='auto',allow_editorial=False,
             frame_outer_cm=None,verified_frame_type='current_documented',
             original_frame_evidence_url=None):
    catalog=load_catalog(catalog_path)
    if variant not in ('cinema_museum','critico_museum'):
        raise ValueError('Only the two Museum variants use these rooms')
    if min(float(art_width_cm),float(art_height_cm))<=0:
        raise ValueError('Artwork measurements must come from museum catalogue')
    room,matched=select_gallery(catalog,art_width_cm,art_height_cm,moods,room_id,prev_rooms)
    image_path=Path(assets_dir)/room['original_generated_filename']
    if not image_path.is_file():
        image_path=Path(assets_dir)/room['file_name']
    if not image_path.is_file():raise FileNotFoundError(f'Room asset {room["room_id"]} missing, materialize from Library')
    if sha256_file(image_path)!=room['sha256']:
        raise ValueError('Room asset SHA mismatch: fail closed, no silent asset substitution')
    room_image=Image.open(image_path)
    painting_path=Path(painting_path)
    painting=Image.open(painting_path).convert('RGB')
    aspect=art_width_cm/art_height_cm
    if abs(painting.width/painting.height/aspect-1)>.065:
        raise ValueError('Artwork pixels mismatch official artwork aspect ratio: use faithful source')
    if authentic_frame_photo:
        if not frame_source_url or not frame_source_url.startswith('https://') or not frame_license:
            raise ValueError('Documented current frame requires verifiable source URL + rights')
        patch=Image.open(authentic_frame_photo).convert('RGB')
        frame_kind=verified_frame_type
        if frame_kind not in ('current_documented','original_documented','historic_documented'):
            raise ValueError('Unknown documented frame kind')
        # A museum photograph of the current frame is NOT proof that the
        # artist chose it or that it is historically original.
        if frame_kind == 'original_documented':
            if not original_frame_evidence_url or not str(original_frame_evidence_url).startswith('https://'):
                raise ValueError('Original frame claim requires separate verifiable historical provenance')
        # The documented frame photo must not be an arbitrary crop that
        # contains another room/side-on view. Artistic frontality QA still required.
        # If no measured outer dimensions exist, use conservative estimate with explicit disclosure.
        if frame_outer_cm is None:
            estimated_width=art_width_cm*1.11
            estimated_height=estimated_width/(patch.width/patch.height)
            if estimated_height<art_height_cm:estimated_height=art_height_cm*1.11;estimated_width=estimated_height*(patch.width/patch.height)
            frame_cm=(estimated_width,estimated_height)
            frame_dimensions_status='ESTIMATED_NOT_MUSEUM_MEASURED'
        else:
            frame_cm=frame_outer_cm
            frame_dimensions_status='DOCUMENTED_OUTER_SIZE_AS_SUPPLIED_PENDING_SOURCE_CHECK'
        if abs((patch.width/patch.height)/(frame_cm[0]/frame_cm[1])-1)>.07:
            raise ValueError('Documented source frame patch aspect ratio inconsistent with supplied frame size')
        source_frame_sha=sha256_file(Path(authentic_frame_photo))
        frame_source_disclosure='Exact existing documented frame photo on artwork, not proof of original historical 16th-century frame'
    else:
        if not allow_editorial:
            raise ValueError('Authentic framed photo absent: explicit editorial fallback approval required')
        frame_style=recommend_editorial_frame_style(moods) if frame_style=='auto' else frame_style
        patch=make_editorial_frame(painting,frame_style)
        frame_kind='editorial_scenographic_not_historical'
        frame_source_url=None;frame_license=None;source_frame_sha=None
        frame_cm=(art_width_cm*(patch.width/painting.width),art_height_cm*(patch.height/painting.height))
        frame_dimensions_status='DESIGNED_FRAME_NOT_ORIGINAL'
        frame_source_disclosure='Editorial frame matching painting mood. Do NOT claim it is real specimen frame; owner review pending.'
    work=room_image
    canvas,geometry=mount_on_wall(work,patch,(art_width_cm,art_height_cm),frame_cm,room)
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    target=out_dir/(variant+'_'+room['room_id']+'_REVIEW.png')
    if target.exists():raise FileExistsError(target)
    canvas.save(target)
    report={'schema':'artvision-ai-gallery-review-v332','variant':variant,
        'source_gallery':room['room_id'],'room_file':image_path.name,
        'room_library_path':room['library_path'],'room_sha256':room['sha256'],
        'room_is_ai_generated_scenography':True,'room_is_real_museum':False,
        'source_artwork_sha256':sha256_file(painting_path),
        'official_artwork_cm':[art_width_cm,art_height_cm],
        'frame_status':frame_kind,'frame_source_url':frame_source_url,'frame_source_license':frame_license,
        'frame_source_sha256':source_frame_sha,'frame_dimensions_status':frame_dimensions_status,
        'original_frame_historical_evidence_url':original_frame_evidence_url if frame_kind=='original_documented' else None,
        'frame_source_disclosure':frame_source_disclosure,'editorial_frame_family':frame_style if frame_kind=='editorial_scenographic_not_historical' else None,
        'moods':list(moods),'matched_tags':matched,
        'paired_variants_lock':'Use the same room_id, authentic frame/source, and art source in both Museum versions',
        'existing_standard_video_untouched':True,'same_original_narration_required':True,
        'same_original_cinema_music_required':True,'camera_motion':'STILL_SAMPLE_NOT_3D',
        'new_audio_generated':False,'paid_api_calls':0,'social_publish':False,
        'museum_approved':False,'Gold_V25':False,'full_speed_video_qa':'NOT_PERFORMED',
        'geometry':geometry,'output_image_sha256':sha256_file(target)}
    qa=out_dir/(variant+'_'+room['room_id']+'_QA.json')
    qa.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'
',encoding='utf8')
    return target,report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--catalog',type=Path,required=True)
    p.add_argument('--assets-dir',type=Path,required=True)
    p.add_argument('--painting',type=Path,required=True)
    p.add_argument('--width-cm',type=float,required=True)
    p.add_argument('--height-cm',type=float,required=True)
    p.add_argument('--moods',default='historic')
    p.add_argument('--room-id')
    p.add_argument('--exclude-room',action='append',default=[])
    p.add_argument('--authentic-frame-photo',type=Path)
    p.add_argument('--frame-source-url')
    p.add_argument('--frame-license')
    p.add_argument('--verified-frame-type',choices=('current_documented','original_documented','historic_documented'),default='current_documented')
    p.add_argument('--original-frame-evidence-url')
    p.add_argument('--frame-style',choices=('auto',)+tuple(PALETTE),default='auto')
    p.add_argument('--allow-editorial',action='store_true')
    p.add_argument('--variant',choices=('cinema_museum','critico_museum'),required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args()
    image,info=assemble(a.catalog,a.assets_dir,a.painting,a.out_dir,a.width_cm,a.height_cm,
        [s.strip() for s in a.moods.split(',')],a.variant,a.room_id,a.exclude_room,
        a.authentic_frame_photo,a.frame_source_url,a.frame_license,a.frame_style,a.allow_editorial,
        verified_frame_type=a.verified_frame_type,original_frame_evidence_url=a.original_frame_evidence_url)
    print(json.dumps({'result':'PHOTO_SCENOGRAPHY_REVIEW_ONLY','png':str(image),
                      'room_id':info['source_gallery'],'frame':info['frame_status'],
                      'sha256':info['output_image_sha256'],'museum_approved':False},ensure_ascii=False))

if __name__=='__main__':main()