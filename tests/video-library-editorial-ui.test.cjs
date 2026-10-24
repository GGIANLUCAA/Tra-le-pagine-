const {JSDOM,VirtualConsole}=require('/tmp/vls-editorial-ui/node_modules/jsdom');
const assert=require('node:assert/strict'),fs=require('node:fs');
const html=fs.readFileSync('site/video-library-v2.html','utf8');
const key='ARTVISION_CARAVAGGIO_CINEMA_V6.mp4',fkey='gpt:Fur_Elise_Music_Motion.mp4';
const catalog={admin:true,items:[
 {key,name:key,size:25000000,uploaded:'2026-10-24T12:00:00.000Z',cover:'/cover/ARTVISION_CARAVAGGIO_CINEMA_V6',title:'Caravaggio — viaggio nelle opere',description:'Opera e dettagli.',category:'Artisti e pittura',version:'final',duration:120,width:1920,height:1080,available:true,favorite:false,hidden:false},
 {key:fkey,name:'Fur_Elise_Music_Motion.mp4',size:2200000,uploaded:null,cover:null,description:null,category:'Musica e visual',version:'draft',available:false,favorite:false,hidden:false}
]};
const record={schemaVersion:1,key,publicTitle:'Caravaggio — viaggio nelle opere',category:'Artisti e pittura',project:'ArtVision',language:'it',shortDescription:'Viaggio nelle opere',
 facebook:'POST FACEBOOK AUTENTICO DAL PROGETTO',instagram:'IG ORIGINAL',tiktok:'TIKTOK ORIGINAL',youtube:'YOUTUBE ORIGINAL',
 hook:'Un dettaglio da scoprire',hashtags:'#Caravaggio #Arte',
 storyboard:'00:00 ingresso, 00:10 dettaglio',directorNotes:'Camera dolly lento',script:'',productionPrompt:'Prompt storico',productionSteps:'Workflow originario',
 technicalNotes:'H264',socialInstructions:'Post del sabato',musicTitle:'',musicAuthor:'',musicLicense:'',musicLink:'',musicAttribution:'Musica documentata nello Studio',
 imageCredits:'',imageSources:'',voiceCredits:'',sources:'',tags:'arte',rightsStatus:'da_verificare',publicationStatus:'bozza',
 publicationNotes:'',edition:'Unico',reprints:'2 copie',masterRef:'master-1',legacyNotes:'Storyboard storico'
};
let captured=null,copied='';
const errs=[],virtualConsole=new VirtualConsole();virtualConsole.on('jsdomError',e=>errs.push(e.stack||e.message));
const dom=new JSDOM(html,{url:'https://video-library-studio.600led.workers.dev/',runScripts:'dangerously',pretendToBeVisual:true,virtualConsole,beforeParse(w){
 w.localStorage.setItem('vlsAdmin','a'.repeat(64));
 w.HTMLElement.prototype.scrollIntoView=()=>{};
 w.IntersectionObserver=class{observe(){}disconnect(){}unobserve(){}};
 w.HTMLDialogElement.prototype.showModal=function(){this.open=true};
 w.HTMLDialogElement.prototype.close=function(){this.open=false};
 w.HTMLMediaElement.prototype.play=()=>Promise.resolve();
 w.HTMLMediaElement.prototype.pause=()=>{};
 w.confirm=()=>true;
 Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async text=>{copied=text}}});
 w.fetch=async(url,options)=>{
  const path=String(url);
  if(path.startsWith('/api/catalog'))return {ok:true,json:async()=>catalog};
  if(path.startsWith('/api/editorial?'))return {ok:true,json:async()=>({ok:true,record,generated:true,metadata:catalog.items[0],assets:[{name:'POST_ORIGINALE.txt',size:810}],missing:['licenza musica']})};
  if(path==='/api/editorial'&&options.method==='POST'){
    captured=JSON.parse(options.body);
    Object.assign(record,captured.data);
    return {ok:true,json:async()=>({ok:true,record,missing:[]})};
  }
  if(path==='/api/social-package-link')return {ok:true,json:async()=>({ok:true,url:'https://example.invalid/test.zip'})};
  throw Error('Unexpected request '+path);
 };
}});
const d=dom.window.document;
async function pause(){await new Promise(resolve=>setTimeout(resolve,900))}
(async()=>{
 await pause();
 assert(d.querySelectorAll('.card').length===2,'Catalog cards missing');
 d.querySelector('#heroStudio').click();
 const dossier=d.querySelector('[data-act="dossier"]');assert(dossier,'Dossier button not present in Studio');
 dossier.click();await pause();
 assert(d.querySelector('#editorial').open,'Dossier dialog not opened');
 const form=d.querySelector('#editorialForm');
 assert.equal(form.elements.namedItem('facebook').value,'POST FACEBOOK AUTENTICO DAL PROGETTO');
 assert.equal(form.elements.namedItem('reprints').value,'2 copie');
 assert.equal(form.elements.namedItem('musicAttribution').value,'Musica documentata nello Studio');
 assert(d.querySelector('#edAssetList').textContent.includes('POST_ORIGINALE.txt'),'Historical attachment missing');
 assert(!d.querySelector('#edZipFull').disabled,'Complete ZIP should be enabled for playable MP4');
 console.log('PASS UI: private dossier opens, reuses prior notes and lists assets');
 d.querySelector('[data-ed-tab="production"]').click();
 assert(!d.querySelector('[data-ed-panel="production"]').hidden,'Regia tab did not open');
 assert.equal(form.elements.namedItem('storyboard').value,'00:00 ingresso, 00:10 dettaglio');
 d.querySelector('[data-ed-tab="social"]').click();
 form.elements.namedItem('facebook').value='TESTO FACEBOOK AGGIORNATO';
 form.elements.namedItem('facebook').dispatchEvent(new dom.window.Event('input',{bubbles:true}));
 form.dispatchEvent(new dom.window.Event('submit',{bubbles:true,cancelable:true}));
 await pause();
 assert.equal(captured.key,key,'Owner edits sent to wrong video');
 assert.equal(captured.data.facebook,'TESTO FACEBOOK AGGIORNATO');
 assert.equal(captured.data.reprints,'2 copie','Original edition info lost on edit');
 d.querySelector('[data-ed-copy="facebook"]').click();
 await pause();
 assert.equal(copied,'TESTO FACEBOOK AGGIORNATO','Copy-post action failed');
 assert(!errs.length,'Browser JavaScript errors '+errs.slice(0,2).join('; '));
 console.log('PASS UI: edit saved, original production metadata preserved, copy caption works');
 dom.window.close();
})().catch(e=>{console.error(e);process.exit(1)});
