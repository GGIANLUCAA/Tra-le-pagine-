/* ArtVision Control Center V1 — separate read-only preview. No account secrets, no writes. */
const REPO="GGIANLUCAA/Tra-le-pagine-";
const LIB="https://video-library-studio.600led.workers.dev";
const UI="https://raw.githubusercontent.com/GGIANLUCAA/Tra-le-pagine-/preview/artvision-control-center-v1/site/control-center-preview.html";
let snapshot=null,snapshotAt=0,pending=null,page=null,pageAt=0;

const APP_ICON='<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">'+
'<rect width="512" height="512" rx="90" fill="#0d1219"/>'+
'<rect x="40" y="40" width="432" height="432" rx="84" fill="#1f242b" stroke="#d3b17c" stroke-width="14"/>'+
'<circle cx="256" cy="262" r="150" fill="none" stroke="#866f4f" stroke-width="4"/>'+
'<path d="M155 357L256 148L357 357M198 283H315" fill="none" stroke="#e9cb99" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>'+
'</svg>';
const APP_MANIFEST={
  name:"ArtVision Control Center",short_name:"ArtVision",id:"/",start_url:"/",scope:"/",
  display:"standalone",background_color:"#0c1118",theme_color:"#0d1217",
  description:"Il centro di controllo in sola lettura per le produzioni ArtVision.",
  icons:[
    {src:"/icon.svg",type:"image/svg+xml",sizes:"any",purpose:"any maskable"},
    {src:"/icon.svg",type:"image/svg+xml",sizes:"192x192",purpose:"any"},
    {src:"/icon.svg",type:"image/svg+xml",sizes:"512x512",purpose:"any"}
  ]
};

async function json(url,github=false,videoService=null){
  // Workers within the same Cloudflare account call one another through a
  // service binding; outbound fetch to the public workers.dev URL can return
  // a synthetic 404 even when the actual video host is healthy.
  const response=videoService&&!github&&url.startsWith(LIB+"/")
    ? await videoService.fetch(new Request(url,{method:"GET",headers:{"Accept":"application/json"}}))
    : await fetch(url,{headers:github?{"Accept":"application/vnd.github+json","User-Agent":"ArtVision-ControlCenter-Readonly"}:{"Accept":"application/json"},cf:{cacheTtl:75,cacheEverything:true}});
  if(!response.ok)throw new Error("HTTP "+response.status);
  return response.json();
}
function clip(s,n=250){return typeof s==="string"?s.slice(0,n):""}

