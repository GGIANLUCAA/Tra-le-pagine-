import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync,existsSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,resolve} from "node:path";
import worker, {validateDispatch,configured} from "../worker/index.mjs";

const root=resolve(dirname(fileURLToPath(import.meta.url)),"..");
const v6={workflow:"v6",inputs:{episodio:"03_siddharta",formato:"libri",budget:"zero"}};
const v7={workflow:"v7",inputs:{mode:"discover",provider:"openverse",kind:"image",query:"river India",asset_id:""}};
const v8={workflow:"v8",inputs:{episode:"03_siddharta",format:"libri",mode:"plan",gate1_approved:false}};
const render={workflow:"render",inputs:{episodio:"03_siddharta",effetti:"v4"},confirmed:true};

test("valid existing V6, V7, V8, render contracts",()=>{
  assert.equal(validateDispatch(v6).workflow,"studio-ibrido-v6.yml");
  assert.equal(validateDispatch(v7).workflow,"archivio-media-v7.yml");
  assert.equal(validateDispatch(v8).workflow,"orchestratore-v8.yml");
  assert.equal(validateDispatch(render).workflow,"render-v3.yml");
});
test("no arbitrary workflows, hidden options or shell injections",()=>{
  assert.throws(()=>validateDispatch({workflow:"my-evil.yml",inputs:{}}));
  assert.throws(()=>validateDispatch({...v6, inputs:{...v6.inputs,command:"curl bad"}}));
  assert.throws(()=>validateDispatch({...v6,inputs:{...v6.inputs,episodio:"../etc/secret"}}));
  assert.throws(()=>validateDispatch({...v6,inputs:{...v6.inputs,episodio:"foo;rm -rf"}}));
  assert.throws(()=>validateDispatch({...v6, extra:true}));
});
test("V8 prepare cannot bypass Gate 1",()=>{
  assert.throws(()=>validateDispatch({workflow:"v8",inputs:{...v8.inputs,mode:"prepare"}}));
  assert.throws(()=>validateDispatch({workflow:"v8",inputs:{...v8.inputs,mode:"prepare",gate1_approved:true}}));
  assert.equal(validateDispatch({workflow:"v8",inputs:{...v8.inputs,mode:"prepare",gate1_approved:true},confirmed:true}).workflow,
    "orchestratore-v8.yml");
});
test("Gemini render requires explicit affirmative confirmation",()=>{
  assert.throws(()=>validateDispatch({...render,confirmed:false}));
  assert.throws(()=>validateDispatch({...render,confirmed:undefined}));
  assert.throws(()=>validateDispatch({...render,inputs:{episodio:"03_siddharta",effetti:"danger"}}));
});
test("Openverse cannot import video, Pexels import requires a numeric ID",()=>{
  assert.throws(()=>validateDispatch({workflow:"v7",inputs:{...v7.inputs,kind:"video"}}));
  assert.throws(()=>validateDispatch({workflow:"v7",inputs:{...v7.inputs,mode:"import"}}));
  assert.equal(validateDispatch({workflow:"v7",inputs:{mode:"import",provider:"pexels",kind:"video",
    query:"river",asset_id:"1827"}}).workflow,"archivio-media-v7.yml");
});
test("Worker session absent without backend secrets",async()=>{
  assert.equal(configured({}),false);
  const env={ASSETS:{fetch:async()=>new Response("ok")}};
  const res=await worker.fetch(new Request("https://studio.example/api/session"),env);
  assert.equal(res.status,200);
  const obj=await res.json();
  assert.deepEqual(obj,{ready:false,authenticated:false,login:""});
});
test("Backend refuses unauthenticated workflow invocation",async()=>{
  const request=new Request("https://studio.example/api/dispatch",{
    method:"POST",headers:{Origin:"https://studio.example","Content-Type":"application/json"},
    body:JSON.stringify(v6)
  });
  const res=await worker.fetch(request,{ASSETS:{fetch:async()=>new Response("ok")}});
  assert.equal(res.status,401);
});
test("Backend blocks cross-origin dispatch attempts",async()=>{
  const req=new Request("https://studio.example/api/dispatch",{
    method:"POST",headers:{Origin:"https://bad.example","Content-Type":"application/json"},
    body:JSON.stringify(v6)
  });
  const res=await worker.fetch(req,{});
  assert.equal(res.status,403);
});
test("All shipped local PWA assets exist",()=>{
  for(const p of ["docs/index.html","docs/styles.css","docs/app.js","docs/icon.svg",
    "docs/sw.js","docs/manifest.webmanifest","docs/.nojekyll","wrangler.toml"]) {
    assert.equal(existsSync(resolve(root,p)),true,p+" must exist");
  }
});
test("Web interface carries out real actions without API keys in client",()=>{
  const html=readFileSync(resolve(root,"docs/index.html"),"utf8");
  const app=readFileSync(resolve(root,"docs/app.js"),"utf8");
  assert.match(html,/id="view-nuovo"/);
  assert.match(html,/id="view-produzioni"/);
  assert.match(html,/id="media-import"/);
  assert.match(app,/media-import/);
  assert.match(app,/\/api\/dispatch/);
  assert.match(app,/\/api\/session/);
  assert.match(app,/navigator\.clipboard/);
  assert.doesNotMatch(html+app,/GITHUB_CLIENT_SECRET|GEMINI_API_KEY|STUDIO_SESSION_SECRET/);
});
test("Cloudflare worker assets same origin and no arbitrary repo targets",()=>{
  const workerSrc=readFileSync(resolve(root,"worker/index.mjs"),"utf8");
  const config=readFileSync(resolve(root,"wrangler.toml"),"utf8");
  assert.match(config,/run_worker_first = true/);
  assert.match(workerSrc,/EXPECTED_USER = "ggianlucaa"/);
  assert.match(workerSrc,/HttpOnly; Secure; SameSite=Lax/);
  assert.match(workerSrc,/AES-GCM/);
  assert.match(workerSrc,/restrictOrigin/);
});
test("Original voice, render, and episode paths still present",()=>{
  for(const name of ["src/gemini_voice.py","src/render.py","src/episode_v3.py",
    "src/studio_ibrido_v6.py","src/archivio_media_v7.py","src/orchestratore_v8.py",
    ".github/workflows/render-v3.yml"]) {
    assert.ok(existsSync(resolve(root,name)),name);
  }
});


