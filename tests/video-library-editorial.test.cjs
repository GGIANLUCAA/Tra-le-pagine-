/* Video Library Studio dossier mock tests: no production secrets or R2 writes. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const AsyncFunction=Object.getPrototypeOf(async()=>{}).constructor;
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
 const attachmentVideo='HOKUSAI_ATTACHMENT_TEST.mp4';add(attachmentVideo,binary);
 const ap='production/files/'+encodeURIComponent(attachmentVideo)+'/';
 add(ap+'POST_FACEBOOK.txt','Un post originale dedicato a questo filmato e alle sue opere.');
 add(ap+'POST_FACEBOOK_COPY.txt','Un post originale dedicato a questo filmato e alle sue opere.');
 add(ap+'POST_INSTAGRAM_V1.txt','Primo testo Instagram.');add(ap+'POST_INSTAGRAM_V2.txt','Secondo testo Instagram.');
 const attached=await (await request('/api/editorial?key='+encodeURIComponent(attachmentVideo))).json();
 assert.equal(attached.record.facebook,'Un post originale dedicato a questo filmato e alle sue opere.');
 assert.equal(attached.socialSources.facebook.kind,'attachment');
 assert.equal(attached.record.instagram,'');assert.equal(attached.socialSources.instagram.kind,'conflict');
 const saveFields=await request('/api/editorial','POST',{key:attachmentVideo,data:{bookAuthor:'Autore verificato',sourceEvidence:'Fonte originale',facebook:'Post curato dall’utente',category:'Artisti e pittura'}});
 assert.equal(saveFields.status,200);
 const reloaded=await (await request('/api/editorial?key='+encodeURIComponent(attachmentVideo))).json();
 assert.equal(reloaded.record.bookAuthor,'Autore verificato');assert.equal(reloaded.record.facebook,'Post curato dall’utente');
 assert.equal(reloaded.socialSources.facebook.kind,'saved');
 assert.equal((await request('/api/editorial','POST',{key:attachmentVideo,data:{category:'Categoria diversa'}})).status,409);
 console.log('PASS: exact-video posts recovered, conflicts exposed, curated copy and new fields persist');

 const projectV13={schema:'video-project-v13',bibliography:{author:'Lewis Carroll',publication_year:'1865'},
  editorial_metadata:{series:'Classici che parlano ancora',themes:'Fantasia e logica'},business:{audience:'Adulti e ragazzi'},
  editorial_plan:{subject_insight:'Un classico di grande ricchezza visiva',mix_reason:'Illustrazioni narrative e movimenti delicati',
  opening_promise:'Una domanda che cambia il mondo',sources:[
   {reference:'https://www.themorgan.org/printed-books/246978',finding:'Prima edizione 1865',verification:'controlled_by_operator'}],
  media_sourcing:{decisions:[{asset_id:'A1',source_reference:'https://example.org/fonte',
     rights_review:'pending',visual_review:'pending'}]}},
  assets:[{id:'A1',file:'alice-scene.jpg',source:'Archivio pubblico',rights:'Da verificare'}],
  scenes:[{asset_id:'A1',description:'Alice guarda la tana',reason:'Introduzione'}]};
 add('production/files/'+encodeURIComponent(video)+'/PROJECT_V13.json',JSON.stringify(projectV13));
 const enriched=(await(await request('/api/editorial?key='+encodeURIComponent(video))).json());
 assert.equal(enriched.projectV13Attached,true,'V13 attachment must be recognized');
 assert.equal(enriched.record.bookAuthor,'Lewis Carroll');
 assert.equal(enriched.record.publicationYear,'1865');
 assert(enriched.record.sourceEvidence.includes('themorgan.org'),'A real recorded source must be imported');
 assert(enriched.record.assetLedger.includes('pending'),'Rights must remain pending');
 assert(enriched.record.storyboard.includes('panoramica'),'Historic owner storyboard must not be overwritten');
 console.log('PASS V35: attached V13 enriches dossier, traces source and keeps unverified rights');
 // V37: an automatic new dossier must not contain generic platform boilerplate.
 assert.equal(dossier.record.instagram,'INSTAGRAM STORICO','Historical Instagram must survive');
 assert.equal(dossier.record.youtube,'','New generic YouTube must be blank, not publication-ready');
 const blocked=await request('/api/editorial','POST',{key:video,data:{
  facebook:'Facebook definitivo con fonte verificata',musicTitle:'Titolo test',rightsStatus:'verificato',publicationStatus:'approvato'}});
 assert.equal(blocked.status,422,'Short or generic captions must not be approved');
 const failure=await blocked.json();
 assert.equal(failure.code,'SOCIAL_REVIEW_REQUIRED');
 assert(failure.issues.some(x=>x.includes('facebook')));
 console.log('PASS V37: placeholders and missing captions block approval');
 const edit=await request('/api/editorial','POST',{key:video,data:{facebook:'Facebook definitivo con fonte verificata',musicTitle:'Titolo test',rightsStatus:'verificato',publicationStatus:'da_revisionare'}});
 assert.equal(edit.status,200,'Editing a draft must remain possible '+await edit.text());
 const again=(await(await request('/api/editorial?key='+encodeURIComponent(video))).json()).record;
 assert.equal(again.facebook,'Facebook definitivo con fonte verificata');
 assert.equal(again.storyboard,'00:00 panoramica; 00:10 dettaglio');
 assert.equal(again.publicationStatus,'da_revisionare');
 const forbidden=await request('/api/editorial','POST',{key:video,data:{
  facebook:'Qui spieghiamo tutte le scelte della regia e del montaggio con un testo decisamente lungo e pieno di parole per superare qualsiasi controllo quantitativo senza parlare di un soggetto reale e senza raccontare una storia autentica che interessi il nostro pubblico e i visitatori del sito oltre al lavoro per prepararlo e presentarlo.',
  publicationStatus:'approvato'}});
 assert.equal(forbidden.status,422,'Public process notes must be blocked');
 const fb='Facebook definitivo — Il dipinto si trova in una collezione storica. Questo racconto si concentra sulle domande che un visitatore può porsi davanti alle figure e sui modi in cui la pittura cambia il nostro sguardo. La storia dell opera viene collocata nel suo tempo, distinguendo fatti e interpretazioni senza inventare dettagli.';
 const ig='Davanti a quest opera si possono osservare almeno due storie: quella che l artista voleva mostrare e quella che il pubblico continua a leggere. Il contesto ci aiuta a guardarla con maggiore attenzione, senza imporre una risposta unica.';
 const tt='Una figura e una scelta raccontano il cuore di questa storia. Una lettura breve, chiara, basata sul contesto e sul soggetto.';
 const yt='Questo episodio prende avvio da un opera conservata in una collezione storica. Attraverso la sua vicenda, le figure e il contesto in cui nacque, esploriamo alcune domande che ancora interessano chi osserva la pittura. Il racconto distingue ciò che conosciamo da ciò che rimane un interpretazione, con un approccio accessibile a tutti.';
 const qaBlocked=await request('/api/editorial','POST',{key:video,data:{facebook:fb,instagram:ig,tiktok:tt,youtube:yt,publicationStatus:'approvato'}});
 assert.equal(qaBlocked.status,422,'Good captions alone must not certify the video');
 assert((await qaBlocked.json()).issues.some(s=>s.includes('Ascolto integrale')));
 const accepted=await request('/api/editorial','POST',{key:video,data:{
  facebook:fb,instagram:ig,tiktok:tt,youtube:yt,publicationStatus:'approvato',rightsStatus:'verificato',reviewImages:'verificato',reviewAudio:'verificato',reviewCover:'verificato',reviewFacts:'verificato'}});
 assert.equal(accepted.status,200,'Four distinct researched captions should be structurally acceptable '+await accepted.text());
 const curated=(await(await request('/api/editorial?key='+encodeURIComponent(video))).json());
 assert.equal(curated.record.publicationStatus,'approvato');
 assert.deepEqual(curated.socialIssues,[]);
 console.log('PASS V37: four distinctive platform texts stored and retrieved with master dossier');
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

 const workflow={collections:['Da migliorare'],videos:{[video]:{title:'Opera',collections:['Da migliorare'],rating:'Da correggere',issue:'Musica',notes:'Abbassare la musica',updatedAt:'2026-10-27T12:00:00Z'}}};
 authenticated=false;assert.equal((await request('/api/workflow')).status,401);authenticated=true;
 assert.equal((await request('/api/workflow')).status,200);
 let cloud=await request('/api/workflow','POST',{data:workflow,revision:0});assert.equal(cloud.status,200);
 const restored=await (await request('/api/workflow')).json();assert.equal(restored.videos[video].notes,'Abbassare la musica');assert.equal(restored.revision,1);
 assert.equal((await request('/api/workflow','POST',{data:workflow,revision:0})).status,409);
 assert.equal((await request('/api/workflow','POST',{data:{collections:[],videos:{bad:{}}},revision:1})).status,400);
 const originalPut=env.VIDEOS.put;env.VIDEOS.put=async()=>null;
 assert.equal((await request('/api/workflow','POST',{data:workflow,revision:1})).status,409);env.VIDEOS.put=originalPut;
 console.log('PASS: private collections persist; stale writes, invalid data and concurrent writes rejected');
 const bad=await request('/api/social-package?key='+encodeURIComponent(video)+'&mode=full&exp='+Math.floor(Date.now()/1000)+'&sig='+'b'.repeat(64));
 assert.equal(bad.status,403);
})();