// Editorial catalogue worlds, not autonomous production agents.
// Counts are based only on catalog objects currently returned by Video Library Studio.
const COLLECTION_NAMES=[
 "Libri narrati","Racconti e fiabe","Artisti e pittura","Critica d’arte",
 "La Storia Rivive","Restauri storici","Musica e visual","WOW LAB",
 "Cinema e cortometraggi","Documentari e curiosità","Cronaca e attualità",
 "Provini e backstage","Altri progetti"
];
function catalogueWorld(row){
  const declared=String(row.category||"").trim();
  if(declared&&declared!=="Altri progetti"){
    if(/^(libri raccontati|libri narrati|audiolibri)$/i.test(declared))return "Libri narrati";
    if(/^(fiabe e racconti|racconti e fiabe)$/i.test(declared))return "Racconti e fiabe";
    return declared.slice(0,80);
  }
  if(declared==="Altri progetti")return declared;
  const s=(String(row.key||row.name||"")+" "+String(row.project||"")).toLowerCase();
  if(/wow[_ -]?lab|wow_lab/.test(s))return "WOW LAB";
  if(/la[_ -]?storia[_ -]?rivive|storia[_ -]?rivive/.test(s))return "La Storia Rivive";
  if(/nils|pifferaio|principe[_ -]?felice|sleepy[_ -]?hollow|fantasma[_ -]?di[_ -]?canterville|alice[_ -]?cartone|ultima[_ -]?foglia/.test(s))return "Racconti e fiabe";
  if(/tra[_ -]?le[_ -]?pagine|ventimila|nautilus|dersu[_ -]?uzala|giardino[_ -]?segreto|la[_ -]?collana|siddharta|delitto[_ -]?e[_ -]?castigo|libro|libri|narrat|racconto|raccont|pifferaio|principe[_ -]?felice|sleepy[_ -]?hollow|ultima[_ -]?foglia|alice[_ -]?cartone/i.test(s)){
    if(/nils|pifferaio|principe[_ -]?felice|sleepy[_ -]?hollow|fantasma[_ -]?di[_ -]?canterville|alice[_ -]?cartone|ultima[_ -]?foglia/.test(s))return "Racconti e fiabe";
    return "Libri narrati";
  }
  if(/(?:artvision|critico|museum|bruegel|simberg|waterhouse|rembrandt|botticelli|caravaggio)/.test(s))
    return /critico|critica/.test(s)?"Critica d’arte":"Artisti e pittura";
  if(/controluce|cronaca|inchiesta/.test(s))return "Cronaca e attualità";
  if(/(?:arroseur|carmencita|lumiere|lumi[eè]re|m[eé]li[eè]s|restaur|edison|ellis[_ -]?island|venezia[_ -]?1896|new[_ -]?york[_ -]?19\d\d)/.test(s))return "Restauri storici";
  if(/terracotta|documentario|national[_ -]?geographic|curiosit/.test(s))return "Documentari e curiosità";
  if(/^(?:source[_ -]?|scene[_ -]?\d+|audio[_ -]?polished|provino|test[_ -]?|base[_ -]?video|review[_ -]?)/.test(s))return "Provini e backstage";
  if(/^(?:cinema[_ -]?reale|short[_ -]?film|cortometraggio)/.test(s))return "Cinema e cortometraggi";
  if(/music|motion|hyperlumen|mozart|beethoven|clair[_ -]?de[_ -]?lune|gymnopedie|symphony|visual|luce[_ -]?respira|scintille/.test(s))
    return "Musica e visual";
  return "Altri progetti";
}
function summarizeCollections(rows,available){
  if(!available)return null;
  const buckets=new Map(COLLECTION_NAMES.map(name=>[name,{name,count:0,available:0,unavailable:0,unknown:0,items:[]}]));
  const sorted=rows.slice().sort((a,b)=>Date.parse(b.uploaded||b.gptCreatedAt||0)-Date.parse(a.uploaded||a.gptCreatedAt||0));
  for(const r of sorted){
    const name=catalogueWorld(r);
    if(!buckets.has(name))buckets.set(name,{name,count:0,available:0,unavailable:0,unknown:0,items:[]});
    const b=buckets.get(name);b.count++;
    if(r.available===true)b.available++;
    else if(r.available===false)b.unavailable++;
    else b.unknown++;
    if(b.items.length<18)b.items.push({key:clip(r.key||r.name,190),
      title:clip(r.title||r.name||r.key,180),
      available:r.available===true?true:r.available===false?false:null});
  }
  return [...buckets.values()];
}
function projectForRun(name){
  const s=String(name||"").toLowerCase();
  // Infrastructure and dashboard jobs must never masquerade as video production.
  if(/control.center|video.library|library.studio|site.smoke|site.download|import|enrich|editorial.dossier|catalog/.test(s))return "site";
  if(/wow[\s_-]*lab/.test(s))return "wow";
  if(/storia[\s_-]*rivive|restauro.storic|restoration|storico/.test(s))return "storia";
  if(/libri|audiolibri|libro|narrat|tra[\s_-]*le[\s_-]*pagine|siddharta|ventimila[\s_-]*leghe/.test(s))return "books";
  if(/documentar|terracotta|curiosit|national.geographic/.test(s))return "documentary";
  if(/musica|music[\s_-]*motion|hyperlumen|visual[\s_-]*music|mozart/.test(s))return "music";
  if(/cinema[\s_-]*reale|cortometragg|short[\s_-]*film/.test(s))return "cinema";
  if(/artvision|art.vision|critico|museum|bruegel|rembrandt|waterhouse|simberg|delacroix|blake/.test(s))return "artvision";
  return "other";
}
const BAD_CONCLUSIONS=new Set(["failure","timed_out","action_required","cancelled"]);
function validDate(x){
  const n=Date.parse(x||"");
  return Number.isFinite(n)&&n>0&&n<=Date.now()+86400000;
}
function latestByWorkflow(runs){
  const seen=new Set(),latest=[];
  for(const r of runs){
    const key=String(r.workflow_id||r.name||"")+"@"+(r.head_branch||"main");
    if(!seen.has(key)){seen.add(key);latest.push(r)}
  }
  return latest;
}
function deriveOverview(runs,works,rows,sources){
  const projects=[["artvision","ArtVision 4×1"],["storia","La Storia Rivive"],["wow","WOW LAB"],["books","Libri narrati"],["music","Musica e visual"],["documentary","Documentari e curiosità"],["cinema","Cinema e cortometraggi"]];
  const main=runs.filter(r=>!r.head_branch||r.head_branch==="main");
  const latest=latestByWorkflow(main);
  const health=projects.map(([id,label])=>{
    const r=main.filter(x=>x.project===id),current=latest.filter(x=>x.project===id);
    const running=current.filter(x=>x.status!=="completed");
    const failures=current.filter(x=>x.status==="completed"&&BAD_CONCLUSIONS.has(x.conclusion));
    const success=r.find(x=>x.status==="completed"&&x.conclusion==="success");
    const newest=r[0]||null;
    const state=!sources.github?.ok?"unknown":running.length?"running":failures.length?"attention":newest?.conclusion==="success"?"observed_success":"unobserved";
    return {id,label,state,observed_count:r.length,active_count:running.length,
      latest_at:newest?.updated_at||null,latest_name:newest?.name||null,
      last_success_at:success?.updated_at||null,last_success_url:success?.html_url||null,
      issues:failures.length};
  });
  const priority=[
    ...latest.filter(x=>x.project!=="other"&&x.status==="completed"&&BAD_CONCLUSIONS.has(x.conclusion))
      .slice(0,6).map(x=>({kind:"workflow",priority:"check",title:clip(x.name,170),
        detail:x.conclusion==="failure"?"Ultima esecuzione del workflow fallita":x.conclusion==="timed_out"?"Tempo massimo del workflow superato":x.conclusion==="cancelled"?"Ultima esecuzione annullata":"GitHub richiede un intervento",
        time:x.updated_at,link:x.html_url,project:x.project,run_id:x.id,branch:x.head_branch,event:x.event,conclusion:x.conclusion})),
    ...["github","queue","catalog"].filter(k=>!sources[k]?.ok)
      .map(k=>({kind:"source",priority:"unknown",title:"Fonte non disponibile: "+({github:"GitHub Actions",queue:"Coda ArtVision",catalog:"Catalogo video"}[k]),
        detail:"Stato non verificabile ora; non significa che la produzione sia ferma.",time:null,link:null,project:"site"}))
  ];
  const pending=works.filter(x=>x.delivered>0&&!x.gold_approved);
  const review=pending.length?{kind:"artistic",priority:"review",count:pending.length,
    title:"Opere con revisione finale ancora non attestata",
    detail:"Il registro non certifica il Gold artistico. Questa voce non blocca automaticamente la produzione."}:null;
  const diary=[];
  for(const r of runs){
    if(!validDate(r.updated_at))continue;
    const verb=r.status!=="completed"?"Workflow avviato o in corso":r.conclusion==="success"?"Workflow riuscito":BAD_CONCLUSIONS.has(r.conclusion)?"Workflow concluso da verificare":"Workflow terminato";
    diary.push({type:"workflow",project:r.project,kind:r.status!=="completed"?"running":r.conclusion==="success"?"success":"attention",
      title:verb+" · "+clip(r.name,140),time:r.updated_at,link:r.html_url,
      note:"Esito GitHub, non certifica un nuovo MP4"});
  }
  // Only genuine catalog upload timestamps are recorded as events.
  if(sources.catalog?.ok){
    for(const row of rows){
      if(!validDate(row.uploaded))continue;
      const filename=String(row.key||row.name||"");
      const link=/^[\w ().-]{1,190}\.mp4$/i.test(filename)?
        LIB+"/watch/"+encodeURIComponent(filename):LIB;
      diary.push({type:"catalog",project:"site",kind:"catalog",
        title:"Registrato nel catalogo · "+clip(row.title||row.name||row.key,130),
        time:row.uploaded,link,note:"Data di importazione dichiarata dal catalogo"});
    }
  }
  diary.sort((a,b)=>Date.parse(b.time)-Date.parse(a.time));
  return {health,attention:priority,review,diary:diary.slice(0,35),scope:{
    github_sample:runs.length,github_main_sample:main.length,
    latest_workflows_in_sample:latest.length,
    caveat:"Ultime 100 esecuzioni al massimo; non è uno storico completo né una verifica artistica.",
    refreshed_at:new Date().toISOString()
  }};
}


