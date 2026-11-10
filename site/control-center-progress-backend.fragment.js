/* Progress V12: truthful GitHub Actions job/step evidence, NOT video completion.
   Isolated GET-only backend, no paid API, no workflow dispatch, bounded public lookups. */
const productionProgressCache=new Map();
const PROGRESS_TTL_MS=105000;
const PRODUCTION_PROJECTS=new Set(["artvision","storia","wow","books","music","documentary","cinema"]);
function progressDate(x){
  const t=Date.parse(x||"");
  return Number.isFinite(t)&&t>0?t:null;
}
function progressElapsed(start,end){
  const a=progressDate(start),b=progressDate(end);
  return a!==null&&b!==null&&b>=a?Math.round((b-a)/1000):null;
}
function progressEta(run,runs,now){
  if(run.status==="completed"||!run.workflow_id||
     !["schedule","workflow_dispatch"].includes(run.event))
    return {available:false,reason:"Nessuna stima storica valida per questo workflow."};
  const durations=runs.filter(x=>
    x.id!==run.id&&x.workflow_id===run.workflow_id&&
    x.head_branch==="main"&&x.status==="completed"&&x.conclusion==="success"&&
    ["schedule","workflow_dispatch"].includes(x.event)
  ).map(x=>progressElapsed(x.run_started_at,x.updated_at))
   .filter(x=>x!==null&&x>=60&&x<=21600).sort((a,b)=>a-b);
  const elapsed=progressElapsed(run.run_started_at,new Date(now).toISOString());
  if(durations.length<5||elapsed===null)
    return {available:false,sample_count:durations.length,
      reason:"Storico insufficiente: non invento un tempo residuo."};
  const low=durations[Math.floor((durations.length-1)*.2)],
        high=durations[Math.ceil((durations.length-1)*.8)];
  if(elapsed>high)return {available:false,sample_count:durations.length,
      reason:"Durata oltre l'intervallo storico: stima non più attendibile."};
  return {available:true,min_seconds:Math.max(0,low-elapsed),
    max_seconds:Math.max(0,high-elapsed),
    sample_count:durations.length,scope:"solo fine workflow GitHub, non MP4",
    quality:"stima statistica orientativa, non promessa"};
}
function productionProgressFromJobs(run,jobs,runs,now=Date.now()){
  const inspected=Array.isArray(jobs)?jobs.slice(0,30):[];
  const steps=inspected.flatMap(job=>
    (Array.isArray(job.steps)?job.steps.slice(0,60):[]).map(step=>({
      job:clip(job.name,90),name:clip(step.name,130),
      status:clip(step.status,35),conclusion:clip(step.conclusion,35),
      started_at:clip(step.started_at,40),completed_at:clip(step.completed_at,40)
    }))
  );
  const completed=steps.filter(step=>step.status==="completed").length;
  const failed=steps.find(x=>["failure","timed_out","cancelled","action_required"].includes(x.conclusion));
  const running=steps.find(x=>x.status==="in_progress");
  const current=running?.name||
    inspected.find(j=>j.status==="in_progress")?.name||
    (run.status==="queued"?"In coda GitHub":
     run.status==="completed"?"Esecuzione terminata":"Fase tecnica non esposta");
  const timestamps=steps.flatMap(s=>[progressDate(s.started_at),progressDate(s.completed_at)])
    .concat(inspected.flatMap(j=>[progressDate(j.started_at),progressDate(j.completed_at)]))
    .filter(n=>n!==null);
  const last_step_at=timestamps.length?new Date(Math.max(...timestamps)).toISOString():null;
  const stalled_signal=run.status==="in_progress"&&
    timestamps.length>0&&now-Math.max(...timestamps)>30*60000;
  // This is a count of OBSERVED GitHub step completions, not video or time percentage.
  const pct=steps.length?Math.floor(completed/steps.length*100):null;
  return {schema:"studio-github-progress-v12",run_id:run.id,
    workflow:run.name,project:run.project,branch:run.head_branch,
    workflow_url:run.html_url,asof:new Date(now).toISOString(),
    run_status:run.status,run_conclusion:run.conclusion,
    step_count:steps.length,steps_completed:completed,step_fraction_percent:pct,
    percent_is_video_completion:false,video_id:null,video_progress_known:false,
    mp4_complete_verified:false,owner_approved:false,publish_authorized:false,
    jobs_available:inspected.length>0,job_count:inspected.length,
    phase:current,failed_step:failed?.name||null,
    last_step_at,older_than_30_minutes_without_step_change:stalled_signal,
    // A running step may legitimately take a long time. It is NOT automatically a block.
    considered_blocked_only_if_failed:failed!==undefined||
      (run.status==="completed"&&BAD_CONCLUSIONS.has(run.conclusion)),
    eta:progressEta(run,runs,now),
    note:"Passaggi GitHub osservati, non percentuale del filmato. Le automazioni ChatGPT non sono visibili a questa API."};
}
async function getProductionProgress(runId,videoService){
  const id=Number(runId);
  if(!Number.isSafeInteger(id)||id<=0)return {ok:false,reason:"ID non valido"};
  const status=await getStatus(videoService);
  if(!status.sources.github?.ok)return {ok:false,reason:"GitHub non disponibile"};
  const run=status.runs.find(r=>r.id===id&&r.head_branch==="main"&&
    PRODUCTION_PROJECTS.has(r.project));
  if(!run)return {ok:false,reason:"Esecuzione non osservata nel campione main dei progetti"};
  const cached=productionProgressCache.get(id);
  if(cached&&Date.now()-cached.at<PROGRESS_TTL_MS)return cached.result;
  try{
    const data=await json("https://api.github.com/repos/"+REPO+
      "/actions/runs/"+id+"/jobs?per_page=100",true);
    if(!Array.isArray(data.jobs))throw Error("Formato job inatteso");
    const result={ok:true,...productionProgressFromJobs(run,data.jobs,status.runs)};
    productionProgressCache.set(id,{at:Date.now(),result});
    if(productionProgressCache.size>30)productionProgressCache.clear();
    return result;
  }catch(err){
    return {ok:false,run_id:id,reason:"Fasi GitHub non disponibili; apri l'esecuzione ufficiale.",
      workflow_url:run.html_url,percent_is_video_completion:false};
  }
}
