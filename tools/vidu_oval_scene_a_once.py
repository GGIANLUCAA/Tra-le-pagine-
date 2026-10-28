#!/usr/bin/env python3
"""Exactly one approved Oval Portrait Vidu API scene, no retries.
Run only from dedicated GitHub Actions workflow. CloudConvert URL is used only for
source transfer, never for generative video or API credits.
"""
import base64,hashlib,json,os,pathlib,subprocess,sys,urllib.request
from PIL import Image
sys.path.insert(0,"src")
from i2v_budget_v41 import plan,submit,collect,get_balance
PHOTO=pathlib.Path("output/vidu-oval-A/SCENA_07.jpg")
OUT=pathlib.Path("output/vidu-oval-A")
SOURCE_SHA="3387ded0dd0691fd24b91aee94028341291575986675679fc6e8a8d652d973b0"
APPROVAL="BC3BD42AC11A"
LEDGER="queue/vidu_api_attempts/OVAL_A_BC3BD42AC11A.json"
def gh(*args):
    return subprocess.check_output(["gh","api",*args],stderr=subprocess.PIPE)
def save_receipt(task):
    repo=os.environ["GITHUB_REPOSITORY"]
    p=f"repos/{repo}/contents/{LEDGER}"
    old=json.loads(gh(p+"?ref=main"))
    prior=json.loads(base64.b64decode(old["content"]))
    assert prior["code"]==APPROVAL and prior["status"]=="reserved"
    prior.update({"status":"submitted_needs_collection","task_id":task["task_id"]})
    encoded=base64.b64encode((json.dumps(prior,sort_keys=True)+"\n").encode()).decode()
    gh("-X","PUT",p,"-f","message=Store Vidu scene A task ID (never resubmit)",
       "-f","content="+encoded,"-f","sha="+old["sha"],"-f","branch=main")
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    url=os.environ["SCENE_SOURCE_URL"]
    with urllib.request.urlopen(url,timeout=35) as response:
        raw=response.read(3_000_000)
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"Wrong image; abort before Vidu"
    PHOTO.write_bytes(raw)
    with Image.open(PHOTO) as image:
        assert image.size==(720,1280)
        image.verify()
    prompt=os.environ["SCENE_PROMPT"]
    p=plan(PHOTO,prompt,seconds=5,off_peak=True,max_cost_usd=0.04,preset="cinema720")
    assert p["approval_code"]==APPROVAL,"Different prompt/image/pricing from approved scene"
    assert p["model"]=="viduq2-pro-fast" and p["credits_estimated"]==8 and p["resolution"]=="720p"
    (OUT/"I2V_PLAN.json").write_text(json.dumps(p,indent=2))
    key=os.environ["VIDU_API_KEY"]
    assert get_balance(key)["available_credits"]>=8,"Insufficient balance"
    # Durable single-use marker before POST. GitHub rejects existing file (HTTP 422).
    repo=os.environ["GITHUB_REPOSITORY"]
    receipt={"code":APPROVAL,"status":"reserved","max_credits":8,"attempts_allowed":1}
    encoded=base64.b64encode((json.dumps(receipt)+"\n").encode()).decode()
    gh("-X","PUT",f"repos/{repo}/contents/{LEDGER}",
       "-f","message=Reserve previously approved Vidu scene A single use",
       "-f","content="+encoded,"-f","branch=main")
    print("Original source & approved fingerprint verified; unique durable attempt reserved",flush=True)
    # From here network uncertainty means no resubmission.
    task=submit(p,OUT,key,approved_plan_code=APPROVAL)
    print("Vidu accepted single job:",task.get("task_id"),flush=True)
    save_receipt(task)
    print("Task ID persisted for future read-only collection")
if __name__=="__main__":
    main()
