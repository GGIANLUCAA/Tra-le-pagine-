/* V13 action-first Android cards. Source is GitHub steps, NOT film completion.
   Static/dated evidence never progresses on its own. */
function progressV13Age(iso,now=Date.now()){
  const t=Date.parse(iso||"");
  return Number.isFinite(t)&&t<=now?Math.max(0,Math.floor((now-t)/60000)):null;
}
function progressV13Severity(run,p){
  if(run.status==="completed"&&["failure","cancelled","timed_out","action_required"].includes(run.conclusion))
    return "error";
  if(p?.attention_level==="confirmed_failure")return "error";
  if(p?.attention_level==="needs_review")return "watch";
  return "normal";
}
function progressV13NextAction(run,p){
  const severity=progressV13Severity(run,p);
  if(severity==="error")return "Apri il log e prepara una correzione con GPT. Non riavviare a caso.";
  if(p?.attention_level==="needs_review")return "Controlla il passaggio in corso: potrebbe essere un'elaborazione lunga.";
  if(run.status==="queued")return "In attesa di un runner GitHub: nessun avanzamento tecnico ancora misurabile.";
  if(run.status==="completed")return "Controlla MP4, audio, download, QA e ZIP: il workflow terminato non prova la consegna.";
  return "Segui l'ultimo passaggio reale. Se non cambia, consulta i log prima di intervenire.";
}
function progressV13Window(eta,asof){
  if(!eta?.available||!Number.isFinite(eta.min_seconds)||!Number.isFinite(eta.max_seconds))return "";
  const timestamp=Date.parse(asof||"");
  if(!Number.isFinite(timestamp)||timestamp>Date.now()+60000)return "";
  const from=new Date(timestamp+Math.max(0,eta.min_seconds)*1000);
  const until=new Date(timestamp+Math.max(0,eta.max_seconds)*1000);
  const clock=new Intl.DateTimeFormat("it-IT",{hour:"2-digit",minute:"2-digit"});
  const day=new Intl.DateTimeFormat("it-IT",{day:"2-digit",month:"2-digit"});
  return (day.format(from)===day.format(until)?"Orario indicativo: "+clock.format(from)+"–"+clock.format(until):
    "Orario indicativo: "+day.format(from)+" "+clock.format(from)+" – "+day.format(until)+" "+clock.format(until));
}

