#!/usr/bin/env python3
"""ArtVision Great Wave V74: authentic Met JP1847 image + ONE full Gacrux WAV.

Independent modes; no video AI and no new work outside Hokusai.
The same verified original Gacrux WAV must be used for TWO Critico versions.
"""
import argparse,hashlib,json,os,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/"modules/artvision_critico/production_series/hokusai_grande_onda.json"
OUT=ROOT/"output/hokusai-v74"
ARTURL="https://images.metmuseum.org/CRDImages/as/original/DP130155.jpg"
META="https://collectionapi.metmuseum.org/public/collection/v1/objects/45434"
KNOWN_ART_SHA="cbb9988f2f18b9180a1cc0cf5dbb0e3bbf8f2e85d17930cf6ca9ab36fac36303"

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def art():
    from PIL import Image
    dest=OUT/"art";dest.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(META,headers={"User-Agent":"ArtVision/74 original openaccess museum print source"}),timeout=45) as response:
        info=json.load(response)
    if info.get("objectID")!=45434 or info.get("isPublicDomain") is not True:
        raise ValueError("Met object mismatched or licensing not Public Domain")
    url=info.get("primaryImage") or ARTURL
    if not (url.startswith("https://images.metmuseum.org/") or url.startswith("https://images.metmuseum.org")):
        raise ValueError("Invalid official source")
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ArtVision/74 artist Hokusai photo restoration"}),timeout=70) as resp:
        original=resp.read(18000000)
    path=dest/"HOKUSAI_MET_JP1847_PD.jpg";path.write_bytes(original)
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as im:
        w,h=im.size
    if min(w,h)<1300 or not 1.38<=w/h<=1.70:
        raise ValueError(f"Actual photo wrong shape/resolution: {w}x{h}")
    record={"schema":"artvision-hokusai-v74-source","title":"Under the Wave off Kanagawa",
      "artist":"Katsushika Hokusai","Met_object_id":45434,"Met_accession":"JP1847",
      "collection_url":"https://www.metmuseum.org/art/collection/search/45434",
      "image_url":url,"image_sha256":digest(path),
      "known_original_sha256":KNOWN_ART_SHA,
      "image_matches_Historic_V55":digest(path)==KNOWN_ART_SHA,
      "image_dimensions":[w,h],"print_cm":[37.9,25.7],
      "source_rights":"Met Open Access Public Domain / CC0",
      "digital_frame":"creative reconstructed, NOT historical original",
      "full_artwork_verified":True}
    save(dest/"REAL_ART_SOURCE.json",record);print(json.dumps(record))

def voice():
    import numpy as np
    import soundfile as sf
    sys.path.insert(0,str(ROOT/"src"))
    import gemini_voice as gv
    dest=OUT/"voice";dest.mkdir(parents=True,exist_ok=True)
    spec=json.loads(PROJECT.read_text(encoding="utf8"))
    assert spec["id"]=="hokusai_grande_onda" and len(spec["beats"])==11
    assert gv.VOICE=="Gacrux" and gv.MODEL=="gemini-3.8-flash-tts"
    script="\n\n".join(x["speech"] for x in spec["beats"])
    words=len(script.split())
    if not 350<=words<=850:raise ValueError("Narration length outside detailed Critico")
    (dest/"CRITICO_SCRIPT_EXACT.txt").write_text(script,encoding="utf8")
    report={"schema":"artvision-hokusai-v74-authentic-one-Gacrux",
      "title":"The Great Wave","artist":"Katsushika Hokusai",
      "beat_count":11,"words":words,
      "script_sha256":hashlib.sha256(script.encode()).hexdigest(),
      "voice_model":gv.MODEL,"voice":gv.VOICE,
      "same_wav_required_for":["critico_standard","critico_museum"],
      "new_Google_calls_max":1,"new_paid_video_AI_calls":0,
      "Google_TTS_cost":"not verified","V25_approved":False}
    if not os.environ.get("GEMINI_API_KEY"):
        report["status"]="FAILED_GEMINI_API_KEY_NOT_AVAILABLE";save(dest/"VOICE_RESULT.json",report)
        raise RuntimeError(report["status"])
    try:
        data,timed=gv.synthesize(script,dest)
        wav=dest/"VOCE.wav"
        raw,sr=sf.read(wav,dtype="float32")
        assert sr==24000 and raw.ndim==1 and np.isfinite(raw).all()
        duration=len(raw)/sr
        assert 130<duration<510,(duration,sr)
        aln=json.loads((dest/"ALLINEAMENTO_VOCE.json").read_text())
        report.update({"wav_sha256":digest(wav),"wav_bytes":wav.stat().st_size,
          "duration_seconds":duration,"sentence_count":len(timed),
          "ASR":aln,"status":"WAV_GENUINE_SYNC_TIMED" if
           aln.get("method")=="asr_with_interpolation" and (aln.get("matched_fraction") or 0)>.50
           else "GENUINE_WAV_NEEDS_ASR_CHECK"})
    except Exception as e:
        report.update({"status":"ONE_CALL_FAILED_NO_AUTO_RETRY",
                      "error_type":type(e).__name__,"error":str(e)[:200],
                      "wav_exists":(dest/"VOCE.wav").exists()})
    save(dest/"VOICE_RESULT.json",report);print(json.dumps(report))
    if report["status"] not in ("WAV_GENUINE_SYNC_TIMED","GENUINE_WAV_NEEDS_ASR_CHECK"):
        raise SystemExit(2)

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("mode",choices=["art","voice"]);args=a.parse_args()
    (art if args.mode=="art" else voice)()
