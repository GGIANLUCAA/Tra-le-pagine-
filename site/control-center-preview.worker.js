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

async function json(url,github=false){
  const response=await fetch(url,{headers:github?{"Accept":"application/vnd.github+json","User-Agent":"ArtVision-ControlCenter-Readonly"}:{"Accept":"application/json"},cf:{cacheTtl:75,cacheEverything:true}});
  if(!response.ok)throw new Error("HTTP "+response.status);
  return response.json();
}
function clip(s,n=250){return typeof s==="string"?s.slice(0,n):""}

function projectForRun(name){
  const s=String(name||"").toLowerCase();
  // Infrastructure and dashboard jobs must never masquerade as video production.
  if(/control.center|video.library|library.studio|site.smoke|site.download|import|enrich|editorial.dossier|catalog/.test(s))return "site";
  if(/wow[\s_-]*lab/.test(s))return "wow";
  if(/storia[\s_-]*rivive|restauro.storic|restoration|storico/.test(s))return "storia";
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
  const projects=[["artvision","ArtVision 4×1"],["storia","La Storia Rivive"],["wow","WOW LAB"]];
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
        time:x.updated_at,link:x.html_url,project:x.project})),
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
    const byProject={artvision:0,storia:0,wow:0,site:0,other:0};
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

async function gather(){
  const results=await Promise.allSettled([
    json("https://api.github.com/repos/"+REPO+"/actions/runs?per_page=100",true),
    json("https://raw.githubusercontent.com/"+REPO+"/main/queue/artvision_owner_selected_ten_20261102.json"),
    json(LIB+"/api/catalog")
  ]);
  const keys=["github","queue","catalog"],sources={};
  results.forEach((r,i)=>{sources[keys[i]]=r.status==="fulfilled"?{ok:true}:{ok:false,error:clip(r.reason&&r.reason.message||"Non disponibile",80)}});
  const gh=results[0].status==="fulfilled"?results[0].value:{};
  const queue=results[1].status==="fulfilled"?results[1].value:{};
  const cat=results[2].status==="fulfilled"?results[2].value:{};
  const runs=(Array.isArray(gh.workflow_runs)?gh.workflow_runs:[]).map(r=>({
    name:clip(r.name,180),status:clip(r.status,32),conclusion:clip(r.conclusion,32),
    html_url:clip(r.html_url,280),updated_at:clip(r.updated_at,40),event:clip(r.event,40),
    head_branch:clip(r.head_branch,100),workflow_id:Number(r.workflow_id)||null,
    project:projectForRun(r.name)
  })).sort((a,b)=>Date.parse(b.updated_at||0)-Date.parse(a.updated_at||0));
  const rows=Array.isArray(cat.items)?cat.items.filter(x=>x&&typeof x==="object"&&x.hidden!==true):[];
  const catalogNames=new Set(rows.map(x=>String(x.key||x.name||"")));
  const catalogAvailability=new Map(rows.map(x=>[String(x.key||x.name||""),x.available===false?false:true]));
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
    key:clip(x.key||x.name,190),title:clip(x.title||x.name||x.key,180),available:x.available===false?false:true
  }));
  const overview=deriveOverview(runs,works,rows,sources);
  const statistics=buildStatistics(runs,works,rows,sources);
  return {asof:new Date().toISOString(),sources,runs,works,media,catalog_count:rows.length,statistics,...overview};
}
async function getStatus(){
  if(snapshot&&Date.now()-snapshotAt<75000)return snapshot;
  if(!pending)pending=gather().then(x=>{snapshot=x;snapshotAt=Date.now();return x}).finally(()=>{pending=null});
  return pending;
}
async function getPage(){
  if(page&&Date.now()-pageAt<3600000)return page;
  const r=await fetch(UI,{headers:{"Accept":"text/html"},cf:{cacheTtl:3600,cacheEverything:true}});
  if(!r.ok)throw new Error("Preview HTML HTTP "+r.status);
  page=await r.text();pageAt=Date.now();return page;
}
export default {async fetch(request){
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
      const res=await fetch(LIB+"/download/"+encodeURIComponent(key),{headers:{"Range":"bytes=0-1023","Accept":"video/mp4"}});
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
  if(path==="/api/status"){
    try{return Response.json(await getStatus(),{headers:{"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}})}
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