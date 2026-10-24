/* Video Library Studio dossier mock tests: no production secrets or R2 writes. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {AsyncFunction}=Object.getPrototypeOf(async()=>{}).constructor;
globalThis.crypto=require('node:crypto').webcrypto;
const core=fs.readFileSync('site/video-library-editorial-core.js','utf8');
const writer=new AsyncFunction('req','env','u','readJSON','videoDetails','auth','json',core+"\nreturn new Response('Not found',{status:404});");
const base='https://video-library-studio.600led.workers.dev',video='ARTVISION_TEST_EDITORIAL.mp4';
const binary=new Uint8Array(2*1024*1024+19).fill(71);binary[0]=0;binary[1]=0;binary[2]=0;binary[3]=24;
const stored=new Map(),encoder=new TextEncoder();
const add=(k,v)=>stored.set(k,typeof v==='string'?encoder.encode(v):v);
add(video,binary);add('ARTVISION_TEST_EDITORIAL.jpg',new Uint8Array([255,216,255,217]));
add('production/notes.json',JSON.stringify({[video]:{
 socialFacebook:'TESTO FACEBOOK STORICO — recuperato dal vecchio Studio',
 socialInstagram:'INSTAGRAM STORICO',
 musicCredits:'Brano — Artista — Fonte storica',
 directions:'Zoom lento sul dettaglio storico',
 recipe:'Workflow originale collaudato',
 storyboard:'00:00 panoramica; 00:10 dettaglio',
 reprints:'3 copie',edition:'Versione unica originale',masterRef:'master_2026',
 socialTags:'#ProgettoTest',notes:'Non cambiare la voce',
 publicationInstructions:'Pubblicazione serale da verificare'
}}));
add('production/files/'+encodeURIComponent(video)+'/POST_STORICO.txt','Questa è la caption autentica.');
const mockObject=(key,bytes)=>{
 if(!bytes)return null;
 const stream=new Response(bytes);
 return {key,size:bytes.byteLength,body:stream.body,json:async()=>JSON.parse(new TextDecoder().decode(bytes))};
};
const env={ADMIN_KEY_SHA256:'a'.repeat(64),VIDEOS:{
 async get(k){return mockObject(k,stored.get(k))},
 async head(k){const v=stored.get(k);return v?{key:k,size:v.length}:null},
 async put(k,v){add(k,v instanceof Uint8Array?v:typeof v==='string'?v:new Uint8Array(await new Response(v).arrayBuffer()));return {key:k}},
 async list({prefix=''}){return {objects:[...stored].filter(([k])=>k.startsWith(prefix)).map(([key,v])=>({key,size:v.length})),truncated:false}}
}};
let authenticated=true;
const readJSON=async k=>{try{return JSON.parse(new TextDecoder().decode(stored.get(k)||new Uint8Array()))}catch{return {}}};
const videoDetails=async k=>({key:k,title:'Opera Test',genre:'Artisti e pittura',description:'Studio di un dipinto.',version:'final',duration:120,width:1920,height:1080,createdAt:'2026-10-24',filename:video,size:stored.get(k)?.byteLength||0});
const auth=async()=>authenticated;
const json=x=>new Response(JSON.stringify(x),{headers:{'content-type':'application/json'}});
const request=async(path,method='GET',data)=>{
 const opts={method,headers:{}};if(data!==undefined){opts.headers['content-type']='application/json';opts.body=JSON.stringify(data)}
 const req=new Request(base+path,opts);return writer(req,env,new URL(req.url),readJSON,videoDetails,auth,json);
};
(async()=>{
 authenticated=false;
 assert.equal((await request('/api/editorial?key='+encodeURIComponent(video))).status,401,'Dossier requires admin');
 assert.equal((await request('/api/social-package-link','POST',{key:video,mode:'light'})).status,401,'ZIP link requires admin');
 authenticated=true;
 const raw=await request('/api/editorial?key='+encodeURIComponent(video));
 assert.equal(raw.status,200);const dossier=await raw.json();
 assert(dossier.generated===true,'New dossier auto generated');
 assert(dossier.record.facebook.startsWith('TESTO FACEBOOK STORICO'),'Existing Facebook post must be reused');
 assert(dossier.record.storyboard.includes('panoramica'),'Existing storyboard must be reused');
 assert(dossier.record.productionSteps.includes('Workflow'),'Existing recipe must be reused');
 assert.equal(dossier.record.musicAttribution,'Brano — Artista — Fonte storica','Music credit reuse');
 assert.equal(dossier.record.reprints,'3 copie');
 assert.equal(dossier.assets.length,1);
 console.log('PASS: auto dossier reuses historical production notes and original attachment');
 const edit=await request('/api/editorial','POST',{key:video,data:{facebook:'Facebook definitivo con fonte verificata',musicTitle:'Titolo test',rightsStatus:'verificato',publicationStatus:'approvato'}});
 assert.equal(edit.status,200,'Editing failed '+await edit.text());
 const again=(await(await request('/api/editorial?key='+encodeURIComponent(video))).json()).record;
 assert.equal(again.facebook,'Facebook definitivo con fonte verificata');
 assert.equal(again.storyboard,'00:00 panoramica; 00:10 dettaglio');
 assert.equal(again.publicationStatus,'approvato');
 console.log('PASS: editing persists and preserves historical recipes');
 let denied=await request('/api/editorial','POST',{key:video,data:{unknown:'oops'}});
 assert.equal(denied.status,400);
 denied=await request('/api/social-package?key='+encodeURIComponent(video)+'&exp=9999999999&sig='+'a'.repeat(64)+'&mode=light');
 assert.equal(denied.status,403);
 console.log('PASS: unknown metadata fields and forged download links rejected');
 for(const mode of ['light','full']){
  const r=await request('/api/social-package-link','POST',{key:video,mode});
  assert.equal(r.status,200,'Cannot generate '+mode+' ZIP download link');
  const link=(await r.json()).url;
  const resp=await request(new URL(link).pathname+new URL(link).search);
  assert.equal(resp.status,200,'ZIP stream '+mode+' failed');
  const bytes=Buffer.from(await resp.arrayBuffer());
  assert.equal(bytes.subarray(0,4).toString('hex'),'504b0304');
  fs.writeFileSync('/tmp/vls-editorial-'+mode+'.zip',bytes);
  console.log('PASS: streaming ZIP '+mode+' bytes='+bytes.length);
 }
 const bad=await request('/api/social-package?key='+encodeURIComponent(video)+'&mode=full&exp='+Math.floor(Date.now()/1000)+'&sig='+'b'.repeat(64));
 assert.equal(bad.status,403);
})();
