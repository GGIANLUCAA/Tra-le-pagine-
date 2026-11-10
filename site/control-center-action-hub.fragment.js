/* Control Center V10 — owner action hub. Pure UI over already fetched public evidence.
   No API writes, no workflow dispatch, no cloud storage of private ChatGPT URLs. */
var ACTION_SLOT_LABELS={critico_standard:"Critico",critico_museum:"Critico Museum",
  cinema_standard:"Cinema",cinema_museum:"Cinema Museum"};
function actionSlotState(v){
  if(!v)return {kind:"unknown",text:"Dati mancanti",next:"Controllare il registro e le fonti."};
  if(!source("queue"))return {kind:"unknown",text:"Registro non disponibile",next:"Ricarica le fonti prima di decidere."};
  if(v.preview_ready&&source("catalog"))
    return {kind:"ready",text:"Guardabile sul sito",next:"Guarda il MP4 e valuta la regia; lo stato Gold non è implicito."};
  if(!source("catalog"))
    return {kind:"unknown",text:"Archivio non verificabile",next:"Riprova il collegamento, non avviare duplicati."};
  if(v.site_catalog&&v.site_available===false)
    return {kind:"offline",text:"Nel catalogo, ma offline",next:"Controlla i byte MP4 e ripristina l'accesso senza un nuovo render."};
  if(v.site_catalog&&v.site_available!==true)
    return {kind:"unknown",text:"Catalogato, stato incerto",next:"Verifica lo streaming reale prima di pubblicare."};
  if(v.recorded)
    return {kind:"registered",text:"Scheda presente, file non accessibile",next:"Cerca MP4/ZIP nelle run e nelle Release; recupera, non duplicare."};
  return {kind:"missing",text:"Variante non individuata",next:"Verifica la coda e le run; produci soltanto se manca davvero."};
}
function actionSlotMode(v){
  var status=actionSlotState(v).kind;
  return status==="ready"?"improve":status==="registered"||status==="offline"||status==="unknown"?"recover":"complete";
}
function contextForActionSlot(work,variant,requested){
  var mode=["complete","recover","improve"].includes(requested)?requested:actionSlotMode(variant);
  var label=variant?.label||ACTION_SLOT_LABELS[variant?.id]||"Variante";
  return {type:"slot",project:"artvision",title:(work?.title||"Opera")+" · "+label,
    detail:actionSlotState(variant).next,work:work,slot:variant,action:mode,run:null};
}
function projectStartContext(key){
  var label=PROJECT_LABELS[key]||"Progetto";
  var health=(state.data?.health||[]).find(function(h){return h.id===key});
  return {type:"project",project:key,title:"Richiedi produzione · "+label,action:"produce",
    detail:health?.state==="running"?
      "È stata osservata una produzione in corso: prima controllare e non avviare duplicati.":
      "Richiesta di una nuova produzione reale, soltanto se non esiste una lavorazione equivalente già attiva.",run:null};
}
function actionWorkflowHelp(key){
  if(key==="artvision")return "queue/artvision_owner_selected_ten_20261102.json · 4×1";
  if(key==="storia")return "La Storia Rivive · produzione e QA per episodi";
  if(key==="wow")return "WOW LAB · produzione isolata";
  return "workflow owner già esistente, se verificato";
}
function actionProjectCards(){
  var health=state.data?.health||[],projects=[["artvision","ArtVision 4×1"],["storia","La Storia Rivive"],["wow","WOW LAB"]];
  return '<section class="actionTop"><div class="overline">PRODUZIONE · ACCESSO RAPIDO</div>'+
    '<h3>Vuoi nuovi video?</h3><p>Scegli un programma. Il pulsante prepara la richiesta per GPT, che deve verificare prima le lavorazioni già in corso. Il pannello pubblico non avvia da solo GitHub o le automazioni.</p>'+
    '<div class="actionProjects">'+projects.map(function(entry){
      var id=entry[0],name=entry[1],row=health.find(function(x){return x.id===id});
      var status=!source("github")?"GitHub non verificabile":row?.state==="running"?"Produzione osservata in corso":
        row?.state==="attention"?"Ultimo workflow da controllare":row?.state==="observed_success"?"Ultimo workflow riuscito":
        row?.state==="unobserved"?"Nessuna run recente osservata":"Stato non noto";
      return '<article class="actionProject"><strong>'+escapeText(name)+'</strong><span>'+escapeText(status)+'</span>'+
        '<small>'+escapeText(actionWorkflowHelp(id))+'</small>'+
        '<button type="button" class="actionPrimary" data-action-project="'+id+'">▶ Richiedi produzione ora</button></article>';
    }).join("")+'</div>'+
    '<p class="actionFine">Avvio effettivo consentito solo da ChatGPT/GitHub con autorizzazioni: nessuna chiamata a pagamento o cron duplicato dal pannello.</p></section>';
}
function actionWorksPanel(){
  if(!source("queue"))return '<div class="panel"><h3>Quadri e video</h3><p class="note">La coda non è verificabile ora. Non classifico alcun video come mancante.</p></div>';
  var works=state.data?.works||[],total=works.reduce(function(n,w){return n+(w.variants||[]).filter(function(v){return v.preview_ready===true}).length},0);
  var count=works.reduce(function(n,w){return n+(w.variants||[]).filter(function(v){return actionSlotState(v).kind!=="ready"}).length},0);
  var out='<section class="panel"><div class="actionHead"><div><h3>Ogni quadro, ogni video</h3><p class="sub">'+total+' anteprime accessibili nel campione · '+count+' slot senza anteprima confermata. Non sono conteggi Gold e non dimostrano mancanza fisica.</p></div>'+
    '<div class="actionFilters"><button data-action-filter="needs" class="'+(state.actionFilter==="needs"?"on":"")+'">Da completare</button>'+
    '<button data-action-filter="all" class="'+(state.actionFilter==="all"?"on":"")+'">Tutte</button>'+
    '<button data-action-filter="ready" class="'+(state.actionFilter==="ready"?"on":"")+'">Guardabili</button></div></div>';
  var filtered=works.filter(function(w){
    var v=w.variants||[];
    return state.actionFilter==="all"||
      (state.actionFilter==="ready"?v.some(function(x){return actionSlotState(x).kind==="ready"}):
       v.some(function(x){return actionSlotState(x).kind!=="ready"}));
  });
  if(!filtered.length)return out+'<div class="empty">Nessuna opera in questa vista, oppure dati incompleti.</div></section>';
  for(const w of filtered){
    var variants=w.variants||[],ready=variants.filter(function(x){return actionSlotState(x).kind==="ready"}).length;
    out+='<details class="actionWork"><summary><span class="actionWorkName">'+escapeText(w.title||"Opera")+
      '<small>'+escapeText(w.artist||"")+'</small></span><span class="actionCount">'+ready+'/4 guardabili sul sito · '+Number(w.delivered||0)+'/4 consegne dichiarate</span></summary>'+
      '<div class="actionSlots">'+variants.map(function(v){
        var status=actionSlotState(v),mode=actionSlotMode(v);
        var action=mode==="improve"?"✦ Migliora con GPT":mode==="recover"?"↻ Recupera video":"▶ Completa video";
        return '<div class="actionSlot"><div class="actionInfo"><strong>'+escapeText(v.label||ACTION_SLOT_LABELS[v.id]||"Variante")+'</strong>'+
          '<span class="actionFlag '+status.kind+'">'+escapeText(status.text)+'</span>'+
          '<small>'+escapeText(status.next)+'</small></div>'+
          '<div class="actionSlotButtons"><button class="actionPrimary" type="button" data-action-work="'+escapeText(w.id||w.title)+
          '" data-action-slot="'+escapeText(v.id||"")+'" data-action-mode="'+mode+'">'+action+'</button>'+
          (v.preview_ready?'<button class="actionSecondary" type="button" data-action-view="'+escapeText(w.id||w.title)+'">▶ Guarda</button>':'')+
          '</div></div>';
      }).join("")+'</div><div class="actionWorkFoot"><button class="actionSecondary" type="button" data-action-open-work="'+escapeText(w.id||w.title)+'">Apri scheda completa e prove</button></div></details>';
  }
  return out+'</section>';
}
function actionInstruction(ctx){
  if(ctx?.type==="slot"){
    if(ctx.action==="improve")return "Guarda il MP4 reale, annota il difetto e chiedi una revisione N+1. Non sovrascrivere la versione originale.";
    if(ctx.action==="recover")return "Cerca prima il file nelle run/Release/Libreria. Verifica download e SHA prima di pensare a un nuovo render.";
    return "Verifica la variante nella coda e nelle run. Se manca davvero, completa questa sola variante senza duplicare l'owner.";
  }
  if(ctx?.action==="produce")return "Richiedi la prossima produzione reale dell'owner. Prima controlla che non sia già in lavorazione.";
  return "Apri la diagnosi nella chat collegata, controlla le prove e correggi soltanto la parte necessaria.";
}
