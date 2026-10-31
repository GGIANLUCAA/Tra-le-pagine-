#!/usr/bin/env python3
"""Personal dog Q3 Pro, one-shot paid generation, no retry, no public releases.
Matches previous user's 8s full non-Fast quality request; entirely separate from ArtVision."""
import argparse,base64,hashlib,io,json,os,pathlib,re,subprocess,sys,time,urllib.request
ROOT=pathlib.Path("output/cane_q3_pro")
REPO=os.environ.get("GITHUB_REPOSITORY","GGIANLUCAA/Tra-le-pagine-")
API="https://api.vidu.com"
KEY=os.environ.get("VIDU_API_KEY","")
REQUEST_ID=re.compile(r"cane-olympic-q3-[a-z0-9-]{8,50}$")
ESTIMATE=160  # Vidu Q3 Pro, 8 seconds, 720p, normal rate (20/sec)
class Stop(Exception):pass
def gh(args,timeout=65,input=None):
    p=subprocess.run(["gh","api"]+args,input=input,text=True,capture_output=True,timeout=timeout)
    if p.returncode:raise Stop("GITHUB_OPERATION_FAILED "+p.stderr[-250:])
    return p.stdout
def provider(path,body=None,timeout=70):
    if not KEY:raise Stop("VIDU_KEY_NOT_CONFIGURED")
    req=urllib.request.Request(API+path,method="POST" if body is not None else "GET",headers={"Authorization":"Token "+KEY,"Accept":"application/json","Content-Type":"application/json"},data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req,timeout=timeout) as res:return json.loads(res.read(1400000))
def save(path,data):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(req):
    if req.get("schema")!="cane_olympic_q3_pro_v1":raise Stop("SCHEMA_INVALID")
    if req.get("model")!="viduq3-pro" or req.get("duration")!=8 or req.get("resolution")!="720p" or req.get("audio") is not False or req.get("off_peak") is not False:raise Stop("UNEXPECTED_PARAMS")
    if req.get("mode") not in ("plan","generate"):raise Stop("MODE_NOT_ALLOWED")
    if not REQUEST_ID.fullmatch(req.get("request_id","")):raise Stop("REQUEST_ID_INVALID")
    if req.get("source_sha256")!="4bf334d64e08efad80b0a48612b39f77953e4a8be7b3ed4c2441442f4eaf0dd9":raise Stop("SOURCE_CHANGED")
    if req.get("source_blob_sha")!="f8db3da8b5022603d33cacfd700f9f99f10842de":raise Stop("SOURCE_BLOB_CHANGED")
    if not isinstance(req.get("prompt"),str) or len(req["prompt"])<200 or len(req["prompt"])>4500:raise Stop("PROMPT_INVALID")
    if req.get("public_release") is not False:raise Stop("PRIVATE_ONLY")
def fp(d):
    fields={k:d[k] for k in ("model","duration","resolution","audio","off_peak","source_sha256","prompt")}
    return hashlib.sha256(json.dumps(fields,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:12].upper()
def credit_state():
    d=provider("/ent/v2/credits")
    rows=d.get("remains",d.get("remaining_credits"))
    if not isinstance(rows,list):raise Stop("CREDIT_SCHEMA_INVALID")
    nums=[r.get("credit_remain") for r in rows if isinstance(r,dict)]
    if not nums or any(type(n) not in (int,float) or n<0 for n in nums):raise Stop("CREDIT_BALANCE_UNREADABLE")
    return any(x>=ESTIMATE for x in nums)
def image_source(req):
    from PIL import Image
    blob=json.loads(gh(["repos/"+REPO+"/git/blobs/"+req["source_blob_sha"]]))
    if blob.get("encoding")!="base64":raise Stop("BLOB_ENCODING")
    data=base64.b64decode(blob["content"])
    if hashlib.sha256(data).hexdigest()!=req["source_sha256"]:raise Stop("IMAGE_DIGEST_MISMATCH")
    p=ROOT/"source.jpg";p.write_bytes(data)
    im=Image.open(io.BytesIO(data));im.load()
    if im.size!=(720,1280):raise Stop("SOURCE_DIMENSIONS")
    return p
def ledger_path(rid):
    return "queue/vidu_api_attempts/CANE_Q3_PRO_"+rid+".json"
def record_create(rid,d):
    blob=base64.b64encode((json.dumps(d,sort_keys=True)+"\n").encode()).decode()
    gh(["-X","PUT","repos/"+REPO+"/contents/"+ledger_path(rid),"-f","branch=main","-f","message=Reserve one private Q3 Pro dog generation "+rid,"-f","content="+blob])
def record_update(rid,d):
    info=json.loads(gh(["repos/"+REPO+"/contents/"+ledger_path(rid)+"?ref=main"]))
    blob=base64.b64encode((json.dumps(d,sort_keys=True)+"\n").encode()).decode()
    gh(["-X","PUT","repos/"+REPO+"/contents/"+ledger_path(rid),"-f","branch=main","-f","sha="+info["sha"],"-f","message=Update dog Q3 Pro generation state","-f","content="+blob])
def process_video(rid, record, state):
    creations=state.get("creations") or []
    url=creations[0].get("url") if creations else None
    if not isinstance(url,str) or not url.startswith("https://"):raise Stop("VIDEO_URL_MISSING")
    name="CANE_OLIMPICO_Q3_PRO_8S.mp4";p=ROOT/name
    request=urllib.request.Request(url,headers={"User-Agent":"PersonalDogQ3ProDownloader/1.0"})
    with urllib.request.urlopen(request,timeout=160) as inp,p.open("wb") as out:
        while True:
            chunk=inp.read(1024*1024)
            if not chunk:break
            out.write(chunk)
            if out.tell()>95_000_000:raise Stop("VIDEO_TOO_LARGE")
    if p.stat().st_size<50_000:raise Stop("VIDEO_EMPTY")
    ffprobe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=width,height","-of","json",str(p)],capture_output=True,text=True,timeout=60,check=True)
    info=json.loads(ffprobe.stdout);dur=float(info["format"]["duration"])
    if not 7.5<=dur<=8.5:raise Stop("VIDEO_WRONG_DURATION")
    if not any(x.get("width")==720 and x.get("height")==1280 for x in info["streams"]):raise Stop("VIDEO_WRONG_SIZE")
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(p),"-f","null","-"],timeout=120,check=True)
    save("PUBLIC_STATUS.json",{"state":"success","model":"viduq3-pro","duration":dur,"file":name,"sha256":file_sha(p),"bytes":p.stat().st_size,"one_paid_post":True,"credits_reported":state.get("credits",record.get("reported_credits")),"qa":"DECODE_VERIFIED_HUMAN_VISUAL_REVIEW_REQUIRED","no_cut_claim_unverified":True,"private":True})
    record["status"]="video_collected";record["video_sha256"]=file_sha(p)
    record_update(rid,record)
    print("CANE_Q3_PRO_REAL_MP4_READY",rid,name,"DURATION",round(dur,2),"bytes",p.stat().st_size,flush=True)