function buildStatistics(runs,works,rows,sources){
  const now=Date.now();
  const realDate=x=>validDate(x)?Date.parse(x):null;
  const main=runs.filter(r=>!r.head_branch||r.head_branch==="main");
  function period(days){
    if(!sources.github?.ok)return null;
    const recent=main.filter(r=>{
      const timestamp=realDate(r.updated_at);
      return timestamp!==null&&now-timestamp>=0&&now-timestamp<=days*86400000;
    });
    const byProject={artvision:0,storia:0,wow:0,books:0,music:0,documentary:0,cinema:0,site:0,other:0};
    for(const r of recent)byProject[r.project] =(byProject[r.project]||0)+1;
    return {observed:recent.length,successful:recent.filter(r=>r.status==="completed"&&r.conclusion==="success").length,
      failed:recent.filter(r=>r.status==="completed"&&BAD_CONCLUSIONS.has(r.conclusion)).length,
      running:recent.filter(r=>r.status!=="completed").length,
      by_project:byProject};
  }
  const catalogue=sources.catalog?.ok?{
    entries:rows.length,
    explicitly_available:rows.filter(r=>r.available===true).length,
    explicitly_offline:rows.filter(r=>r.available===false).length,
    availability_unknown:rows.filter(r=>typeof r.available!=="boolean").length,
    dated_entries:rows.filter(r=>realDate(r.uploaded)!==null).length,
    dated_imports_7d:rows.filter(r=>{
      const ts=realDate(r.uploaded);
      return ts!==null&&now-ts>=0&&now-ts<=7*86400000;
    }).length
  }:null;
  const variants=works.flatMap(w=>w.variants||[]);
  const artvision=sources.queue?.ok?{
    works:works.length,expected_slots:works.length*4,
    registered_deliveries:works.reduce((sum,w)=>sum+Math.max(0,Math.min(4,Number(w.delivered)||0)),0),
    variants_with_record:variants.filter(v=>v.recorded).length,
    variants_exactly_catalogued:variants.filter(v=>v.site_catalog).length,
    variants_with_available_flag:variants.filter(v=>v.preview_ready).length,
    variants_with_sha:variants.filter(v=>v.qa?.sha_recorded).length,
    variants_with_full_download_attestation:variants.filter(v=>v.qa?.site_full_sha_documented).length,
    variants_gold_attested:variants.filter(v=>v.qa?.gold_approved).length
  }:null;
  return {activity_24h:period(1),activity_7d:period(7),catalogue,artvision,scope:{
    github_window:"Ultime 100 run GitHub pubbliche al massimo: non è uno storico completo.",
    imported_dates:"Le importazioni sono conteggiate soltanto quando il catalogo dichiara il campo uploaded.",
    product_quality:"Workflow, scheda tecnica e anteprima non equivalgono a MP4 Gold approvato.",
    updated_at:new Date().toISOString()
  }};
}

