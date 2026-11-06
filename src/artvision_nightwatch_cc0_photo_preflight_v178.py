#!/usr/bin/env python3
"""V178 Night Watch: recover EXACT Commons CC0 color museum installation original.
One photographic source only; metadata is not artistic verification or frame approval.
"""
import json,hashlib,pathlib,urllib.request,time
from PIL import Image
OUT=pathlib.Path('/tmp/artvision_nightwatch_v178');OUT.mkdir(parents=True,exist_ok=True)
URL='https://upload.wikimedia.org/wikipedia/commons/2/2c/Bezoekers_bij_de_Nachtwacht_op_zaal_tijdens_de_herfstvakantie%2C_HA-0027935.jpg'
PAGE='https://commons.wikimedia.org/wiki/File:Bezoekers_bij_de_Nachtwacht_op_zaal_tijdens_de_herfstvakantie%2C_HA-0027935.jpg'
EXPECTED_SHA1='cda206ac3de93f254af5a5698baa061f510d25ad'
EXPECTED_BYTES=2563083
EXPECTED_PIXELS=(5296,3530)
f=OUT/'NIGHTWATCH_RIJKSMUSEUM_2013_CC0_REAL_ROOM_V178.jpg'
manifest={'work':'Rembrandt The Night Watch','museum':'Rijksmuseum SK-C-5','source_page':PAGE,'source_original':URL,'source_metadata':'V177 original Wikimedia Commons imageinfo','license_metadata':'CC0','photographer':'René den Engelsman / Rijksmuseum','photo_date':'2013-10-25','expected_sha1':EXPECTED_SHA1,'expected_bytes':EXPECTED_BYTES,'expected_pixels':EXPECTED_PIXELS,'image_is_color':False,'photo_original_verified':False,'frame_of_specific_work_verified':False,'museum_approved':False,'gold':False,'published':False,'paid_calls':0,'tts_calls':0,'rendered_video':False}
try:
  error=None
  for attempt in range(2):
    try:
      req=urllib.request.Request(URL,headers={'User-Agent':'ArtVisionSourcePreflight/1.0 (source attribution; no publication)'})
      with urllib.request.urlopen(req,timeout=35) as response:
        data=response.read(12000000)
      if len(data)!=EXPECTED_BYTES: raise ValueError('size mismatch '+str(len(data)))
      if hashlib.sha1(data).hexdigest()!=EXPECTED_SHA1:raise ValueError('SHA1 mismatch')
      f.write_bytes(data)
      with Image.open(f) as im:
        if im.size!=EXPECTED_PIXELS or im.format!='JPEG':raise ValueError('pixel/format mismatch')
        im.convert('RGB').resize((1200,800)).save(OUT/'NIGHTWATCH_V178_REVIEW_PREVIEW.jpg',quality=90)
        manifest['image_is_color']=im.mode in ('RGB','RGBA','P')
      manifest.update({'photo_original_verified':True,'actual_sha256':hashlib.sha256(data).hexdigest(),'actual_bytes':len(data),'actual_pixels':EXPECTED_PIXELS,'status':'EXACT_ORIGINAL_SHA1_BYTES_PIXELS_PASS_VISUAL_REVIEW_PENDING'})
      error=None
      break
    except Exception as e:
      error=str(e)
      if attempt==0:time.sleep(3)
  if error:raise RuntimeError(error)
except Exception as e:
  manifest['status']='SOURCE_RECOVERY_BLOCKED';manifest['error']=str(e)
(OUT/'NIGHTWATCH_V178_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(manifest,indent=2))
if not manifest['photo_original_verified']:raise SystemExit(2)
