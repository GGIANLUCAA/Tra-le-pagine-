#!/usr/bin/env python3
"""Night Watch V175: search Wikimedia Commons for genuine COLOR room/frame photography.
Research only. Metadata is not visual verification; never approve a Museum render automatically.
"""
import json,urllib.parse,urllib.request,re,html,hashlib,datetime,pathlib,time
OUT=pathlib.Path('/tmp/artvision_nightwatch_v175');OUT.mkdir(parents=True,exist_ok=True)
API='https://commons.wikimedia.org/w/api.php'
TERMS=['Night Watch Rijksmuseum gallery room colour','Rembrandt Nachtwacht Rijksmuseum zaal lijst','Night Watch Rijksmuseum framed painting','Nachtwacht Eregalerij Rijksmuseum 2024']
def get(q):
 url=API+'?'+urllib.parse.urlencode(q)
 req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionMuseumSourceResearch/1.0 (noncommercial metadata audit; no automated reuse)'})
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)
results=[];errors=[]
for term in TERMS:
 try:
  j=get({'action':'query','generator':'search','gsrsearch':'filetype:bitmap '+term,'gsrnamespace':6,'gsrlimit':12,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':700,'format':'json'})
  for p in j.get('query',{}).get('pages',{}).values():
   ii=(p.get('imageinfo') or [{}])[0];m=ii.get('extmetadata') or {}
   def clean(k):return re.sub('<[^>]+>',' ',html.unescape(m.get(k,{}).get('value',''))).strip()[:400]
   item={'title':p['title'],'source_page':'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(p['title'].replace(' ','_'),safe=':/_()'),'width':ii.get('width'),'height':ii.get('height'),'sha1':ii.get('sha1'),'size':ii.get('size'),'mime':ii.get('mime'),'license':clean('LicenseShortName'),'artist':clean('Artist'),'date':clean('DateTimeOriginal') or clean('DateTime'),'description':clean('ImageDescription'),'thumburl':ii.get('thumburl'),'original_url':ii.get('url'),'matched_term':term,'real_room_photo_verified':False,'frame_specific_verified':False,'museum_approved':False}
   if item['width'] and item['height'] and item['width']>=1200 and item['height']>=800 and item['mime'] in ('image/jpeg','image/png'):results.append(item)
 except Exception as e:errors.append({'term':term,'error':str(e)[:300]})
 time.sleep(0.4)
uniq={x['title']:x for x in results}
candidates=list(uniq.values())
def rank(x):
 t=(x['title']+' '+x['description']).lower()
 return 4*('night watch' in t or 'nachtwacht' in t)+3*('room' in t or 'zaal' in t or 'gallery' in t or 'eregalerij' in t)+2*('frame' in t or 'lijst' in t)+min(x['width']/1500,3)
candidates.sort(key=rank,reverse=True)
manifest={'schema':'artvision-nightwatch-v175-color-frame-research','date':'2026-11-06','work':'The Night Watch','accession':'Rijksmuseum SK-C-5','queries':TERMS,'candidate_count':len(candidates),'errors':errors,'candidates':candidates[:40],'status':'METADATA_CANDIDATES_ONLY_HUMAN_VISUAL_AND_RIGHTS_REVIEW_REQUIRED' if candidates else 'NO_VALID_METADATA_CANDIDATES','museum_approved':False,'slots_added':0,'new_tts':0,'paid_calls':0,'published':False,'gold':False,'note':'Do not assume candidates depict the original painting, correct frame, color photograph, or real present-day room until image pixels and license are individually verified.'}
(OUT/'NIGHT_WATCH_V175_COLOR_FRAME_CANDIDATES.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
(OUT/'NIGHT_WATCH_V175_COLOR_FRAME_REVIEW.md').write_text('# Night Watch V175 — Color real-frame candidate research\\n\\n'+f"Found {len(candidates)} unique sufficiently large image metadata records. No photo approved.\\n\\n"+'\\n'.join(f"- [{x['title']}]({x['source_page']}) — {x['width']}×{x['height']}, {x['license'] or 'license unverified'}, SHA1 {x['sha1']}" for x in candidates[:25])+'\\n\\nNo TTS, render, Gold or publication. Only documentary source metadata.\\n')
print(json.dumps({'candidates':len(candidates),'errors':errors,'top':[{k:x[k] for k in ('title','width','height','license')} for x in candidates[:8]]},ensure_ascii=False))
