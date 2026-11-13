#!/usr/bin/env python3
"""Exact original-only private source preflight for Paul Klee Fish Magic (PMA 1950-134-112)."""
import hashlib,io,json,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/owner-fish-magic-source-preflight";OUT.mkdir(parents=True,exist_ok=True)
KEY="Fish_Magic,_1925_-_Paul_Klee.jpg"
MD5=hashlib.md5(KEY.encode()).hexdigest()
URL="https://upload.wikimedia.org/wikipedia/commons/"+MD5[:1]+"/"+MD5[:2]+"/"+urllib.parse.quote(KEY,safe="._-")
ALT="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(KEY,safe="._-")
EXPECT_SHA1="0a017ad16420ca4ce519ab5c2168c2298efc130c"
EXPECT_BYTES=3471756
EXPECT_SIZE=(4096,3213)
for url in (URL,ALT):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ArtVisionOwnerPrivateResearch/1.0 (historical original exact source, no commercial publication)"}),timeout=80) as resp:b=resp.read(EXPECT_BYTES+1)
  assert len(b)==EXPECT_BYTES and hashlib.sha1(b).hexdigest()==EXPECT_SHA1, "Source size or SHA mismatch"
  with Image.open(io.BytesIO(b)) as im:
   assert im.format=="JPEG" and im.size==EXPECT_SIZE, "Wrong identity image"
   im.verify()
  with Image.open(io.BytesIO(b)) as im:
   preview=im.convert("RGB");preview.thumbnail((1000,800))
   preview.save(OUT/"SOURCE_PREVIEW.jpg",quality=88)
  (OUT/"ORIGINAL_ARTWORK.jpg").write_bytes(b)
  report={"status":"EXACT_SOURCE_BYTES_SHA1_PIXELS_PASS","source_name":KEY,"source_sha1":EXPECT_SHA1,"source_sha256":hashlib.sha256(b).hexdigest(),"size":len(b),"pixels":EXPECT_SIZE,"file_page":"https://commons.wikimedia.org/wiki/File:Fish_Magic,_1925_-_Paul_Klee.jpg","source_url_used":url,"collection":"Philadelphia Museum of Art object 51027 accession 1950-134-112","rights":"Commons PD-Art/PDM stated; museum site says educational use. Private review only; commercial/social publication PENDING","this_is_not_video":True}
  (OUT/"QA_SOURCE.json").write_text(json.dumps(report,indent=2)+"\n")
  print("EXACT_KLEE_FISH_MAGIC_BYTES_SHA_PASS",json.dumps(report),flush=True)
  break
 except Exception as e:
  print("SOURCE_DOWNLOAD_ATTEMPT_FAILED",type(e).__name__,str(e)[:240],flush=True)
else:raise RuntimeError("NO_VERIFIED_FISH_MAGIC_SOURCE_ABORT_NO_VIDEO")

# Check one different track from the fixed twenty (not a substitute for its licensed master).
TRACK_URL="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Immersed.mp3"
try:
 with urllib.request.urlopen(urllib.request.Request(TRACK_URL,headers={"User-Agent":"ArtVisionOwnerPrivateResearch/1.0"}),timeout=75) as resp:audio=resp.read(16000001)
 assert 100000<len(audio)<16000000 and (audio[:3]==b'ID3' or audio[:2] in (b'\xff\xfb',b'\xff\xf3',b'\xff\xf2')), "Not an MP3 recording"
 music=OUT/"IMMERSSED_OFFICIAL_MP3.mp3";music.write_bytes(audio)
 import subprocess
 probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(music)]))
 duration=float(probe["format"]["duration"])
 assert duration>65 and any(x.get("codec_type")=="audio" for x in probe["streams"]), "Not an intact musical recording"
 proof={"track":"Immersed","composer":"Kevin MacLeod","isrc":"USUAN1600010","source_url":TRACK_URL,"official_page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1600010","license":"CC BY 4.0 attribution required","bytes":len(audio),"sha256":hashlib.sha256(audio).hexdigest(),"duration_seconds":duration,"status":"VERIFIED_REAL_RECORDING_FOR_PRIVATE_REVIEW"}
 (OUT/"MUSIC_PROOF.json").write_text(json.dumps(proof,indent=2)+"\n")
 print("FISH_MAGIC_REAL_MUSIC20_AUDIO_PASS",json.dumps(proof),flush=True)
except Exception as e:
 (OUT/"MUSIC_BLOCKED.txt").write_text(type(e).__name__+": "+str(e)[:180])
 print("MUSIC_CANDIDATE_UNAVAILABLE",type(e).__name__,str(e)[:180],flush=True)

