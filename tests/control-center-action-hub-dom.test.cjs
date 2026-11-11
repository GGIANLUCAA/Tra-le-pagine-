'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM,VirtualConsole}=require('/tmp/control-v10/node_modules/jsdom');
const html=fs.readFileSync('site/control-center-preview.html','utf8');
const work={id:'simberg_garden_1896',title:'The Garden of Death',artist:'Hugo Simberg',
 delivered:2,variants:[
  {id:'critico_standard',label:'Critico',recorded:true,preview_ready:true,site_catalog:true,site_available:true,
   filename:'SIMBERG_CRITICO.mp4',media_url:'https://video-library-studio.600led.workers.dev/media/SIMBERG_CRITICO.mp4',qa:{gold_approved:false}},
  {id:'critico_museum',label:'Critico Museum',recorded:true,preview_ready:false,site_catalog:false,site_available:null,
   filename:'SIMBERG_CRITICO_MUSEUM.mp4',qa:{gold_approved:false}},
  {id:'cinema_standard',label:'Cinema',recorded:false,preview_ready:false,site_catalog:false,site_available:null,
   filename:null,qa:{gold_approved:false}},
  {id:'cinema_museum',label:'Cinema Museum',recorded:false,preview_ready:false,site_catalog:false,site_available:null,
   filename:null,qa:{gold_approved:false}}
 ]};
const data={asof:'2026-11-10T18:00:00Z',sources:{github:{ok:true},queue:{ok:true},catalog:{ok:true}},
 runs:[{id:880,name:'ArtVision 4×1 · Produzione',project:'artvision',head_branch:'main',
  status:'in_progress',conclusion:null,event:'workflow_dispatch',workflow_id:70,
  run_started_at:'2026-11-10T18:00:00Z',updated_at:'2026-11-10T18:05:00Z',
  html_url:'https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/880'}],works:[work],health:[
  {id:'artvision',state:'unobserved',observed_count:0,active_count:0,issues:0},
  {id:'storia',state:'observed_success',observed_count:1,active_count:0,issues:0},
  {id:'wow',state:'unknown',observed_count:0,active_count:0,issues:0}
 ],attention:[],review:{count:1,detail:'Da revisionare'},diary:[],media:[{key:'STORIA_CARMENCITA_1894.mp4',title:'Carmencita 1894',available:true}],catalog_count:1};
const errors=[],calls=[],vc=new VirtualConsole();
vc.on('jsdomError',e=>errors.push(String(e.stack||e.message)));
let copied='';
const dom=new JSDOM(html,{url:'https://artvision-control-preview.600led.workers.dev/',
 runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){
  w.fetch=async(url,init={})=>{
   calls.push({url:String(url),method:init.method||'GET'});
   if(String(url).startsWith('/api/progress?run=880'))
      return {ok:true,json:async()=>({schema:'studio-github-progress-v12',ok:true,run_id:880,
      telemetry_version:'v13',step_fraction_percent:50,step_count:4,steps_completed:2,
      match_status:'exact_queue_run_id',
      linked_video:{work_id:'simberg_garden_1896',work_title:'The Garden of Death',artist:'Hugo Simberg',
      slot_id:'critico_standard',slot_label:'Critico',filename:'SIMBERG_CRITICO.mp4',preview_ready:true,
      gold_approved:false},
      phase:'Render reale',current_phase_group:'Elaborazione video',
      current_phase_elapsed_seconds:380,elapsed_seconds:940,
      latest_observation_at:new Date().toISOString(),last_step_at:new Date(Date.now()-2*60000).toISOString(),
      timeline:[{name:'Preparazione materiale',status:'completed_success',conclusion:'success',
        completed_at:'2026-11-10T18:04:30Z'}],
      eta:{available:false,reason:'Storico insufficiente',sample_count:2},
      percent_is_video_completion:false,mp4_complete_verified:false,video_progress_known:false})};
   if(String(url).startsWith('/api/status'))return {ok:true,json:async()=>data};
   return {ok:false,status:404,json:async()=>({ok:false})};
  };
  w.scrollTo=()=>{};
  w.HTMLElement.prototype.scrollIntoView=()=>{};
  w.HTMLDialogElement.prototype.showModal=function(){this.open=true};
  w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'))};
  w.HTMLMediaElement.prototype.play=()=>Promise.resolve();
  w.HTMLMediaElement.prototype.pause=()=>{};
  w.HTMLMediaElement.prototype.load=()=>{};
  Object.defineProperty(w.navigator,'clipboard',{configurable:true,value:{writeText:async t=>{copied=t}}});
 }});
