
/* Video Library Studio Editorial Dossier V1. Additive routes; one source MP4 kept in R2. */
const EDITORIAL_SCHEMA_VERSION=1;
const edValidKey=k=>typeof k==='string'&&/^(?:gpt:)?[\w ().-]{1,190}\.(?:mp4|m4v|mov)$/i.test(k);
const edEsc=s=>String(s==null?'':s);
const edAscii=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^A-Za-z0-9-]+/g,'_').replace(/^_+|_+$/g,'').slice(0,100)||'Video';
const edFilesKey=k=>'catalog/editorial/'+k+'.json';
// V37: objective pre-publication checks. Human editorial and rights review still required.
const edPublicPlatforms={facebook:40,instagram:25,tiktok:12,youtube:40};
function edSocialIssues(rec){
 const issues=[],copies=[];
 const forbidden=/\b(?:montaggio|inquadra(?:tura|ture)|zoom|render(?:ing)?|workflow|prompt|algoritm[oi]|regia|sceneggiatura|generat[oa] con (?:ai|ia)|intelligenza artificiale|video generato|tecnich[ea] di montaggio)\b/i;
 const generic=/\b(?:un viaggio tra musica e immagini|una nuova produzione audiovisiva da scoprire|un racconto audiovisivo da ascoltare|un'opera, mille dettagli|quale momento del racconto ti e piaciuto|descrizione e crediti saranno integrati)\b/i;
 for(const [platform,minWords] of Object.entries(edPublicPlatforms)){
  const copy=String(rec?.[platform]||'').trim(),body=copy.replace(/#\p{L}[\p{L}\p{N}_]*/gu,' ').replace(/https?:\/\/\S+/g,' ').trim();
  const words=body.split(/\s+/).filter(Boolean).length;
  if(words<minWords)issues.push(platform+': testo assente o troppo breve per una descrizione curata');
  if(forbidden.test(body))issues.push(platform+': contiene linguaggio tecnico riservato al dossier');
  if(generic.test(body))issues.push(platform+': formula generica da riscrivere');
  if(copy)copies.push({platform,text:body.toLocaleLowerCase('it').replace(/\s+/g,' ')});
 }
 for(let i=0;i<copies.length;i++)for(let j=0;j<i;j++)
  if(copies[i].text===copies[j].text)issues.push(copies[i].platform+': testo identico a '+copies[j].platform);
 // Structured checks cannot establish literary quality or verify all the facts.
 return issues;
}
async function edExists(k){
 if(!edValidKey(k))return false;
 if(!k.startsWith('gpt:'))return !!await env.VIDEOS.head(k);
 const idx=await readJSON('catalog/chatgpt-index.json');
 return Array.isArray(idx)&&idx.some(x=>x.name===k.slice(4));
}
async function edInfo(k){
 if(!k.startsWith('gpt:'))return videoDetails(k);
 const idx=await readJSON('catalog/chatgpt-index.json'),v=Array.isArray(idx)?idx.find(x=>x.name===k.slice(4)):null;
 const base=k.slice(4).replace(/\.(mp4|m4v|mov)$/i,'').replace(/_/g,' ');
 const e=(await readJSON('catalog/manage.json'))[k]||{};
 return {key:k,title:e.title||base,description:e.description||'',genre:e.category||'Video da ChatGPT',version:e.version||'unknown',duration:null,width:null,height:null,createdAt:v?.createdAt||null,filename:base+'.mp4',size:v?.size||0,available:false};
}
function edTemplate(m){
 const title=m.title||'Video senza titolo',genre=m.genre||'Video creativi';
 const classification=/musica|motion|visual/i.test(genre)?'music':/critica/i.test(genre)?'critique':/art|pittura/i.test(genre)?'art':/libr/i.test(genre)?'book':'general';
 const fallback={
 music:'Un viaggio tra musica e immagini in movimento, per lasciarsi guidare dal ritmo e dalle forme.',
 critique:'Un percorso tra i dettagli di un’opera, alla ricerca di nuove prospettive e interpretazioni.',
 art:'Un viaggio nelle opere e nei particolari che meritano uno sguardo più attento.',
 book:'Un racconto audiovisivo da ascoltare e guardare, seguendo il filo della storia.',
 general:'Una nuova produzione audiovisiva da scoprire.'
 }[classification];
 const description=(m.description||'').trim()||fallback;
 const question={music:'Quale passaggio visivo ti ha colpito di più?',critique:'Quale dettaglio ti ha fatto riflettere?',art:'Quale particolare ti è rimasto impresso?',book:'Quale momento del racconto ti è piaciuto di più?',general:'Qual è il momento che rivedresti?'}[classification];
 const tags={
 music:'#Musica #VisualMusic #ArteDigitale #MusicMotion',
 critique:'#StoriaDellArte #Arte #CriticaDArte',
 art:'#Arte #StoriaDellArte #Capolavori',
 book:'#Libri #Racconti #Letteratura',
 general:'#VideoCreativi #Creativita #Cinema'
 }[classification];
 const hook={music:'Quando la musica prende forma',critique:'I dettagli che cambiano il modo di guardare',art:'Un’opera, mille dettagli',book:'Una storia da vedere e ascoltare',general:'Una nuova storia da scoprire'}[classification];
 // V37: never present title/category boilerplate as publishable social captions.
 // Existing historical descriptions remain the preferred source in edLoad().
 const main='',ig='',tt='',yt='';
 return {
  schemaVersion:EDITORIAL_SCHEMA_VERSION,key:m.key,publicTitle:title,shortDescription:description,
  category:genre,project:'',language:'it',hook,hashtags:tags,
  facebook:main,instagram:ig,tiktok:tt,youtube:yt,
  musicTitle:'',musicAuthor:'',musicLicense:'',musicLink:'',
  imageCredits:'',imageSources:'',voiceCredits:'',sources:'',
  bookAuthor:'',publicationYear:'',seriesTitle:'',selectionReason:'',targetAudience:'',narrativeThemes:'',visualMix:'',sourceEvidence:'',assetLedger:'',
  directorNotes:'',storyboard:'',script:'',productionPrompt:'',
  productionSteps:'',technicalNotes:'',socialInstructions:'',
  publicationNotes:'',tags:'',edition:'',reprints:'',masterRef:'',musicAttribution:'',legacyNotes:'',rightsStatus:'da_verificare',
  publicationStatus:'bozza',createdAt:null,updatedAt:null,
  authoring:'autogenerated',rule:'VLS-EDITORIAL-1.0'
 };
}

/* V35: Read evidence ONLY from a real PROJECT_V13 attachment. Never infer verification. */
const ev35=s=>typeof s==='string'?s.trim():'';
function v35ProjectFields(p){
 if(!p||p.schema!=='video-project-v13')return {};
 const plan=p.editorial_plan||{},biz=p.business||{},bib=p.bibliography||{},m=p.editorial_metadata||{};
 const decisions=Array.isArray(plan.media_sourcing?.decisions)?plan.media_sourcing.decisions:[];
 const map=new Map(decisions.filter(x=>x&&x.asset_id).map(x=>[x.asset_id,x]));
 const ev=(Array.isArray(plan.sources)?plan.sources:[]).filter(x=>x&&typeof x==='object').slice(0,40).map((v,i)=>
  (i+1)+'. '+ev35(v.reference)+' | Dato: '+ev35(v.finding)+' | Verifica dichiarata: '+ev35(v.verification)).join('\n').slice(0,25000);
 const ledger=(Array.isArray(p.assets)?p.assets:[]).filter(x=>x?.id).slice(0,100).map((a,i)=>{
  const d=map.get(a.id)||{};return (i+1)+'. '+ev35(a.id)+' | '+ev35(a.file||a.name)+
  ' | Fonte: '+ev35(d.source_reference||a.source)+' | Diritti dichiarati: '+ev35(a.rights)+
  ' | Rights review: '+ev35(d.rights_review||'pending')+' | Visual review: '+ev35(d.visual_review||'pending');
 }).join('\n').slice(0,25000);
 const story=(Array.isArray(p.scenes)?p.scenes:[]).filter(x=>x&&typeof x==='object').slice(0,100).map((a,i)=>
  (i+1)+'. '+ev35(a.description)+' | Funzione: '+ev35(a.reason)+' | Asset: '+ev35(a.asset_id)).join('\n').slice(0,10000);
 const all={bookAuthor:ev35(bib.author||m.author),publicationYear:ev35(bib.publication_year||m.year),
  seriesTitle:ev35(m.series),selectionReason:ev35(plan.subject_insight),targetAudience:ev35(biz.audience),
  narrativeThemes:ev35(m.themes),visualMix:ev35(plan.mix_reason),sourceEvidence:ev,assetLedger:ledger,
  storyboard:story,hook:ev35(plan.opening_promise)};
 return Object.fromEntries(Object.entries(all).filter(([k,v])=>v).map(([k,v])=>[k,v.slice(0,['hook','publicationYear','bookAuthor','seriesTitle','targetAudience'].includes(k)?1600:25000)]));
}
async function v35FindProject(assets){
 const a=assets.find(x=>x.name==='PROJECT_V13.json'&&x.size>20&&x.size<=250000);
 if(!a)return null;
 try{const f=await env.VIDEOS.get(a.key);const o=f&&await f.json();return o?.schema==='video-project-v13'?o:null}catch{return null}
}


async function edOriginalPosts(assets){
 const posts={},sources={};
 for(const platform of Object.keys(edPublicPlatforms)){
  const candidates=assets.filter(a=>a.size>0&&a.size<=100000&&/^(txt|md)$/.test(a.extension)&&new RegExp(platform,'i').test(a.name)&&/post|caption|descrizion|testo/i.test(a.name));
  const values=[];
  for(const a of candidates.slice(0,8)){
   const obj=await env.VIDEOS.get(a.key);if(!obj)continue;
   const text=(await new Response(obj.body).text()).trim();
   if(text&&text.length<=25000)values.push({text,file:a.name});
  }
  const unique=[...new Set(values.map(v=>v.text.replace(/\r\n/g,'\n')))];
  if(unique.length===1){posts[platform]=values[0].text;sources[platform]={kind:'attachment',label:'Post originale recuperato — da revisionare',file:values[0].file};}
  else if(unique.length>1)sources[platform]={kind:'conflict',label:'Più post originali diversi: scegli dal dossier',files:values.map(v=>v.file)};
 }
 return {posts,sources};
}

async function edLoad(k){
 const meta=await edInfo(k),template=edTemplate(meta);
 const oldNotes=await readJSON('production/notes.json'),old=oldNotes[k]||{};
 const linked={
  facebook:old.socialFacebook||template.facebook,
  instagram:old.socialInstagram||template.instagram,
  tiktok:old.socialTikTok||template.tiktok,
  youtube:old.socialYouTube||template.youtube,
  hashtags:old.socialTags||template.hashtags,
  socialInstructions:old.publicationInstructions||'',
  directorNotes:old.directions||'',
  storyboard:old.storyboard||'',
  productionSteps:old.recipe||'',
  shortDescription:old.brief||template.shortDescription,
  imageSources:old.visualSources||'',
  musicAttribution:old.musicCredits||'',
  publicationNotes:old.notes||'',
  edition:old.edition||'',reprints:old.reprints||'',
  masterRef:old.masterRef||'',legacyNotes:old.notes||''
 };
 const saved=await readJSON(edFilesKey(k));
 const isSaved=saved&&saved.schemaVersion===EDITORIAL_SCHEMA_VERSION&&saved.key===k;
 const prefix='production/files/'+encodeURIComponent(k)+'/';
 const listing=await env.VIDEOS.list({prefix,limit:200});
 const assets=listing.objects.filter(a=>!a.key.endsWith('/')).map(a=>({
  name:decodeURIComponent(a.key.slice(prefix.length)),size:a.size,key:a.key,
  extension:a.key.split('.').pop().toLowerCase()
 }));
 const project=await v35FindProject(assets),derived=project?v35ProjectFields(project):{};
 const rec={...template,...linked,...(isSaved?saved:{}),key:k,schemaVersion:EDITORIAL_SCHEMA_VERSION};
 for(const [k,v] of Object.entries(derived))if(!rec[k]||(!isSaved&&k==='hook'))rec[k]=v;
 const originals=await edOriginalPosts(assets),socialSources={};
 for(const platform of Object.keys(edPublicPlatforms)){
  const savedHas=isSaved&&Object.prototype.hasOwnProperty.call(saved,platform);
  if(!rec[platform]&&!savedHas&&originals.posts[platform])rec[platform]=originals.posts[platform];
  socialSources[platform]=savedHas?{kind:saved[platform]?'saved':'missing',label:saved[platform]?'Testo salvato nel dossier — da revisionare':'Testo mancante'}:
   old['social'+platform[0].toUpperCase()+platform.slice(1)]?{kind:'legacy',label:'Post originale dallo Studio — da revisionare'}:
   originals.sources[platform]||{kind:'missing',label:'Testo mancante'};
 }
 // Archive is the authority for category; historical dossier values stay in storage.
 rec.category=meta.genre;
 const socialIssues=edSocialIssues(rec);
 return {record:rec,metadata:meta,assets,socialSources,projectV13Attached:!!project,generated:!isSaved||rec.authoring==='autogenerated',socialIssues,missing:[
  !rec.sources&&!rec.imageSources&&!rec.sourceEvidence?'fonti delle immagini e dell’opera':null,
  !(rec.musicAttribution||(rec.musicTitle&&rec.musicAuthor))||!rec.musicLicense?'autore e licenza della musica':null,
  !rec.script?'testo o sceneggiatura originali':null,
  !rec.storyboard?'scaletta o regia delle scene':null,
  !rec.productionPrompt&&!rec.productionSteps?'ricetta di produzione':null,
  ...socialIssues.map(x=>'testo social: '+x)
 ].filter(Boolean)};
}
function edTxt(s){return edEsc(s).replace(/\r\n/g,'\n').replace(/\r/g,'\n')}
const edFields=['bookAuthor','publicationYear','seriesTitle','selectionReason','targetAudience','narrativeThemes','visualMix','sourceEvidence','assetLedger','edition','reprints','masterRef','musicAttribution','legacyNotes','publicTitle','shortDescription','category','project','language','hook','hashtags','facebook','instagram','tiktok','youtube','musicTitle','musicAuthor','musicLicense','musicLink','imageCredits','imageSources','voiceCredits','sources','directorNotes','storyboard','script','productionPrompt','productionSteps','technicalNotes','socialInstructions','publicationNotes','tags','rightsStatus','publicationStatus'];
const edLarge=new Set(['selectionReason','narrativeThemes','visualMix','sourceEvidence','assetLedger','musicAttribution','legacyNotes','facebook','instagram','tiktok','youtube','imageCredits','imageSources','sources','directorNotes','storyboard','script','productionPrompt','productionSteps','technicalNotes','socialInstructions','publicationNotes']);
function edSnapshot(k,record,metadata,missing){
 const p=s=>edTxt(s||'Da completare / verificare');
 const info=[
 'VIDEO LIBRARY STUDIO — DOSSIER DI PRODUZIONE','',
 'Titolo: '+record.publicTitle,
 'Autore: '+p(record.bookAuthor),'Prima pubblicazione: '+p(record.publicationYear),
 'Serie: '+p(record.seriesTitle),'Motivo scelta: '+p(record.selectionReason),
 'Pubblico: '+p(record.targetAudience),'Temi: '+p(record.narrativeThemes),
 'Mix visivo: '+p(record.visualMix),
 'Categoria: '+record.category,
 'Progetto: '+p(record.project),
 'Stato versione: '+metadata.version,
 'Stato pubblicazione: '+record.publicationStatus,
 'Stato diritti: '+record.rightsStatus,
 'Descrizione: '+record.shortDescription,
 'Durata: '+(metadata.duration||'non disponibile')+' secondi',
 'Risoluzione: '+(metadata.width&&metadata.height?metadata.width+' × '+metadata.height:'non rilevata'),
 'File originale: '+metadata.key,
 'Dimensione: '+metadata.size+' byte',
 'Data ChatGPT: '+(metadata.createdAt||'sconosciuta'),
 'Ultimo aggiornamento scheda: '+(record.updatedAt||'bozza autogenerata'),
 'Lingua: '+record.language,
 'Edizione: '+p(record.edition),'Ristampe / numero copie: '+p(record.reprints),
 'Riferimento master: '+p(record.masterRef),
 '',
 'CAMPI DA COMPLETARE',...missing.map(s=>'- '+s),
 '',
 'AVVERTENZA',
 'Le descrizioni iniziali sono bozze ricavate da titolo/categoria, non da una visione integrale del filmato.',
 'Non pubblicare attribuzioni, musica e licenze senza controllare le fonti.',
 'Il filmato originale rimane uno solo nell’archivio; questo ZIP è generato solo quando richiesto.'
 ].join('\n');
 const credits=['CREDITI E FONTI','',
 'Musica: '+p(record.musicTitle),
 'Crediti musicali già presenti nel progetto: '+p(record.musicAttribution),
 'Compositore/autore: '+p(record.musicAuthor),
 'Licenza musicale: '+p(record.musicLicense),
 'Fonte/licenza musica: '+p(record.musicLink),
 'Immagini e opere: '+p(record.imageCredits),
 'Sorgenti immagini: '+p(record.imageSources),
 'Voce e narrazione: '+p(record.voiceCredits),
 'Fonti consultate: '+p(record.sources),
 'Riferimenti bibliografici dichiarati (non controllati automaticamente): '+p(record.sourceEvidence),
 'Registro asset e diritti dichiarati: '+p(record.assetLedger),
 'Stato verifica diritti: '+record.rightsStatus,
 'Verificare che siano disponibili i diritti di utilizzo prima della pubblicazione.'
 ].join('\n');
 const direction=['REGIA / SCENE','',p(record.directorNotes),'','STORYBOARD / SCALLETTA','',p(record.storyboard),
 '','SCENEGGIATURA / TESTO NARRATO','',p(record.script)].join('\n');
 const recipe=['RICETTA DI PRODUZIONE','', 'Prompt / istruzioni di creazione:',p(record.productionPrompt),
 '','Passaggi di produzione:',p(record.productionSteps),
 '','Informazioni tecniche:',p(record.technicalNotes),
 '','Istruzioni per i social:',p(record.socialInstructions),
 '','Note di pubblicazione:',p(record.publicationNotes),
 '','Note storiche del progetto:',p(record.legacyNotes)].join('\n');
 return {info,credits,direction,recipe};
}
function edFiles(rec,m,missing){
 const docs=edSnapshot(m.key,rec,m,missing);
 const base=[
  {name:'00_LEGGIMI.txt',text:'VIDEO LIBRARY STUDIO — PACCHETTO SOCIAL\n\n'+
  'Questo ZIP viene generato solo quando lo scarichi, senza creare copie video permanenti.\n'+
  'La cartella SOCIAL contiene testi per Facebook, Instagram, TikTok e YouTube pronti da rivedere.\n'+
  'La cartella PROGETTO contiene la scheda, fonti, crediti, regia, storyboard e ricetta.\n'+
  'I campi non verificati sono segnalati. Non inserire musiche o licenze inventate.\n'+
  (m.available===false?'Il video è attualmente registrato soltanto nella libreria ChatGPT e non può essere incluso nello ZIP.\n':'')+
  '\nIl file MP4 compare solo nella versione del pacchetto COMPRENSIVA DI VIDEO.\n'},
  {name:'01_SOCIAL/Facebook_post.txt',text:rec.facebook},
  {name:'01_SOCIAL/Instagram_caption.txt',text:rec.instagram},
  {name:'01_SOCIAL/TikTok_descrizione.txt',text:rec.tiktok},
  {name:'01_SOCIAL/YouTube_descrizione.txt',text:rec.youtube},
  {name:'01_SOCIAL/Hook_e_hashtag.txt',text:'HOOK:\n'+rec.hook+'\n\nHASHTAG:\n'+rec.hashtags+'\n'},
  {name:'02_PROGETTO/Scheda_produzione.txt',text:docs.info},
  {name:'02_PROGETTO/Fonti_e_crediti.txt',text:docs.credits},
  {name:'02_PROGETTO/Regia_e_sceneggiatura.txt',text:docs.direction},
  {name:'02_PROGETTO/Ricetta_e_istruzioni.txt',text:docs.recipe},
  {name:'02_PROGETTO/Scheda_completa.json',text:JSON.stringify({metadata:m,editorial:rec,missing},null,2)+'\n'}
 ];
 return base;
}
function edU16(a,i,v){a[i]=v&255;a[i+1]=(v>>>8)&255}
function edU32(a,i,v){a[i]=v&255;a[i+1]=(v>>>8)&255;a[i+2]=(v>>>16)&255;a[i+3]=(v>>>24)&255}
const edEncoder=new TextEncoder();
const edCrcTable=(()=>{const t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let j=0;j<8;j++)c=c&1?0xedb88320^(c>>>1):c>>>1;t[n]=c>>>0}return t})();
function edCRC(prev,bytes){let c=prev;for(let i=0;i<bytes.length;i++)c=edCrcTable[(c^bytes[i])&255]^(c>>>8);return c>>>0}
function edJoin(...bufs){const b=new Uint8Array(bufs.reduce((s,x)=>s+x.length,0));let p=0;for(const a of bufs){b.set(a,p);p+=a.length}return b}
function edDate(){const now=new Date();return {time:(now.getHours()<<11)|(now.getMinutes()<<5)|(Math.floor(now.getSeconds()/2)),date:((Math.max(now.getFullYear(),1980)-1980)<<9)|((now.getMonth()+1)<<5)|now.getDate()}}
async function* edGenerateZIP(files){
 const entries=[];let offset=0;
 const dt=edDate();
 for(const file of files){
  const fname=edEncoder.encode(file.name);
  if(fname.length>65535)throw Error('Nome file troppo lungo');
  const start=offset,local=new Uint8Array(30);
  edU32(local,0,0x04034b50);edU16(local,4,20);edU16(local,6,0x0808);edU16(local,8,0);
  edU16(local,10,dt.time);edU16(local,12,dt.date);edU16(local,26,fname.length);
  const header=edJoin(local,fname);offset+=header.length;yield header;
  let sz=0,crc=0xffffffff;
  if(file.text!==undefined){
   const bytes=edEncoder.encode(edTxt(file.text));sz=bytes.length;crc=edCRC(crc,bytes);offset+=bytes.length;yield bytes;
  }else if(file.object){
   const reader=file.object.body.getReader();
   try{
    while(true){
     const next=await reader.read();if(next.done)break;
     const chunk=next.value;if(!chunk||!chunk.length)continue;
     sz+=chunk.length;if(sz>4294967295)throw Error('ZIP64 non supportato: file troppo grande');
     crc=edCRC(crc,chunk);offset+=chunk.length;yield chunk;
    }
   }finally{reader.releaseLock()}
   if(sz!==file.object.size)throw Error('Dimensione file non corretta: '+file.name);
  }
  crc=(crc^0xffffffff)>>>0;
  const descriptor=new Uint8Array(16);edU32(descriptor,0,0x08074b50);edU32(descriptor,4,crc);edU32(descriptor,8,sz);edU32(descriptor,12,sz);
  offset+=descriptor.length;yield descriptor;
  entries.push({fname,start,crc,sz});
 }
 const centralStart=offset;
 for(const en of entries){
  const dir=new Uint8Array(46);edU32(dir,0,0x02014b50);
  edU16(dir,4,20);edU16(dir,6,20);edU16(dir,8,0x0808);edU16(dir,10,0);
  edU16(dir,12,dt.time);edU16(dir,14,dt.date);edU32(dir,16,en.crc);
  edU32(dir,20,en.sz);edU32(dir,24,en.sz);edU16(dir,28,en.fname.length);
  edU32(dir,42,en.start);
  const buf=edJoin(dir,en.fname);offset+=buf.length;yield buf;
 }
 const last=new Uint8Array(22);edU32(last,0,0x06054b50);
 edU16(last,8,entries.length);edU16(last,10,entries.length);
 edU32(last,12,offset-centralStart);edU32(last,16,centralStart);yield last;
}
function edAsStream(iterator){
 return new ReadableStream({async pull(controller){
  try{const x=await iterator.next();if(x.done)controller.close();else controller.enqueue(x.value)}
  catch(e){controller.error(e)}
 },async cancel(){try{await iterator.return()}catch{}}});
}
async function edSigner(){
 const seed=String(env.ADMIN_KEY_SHA256||'');if(!/^[a-f0-9]{64}$/i.test(seed))throw Error('Chiave server non configurata');
 return crypto.subtle.importKey('raw',edEncoder.encode(seed),{name:'HMAC',hash:'SHA-256'},false,['sign','verify']);
}
const edHex=bytes=>Array.from(new Uint8Array(bytes),v=>v.toString(16).padStart(2,'0')).join('');
async function edSign(input){return edHex(await crypto.subtle.sign('HMAC',await edSigner(),edEncoder.encode(input)))}
async function edCheck(input,sig){if(!/^[a-f0-9]{64}$/i.test(sig))return false;const bytes=new Uint8Array(sig.match(/.{2}/g).map(x=>parseInt(x,16)));return crypto.subtle.verify('HMAC',await edSigner(),bytes,edEncoder.encode(input))}
if(u.pathname==='/api/editorial'&&req.method==='GET'){
 if(!await auth())return new Response('Non autorizzato',{status:401});
 const key=u.searchParams.get('key')||'';if(!await edExists(key))return new Response('Video inesistente',{status:404});
 const res=await edLoad(key);
 return json({ok:true,...res,automaticDefaults:true,note:'La bozza viene creata automaticamente per ogni nuovo video. Fonti e crediti vanno verificati prima di pubblicare.'});
}
if(u.pathname==='/api/editorial'&&req.method==='POST'){
 if(!await auth())return new Response('Non autorizzato',{status:401});
 if(Number(req.headers.get('content-length')||0)>350000)return new Response('Scheda troppo grande',{status:413});
 let body;try{body=await req.json()}catch{return new Response('Richiesta errata',{status:400})}
 const key=body?.key;if(!await edExists(key))return new Response('Video inesistente',{status:404});
 if(!body?.data||Array.isArray(body.data)||typeof body.data!=='object')return new Response('Campi non validi',{status:400});
 const snapshot=await edLoad(key),rec={...snapshot.record};
 for(const [name,value] of Object.entries(body.data)){
  if(!edFields.includes(name)||typeof value!=='string')return new Response('Campo non consentito: '+name,{status:400});
  const limit=edLarge.has(name)?25000:1600;
  if(value.length>limit)return new Response('Testo troppo lungo: '+name,{status:400});
  if(name==='category'&&value.trim()!==snapshot.metadata.genre)return new Response('Cambia la categoria dal menu del video: Sposta in categoria.',{status:409});
  rec[name]=value.trim();
 }
 if(!['da_verificare','verificato','non_utilizzabile'].includes(rec.rightsStatus))return new Response('Diritti non validi',{status:400});
 if(!['bozza','da_revisionare','approvato','pubblicato'].includes(rec.publicationStatus))return new Response('Stato non valido',{status:400});
 const socialIssues=edSocialIssues(rec);
 if(['approvato','pubblicato'].includes(rec.publicationStatus)&&socialIssues.length)
  return new Response(JSON.stringify({ok:false,code:'SOCIAL_REVIEW_REQUIRED',issues:socialIssues,status:'da_revisionare'}),{status:422,headers:{'content-type':'application/json; charset=utf-8'}});
 rec.updatedAt=new Date().toISOString();rec.createdAt=rec.createdAt||rec.updatedAt;rec.authoring='edited';
 await env.VIDEOS.put(edFilesKey(key),JSON.stringify(rec),{httpMetadata:{contentType:'application/json'}});
 return json({ok:true,record:rec,missing:(await edLoad(key)).missing});
}
if(u.pathname==='/api/social-package-link'&&req.method==='POST'){
 if(!await auth())return new Response('Non autorizzato',{status:401});
 let body;try{body=await req.json()}catch{return new Response('Richiesta errata',{status:400})}
 const key=body?.key,mode=body?.mode==='full'?'full':body?.mode==='light'?'light':null;
 if(!mode||!await edExists(key))return new Response('Video o modalità non valida',{status:400});
 if(mode==='full'&&key.startsWith('gpt:'))return new Response('MP4 ancora solo su ChatGPT. Usa ZIP leggero.',{status:409});
 const exp=Math.floor(Date.now()/1000)+300;
 const sig=await edSign(key+'|'+mode+'|'+exp);
 const href=u.origin+'/api/social-package?key='+encodeURIComponent(key)+'&mode='+mode+'&exp='+exp+'&sig='+sig;
 return json({ok:true,url:href,expiresInSeconds:300,mode});
}
if(u.pathname==='/api/social-package'&&req.method==='GET'){
 const key=u.searchParams.get('key')||'',mode=u.searchParams.get('mode')||'',
 exp=Number(u.searchParams.get('exp')),sig=u.searchParams.get('sig')||'';
 const now=Math.floor(Date.now()/1000);
 if(!edValidKey(key)||!['full','light'].includes(mode)||!Number.isSafeInteger(exp)||exp<now||exp>now+300||!await edCheck(key+'|'+mode+'|'+exp,sig))return new Response('Collegamento non valido o scaduto',{status:403});
 if(!await edExists(key))return new Response('Video non trovato',{status:404});
 const e=await edLoad(key),m=e.metadata,files=edFiles(e.record,m,e.missing);
 if(e.assets.length){
  files.push({name:'02_PROGETTO/Inventario_materiali_originali.txt',text:e.assets.map(x=>x.name+' ('+x.size+' byte)').join('\n')+'\n'});
  let added=0,addedBytes=0;
  for(const item of e.assets){
   if(added>=40||item.size>40000000||addedBytes+item.size>95000000||item.extension==='zip')continue;
   const object=await env.VIDEOS.get(item.key);if(!object)continue;
   const name=item.name,ext=item.extension;
   files.push({name:'05_ALLEGATI/'+edAscii(name.slice(0,-ext.length-1))+'.'+edAscii(ext),object});
   added++;addedBytes+=item.size;
  }
 }
 const isGPT=key.startsWith('gpt:');
 if(!isGPT){
  const coverKey=key.replace(/\.(mp4|m4v|mov)$/i,'.jpg');
  const cover=await env.VIDEOS.get(coverKey);
  if(cover)files.push({name:'03_COPERTINA/Copertina_originale.jpg',object:cover});
 }
 if(mode==='full'){
  const video=await env.VIDEOS.get(key);
  if(!video)return new Response('Video mancante',{status:404});
  if(video.size>4294967295)return new Response('Dimensione maggiore di 4 GB non supportata nello ZIP',{status:413});
  files.push({name:'04_VIDEO/'+edAscii(e.record.category)+'__'+edAscii(e.record.publicTitle)+'.'+key.split('.').pop().toLowerCase(),object:video});
 }
 if(files.length>65535)return new Response('Troppi file',{status:413});
 const label=['VideoLibraryStudio',edAscii(e.record.category),edAscii(e.record.publicTitle),mode==='full'?'COMPLETO':'SOCIAL_TESTI'].filter(Boolean).join('__').slice(0,185)+'.zip';
 return new Response(edAsStream(edGenerateZIP(files)),{headers:{
  'content-type':'application/zip',
  'content-disposition':'attachment; filename="'+label+'"',
  'cache-control':'private, no-store',
  'x-content-type-options':'nosniff',
  'referrer-policy':'no-referrer'
 }});
}

