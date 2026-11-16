// Offline regression for genuine private R2 owner staging. No network, public uploads or secrets.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
globalThis.crypto ||= crypto.webcrypto;

async function main() {
  const src = fs.readFileSync('site/video-library-importer-with-editorial.js', 'utf8');
  assert(src.includes('const PRIVATE_WF='));
  assert(src.includes("new URL(req.url).pathname.startsWith('/private-')?[PRIVATE_WF]"),
    'Private OIDC workflow must not be added to the public route allowlist');
  assert(src.includes("if(!env.PRIVATE_ARCHIVE)return resp("),
    'Missing private binding must fail closed');
  const patched = src.replace('async function authorized(req){',
    'async function authorized(req){return true;} async function originalAuthorized(req){');
  const {default: worker} = await import('data:text/javascript;base64,'+
    Buffer.from(patched).toString('base64'));

  const privateObjects = new Map();
  let publicWrites = 0;
  const env = {
    VIDEOS: {async put(){publicWrites++;throw Error('PUBLIC BUCKET MUST NOT BE USED')}},
    PRIVATE_ARCHIVE: {
      async head(key) {
        const v = privateObjects.get(key);
        return v ? {size:v.bytes.byteLength,customMetadata:v.meta} : null;
      },
      async put(key, value, options) {
        assert.equal(options.customMetadata.visibility,'private_owner_review');
        assert(options.onlyIf?.etagDoesNotMatch==='*');
        assert(!privateObjects.has(key));
        const bytes = value instanceof ArrayBuffer ? new Uint8Array(value)
          : Uint8Array.from(value);
        privateObjects.set(key,{bytes,meta:options.customMetadata});
        return {size:bytes.byteLength};
      }
    }
  };
  const bytes=Buffer.alloc(2048);
  for(let i=0;i<bytes.length;i++)bytes[i]=i%251;
  const sha=crypto.createHash('sha256').update(bytes).digest('hex');
  const root='https://example.test/private-single?artifact=14156323297&key=TEST_VIDEO.mp4&sha256=';
  const invoke=(route,method,body, environment=env)=>worker.fetch(
    new Request(route,{method,body:method==='POST'?body:undefined}),environment);

  let result=await invoke(root+sha,'POST',bytes,{VIDEOS:env.VIDEOS});
  assert.equal(result.status,503,'Private binding absence fails closed');
  assert.equal(publicWrites,0);

  result=await invoke(root+'0'.repeat(64),'POST',bytes);
  assert.equal(result.status,400,'SHA mismatch refuses upload');
  assert.equal(privateObjects.size,0);

  result=await invoke(root+sha,'POST',bytes);
  assert.equal(result.status,200);
  const ok=await result.json();
  assert.equal(ok.private,true);
  assert.equal(ok.stored,true);
  assert.equal(ok.sha256,sha);
  assert.equal(ok.size,2048);
  assert.equal(privateObjects.size,1);
  assert.equal(publicWrites,0);
  assert(privateObjects.has('gh-artifacts/14156323297/TEST_VIDEO.mp4'));

  result=await invoke(root+sha,'POST',bytes);
  assert.equal(result.status,200);
  assert.equal((await result.json()).already_exists,true);

  const changed=Buffer.alloc(2048,4);
  const changedSha=crypto.createHash('sha256').update(changed).digest('hex');
  result=await invoke(root+changedSha,'POST',changed);
  assert.equal(result.status,409,'Existing object cannot be overwritten');
  assert.equal(privateObjects.size,1);

  result=await invoke('https://example.test/private-status?artifact=14156323297&key=TEST_VIDEO.mp4','GET');
  assert.equal(result.status,200);
  const state=await result.json();
  assert.deepEqual({private:state.private,size:state.size,sha256:state.sha256},
    {private:true,size:2048,sha256:sha});
  assert(!JSON.stringify(state).includes(bytes.toString('base64')));

  result=await invoke(root+sha,'GET');
  assert.equal(result.status,405,'No private video byte-serving route');

  result=await invoke('https://example.test/private-single?artifact=14156323297&key=SOURCE_SHOT_01.mp4&sha256='+sha,'POST',bytes);
  assert.equal(result.status,400,'Source footage cannot enter finished-video archive');
  result=await invoke('https://example.test/private-single?artifact=bad&key=TEST_VIDEO.mp4&sha256='+sha,'POST',bytes);
  assert.equal(result.status,400);
  assert.equal(publicWrites,0);

  console.log('PASS: private-only staging, exact SHA, owner OIDC route separation, no public bucket writes');
}
main().catch(error=>{console.error(error);process.exitCode=1});
