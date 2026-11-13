#!/usr/bin/env python3
"""Zero-cost, no-network audit of configured image restoration provider candidates.

Reports presence of credentials without disclosing values. Does not claim models
are reachable, free, licensed or capable of faithful historical I2I.
"""
import json,os
from pathlib import Path

PROVIDERS={
 "hugging_face":{"secrets":["HF_TOKEN"],"purpose":"generative_i2i_candidate","status":"requires_live_model_and_quota_check"},
 "ai_horde":{"secrets":["AIHORDE_API_KEY","AIHORDE_API_KEY_2"],"purpose":"generative_i2i_candidate","status":"requires_model_capability_and_credit_check"},
 "nvidia":{"secrets":["NVIDIA_API_KEY"],"purpose":"model_catalog_research_only","status":"existing_nim_adapter_text_only"},
 "vidu":{"secrets":["VIDU","VIDU2","VIDUOK"],"purpose":"motion_after_photo_approval","status":"not_a_photo_reconstruction_provider"},
 "gemini":{"secrets":["GEMINI_API_KEY","GEMINI_API_KEY2"],"purpose":"scene_analysis","status":"not_a_verified_i2i_restoration_provider"},
 "openrouter":{"secrets":["OPENRUTER2","OPENRUTER3"],"purpose":"scene_analysis","status":"not_a_verified_i2i_restoration_provider"}
}
def audit(env):
    return {"schema":"storia-provider-audit-v1","paid_requests":0,
            "model_inference_requests":0,"no_secret_values_recorded":True,
            "providers":{p:{"purpose":cfg["purpose"],"status":cfg["status"],
              "configured_secret_names":[k for k in cfg["secrets"] if bool(env.get(k))],
              "live_model_verified":False,"image_quality_verified":False,
              "commercial_rights_verified":False} for p,cfg in PROVIDERS.items()},
            "final_video_approved":False}
def main():
    out=Path("output/storia_provider_audit/PROVIDERS.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    report=audit(os.environ)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print("PROVIDER_AUDIT_ONLY_NO_INFERENCE",json.dumps(report))
if __name__=="__main__": main()
