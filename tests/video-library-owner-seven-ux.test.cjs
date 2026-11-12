/* Run with jsdom installed in /tmp/museum-v4 (existing site preview CI). */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM,VirtualConsole}=require('/tmp/museum-v4/node_modules/jsdom');
const html=fs.readFileSync('site/video-library-v2.html','utf8');
const name=(slot,v)=>'BRUEGEL_THE_FALL_OF_THE_REBEL_ANGELS_'+slot+'_V'+v+'_REVIEW.mp4';
const items=[
  ['CRITICO_STANDARD',144],['CRITICO_MUSEUM',197],['CINEMA_STANDARD',153],['CINEMA_MUSEUM',196]
].map(([slot,v],i)=>({key:name(slot,v),name:name(slot,v),available:true,size:1000000+i*100,
  cover:'/cover/'+slot+'.jpg',category:'Artisti e pittura',uploaded:'2026-11-08T09:00:00Z',version:'draft',duration:60}));
items.push({key:'STORIA_CARMENCITA_1894.mp4',name:'STORIA_CARMENCITA_1894.mp4',
 available:true,size:800000,cover:'/cover/carmencita.jpg',uploaded:'2026-11-08T09:00:00Z'});
items.push({key:'ARTVISION_GPT_MISSING.mp4',name:'ARTVISION_GPT_MISSING.mp4',
 available:false,size:300000,uploaded:'2026-11-08T09:00:00Z'});
const calls=[],errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
let copied='';
const dom=new JSDOM(html,{url:'https://video-library-studio.600led.workers.dev/',
  runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){
   w.fetch=async(url,options={})=>{
    calls.push({url:String(url),method:options.method||'GET',range:options.headers?.Range});
    if(new URL(String(url),w.location.origin).pathname.startsWith('/download/'))return {
      status:206,headers:new Map([['content-range','bytes 0-0/1000000'],['content-type','video/mp4']]),
      body:{cancel:async()=>{}}
    };
    if(String(url).startsWith('/api/catalog'))return {ok:true,json:async()=>({admin:true,items})};
    return {ok:false,status:404,json:async()=>({})};
   };
   w.HTMLElement.prototype.scrollIntoView=()=>{};
   w.HTMLDialogElement.prototype.showModal=function(){this.open=true};
   w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'))};
   w.HTMLMediaElement.prototype.play=()=>Promise.resolve();
   w.HTMLMediaElement.prototype.pause=()=>{};
   w.HTMLMediaElement.prototype.load=()=>{};
   w.HTMLMediaElement.prototype.requestFullscreen=function(){this.dataset.fullscreenRequested='yes';return Promise.resolve()};
   w.matchMedia=()=>({matches:false,addListener(){},removeListener(){}});
   Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async t=>{copied=t}}});
  }});
const d=dom.window.document;
const tick=async()=>new Promise(resolve=>setTimeout(resolve,35));
(async()=>{
 await tick();
 const mainSections=[...d.querySelectorAll('main > section')].map(section=>section.id);
 assert.deepEqual(mainSections.slice(0,3),['recent','collections','museum'],'Video-first: latest available films precede categories and museum');
 assert.match(d.querySelector('#recent .section-eyebrow').textContent,/ULTIMI IN ARCHIVIO/,'Latest rail must not imply newly produced or artistically approved videos');
 assert(d.querySelector('#latestRail'),'Latest film rail remains available');
 const root=d.querySelector('#vlsWorks');
 assert(root&&!root.hidden,'Group section must be displayed');
 const group=[...root.querySelectorAll('.vls-work')].find(w=>/Fall of the Rebel Angels/.test(w.textContent));
 assert(group,'Bruegel work grouped from catalog');
 assert.equal(group.querySelectorAll('.vls-slot').length,4);
 assert.equal(group.querySelectorAll('.vls-slot:disabled').length,0);
 const cover=d.querySelector('.card[data-video-key="'+items[0].key+'"] .poster');
 assert(cover,'Playable card must exist');
 cover.click();assert(d.querySelector('#player').open,'Cover tap opens existing player');
 d.querySelector('#vlsFullscreen').click();await tick();
 assert.equal(d.querySelector('#video').dataset.fullscreenRequested,'yes');
 d.querySelector('#vlsRepairFromPlayer').click();
 assert(d.querySelector('#vlsRepair').open,'Admin only GPT handoff');
 d.querySelector('#vlsIssueNote').value='La camera taglia la figura.';
 d.querySelector('#vlsCopyGPT').click();await tick();
 assert.match(copied,/La camera taglia la figura/);
 assert.match(copied,/github.com\/GGIANLUCAA\/Tra-le-pagine-/);
 assert(!copied.includes('Bearer '),'No admin token can be leaked');
 d.querySelector('#vlsRepair').close();
 d.querySelector('#playerDownload').click();await tick();
 assert(d.querySelector('#vlsDownload').open);
 assert.match(d.querySelector('#vlsDownloadStatus').textContent,/Accesso parziale OK/);
 assert.equal(d.querySelector('#vlsDownloadZIP').hidden,false);
 assert(calls.some(c=>new URL(String(c.url),dom.window.location.origin).pathname.startsWith('/download/')&&c.range==='bytes=0-0'),'Range preflight is required');
 d.querySelector('#vlsDownload').close();d.querySelector('#player').close();
 group.querySelector('.vls-work-actions button').click();
 assert(d.querySelector('#vlsCompare').open,'A/B dialog opens');
 assert.equal(d.querySelectorAll('#vlsSelectA option').length,4);
 assert(d.querySelector('#vlsVideoA').src.includes('BRUEGEL_'));
 assert(d.querySelector('#vlsVideoB').muted,'Avoid two simultaneous audio tracks');
 d.querySelector('#vlsCompare').close();
 const tab=name=>d.querySelector('.bottom-nav [data-section="'+name+'"]');
 assert.equal(tab('home').getAttribute('aria-current'),'location','Home must be current initially');
 assert.equal(d.querySelectorAll('.bottom-nav [aria-current="location"]').length,1);
 tab('library').click();
 assert.equal(tab('library').getAttribute('aria-current'),'location','Video tab must become current');
 assert.equal(tab('home').hasAttribute('aria-current'),false,'Previous tab state must be cleared');
 d.querySelector('#heroStudio').click();await tick();
 assert.equal(tab('studio').getAttribute('aria-current'),'location','Studio must remain highlighted after navigating to private ready section');
 assert(tab('studio').classList.contains('active'));
 assert.equal(d.querySelectorAll('.bottom-nav [aria-current="location"]').length,1,'Only one active tab is announced');
 assert.match(html,/\.bottom-nav button\{min-width:45px;flex:1 1 0;padding:0 2px;font-size:11px/,'Android labels should remain readable');
 assert.equal(d.querySelector('#vlsStudioQuick').hidden,false,'Private quick studio opens');
 assert(d.querySelector('#vlsStudioQuick').textContent.includes('Centro di controllo'));
 assert.equal(errors.length,0,errors.join('\n'));
 console.log('PASS: grouped 4x1, poster tap, fullscreen, A/B, GPT handoff, byte-range check, private Studio');
 dom.window.close();
})().catch(e=>{console.error(e);dom.window.close();process.exit(1)});
