/* V11 local correction diary and non-duplicating "unblock possible" GPT handoff.
   All browser writes are localStorage; no public API or automatic dispatch. */
var QUALITY_NOTE_STORAGE="artvision.controlCenter.videoCorrections.v1";
var qualityNotes=[];
function qualityKey(ctx){
  var work=String(ctx?.work?.id||""),slot=String(ctx?.slot?.id||"");
  return /^[a-z0-9_-]{3,120}$/i.test(work)?
    "work:"+work+(slot?":"+slot:""):null;
}
function loadQualityNotes(){
  try{
    var raw=JSON.parse(localStorage.getItem(QUALITY_NOTE_STORAGE)||"[]");
    if(!Array.isArray(raw))return [];
    return raw.slice(-100).filter(function(x){
      return x&&typeof x==="object"&&typeof x.id==="string"&&
        /^[a-z0-9_-]{4,96}$/.test(x.id)&&
        typeof x.key==="string"&&/^work:[a-z0-9_-]{3,120}(?::[a-z0-9_]+)?$/i.test(x.key)&&
        typeof x.note==="string"&&x.note.length>=4&&x.note.length<=1800&&
        ["direction","pacing","audio","visual","authenticity","editorial","download","other"].includes(x.category)&&
        x.status==="reported";
    });
  }catch{return []}
}
function saveQualityNotes(){
  try{
    localStorage.setItem(QUALITY_NOTE_STORAGE,JSON.stringify(qualityNotes.slice(-100)));
    return true;
  }catch{return false}
}
function noteForContext(ctx){
  var key=qualityKey(ctx);return key?qualityNotes.filter(function(x){return x.key===key}):[];
}
function formatQualityTimestamp(value){
  var dateValue=new Date(value);
  return Number.isFinite(+dateValue)?dateValue.toLocaleString("it-IT",{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"}):"Data sconosciuta";
}
function renderQualityNotes(ctx){
  var supported=!!(ctx&&ctx.work&&qualityKey(ctx));
  document.getElementById("qualityJournal").hidden=!supported;
  if(!supported)return;
  var rows=noteForContext(ctx).slice().reverse(),holder=document.getElementById("qualityJournalRows");
  holder.replaceChildren();
  if(!rows.length){
    holder.textContent="Nessuna correzione annotata su questo dispositivo per questo video.";
  }else{
    rows.forEach(function(note){
      var item=document.createElement("div");item.className="qualityNoteRow";
      var heading=document.createElement("strong");
      heading.textContent=formatQualityTimestamp(note.created_at)+" · "+note.category+
        (note.owner_requested_generalization?" · candidata per i futuri video":"");
      var body=document.createElement("p");body.textContent=note.note;
      var info=document.createElement("small");
      info.textContent="Salvata su questo Android · da registrare nel repository tramite GPT · non verificata sul MP4";
      item.append(heading,body,info);holder.append(item);
    });
  }
}
function addQualityNote(ctx,sourceText,category,requestedGeneralization){
  if(!ctx||!ctx.work||!qualityKey(ctx))return {ok:false,reason:"Apri la scheda del quadro o della sua variante."};
  var text=String(sourceText||"").trim();
  if(text.length<4||text.length>1800)return {ok:false,reason:"Scrivi cosa hai corretto (4–1800 caratteri)."};
  if(!["direction","pacing","audio","visual","authenticity","editorial","download","other"].includes(category))
    return {ok:false,reason:"Categoria non riconosciuta."};
  var key=qualityKey(ctx);
  var duplicate=qualityNotes.some(function(n){return n.key===key&&n.note===text});
  if(duplicate)return {ok:false,reason:"Questa osservazione è già nella cronologia locale."};
  var row={
    id:"feedback_"+Date.now().toString(36)+"_"+Math.random().toString(36).slice(2,9),
    key:key,work_id:String(ctx.work.id),slot_id:ctx.slot?.id||null,
    filename:String(ctx.slot?.filename||"").slice(0,180),
    project:ctx.project||"artvision",note:text,category:category,
    status:"reported",owner_requested_generalization:requestedGeneralization===true,
    created_at:new Date().toISOString()
  };
  qualityNotes.push(row);
  if(qualityNotes.length>100)qualityNotes=qualityNotes.slice(-100);
  var stored=saveQualityNotes();
  return {ok:true,stored:stored,row:row};
}
function qualityNotesForPrompt(ctx){
  return noteForContext(ctx).slice(-6).map(function(x){
    return {id:x.id,work_id:x.work_id,slot_id:x.slot_id,
      filename:x.filename,note:x.note,category:x.category,
      status:"reported",created_at:x.created_at,
      owner_requested_generalization:x.owner_requested_generalization};
  });
}
function unblockCandidates(){
  if(!source("queue")||!source("catalog"))return [];
  var works=state.data?.works||[],found=[];
  for(const w of works){
    if(/dali|dal[iì]/i.test(String(w.id||"")+" "+String(w.title||"")))continue;
    for(const v of w.variants||[]){
      var current=actionSlotState(v),action=actionSlotMode(v);
      if(current.kind==="ready"||current.kind==="unknown")continue;
      if(!["recover","complete"].includes(action))continue;
      found.push({work_id:w.id,title:w.title,slot_id:v.id,
        label:v.label,status:current.kind,action:action,filename:v.filename||null});
    }
  }
  // Favor rescue of existing produced bytes over new rendering.
  return found.sort(function(a,b){
    var weight={offline:0,registered:1,missing:2};
    return (weight[a.status]??99)-(weight[b.status]??99);
  }).slice(0,10);
}
function unblockContext(){
  var candidates=unblockCandidates();
  return {type:"bulk",project:"artvision",title:"Sblocca i video possibili",
    detail:"Prima recupera i file già prodotti, poi verifica quali varianti mancano davvero.",
    action:"unblock",items:candidates,run:null};
}