const d=dom.window.document;
const tick=()=>new Promise(r=>setTimeout(r,50));
(async()=>{
 await tick();
 // V14: first useful card is progress; no large hero/stat/category wall before it.
 const content=d.querySelector('#content');
 assert(content.querySelector('.simpleWelcome'),'Compact V14 introduction visible');
 assert(content.querySelector('.productionPanel'),'Workflow progress is on Home');
 assert(content.querySelector('.simpleWelcome').compareDocumentPosition(content.querySelector('.productionPanel')) &
   dom.window.Node.DOCUMENT_POSITION_FOLLOWING,'Progress follows compact heading');
 assert(content.querySelector('.productionPanel').compareDocumentPosition(content.querySelector('.simpleAttention')) &
   dom.window.Node.DOCUMENT_POSITION_FOLLOWING,'Progress comes before diagnostics');
 assert.equal(content.querySelector('.simpleMore').open,false,'Advanced details collapsed by default');
 const extraHome=d.querySelector('[data-ui-section="home-more"]');
 extraHome.open=true;
 d.querySelector('#refresh').click();await tick();
 assert.equal(d.querySelector('[data-ui-section="home-more"]').open,true,
   'Opening advanced information persists when new live status arrives');
 assert.equal(d.querySelectorAll('.bottom [data-page]').length,4,'Four clear mobile navigation choices');
 assert.match(html,/\.hero,\.stats\{display:none\}/,'Old large hero and KPI wall are hidden');
 const bar=d.querySelector('.productionTrack[role="progressbar"]');
 assert(bar,'Home must show a real GitHub steps bar');
 assert.equal(bar.getAttribute('aria-valuenow'),'50');
 assert.match(d.querySelector('.productionRun').textContent,/non del video/i);
 assert.match(d.querySelector('.productionRun').textContent,/Storico insufficiente/);
 assert.match(d.querySelector('.productionRun').textContent,/Render reale/);
 assert.match(d.querySelector('.productionRun').textContent,/Elaborazione video/);
 assert.match(d.querySelector('.productionVideoLink')?.textContent||d.querySelector('.progressVideoLink').textContent,
   /The Garden of Death/);
 assert(d.querySelector('.progressVideoLink a').href.endsWith('/media/SIMBERG_CRITICO.mp4'));
 assert.match(d.querySelector('.progressVideoLink').textContent,/nessuna approvazione artistica/i);
 assert.match(d.querySelector('.productionRun').textContent,/FINE STIMATA DEL WORKFLOW/);
 assert(d.querySelector('.progressExtra'),'Recent phase timeline is expandable');
 d.querySelector('.progressExtra').open=true;
 assert.match(d.querySelector('.progressExtra').textContent,/Preparazione materiale/);
 d.querySelector('.bottom [data-page="issues"]').click();
 await tick();
 assert(d.querySelector('.actionTop'),'Immediate action panel exists');
 assert(d.querySelector('details.simpleMore'),'Long repair options are collapsed but not removed');
 assert.equal(d.querySelector('details.simpleMore').open,false);
 assert.equal(d.querySelectorAll('details.simpleMore').length>=3,true);
 assert.equal(d.querySelectorAll('[data-action-project]').length,3);
 assert.match(d.querySelector('#content').textContent,/The Garden of Death/);
 const row=d.querySelector('[data-action-work="simberg_garden_1896"][data-action-slot="cinema_standard"]');
 assert(row,'Missing single video has button');
 assert.equal(row.dataset.actionMode,'complete');
 row.click();await tick();
 assert(d.querySelector('#repairDialog').open,'Guided repair dialog opens');
 assert.equal(d.querySelector('#repairChatScope').value,'slot','Per-video link is first choice');
 assert.match(d.querySelector('#repairNextStep').textContent,/completa questa sola variante/i);
 assert.match(d.querySelector('#repairPrompt').value,/cinema_standard/);
 assert.match(d.querySelector('#repairPrompt').value,/non identificato/i);
 d.querySelector('#repairAdvancedChat').open=true;
 const chat='https://chatgpt.com/c/12345678-abcd-1234-abcd-123456789abc';
 d.querySelector('#repairChatInput').value=chat;
 d.querySelector('#saveRepairChat').click();await tick();
 assert.equal(d.querySelector('#repairCopyOpen').href,chat,'The correct video chat is selected');
 assert(d.querySelector('#repairAdvancedChat').open,'Chat settings stay visible after save');
 const note=d.querySelector('#repairOwnerNote');
 note.value='Voglio completare senza creare duplicati';
 note.dispatchEvent(new dom.window.Event('input',{bubbles:true}));
 assert.match(d.querySelector('#repairPrompt').value,/Voglio completare senza creare duplicati/);
 assert.equal(d.querySelector('#qualityJournal').hidden,false,'Feedback diary available for this slot');
 d.querySelector('#qualityCategory').value='direction';
 d.querySelector('#qualitySuggestFuture').checked=true;
 d.querySelector('#qualitySaveFeedback').click();await tick();
 const saved=JSON.parse(dom.window.localStorage.getItem('artvision.controlCenter.videoCorrections.v1')||'[]');
 assert.equal(saved.length,1,'One note persisted to this Android browser');
 assert.equal(saved[0].slot_id,'cinema_standard');
 assert.equal(saved[0].status,'reported','Unverified note cannot be treated as a fix');
 assert.equal(saved[0].owner_requested_generalization,true);
 assert.match(d.querySelector('#repairPrompt').value,/feedback_/);
 assert.match(d.querySelector('#repairPrompt').value,/VERIFICARE SE GIA REGISTRATE NEL REPOSITORY/i);
 assert.match(d.querySelector('#qualityJournalRows').textContent,/Voglio completare senza creare duplicati/);

 const action=d.querySelector('#repairCopyOpen');
 action.addEventListener('click',ev=>ev.preventDefault(),true); // Prevent jsdom navigation; allow original copy handler.
 action.click();await tick();
 assert.match(copied,/Voglio completare senza creare duplicati/);
 assert.equal(calls.every(x=>x.method==='GET'),true,'No production dispatch or mutation');
 d.querySelector('#closeRepairDialog').click();
 d.querySelector('[data-action-unblock]').click();await tick();
 assert(d.querySelector('#repairDialog').open,'Batch unblock opens the same guided GPT dialog');
 const proposed=d.querySelector('#repairPrompt').value;
 assert.match(proposed,/SBLOCCA CIO CHE E POSSIBILE/);
 assert.match(proposed,/critico_museum/);
 assert.match(proposed,/cinema_museum/);
 assert.match(proposed,/Recupera prima video esistenti/);
 assert.doesNotMatch(proposed,/nuovo render avviato con successo/i);
 d.querySelector('#closeRepairDialog').click();
 const recent=d.querySelector('[data-action-video="STORIA_CARMENCITA_1894.mp4"]');
 assert(recent,'Storia catalogue MP4 has its own improvement shortcut');
 recent.click();await tick();
 assert(d.querySelector('#repairDialog').open);
 assert.match(d.querySelector('#repairPrompt').value,/STORIA_CARMENCITA_1894.mp4/);
 assert.equal(d.querySelector('#repairChatScope').value,'work');
 d.querySelector('#repairOwnerNote').value='Ridurre stacchi fra le fotografie storiche.';
 d.querySelector('#qualitySaveFeedback').click();await tick();
 const records=JSON.parse(dom.window.localStorage.getItem('artvision.controlCenter.videoCorrections.v1'));
 assert.equal(records.length,2,'Storia video note stored independently from ArtVision');
 assert.equal(records[1].slot_id,null);
 assert.equal(records[1].filename,'STORIA_CARMENCITA_1894.mp4');
 assert.equal(records[1].project,'storia');
 d.querySelector('#closeRepairDialog').click();
 d.querySelector('[data-action-project="artvision"]').click();await tick();
 assert.match(d.querySelector('#repairPrompt').value,/nuova produzione REALE/i);
 assert.match(d.querySelector('#repairNextStep').textContent,/produzione reale/i);
 assert.equal(errors.length,0,errors.join('\n'));
 console.log('PASS V11 DOM: ArtVision/Storia notes saved separately, correct GPT handoff, recovery candidates, no writes');
 dom.window.close();
})().catch(e=>{console.error(e);dom.window.close();process.exit(1)});
