import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext,Script} from "node:vm";

const backend=readFileSync("site/control-center-preview.worker.js","utf8");
const backendFragment=readFileSync("site/control-center-progress-backend.fragment.js","utf8");
const ui=readFileSync("site/control-center-preview.html","utf8");
const uiFragment=readFileSync("site/control-center-progress-frontend.fragment.js","utf8");
test("V12 progress code ships in read-only Worker and Android inline UI",()=>{
 assert(backend.includes(backendFragment.trim()));
 assert(ui.includes(uiFragment.trim()));
 new Script(backend.replace("export default","const WORKER = "));
 new Script(ui.match(/<script>([\s\S]*?)<\/script>/)[1]);
 assert.match(backend,/if\(path==="\/api\/progress"\)/);
 assert.match(backend,/if\(request.method!=="GET"\)/);
 assert.match(ui,/productionProgressPanel\(\)/);
 assert.match(ui,/setInterval\(function\(\)\{if\(!document.hidden\)refresh\(\)\},105000\)/);
});
const now=new Date("2026-11-10T21:00:00Z").getTime();
const iso=(ms)=>new Date(ms).toISOString();
const current={id:880,workflow_id:70,name:"ArtVision 4×1 · Produzione",
 project:"artvision",head_branch:"main",status:"in_progress",conclusion:"",
 event:"workflow_dispatch",run_started_at:iso(now-1200000),
 updated_at:iso(now-120000),html_url:"https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/880"};
const history=[36,40,44,48,52,57].map((mins,i)=>({
 id:101+i,workflow_id:70,name:current.name,project:"artvision",
 head_branch:"main",status:"completed",conclusion:"success",
 event:"workflow_dispatch",run_started_at:iso(now-(mins+95)*60000),
 updated_at:iso(now-95*60000)
}));
const job={id:100,status:"in_progress",name:"build_candidate",
 started_at:iso(now-1200000),
 steps:[
  {number:1,name:"Setup",status:"completed",conclusion:"success",
   started_at:iso(now-1200000),completed_at:iso(now-1100000)},
  {number:2,name:"Research frames",status:"completed",conclusion:"success",
   started_at:iso(now-1100000),completed_at:iso(now-1000000)},
  {number:3,name:"Render",status:"in_progress",conclusion:null,started_at:iso(now-90000)}
 ]};
function pure(){
 return runInNewContext(backendFragment+
   "\n({productionProgressFromJobs,progressEta,progressElapsed});",{
  Date,Math,Number,Set,Map,JSON,clip:(s)=>typeof s==="string"?s:"",
  BAD_CONCLUSIONS:new Set(["failure","timed_out","cancelled","action_required"]),
 });
}
test("V12 real step fraction is explicitly NOT movie progress",()=>{
 const res=pure().productionProgressFromJobs(current,[job],[current,...history],now);
 assert.equal(res.schema,"studio-github-progress-v12");
 assert.equal(res.phase,"Render");
 assert.equal(res.step_fraction_percent,66);
 assert.equal(res.steps_completed,2);
 assert.equal(res.step_count,3);
 assert.equal(res.video_progress_known,false);
 assert.equal(res.percent_is_video_completion,false);
 assert.equal(res.mp4_complete_verified,false);
 assert.equal(res.owner_approved,false);
 assert.equal(res.older_than_30_minutes_without_step_change,false);
 assert.equal(res.eta.available,true);
 assert.equal(res.eta.sample_count,6);
 assert(res.eta.min_seconds<=res.eta.max_seconds);
 assert.match(res.eta.scope,/non MP4/);
});
test("V12 no fake ETA when missing history or timestamps",()=>{
 const noHistory=pure().progressEta(current,[current,...history.slice(0,3)],now);
 assert.equal(noHistory.available,false);
 assert.match(noHistory.reason,/Storico insufficiente/);
 const missing=pure().progressEta({...current,run_started_at:""},[current,...history],now);
 assert.equal(missing.available,false);
});
test("V12 slow step is a signal to inspect, not a proven block",()=>{
 const old=JSON.parse(JSON.stringify(job));
 old.steps[2].started_at=iso(now-45*60000);
 const r=pure().productionProgressFromJobs(current,[old],[current,...history],now);
 assert.equal(r.older_than_30_minutes_without_step_change,false,
   "The inspected job has a newer start timestamp");
 old.started_at=iso(now-45*60000);
 old.steps[0].started_at=iso(now-55*60000);
 old.steps[0].completed_at=iso(now-53*60000);
 old.steps[1].started_at=iso(now-53*60000);
 old.steps[1].completed_at=iso(now-49*60000);
 const stale=pure().productionProgressFromJobs(current,[old],[current,...history],now);
 assert.equal(stale.older_than_30_minutes_without_step_change,true);
 assert.equal(stale.considered_blocked_only_if_failed,false);
 old.steps[2].status="completed";old.steps[2].conclusion="failure";
 const failed=pure().productionProgressFromJobs({...current,status:"completed",conclusion:"failure"},[old],[current,...history],now);
 assert.equal(failed.considered_blocked_only_if_failed,true);
 assert.equal(failed.eta.available,false);
});
function workerFixture(){
 const runs=[current,...history].map(r=>({
  id:r.id,workflow_id:r.workflow_id,name:r.name,status:r.status,conclusion:r.conclusion,
  head_branch:r.head_branch,event:r.event,html_url:r.html_url||current.html_url,
  run_started_at:r.run_started_at,created_at:r.run_started_at,updated_at:r.updated_at
 }));
 const calls=[];
 const responses=(url)=>{
  const path=String(url);
  if(path.includes("/actions/runs?per_page"))return {workflow_runs:runs};
  if(path.includes("/queue/artvision_"))return {works:[]};
  if(path.includes("/api/catalog"))return {items:[]};
  if(path.includes("/actions/runs/880/jobs?"))return {jobs:[job]};
  return {};
 };
 const fetchStub=async url=>{calls.push(String(url));
  return new Response(JSON.stringify(responses(url)),
   {status:200,headers:{"content-type":"application/json"}})};
 const context={fetch:fetchStub,URL,Request,Response,Date,Math,Number,Set,Map,console};
 const worker=runInNewContext(backend.replace("export default","const WORKER = ")+"\nWORKER;",context);
 return {worker,calls};
}
test("GET progress is bounded to recent main workflow; no write capabilities",async()=>{
 const {worker,calls}=workerFixture();
 const base="https://preview.example/api/progress?run=";
 const response=await worker.fetch(new Request(base+"880"),{});
 assert.equal(response.status,200);
 const json=await response.json();
 assert.equal(json.ok,true);
 assert.equal(json.step_count,3);
 assert.equal(json.percent_is_video_completion,false);
 assert.equal(json.video_id,null);
 assert.equal(json.video_progress_known,false);
 assert.equal((await worker.fetch(new Request(base+"90000"),{})).status,404);
 assert.equal((await worker.fetch(new Request(base+"abc"),{})).status,400);
 assert.equal((await worker.fetch(new Request(base+"880",{method:"POST"}),{})).status,405);
 const ghCalls=calls.filter(x=>x.includes("880/jobs?"));
 assert.equal(ghCalls.length,1);
 const again=await worker.fetch(new Request(base+"880"),{});
 assert.equal(again.status,200);
 assert.equal(calls.filter(x=>x.includes("880/jobs?")).length,1,"Cache prevents repeated API calls");
});
