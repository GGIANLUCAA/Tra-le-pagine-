/* V12 Android-first progress for observed public GitHub runs (not ChatGPT automations).
   All status/steps are fetched, never animated into fictional completion. */
function productionCandidates(){
  if(!state.data?.sources?.github?.ok)return [];
  const allowed=new Set(["artvision","storia","wow","books","music","documentary","cinema"]);
  const all=(state.data.runs||[]).filter(r=>
    r&&r.head_branch==="main"&&allowed.has(r.project)&&Number.isSafeInteger(r.id)&&r.id>0);
  const running=all.filter(r=>r.status!=="completed").slice(0,3);
  if(running.length)return running;
  // Latest completed activity is useful context, but never called "render ready".
  return all.filter(r=>r.status==="completed"&&
    Number.isFinite(Date.parse(r.updated_at))&&Date.now()-Date.parse(r.updated_at)<90*60000).slice(0,1);
}
function progressClock(seconds){
  const n=Math.max(0,Math.ceil(Number(seconds)||0));
  if(!n)return "meno di 1 min";
  if(n<3600)return Math.max(1,Math.ceil(n/60))+" min";
  const hours=Math.floor(n/3600),mins=Math.ceil((n%3600)/60);
  return hours+" h"+(mins?" "+mins+" min":"");
}
function progressStatus(run,details){
  if(run.status==="completed"){
    return ["failure","cancelled","timed_out","action_required"].includes(run.conclusion)?
      "Ultima esecuzione fallita · da riparare":"Workflow terminato · MP4 da verificare";
  }
  if(details?.considered_blocked_only_if_failed)return "Step fallito · intervento richiesto";
  if(run.status==="queued")return "In coda GitHub";
  if(details?.older_than_30_minutes_without_step_change)
    return "Fase lunga, nessun nuovo step osservato · controllare";
  return "Esecuzione in corso su GitHub";
}
function progressEtaText(value){
  if(!value?.available)return value?.reason||"Stima non disponibile";
  const a=progressClock(value.min_seconds),b=progressClock(value.max_seconds);
  return a===b?"Circa "+b:"Fra "+a+" e "+b;
}
function progressCard(run){
  const row=state.productionProgress?.[run.id];
  const p=row?.ok?row:null;
  const label=PROJECT_LABELS[run.project]||run.project||"Produzione";
  const isPreparation=/research|ricerc|prepar|scout|quality|qualità|qa|audit|preflight|source|fonte|test|check|gate|report/i.test(run.name);
  const stage=p?.phase||"Recupero delle fasi GitHub…";
  const status=progressStatus(run,p);
  const progressKnown=!!(p&&Number.isFinite(p.step_fraction_percent)&&p.step_count>0);
  const completion=progressKnown?Math.max(0,Math.min(100,Math.round(p.step_fraction_percent))):null;
  const critical=run.status==="completed"&&["failure","timed_out","cancelled","action_required"].includes(run.conclusion);
  let out='<article class="productionRun"><div class="productionRow"><div><span class="productionProgram">'+
    escapeText(label)+'</span><h4>'+escapeText(run.name||"Attività GitHub")+'</h4>'+
    '<p class="productionStatus">'+escapeText(status)+'</p></div>'+
    '<span class="productionBadge'+(critical?' warning':'')+'">'+
    (isPreparation?'Ricerca / preparazione':'Workflow GitHub')+'</span></div>';
  if(progressKnown){
    out+='<div class="productionTrack" role="progressbar" aria-valuenow="'+completion+
      '" aria-valuemin="0" aria-valuemax="100" aria-label="Percentuale dei passaggi GitHub osservati, non del video">'+
      '<span style="width:'+completion+'%"></span></div>'+
      '<p class="productionMeta">'+p.steps_completed+'/'+p.step_count+
      ' passaggi tecnici osservati · '+completion+'% dei passaggi GitHub; NON del video</p>';
  }else{
    out+='<div class="productionTrack isUnknown" aria-hidden="true"><span></span></div>'+
      '<p class="productionMeta">Progressione non calcolabile: GitHub non espone ancora i passaggi verificabili.</p>';
  }
  out+='<div class="productionDetails"><div><span>Fase adesso</span><strong>'+
    escapeText(stage)+'</strong></div><div><span>Tempo alla fine del workflow</span><strong>'+
    escapeText(p?progressEtaText(p.eta):"In attesa di dati reali")+
    '</strong></div><div><span>Ultima prova</span><strong>'+
    escapeText(p?.asof?date(p.asof):date(run.updated_at))+
    '</strong></div></div>';
  if(p?.eta?.available)out+='<p class="productionMeta">Stima ricavata da '+p.eta.sample_count+
    ' esecuzioni precedenti dello stesso workflow. Non è la data di consegna di un MP4.</p>';
  if(p?.older_than_30_minutes_without_step_change)
    out+='<p class="productionHint">Nessuna nuova fase osservata da oltre 30 minuti; può essere un normale render lungo. Verifica i log prima di considerarlo bloccato.</p>';
  out+='<div class="productionButtons"><a class="miniBtn secondary" href="'+
    escapeText("https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/"+run.id)+
    '" target="_blank" rel="noopener noreferrer">Apri fasi GitHub ↗</a>'+
    '<button type="button" class="miniBtn" data-repair-run="'+run.id+'">Ripara / verifica GPT</button></div>'+
    '<p class="productionDisclaimer">Consegna video: <b>non confermata</b>. Le automazioni ChatGPT non sono tracciabili da questi dati.</p></article>';
  return out;
}
function productionProgressPanel(){
  const runs=productionCandidates();
  let text='<section class="panel productionPanel"><div class="productionHead"><div>'+
    '<h3>Avanzamento dei lavori</h3><p class="sub">Aggiornamento automatico circa ogni 2 minuti, usando fasi reali GitHub. '+
    'Nessuna barra simulata e nessun tempo di consegna inventato.</p></div>'+
    '<button type="button" class="miniBtn secondary" data-progress-refresh>↻ Aggiorna ora</button></div>';
  if(!source("github"))return text+
    '<div class="empty">GitHub non raggiungibile: non posso valutare avanzamento o tempi.</div></section>';
  if(!runs.length)return text+'<div class="empty">Nessun workflow produttivo GitHub in corso nel campione pubblico. Le produzioni avviate dalle automazioni ChatGPT potrebbero essere attive ma qui non visibili.</div></section>';
  return text+runs.map(progressCard).join("")+
    '<p class="note">Per sapere il tempo rimanente del singolo video serviranno checkpoint inviati direttamente dal produttore e il file MP4 identificato. Le fasi GitHub e una percentuale di step non dimostrano la qualità o la conclusione del video.</p></section>';
}
var productionProgressBusy=false;
async function refreshProductionProgress(){
  if(productionProgressBusy||!state.data?.sources?.github?.ok)return;
  const candidates=productionCandidates();
  if(!candidates.length)return;
  productionProgressBusy=true;
  await Promise.all(candidates.map(async run=>{
    try{
      const response=await fetch("/api/progress?run="+encodeURIComponent(run.id),{cache:"no-store"});
      if(!response.ok)throw Error("HTTP "+response.status);
      const payload=await response.json();
      if(payload?.ok===true&&payload.run_id===run.id&&payload.schema==="studio-github-progress-v12")
        state.productionProgress[run.id]=payload;
    }catch{delete state.productionProgress[run.id]}
  }));
  productionProgressBusy=false;
  if(["home","health","issues"].includes(state.page)&&state.data)render();
}