async function gather(videoService){
  const results=await Promise.allSettled([
    json("https://api.github.com/repos/"+REPO+"/actions/runs?per_page=100",true),
    json("https://raw.githubusercontent.com/"+REPO+"/main/queue/artvision_owner_selected_ten_20261102.json"),
    json(LIB+"/api/catalog",false,videoService)
  ]);
  const keys=["github","queue","catalog"],sources={};
  results.forEach((r,i)=>{sources[keys[i]]=r.status==="fulfilled"?{ok:true}:{ok:false,error:clip(r.reason&&r.reason.message||"Non disponibile",80)}});
  const gh=results[0].status==="fulfilled"?results[0].value:{};
  const queue=results[1].status==="fulfilled"?results[1].value:{};
  const cat=results[2].status==="fulfilled"?results[2].value:{};
  const runs=(Array.isArray(gh.workflow_runs)?gh.workflow_runs:[]).map(r=>({
    id:Number(r.id)||null,name:clip(r.name,180),status:clip(r.status,32),conclusion:clip(r.conclusion,32),
    html_url:clip(r.html_url,280),updated_at:clip(r.updated_at,40),event:clip(r.event,40),
    created_at:clip(r.created_at,40),run_started_at:clip(r.run_started_at,40),
    head_branch:clip(r.head_branch,100),workflow_id:Number(r.workflow_id)||null,
    head_sha:clip(r.head_sha,48),project:projectForRun(r.name)
  })).sort((a,b)=>Date.parse(b.updated_at||0)-Date.parse(a.updated_at||0));
  const rows=Array.isArray(cat.items)?cat.items.filter(x=>x&&typeof x==="object"&&x.hidden!==true):[];
  const catalogNames=new Set(rows.map(x=>String(x.key||x.name||"")));
  const catalogAvailability=new Map(rows.map(x=>[String(x.key||x.name||""),x.available===true?true:x.available===false?false:null]));
  const slotDefs=[
    {id:"critico_standard",label:"Critico · Classico",patterns:[/^critico_standard_v\d+$/]},
    {id:"critico_museum",label:"Critico · Museum",patterns:[/^critico_museum_v\d+$/]},
    {id:"cinema_standard",label:"Cinema · Classico",patterns:[/^(?:new_)?cinema_standard_v\d+$/,/^v\d+_cinema_candidate$/]},
    {id:"cinema_museum",label:"Cinema · Museum",patterns:[/^cinema_museum_v\d+$/]}
  ];
  const verified=(x)=>{
    if(x===true)return true;
    if(typeof x!=="string")return false;
    const t=x.trim();
    // A named verification with a positive result, never a PENDING/FAILED field.
    return /^(PASS|MATCH|VERIFIED)(\b|[_ :.-])/i.test(t)&&!/PENDING|FAILED|FAIL\b/i.test(t);
  };
  const evidence=(rec,fields)=>fields.some(k=>verified(rec[k]));
  const pickSlot=(w,definition)=>{
    const found=Object.entries(w).filter(([key,val])=>
      definition.patterns.some(re=>re.test(key))&&val&&typeof val==="object"&&
      (val.filename||val.mp4_filename||val.file||val.sha256||val.mp4_sha256));
    // Explicitly selected active replacement wins, then newest version.
    // Within the same version prefer its canonical "cinema_standard" record over
    // older duplicate "vNN_cinema_candidate" bookkeeping.
    found.sort((a,b)=>{
      const active=w.active_cinema_standard;
      if(a[0]===active)return -1;if(b[0]===active)return 1;
      const v=(k)=>Number((k.match(/v(\d+)/)||[])[1])||0;
      const diff=v(b[0])-v(a[0]);
      if(diff)return diff;
      const rank=(k)=>/^(critico|cinema|new_cinema)/.test(k)?0:1;
      return rank(a[0])-rank(b[0]);
    });
    const [source,record]=found[0]||["",{}];
    const filename=clip(record.filename||record.mp4_filename||record.file,190);
    const validFile=/^[\w ().-]{1,190}\.mp4$/i.test(filename)?filename:"";
    const present=!!validFile&&catalogNames.has(validFile);
    const availability=present?catalogAvailability.get(validFile):null;
    const canPreview=present&&availability===true;
    const fields={
      video_sha:record.sha256||record.mp4_sha256||record.mp4_sha256_ci||"",
      bytes:Number(record.bytes||record.mp4_bytes)||null,
      duration_s:Number(record.duration_s||record.duration_seconds)||null,
      codec:clip(record.codec||record.video_codec,90),
      status:clip(record.status||"",190)
    };
    const qa={
      sha_recorded:/^[a-f0-9]{64}$/i.test(String(fields.video_sha)),
      decode_documented:evidence(record,["ffmpeg_full_decode","full_ffmpeg_decode","full_ffmpeg_video_audio_decode",
        "independent_ffmpeg_video_audio_full_decode","ffmpeg_all_streams_full_decode",
        "full_decode_pass_ci","full_decode_pass_local","full_ffmpeg_decode"]),
      zip_documented:evidence(record,["zip_crc","zip_crc_readback","original_zip_crc","original_artifact_zip_crc",
        "private_library_download_zip_crc","zip_local_readback_sha_pass","private_library_readback_zip_crc"]),
      site_full_sha_documented:evidence(record,["site_full_download_sha256","site_catalog_and_full_download_sha256"]),
      site_range_documented:evidence(record,["site_http_206_stream_download","site_download_HTTP_206"]),
      site_playback_historic:record.site_playback_verified===true,
      gold_approved:record.gold_v25===true||record.Gold_V25===true,
      human_review:clip(record.human_artistic_review||record.artistic_human_review||record.artistic_review||"",160),
      rights_review:clip(record.commercial_rights_review||record.licensing_review||"",120)
    };
    const runId=Number(record.run_id||record.github_run_id||record.source_run_id||record.github_actions_run)||null;
    return {
      id:definition.id,label:definition.label,recorded:!!source,source,filename:validFile,
      has_sha:qa.sha_recorded,site_catalog:present,site_available:availability,
      preview_ready:canPreview,
      media_url:canPreview?LIB+"/media/"+encodeURIComponent(validFile):null,
      poster_url:canPreview?LIB+"/cover/"+encodeURIComponent(validFile.replace(/\.mp4$/i,"")):null,
      download_url:canPreview?LIB+"/download/"+encodeURIComponent(validFile):null,
      technical_status:fields.status,run_id:runId,
      details:{bytes:fields.bytes,duration_s:fields.duration_s,codec:fields.codec},
      qa
    };
  };
  const works=(Array.isArray(queue.works)?queue.works:[])
    .filter(w=>!/dal[ií]|temptation of st\.?\s*anthony/i.test(String(w.artist||"")+" "+String(w.title_en||"")))
    .map(w=>({id:clip(w.id),title:clip(w.title_en),artist:clip(w.artist),
      delivered:Number(w.slots_delivered_this_selection)||0,museum_approved:w.museum_approved===true,
      gold_approved:w.Gold_V25===true,publication_authorized:w.publication_authorized===true,
      note:clip(w.preflight_status,340),site_archive_verified_slots:
        Number.isFinite(Number(w.site_archive_verified_slots))?Number(w.site_archive_verified_slots):null,
      variants:slotDefs.map(s=>pickSlot(w,s))}));
  const media=rows.slice().sort((a,b)=>Date.parse(b.uploaded||b.gptCreatedAt||0)-Date.parse(a.uploaded||a.gptCreatedAt||0)).slice(0,24).map(x=>({
    key:clip(x.key||x.name,190),title:clip(x.title||x.name||x.key,180),available:x.available===true?true:x.available===false?false:null
  }));
  const overview=deriveOverview(runs,works,rows,sources);
  const statistics=buildStatistics(runs,works,rows,sources);
  const collections=summarizeCollections(rows,sources.catalog?.ok);
  return {asof:new Date().toISOString(),sources,runs,works,media,collections,catalog_count:rows.length,statistics,...overview};
}
// QA is an on-demand public metadata lookup, never a review of an MP4.
// Artifacts are listed by GitHub but their contents are NOT read here.
let qualitySnapshot=null,qualityAt=0,qualityPending=null;
async function gatherQuality(videoService){
  let feed=null,scope="workflow_specific",lookupError=null;
  try{
    feed=await json("https://api.github.com/repos/"+REPO+
      "/actions/workflows/quality-director-v17.yml/runs?per_page=25",true);
    if(!Array.isArray(feed.workflow_runs))throw new Error("Unexpected workflow payload");
  }catch(e){
    lookupError=clip(e&&e.message||"Non raggiungibile",80);
    const recent=await getStatus(videoService);
    scope="fallback_last_100_actions";
    feed={workflow_runs:(recent.runs||[]).filter(r=>
      Number(r.workflow_id)===392238876||/regia qualita|regia qualità v17/i.test(r.name))};
  }
  // Only manual dispatches create the QA report artifact; pull-request CI
  // passing is explicitly NOT a video check.
  const selected=feed.workflow_runs.filter(r=>r.event==="workflow_dispatch"&&
    (!r.head_branch||r.head_branch==="main")).sort((a,b)=>
      Date.parse(b.created_at||b.updated_at||0)-Date.parse(a.created_at||a.updated_at||0)).slice(0,6);
  const rows=await Promise.all(selected.map(async run=>{
    const id=Number(run.id);
    const item={id:Number.isSafeInteger(id)&&id>0?id:null,
      name:clip(run.name,130),status:clip(run.status,40),
      conclusion:clip(run.conclusion,40),updated_at:clip(run.updated_at,40),
      run_url:Number.isSafeInteger(id)&&id>0?
        "https://github.com/"+REPO+"/actions/runs/"+id:null,
      artifact_present:null,artifact_expired:null,artifact_size_bytes:null,
      artifact_metadata_checked:false};
    if(item.id&&run.status==="completed"){
      try{
        const data=await json("https://api.github.com/repos/"+REPO+
          "/actions/runs/"+id+"/artifacts?per_page=30",true);
        if(!Array.isArray(data.artifacts))throw new Error("Artifact list malformed");
        const found=data.artifacts.find(a=>a.name==="quality-v17-report");
        item.artifact_present=!!found;
        item.artifact_metadata_checked=true;
        if(found){
          item.artifact_expired=found.expired===true;
          item.artifact_size_bytes=Number(found.size_in_bytes)||null;
        }
      }catch(e){item.artifact_metadata_checked=false;}
    }
    return item;
  }));
  return {schema:"artvision-quality-metadata-v8",asof:new Date().toISOString(),
    scope,lookup_error:lookupError,source_ok:scope==="workflow_specific",
    runs:rows,manual_runs_observed:rows.length,
    report_contents_read:false,qa_pass_verified:false,mp4_bytes_verified:false,
    sha256_verified:false,owner_approved:false,publish_authorized:false,
    info:"Artifact metadata only. No JSON/MP4 or approval inspected; a successful CI run does not certify a video."};
}
async function getQuality(videoService){
  if(qualitySnapshot&&Date.now()-qualityAt<90000)return qualitySnapshot;
  if(!qualityPending)qualityPending=gatherQuality(videoService).then(r=>{
    qualitySnapshot=r;qualityAt=Date.now();return r
  }).finally(()=>{qualityPending=null});
  return qualityPending;
}

