/* ArtVision Control Center V1 — separate read-only preview. No account secrets, no writes. */
const REPO="GGIANLUCAA/Tra-le-pagine-";
const LIB="https://video-library-studio.600led.workers.dev";
const UI="https://raw.githubusercontent.com/GGIANLUCAA/Tra-le-pagine-/e7b4b9f4b97e51426be7f0fcb32b635020f5d669/site/control-center-preview.html";
let snapshot=null,snapshotAt=0,pending=null,page=null,pageAt=0;
async function json(url,github=false){
  const response=await fetch(url,{headers:github?{"Accept":"application/vnd.github+json","User-Agent":"ArtVision-ControlCenter-Readonly"}:{"Accept":"application/json"},cf:{cacheTtl:75,cacheEverything:true}});
  if(!response.ok)throw new Error("HTTP "+response.status);
  return response.json();
}
function clip(s,n=250){return typeof s==="string"?s.slice(0,n):""}
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
    html_url:clip(r.html_url,280),updated_at:clip(r.updated_at,40),event:clip(r.event,40)
  }));
  const rows=Array.isArray(cat.items)?cat.items.filter(x=>x&&typeof x==="object"&&x.hidden!==true):[];
  const catalogNames=new Set(rows.map(x=>String(x.key||x.name||"")));
  const catalogAvailability=new Map(rows.map(x=>[String(x.key||x.name||""),x.available===false?false:true]));
  const slotDefs=[
    {id:"critico_standard",label:"Critico · Classico",patterns:[/^critico_standard_v\d+$/]},
    {id:"critico_museum",label:"Critico · Museum",patterns:[/^critico_museum_v\d+$/]},
    {id:"cinema_standard",label:"Cinema · Classico",patterns:[/^(?:new_)?cinema_standard_v\d+$/,/^v\d+_cinema_candidate$/]},
    {id:"cinema_museum",label:"Cinema · Museum",patterns:[/^cinema_museum_v\d+$/]}
  ];
  const pickSlot=(w,definition)=>{
    const found=Object.entries(w).filter(([key,val])=>
      definition.patterns.some(re=>re.test(key))&&val&&typeof val==="object"&&
      (val.filename||val.mp4_filename||val.file||val.sha256||val.mp4_sha256));
    // Prefer a specifically marked active slot when present; otherwise highest version.
    found.sort((a,b)=>{
      const active=w.active_cinema_standard;
      if(a[0]===active)return -1;if(b[0]===active)return 1;
      return (Number((b[0].match(/v(\d+)/)||[])[1])||0)-(Number((a[0].match(/v(\d+)/)||[])[1])||0);
    });
    const [source,record]=found[0]||["",{}];
    const filename=clip(record.filename||record.mp4_filename||record.file,190);
    const validFile=/^[\w ().-]{1,190}\.mp4$/i.test(filename)?filename:"";
    const siteFound=!!validFile&&catalogNames.has(validFile);
    const qa=!!(record.sha256||record.mp4_sha256)&&!!validFile;
    const recorded=!!source;
    const onSite=siteFound?catalogAvailability.get(validFile):null;
    return {id:definition.id,label:definition.label,recorded,source,filename:validFile,
      has_sha:qa,site_catalog:siteFound,site_available:onSite,
      technical_status:clip(record.status||"",120),run_id:Number(record.run_id||record.github_run_id||record.source_run_id)||null};
  };
  const works=(Array.isArray(queue.works)?queue.works:[])
    .filter(w=>!/dal[ií]|temptation of st\.?\s*anthony/i.test(String(w.artist||"")+" "+String(w.title_en||"")))
    .map(w=>({id:clip(w.id),title:clip(w.title_en),artist:clip(w.artist),
      delivered:Number(w.slots_delivered_this_selection)||0,museum_approved:w.museum_approved===true,
      note:clip(w.preflight_status,340),site_archive_verified_slots:
        Number.isFinite(Number(w.site_archive_verified_slots))?Number(w.site_archive_verified_slots):null,
      variants:slotDefs.map(s=>pickSlot(w,s))}));
  const media=rows.slice().sort((a,b)=>Date.parse(b.uploaded||b.gptCreatedAt||0)-Date.parse(a.uploaded||a.gptCreatedAt||0)).slice(0,24).map(x=>({
    key:clip(x.key||x.name,190),title:clip(x.title||x.name||x.key,180),available:x.available===false?false:true
  }));
  return {asof:new Date().toISOString(),sources,runs,works,media,catalog_count:rows.length};
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
      "Content-Security-Policy":"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src https://video-library-studio.600led.workers.dev data:; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors https://video-library-studio.600led.workers.dev"
    }})}catch(e){return new Response("Anteprima temporaneamente non disponibile",{status:503})}
  }
  return new Response("Not found",{status:404});
}};