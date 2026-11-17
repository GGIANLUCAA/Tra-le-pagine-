// V336 — no-network regression tests for artifact proof endpoints.
// Run: node tests/artvision_import_proof_contract_v336.mjs
// The production OIDC authorization guard is replaced ONLY in this local VM test.
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const source = fs.readFileSync("site/video-library-importer-with-editorial.js", "utf8");
const authGuard = "try{if(!await authorized(request))return resp({error:'Not authorized'},401);}catch(e){return resp({error:'Authentication temporarily unavailable'},503);}";
assert.equal(source.split(authGuard).length - 1, 1, "Do not weaken production OIDC authentication.");
assert.ok(source.includes("if(route==='/artifact-proof'&&method==='GET')"));
assert.ok(source.includes("if(route==='/artifact-confirm'&&method==='POST')"));
const testSource = source.replace(authGuard, "/* TEST ONLY: OIDC bypass inside isolated Node VM */")
  .replace("export default{", "globalThis.__testedWorker={");
assert.notEqual(testSource, source);
const context = {
  URL,
  Date,
  Response: {json: (body, opts={}) => ({status:opts.status||200, body})},
};
vm.createContext(context);
vm.runInContext(testSource, context, {filename:"video-library-importer-with-editorial.js"});
const worker = context.__testedWorker;
assert.equal(typeof worker.fetch, "function");
const markers = new Map();
const videos = new Map([["FINAL.mp4", 123]]);
const env = {VIDEOS:{
  get: async key => markers.has(key) ? {json:async()=>JSON.parse(markers.get(key))} : null,
  head: async key => videos.has(key) ? {size:videos.get(key)} : null,
  put: async (key,body) => {markers.set(key, String(body));return {key};},
}};
const get = id => worker.fetch({url:"https://import.invalid/artifact-proof?artifact="+id,method:"GET"},env);
const post = (id,data) => worker.fetch({url:"https://import.invalid/artifact-confirm?artifact="+id,method:"POST",json:async()=>data},env);
let resp = await get("12345");
assert.equal(resp.body.state,"untracked");
assert.equal(resp.body.verified,false);
markers.set("sync/gh/12345.json",JSON.stringify({id:"12345",name:"ORIGINAL_LEGACY_MARKER"}));
resp = await get("12345");
assert.equal(resp.body.state,"legacy_unverified");
assert.equal(resp.body.synced,false);
resp = await post("12345",{name:"MASTER",state:"complete",files:[{key:"NOT_PRESENT.mp4",size:123,sha256:"a".repeat(64)}]});
assert.equal(resp.status,409,"No completed sync when the R2 object is absent");
resp = await post("12345",{name:"MASTER",state:"complete",files:[{key:"FINAL.mp4",size:123,sha256:"a".repeat(64)}]});
assert.equal(resp.status,200);
resp = await get("12345");
assert.equal(resp.body.state,"uploaded_verified");
assert.equal(resp.body.verified,true);
videos.set("FINAL.mp4",88);
resp = await get("12345");
assert.equal(resp.body.state,"missing_or_size_mismatch");
assert.equal(resp.body.verified,false);
resp = await post("55555",{name:"PRIVATE",state:"private_review"});
assert.equal(resp.body.synced,false);
resp = await get("55555");
assert.equal(resp.body.state,"private_review");
assert.equal(resp.body.synced,false);
resp = await post("66666",{name:"REJECTED",state:"blocked_rights"});
assert.equal(resp.body.synced,false);
resp = await post("77777",{name:"DELETED",state:"owner_deleted"});
assert.equal(resp.body.synced,false);
resp = await post("88888",{name:"DUP",state:"complete",files:[
  {key:"FINAL.mp4",size:88,sha256:"a".repeat(64)},
  {key:"FINAL.mp4",size:88,sha256:"a".repeat(64)}]});
assert.equal(resp.status,400,"Duplicate file references must fail");
const wf = fs.readFileSync(".github/workflows/video-library-r2-import.yml","utf8");
assert.match(wf, /recovery_left=6/);
assert.match(wf, /artifact-proof/);
assert.match(wf, /artifact-confirm/);
assert.ok(!wf.includes("cf('POST','/artifact-mark'"),"Legacy marker endpoint must not be used for new production");
console.log("PASS V336: 13 endpoint + workflow checks; no external calls, no publication.");