function progressV13Timeline(p){
  const list=Array.isArray(p?.timeline)?p.timeline.slice(0,4):[];
  if(!list.length)return '<p class="productionMeta">Nessun passaggio precedente disponibile in questo campione.</p>';
  return '<ol class="progressTimeline">'+list.map(step=>
    '<li><span class="progressStepDot" aria-hidden="true"></span><div><strong>'+
    escapeText(step.name||"Passaggio GitHub")+'</strong><small>'+
    escapeText(step.completed_at?date(step.completed_at):"Ora non dichiarata")+
    ' · '+escapeText(step.conclusion||"esito non dichiarato")+
    '</small></div></li>').join('')+'</ol>';
}
function progressCard(run){
  const row=state.productionProgress?.[run.id];
  const p=row?.ok&&row.telemetry_version==="v13"?row:null;
  const label=PROJECT_LABELS[run.project]||run.project||"Produzione";
  const isPreparation=/research|ricerc|prepar|scout|quality|qualità|qa|audit|preflight|source|fonte|test|check|gate|report/i.test(run.name);
  const severity=progressV13Severity(run,p),stale=p&&progressV13Age(p.latest_observation_at)>5;
  const known=!!(p&&Number.isFinite(p.step_fraction_percent)&&p.step_count>0);
  const completed=known?Math.max(0,Math.min(100,Math.round(p.step_fraction_percent))):null;
  const eta=p?.eta;
  const etaValid=!!(p&&eta?.available&&run.status==="in_progress"&&!stale);
  const status=progressStatus(run,p);
  const last=p?.last_step_at?progressV13Age(p.last_step_at):null;
  const stage=p?.phase||"Fase GitHub non ancora acquisita";
  const stageGroup=p?.current_phase_group||"Passaggio GitHub";
  const elapsed=p?.elapsed_seconds!=null?progressClock(p.elapsed_seconds):"Non dichiarato";
  const stageElapsed=p?.current_phase_elapsed_seconds!=null?progressClock(p.current_phase_elapsed_seconds):"Non dichiarato";
  const confidence=etaValid?(eta.confidence==="media"?"Storico discreto":"Storico limitato"):"Stima sospesa";
  const etaText=stale?"Dati non aggiornati; aggiorna il pannello":
    etaValid?progressEtaText(eta):eta?.reason||"Non stimabile dai dati disponibili";
  const sample=eta?.sample_count;
  const runLink="https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/"+Number(run.id);
  let html='<article class="productionRun progressV13 '+severity+'" aria-label="'+escapeText(label+' · '+run.name)+'">'+
    '<div class="productionRow"><div><span class="productionProgram">'+escapeText(label)+
    '</span><h4>'+escapeText(run.name||"Attività GitHub")+'</h4>'+
    '<p class="productionStatus">'+escapeText(status)+'</p></div>'+
    '<span class="productionBadge">'+(isPreparation?'Attività preparatoria':'Workflow GitHub')+'</span></div>';
  if(p?.match_status==="exact_queue_run_id"&&p.linked_video){
    const v=p.linked_video;
    html+='<div class="progressVideoLink"><span>VIDEO COLLEGATO CON ID RUN DELLA CODA</span>'+
      '<strong>'+escapeText(v.work_title||"Opera")+' · '+escapeText(v.slot_label||"Variante")+'</strong>'+
      '<small>'+(v.preview_ready?"Scheda dichiarata accessibile nel catalogo":"MP4 non confermato sul sito")+
      ' · nessuna approvazione artistica implicita</small>';
    if(v.preview_ready&&/^[\\w ().-]{1,190}\\.mp4$/i.test(v.filename||"")){
      html+='<a href="https://video-library-studio.600led.workers.dev/media/'+
        encodeURIComponent(v.filename)+'" target="_blank" rel="noopener noreferrer">Guarda il file ↗</a>';
    }
    html+='</div>';
  }else if(p?.match_status==="ambiguous"){
    html+='<p class="progressAlert">Questa run risulta associata a più varianti nel registro. '+
      'Non posso assegnare la barra a un singolo video.</p>';
  }
  if(stale)html+='<p class="progressAlert">Ultimo controllo non recente: percentuale e tempi potrebbero essere cambiati.</p>';
  if(known){
    html+='<div class="progressMeasure"><span>Passaggi GitHub conclusi</span><strong>'+
      p.steps_completed+'/'+p.step_count+'</strong></div>'+
      '<div class="productionTrack" role="progressbar" aria-valuenow="'+completed+
      '" aria-valuemin="0" aria-valuemax="100" aria-label="Passaggi GitHub osservati completati, NON percentuale video">'+
      '<span style="width:'+completed+'%"></span></div>'+
      '<p class="productionMeta">'+completed+'% dei passaggi tecnici <b>non del video</b>. '+
      'Le nuove fasi aggiunte dal workflow possono modificare questa proporzione.</p>';
  }else{
    html+='<div class="productionTrack isUnknown" aria-hidden="true"><span></span></div>'+
      '<p class="productionMeta">Passaggi non rilevati; barra indeterminata, nessun progresso presunto.</p>';
  }
  html+='<div class="progressPrimaryData"><div class="progressCurrent"><span>ADESSO · '+
    escapeText(stageGroup)+'</span><strong>'+escapeText(stage)+'</strong>'+
    '<small>In questa fase: '+escapeText(stageElapsed)+'</small></div>'+
    '<div class="progressEstimate"><span>FINE STIMATA DEL WORKFLOW</span><strong>'+
    escapeText(etaText)+'</strong><small>'+escapeText(confidence)+
    (etaValid&&Number.isFinite(sample)?' · '+sample+' casi comparabili':'')+'</small></div></div>';
  if(etaValid){
    const windowText=progressV13Window(eta,p.latest_observation_at);
    if(windowText)html+='<p class="progressWindow">'+escapeText(windowText)+
      ' · fascia storica, non appuntamento di consegna.</p>';
  }
  html+='<div class="progressMetaRow"><span><b>Da avvio:</b> '+escapeText(elapsed)+'</span>'+
    '<span><b>Ultima transizione:</b> '+(last===null?'non disponibile':escapeText(last+' min fa'))+
    '</span><span><b>Controllo:</b> '+escapeText(p?.latest_observation_at?date(p.latest_observation_at):"in attesa")+'</span></div>';
  if(severity!=="normal")
    html+='<p class="progressAlert">'+escapeText(p?.attention_reason||"Controlla i log originali.")+'</p>';
  if(eta?.over_historical_window&&!stale)
    html+='<p class="progressAlert">Il tempo sta superando la fascia storica; non è una prova di blocco, ma la stima non è più attendibile.</p>';
  html+='<div class="progressNext"><strong>Cosa fare adesso</strong><p>'+
    escapeText(progressV13NextAction(run,p))+'</p></div>'+
    '<div class="productionButtons"><a class="miniBtn secondary" href="'+escapeText(runLink)+
    '" target="_blank" rel="noopener noreferrer">Fasi e log GitHub ↗</a>'+
    '<button class="miniBtn" type="button" data-repair-run="'+Number(run.id)+'">'+
    (severity==="error"?"Ripara con GPT":"Verifica con GPT")+'</button></div>'+
    '<details class="progressExtra"><summary>Dettagli e ultime fasi osservate</summary>'+
    progressV13Timeline(p)+'</details>'+
    '<p class="productionDisclaimer">Il video è <strong>pronto solo dopo verifica del file reale</strong>. '+
    'Questo cronometro segue GitHub, non le attività ChatGPT né la qualità artistica.</p></article>';
  return html;
}
function productionProgressPanel(){
  const runs=productionCandidates();
  let head='<section class="panel productionPanel progressV13Panel"><div class="productionHead"><div>'+
    '<h3>Avanzamento dei lavori</h3><p class="sub">Dati GitHub, aggiornati automaticamente quando il pannello è aperto. '+
    'Fasi reali, nessuna percentuale inventata per gli MP4.</p></div>'+
    '<button class="miniBtn secondary" type="button" data-progress-refresh>↻ Aggiorna</button></div>';
  if(!source("github"))return head+
    '<div class="empty">GitHub non è raggiungibile: non è possibile conoscere la fase o il tempo residuo.</div></section>';
  if(!runs.length)return head+
    '<div class="empty">Nessun workflow video GitHub in corso nel campione. '+
    'Le produzioni ChatGPT possono essere attive ma non osservabili qui.</div></section>';
  const all=(state.data.runs||[]).filter(r=>r?.head_branch==="main"&&
    r.status!=="completed"&&["artvision","storia","wow","books","music","documentary","cinema"].includes(r.project)).length;
  return head+runs.map(progressCard).join("")+
    (all>runs.length?'<p class="productionMeta">'+(all-runs.length)+
      ' altre attività in esecuzione nel campione: apri «Attività GitHub» per vederle.</p>':'')+
    '<p class="note">Tempo stimato = <b>fine tecnica GitHub</b>, non data di consegna. '+
    'Il produttore dovrà inviare checkpoint per ottenere il tempo del singolo video.</p></section>';
}
