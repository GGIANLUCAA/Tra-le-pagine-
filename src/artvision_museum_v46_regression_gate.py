#!/usr/bin/env python3
"""ArtVision Museum V46 regression gate — FAIL CLOSED for fake museum transitions.

Real approved visual references:
 * The Cyclops, Odilon Redon, SENZA STRISCE CORRETTO — Drive ref 1w9mb1N5hrGAaB870JANHoKk98MiibtpW
 * Hiroshige, Sudden Shower, Museum Scale — Drive ref 14X8_TObXEijGlBg8HuyR6ITTlPjJk0dA

Checks the actual pair of consecutive decoded frames at the *declared*
gallery->painting and painting->gallery transitions. It rejects sudden spikes while allowing genuine continuous camera movements.
It catches the fatal jump-cut regression, NOT photorealism, period framing or full artistic value.
Those need real comparison against both approved video masters plus human QA.
Do NOT change a video status to approved simply because this code passes.
No network or paid service calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

W,H=180,320
BPP=3
FRAME_BYTES=W*H*BPP
MAX_JUMP_MAD=30.0
MIN_SPIKE_RATIO=2.7
MIN_SPIKE_EXCESS=18.0
MAX_ARTWORK_RATIO_ERROR=.012
ALLOWED_AUTHENTICITY={
    "documented_current","documented_historical",
    "partial_reconstruction","scenic_reconstruction"
}

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()

def probe(video):
    cmd=['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height,avg_frame_rate','-of','json',str(video)]
    j=json.loads(subprocess.check_output(cmd,text=True,timeout=30))
    video_stream=next((s for s in j['streams'] if s['codec_type']=='video'),None)
    if not video_stream:raise ValueError('No real video stream')
    fps=video_stream.get('avg_frame_rate','24/1').split('/')
    rate=float(fps[0])/float(fps[1])
    return {'seconds':float(j['format']['duration']),
            'width':int(video_stream.get('width',0)),
            'height':int(video_stream.get('height',0)),'fps':rate}

def nearby_frames(video,center,fps):
    """Read a 0.52s real decoded sample around declared boundary."""
    start=max(0.0,float(center)-.26)
    cmd=['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
         '-ss',f'{start:.6f}','-i',str(video),
         '-t','.58','-an','-vf',f'fps={fps:.8f},scale={W}:{H}:flags=bilinear',
         '-pix_fmt','rgb24','-f','rawvideo','-']
    raw=subprocess.check_output(cmd,timeout=70)
    if len(raw)<FRAME_BYTES*5:raise ValueError('Too few actual frames around museum handoff')
    frames=[memoryview(raw)[i:i+FRAME_BYTES] for i in range(0,len(raw)-FRAME_BYTES+1,FRAME_BYTES)]
    return frames

def mad(a,b):
    if len(a)!=len(b):raise ValueError('Wrong frame shape')
    # use no external Python libraries in this checker
    return sum(abs(x-y) for x,y in zip(a,b))/len(a)

def describe_motion_discontinuity(values):
    """Distinguish a single-frame scene jump from fast BUT smooth camera motion.

    The approved Cyclops V46 master reaches RGB MAD 22.81/255 during an
    unbroken move. The new V57 pilot reaches 22.02. Both have local ratios
    near 1.05. Rejected Hokusai/Homer reach 66-130 and ratios 31-52+.
    Never infer artistic approval from this mathematical test alone.
    """
    if len(values)<4:
        raise ValueError('At least four real adjacent frame differences required')
    data=[float(x) for x in values]
    peak=max(data)
    rest=sorted(data)
    rest.remove(peak)
    m=len(rest)
    median=rest[m//2] if m%2 else (rest[m//2-1]+rest[m//2])/2
    ratio=peak/max(0.1,median)
    excess=peak-median
    cut=(peak>=MAX_JUMP_MAD and ratio>=MIN_SPIKE_RATIO
         and excess>=MIN_SPIKE_EXCESS)
    return {
        'largest_adjacent_frame_mad_rgb_255':round(peak,3),
        'median_neighbour_mad_rgb_255':round(median,3),
        'spike_ratio_vs_neighbour_median':round(ratio,3),
        'excess_over_neighbour_median':round(excess,3),
        'thresholds':{'minimum_peak':MAX_JUMP_MAD,'minimum_ratio':MIN_SPIKE_RATIO,
                      'minimum_excess':MIN_SPIKE_EXCESS},
        'isolated_hard_cut_detected':cut,
        'passed_transition_continuity':not cut,
    }

def boundary_jump(video,t,fps):
    frames=nearby_frames(video,t,fps)
    values=[mad(frames[i-1],frames[i]) for i in range(1,len(frames))]
    return {
        'timestamp_s':round(float(t),3),
        'samples':len(frames),
        **describe_motion_discontinuity(values),
    }

def validate_profile(profile):
    errors=[]
    if not isinstance(profile,dict):
        return ['Missing V46 artistic evidence profile']
    fr=profile.get('frame_research')
    if not isinstance(fr,dict):
        errors.append('frame_research missing; actual frame photography must be researched before recreation')
    else:
        if fr.get('authenticity_status') not in ALLOWED_AUTHENTICITY:
            errors.append('frame_research.authenticity_status must distinguish documented vs reconstruction')
        if not fr.get('source_urls') or not isinstance(fr['source_urls'],list):
            errors.append('frame_research.source_urls missing; record original frame source(s) or explicit search evidence')
        for name in ('photo_date_or_unknown','rights_status','evidence_notes','assumptions'):
            if not str(fr.get(name,'')).strip():
                errors.append('frame_research.'+name+' missing')
        if fr.get('authenticity_status') in {'documented_current','documented_historical'}:
            if not any(str(x).startswith('https://') for x in fr.get('source_urls',[])):
                errors.append('Documented frame requires a verifiable reference URL')
    scale=profile.get('physical_scale')
    if not isinstance(scale,dict):
        errors.append('physical_scale missing')
    else:
        w=scale.get('painting_width_cm');h=scale.get('painting_height_cm')
        if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in (w,h)):
            errors.append('painting_width_cm / painting_height_cm must be measured positive cm')
        if not str(scale.get('primary_museum_dimensions_source','')).startswith('https://'):
            errors.append('physical size primary museum URL missing')
        if not str(scale.get('human_scale_reference','')).strip():
            errors.append('Human-size person or architecture reference missing')
        if type(scale.get('camera_start_distance_m')) not in (int,float) or scale['camera_start_distance_m']<=0:
            errors.append('Actual starting camera distance in metres missing')
    refs=profile.get('reference_comparison')
    if not isinstance(refs,dict) or not refs.get('cyclops_master_compared_on_real_frames') or not refs.get('hiroshige_master_compared_on_real_frames'):
        errors.append('Real frame comparison to BOTH approved Cyclops and Hiroshige masters missing')
    qa=profile.get('artistic_visual_qa')
    needed=('photographic_room_quality','physical_frame_moulding_and_corners',
            'recessed_painting_and_contact_shadows','human_scale_and_camera_perspective',
            'gallery_entry_continuity','gallery_exit_same_room',
            'no_stretched_pixels_or_ghosting','phone_size_view_review')
    if not isinstance(qa,dict) or not all(qa.get(k) is True for k in needed):
        errors.append('Independent human V46 review missing or failed: '+','.join(k for k in needed if not isinstance(qa,dict) or qa.get(k) is not True))
    return errors

def evaluate(video,enter,leave,profile=None):
    video=Path(video)
    if not video.is_file() or video.stat().st_size<10000:raise ValueError('Actual MP4 missing')
    metadata=probe(video)
    if (metadata['width'],metadata['height'])!=(1080,1920):
        raise ValueError('ArtVision portrait movie must be real 1080x1920')
    if not 0<enter<leave<metadata['seconds']:
        raise ValueError('Transitions must be within one real video in temporal order')
    jumps={'museum_to_artwork':boundary_jump(video,enter,metadata['fps']),
           'artwork_to_same_museum':boundary_jump(video,leave,metadata['fps'])}
    blockers=[]
    for name,item in jumps.items():
        if not item['passed_transition_continuity']:
            blockers.append(f'{name}: abrupt jump {item["largest_adjacent_frame_mad_rgb_255"]}/255 is an isolated discontinuity (ratio {item["spike_ratio_vs_neighbour_median"]})')
    blockers.extend(validate_profile(profile))
    return {
      'schema':'artvision-v46-museum-regression-v56',
      'video':video.name,'video_sha256':sha256(video),'video_bytes':video.stat().st_size,
      'video_probe':metadata,'reference_models':[
        'The Cyclops — SENZA STRISCE CORRETTO (approved)',
        'Hiroshige — Museum Scale (approved)'],
      'transitions':jumps,'blockers':blockers,
      'museum_quality_gate_passed':not blockers,
      'automatic_artist_approval':False,
      'usable_as_new_museum_reference':False if blockers else None,
      'interpretation':'Numeric continuity is an automatic veto, never artistic approval. Actual full video comparison and human review remain mandatory.'
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--video',type=Path,required=True)
    ap.add_argument('--entry-cut',required=True,type=float,
                    help='Physical gallery->painting handoff in actual MP4 seconds')
    ap.add_argument('--exit-cut',required=True,type=float,
                    help='Painting->same-gallery handoff in actual MP4 seconds')
    ap.add_argument('--profile',type=Path,help='Real V46 visual comparison/physical frame research JSON')
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    profile=json.loads(args.profile.read_text(encoding='utf-8')) if args.profile else None
    result=evaluate(args.video,args.entry_cut,args.exit_cut,profile)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if not result['museum_quality_gate_passed']:
        raise SystemExit(2)

if __name__=='__main__':main()