def main():
    a=argparse.ArgumentParser();a.add_argument("--request",required=True);args=a.parse_args()
    rfile=pathlib.Path(args.request);req=json.loads(rfile.read_text())
    validate(req)
    if rfile.as_posix()!="requests/cane_q3_pro/"+req["request_id"]+".json":raise Stop("REQUEST_PATH_INVALID")
    rid=req["request_id"];ROOT.mkdir(parents=True,exist_ok=True)
    code=fp(req)
    sufficient=credit_state()
    if req["mode"]=="plan":
        image_source(req)
        save("PUBLIC_STATUS.json",{"mode":"plan","estimated_credits":ESTIMATE,"model":"viduq3-pro","available_credits_sufficient":sufficient,"approval_code":code,"paid_post":False,"no_api_charges":True})
        print("CANE_Q3_PRO_FREE_PLAN",code,"BALANCE_SUFFICIENT",sufficient,flush=True)
        return
    spend=req.get("spend") or {}
    if spend.get("approved_max_credits")!=ESTIMATE or spend.get("approved_plan_code")!=code or spend.get("authorization_phrase")!="AUTORIZZO_160_CREDITI_VIDU" or spend.get("user_approved_this_exact_scene") is not True:
        raise Stop("NO_APPROVAL_FOR_SINGLE_160_CREDIT_TASK")
    if not sufficient:raise Stop("INSUFFICIENT_EXISTING_VIDU_CREDITS_NO_CHARGE")
    p=image_source(req)
    record={"request_id":rid,"status":"reserved_no_post_yet","max_credits":ESTIMATE,"model":req["model"],"source_sha256":file_sha(p),"prompt_sha256":hashlib.sha256(req["prompt"].encode()).hexdigest(),"paid_post_count":0,"plan_code":code,"created_utc":time.time()}
    record_create(rid,record)
    data={"model":req["model"],"images":["data:image/jpeg;base64,"+base64.b64encode(p.read_bytes()).decode()],"prompt":req["prompt"],"duration":8,"resolution":"720p","audio":False,"is_rec":False,"seed":0,"off_peak":False,"payload":"private-cane-q3-pro-"+rid}
    # Only one billable POST; ambiguous timeouts MUST NOT be retried.
    try:
        result=provider("/ent/v2/img2video",body=data,timeout=75)
    except Exception as e:
        record["paid_post_count"]=1;record["status"]="submission_ambiguous_no_retry";record_update(rid,record)
        raise Stop("PAID_POST_AMBIGUOUS_NO_RETRY "+str(type(e).__name__)) from e
    record["paid_post_count"]=1;record["status"]="accepted";record["task_id"]=str(result.get("task_id") or "");record["reported_credits"]=result.get("credits");record_update(rid,record)
    if not record["task_id"]:raise Stop("NO_TASK_ID_STOP")
    if type(record["reported_credits"]) not in (int,float) or record["reported_credits"]>ESTIMATE:
        raise Stop("PROVIDER_CREDIT_COST_EXCEEDED_CAP_NO_RETRY")
    print("CANE_Q3_PRO_POST_ACCEPTED",rid,record["task_id"],"reported_credits",record["reported_credits"],flush=True)
    for t in range(65):
        time.sleep(10)
        try:state=provider("/ent/v2/tasks/"+record["task_id"]+"/creations",timeout=35)
        except Exception:continue
        if state.get("state")=="success":
            process_video(rid,record,state);return
        if state.get("state") in ("failed","cancelled"):
            record["status"]="failed";record_update(rid,record);raise Stop("VIDU_MODEL_FAILED_NO_RETRY")
    record["status"]="poll_timeout_collect_get_only";record_update(rid,record)
    save("PUBLIC_STATUS.json",{"state":"pending","task_id":record["task_id"],"mode":"generate","paid_post_count":1,"never_retry_post":True})
    print("CANE_Q3_PRO_STILL_PENDING_NO_RETRY",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("CANE_Q3_PRO_STOP",type(e).__name__,str(e),flush=True)
        sys.exit(1)