// Manual exact-SHA audit runs are evidence that GitHub executed a check,
// NOT proof of a matching master until the report artifact is actually read.
let integritySnapshot=null,integrityAt=0,integrityPending=null;
async function gatherIntegrity(){
  let feed;
  try{
    feed=await json("https://api.github.com/repos/"+REPO+
      "/actions/workflows/studio-integrity-v9.yml/runs?per_page=20",true);
    if(!Array.isArray(feed.workflow_runs))throw new Error("Unexpected workflow list");
  }catch(e){
    return {schema:"studio-integrity-metadata-v9",asof:new Date().toISOString(),
      source_ok:false,runs:[],error:"Elenco degli audit GitHub non accessibile.",
      report_contents_read:false,full_sha256_verified_by_dashboard:false,
      zip_crc_verified_by_dashboard:false,owner_approved:false,publish_authorized:false};
  }
  const selected=feed.workflow_runs.filter(r=>["workflow_dispatch","push"].includes(r.event)&&
    r.head_branch==="main").sort((a,b)=>Date.parse(b.created_at||0)-Date.parse(a.created_at||0)).slice(0,5);
  const runs=await Promise.all(selected.map(async r=>{
    const id=Number(r.id);
    const out={id:Number.isSafeInteger(id)&&id>0?id:null,
      name:clip(r.name,140),status:clip(r.status,35),conclusion:clip(r.conclusion,35),
      updated_at:clip(r.updated_at,40),event:clip(r.event,35),
      run_url:Number.isSafeInteger(id)&&id>0?"https://github.com/"+REPO+"/actions/runs/"+id:null,
      artifact_metadata_checked:false,artifact_present:null,artifact_expired:null};
    if(out.id&&out.status==="completed"){
      try{
        const response=await json("https://api.github.com/repos/"+REPO+
          "/actions/runs/"+id+"/artifacts?per_page=30",true);
        if(!Array.isArray(response.artifacts))throw new Error("Bad artifact list");
        const a=response.artifacts.find(x=>x.name==="STUDIO_INTEGRITY_V9_ONE_MASTER");
        out.artifact_metadata_checked=true;out.artifact_present=!!a;
        if(a)out.artifact_expired=a.expired===true;
      }catch(e){out.artifact_metadata_checked=false;}
    }
    return out;
  }));
  return {schema:"studio-integrity-metadata-v9",asof:new Date().toISOString(),
    source_ok:true,runs,report_contents_read:false,
    full_sha256_verified_by_dashboard:false,zip_crc_verified_by_dashboard:false,
    owner_approved:false,publish_authorized:false,
    info:"The downloadable report may contain exact SHA proof, but this dashboard only reads artifact metadata."};
}
async function getIntegrity(){
  if(integritySnapshot&&Date.now()-integrityAt<90000)return integritySnapshot;
  if(!integrityPending)integrityPending=gatherIntegrity().then(v=>{
    integritySnapshot=v;integrityAt=Date.now();return v
  }).finally(()=>{integrityPending=null});
  return integrityPending;
}

