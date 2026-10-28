#!/usr/bin/env python3
"""Consumer Vidu automation with strict per-shot approval and crash-safe reservation.

Modes:
  plan     Offline validation + exact approval fingerprint. NEVER submits.
  quote    Read-only account quote. NEVER submits.
  submit   One shot ONLY after human-approved exact manifest, account quote and ledger reservation.
  collect  Read-only retrieval of a previously submitted task.
No automatic paid retry, provider/model substitution, or social publication.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

CONSUMER_URL = "https://service.vidu.com"
ALLOWED_MODELS = {"3.1", "3.2", "3.2_a"}
ALLOWED_SCHEDULES = {"claw_pass", "nopeak"}
FIELDS = ("image_sha256", "prompt", "model_version", "duration",
          "resolution", "transition", "schedule_mode", "max_credits")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def fingerprint(p):
    canonical = {k:p[k] for k in FIELDS}
    return hashlib.sha256(json.dumps(canonical, sort_keys=True,
                     separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def validate(path, approve=False):
    root = Path.cwd().resolve()
    path = Path(path).resolve()
    if root not in path.parents or path.suffix != ".json":
        raise ValueError("Manifest must be a JSON file inside the repository")
    p = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(p, dict):
        raise ValueError("Manifest must contain an object")
    if p.get("provider") != "vidu_consumer_official_cli":
        raise ValueError("Wrong provider: developer API is NOT the consumer subscription")
    if p.get("model_version") not in ALLOWED_MODELS:
        raise ValueError("CLI model unavailable/unverified, no model substitution")
    model_names={"3.1":"Q2 (CLI 3.1)", "3.2":"Q3 (CLI 3.2)", "3.2_a":"Q3 audio (CLI 3.2_a)"}
    if p.get("model_name") != model_names[p["model_version"]]:
        raise ValueError("Exact CLI model name mismatch; no substitution permitted")
    if type(p.get("duration")) is not int or not 2<=p["duration"]<=8:
        raise ValueError("Duration must be 2-8 seconds")
    if p.get("resolution")!="1080p" or p.get("transition") not in ("pro","speed"):
        raise ValueError("Consumer CLI Q2/Q3 only: 1080p and supported transition")
    if p.get("schedule_mode") not in ALLOWED_SCHEDULES:
        raise ValueError("Only explicitly selected subscription pass/offpeak modes")
    if type(p.get("max_credits")) is not int or not 0<=p["max_credits"]<=8:
        raise ValueError("Per-shot ceiling 0-8 credits")
    if not isinstance(p.get("prompt"),str) or not 50<=len(p["prompt"])<=2000:
        raise ValueError("Narrative action prompt missing")
    if not isinstance(p.get("spoken_line"),str) or len(p["spoken_line"].strip())<12:
        raise ValueError("Must bind shot to narration")
    if not re.fullmatch(r"[0-9a-f]{64}",p.get("image_sha256","")):
        raise ValueError("Source image SHA-256 required")
    image = (root / str(p.get("image_path",""))).resolve()
    if root not in image.parents or not image.is_file() or image.suffix.lower() not in (".jpg",".jpeg",".png",".webp"):
        raise ValueError("Verified image must already exist INSIDE the repository")
    if not 1024<=image.stat().st_size<=9_500_000 or sha256(image)!=p["image_sha256"]:
        raise ValueError("Image missing, damaged or SHA mismatch")
    code=fingerprint(p)[:12].upper()
    if approve:
        a=p.get("approval") or {}
        if a.get("status")!="explicit_user_approved" or a.get("plan_code")!=code:
            raise PermissionError("No user-approved exact image/prompt/model/cost fingerprint")
        if not isinstance(a.get("user_text"),str) or len(a["user_text"].strip())<35:
            raise PermissionError("Missing verifiable exact user approval statement")
        if a.get("max_generations")!=1:
            raise PermissionError("One generation per user approval only")
        # This gate explicitly rejects the past Q2-Pro-Fast approval being
        # misinterpreted as CLI Q2 3.1.
        if "Q2 Pro Fast" in a["user_text"] and p["model_version"]=="3.1":
            raise PermissionError("Q2 Pro Fast is not established equivalent to CLI Q2 3.1")
    return p, image, code

def cli(args,timeout=90):
    run=subprocess.run(["vidu-cli",*args],capture_output=True,text=True,timeout=timeout,check=False)
    if run.returncode:
        raise RuntimeError("Vidu CLI failed (no automatic retry); exit status "+str(run.returncode))
    try:
        result=json.loads(run.stdout)
    except json.JSONDecodeError:
        raise ValueError("Vidu CLI did not return valid JSON (no retry)")
    if not isinstance(result,dict) or result.get("ok") is not True:
        raise RuntimeError("Vidu account/provider rejected request; no retry")
    return result

def require_account():
    if not os.getenv("VIDU_TOKEN","").strip() or os.getenv("VIDU_BASE_URL")!=CONSUMER_URL:
        raise RuntimeError("Consumer Vidu token not configured at official overseas endpoint")

def quote(p):
    require_account()
    if p["schedule_mode"]=="claw_pass":
        quota=cli(["quota","pass"])
        if quota.get("has_pass") is not True or quota.get("remain_seconds",0)<p["duration"]:
            raise RuntimeError("Subscription pass unavailable or exhausted; no credit fallback")
    args=["task","cost","--type","img2video","--model-version",p["model_version"],
         "--duration",str(p["duration"]),"--resolution",p["resolution"],
         "--transition",p["transition"],"--sample-count","1",
         "--codec","h264","--schedule-mode",p["schedule_mode"]]
    q=cli(args)
    cost=q.get("cost_credits")
    if type(cost) is not int or cost<0 or cost>p["max_credits"]:
        raise RuntimeError("Server quote exceeds explicitly approved maximum")
    if q.get("can_submit") is not True:
        raise RuntimeError("Provider quote does not allow this task")
    return cost

def ledger_path(code):
    return "queue/vidu_consumer_attempts/"+code+".json"

def reserve_once(code):
    """Durable GitHub file created *before* outbound paid task. Abort on failure."""
    repo=os.getenv("GITHUB_REPOSITORY","")
    token=os.getenv("GH_TOKEN","")
    branch=os.getenv("GITHUB_REF_NAME","")
    if not repo or not token or branch!="main":
        raise RuntimeError("Paid submit requires official repo main branch with GH_TOKEN")
    dest=ledger_path(code)
    payload={"status":"reserved_before_provider_submit",
             "plan_code":code,"attempts_allowed":1,"provider":"vidu_consumer"}
    content=base64.b64encode((json.dumps(payload,sort_keys=True)+"\n").encode()).decode()
    cmd=["gh","api","-X","PUT","repos/"+repo+"/contents/"+dest,
         "-f","message=Reserve Vidu consumer shot "+code+" before provider request",
         "-f","content="+content,"-f","branch=main"]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=30,check=False)
    if r.returncode:
        # Existing marker, branch protections, or concurrent writes all FAIL CLOSED.
        raise RuntimeError("Cannot make exclusive durable reservation; NO paid submit")
    return dest

def update_ledger(code, changes):
    """Persist task ID on GitHub main; no tokens, quotas or signed URLs in public data."""
    repo = os.getenv("GITHUB_REPOSITORY","")
    if not os.getenv("GH_TOKEN") or os.getenv("GITHUB_REF_NAME")!="main":
        raise RuntimeError("Ledger update requires authenticated main-branch workflow")
    dest=ledger_path(code)
    got=subprocess.run(["gh","api","repos/"+repo+"/contents/"+dest+"?ref=main"],
                       capture_output=True,text=True,timeout=30,check=False)
    if got.returncode:raise RuntimeError("Could not read existing durable attempt marker")
    raw=json.loads(got.stdout)
    old=json.loads(base64.b64decode(raw["content"]))
    if old.get("plan_code")!=code or old.get("attempts_allowed")!=1:
        raise RuntimeError("Attempt marker fingerprint mismatch")
    old.update(changes)
    content=base64.b64encode((json.dumps(old,sort_keys=True)+"\n").encode()).decode()
    put=subprocess.run([
        "gh","api","-X","PUT","repos/"+repo+"/contents/"+dest,
        "-f","message=Update Vidu result receipt "+code,
        "-f","content="+content,"-f","sha="+raw["sha"],"-f","branch=main"],
        capture_output=True,text=True,timeout=30,check=False)
    if put.returncode:raise RuntimeError("Ledger update failed. Do not resubmit.")


def run_submit(p,image,code,out):
    cost=quote(p)
    print("APPROVED_SCENE_PRICE_WITHIN_LIMIT:",cost,"credits",flush=True)
    ledger=reserve_once(code)  # Must run before even uploading image to provider
    out.mkdir(parents=True,exist_ok=True)
    (out/"RESERVATION.json").write_text(json.dumps({"plan":code,"ledger":ledger,
         "status":"possibly_submitted_do_not_retry"},indent=2)+"\n")
    cmd=["task","submit","--type","img2video","--model-version",p["model_version"],
         "--image",str(image),"--prompt",p["prompt"],"--duration",str(p["duration"]),
         "--resolution",p["resolution"],"--transition",p["transition"],
         "--sample-count","1","--codec","h264",
         "--schedule-mode",p["schedule_mode"]]
    response=cli(cmd,timeout=180) # ONE submission. Never retry if timeout.
    task_id=response.get("task_id")
    if not isinstance(task_id,(str,int)) or not str(task_id).strip():
        raise RuntimeError("Provider did not return task ID; check console, do not retry")
    receipt={"plan":code,"task_id":str(task_id),"state":"submitted_needs_collection",
             "provider":"vidu_consumer","reported_cost_credits":cost,
             "status":"rendered_needs_review"}
    (out/"TASK_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    update_ledger(code,{"status":"submitted_needs_collection","task_id":str(task_id)})
    print("ONE_SUBMISSION_ACCEPTED; receipt saved for read-only collection")
    return str(task_id)

def run_collect(task_id,out):
    require_account()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{4,100}",task_id):
        raise ValueError("Invalid task identifier")
    out.mkdir(parents=True,exist_ok=True)
    result=cli(["task","get",task_id,"--output",str(out)],timeout=150)
    state=result.get("state","unknown")
    print("provider_status:",state)
    if state!="success":
        return
    files=[p for p in out.rglob("*") if p.suffix.lower()==".mp4"]
    if not files:
        raise RuntimeError("Provider reported success but no MP4 was saved")
    import subprocess as sp
    for f in files:
        sp.run(["ffmpeg","-v","error","-i",str(f),"-f","null","-"],check=True,timeout=120)
    dest=out/"VIDU_CLIP_SOLO_VIDEO_DA_REVISIONARE.zip"
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_STORED) as z:
        for f in files:z.write(f,arcname=f.name)
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise RuntimeError("ZIP CRC failure")
    print("REAL_MEDIA_VERIFIED; requires V44 human artistic review:",[x.name for x in files])
    return {"sha256":sha256(files[0]),"bytes":files[0].stat().st_size,"clip_name":files[0].name}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("action",choices=("plan","quote","submit","collect"))
    a.add_argument("--manifest")
    a.add_argument("--task-id")
    a.add_argument("--out",default="output/vidu_consumer_auto")
    args=a.parse_args()
    try:
        if args.action=="collect":
            if not args.task_id:raise ValueError("Receipt task ID required")
            result=run_collect(args.task_id,Path(args.out))
            if result and args.manifest:
                code=Path(args.manifest).stem
                if not re.fullmatch(r"[0-9A-F]{12}",code):
                    raise ValueError("Expected reserved plan code as ledger filename")
                update_ledger(code,{"status":"collected_needs_review",
                                    "mp4_sha256":result["sha256"],
                                    "mp4_bytes":result["bytes"]})
            return
        if not args.manifest:raise ValueError("Manifest required")
        p,image,code=validate(args.manifest,approve=args.action=="submit")
        print("PLAN_FINGERPRINT:",code,"duration:",p["duration"],"model:",p["model_name"])
        if args.action=="plan":return
        if args.action=="quote":
            print("SERVER_QUOTE_WITHIN_LIMIT:",quote(p))
            return
        run_submit(p,image,code,Path(args.out))
    except Exception as exc:
        print("FAIL_CLOSED:",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(3)

if __name__=="__main__":
    main()
