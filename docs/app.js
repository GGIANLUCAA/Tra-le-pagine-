import {initVideoLibrary,getPublishedVideos,videoForEpisode,watchVideo} from "./videoteca_v11.js";
import {loadGallery,makeEpisodeCard,showEpisodePreview,initEpisodePreview} from "./episode_gallery_v10.js";
/* Tra le Pagine V9 — static frontend, no user token in browser. */
const OWNER = "GGIANLUCAA";
const REPO = "Tra-le-pagine-";
const REPO_URL = "https://github.com/" + OWNER + "/" + REPO;
const API_URL = "https://api.github.com/repos/" + OWNER + "/" + REPO;
const WORKFLOWS = Object.freeze({
  v6: "studio-ibrido-v6.yml",
  v7: "archivio-media-v7.yml",
  v8: "orchestratore-v8.yml",
  render: "render-v3.yml"
});
const FORMAT_VALUES = ["libri", "cronaca", "documentario", "fiabe", "social"];
const $ = (q) => document.querySelector(q);
const $$ = (q) => [...document.querySelectorAll(q)];
const esc = (x) => String(x ?? "").replace(/[&<>"']/g, (c) =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let activeEpisode = "";
let activeFormat = "libri";
let mediaKind = "image";
let auth = { backend: false, authenticated: false, login: "" };
let runs = [];
let episodeSlugs = [];
let toastTimer;

function toast(message) {
  const el = $("#toast"); el.textContent = message; el.classList.add("visible");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove("visible"), 4500);
}
function go(tab) {
  if (!$("#view-" + tab)) return;
  $$(".view").forEach(x => x.classList.toggle("active", x.id === "view-" + tab));
  $$(".nav-item[data-tab]").forEach(x => x.classList.toggle("active", x.dataset.tab === tab));
  const labels = {studio:"PANORAMICA",nuovo:"NUOVO VIDEO",episodi:"EPISODI",videoteca:"VIDEOTECA",archivio:"ARCHIVIO MEDIA",produzioni:"PRODUZIONI",impostazioni:"IMPOSTAZIONI"};
  $("#section-label").textContent = labels[tab]; $("#section-crumb").textContent = "Studio";
  window.location.hash = tab;
  $("#sidebar").classList.remove("open"); $("#overlay").hidden = true;
  window.scrollTo({top:0,behavior:"instant"});
}
function openLink(url) {
  const a = document.createElement("a"); a.href = url; a.target = "_blank"; a.rel = "noopener noreferrer";
  document.body.appendChild(a); a.click(); a.remove();
}
async function getPublic(path) {
  const response = await fetch(API_URL + path, {headers: {"Accept":"application/vnd.github+json"}});
  if (!response.ok) throw new Error(response.status === 403 ? "Limite letture GitHub raggiunto. Riprova più tardi." : "GitHub API: HTTP " + response.status);
  return response.json();
}
function shortDate(value) {
  try { return new Date(value).toLocaleString("it-IT",{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"}); }
  catch { return ""; }
}
function runItem(run) {
  const title = esc(run.display_title || run.name || "Produzione GitHub");
  const id = Number(run.id);
  if (!Number.isSafeInteger(id)) return "";
  const good = run.conclusion === "success", failure = run.status === "completed" && !good;
  const kind = good ? "success" : (failure ? "failure" : "running");
  const icon = good ? "✓" : (failure ? "!" : "◷");
  const label = good ? "Completata" : (failure ? "Da verificare" : "In corso");
  const summary = esc(run.name || "GitHub Actions");
  return '<a class="run-item" href="' + REPO_URL + '/actions/runs/' + id + '" target="_blank" rel="noopener"><span class="run-symbol ' + kind + '">' + icon + '</span><span><strong>' + title + '</strong><small>' + summary + ' · ' + shortDate(run.created_at) + ' · ' + label + '</small></span><span class="run-side">Apri ↗</span></a>';
}
async function refreshRuns() {
  try {
    const data = await getPublic("/actions/runs?branch=main&per_page=14");
    runs = Array.isArray(data.workflow_runs) ? data.workflow_runs : [];
    $("#stat-runs").textContent = String(runs.length);
    $("#all-runs").innerHTML = runs.length ? runs.map(runItem).join("") : '<div class="empty">Non risultano esecuzioni.</div>';
    $("#home-runs").innerHTML = runs.length ? runs.slice(0,4).map(runItem).join("") : '<div class="empty">Non risultano esecuzioni.</div>';
    $("#sync-status").innerHTML = '<span class="live-dot"></span> GitHub aggiornato';
  } catch (error) {
    const msg = '<div class="empty">' + esc(error.message) + ' · <a href="' + REPO_URL + '/actions" target="_blank" rel="noopener">Apri GitHub</a></div>';
    $("#home-runs").innerHTML = msg; $("#all-runs").innerHTML = msg;
    $("#sync-status").textContent = "Connessione da verificare";
  }
}
async function refreshEpisodes() {
  try {
    const data = await getPublic("/contents/episodes?ref=main");
    episodeSlugs = data.filter(x => x.type === "dir" && /^[a-zA-Z0-9_-]{1,75}$/.test(x.name)).map(x=>x.name);
    $("#stat-episodes").textContent = String(episodeSlugs.length);
    await loadGallery();
    $("#episode-grid").innerHTML = episodeSlugs.length ? episodeSlugs.map((name,i) => makeEpisodeCard(name,i)).join("") : '<div class="empty">Nessun episodio disponibile.</div>';
    if (activeEpisode && !episodeSlugs.includes(activeEpisode)) {
      activeEpisode = ""; $("#selected-panel").hidden = true;
    }
  } catch (error) {
    $("#episode-grid").innerHTML = '<div class="empty">' + esc(error.message) + ' · <a target="_blank" rel="noopener" href="' + REPO_URL + '/tree/main/episodes">Apri episodi GitHub</a></div>';
  }
}
function selectEpisode(slug) {
  if (!episodeSlugs.includes(slug)) return;
  activeEpisode = slug;
  $$(".episode-card").forEach(x => x.classList.toggle("selected", x.dataset.episode === slug));
  $("#selected-panel").hidden = false;
  $("#selected-title").textContent = slug.replace(/^\d+_?/,"").replace(/_/g," ");
  $("#selected-slug").textContent = "episodes/" + slug;
  $("#selected-panel").scrollIntoView({block:"nearest",behavior:"smooth"});
}
async function session() {
  try {
    const r = await fetch("/api/session", {credentials:"same-origin",cache:"no-store"});
    if (!r.ok) throw new Error("Backend assente");
    const data = await r.json();
    if (typeof data.authenticated !== "boolean") throw new Error("Backend non riconosciuto");
    auth = {backend:data.ready === true,authenticated:data.ready === true && data.authenticated,login:data.login || ""};
  } catch { auth={backend:false,authenticated:false,login:""}; }
  const status = auth.authenticated ? "GitHub connesso" : (auth.backend ? "Accesso GitHub disponibile" : "Modalità GitHub guidata");
  $("#backend-status").textContent = status;
  $("#account-action").textContent = auth.authenticated ? "✓" : "GH";
  $("#auth-description").textContent = auth.authenticated
    ? "Connesso come " + auth.login + ". Puoi lanciare direttamente i workflow autorizzati."
    : (auth.backend ? "Il backend privato è attivo. Accedi con GitHub per avviare workflow direttamente."
      : "L'interfaccia pubblica è attiva. Per i workflow puoi usare l'apertura guidata di GitHub; per il lancio diretto configura il backend Cloudflare.");
  $("#auth-button").textContent = auth.authenticated ? "Disconnetti GitHub" : (auth.backend ? "Accedi con GitHub" : "Istruzioni per attivare");
  $("#dispatch-hint").textContent = auth.authenticated ? "Autenticato: questi pulsanti avviano workflow reali tramite il backend sicuro."
    : "Modalità guidata: i pulsanti aprono GitHub Actions; poi premi Run workflow con gli stessi valori.";
}
async function authAction() {
  if (!auth.backend) {
    openLink(REPO_URL + "/blob/main/STUDIO_WEB_V9_GUIDA.md");
    toast("Per avviare direttamente dall'app serve attivare Cloudflare e GitHub OAuth.");
    return;
  }
  if (!auth.authenticated) { window.location.assign("/auth/start"); return; }
  await fetch("/api/logout",{method:"POST",credentials:"same-origin"});
  await session();
  toast("Sessione GitHub chiusa.");
}
function confirmChoice(title,description,consent) {
  const dialog=$("#confirm-dialog");
  $("#dialog-title").textContent=title;
  $("#dialog-desc").textContent=description;
  $("#dialog-consent-text").textContent=consent;
  $("#dialog-check").checked=false; $("#dialog-confirm").disabled=true;
  dialog.showModal();
  return new Promise(resolve => {
    dialog.addEventListener("close",()=>resolve(dialog.returnValue==="confirm"),{once:true});
  });
}
async function dispatch(workflow,inputs,confirm=null) {
  if (!WORKFLOWS[workflow]) return;
  if (confirm) {
    if (!await confirmChoice(confirm.title,confirm.body,confirm.consent)) return;
  }
  if (!auth.authenticated) {
    openLink(REPO_URL + "/actions/workflows/" + WORKFLOWS[workflow]);
    toast("Su GitHub scegli Run workflow, inserisci i dati e conferma.");
    return;
  }
  try {
    const response = await fetch("/api/dispatch",{method:"POST",credentials:"same-origin",
      headers:{"Content-Type":"application/json"},body:JSON.stringify({workflow,inputs,
        confirmed:Boolean(confirm)})});
    const data = await response.json().catch(()=>({}));
    if (!response.ok) throw new Error(data.error || "Non è stato possibile avviare il workflow.");
    toast("Richiesta accettata da GitHub. Controlla Produzioni fra qualche istante.");
    go("produzioni");
  } catch(error) {toast(error.message);}
}
function getProjects() {
  try {
    const result = JSON.parse(localStorage.getItem("tlp_v9_projects") || "[]");
    return Array.isArray(result) ? result.slice(0,40) : [];
  } catch { return []; }
}
function projectFromForm() {
  return {id:crypto.randomUUID?.() || String(Date.now()), title:$("#video-title").value.trim().slice(0,110) || "Nuovo progetto",
    idea:$("#video-idea").value.trim().slice(0,6000),format:activeFormat,
    minutes:Number($("#video-length").value),preferReal:$("#real-sources").checked,
    savedAt:new Date().toISOString()};
}
function saveProject() {
  const p=projectFromForm();
  if (!p.idea || p.idea.length<10) {toast("Scrivi almeno una breve descrizione della storia.");return;}
  try {localStorage.setItem("tlp_v9_projects",JSON.stringify([p,...getProjects()].slice(0,40)));
    renderSaved(); toast("Progetto salvato in questo browser.");}
  catch {toast("Il browser non consente di salvare dati locali.");}
}
function renderSaved() {
  const p=getProjects();
  $("#saved-projects").innerHTML=p.length ? p.map(v =>
    '<div class="saved-card"><small>' + esc(v.format).toUpperCase() + ' · ' + shortDate(v.savedAt) +
    '</small><h3>' + esc(v.title) + '</h3><p>' + esc(v.idea.slice(0,150)) +
    '</p><div class="saved-buttons"><button data-project-open="' + esc(v.id) +
    '">Riapri</button><button data-project-delete="' + esc(v.id) + '">Elimina</button></div></div>'
  ).join("") : '<p class="empty">Non hai ancora salvato progetti.</p>';
}
function applyProject(project) {
  $("#video-title").value=project.title;$("#video-idea").value=project.idea;
  $("#video-length").value=String(project.minutes || 3); activeFormat=FORMAT_VALUES.includes(project.format)?project.format:"libri";
  $("#real-sources").checked=project.preferReal!==false;
  $$("#type-options .chip").forEach(x=>x.classList.toggle("selected",x.dataset.value===activeFormat));
  go("nuovo");
}
function buildGptPrompt(p) {
  return [
    "Sto creando un episodio per il mio progetto Tra le Pagine — Studio Ibrido.",
    "Repository: " + REPO_URL,
    "Utilizzo: smartphone Android + GitHub Actions. Preserva V3–V8.",
    "Voce: Google Gemini TTS, non cambiarla. Non presumere di avere accesso all'API di GPT con Plus.",
    "Obiettivo: prepara il materiale editoriale per un video originale.",
    "Titolo: " + p.title,
    "Formato: " + p.format,
    "Durata indicativa: " + p.minutes + " minuti.",
    "Idea dell'episodio: " + p.idea,
    "Prima riutilizza media già approvati, poi cerca materiali consentiti, solo alla fine immagini AI: " + (p.preferReal?"sì":"facoltativo") + ".",
    "Fornisci un copione narrato naturale in italiano, una divisione in scene con descrizioni corrispondenti alle frasi, eventuali fonti per fatti di cronaca, indicazione di materiale visivo necessario e note per l'approvazione Gate 1.",
    "Non inventare fonti. Non dichiarare che il video è pronto: produci prima un copione e uno storyboard da approvare.",
    "Per file di episodio compatibili, considera il formato esistente scene_cues.json, testo.txt, metadata.json nel repository reale."
  ].join("\n\n");
}
async function copyGpt() {
  const p=projectFromForm();
  if (!p.idea || p.idea.length<10) {toast("Inserisci prima l'idea del video.");return;}
  const draft=buildGptPrompt(p);
  try {
    await navigator.clipboard.writeText(draft);
    toast("Brief copiato! Tocca Apri ChatGPT e incollalo nella conversazione.");
  } catch { window.prompt("Copia questo testo e incollalo in ChatGPT:",draft); }
}
function bind() {
  $$(".nav-item[data-tab], [data-go]").forEach(x=>x.addEventListener("click",()=>go(x.dataset.tab||x.dataset.go)));
  $("#menu-open").addEventListener("click",()=>{$("#sidebar").classList.add("open");$("#overlay").hidden=false;});
  $("#overlay").addEventListener("click",()=>{$("#sidebar").classList.remove("open");$("#overlay").hidden=true;});
  $("#refresh-all").addEventListener("click",()=>Promise.all([refreshRuns(),refreshEpisodes(),initVideoLibrary()]));
  $("#refresh-runs").addEventListener("click",refreshRuns);
  window.addEventListener("studio-videos-updated",()=>{const count=getPublishedVideos().length;const el=$("#videos-count");if(el)el.textContent=String(count);if(episodeSlugs.length)refreshEpisodes().catch(()=>{});});
  $("#refresh-episodes").addEventListener("click",refreshEpisodes);
  $("#episode-grid").addEventListener("click",e=>{
    const watch=e.target.closest("[data-watch-episode]");
    if(watch){watchVideo(videoForEpisode(watch.dataset.watchEpisode));return;}
    const preview=e.target.closest("[data-preview]");
    if(preview){showEpisodePreview(preview.dataset.preview,{onSelect:selectEpisode});return;}
    const item=e.target.closest("[data-episode]");
    if(item) selectEpisode(item.dataset.episode);
  });
  $("#type-options").addEventListener("click",e=>{
    const b=e.target.closest("[data-value]");if(!b)return;
    activeFormat=b.dataset.value; $$("#type-options .chip").forEach(x=>x.classList.toggle("selected",x===b));
  });
  $("#kind-options").addEventListener("click",e=>{
    const b=e.target.closest("[data-value]");if(!b)return;
    mediaKind=b.dataset.value;$$("#kind-options .chip").forEach(x=>x.classList.toggle("selected",x===b));
  });
  $("#save-brief").addEventListener("click",saveProject);
  $("#copy-gpt").addEventListener("click",copyGpt);
  $("#saved-projects").addEventListener("click",e=>{
    const op=e.target.closest("[data-project-open]");const del=e.target.closest("[data-project-delete]");
    if(op){const p=getProjects().find(v=>v.id===op.dataset.projectOpen);if(p)applyProject(p);}
    if(del){localStorage.setItem("tlp_v9_projects",JSON.stringify(getProjects().filter(x=>x.id!==del.dataset.projectDelete)));renderSaved();}
  });
  $("#clear-local").addEventListener("click",()=>{
    if(window.confirm("Eliminare tutti i brief salvati nel browser?")){localStorage.removeItem("tlp_v9_projects");renderSaved();toast("Brief locali eliminati.");}
  });
  $("#account-action").addEventListener("click",()=>{go("impostazioni");});
  $("#auth-button").addEventListener("click",authAction);
  $("#dialog-check").addEventListener("change",e=>{$("#dialog-confirm").disabled=!e.target.checked;});
  $("#action-v6").addEventListener("click",()=>dispatch("v6",{episodio:activeEpisode,formato:"libri",budget:"zero"}));
  $("#action-v8-plan").addEventListener("click",()=>dispatch("v8",{episode:activeEpisode,format:"libri",mode:"plan",gate1_approved:false}));
  $("#action-v8-prepare").addEventListener("click",()=>dispatch("v8",{episode:activeEpisode,format:"libri",mode:"prepare",gate1_approved:true},{
    title:"Approvi il Gate 1?",body:"Hai controllato copione, storyboard, immagini e fonti per questo episodio? Se mancano asset, il workflow si fermerà prima del montaggio.",
    consent:"Confermo di aver controllato il progetto e approvo la preparazione."}));
  $("#action-render").addEventListener("click",()=>dispatch("render",{episodio:activeEpisode,effetti:"v4"},{
    title:"Avviare il montaggio MP4?",body:"Questa operazione può consumare minuti GitHub e una quota di sintesi Google Gemini. Usa soltanto episodi già approvati e con tutte le immagini premium.",
    consent:"Confermo il montaggio e l'eventuale consumo delle quote Google/GitHub."}));
  $("#media-import").addEventListener("click",()=>{
    const id=$("#import-id").value.trim(),provider=$("#import-provider").value;
    if(provider==="openverse" && !/^[0-9a-fA-F-]{36}$/.test(id)){
      toast("Openverse richiede un ID UUID di 36 caratteri.");return;
    }
    if(provider==="pexels" && !/^\d{1,14}$/.test(id)){
      toast("Pexels richiede un ID numerico.");return;
    }
    if(provider==="openverse" && mediaKind==="video"){
      toast("I video possono essere importati soltanto da Pexels.");return;
    }
    dispatch("v7",{mode:"import",provider,kind:mediaKind,
      query:"materiale scelto",asset_id:id});
  });
  $("#media-search").addEventListener("click",()=>{
    const query=$("#media-query").value.trim();const provider=$("#media-provider").value;
    if(query.length<2||query.length>180){toast("La ricerca deve avere tra 2 e 180 caratteri.");return;}
    if(provider==="openverse"&&mediaKind==="video"){toast("Per cercare video devi scegliere Pexels.");return;}
    dispatch("v7",{mode:"discover",provider,kind:mediaKind,query,asset_id:""});
  });
}
async function init() {
  bind();
  initEpisodePreview();
  const tab=window.location.hash.substring(1);
  go(["studio","nuovo","videoteca","episodi","archivio","produzioni","impostazioni"].includes(tab)?tab:"studio");
  window.addEventListener("hashchange",()=>{const v=window.location.hash.slice(1);if($("#view-"+v))go(v);});
  renderSaved();
  await Promise.allSettled([session(),refreshRuns(),refreshEpisodes(),initVideoLibrary()]);
  if("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(()=>{});
}
init();