test("public video publishing requires explicit valid episode, run and confirmation",()=>{
  const payload={workflow:"publish",inputs:{episode:"01_scacchi",
    render_run_id:"39171898138",publish_public:true},confirmed:true};
  assert.equal(validateDispatch(payload).workflow,"pubblica-video-v11.yml");
  assert.throws(()=>validateDispatch({...payload,confirmed:false}));
  assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,publish_public:false}}));
  assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,render_run_id:"foo"}}));
  assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,episode:"../../secrets"}}));
  assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,extra:"x"}}));
});

test("AutoPilot BETA can only start with validated story and explicit quota approval",()=>{
 const payload={workflow:"autopilot",inputs:{
   title:"Viaggio attraverso il bosco",idea:"Una storia poetica di crescita e ricerca interiore, senza cronaca",
   formato:"fiabe",durata:"3",conferma_costi:true},confirmed:true};
 assert.equal(validateDispatch(payload).workflow,"studio-autopilot-v11.yml");
 assert.throws(()=>validateDispatch({...payload,confirmed:false}));
 assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,conferma_costi:false}}));
 assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,formato:"cronaca"}}));
 assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,durata:"120"}}));
 assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,idea:"no"}}));
 assert.throws(()=>validateDispatch({...payload,inputs:{...payload.inputs,idea:"hello\nbad"}}));
});
