import assert from 'node:assert/strict';
import {Buffer} from 'node:buffer';
import worker from './workspace-base.mjs';

// Offline simulation. No Cloudflare credentials, no real uploads/deletes.
const OLD='ARTVISION_PIRANESI_CINEMA_V6.mp4';
const KEEP='ArtVision_WOW7_Piranesi_Le_Prigioni_Impossibili.mp4';
const SIZE=41361075;
const ETAG='2596f0317268b24c3eeefb522a03ab09-5';
const ORIGIN='https://video-library-studio.example.test';

function fakeR2({hasOld=false,keepEtag=ETAG,keepSize=SIZE,
                removed=false,hiddenOld=false,hiddenKeep=false,
                lackMetadata=false,metadataError=false}={}) {
 const touched={head:[],get:[]};
 const manage={[OLD]:hiddenOld?{hidden:true}:undefined,
               [KEEP]:hiddenKeep?{hidden:true}:undefined};
 const deleted=removed?{[OLD]:{reason:'owner intentionally deleted'}}:{};
 const valid=(key)=>key===KEEP||(key===OLD&&hasOld);
 return {touched,
   async head(key) {
     touched.head.push(key);
     if(!valid(key))return null;
     return {size:key===KEEP?keepSize:SIZE,etag:key===KEEP?keepEtag:ETAG};
   },
   async get(key,options={}) {
     touched.get.push(key);
     if(key==='catalog/manage.json'||key==='catalog/deleted.json') {
       if(lackMetadata)return null;
       if(metadataError)throw Error('R2 temporarily unavailable');
       const doc=key.endsWith('/manage.json')?manage:deleted;
       return {async json(){return doc}};
     }
     if(key==='catalog/info.json')return {async json(){return {}}};
     if(!valid(key))return null;
     const slice=options?.range?1024:SIZE;
     const body=Buffer.alloc(slice>1024?1024:slice,42);
     return {
       body,size:key===KEEP?keepSize:SIZE,etag:key===KEEP?keepEtag:ETAG,
       httpEtag:'"'+ETAG+'"',
       range:{offset:0,length:1024},
       writeHttpMetadata(h){h.set('content-type','video/mp4')}
     };
   }
 };
}

async function call(route,env,range=false) {
 const headers=range?{'Range':'bytes=0-1023'}:{};
 return worker.fetch(new Request(ORIGIN+route,{headers}),{VIDEOS:env});
}

const clean=fakeR2();
for(const route of ['/media/','/download/','/watch/','/info/','/download-info/']){
 const res=await call(route+encodeURIComponent(OLD),clean,true);
 assert.equal(res.status,307,route+' must preserve old URL while old object is absent');
 assert.equal(res.headers.get('cache-control'),'no-store');
 const loc=new URL(res.headers.get('location'));
 assert.equal(loc.origin,ORIGIN);
 assert.equal(decodeURIComponent(loc.pathname),route+KEEP);
}
// Following the redirect with the original Range header still returns HTTP 206.
const redirect=await call('/media/'+OLD,fakeR2(),true);
const followed=await call(new URL(redirect.headers.get('location')).pathname,fakeR2(),true);
assert.equal(followed.status,206);
assert.equal(followed.headers.get('content-range'),'bytes 0-1023/'+SIZE);
assert.equal(followed.headers.get('accept-ranges'),'bytes');
assert.equal(followed.headers.get('content-type'),'video/mp4');

const original=fakeR2({hasOld:true});
const stillAvailable=await call('/media/'+OLD,original,true);
assert.equal(stillAvailable.status,206,'alias is dormant while old bytes still exist');
assert(original.touched.get.includes(OLD));

for(const p of [
 {removed:true}, {hiddenOld:true}, {hiddenKeep:true},
 {keepEtag:'different-etag'}, {keepSize:12}, {lackMetadata:true}
]){
 const env=fakeR2(p);
 const result=await call('/media/'+OLD,env);
 assert.equal(result.status,404,'fail closed for '+JSON.stringify(p));
}
const damaged=fakeR2({metadataError:true});
assert.equal((await call('/media/'+OLD,damaged)).status,503);
assert.equal((await call('/media/OTHER_FILM.mp4',fakeR2())).status,404,
 'No generic alias; unrelated video must not become public');
assert.equal((await call('/cover/ARTVISION_PIRANESI_CINEMA_V6',fakeR2())).status,404,
 'No automatic cover-alias: cover is governed by its own source object');
console.log('PASS Piranesi aliases: old link unchanged, 307 to exact keeper, 206 Range, hidden/deleted fail-closed, no R2 mutation');
