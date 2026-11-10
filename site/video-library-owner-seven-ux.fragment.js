/* Owner-selected Video Library UX: 5/6/12/13/15/16/18. Inline fragment inside existing IIFE.
   Catalog-derived data are NOT verified artistic approvals; never modify originals. */
const vlsSevenWorks=[
 ['rebel','The Fall of the Rebel Angels',['fall_of_the_rebel_angels','fall_rebel_angels','rebel_angels']],
 ['garden','The Garden of Death',['garden_of_death','simberg_garden']],
 ['babel','The Tower of Babel',['tower_of_babel','bruegel_babel']],
 ['shalott','The Lady of Shalott',['lady_of_shalott','lady_shalott']],
 ['triumph','The Triumph of Death',['triumph_of_death','bruegel_triumph']],
 ['circle','The Magic Circle',['magic_circle','waterhouse_circle']],
 ['flea','The Ghost of a Flea',['ghost_of_a_flea','ghost_of_flea','blake_flea']],
 ['watch','The Night Watch',['night_watch','nightwatch']],
 ['sardanapalus','The Death of Sardanapalus',['death_of_sardanapalus','sardanapalus']]
];
const vlsSevenSlots=[['critico_standard','Critico'],['critico_museum','Critico Museum'],['cinema_standard','Cinema'],['cinema_museum','Cinema Museum']];
const vlsNorm=s=>norm(String(s||'')).replace(/[^a-z0-9]+/g,'_');
function vlsWorkFor(x){
 const key=vlsNorm(x.key||x.name);
 if(!/(artvision|critico|cinema|museum|rebel_angels|night_watch)/.test(key))return null;
 return vlsSevenWorks.find(w=>w[2].some(alias=>key.includes(alias)))||null;
}
function vlsSlotFor(x){
 const key=vlsNorm(x.key||x.name);
 if(key.includes('critico'))return key.includes('museum')?'critico_museum':'critico_standard';
 if(key.includes('cinema'))return key.includes('museum')?'cinema_museum':'cinema_standard';
 return null;
}
function vlsGroups(){
 const map=new Map();
 for(const x of g.items){
  if(x.hidden)continue;
  const work=vlsWorkFor(x),slot=vlsSlotFor(x);if(!work||!slot)continue;
  if(!map.has(work[0]))map.set(work[0],{work,slots:new Map(),all:[]});
  const row=map.get(work[0]);row.all.push(x);
  if(!row.slots.has(slot))row.slots.set(slot,[]);
  row.slots.get(slot).push(x);
 }
 for(const row of map.values())for(const files of row.slots.values())
  files.sort((a,b)=>(Date.parse(b.uploaded||b.gptCreatedAt)||0)-(Date.parse(a.uploaded||a.gptCreatedAt)||0));
 return [...map.values()].sort((a,b)=>vlsSevenWorks.indexOf(a.work)-vlsSevenWorks.indexOf(b.work));
}
function vlsEl(tag,cls,label){
 const e=document.createElement(tag);if(cls)e.className=cls;if(label!==undefined)e.textContent=label;return e;
}
function vlsRenderWorks(){
 const root=$('#vlsWorks'),groups=vlsGroups();root.hidden=!groups.length;
 if(!groups.length){root.replaceChildren();return}
 root.replaceChildren(vlsEl('h3','','Opere e quattro versioni'),vlsEl('p','','Versioni riconosciute dai nomi nel catalogo, senza attestare approvazione artistica. I video non presenti qui possono esistere fuori dal sito.'));
 const list=vlsEl('div','vls-works-list');
 for(const group of groups){
  const box=vlsEl('details','vls-work'),head=vlsEl('summary');
  head.append(vlsEl('span','',group.work[1]),vlsEl('small','',group.slots.size+' tipologie su 4'));box.append(head);
  const grid=vlsEl('div','vls-slot-grid');
  for(const [slot,label] of vlsSevenSlots){
   const files=group.slots.get(slot)||[],x=files.find(y=>y.available!==false)||files[0];
   const btn=vlsEl('button','vls-slot',label);btn.type='button';btn.disabled=!x;
   btn.append(vlsEl('small','',x?(x.available===false?'Solo ChatGPT':files.length+' file / revisioni'):'Non trovato sul sito'));
   if(x)btn.onclick=()=>x.available===false?details(x):play(x);
   grid.append(btn);
  }
  box.append(grid);
  const actions=vlsEl('div','vls-work-actions'),compare=vlsEl('button','','↔ Confronta versioni');compare.type='button';
  compare.disabled=group.all.filter(x=>x.available!==false).length<2;
  compare.onclick=()=>vlsCompareOpen(group);actions.append(compare);box.append(actions);list.append(box);
 }
 root.append(list);
}
const vlsCompareState={group:null};
function vlsCompareLoad(key){
 const sel=$('#vlsSelect'+key),video=$('#vlsVideo'+key);
 const x=vlsCompareState.group?.all.find(v=>v.key===sel.value&&v.available!==false);
 video.pause();video.removeAttribute('src');video.removeAttribute('poster');
 if(x){video.src=mediaURL(x);if(x.cover)video.poster=x.cover}video.load();
}
function vlsComparePane(key){
 for(const which of ['A','B']){
  $('#vlsPane'+which).classList.toggle('active',which===key);
  $('#vlsSwitch'+which).className=which===key?'btn primary':'ghost';
  if(which!==key&&window.matchMedia('(max-width:700px)').matches)$('#vlsVideo'+which).pause();
 }
}
function vlsCompareOpen(group){
 const videos=group.all.filter(x=>x.available!==false);if(videos.length<2)return;
 vlsCompareState.group=group;$('#vlsCompareTitle').textContent='Confronta · '+group.work[1];
 for(const key of ['A','B']){
  const select=$('#vlsSelect'+key);select.replaceChildren();
  for(const x of videos){const slot=vlsSevenSlots.find(z=>z[0]===vlsSlotFor(x));
   select.add(new Option((slot?slot[1]:'Versione')+' · '+(x.name||x.key),x.key))}
 }
 $('#vlsSelectA').selectedIndex=0;$('#vlsSelectB').selectedIndex=1;
 vlsCompareLoad('A');vlsCompareLoad('B');$('#vlsVideoB').muted=true;vlsComparePane('A');
 $('#vlsCompareInfo').textContent='La seconda versione è inizialmente senza audio. Il confronto non certifica i contenuti.';
 $('#vlsCompare').showModal();
}
for(const key of ['A','B']){
 $('#vlsSelect'+key).onchange=()=>vlsCompareLoad(key);
 $('#vlsSwitch'+key).onclick=()=>vlsComparePane(key);
}
$('#vlsAlign').onclick=()=>{
 const a=$('#vlsVideoA'),b=$('#vlsVideoB');
 try{b.currentTime=Math.min(Number.isFinite(b.duration)?b.duration:a.currentTime,a.currentTime||0);
 $('#vlsCompareInfo').textContent='Seconda versione allineata al tempo della prima. Avvia la riproduzione quando vuoi.'}
 catch{$('#vlsCompareInfo').textContent='Attendi il caricamento dei metadati prima di allineare.'}
};
$('#vlsCompare').addEventListener('close',()=>{
 for(const key of ['A','B']){const video=$('#vlsVideo'+key);video.pause();video.removeAttribute('src');video.load()}
 vlsCompareState.group=null;
});
$('#vlsFullscreen').onclick=async()=>{
 const video=$('#video');
 try{if(video.requestFullscreen)await video.requestFullscreen();
 else if(video.webkitEnterFullscreen)video.webkitEnterFullscreen();else throw Error('unsupported')}
 catch{log('Usa il tasto schermo intero del player Android.')}
};
let vlsRepairItem=null,vlsRepairSecond=null;
function vlsRepairOpen(x){
 if(!g.admin){$('#adminDialog').showModal();return}
 vlsRepairItem=x;
 vlsRepairSecond=$('#player').open&&g.selected?.key===x.key?Number($('#video').currentTime)||0:null;
 $('#vlsRepairVideo').textContent=x.viewTitle+(vlsRepairSecond!==null?' · '+vlsRepairSecond.toFixed(1)+' s':'');
 $('#vlsIssue').value='regia';$('#vlsIssueNote').value='';$('#vlsRepairInfo').textContent='';
 $('#vlsRepair').showModal();
}
function vlsRepairPrompt(){
 const x=vlsRepairItem;
 return 'Controlla e, se possibile, correggi il problema nel progetto Tra le Pagine / ArtVision.\n'+
 'Repository: https://github.com/GGIANLUCAA/Tra-le-pagine-\nVideo: '+(x.name||x.key)+'\n'+
 'Chiave pubblica catalogo: '+x.key+'\n'+
 (vlsRepairSecond===null?'':'Secondo osservato: '+vlsRepairSecond.toFixed(1)+'\n')+
 'Problema: '+$('#vlsIssue').value+'\n'+
 'Descrizione: '+($('#vlsIssueNote').value.trim()||'Da verificare sul video')+'\n'+
 'Prima verifica repository, workflow, file MP4 reale e regole attive. Non supporre che catalogato equivalga ad approvato, scaricabile per intero o pubblicabile. Se possibile proponi correzione minima e sicura in un ramo separato, con QA e senza toccare master approvati.';
}
$('#vlsRepairFromPlayer').onclick=()=>{if(g.selected&&g.admin)vlsRepairOpen(g.selected)};
$('#vlsCopyGPT').onclick=async()=>{
 if(!vlsRepairItem)return;
 const message=vlsRepairPrompt();
 try{await navigator.clipboard.writeText(message);$('#vlsRepairInfo').textContent='Copiato. Apri ChatGPT e incolla.'}
 catch{$('#vlsRepairInfo').textContent='Copia manualmente il testo selezionato.';const input=$('#vlsIssueNote');input.value=message.slice(0,1500);input.focus();input.select()}
};
let vlsDownloadItem=null,vlsDownloadRequest=0;
async function vlsVerifyDownload(x){
 const request=++vlsDownloadRequest,controller=new AbortController();
 $('#vlsDownloadStatus').textContent='Verifica dei primi byte in corso…';
 const timer=setTimeout(()=>controller.abort(),12000);
 try{
  const r=await fetch(fullURL(x),{method:'GET',headers:{Range:'bytes=0-0'},cache:'no-store',signal:controller.signal});
  if(request!==vlsDownloadRequest)return;
  const range=r.headers.get('content-range')||'',mime=r.headers.get('content-type')||'';
  $('#vlsDownloadStatus').textContent=r.status===206&&/^bytes\s+0-0\/\d+$/i.test(range)&&/(video\/mp4|application\/octet-stream)/i.test(mime)
   ?'Accesso parziale OK (HTTP 206). Integrità dell’MP4 completo NON verificata.'
   :'Verifica rapida non conclusiva (HTTP '+r.status+'). Il download resta possibile, ma non certificato.';
 }catch(e){if(request===vlsDownloadRequest)$('#vlsDownloadStatus').textContent='Verifica non riuscita: '+(e.name==='AbortError'?'tempo scaduto':'rete/archivio non disponibile')+'. Download non certificato.'}
 finally{clearTimeout(timer);controller.abort()}
}
function vlsDownloadOpen(x){
 if(!x||x.available===false){log('Video presente solo in ChatGPT: MP4 non disponibile su questo sito.');return}
 vlsDownloadItem=x;$('#vlsDownloadTitle').textContent='Scarica · '+x.viewTitle;
 $('#vlsDownloadInfo').textContent='File originale · '+size(x.size)+' · '+dur(x.duration);
 $('#vlsDownloadMP4').href=fullURL(x);$('#vlsDownloadZIP').hidden=!g.admin;
 $('#vlsDownload').showModal();vlsVerifyDownload(x);
}
$('#vlsRetryDownload').onclick=()=>{if(vlsDownloadItem)vlsVerifyDownload(vlsDownloadItem)};
$('#vlsDownloadZIP').onclick=async()=>{const x=vlsDownloadItem;if(!x||!g.admin)return;
 $('#vlsDownload').close();await openEditorial(x);if($('#editorial').open)edActivateTab('package');
};
$('#vlsDownload').addEventListener('close',()=>{vlsDownloadRequest++;vlsDownloadItem=null});
function vlsRenderQuick(){
 const node=$('#vlsStudioQuick');node.hidden=!(g.admin&&g.studio);if(node.hidden)return;
 const rows=g.items.filter(x=>!x.hidden);
 const drafts=rows.filter(x=>x.viewVersion==='draft').length,unavailable=rows.filter(x=>x.available===false).length;
 node.replaceChildren(vlsEl('strong','','Sala di regia rapida'),vlsEl('span','',drafts+' provini nel catalogo · '+unavailable+' schede senza MP4 sul sito'));
 const review=vlsEl('button','','Esamina provini');review.type='button';
 review.onclick=()=>{$('#versions').value='draft';$('#availability').value='online';g.category='Tutti';categories();refreshFilter();gotoSection('library')};
 const center=vlsEl('button','','Centro di controllo');center.type='button';center.onclick=openControlCenter;
 node.append(review,center);
}
