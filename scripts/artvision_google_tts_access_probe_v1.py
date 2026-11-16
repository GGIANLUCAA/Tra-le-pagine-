#!/usr/bin/env python3
"""Diagnose Google Gemini TTS model visibility WITHOUT generating audio or text.

Uses only GET metadata endpoints. No billing, no generation or fallback voices.
Never prints keys, request headers or response bodies. Output is generic status.
"""
import json,os,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone

ENDPOINTS=(
  ("v1beta","gemini-3.8-flash-tts"),
  ("v1","gemini-3.8-flash-tts"),
  ("v1beta","gemini-3.8-flash-lite-tts"),
  ("v1beta","gemini-3.1-flash-tts-preview"),
  ("v1beta","gemini-2.5-flash-preview-tts"),
  ("v1","gemini-2.5-flash-preview-tts"),
)
HOST="https://generativelanguage.googleapis.com"
def check_model(version,model,key,opener=None):
    if not key:
        return {"api_version":version,"model":model,"status":"NO_KEY"}
    # GET metadata only. Never log the URL with tokens, headers or response body.
    url=f"{HOST}/{version}/models/{model}"
    req=urllib.request.Request(url,headers={
        "x-goog-api-key":key,"Accept":"application/json","User-Agent":"ArtVision-Model-Visibility-V1"})
    call=opener or urllib.request.urlopen
    try:
        with call(req,timeout=18) as res:
            code=int(getattr(res,"status",200))
            return {"api_version":version,"model":model,"status":"VISIBLE" if code==200 else "HTTP_"+str(code)}
    except urllib.error.HTTPError as e:
        return {"api_version":version,"model":model,"status":"HTTP_"+str(e.code)}
    except (urllib.error.URLError,TimeoutError,OSError) as e:
        return {"api_version":version,"model":model,"status":"NETWORK_"+type(e).__name__}
def scan(key,opener=None):
    return {"schema":"artvision-gemini-tts-metadata-probe-v1",
            "checked_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "operation":"GET model metadata only; NO audio and NO generateContent or interactions",
            "voice_policy":"Gacrux_only_no_substitution",
            "mode":"verified_read_only_probe" if key else "no_key_skip",
            "results":[check_model(v,m,key,opener) for v,m in ENDPOINTS]}
def main():
    out=Path(os.getenv("ARTVISION_GOOGLE_TTS_PROBE_OUT","output/artvision-google-tts-access-v1/report.json"))
    out.parent.mkdir(parents=True,exist_ok=True)
    data=scan(os.getenv("GEMINI_API_KEY"))
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Only non-sensitive status codes on stdout.
    for item in data["results"]:
        print(item["api_version"],item["model"],item["status"])
    print("NO_GENERATION_NO_NEW_VOICE_NO_PAID_CALLS")
if __name__=="__main__":main()
