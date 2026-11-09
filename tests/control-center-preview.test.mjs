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
});
test("Backend only exposes GET and expected read-only endpoints",()=>{
  assert.match(backend,/if\(request.method!=="GET"\)/);
  assert.match(backend,/\/api\/status/);
  assert.match(backend,/\/api\/check/);
  new Script(backend.replace("export default","const WORKER = "));
});
function fixture(){
  const queue={works:[
    {artist:"Hugo Simberg",title_en:"The Garden of Death",slots_delivered_this_selection:2,
      museum_approved:false,critico_standard_v146:{filename:"SIMBERG_CRITICO.mp4",sha256:"test"},
      v134_cinema_candidate:{mp4_filename:"SIMBERG_CINEMA.mp4",mp4_sha256:"test"}},
    {artist:"Salvador Dalí",title_en:"The Temptation of St. Anthony",slots_delivered_this_selection:0}
  ]};
  const catalog={items:[{key:"SIMBERG_CRITICO.mp4",title:"Simberg Critico"},
    {key:"SIMBERG_CINEMA.mp4",title:"Simberg Cinema",available:true}]};
  const runs={workflow_runs:[{name:"ArtVision test",status:"completed",conclusion:"success",
    html_url:"https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/1",event:"push",updated_at:"2026-11-09T03:00:00Z"}]};
  const responses=[runs,queue,catalog];
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
