#!/usr/bin/env python3
"""Read-only discovery of image-model availability, no image generation or spend."""
import json
import urllib.request
import urllib.error
from pathlib import Path

ENDPOINTS={
 "ai_horde_image_models":"https://aihorde.net/api/v2/status/models?type=image",
 "huggingface_finegrain_space":"https://huggingface.co/api/spaces/finegrain/finegrain-image-enhancer",
}
def check(name,url):
    req=urllib.request.Request(url,headers={"User-Agent":"TraLePagine-ReadOnlyModelScout/1.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=18) as response:
            raw=response.read(2_000_001)
            if len(raw)>2_000_000: raise ValueError("RESPONSE_TOO_LARGE")
            payload=json.loads(raw)
        if name=="ai_horde_image_models":
            if not isinstance(payload,list): raise ValueError("UNEXPECTED_CATALOG")
            candidates=[{"name":str(m.get("name",""))[:100],
                         "count":m.get("count"),"performance":m.get("performance")}
                        for m in payload if isinstance(m,dict) and any(k in str(m.get("name","")).lower() for k in ("flux","realistic","photo","sdxl"))]
            return {"http_ok":True,"catalog_total":len(payload),"candidates":candidates[:30],
                    "i2i_capability_verified":False,"quality_verified":False}
        if not isinstance(payload,dict): raise ValueError("UNEXPECTED_SPACE")
        return {"http_ok":True,"space_id":payload.get("id"),
                "sdk":payload.get("sdk"),"runtime_stage":(payload.get("runtime") or {}).get("stage"),
                "i2i_capability_verified":False,"quota_verified":False,"quality_verified":False}
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError) as e:
        return {"http_ok":False,"error_type":type(e).__name__,"quality_verified":False}
def main():
    result={"schema":"storia-read-only-image-catalog-v1","inference_calls":0,
            "paid_requests":0,"secrets_used":False,"providers":{k:check(k,v) for k,v in ENDPOINTS.items()},
            "note":"Catalog discovery is not model authorization, commercial licensing, i2i support, or visual benchmark approval"}
    out=Path("output/storia_provider_audit/READ_ONLY_MODEL_CATALOG.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print("MODEL_CATALOG_READ_ONLY",json.dumps(result))
if __name__=="__main__":main()
