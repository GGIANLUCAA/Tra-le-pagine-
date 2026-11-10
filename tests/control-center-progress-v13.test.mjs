import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext,Script} from "node:vm";

const worker=readFileSync("site/control-center-preview.worker.js","utf8");
const html=readFileSync("site/control-center-preview.html","utf8");
const be=readFileSync("site/control-center-progress-v13-backend.fragment.js","utf8");
const fe=readFileSync("site/control-center-progress-v13-frontend.fragment.js","utf8");
test("V13 is integrated, JS parses and backend is GET-only",()=>{
 assert(worker.includes(be.trim()));
 assert(html.includes(fe.trim()));
 new Script(worker.replace("export default","const WORKER = "));
 new Script(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
 assert.match(worker,/if\(request.method!=="GET"\)/);
 assert.match(worker,/productionProgressUpgradeV13\(productionProgressFromJobs/);
 assert.match(html,/progressV13Panel/);
});

const now=Date.parse("2026-11-10T22:00:00Z");
const iso=n=>new Date(n).toISOString();
const run={id:904,workflow_id:75,name:"ArtVision render master",
 status:"in_progress",event:"workflow_dispatch",head_branch:"main",
 project:"artvision",run_started_at:iso(now-24*60000),updated_at:iso(now-60*1000)};
const histories=[37,40,42,43,46,47,50,52,54,56,60,63].map((min,index)=>({
 id:100+index,workflow_id:75,status:"completed",conclusion:"success",
 head_branch:"main",event:"workflow_dispatch",run_started_at:iso(now-90*60000-min*60000),
 updated_at:iso(now-90*60000)
}));
const context={Date,Math,Number,Set,Map,JSON,
 clip:(v,n=250)=>typeof v==="string"?v.slice(0,n):"",
 progressDate:x=>{const t=Date.parse(x||"");return Number.isFinite(t)&&t>0?t:null},
 progressElapsed:(a,b)=>{const s=Date.parse(a||""),e=Date.parse(b||"");return Number.isFinite(s)&&Number.isFinite(e)&&e>=s?Math.round((e-s)/1000):null}
};
const funcs=runInNewContext(be+"\n({progressQuantileV13,progressEtaV13,productionProgressUpgradeV13,progressVideoLinkV13});",context);
test("ETA uses recent same-workflow history with medium confidence, no MP4 claim",()=>{
 const eta=funcs.progressEtaV13(run,[run,...histories],now);
 assert.equal(eta.available,true);
 assert.equal(eta.confidence,"media");
 assert.equal(eta.sample_count,12);
 assert.equal(eta.not_video_delivery,true);
 assert(eta.min_seconds<=eta.median_seconds&&eta.median_seconds<=eta.max_seconds);
 assert.match(eta.scope,/non MP4/);
});
test("minimum evidence and wrong branch do not yield an ETA",()=>{
 const tooFew=funcs.progressEtaV13(run,[run,...histories.slice(0,4)],now);
 assert.equal(tooFew.available,false);
 assert.match(tooFew.reason,/Meno di 5/);
 const mismatch=funcs.progressEtaV13({...run,status:"queued"},[run,...histories],now);
 assert.equal(mismatch.available,false);
 const branch=funcs.progressEtaV13(run,[run,...histories.map(h=>({...h,head_branch:"feature"}))],now);
 assert.equal(branch.available,false);
});
test("overrun suspends the estimate rather than showing zero or negative time",()=>{
 const slow=funcs.progressEtaV13({...run,run_started_at:iso(now-120*60000)},[run,...histories],now);
 assert.equal(slow.available,false);
 assert.equal(slow.over_historical_window,true);
 assert.equal(slow.not_video_delivery,true);
});
test("wide sample handles outliers conservatively",()=>{
 const shifted=[...histories,{...histories[0],id:999,run_started_at:iso(now-90*60000-350*60000)}];
 const eta=funcs.progressEtaV13(run,[run,...shifted],now);
 assert.equal(eta.available,true);
 assert(eta.sample_count<=histories.length);
});
test("observed phase history and inactivity are diagnostic, not evidence of an MP4",()=>{
 const old={phase:"Render video",last_step_at:iso(now-41*60000),
  percent_is_video_completion:false,considered_blocked_only_if_failed:false,
  step_fraction_percent:33,step_count:3,steps_completed:1};
 const jobs=[{name:"build",status:"in_progress",steps:[
  {name:"Fetch image",status:"completed",conclusion:"success",
   started_at:iso(now-55*60000),completed_at:iso(now-49*60000)},
  {name:"Render video",status:"in_progress",conclusion:null,
   started_at:iso(now-41*60000)}
 ]}];
 const result=funcs.productionProgressUpgradeV13(old,run,jobs,[run,...histories],now);
 assert.equal(result.telemetry_version,"v13");
 assert.equal(result.current_phase_group,"Elaborazione video");
 assert.equal(result.attention_level,"needs_review");
 assert.equal(result.phase_observed_only,true);
 assert.equal(result.video_progress_known,false);
 assert.equal(result.mp4_complete_verified,false);
 assert.equal(result.timeline.length,1);
 assert.equal(result.timeline[0].name,"Fetch image");
 const failed=funcs.productionProgressUpgradeV13({...old,considered_blocked_only_if_failed:true},run,jobs,[run,...histories],now);
 assert.equal(failed.attention_level,"confirmed_failure");
 assert.match(failed.attention_reason,/fallito/);
});
const source=html.match(/<script>([\s\S]*?)<\/script>/)[1];
test("exact queue run matches one video; ambiguity or missing sources never guess",()=>{
 const status={sources:{queue:{ok:true}},works:[{
   id:"blake_ghost_flea_1819",title:"The Ghost of a Flea",artist:"William Blake",
   variants:[{id:"cinema_museum",label:"Cinema Museum",run_id:904,
     filename:"BLAKE_MUSEUM.mp4",preview_ready:true,qa:{gold_approved:false}}]
 }]};
 const linked=funcs.progressVideoLinkV13(status,run);
 assert.equal(linked.match_status,"exact_queue_run_id");
 assert.equal(linked.linked_video.work_title,"The Ghost of a Flea");
 assert.equal(linked.linked_video.slot_id,"cinema_museum");
 assert.equal(linked.linked_video.preview_ready,true);
 assert.equal(linked.linked_video.gold_approved,false);
 assert.equal(funcs.progressVideoLinkV13({sources:{queue:{ok:false}},works:status.works},run).linked_video,null);
 const duplicated=JSON.parse(JSON.stringify(status));
 duplicated.works[0].variants.push({...duplicated.works[0].variants[0],id:"cinema_standard"});
 const ambiguous=funcs.progressVideoLinkV13(duplicated,run);
 assert.equal(ambiguous.match_status,"ambiguous");
 assert.equal(ambiguous.linked_video,null);
});
test("V13 clock window appears only with a valid interval and honest wording",()=>{
 const ui=runInNewContext(fe+"\n({progressV13Window,progressV13Age});",{
  Date,Intl,Math,Number,PROJECT_LABELS:{},state:{productionProgress:{}}
 });
 const asof=new Date(Date.now()-30000).toISOString();
 const label=ui.progressV13Window({available:true,min_seconds:600,max_seconds:1800},asof);
 assert.match(label,/Orario indicativo:/);
 assert.match(label,/–/);
 assert.equal(ui.progressV13Window({available:false},asof),"");
 assert(ui.progressV13Age(new Date(Date.now()-360000).toISOString())>=6);
});
test("V13 UI labels estimate scope and explains what to do",()=>{
 assert.match(fe,/FINE STIMATA DEL WORKFLOW/);
 assert.match(fe,/non del video/);
 assert.match(fe,/progressV13NextAction/);
 assert.match(fe,/progressV13Timeline/);
 assert.match(fe,/Dati non aggiornati/);
 assert.match(fe,/verifica del file reale/);
 assert.match(source,/function progressV13Severity/);
});
