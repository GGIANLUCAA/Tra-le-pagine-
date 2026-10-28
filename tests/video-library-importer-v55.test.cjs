// Offline tests for authenticated V55 production attachments.
// No Cloudflare credentials, paid calls or live deployment.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
globalThis.crypto ||= crypto.webcrypto;

async function main(){
 const original = fs.readFileSync('site/video-library-importer-with-editorial.js','utf8');
 assert(original.includes("async function authorized(req){"));
 const patched = original.replace("async function authorized(req){",
   "async function authorized(req){return true;} async function originalAuthorized(req){");
 const {default:worker} = await import('data:text/javascript;base64,'+Buffer.from(patched).toString('base64'));
 const data = new Map();
 const bytes = v => v instanceof Uint8Array ? v : new Uint8Array(v);
 const env = {VIDEOS: {
   async head(key){const x=data.get(key);return x?{key,size:x.length}:null},
   async get(key){const x=data.get(key);return x?{
     async arrayBuffer(){return Uint8Array.from(x).buffer},
     async json(){return JSON.parse(Buffer.from(x).toString('utf8'))}
   }:null},
   async put(key,buffer){const x=bytes(buffer);data.set(key,x);return {key,size:x.length}}
 }};
 const video='ARTVISION_V55_TEST.mp4';
 data.set(video,new Uint8Array([10,20,30]));
 const name='POST_FACEBOOK.txt',content=Buffer.from(
   'Un testo editoriale autentico dedicato a questa specifica opera e alla sua storia.');
 const hash=crypto.createHash('sha256').update(content).digest('hex');
 const link=(v=video,n=name,h=hash)=>
   'https://example.test/production-file?video='+encodeURIComponent(v)+'&name='+encodeURIComponent(n)+'&sha256='+h;
 const request=(url,body,method='POST')=>
   worker.fetch(new Request(url,{method,body:method==='POST'?body:undefined}),env);
 let response=await request(link(),content);
 assert.equal(response.status,200);
 let saved=await response.json();
 assert.equal(saved.sha256,hash);
 assert(saved.stored);
 const key='production/files/'+encodeURIComponent(video)+'/'+encodeURIComponent(name);
 assert.equal(Buffer.from(data.get(key)).toString('utf8'),content.toString('utf8'));
 response=await request(link(),content);
 assert.equal(response.status,200);
 assert((await response.json()).already_exists);
 response=await request(link(),Buffer.from('different bytes'));
 assert.equal(response.status,400);
 const altered=Buffer.from('A different editorial text that cannot overwrite the first version');
 const altHash=crypto.createHash('sha256').update(altered).digest('hex');
 response=await request(link(video,name,altHash),altered);
 assert.equal(response.status,409,'Curated content must be append-only');
 assert.equal(Buffer.from(data.get(key)).toString(),content.toString());
 response=await request(link('UNKNOWN.mp4'),content);
 assert.equal(response.status,409);
 response=await request(link(video,'../secret.txt'),content);
 assert.equal(response.status,400);
 response=await request(link(),undefined,'GET');
 assert.equal(response.status,200);
 assert((await response.json()).exists);
 response=await request(link(video,'PROJECT_V13.json',hash),content);
 assert.equal(response.status,200);
 console.log('PASS: V55 attachments hash-checked, scoped to MP4 and conflict-safe (mock auth only)');
}
main().catch(e=>{console.error(e);process.exitCode=1});
