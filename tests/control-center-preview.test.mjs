import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {join,dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {runInNewContext,Script} from "node:vm";
const root=resolve(dirname(fileURLToPath(import.meta.url)),"..");
const html=readFileSync(join(root,"site/control-center-preview.html"),"utf8");
const backend=readFileSync(join(root,"site/control-center-preview.worker.js"),"utf8");
test("HTML and inline UI parse correctly",()=>{
  const match=html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(match);
  new Script(match[1]);
  assert.match(html,/data-page="works"/);
  assert.match(html,/data-page="issues"/);
  for(const page of ["todo","health","diary"])assert.ok(html.includes(`data-page="${page}"`));
  for(const fn of ["function todo()","function health()","function diary()"])assert.ok(html.includes(fn));
});
test("Backend only exposes GET and expected read-only endpoints",()=>{
  assert.match(backend,/if\(request.method!=="GET"\)/);
  assert.match(backend,/\/api\/status/);
  assert.match(backend,/\/api\/check/);
  new Script(backend.replace("export default","const WORKER = "));
});
function fixture(options={}){
  const queue={works:[
    {artist:"Hugo Simberg",title_en:"The Garden of Death",slots_delivered_this_selection:2,
      museum_approved:false,critico_standard_v146:{filename:"SIMBERG_CRITICO.mp4",sha256:"test"},
      v134_cinema_candidate:{mp4_filename:"SIMBERG_CINEMA.mp4",mp4_sha256:"test"}},
    {artist:"Salvador Dalí",title_en:"The Temptation of St. Anthony",slots_delivered_this_selection:0}
  ]};
  const catalog=options.catalog||{items:[{key:"SIMBERG_CRITICO.mp4",title:"Simberg Critico",uploaded:"2026-11-08T20:00:00Z"},
    {key:"SIMBERG_CINEMA.mp4",title:"Simberg Cinema",available:true}]};
  const runs={workflow_runs:options.runs||[{name:"ArtVision test",status:"completed",conclusion:"success",
    html_url:"https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/1",event:"push",updated_at:"2026-11-09T03:00:00Z"}]};
  const responses=[runs,options.queue||queue,catalog];
  async function fetchStub(url){
    const href=String(url);
    if(href.includes("/actions/runs/")&&href.includes("/jobs?")){
      const data=options.jobs||{jobs:[{name:"Render video",conclusion:"failure",
        html_url:"https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/123/job/456",
        steps:[{name:"Render FFmpeg",number:4,conclusion:"failure"},{name:"Upload",number:5,conclusion:"skipped"}]}]};
      return new Response(JSON.stringify(data),{status:200,headers:{"content-type":"application/json"}});
    }
    if(href.includes("/download/SIMBERG_CINEMA.mp4"))
      return new Response(new Uint8Array(1024),{status:206,headers:{"content-range":"bytes 0-1023/4096","content-length":"1024",
        "content-type":"video/mp4","content-disposition":'attachment; filename="SIMBERG_CINEMA.mp4"'}});
    const i=href.includes("/actions/runs?")?0:href.includes("/queue/artvision")?1:href.includes("/api/catalog")?2:-1;
    return new Response(JSON.stringify(responses[i]||{error:"not found"}),{status:i>=0?200:404,
      headers:{"content-type":"application/json"}});
  }
  const code=backend.replace("export default","const WORKER = ")+"\nWORKER;";
  return runInNewContext(code,{fetch:fetchStub,URL,Response,Date,console});
}
test("Status shows explicit evidence, excludes Dalí and returns four variants",async()=>{
  const worker=fixture();
  const res=await worker.fetch(new Request("https://preview.example/api/status"));
  assert.equal(res.status,200);
  const data=await res.json();
  assert.equal(data.works.length,1);
  assert.equal(data.works[0].delivered,2);
  assert.equal(data.works[0].variants.length,4);
  assert.equal(data.works[0].variants.filter(x=>x.recorded).length,2);
  assert.equal(data.works[0].variants.find(x=>x.id==="cinema_standard").site_catalog,true);
  assert.equal(data.runs.length,1);
});
test("V3 computes health and owner attention only from the latest main-branch workflow evidence",async()=>{
  const base="https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/";
  const runs=[
    {name:"La Storia Rivive · Produzione",workflow_id:22,head_branch:"main",status:"completed",conclusion:"success",updated_at:"2026-11-09T03:30:00Z",html_url:base+"101"},
    {name:"WOW LAB · Produzione",workflow_id:33,head_branch:"main",status:"completed",conclusion:"failure",updated_at:"2026-11-09T03:28:00Z",html_url:base+"102"},
    {name:"ArtVision 4×1 · Produzione",workflow_id:11,head_branch:"main",status:"completed",conclusion:"success",updated_at:"2026-11-09T03:25:00Z",html_url:base+"103"},
    {name:"ArtVision 4×1 · Produzione",workflow_id:11,head_branch:"main",status:"completed",conclusion:"failure",updated_at:"2026-11-09T03:10:00Z",html_url:base+"104"},
    {name:"Control Center · integrazione",workflow_id:99,head_branch:"preview",status:"completed",conclusion:"failure",updated_at:"2026-11-09T03:05:00Z",html_url:base+"105"}
  ];
  const worker=fixture({runs});
  const res=await worker.fetch(new Request("https://preview.example/api/status"));
  const data=await res.json();
  const artvision=data.health.find(x=>x.id==="artvision");
  const wow=data.health.find(x=>x.id==="wow");
  const story=data.health.find(x=>x.id==="storia");
  assert.equal(artvision.state,"observed_success","Recovered ArtVision failure is not an open issue");
  assert.equal(wow.state,"attention");
  assert.equal(wow.issues,1);
  assert.equal(story.state,"observed_success");
  assert.equal(data.attention.filter(x=>x.kind==="workflow").length,1);
  assert.ok(data.attention[0].title.includes("WOW LAB"));
  assert.equal(data.review.count,1,"Artistic review stays separate and nonurgent");
  assert.ok(data.diary.some(x=>x.type==="catalog"),"Only dated catalog events appear");
  assert.ok(data.diary.every(x=>Boolean(x.time)));
  assert.equal(data.scope.github_main_sample,4);
  assert.match(data.scope.caveat,/100/);
});
test("V3 never reports an unobserved production as stopped",async()=>{
  const worker=fixture({runs:[]});
  const data=await (await worker.fetch(new Request("https://preview.example/api/status"))).json();
  assert.ok(data.health.every(x=>x.state==="unobserved"));
  assert.equal(data.attention.filter(x=>x.kind==="workflow").length,0);
  assert.equal(data.diary.filter(x=>x.type==="workflow").length,0);
});
test("V4 exposes only catalogued and available real MP4 URLs for playback",async()=>{
  const queue={works:[
    {id:"test_artwork",artist:"Hugo Simberg",title_en:"The Garden of Death",slots_delivered_this_selection:3,
      museum_approved:false,Gold_V25:false,
      critico_standard_v146:{filename:"SIMBERG_CRITICO.mp4",sha256:"a".repeat(64),
        ffmpeg_full_decode:"PASS independent test",zip_crc:"PASS",
        site_full_download_sha256:"PASS exact sha256",site_download_HTTP_206:"PASS",
        human_artistic_review:"PENDING",gold_v25:false,bytes:5242880,run_id:1001},
      critico_museum_v150:{filename:"SIMBERG_MUSEUM.mp4",sha256:"b".repeat(64)},
      v134_cinema_candidate:{mp4_filename:"SIMBERG_CINEMA.mp4",mp4_sha256:"c".repeat(64),
        site_full_download_sha256:"PENDING_HTTP_PROBE",zip_crc:"FAIL"},
      cinema_museum_v190:{mp4_sha256:"d".repeat(64),status:"rendered but no public filename"}
    },
    {artist:"Salvador Dalí",title_en:"The Temptation of St. Anthony",slots_delivered_this_selection:0}
  ]};
  const catalog={items:[
    {key:"SIMBERG_CRITICO.mp4",available:true},
    {key:"SIMBERG_CINEMA.mp4",available:false},
    {key:"HIDDEN.mp4",hidden:true,available:true}
  ]};
  const worker=fixture({queue,catalog});
  const data=await (await worker.fetch(new Request("https://preview.example/api/status"))).json();
  assert.equal(data.works.length,1,"Dalí remains out of operating queue");
  const v=data.works[0].variants;
  assert.equal(v.length,4);
  const standard=v.find(x=>x.id==="critico_standard");
  assert.equal(standard.preview_ready,true);
  assert.equal(standard.media_url,"https://video-library-studio.600led.workers.dev/media/SIMBERG_CRITICO.mp4");
  assert.equal(standard.qa.sha_recorded,true);
  assert.equal(standard.qa.decode_documented,true);
  assert.equal(standard.qa.zip_documented,true);
  assert.equal(standard.qa.site_full_sha_documented,true);
  assert.equal(standard.qa.gold_approved,false);
  assert.equal(standard.details.bytes,5242880);
  const offline=v.find(x=>x.id==="cinema_standard");
  assert.equal(offline.site_catalog,true);
  assert.equal(offline.preview_ready,false);
  assert.equal(offline.media_url,null);
  assert.equal(offline.qa.zip_documented,false,"FAIL is not a pass");
  assert.equal(offline.qa.site_full_sha_documented,false,"PENDING is not a pass");
  const missing=v.find(x=>x.id==="critico_museum");
  assert.equal(missing.site_catalog,false);
  assert.equal(missing.media_url,null);
  const unidentified=v.find(x=>x.id==="cinema_museum");
  assert.equal(unidentified.recorded,true);
  assert.equal(unidentified.filename,"");
  assert.equal(unidentified.preview_ready,false);
});
test("V4 prefers explicitly active newer cinema replacement over outdated variants",async()=>{
  const queue={works:[{id:"bruegel",title_en:"The Fall of the Rebel Angels",artist:"Pieter Bruegel",
    slots_delivered_this_selection:2,active_cinema_standard:"new_cinema_standard_v153",
    new_cinema_standard_v135:{filename:"OLD_V135.mp4",sha256:"a".repeat(64)},
    new_cinema_standard_v153:{filename:"REPLACEMENT_V153.mp4",sha256:"b".repeat(64)},
    critico_standard_v144:{filename:"CRITICO.mp4",sha256:"c".repeat(64)}}]};
  const catalog={items:[{key:"REPLACEMENT_V153.mp4",available:true}]};
  const data=await (await fixture({queue,catalog}).fetch(new Request("https://preview.example/api/status"))).json();
  const cinema=data.works[0].variants.find(x=>x.id==="cinema_standard");
  assert.equal(cinema.source,"new_cinema_standard_v153");
  assert.equal(cinema.filename,"REPLACEMENT_V153.mp4");
  assert.equal(cinema.preview_ready,true);
});
test("V4 mobile player markup is present and CSP permits only original video host",()=>{
  assert.match(html,/id="reviewPlayer"/);
  assert.match(html,/id="reviewVideo"/);
  assert.match(html,/class="slotGrid"/);
  assert.match(html,/data-play=/);
  assert.match(html,/function closeReviewPlayer/);
  assert.match(backend,/media-src https:\/\/video-library-studio\.600led\.workers\.dev/);
  assert.match(backend,/frame-ancestors https:\/\/video-library-studio\.600led\.workers\.dev/);
  assert.match(backend,/if\(request.method!=="GET"\)/);
});
test("V5 statistics use actual dated sample, not inferred video output",async()=>{
  const stamp=hours=>new Date(Date.now()-hours*3600000).toISOString();
  const runs=[
    {name:"ArtVision 4×1 · Produzione",workflow_id:11,head_branch:"main",status:"completed",conclusion:"success",updated_at:stamp(3)},
    {name:"WOW LAB · Produzione",workflow_id:22,head_branch:"main",status:"completed",conclusion:"failure",updated_at:stamp(8)},
    {name:"La Storia Rivive · Produzione",workflow_id:33,head_branch:"main",status:"completed",conclusion:"success",updated_at:stamp(48)},
    {name:"Control Center tests",workflow_id:44,head_branch:"preview/test",status:"completed",conclusion:"failure",updated_at:stamp(4)},
    {name:"Old archive run",workflow_id:55,head_branch:"main",status:"completed",conclusion:"success",updated_at:stamp(250)}
  ];
  const catalog={items:[
    {key:"ONE.mp4",uploaded:stamp(27),available:true},
    {key:"TWO.mp4",uploaded:stamp(9*24),available:false},
    {key:"THREE.mp4",available:null}
  ]};
  const worker=fixture({runs,catalog});
  const data=await (await worker.fetch(new Request("https://preview.example/api/status"))).json();
  assert.equal(data.statistics.activity_24h.observed,2);
  assert.equal(data.statistics.activity_24h.successful,1);
  assert.equal(data.statistics.activity_24h.failed,1);
  assert.equal(data.statistics.activity_7d.observed,3);
  assert.equal(data.statistics.activity_7d.by_project.artvision,1);
  assert.equal(data.statistics.activity_7d.by_project.storia,1);
  assert.equal(data.statistics.activity_7d.by_project.wow,1);
  assert.equal(data.statistics.catalogue.entries,3);
  assert.equal(data.statistics.catalogue.explicitly_available,1);
  assert.equal(data.statistics.catalogue.explicitly_offline,1);
  assert.equal(data.statistics.catalogue.availability_unknown,1);
  assert.equal(data.statistics.catalogue.dated_imports_7d,1);
  assert.equal(data.statistics.artvision.expected_slots,4);
  assert.equal(data.statistics.artvision.registered_deliveries,2);
  assert.match(data.statistics.scope.github_window,/100/);
});
test("V5 has both top metrics and analytics page, plus gallery filters",()=>{
  assert.equal((html.match(/function stats\(\)/g)||[]).length,1);
  assert.equal((html.match(/function statisticsPage\(\)/g)||[]).length,1);
  assert.match(html,/data-page="stats"/);
  assert.match(html,/data-stats-window="24h"/);
  assert.match(html,/data-work-filter="playable"/);
  assert.match(html,/data-work-filter="missing"/);
  assert.match(html,/id="workSearch"/);
});
test("V5 never enables player when catalog availability is not declared",async()=>{
  const queue={works:[{id:"mystery",artist:"Painter",title_en:"Unknown",
    slots_delivered_this_selection:1,critico_standard_v111:{filename:"KNOWN.mp4",sha256:"a".repeat(64)}}]};
  const catalog={items:[{key:"KNOWN.mp4",title:"Known, but availability not confirmed"}]};
  const worker=fixture({queue,catalog});
  const response=await worker.fetch(new Request("https://preview.example/api/status"));
  const data=await response.json();
  const v=data.works[0].variants.find(x=>x.id==="critico_standard");
  assert.equal(v.site_catalog,true);
  assert.equal(v.site_available,null);
  assert.equal(v.preview_ready,false);
  assert.equal(v.media_url,null);
  assert.equal(data.statistics.catalogue.availability_unknown,1);
});
test("V5 Android manifest provides a standalone icon and never writes video data",async()=>{
  const worker=fixture();
  const manifest=await worker.fetch(new Request("https://preview.example/manifest.webmanifest"));
  assert.equal(manifest.status,200);
  const app=await manifest.json();
  assert.equal(app.name,"ArtVision Control Center");
  assert.equal(app.display,"standalone");
  assert.ok(app.icons.some(x=>x.sizes==="192x192"));
  assert.ok(app.icons.some(x=>x.sizes==="512x512"));
  const icon=await worker.fetch(new Request("https://preview.example/icon.svg"));
  assert.equal(icon.status,200);
  assert.match(await icon.text(),/<svg/);
  assert.match(backend,/manifest-src 'self'/);
  assert.match(html,/rel="manifest"/);
  const deny=await worker.fetch(new Request("https://preview.example/api/status",{method:"POST"}));
  assert.equal(deny.status,405);
});
test("V6 diagnose returns only public run jobs from the observed GitHub sample",async()=>{
  const id=123;
  const runs=[{id,name:"WOW LAB · Produzione",workflow_id:7,head_branch:"main",
    status:"completed",conclusion:"failure",event:"schedule",updated_at:"2026-11-09T06:10:00Z",
    html_url:"https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/123"}];
  const worker=fixture({runs});
  const result=await worker.fetch(new Request("https://preview.example/api/diagnose?run=123"));
  assert.equal(result.status,200);
  const data=await result.json();
  assert.equal(data.run_id,id);
  assert.equal(data.jobs_available,true);
  assert.equal(data.jobs.length,1);
  assert.equal(data.jobs[0].name,"Render video");
  assert.equal(data.jobs[0].failed_steps[0].name,"Render FFmpeg");
  assert.equal(data.jobs[0].failed_steps.length,1,"Do not show skipped steps as errors");
  assert.ok(data.run_url.startsWith("https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/123"));
  const missing=await worker.fetch(new Request("https://preview.example/api/diagnose?run=999"));
  assert.equal(missing.status,404,"No arbitrary run lookup");
  const invalid=await worker.fetch(new Request("https://preview.example/api/diagnose?run=not-a-run"));
  assert.equal(invalid.status,400);
  const write=await worker.fetch(new Request("https://preview.example/api/diagnose?run=123",{method:"POST"}));
  assert.equal(write.status,405);
});
test("V6 only recognizes continuable private ChatGPT URLs, not shared snapshots",()=>{
  const start=html.indexOf("function allowedChatUrl(value){");
  const end=html.indexOf("function loadChats(){",start);
  assert.ok(start>0&&end>start);
  const checker=runInNewContext(html.slice(start,end)+"\nallowedChatUrl;",{URL});
  assert.equal(checker("https://chatgpt.com/c/12345678-abcd-1234-abcd-123456789abc"),
    "https://chatgpt.com/c/12345678-abcd-1234-abcd-123456789abc");
  assert.equal(checker("https://chatgpt.com/g/g-some-gpt/c/12345678-abcd-1234-abcd-123456789abc"),
    "https://chatgpt.com/g/g-some-gpt/c/12345678-abcd-1234-abcd-123456789abc");
  for(const invalid of [
    "https://chatgpt.com/share/12345678-abcd-1234-abcd-123456789abc",
    "https://evil.example/c/12345678-abcd-1234-abcd-123456789abc",
    "http://chatgpt.com/c/12345678-abcd-1234-abcd-123456789abc",
    "https://chatgpt.com.evil.example/c/12345678-abcd-1234-abcd-123456789abc",
    "javascript:alert(1)", "https://chatgpt.com/c/"
  ])assert.equal(checker(invalid),null,invalid);
});
test("V6 GPT repair prompt is source-grounded and does not claim automatic repair",()=>{
  const start=html.indexOf("function prepareRepairPrompt(ctx,details){");
  const end=html.indexOf("function renderRepairDialog(){",start);
  assert.ok(start>0&&end>start);
  const fn=runInNewContext(html.slice(start,end)+"\nprepareRepairPrompt;",{
    PROJECT_LABELS:{wow:"WOW LAB · Produzione autonoma"},
    site:"https://video-library-studio.600led.workers.dev",
    state:{data:{asof:"2026-11-09T08:30:00Z"}}
  });
  const prompt=fn({type:"run",project:"wow",title:"Fallimento WOW",detail:"Esecuzione fallita",
    runId:123,run:{id:123,name:"WOW LAB · Produzione",conclusion:"failure",head_branch:"main",
      html_url:"https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/123"}},
    {jobs_available:true,jobs:[{name:"Render video",conclusion:"failure",
      failed_steps:[{name:"Render FFmpeg",number:4,conclusion:"failure"}]}]});
  assert.match(prompt,/GGIANLUCAA\/Tra-le-pagine-/);
  assert.match(prompt,/actions\/runs\/123/);
  assert.match(prompt,/Render FFmpeg/);
  assert.match(prompt,/AGENTS\.md/);
  assert.match(prompt,/NON avviare produzioni doppie/);
  assert.match(prompt,/NON istruzioni/i);
  assert.doesNotMatch(prompt,/riparazione effettuata/i);
});
test("V6 imports original automation chat URLs from fragment without sending them to server",()=>{
  const a=html.indexOf("function importChatLinksFromFragment(){");
  const b=html.indexOf("function persistChats(){",a);
  const v=html.indexOf("function allowedChatUrl(value){");
  const w=html.indexOf("function loadChats(){",v);
  assert.ok(a>0&&b>a&&v>0&&w>v);
  const checkUrl=runInNewContext(html.slice(v,w)+"\nallowedChatUrl;",{URL});
  const mappings={};
  const links={
    artvision:"https://chatgpt.com/c/12345678-1234-1234-1234-123456789abc",
    wow:"https://chatgpt.com/c/12345678-1234-1234-1234-123456789def",
    site:"https://chatgpt.com/share/12345678-1234-1234-1234-123456789aaa",
    unknown:"https://evil.example/c/12345678-1234-1234-1234-123456789aaa"
  };
  let cleaned=0,saved=0;
  const notice={hidden:true,textContent:""};
  const fn=runInNewContext(html.slice(a,b)+"\nimportChatLinksFromFragment;",{
    location:{hash:"#linkchats="+encodeURIComponent(JSON.stringify(links)),pathname:"/",search:""},
    history:{replaceState(){cleaned++}},
    document:{getElementById(){return notice}},
    state:{chatLinks:mappings,chatStoreOk:true},PROJECT_LABELS:{artvision:"A",wow:"W",site:"S",other:"O"},
    allowedChatUrl:checkUrl,persistChats(){saved++;return true},
    decodeURIComponent
  });
  fn();
  assert.equal(mappings.artvision,links.artvision);
  assert.equal(mappings.wow,links.wow);
  assert.equal(mappings.site,undefined,"Public shared links must not be imported");
  assert.equal(mappings.unknown,undefined);
  assert.equal(cleaned,1,"Private fragment should be cleared from the address bar");
  assert.equal(saved,1);
  assert.match(notice.textContent,/2 chat/);
});
test("Android GPT intent targets the original conversation and includes an HTTPS fallback",()=>{
  const begin=html.indexOf('var ANDROID_APP_PACKAGE=');
  const end=html.indexOf('function loadChats(){',begin);
  assert.ok(begin>=0&&end>begin);
  const result=runInNewContext(html.slice(begin,end)+"\n({androidChatGPTIntent,isAndroidDevice});",{
    URL,
    navigator:{userAgent:"Mozilla/5.0 (Linux; Android 16; Mobile) Chrome/141"}
  });
  const chat="https://chatgpt.com/c/12345678-1234-1234-1234-123456789abc";
  const intent=result.androidChatGPTIntent(chat,false);
  assert.equal(result.isAndroidDevice(),true);
  assert.ok(intent.startsWith("intent://chatgpt.com/c/12345678-1234-1234-1234-123456789abc#Intent;"));
  assert.match(intent,/scheme=https;package=com\.openai\.chatgpt;/);
  assert.match(intent,/S\.browser_fallback_url=https%3A%2F%2Fchatgpt\.com%2Fc%2F12345678-1234-1234-1234-123456789abc;end$/);
  assert.equal(result.androidChatGPTIntent("https://chatgpt.com/share/12345678-1234-1234-1234-123456789abc",false),null);
  assert.equal(result.androidChatGPTIntent("https://evil.example/c/12345678-1234-1234-1234-123456789abc",false),null);
  const home=result.androidChatGPTIntent("https://chatgpt.com/",true);
  assert.match(home,/^intent:\/\/chatgpt\.com\/#Intent;scheme=https;package=com\.openai\.chatgpt;/);
  assert.match(home,/S\.browser_fallback_url=https%3A%2F%2Fchatgpt\.com%2F;end$/);
});
test("Android app and browser choices are both present in repair dialog and project directory",()=>{
  assert.match(html,/id="openRelatedChatApp"/);
  assert.match(html,/id="openNewGPTApp"/);
  assert.match(html,/id="openRelatedChat"/);
  assert.match(html,/id="openNewGPT"/);
  assert.match(html,/Apri nell.app ChatGPT/);
  assert.match(html,/androidChatGPTIntent\(preferred,false\)/);
  assert.match(html,/androidChatGPTIntent\(state\.chatLinks\[key\],false\)/);
  assert.match(html,/id="androidAppHint"/);
  assert.match(html,/isAndroidDevice\(\)/);
});
test("V6 repair centre has GPT links, original-chat mapping and clipboard fallback",()=>{
  assert.match(html,/id="repairDialog"/);
  assert.match(html,/data-page="issues"/);
  assert.match(html,/data-repair-issue/);
  assert.match(html,/data-repair-run/);
  assert.match(html,/data-repair-work/);
  assert.match(html,/id="copyRepairPrompt"/);
  assert.match(html,/document\.execCommand\("copy"\)/);
  assert.match(html,/localStorage\.setItem\(CHAT_MAP_STORAGE_KEY/);
  assert.match(html,/id="repairChatScope"/);
  assert.match(html,/href="https:\/\/chatgpt\.com\/"/);
  assert.match(html,/saveRepairChat/);
});
test("V7 all categories preserve actual catalog counts and narrated book aliases",async()=>{
  const catalog={items:[
    {key:"TRA_LE_PAGINE_EP03_SIDDHARTA.mp4",category:"Libri raccontati",available:true},
    {key:"LA_COLLANA_VIDEO_FINALE.mp4",category:"Libri raccontati",available:true},
    {key:"NILS_CLIP_01_IL_PRIMO_VOLO.mp4",available:false},
    {key:"ARROSEUR_1895_CINEMA_RESTORED.mp4",available:true},
    {key:"WOW_LAB_TEST.mp4",available:null},
    {key:"ARTVISION_BOSCH_CINEMA_V6.mp4",category:"Artisti e pittura",available:true},
    {key:"SOURCE_SHOT_05__8973.mp4",available:true}
  ]};
  const data=await (await fixture({catalog}).fetch(new Request("https://preview.example/api/status"))).json();
  assert.equal(data.collections.length,13);
  const m=new Map(data.collections.map(x=>[x.name,x]));
  assert.equal(m.get("Libri narrati").count,2);
  assert.equal(m.get("Libri narrati").available,2);
  assert.equal(m.get("Racconti e fiabe").count,1);
  assert.equal(m.get("Racconti e fiabe").unavailable,1);
  assert.equal(m.get("Restauri storici").count,1);
  assert.equal(m.get("WOW LAB").count,1);
  assert.equal(m.get("WOW LAB").unknown,1);
  assert.equal(m.get("Artisti e pittura").count,1);
  assert.equal(m.get("Provini e backstage").count,1);
  assert.equal(m.get("Documentari e curiosità").count,0);
  assert.ok(m.get("Libri narrati").items[0].key.endsWith(".mp4"));
  assert.equal(data.catalog_count,7);
});
test("V7 categories remain unknown if public catalog fails and UI has no eight-card limit",()=>{
  assert.match(backend,/function summarizeCollections/);
  assert.match(backend,/if\(!available\)return null/);
  assert.match(backend,/COLLECTION_NAMES/);
  assert.match(html,/data-page="genres"/);
  assert.match(html,/function genreSection\(\)/);
  assert.match(html,/function genres\(\)/);
  assert.match(html,/selectedGenre:"Libri narrati"/);
  assert.match(html,/data-genre/);
  assert.match(html,/In preparazione/);
  assert.match(html,/\/\?category=/);
});
test("On-demand range probe does not claim full SHA",async()=>{
  const worker=fixture();
  const res=await worker.fetch(new Request("https://preview.example/api/check?key=SIMBERG_CINEMA.mp4"));
  assert.equal(res.status,200);
  const data=await res.json();
  assert.equal(data.ok,true);
  assert.match(data.scope,/NON VERIFICATI/);
  assert.ok(data.download_url.startsWith("https://video-library-studio.600led.workers.dev/download/"));
});
test("Reject writes and invalid file keys",async()=>{
  const worker=fixture();
  const put=await worker.fetch(new Request("https://preview.example/api/status",{method:"POST"}));
  assert.equal(put.status,405);
  const bad=await worker.fetch(new Request("https://preview.example/api/check?key=..%2Fsecret.txt"));
  assert.equal(bad.status,400);
});
