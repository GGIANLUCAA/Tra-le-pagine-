#!/usr/bin/env python3
"""V240: one free anonymous Qwen 2511 Unblur-Anything edit of real Lusitania frame.
No retry, no paid provider, no Vidu, no final approval."""
from __future__ import annotations
import argparse,base64,hashlib,io,json
from pathlib import Path
from PIL import Image

SPACE="prithivMLmods/Qwen-Image-Edit-2511-LoRAs-Fast"
SOURCE_SHA="716a886ab8583f87d2f9c28e7cb7a236f4243f029e95f29e2cfed85ddf029f10"
PRIOR_SHA="21544bcbf9acb39577141ad9a4ac1c8f7c4da183acc74932dcffd76ff20733a4"
SOURCE_SIZE=(608,1080)
PROMPT=("Restore and colorize this exact black and white documentary film photograph, "
        "New York harbor, 1915. Preserve camera angle, framing, the exact number of "
        "people, their locations, head shapes, expressions, suits, hats, hands, "
        "architecture and awnings. The two men in hats facing the camera and the "
        "partly cropped third man must remain in exactly their original positions. "
        "Keep every source silhouette and every face exactly aligned to the original film pixels. Photographic detail in natural neutral daylight, accurate period clothing, "
        "realistic skin texture. No new people, faces, fingers, buildings or objects. "
        "No orange or sepia cast, no glamour retouching, no painted look, no text.")

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_source(source:Path,expected_sha:str=SOURCE_SHA,expected_size=SOURCE_SIZE)->None:
    if source.is_symlink() or not source.is_file() or digest(source)!=expected_sha:
        raise ValueError("V240_SOURCE_SHA_MISMATCH")
    with Image.open(source) as im:
        if im.format!="PNG" or im.size!=expected_size:
            raise ValueError("V240_SOURCE_GEOMETRY_MISMATCH")
        im.verify()

def extract_result(result:dict,out:Path)->dict:
    if not isinstance(result,dict) or result.get("status")!="success":
        raise ValueError("V240_PROVIDER_NO_SUCCESSFUL_IMAGE")
    raw=result.get("image")
    if not isinstance(raw,str) or not raw.startswith("data:image/png;base64,"):
        raise ValueError("V240_PROVIDER_NOT_PNG_DATA_URI")
    encoded=raw.partition(",")[2]
    if len(encoded)>35_000_000:raise ValueError("V240_PROVIDER_IMAGE_TOO_LARGE")
    payload=base64.b64decode(encoded,validate=True)
    if len(payload)<10_000:raise ValueError("V240_PROVIDER_IMAGE_TOO_SMALL_BYTES")
    with Image.open(io.BytesIO(payload)) as im:
        if im.format!="PNG" or min(im.size)<512:
            raise ValueError("V240_PROVIDER_IMAGE_NOT_FULL_RES_PNG")
        w,h=im.size
        if abs(w/h-SOURCE_SIZE[0]/SOURCE_SIZE[1])>.025:
            raise ValueError("V240_PROVIDER_IMAGE_ASPECT_CHANGED")
        im.verify()
    out.write_bytes(payload)
    return {"generated_sha256":digest(out),"generated_size_px":[w,h],
            "new_real_i2i_candidates":1}

def one_free_attempt(source:Path,output:Path,client_factory=None)->dict:
    validate_source(source)
    if client_factory is None:
        from gradio_client import Client
        client_factory=Client
    client=client_factory(SPACE,verbose=False)
    data="data:image/png;base64,"+base64.b64encode(source.read_bytes()).decode("ascii")
    # One predict only. Never retry ambiguous or failed calls.
    response=client.predict(images_b64_json=json.dumps([data]),prompt=PROMPT,
                            lora_adapter="Unblur-Anything",seed=42,
                            randomize_seed=False,guidance_scale=1.0,
                            steps=4,api_name="/edit_image")
    return extract_result(response,output)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--prior",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    validate_source(a.source)
    if a.prior.is_symlink() or not a.prior.is_file() or digest(a.prior)!=PRIOR_SHA:
        raise SystemExit("V240_PRIOR_REJECTED_I2I_SHA_MISMATCH")
    report={"version":"V240_QWEN_FAST_REAL_I2I_TRIAL","space":SPACE,
            "source_sha256":SOURCE_SHA,"prior_rejected_sha256":PRIOR_SHA,
            "source_rights_italy_verified":False,"provider_attempts":0,
            "paid_credits_spent":0,"new_real_i2i_candidates":0,
            "four_i2i_complete":False,"vidu_generated":False,
            "final_mp4":False,"final_zip":False,"new_final_episodes_delivered":0,
            "human_artistic_approved":False,"publish_allowed":False,
            "status":"SOURCE_LOCKED_NO_PROVIDER_CALL"}
    report_path=a.out/"V240_REAL_MEDIA_STATUS.json"
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    if not a.offline:
        report["provider_attempts"]=1
        try:
            candidate=a.out/"V240_REAL_QWEN_FAST_I2I_CANDIDATE.png"
            report.update(one_free_attempt(a.source,candidate))
            from storia_rivive_v237_qwen_photo_ab import make_ab
            ab=make_ab(a.source,a.prior,candidate,a.out)
            report["comparison_sheet"]=ab["comparison_sheet"]
            report["status"]="REAL_GENERATIVE_I2I_CANDIDATE_ARTISTIC_QA_PENDING"
        except Exception as exc:
            report["status"]="FREE_PROVIDER_FAILED_NO_NEW_PHOTO"
            report["error_type"]=type(exc).__name__
            raise
        finally:
            report_path.write_text(json.dumps(report,indent=2)+"\n")
    print("V240",report["status"],"NEW_FINAL_0_OF_4")

if __name__=="__main__":main()
