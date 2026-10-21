(() => {
  if (typeof g !== 'object' || typeof draw !== 'function') return;
  const STORAGE = 'vls.workspace.v1', SELECTION = 'vls.selection.v1';
  const roleNames = {voice:'Voce e narrazione',visual:'Stile delle immagini',cover:'Copertina e caratteri',rhythm:'Ritmo e transizioni',music:'Musica e atmosfera',subtitles:'Sottotitoli e testi'};
  let local = [], cloud = [], selecting = false, sharedOnly = null, draft = null, editingId = null, busy = false, cloudAuth = '', workspaceTab = 'style';
  let selected = new Set();
  try {local = JSON.parse(localStorage.getItem(STORAGE) || '[]'); if (!Array.isArray(local)) local = [];} catch {}
  try {const rows=JSON.parse(localStorage.getItem(SELECTION)||'[]');if(Array.isArray(rows))selected=new Set(rows.filter(x=>typeof x==='string').slice(0,200));} catch {}
  function storeLocal(rows) {localStorage.setItem(STORAGE,JSON.stringify(rows)); local=rows;}
  function rememberSelection() {try{localStorage.setItem(SELECTION,JSON.stringify([...selected]));}catch{}}
  const allRecords = () => [...local.filter(x=>!cloud.some(c=>c.id===x.id)),...cloud].sort((a,b)=>Date.parse(b.updatedAt)-Date.parse(a.updatedAt));
  const chosen = () => g.items.filter(x=>selected.has(x.key));
  const snapshot = x => ({key:x.key,title:x.viewTitle || x.title || x.key,category:x.viewCategory || x.category || '',size:x.size || 0});
  const refsNow = () => chosen().map(snapshot);
  const date = value => new Date(value).toLocaleString('it-IT',{dateStyle:'short',timeStyle:'short'});
  const button = (title, action, cls='ghost') => {const b=document.createElement('button');b.className=cls;b.type='button';b.textContent=title;b.onclick=action;return b;};
  const style = document.createElement('style');
  style.textContent = `
  body.vls-selecting{padding-bottom:145px}.vls-selected{outline:2px solid #c5a4fa;outline-offset:2px}.vls-check{position:absolute;top:10px;left:10px;z-index:4;display:flex;align-items:center;justify-content:center;width:42px;height:42px;background:#0a1126e8;border:1px solid #c9b4ed;border-radius:12px;cursor:pointer}.vls-check input{width:22px;height:22px;min-height:0;margin:0;accent-color:#c5a4fa}.vls-selectiontools{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 18px}.vls-selectiontools span{font-size:12px;color:#aebed3}.vls-bulkbar{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);z-index:8;width:min(1040px,calc(100% - 24px));display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:12px;background:#172137f5;border:1px solid #9070bc;border-radius:18px;box-shadow:0 10px 40px #0008;backdrop-filter:blur(16px)}.vls-bulkbar[hidden]{display:none}.vls-bulkbar strong{padding:0 8px;min-width:105px}.vls-bulkbar button{min-height:44px;padding:9px 12px}.vls-modal{width:min(96vw,960px)}.vls-modal .modalhead{position:sticky;top:0;background:#121b2a;z-index:5}.vls-modal h3{font-size:16px}.vls-muted{font-size:12px;color:#aebed3}.vls-refrow{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px solid #2a374b;font-size:13px}.vls-refrow small{color:#aebed3;display:block}.vls-refrow button{padding:3px 9px;min-height:32px}.vls-role{padding:12px;border:1px solid #33445e;border-radius:12px}.vls-role select{width:100%}.vls-role textarea{min-height:70px;resize:vertical}.vls-prompt{width:100%;min-height:220px;resize:vertical;font:12px/1.6 ui-monospace,monospace}.vls-librarylist{display:grid;gap:12px}.vls-record{border:1px solid #35455c;border-radius:13px;padding:14px;background:#172236}.vls-record h3{margin:0 0 6px}.vls-record p{font-size:13px;color:#b4c2d7;white-space:pre-wrap;overflow-wrap:anywhere}.vls-record .modalactions{margin-top:10px}.vls-state{padding:5px 8px;border-radius:6px;background:#29334e;color:#d5c3f1;font-size:11px}.vls-warning{border:1px solid #675533;padding:12px;border-radius:10px;color:#e5cc9d;font-size:12px}.vls-tabs{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:14px}.vls-modal select,.vls-modal input,.vls-modal textarea{max-width:100%}.vls-modal .field{min-width:0}.vls-shared{padding:12px 15px;margin-bottom:16px;border:1px solid #756093;border-radius:12px;background:#201c32}.vls-draftstatus{min-height:24px;color:#c8b7e7;font-size:12px;margin:10px 0}.vls-bulkbar button:disabled{opacity:.45;cursor:not-allowed}#toast{z-index:30;bottom:160px}
  @media(max-width:600px){body.vls-selecting{padding-bottom:230px}.vls-bulkbar{bottom:max(8px,env(safe-area-inset-bottom));gap:6px;padding:10px}.vls-bulkbar strong{width:100%;font-size:13px}.vls-bulkbar button{flex:1 0 auto;font-size:12px;padding:8px}.vls-modal .modalbody{padding:13px}.vls-modal .modalhead{padding:13px}.vls-role{padding:10px}.vls-selectiontools .ghost{font-size:12px;padding:8px 10px}.vls-bulkbar .vls-secondary{display:none}}
  `;
  document.head.append(style);
  const tools = document.createElement('div');tools.className='vls-selectiontools';
  const toggle=button('☑ Seleziona',()=>{selecting=!selecting;draw();});
  tools.append(toggle,button('Seleziona risultati',()=>{const rows=filtered();if(rows.length>200){log('Puoi selezionare fino a 200 video per volta.');return}for(const x of rows)selected.add(x.key);selecting=true;rememberSelection();draw();}),button('✦ Laboratorio',()=>openLibrary('style')));
  const storageHint=document.createElement('span');tools.append(storageHint);
  document.querySelector('#grid').before(tools);
  const bar=document.createElement('div');bar.className='vls-bulkbar';bar.hidden=true;bar.setAttribute('aria-label','Azioni sui video selezionati');
  const count=document.createElement('strong');count.setAttribute('aria-live','polite');bar.append(count);
  const copyNames=button('Copia nomi',()=>{
    draft=null;body.oninput=body.onchange=null;open('Copia i nomi dei selezionati');body.replaceChildren();
    const area=document.createElement('textarea');area.className='vls-prompt';area.readOnly=true;area.setAttribute('aria-label','Nomi dei video selezionati');area.value=chosen().map(x=>x.viewTitle).join('\n');
    const actions=document.createElement('div');actions.className='modalactions';actions.append(button('Titoli',()=>{area.value=chosen().map(x=>x.viewTitle).join('\n');}),button('Nomi originali dei file',()=>{area.value=chosen().map(x=>x.name||x.key).join('\n');}),button('Copia testo',()=>copy(area.value),'btn primary'));body.append(area,actions);
  });
  const copyLinks=button('Copia link',()=>copy(chosen().map(x=>x.viewTitle+'\n'+(x.available===false?'Solo nella libreria ChatGPT':shareURL(x))).join('\n\n')));
  const shareButton=button('Condividi',shareSelection);
  bar.append(copyNames,copyLinks,shareButton,button('✦ Riferimenti',()=>openComposer('project'), 'btn primary'),button('Diario',()=>openComposer('log')),button('Svuota',()=>{selected.clear();rememberSelection();draw();}));
  const archiveButton=button('Archivia',()=>bulk('archive'));archiveButton.classList.add('vls-secondary');bar.append(archiveButton);
  document.body.append(bar);
  const dialog=document.createElement('dialog');dialog.id='vlsWorkspace';dialog.className='vls-modal';
  dialog.innerHTML='<div class="modalhead"><h2 id="vlsModalTitle">Laboratorio</h2><button type="button" class="ghost" id="vlsClose">✕ Chiudi</button></div><div class="modalbody" id="vlsBody"></div>';
  document.body.append(dialog);document.querySelector('#vlsClose').onclick=()=>dialog.close();
  dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
  const body=document.querySelector('#vlsBody');
  function open(title) {document.querySelector('#vlsModalTitle').textContent=title;if(!dialog.open)dialog.showModal();}
  async function copy(value) {
    try {await navigator.clipboard.writeText(value);log('Copiato negli appunti.');}
    catch {const area=document.createElement('textarea');area.value=value;area.className='vls-prompt';body.replaceChildren(area);open('Seleziona e copia il testo');area.focus();area.select();}
  }
  function download(name, value, type='application/json') {const blob=new Blob([value],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);}
  function updateBar() {
    const n=chosen().length;bar.hidden=!n;count.textContent=n+' selezionati';
    document.body.classList.toggle('vls-selecting',n>0);toggle.textContent=selecting?'✓ Fine selezione':'☑ Seleziona';
    archiveButton.disabled=!g.admin;archiveButton.title=g.admin?'Nascondi dal sito, conservando i file':'Disponibile nella gestione privata';
    storageHint.textContent=g.admin?'Stili e diario privati · salvataggio online':'Stili e diario salvati su questo dispositivo';
    if(!g.admin){cloud=[];cloudAuth='';}else if(cloudAuth!==g.token){cloudAuth=g.token;void loadCloud();}
  }
  const originalFiltered=filtered;
  filtered=function(){const rows=originalFiltered();return sharedOnly?rows.filter(x=>sharedOnly.has(x.key)):rows;};
  const originalDraw=draw;
  draw=function(){
    originalDraw();const rows=filtered();
    document.querySelectorAll('#grid .card').forEach((card,i)=>{
      const x=rows[i];if(!x)return;card.classList.toggle('vls-selected',selected.has(x.key));
      if(!selecting && !selected.has(x.key))return;
      const label=document.createElement('label');label.className='vls-check';
      const input=document.createElement('input');input.type='checkbox';input.checked=selected.has(x.key);input.setAttribute('aria-label','Seleziona '+x.viewTitle);
      label.append(input);label.onclick=e=>e.stopPropagation();input.onchange=()=>{
        if(input.checked){if(selected.size>=200){input.checked=false;log('Massimo 200 video selezionati.');return}selected.add(x.key);}else selected.delete(x.key);
        rememberSelection();card.classList.toggle('vls-selected',input.checked);updateBar();
      };card.querySelector('.poster')?.append(label);
    });updateBar();
  };
  async function loadCloud(){
    try {
      const token=g.token,items=[];let cursor='';
      do{const res=await fetch('/api/workspace'+(cursor?'?cursor='+encodeURIComponent(cursor):''),{headers:{Authorization:'Bearer '+token},cache:'no-store'});const data=await res.json();if(!res.ok)throw Error(data.message||'Caricamento non riuscito');items.push(...data.items);cursor=data.cursor||'';}while(cursor&&items.length<1000);
      if(g.admin&&g.token===token){cloud=items.map(x=>({...x,scope:'cloud'}));if(dialog.open&&!draft)openLibrary(workspaceTab);}
    }catch(e){log('Schede online: '+e.message);}
  }
  async function saveRecord(record){
    const now=new Date().toISOString();const value={...record,createdAt:record.createdAt||now,updatedAt:now};
    if(g.admin){
      const res=await fetch('/api/workspace',{method:'POST',headers:{'content-type':'application/json',Authorization:'Bearer '+g.token},body:JSON.stringify({record:value,etag:record.etag||null})});const data=await res.json();
      if(!res.ok)throw Error(data.message||'Salvataggio non riuscito');
      const saved={...data.record,scope:'cloud'};cloud=[saved,...cloud.filter(x=>x.id!==saved.id)];storeLocal(local.filter(x=>x.id!==saved.id));return saved;
    }
    if(record.scope==='cloud')throw Error('Accedi alla gestione per aggiornare questa scheda online.');
    const saved={...value,scope:'device',revision:(record.revision||0)+1};storeLocal([saved,...local.filter(x=>x.id!==saved.id)]);return saved;
  }
  function fresh(type,refs){return {id:crypto.randomUUID(),type,title:'',topic:'',notes:'',refs,roles:{},settings:{format:'Verticale 9:16',duration:'',language:'Italiano',destination:''},archived:false};}
  function openComposer(type,existing){
    if(busy)return;editingId=existing?.id||null;draft=existing?JSON.parse(JSON.stringify(existing)):fresh(type,refsNow());
    if(!existing&&!draft.refs.length){log('Seleziona prima almeno un video.');return;}
    renderComposer();
  }
  function promptFor(record){
    const refs=record.refs||[],lines=['SCHEDA DI PRODUZIONE — '+(record.title||'Nuovo video'),''];
    if(record.topic)lines.push('ARGOMENTO / OBIETTIVO',record.topic,'');
    lines.push('RIFERIMENTI SELEZIONATI');
    refs.forEach((ref,i)=>{lines.push((i+1)+'. '+ref.title,'File originale: '+ref.key,ref.key.startsWith('gpt:')?'Disponibile nella libreria ChatGPT':location.origin+'/watch/'+encodeURIComponent(ref.key));});
    lines.push('','ELEMENTI DA RIUTILIZZARE');
    for(const [role,label] of Object.entries(roleNames)){const value=record.roles?.[role],ref=refs.find(x=>x.key===value?.key);if(ref||value?.note)lines.push(label+': '+(ref?ref.title+' ['+ref.key+']':'Nuova scelta')+(value?.note?'\nIndicazioni: '+value.note:''));}
    lines.push('','IMPOSTAZIONI');for(const [key,label] of Object.entries({format:'Formato',duration:'Durata',language:'Lingua',destination:'Destinazione'}))if(record.settings?.[key])lines.push(label+': '+record.settings[key]);
    if(record.notes)lines.push('','NOTE DI REGIA / COSA MI PIACE',record.notes);
    lines.push('','Questi video sono riferimenti creativi. Verifica i file e le impostazioni originali prima di riprodurre voce, font o effetti. Se un parametro non è disponibile, dichiaralo e descrivi la scelta proposta.');
    return lines.join('\n');
  }
  function captureForm(){
    if(!draft)return;for(const field of ['title','topic','notes'])draft[field]=document.querySelector('#vls-'+field)?.value||'';
    for(const role of Object.keys(roleNames))draft.roles[role]={key:document.querySelector('#vls-role-'+role)?.value||'',note:document.querySelector('#vls-note-'+role)?.value||''};
    for(const field of ['format','duration','language','destination'])draft.settings[field]=document.querySelector('#vls-setting-'+field)?.value||'';
  }
  function renderComposer(){
    open(draft.type==='log'?'Diario dei riferimenti':draft.type==='style'?'Stile riutilizzabile':'Crea dai riferimenti');
    const options='<option value="">Nuova scelta / da definire</option>'+draft.refs.map(x=>'<option value="'+h(x.key)+'">'+h(x.title)+'</option>').join('');
    body.innerHTML='<p class="vls-muted">Scegli cosa prendere da ciascun video. La scheda conserva le tue indicazioni e prepara le istruzioni per la prossima produzione.</p><div class="formgrid"><label class="field full">Nome della scheda<input id="vls-title" maxlength="160" placeholder="Es. Racconto con voce calda e immagini pittoriche" value="'+h(draft.title)+'"></label><label class="field full">Nuovo argomento / obiettivo<textarea id="vls-topic" maxlength="1500" placeholder="Di cosa deve parlare il prossimo video?">'+h(draft.topic)+'</textarea></label></div><h3>'+draft.refs.length+' video di riferimento</h3><div id="vlsRefs"></div><h3>Combina gli elementi</h3><div class="formgrid" id="vlsRoles"></div><h3>Impostazioni della produzione</h3><div class="formgrid">'+Object.entries({format:'Formato',duration:'Durata desiderata',language:'Lingua',destination:'Dove pubblicare'}).map(([key,label])=>'<label class="field">'+label+'<input id="vls-setting-'+key+'" maxlength="160" value="'+h(draft.settings[key]||'')+'" placeholder="'+(key==='duration'?'Es. 3 minuti':key==='destination'?'Es. Facebook, YouTube':'')+'"></label>').join('')+'<label class="field full">Cosa mi piace / note di regia<textarea id="vls-notes" maxlength="6000" placeholder="Es. Mantieni la voce lenta, evita transizioni veloci, usa il font della copertina scelta.">'+h(draft.notes)+'</textarea></label></div><p class="vls-warning">Le impostazioni tecniche non vengono recuperate automaticamente dal solo MP4: qui salvi i riferimenti e le scelte da applicare alla nuova produzione.</p><div class="vls-draftstatus" id="vlsSaveStatus" role="status"></div><div class="modalactions" id="vlsComposerActions"></div><details style="margin-top:18px"><summary>Mostra istruzioni complete</summary><textarea class="vls-prompt" id="vlsPrompt" readonly aria-label="Istruzioni di produzione"></textarea></details>';
    const refsNode=document.querySelector('#vlsRefs');draft.refs.forEach(ref=>{
      const row=document.createElement('div');row.className='vls-refrow';const title=document.createElement('div');title.textContent=ref.title;const small=document.createElement('small');small.textContent=ref.key;title.append(small);row.append(title,button('Rimuovi',()=>{captureForm();draft.refs=draft.refs.filter(x=>x.key!==ref.key);for(const role of Object.keys(roleNames))if(draft.roles[role]?.key===ref.key)draft.roles[role].key='';renderComposer();}));refsNode.append(row);
    });
    const roles=document.querySelector('#vlsRoles');for(const [role,label] of Object.entries(roleNames)){
      const field=document.createElement('label');field.className='field vls-role';field.innerHTML=h(label)+'<select id="vls-role-'+role+'">'+options+'</select><textarea id="vls-note-'+role+'" maxlength="1200" placeholder="Che cosa vuoi riutilizzare o cambiare?">'+h(draft.roles[role]?.note||'')+'</textarea>';roles.append(field);document.querySelector('#vls-role-'+role).value=draft.roles[role]?.key||'';
    }
    const actions=document.querySelector('#vlsComposerActions');
    actions.append(button('Copia istruzioni',()=>{captureForm();void copy(promptFor(draft));},'btn primary'),button('Salva progetto',()=>void saveDraft('project')),button('Salva stile',()=>void saveDraft('style')),button('Salva nel diario',()=>void saveDraft('log')),button('Scarica scheda',()=>{captureForm();download('Scheda_produzione.json',JSON.stringify(draft,null,2));}),button('I miei stili e progetti',()=>openLibrary(draft.type)));
    body.oninput=body.onchange=()=>{captureForm();document.querySelector('#vlsPrompt').value=promptFor(draft);};document.querySelector('#vlsPrompt').value=promptFor(draft);
  }
  async function saveDraft(type){
    if(busy)return;captureForm();const status=document.querySelector('#vlsSaveStatus');if(!draft.title.trim()){status.textContent='Dai un nome alla scheda prima di salvarla.';document.querySelector('#vls-title').focus();return;}
    busy=true;status.textContent='Salvataggio…';
    try{let record={...draft,type};if(type!==draft.type){record.id=crypto.randomUUID();delete record.etag;delete record.createdAt;record.revision=0;}draft=await saveRecord(record);editingId=draft.id;status.textContent=(g.admin?'Salvato online nella gestione privata':'Salvato su questo dispositivo')+' · '+date(draft.updatedAt);log('Scheda salvata.');}
    catch(e){status.textContent=e.message;}finally{busy=false;}
  }
  function openLibrary(type='style',archived=false){
    captureForm();draft=null;editingId=null;body.oninput=body.onchange=null;workspaceTab=type;
    open('Il tuo laboratorio');body.replaceChildren();
    const hint=document.createElement('p');hint.className='vls-muted';hint.textContent=g.admin?'Schede private online e schede conservate su questo dispositivo.':'Le schede sono private e salvate su questo dispositivo. Esportale per portarle su un altro telefono.';body.append(hint);
    const tabs=document.createElement('div');tabs.className='vls-tabs';for(const [key,label]of Object.entries({style:'Stili',project:'Progetti',log:'Diario'}))tabs.append(button(label,()=>openLibrary(key,archived),key===type?'btn primary':'ghost'));
    tabs.append(button(archived?'Torna alle schede':'Cestino schede',()=>openLibrary(type,!archived)));body.append(tabs);
    const header=document.createElement('div');header.className='modalactions';header.append(button('Esporta laboratorio',()=>download('Laboratorio_video.json',JSON.stringify({version:1,records:allRecords()},null,2))),button('Importa schede',()=>importRecords()));
    if(selected.size)header.append(button('Nuovo dai selezionati',()=>openComposer(type)));
    body.append(header);
    const list=document.createElement('div');list.className='vls-librarylist';list.style.marginTop='18px';body.append(list);
    const records=allRecords().filter(x=>x.type===type&&!!x.archived===archived);
    if(!records.length){const p=document.createElement('p');p.className='vls-muted';p.textContent=archived?'Il cestino è vuoto.':'Nessuna scheda salvata. Seleziona dei video e apri Riferimenti per iniziare.';list.append(p);}
    for(const record of records){
      const card=document.createElement('article');card.className='vls-record';const title=document.createElement('h3');title.textContent=record.title;const meta=document.createElement('span');meta.className='vls-state';meta.textContent=(record.scope==='cloud'?'Online privato':'Questo dispositivo')+' · '+record.refs.length+' riferimenti · '+date(record.updatedAt);
      const p=document.createElement('p');p.textContent=(record.topic||record.notes||'').slice(0,300);const actions=document.createElement('div');actions.className='modalactions';
      actions.append(button('Apri',()=>openComposer(record.type,record)),button('Copia istruzioni',()=>copy(promptFor(record))),button('Duplica progetto',()=>{const copyRecord=JSON.parse(JSON.stringify(record));copyRecord.id=crypto.randomUUID();copyRecord.type='project';copyRecord.title+=' — copia';delete copyRecord.etag;delete copyRecord.scope;delete copyRecord.createdAt;copyRecord.revision=0;openComposer('project',copyRecord);}));
      if(g.admin&&record.scope!=='cloud')actions.append(button('Salva online',async()=>{try{await saveRecord(record);openLibrary(type,archived);log('Scheda salvata online.');}catch(e){log(e.message)}}));
      actions.append(button(archived?'Ripristina':'Sposta nel cestino',async()=>{try{await saveRecord({...record,archived:!archived});openLibrary(type,archived);}catch(e){log(e.message)}}));
      card.append(title,meta,p,actions);list.append(card);
    }
    if(g.admin){const actions=document.createElement('div');actions.className='modalactions';actions.append(button('Archivia video selezionati',()=>bulk('archive')),button('Ripristina video selezionati',()=>bulk('restore')));body.append(actions);}
  }
  function importRecords(){
    const input=document.createElement('input');input.type='file';input.accept='.json,application/json';input.onchange=async()=>{
      const file=input.files?.[0];if(!file)return;if(file.size>5000000){log('Il file è troppo grande.');return;}
      try{const data=JSON.parse(await file.text()),rows=Array.isArray(data.records)?data.records:[data];if(rows.length>200)throw Error('Massimo 200 schede per importazione.');
        const imported=rows.map(row=>{
          if(!row||typeof row.title!=='string'||!row.title.trim()||row.title.length>160||!['style','project','log'].includes(row.type)||!Array.isArray(row.refs)||row.refs.length>200)throw Error('File di schede non valido.');
          const refs=row.refs.map(ref=>{if(!ref||typeof ref.key!=='string'||!/^(?:gpt:)?[\w ().-]{1,190}\.(mp4|mov|m4v)$/i.test(ref.key)||typeof ref.title!=='string'||ref.title.length>200)throw Error('Riferimento non valido.');return {key:ref.key,title:ref.title,category:String(ref.category||'').slice(0,160),size:Number(ref.size)||0};});
          const roles={};for(const role of Object.keys(roleNames)){const value=row.roles?.[role];roles[role]={key:refs.some(x=>x.key===value?.key)?value.key:'',note:typeof value?.note==='string'?value.note.slice(0,1200):''};}
          const settings={};for(const key of ['format','duration','language','destination'])settings[key]=typeof row.settings?.[key]==='string'?row.settings[key].slice(0,160):'';
          return {id:crypto.randomUUID(),type:row.type,title:row.title,topic:typeof row.topic==='string'?row.topic.slice(0,1500):'',notes:typeof row.notes==='string'?row.notes.slice(0,6000):'',refs,roles,settings,archived:row.archived===true,scope:'device',createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()};
        });
        storeLocal([...imported,...local]);openLibrary(workspaceTab);log(imported.length+' schede importate su questo dispositivo.');
      }catch(e){log(e.message);}
    };input.click();
  }
  async function shareSelection(){
    const rows=chosen().filter(x=>x.available!==false&&!x.hidden);if(!rows.length){log('Seleziona almeno un video riproducibile.');return;}
    const url=new URL(location.origin+'/');url.searchParams.set('raccolta',JSON.stringify(rows.map(x=>x.key)));
    if(url.href.length>14000){log('La raccolta è troppo grande per un unico link. Condividi un gruppo più piccolo.');return;}
    try{if(navigator.share)await navigator.share({title:'Video selezionati · Video Library Studio',text:rows.length+' video dalla videoteca',url:url.href});else await copy(url.href);}catch(e){if(e.name!=='AbortError')await copy(url.href);}
  }
  async function bulk(action){
    if(busy)return;if(!g.admin){log('Accedi alla gestione privata per archiviare i video.');return;}
    const rows=chosen();if(!rows.length){log('Seleziona prima dei video.');return;}
    const title=action==='archive'?'Archivia '+rows.length+' video':'Ripristina '+rows.length+' video';
    draft=null;body.oninput=body.onchange=null;open(title);body.replaceChildren();const p=document.createElement('p');p.textContent=action==='archive'?'I video saranno nascosti dalla videoteca pubblica. I file originali restano conservati e potrai ripristinarli dalla gestione.':'I video torneranno visibili nella videoteca pubblica.';body.append(p);const confirm=button('Conferma',async()=>{
      busy=true;confirm.disabled=true;try{const res=await fetch('/api/bulk',{method:'POST',headers:{'content-type':'application/json',Authorization:'Bearer '+g.token},body:JSON.stringify({action,keys:rows.map(x=>x.key)})}),data=await res.json();if(!res.ok)throw Error(data.message||'Operazione non riuscita');selected.clear();rememberSelection();dialog.close();await load(true);log(data.count+' video '+(action==='archive'?'archiviati':'ripristinati')+'.');}catch(e){log(e.message);}finally{busy=false;confirm.disabled=false;}
    },'btn primary');body.append(confirm,button('Annulla',()=>dialog.close()));
  }
  try{
    const value=new URL(location.href).searchParams.get('raccolta');if(value&&value.length<=14000){const keys=JSON.parse(value);if(Array.isArray(keys)&&keys.length<=200&&keys.every(k=>typeof k==='string'&&/^[\w ().-]{1,190}\.(mp4|mov|m4v)$/i.test(k))){sharedOnly=new Set(keys);selected=new Set();const banner=document.createElement('div');banner.className='vls-shared';banner.textContent='Raccolta condivisa · '+keys.length+' video ';banner.append(button('Mostra tutta la videoteca',()=>{sharedOnly=null;banner.remove();const url=new URL(location.href);url.searchParams.delete('raccolta');history.replaceState(null,'',url);draw();}));tools.before(banner);}}
  }catch{}
  for(const id of ['availability','project','sort','versions','includeArchived'])document.querySelector('#'+id).onchange=()=>draw();
  document.querySelector('#query').oninput=()=>draw();
  draw();
})();