async function getStatus(videoService){
  if(snapshot&&Date.now()-snapshotAt<75000)return snapshot;
  if(!pending)pending=gather(videoService).then(x=>{snapshot=x;snapshotAt=Date.now();return x}).finally(()=>{pending=null});
  return pending;
}
// Read-only diagnostic context. A run must belong to the currently observed public
// GitHub sample; it cannot target arbitrary GitHub repositories or private APIs.
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
    const result={ok:true,...productionProgressUpgradeV13(productionProgressFromJobs(run,data.jobs,status.runs),run,data.jobs,status.runs),...progressVideoLinkV13(status,run)};
    productionProgressCache.set(id,{at:Date.now(),result});
    if(productionProgressCache.size>30)productionProgressCache.clear();
    return result;
  }catch(err){
    return {ok:false,run_id:id,reason:"Fasi GitHub non disponibili; apri l'esecuzione ufficiale.",
      workflow_url:run.html_url,percent_is_video_completion:false};
  }
}

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
const diagnosisCache=new Map();
async function getDiagnosis(runId,videoService){
  const id=Number(runId);
  if(!Number.isSafeInteger(id)||id<1)return {ok:false,reason:"ID esecuzione non valido"};
  const status=await getStatus(videoService);
  const run=(status.runs||[]).find(r=>r.id===id);
  if(!run||!status.sources.github?.ok)return {ok:false,reason:"Run non presente nel campione pubblico consultato"};
  const url="https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/"+id;
  const base={ok:true,run_id:id,run_url:url,workflow:run.name,project:run.project,
    conclusion:run.conclusion,status:run.status,branch:run.head_branch,head_sha:run.head_sha,
    updated_at:run.updated_at,event:run.event,
    jobs_available:false,jobs:[],notes:"I passaggi GitHub sono evidenza tecnica, non diagnosi certa. Aprire i log per la causa."};
  const current=diagnosisCache.get(id);
  if(current&&Date.now()-current.at<90000)return {...base,...current.jobs};
  try{
    const data=await json("https://api.github.com/repos/"+REPO+"/actions/runs/"+id+"/jobs?per_page=100",true);
    if(!Array.isArray(data.jobs))return {...base,notes:"GitHub non ha fornito l'elenco dei job; consulta il link."};
    const jobs=data.jobs.filter(j=>["failure","cancelled","timed_out","action_required"].includes(j.conclusion))
      .slice(0,8).map(j=>({
        name:clip(j.name,160),conclusion:clip(j.conclusion,40),html_url:clip(j.html_url,350),
        failed_steps:(Array.isArray(j.steps)?j.steps:[]).filter(st=>
          ["failure","cancelled","timed_out","action_required"].includes(st.conclusion)).slice(0,10)
          .map(st=>({name:clip(st.name,160),conclusion:clip(st.conclusion,40),number:Number(st.number)||null}))
      }));
    const response={jobs_available:true,jobs,notes:"Job e step ottenuti da GitHub. I log completi non vengono importati né attribuiti automaticamente."};
    diagnosisCache.set(id,{at:Date.now(),jobs:response});
    if(diagnosisCache.size>70)diagnosisCache.clear();
    return {...base,...response};
  }catch(e){
    return {...base,notes:"GitHub non ha fornito il dettaglio dei job: controlla il log tramite il link ufficiale."};
  }
}

