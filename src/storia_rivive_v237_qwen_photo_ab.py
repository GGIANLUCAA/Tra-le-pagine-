#!/usr/bin/env python3
"""V237: ONE anonymous/free Qwen I2I attempt on real V236 Lusitania frame_04.
Provider A/B against REJECTED Finegrain, never a final restoration or Vidu permission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageStat

EPISODE = 'lusitania_departure_1915_v220'
SOURCE_SHA256 = '716a886ab8583f87d2f9c28e7cb7a236f4243f029e95f29e2cfed85ddf029f10'
SOURCE_SIZE = (608,1080)
PRIOR_SHA256 = '21544bcbf9acb39577141ad9a4ac1c8f7c4da183acc74932dcffd76ff20733a4'
SPACE = 'kulkas2pintu/QWEN_EDIT_IMAGE'
PROMPT = (
    'Restore and colorize this EXACT black-and-white documentary film frame from '
    'New York 1915 into a sharp, photorealistic natural-daylight photograph. '
    'Preserve the EXACT original scene, camera position, number and locations of '
    'all people, their faces, expressions, gaze, hats, suits, hands, luggage, '
    'awnings, building and dock structures. Two men in dark suits and brimmed hats '
    'face the camera at left/center; a third adult man is partially cropped at '
    'right foreground; crowd and dark awning behind. Preserve every silhouette. '
    'Do not replace faces or invent people, vehicles, fingers, or objects. '
    'Natural restrained neutral daylight, detailed cloth and skin, accurate '
    'historical 1915 materials, no orange, sepia, magenta, oversaturation, '
    'beauty filter, plastic skin, or cinematic re-lighting. No text or logos.'
)

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def check_source(source:Path, prior:Path)->dict:
    if source.is_symlink() or prior.is_symlink() or not source.is_file() or not prior.is_file():
        raise ValueError('V237_SOURCE_OR_BASELINE_MISSING')
    if sha(source)!=SOURCE_SHA256 or sha(prior)!=PRIOR_SHA256:
        raise ValueError('V237_SOURCE_OR_BASELINE_SHA_CHANGED')
    with Image.open(source) as im:
        if im.format!='PNG' or im.size!=SOURCE_SIZE:
            raise ValueError('V237_SOURCE_IMAGE_GEOMETRY_CHANGED')
        im.verify()
    with Image.open(prior) as im:
        if im.format!='PNG' or im.width<300 or im.height<500:
            raise ValueError('V237_PRIOR_IMAGE_UNREADABLE')
        im.verify()
    return {'source_sha256':SOURCE_SHA256,'finegrain_prior_sha256':PRIOR_SHA256,
            'source_dimensions':list(SOURCE_SIZE)}

def baseline_report(source:Path,prior:Path)->dict:
    locked=check_source(source,prior)
    return {'version':'V237_ALTERNATIVE_GENERATIVE_PHOTO_AB',
            'episode_id':EPISODE,
            'source_page':'https://commons.wikimedia.org/wiki/File:Passengers_arriving_for_the_RMS_Lusitania,_NYC,_May_1,_1915.webm',
            'source_film_sha256':'6b73739ef20bcacd2f43c11ab0970204a8e920b8048c16c251fef319539f5d14',
            **locked,'alternative_provider':SPACE,
            'mode':'ANONYMOUS_PUBLIC_SPACE_FREE_QUOTA_ONLY_NO_HF_TOKEN',
            'no_provider_retry':True,'paid_credit_spend_allowed':False,
            'italian_rights_verified':False,'human_artistic_approved':False,
            'vidu_generated':False,'four_i2i_complete':False,
            'final_mp4':False,'final_zip':False,'new_final_episodes_delivered':0,
            'publish_allowed':False}

def measure(im:Image.Image)->dict:
    img=im.convert('RGB').resize((128,228),Image.Resampling.LANCZOS)
    means=ImageStat.Stat(img).mean
    return {'mean_rgb':[round(v,2) for v in means],
            'red_minus_blue':round(means[0]-means[2],2),
            'mean_channel_spread':round(sum(max(p)-min(p) for p in img.getdata())/(128*228),2)}

def make_ab(source:Path,prior:Path,candidate:Path,out:Path)->dict:
    if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size<10000:
        raise ValueError('V237_NO_REAL_GENERATED_IMAGE')
    with Image.open(candidate) as im:
        if im.width<512 or im.height<512:
            raise ValueError('V237_GENERATED_IMAGE_TOO_SMALL')
        im.verify()
    rows=[]
    canvas=Image.new('RGB',(3*420,780),(23,23,23))
    d=ImageDraw.Draw(canvas)
    for i,(name,path) in enumerate([('SOURCE ORIGINAL B/W',source),('FINEGRAIN REJECTED',prior),('QWEN I2I NEW / REVIEW',candidate)]):
        with Image.open(path) as im:
            original=im.convert('RGB')
            stats=measure(original)
            resized=ImageOps.contain(original,(400,705),Image.Resampling.LANCZOS)
            canvas.paste(resized,(i*420+(420-resized.width)//2,45))
            rows.append({'name':name,'sha256':sha(path),'dimensions':list(im.size),'statistics':stats})
        d.text((i*420+15,16),name,fill=(255,255,255))
    sheet=out/'V237_REAL_QWEN_VS_REJECTED_FINEGRAIN.jpg'
    canvas.save(sheet,quality=91)
    return {'status':'REAL_ALTERNATIVE_I2I_CANDIDATE_NEEDS_ARTISTIC_QA',
            'provider_attempts':1,'new_real_i2i_candidates':1,
            'generated_photo_sha256':sha(candidate),'comparison_sheet':sheet.name,
            'images':rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--prior',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--offline',action='store_true')
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    report=baseline_report(args.source,args.prior)
    report['status']='SOURCE_LOCKED_PROVIDER_NOT_CALLED'
    if not args.offline:
        # Anonymous public ZeroGPU only: no HF token, paid InferenceProvider or retry.
        from gradio_client import Client,handle_file
        client=Client(SPACE)
        result=client.predict(image=handle_file(str(args.source)),prompt=PROMPT,
                              lora_adapter='',image2=None,seed=42,
                              randomize_seed=False,guidance_scale=2.5,steps=6,
                              preserve_identity=True,identity_strength=90,
                              output_size=1536,fix_hands=True,api_name='/edit')
        path=Path(result[0] if isinstance(result,(list,tuple)) else result)
        if not path.is_file():raise ValueError('V237_PROVIDER_NO_IMAGE_FILE')
        with Image.open(path) as im:
            im.convert('RGB').save(args.out/'V237_QWEN_REAL_I2I_CANDIDATE.png')
        report.update(make_ab(args.source,args.prior,args.out/'V237_QWEN_REAL_I2I_CANDIDATE.png',args.out))
    (args.out/'V237_REAL_MEDIA_STATUS.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V237',report['status'],'FINAL_0_OF_4')
if __name__=='__main__':main()
