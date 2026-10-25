/* Zero-AI boards: mobile UI regression in simulated browser. */
const {JSDOM,VirtualConsole}=require('/tmp/vls-editorial-ui/node_modules/jsdom');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('site/video-library-v2.html','utf8');
const key='TRA_LE_PAGINE_PRINCIPE_FELICE.mp4';
const catalog={admin:true,items:[{key,name:key,available:true,size:12700000,cover:'/cover/test',title:'Il principe felice',description:'Una fiaba di Oscar Wilde',category:'Libri raccontati',project:'Tra le Pagine',duration:185,version:'final'}]};
const record={key,schemaVersion:1,publicTitle:'Il principe felice',shortDescription:'La storia di una rondine e di una statua',project:'Tra le Pagine',category:'Libri raccontati',language:'it',hook:'Un principe che rinuncia a tutto',directorNotes:'Movimenti lenti e tagli narrativi',storyboard:'00:00 La statua sulla città\n00:15 La rondine si posa\n00:35 La sarta riceve il rubino',rightsStatus:'da_verificare',publicationStatus:'bozza',musicAttribution:'',imageSources:'',sources:'',voiceCredits:'Google Gacrux'};
let sent=0,drawn=[],downloads=[],errors=[];
const vconsole=new VirtualConsole();vconsole.on('jsdomError',e=>errors.push(e.message));
const dom=new JSDOM(html,{url:'https://video-library-studio.600led.workers.dev/',runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vconsole,beforeParse(w){
 w.localStorage.setItem('vlsAdmin','a'.repeat(64));
 w.IntersectionObserver=class{observe(){}disconnect(){}unobserve(){}};
 w.HTMLElement.prototype.scrollIntoView=()=>{};
 w.HTMLDialogElement.prototype.showModal=function(){this.open=true};
 w.HTMLDialogElement.prototype.close=function(){this.open=false};
 w.HTMLMediaElement.prototype.pause=()=>{};
 w.HTMLMediaElement.prototype.play=()=>Promise.resolve();
 w.URL.createObjectURL=()=> 'blob:board-v34';
 w.URL.revokeObjectURL=()=>{};
 w.HTMLAnchorElement.prototype.click=function(){if(this.download)downloads.push(this.download)};
 w.HTMLCanvasElement.prototype.getContext=function(){return {
  fillStyle:'',font:'',textBaseline:'',fillRect(){},beginPath(){},moveTo(){},lineTo(){},quadraticCurveTo(){},closePath(){},fill(){},
  drawImage(){},fillText(text){drawn.push(String(text))},measureText(text){return {width:String(text).length*12}}
 }};
 w.HTMLCanvasElement.prototype.toBlob=function(done,type){done(new w.Blob(['fake-png'],{type}))};
 w.fetch=async(url,options={})=>{
  const path=String(url);
  if(path.startsWith('/api/catalog'))return {ok:true,json:async()=>catalog};
  if(path.startsWith('/api/editorial?'))return {ok:true,json:async()=>({ok:true,record,metadata:catalog.items[0],assets:[{name:'SCENA_01.jpg',size:50000}],generated:true,missing:['licenze da verificare']})};
  sent++;throw Error('Unexpected request '+path);
 };
}});
const d=dom.window.document;
const pause=()=>new Promise(done=>setTimeout(done,400));
(async()=>{
 await pause();
 d.querySelector('#heroStudio').click();
 const dossier=d.querySelector('[data-act="dossier"]');
 assert(dossier,'No dossier button');
 dossier.click();await pause();
 d.querySelector('[data-ed-tab="boards"]').click();
 const canvas=d.querySelector('#edBoardCanvas');
 assert.equal(canvas.width,1200,'Canvas board width');
 assert(d.querySelector('#edBoardInfo').textContent.includes('Zero generazioni AI'),'Zero API notice missing');
 assert(drawn.some(x=>x.includes('Il principe felice')),'Existing title not shown');
 assert(drawn.some(x=>x.includes('Diritti da verificare')),'Unverified rights must not be approved');
 assert.equal(d.querySelector('#edBoardKind').value,'concept');
 d.querySelector('#edBoardKind').value='production';
 d.querySelector('#edBoardKind').dispatchEvent(new dom.window.Event('change'));
 assert(drawn.some(x=>x.includes('SCENA_01.jpg')),'Attachments absent');
 d.querySelector('#edBoardKind').value='scenes';
 d.querySelector('#edBoardKind').dispatchEvent(new dom.window.Event('change'));
 assert(canvas.height>=1100,'Contact sheet height invalid');
 assert(drawn.some(x=>x.includes('La rondine si posa')),'Storyboard not reflected');
 d.querySelector('#edBoardDownload').click();await pause();
 assert(downloads.length===1&&downloads[0].endsWith('_scenes_V34.png'),'PNG download not wired');
 assert.equal(sent,0,'Board must not make extra API calls');
 assert(!errors.length,'Browser error: '+errors.slice(0,2).join(', '));
 console.log('PASS Visual Boards V34: 3 layouts, source labels, responsive canvas PNG, no extra provider calls');
 dom.window.close();
})().catch(e=>{console.error(e);process.exit(1)});