async function getPage(){
  if(page&&Date.now()-pageAt<3600000)return page;
  const r=await fetch(UI,{headers:{"Accept":"text/html"},cf:{cacheTtl:3600,cacheEverything:true}});
  if(!r.ok)throw new Error("Preview HTML HTTP "+r.status);
  page=await r.text();pageAt=Date.now();return page;
}
export default {async fetch(request,env){
  const path=new URL(request.url).pathname;
  if(request.method!=="GET")return new Response("Method not allowed",{status:405,headers:{"Allow":"GET"}});
  if(path==="/manifest.webmanifest"){
    return new Response(JSON.stringify(APP_MANIFEST),{headers:{"content-type":"application/manifest+json;charset=utf-8",
      "cache-control":"public,max-age=3600","x-content-type-options":"nosniff"}});
  }
  if(path==="/icon.svg"){
    return new Response(APP_ICON,{headers:{"content-type":"image/svg+xml;charset=utf-8",
      "cache-control":"public,max-age=86400","x-content-type-options":"nosniff"}});
  }
  if(path==="/api/check"){
    const key=new URL(request.url).searchParams.get("key")||"";
    if(!/^[\w ().-]{1,190}\.mp4$/i.test(key))return Response.json({ok:false,reason:"Nome file non valido"},{status:400,headers:{"cache-control":"no-store"}});
    try{
      const probeUrl=LIB+"/download/"+encodeURIComponent(key);
      const opts={method:"GET",headers:{"Range":"bytes=0-1023","Accept":"video/mp4"}};
      const res=env?.VIDEO_LIBRARY
        ? await env.VIDEO_LIBRARY.fetch(new Request(probeUrl,opts))
        : await fetch(probeUrl,opts);
      const contentType=res.headers.get("content-type")||"";
      const contentRange=res.headers.get("content-range")||"";
      const attachment=res.headers.get("content-disposition")||"";
      const rangeValid=/^bytes 0-1023\/\d+$/.test(contentRange);
      const declaredLength=Number(res.headers.get("content-length"));
      const validHeaders=res.status===206&&rangeValid&&declaredLength===1024&&
        contentType.toLowerCase().startsWith("video/mp4")&&/attachment/i.test(attachment);
      const bytesRead=validHeaders?(await res.arrayBuffer()).byteLength:0;
      const ok=validHeaders&&bytesRead===1024;
      if(!ok&&res.body)await res.body.cancel();
      return Response.json({ok,http_status:res.status,range_ok:rangeValid,bytes_read:bytesRead,mime_ok:contentType.toLowerCase().startsWith("video/mp4"),
        tested_at:new Date().toISOString(),scope:"PRIMI 1024 BYTE; HASH E DOWNLOAD INTEGRALE NON VERIFICATI",
        download_url:ok?LIB+"/download/"+encodeURIComponent(key):null},
        {headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}});
    }catch(e){return Response.json({ok:false,error:"Verifica temporaneamente non disponibile"},{status:503,headers:{"cache-control":"no-store"}})}
  }
  if(path==="/api/integrity"){
    try{return Response.json(await getIntegrity(),{headers:{
      "cache-control":"no-store","x-content-type-options":"nosniff"}})}
    catch(e){return Response.json({schema:"studio-integrity-metadata-v9",source_ok:false,
      runs:[],report_contents_read:false,full_sha256_verified_by_dashboard:false,
      zip_crc_verified_by_dashboard:false,owner_approved:false,publish_authorized:false,
      error:"Audit GitHub temporaneamente non disponibile."},
      {status:503,headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}})}
  }
  if(path==="/api/quality"){
    try{return Response.json(await getQuality(env?.VIDEO_LIBRARY),{headers:{
      "cache-control":"no-store","x-content-type-options":"nosniff"}})}
    catch(e){return Response.json({schema:"artvision-quality-metadata-v8",source_ok:false,
      runs:[],report_contents_read:false,qa_pass_verified:false,mp4_bytes_verified:false,
      sha256_verified:false,owner_approved:false,publish_authorized:false,
      error:"GitHub QA metadata non disponibile; non equivale a test fallito."},
      {status:503,headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}})}
  }
  if(path==="/api/progress"){
    const id=new URL(request.url).searchParams.get("run")||"";
    if(!/^[1-9]\d{0,17}$/.test(id)){
      return Response.json({ok:false,reason:"ID run non valido"},
        {status:400,headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}});
    }
    try{
      const result=await getProductionProgress(id,env?.VIDEO_LIBRARY);
      return Response.json(result,{status:result.ok?200:404,headers:{
        "cache-control":"no-store","x-content-type-options":"nosniff"}});
    }catch{
      return Response.json({ok:false,reason:"Progresso GitHub temporaneamente non disponibile"},
        {status:503,headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}});
    }
  }
  if(path==="/api/diagnose"){
    const run=new URL(request.url).searchParams.get("run")||"";
    if(!/^[1-9]\d{0,17}$/.test(run)){
      return Response.json({ok:false,error:"ID run non valido"},{status:400,
        headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}});
    }
    try{
      const result=await getDiagnosis(run,env?.VIDEO_LIBRARY);
      return Response.json(result,{status:result.ok?200:404,
        headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}});
    }catch(e){
      return Response.json({ok:false,error:"Dettagli GitHub non raggiungibili"},{status:503,
        headers:{"cache-control":"no-store","x-content-type-options":"nosniff"}});
    }
  }
  if(path==="/api/status"){
    try{return Response.json(await getStatus(env?.VIDEO_LIBRARY),{headers:{"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}})}
    catch(e){return Response.json({error:"Fonti temporaneamente non disponibili"},{status:503,headers:{"Cache-Control":"no-store"}})}
  }
  if(path==="/"||path==="/index.html"){
    try{return new Response(await getPage(),{headers:{
      "Content-Type":"text/html;charset=UTF-8","Cache-Control":"no-cache","X-Content-Type-Options":"nosniff","Referrer-Policy":"no-referrer",
      "Content-Security-Policy":"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; manifest-src 'self'; img-src 'self' https://video-library-studio.600led.workers.dev data:; media-src https://video-library-studio.600led.workers.dev; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors https://video-library-studio.600led.workers.dev"
    }})}catch(e){return new Response("Anteprima temporaneamente non disponibile",{status:503})}
  }
  return new Response("Not found",{status:404});
}};