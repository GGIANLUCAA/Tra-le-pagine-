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
