#!/usr/bin/env python3
"""V236: source-locked actual 1915 portrait recut; 4 photo inputs + 1 Vidu anchor.
Manually chosen from twelve original V217 frames, not an automated pixel score.
Never approves shots, rights, photos or finished episodes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

FILM_SHA = '6b73739ef20bcacd2f43c11ab0970204a8e920b8048c16c251fef319539f5d14'
EPISODE = 'lusitania_departure_1915_v220'
SOURCE_PAGE = 'https://commons.wikimedia.org/wiki/File:Passengers_arriving_for_the_RMS_Lusitania,_NYC,_May_1,_1915.webm'
SHOTS = [
 ('frame_02.png','039153b4069275386fb635821ed10c3dc59f8fd55c24b192fe987ab19a66d583',702,'Passenger and porter at car, hands visible, dock-side luggage','I2I'),
 ('frame_03.png','a9cc2d4105bb4c1b08618842f363b3483a7f228d43e345b5970e331d23af5ceb',728,'Man in dark hat walking toward camera beside 1915 motorcars','I2I'),
 ('frame_04.png','41d47e2bfa3e2d1d6656ff526dce6b2839452f4ae2fe88a2ec5da0c81a57ff79',210,'Two men in hats facing camera, another in foreground; dock crowd','I2I'),
 ('frame_07.png','f195d35dedfece1b7c61a4d768d6d9fb1adeb1f2b10fa869446838caa95239cc',790,'Passengers in hats and deck crew beside ship railings','I2I'),
 ('frame_09.png','13ec759cef261aaaeb9d992a64fdd7a89b7b18532ff5af2534b4da03ad323b52',780,'Crew member waving flag on deck above boarding passengers','VIDU_SOURCE_ANCHOR_NO_I2I')
]
CROP_W,H,W=608,1080,1920

def sha(path:Path)->str:
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()

def prepare(cache:Path,out:Path,require_film:bool=True)->dict:
    scout=json.loads((cache/'SCOUT_REPORT.json').read_text(encoding='utf-8'))
    if (scout.get('status')!='REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW'
        or scout.get('source_page')!=SOURCE_PAGE or scout.get('original_sha256')!=FILM_SHA
        or scout.get('source_frames_extracted')!=12):
        raise ValueError('V236_REAL_SOURCE_REPORT_NOT_VERIFIED')
    if require_film:
        film=cache/'ORIGINAL_ARCHIVE.webm'
        if film.is_symlink() or not film.is_file() or sha(film)!=FILM_SHA:
            raise ValueError('V236_ORIGINAL_FILM_BYTES_CHANGED')
    period=scout.get('sampling_period_s')
    if type(period) not in (int,float) or not math.isfinite(period) or not 20<period<30:
        raise ValueError('V236_SOURCE_TIMEBASE_CHANGED')
    out.mkdir(parents=True,exist_ok=True)
    frames=out/'FOUR_PHOTO_INPUTS_ONE_VIDU_ANCHOR'
    frames.mkdir(exist_ok=True)
    rows=[]
    for name,expected,left,inventory,kind in SHOTS:
        frame=cache/'original_frames'/name
        if frame.is_symlink() or not frame.is_file() or sha(frame)!=expected:
            raise ValueError('V236_SOURCE_FRAME_SHA_MISMATCH_'+name)
        with Image.open(frame) as image:
            if image.format!='PNG' or image.size!=(W,H):
                raise ValueError('V236_SOURCE_FRAME_GEOMETRY_MISMATCH')
            image.verify()
        if left%2 or left<0 or left+CROP_W>W:
            raise ValueError('V236_PORTRAIT_CROP_OUT_OF_BOUNDS')
        with Image.open(frame) as image:
            cropped=frames/name
            image.convert('RGB').crop((left,0,left+CROP_W,H)).save(cropped)
        number=int(name[6:8]);timecode=round((number-.5)*period,3)
        rows.append({'frame':name,'original_sha256':expected,'portrait_sha256':sha(cropped),
                     'crop_left_px':left,'crop_width_px':CROP_W,'timecode_s':timecode,
                     'target_kind':kind,'verified_visible_objects':inventory,
                     'rights_italy_verified':False,'artistic_approved':False})
    report={'version':'V236_LUSITANIA_CURATED_SOURCE_REVIEW','episode_id':EPISODE,
            'source_page':SOURCE_PAGE,'original_film_sha256':FILM_SHA,
            'five_candidate_camera_views_not_yet_approved':True,
            'italian_rights_verified':False,'provider_calls_sent':0,
            'paid_credits_authorized':False,'publish_permitted':False,
            'final_episode':False,'photos_generated':0,'vidu_clips_generated':0,
            'four_i2i_inputs':4,'one_vidu_anchor':1,'shots':rows}
    (out/'V236_CURATED_SOURCE_LOCK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    selection={'version':'V210_SHOT_AWARE_PRESELECTION',
               'status':'FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW',
               'reason':'V236_MANUALLY_CURATED_ON_ACTUAL_V217_FRAMES_PENDING_FULL_MOTION_REVIEW',
               'preselected':[{'filename':x['frame']} for x in rows],
               'candidate_segment_times_s':[x['timecode_s'] for x in rows],
               'five_distinct_shots_approved':False,'provider_calls_permitted':False,
               'publish_permitted':False,'credits_spent':0}
    (out/'SHOT_AWARE_SELECTION_V236.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cache',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--allow-without-film',action='store_true',help='offline crop/hash test only')
    args=parser.parse_args()
    r=prepare(args.cache,args.out,require_film=not args.allow_without_film)
    print('V236_FIVE_REAL_FRAME_CROPS',len(r['shots']),'FOUR_I2I_INPUTS_ONE_VIDU_ANCHOR_NO_GENERATION')
if __name__=='__main__':main()
