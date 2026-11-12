/* V13 progress intelligence. All estimates are workflow-only, never promises of MP4 delivery.
   No writing to GitHub, R2, production jobs, video archives, or billing. */
function progressQuantileV13(sorted,fraction){
  if(!sorted.length)return null;
  const rank=(sorted.length-1)*fraction,lo=Math.floor(rank),hi=Math.ceil(rank);
  return sorted[lo]+(sorted[hi]-sorted[lo])*(rank-lo);
}
function progressEtaV13(run,runs,now=Date.now()){
  const empty=(reason,n=0)=>({available:false,reason,sample_count:n,confidence:"assente",
    relates_to:"workflow_GitHub_only",not_video_delivery:true});
  if(run.status==="completed")return empty("Workflow già terminato. Verifica separatamente il video.");
  if(run.status==="queued"||!progressDate(run.run_started_at))
    return empty("L'avvio effettivo non è ancora osservato.");
  if(!run.workflow_id||!["schedule","workflow_dispatch"].includes(run.event))
    return empty("Non confrontabile con altre esecuzioni dello stesso workflow.");
  const history=runs.filter(r=>r.id!==run.id&&r.workflow_id===run.workflow_id&&
    r.head_branch==="main"&&r.status==="completed"&&r.conclusion==="success"&&
    ["schedule","workflow_dispatch"].includes(r.event)&&progressDate(r.updated_at)!==null)
    .sort((a,b)=>progressDate(b.updated_at)-progressDate(a.updated_at))
    .slice(0,25);
  let samples=history.map(r=>progressElapsed(r.run_started_at,r.updated_at))
    .filter(n=>n!==null&&n>=60&&n<=21600).sort((a,b)=>a-b);
  if(samples.length<5)return empty("Meno di 5 esecuzioni riuscite e confrontabili.",samples.length);
  // Robust fence only with a sufficiently broad sample.
  if(samples.length>=10){
    const q1=progressQuantileV13(samples,.25),q3=progressQuantileV13(samples,.75),
          iqr=Math.max(1,q3-q1);
    const trimmed=samples.filter(v=>v>=Math.max(60,q1-1.5*iqr)&&v<=q3+1.5*iqr);
    if(trimmed.length>=5)samples=trimmed;
  }
  const elapsed=Math.floor((now-progressDate(run.run_started_at))/1000);
  if(!Number.isFinite(elapsed)||elapsed<0)return empty("Orologio di avvio non valido.",samples.length);
  const low=Math.round(progressQuantileV13(samples,.2)),
        mid=Math.round(progressQuantileV13(samples,.5)),
        high=Math.round(progressQuantileV13(samples,.8));
  if(elapsed>high)return {...empty("Tempo oltre la fascia abituale: stima sospesa, controlla la fase corrente.",samples.length),
    over_historical_window:true,median_total_seconds:mid,historical_upper_seconds:high,
    elapsed_seconds:elapsed};
  return {available:true,min_seconds:Math.max(0,low-elapsed),
    max_seconds:Math.max(0,high-elapsed),
    median_seconds:Math.max(0,mid-elapsed),
    median_total_seconds:mid,
    sample_count:samples.length,
    elapsed_seconds:elapsed,confidence:samples.length>=10?"media":"limitata",
    sample_type:"same_workflow_main_success",relates_to:"workflow_GitHub_only",not_video_delivery:true,
    scope:"solo fine workflow GitHub, non MP4",
    quality:"intervallo empirico, non garanzia"};
}
function progressPhaseV13(stepName){
  const s=String(stepName||"").toLowerCase();
  if(/render|ffmpeg|encode|montag|film|clip|video/i.test(s))return "Elaborazione video";
  if(/tts|audio|voice|voce|narrat|music|musica/i.test(s))return "Audio e narrazione";
  if(/frame|image|fotograf|asset|download|source|fonti|research|ricerc/i.test(s))return "Materiali e fonti";
  if(/qa|quality|valid|verify|test|check|audit|preflight|integrity/i.test(s))return "Controlli tecnici";
  if(/upload|publish|release|archiv|s3|r2/i.test(s))return "Archivio e consegna";
  return "Passaggio GitHub";
}
function productionProgressUpgradeV13(old,run,jobs,runs,now=Date.now()){
  const steps=(Array.isArray(jobs)?jobs.slice(0,30):[]).flatMap(job=>
    (Array.isArray(job.steps)?job.steps.slice(0,60):[]).map(step=>({
      name:clip(step.name,130),job_name:clip(job.name,110),
      status:clip(step.status,35),conclusion:clip(step.conclusion,35),
      started_at:clip(step.started_at,40),completed_at:clip(step.completed_at,40)
    })));
  const active=steps.find(s=>s.status==="in_progress")||null;
  const recent=steps.filter(s=>s.status==="completed")
    .sort((a,b)=>(progressDate(b.completed_at)||progressDate(b.started_at)||0)-
                  (progressDate(a.completed_at)||progressDate(a.started_at)||0))
    .slice(0,4).map(s=>({name:s.name,job_name:s.job_name,
      status:s.conclusion==="success"?"completed_success":"completed_other",
      conclusion:s.conclusion,completed_at:s.completed_at}));
  const lastEvent=old.last_step_at?progressDate(old.last_step_at):null;
  const idleMinutes=lastEvent!==null?Math.max(0,Math.floor((now-lastEvent)/60000)):null;
  const started=progressDate(run.run_started_at);
  const elapsed=started!==null&&now>=started?Math.floor((now-started)/1000):null;
  const bad=old.considered_blocked_only_if_failed===true;
  const alert=bad?"confirmed_failure":
    run.status==="in_progress"&&idleMinutes!==null&&idleMinutes>=30?"needs_review":"none";
  const currentStage=old.phase||"Passaggio non rilevato";
  const currentSince=active?active.started_at:null;
  const stepDuration=currentSince&&progressDate(currentSince)<=now?
    Math.floor((now-progressDate(currentSince))/1000):null;
  return {...old,telemetry_version:"v13",
    eta:progressEtaV13(run,runs,now),
    latest_observation_at:new Date(now).toISOString(),
    current_phase_group:progressPhaseV13(currentStage),
    current_phase_started_at:currentSince,
    current_phase_elapsed_seconds:stepDuration,
    elapsed_seconds:elapsed,
    idle_minutes:idleMinutes,
    attention_level:alert,
    attention_reason:bad?
      "Un job/step è fallito, è stato annullato oppure è scaduto. Apri i log.":
      alert==="needs_review"?
      "Nessuna nuova transizione osservata per almeno 30 min; non prova che il render sia bloccato.":
      "Nessun errore di questa run confermato dai passaggi recuperati.",
    timeline:recent,
    phase_observed_only:true,video_progress_known:false,
    mp4_complete_verified:false,owner_approved:false,
    percent_is_video_completion:false};
}

function progressVideoLinkV13(status,run){
  if(!status?.sources?.queue?.ok||!Array.isArray(status.works))return {match_status:"unavailable",linked_video:null};
  const matches=[];
  for(const w of status.works){
    for(const v of w.variants||[]){
      if(v&&Number.isSafeInteger(v.run_id)&&v.run_id===run.id){
        matches.push({work_id:String(w.id||"").slice(0,120),
          work_title:String(w.title||"").slice(0,180),
          artist:String(w.artist||"").slice(0,100),
          slot_id:String(v.id||"").slice(0,55),
          slot_label:String(v.label||"").slice(0,100),
          filename:String(v.filename||"").slice(0,190),
          preview_ready:v.preview_ready===true,
          gold_approved:v.qa?.gold_approved===true});
      }
    }
  }
  if(matches.length===1)return {match_status:"exact_queue_run_id",linked_video:matches[0]};
  if(matches.length>1)return {match_status:"ambiguous",linked_video:null};
  return {match_status:"no_exact_match",linked_video:null};
}
