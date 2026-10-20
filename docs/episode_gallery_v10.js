import {videoForEpisode} from "./videoteca_v11.js";
/**
 * Episode Gallery V10: real (never invented) image storyboard, private local MP4 playback,
 * and official Actions links for archived videos. No token, no AI API, no video upload.
 */
const REPO = "GGIANLUCAA/Tra-le-pagine-";
const API = "https://api.github.com/repos/" + REPO;
const PAGES_ROOT = new URL("./", import.meta.url);
const SAFE_SLUG = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,70}$/;
const esc = v => String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeFrames = value => Array.isArray(value) ? value.filter(x=>typeof x?.src==="string" && /^previews\/[a-z0-9_-]+\/[a-zA-Z0-9_-]+\.jpg$/.test(x.src)) : [];
const $ = selector => document.querySelector(selector);
let gallery = {};
let state = {slug:"", title:"", frames:[], position:0, timer:0, videoURL:null, storyboard:[]};

export async function loadGallery(){
  try{
    const r=await fetch(new URL("previews/catalog.json",PAGES_ROOT),{cache:"no-cache"});
    if(!r.ok)throw Error(String(r.status));
    const obj=await r.json();
    gallery=obj?.episodes && typeof obj.episodes==="object" ? obj.episodes : {};
  }catch {gallery={};}
  return gallery;
}
export function makeEpisodeCard(slug,index){
  if(!SAFE_SLUG.test(slug))return "";
  const v=gallery[slug]||{};
  const title=esc(v.title||slug.replace(/^\d+_?/,"").replace(/_/g," "));
  const author=esc(v.author||"");
  const hasPicture=v.visual_status==="real_episode_images" && safeFrames(v.frames).length>0;
  const published=videoForEpisode(slug);
  const image=hasPicture ? '<img loading="lazy" alt="Copertina reale dell’episodio" src="'+esc(new URL(v.poster,PAGES_ROOT).href)+'">' : '';
  const visual=published ? "▶ VIDEO MP4 PRONTO" :
    (hasPicture ? "Immagini reali disponibili" : "Nessuna scena illustrata");
  return '<div class="episode-entry"><button class="episode-card ep-v10" data-episode="'+esc(slug)+'">' +
      '<span class="episode-cover v10-cover '+(hasPicture?"has-picture":"no-picture")+'">'+image+
      '<span class="episode-number">'+String(index+1).padStart(2,"0")+'</span></span>'+
      '<span class="episode-title">'+title+'</span><small>'+author+'</small>'+
      '<span class="episode-availability '+((hasPicture||published)?"available":"unavailable")+'">'+
      (published?"▶ ":(hasPicture?"◉ ":"○ "))+visual+'</span></button>'+
    (published?'<button class="episode-preview-btn" data-watch-episode="'+esc(slug)+'">▶ Guarda il video</button>':
      '<button class="episode-preview-btn" data-preview="'+esc(slug)+'">▶ Apri anteprima</button>')+'</div>';
}
function stop(){
  clearInterval(state.timer);state.timer=0;
  if(state.videoURL){URL.revokeObjectURL(state.videoURL);state.videoURL=null;}
  const video=$("#episode-video");
  if(video){video.pause();video.removeAttribute("src");video.load();}
}
function showFrame(){
  const box=$("#preview-frame");
  if(!box)return;
  const frame=state.frames[state.position];
  const empty=$("#preview-no-scenes");
  const controls=$("#preview-slide-controls");
  if(frame){
    box.hidden=false;empty.hidden=true;controls.hidden=state.frames.length<=1;
    box.src=new URL(frame.src,PAGES_ROOT).href;
    box.alt="Immagine "+(state.position+1)+" dell’episodio "+state.title;
    $("#preview-slide-count").textContent=(state.position+1)+" / "+state.frames.length;
  }else{
    box.hidden=true;empty.hidden=false;controls.hidden=true;
  }
}
async function loadCues(slug){
  if(!SAFE_SLUG.test(slug))return [];
  try{
    const r=await fetch(API+"/contents/episodes/"+encodeURIComponent(slug)+"/scene_cues.json?ref=main");
    if(!r.ok)return [];
    const file=await r.json();
    if(typeof file.content!=="string"||file.encoding!=="base64")return [];
    const ascii=atob(file.content.replace(/\s/g,""));
    const bytes=Uint8Array.from(ascii,c=>c.charCodeAt(0));
    const cues=JSON.parse(new TextDecoder().decode(bytes));
    return Array.isArray(cues)?cues.filter(x=>typeof x?.description==="string").slice(0,40):[];
  }catch{return [];}
}
function cuesRender(cues){
  const box=$("#preview-scenes-list");
  box.innerHTML=cues.length ? cues.map((x,i)=>'<div class="scene-line"><span>'+String(i+1).padStart(2,"0")+
    '</span><p>'+esc(x.description)+'</p></div>').join("")
    : '<p class="micro-note">Storyboard non ancora disponibile per questo episodio.</p>';
}
export async function showEpisodePreview(slug, {onSelect}={}){
  if(!SAFE_SLUG.test(slug))return;
  stop();
  const v=gallery[slug]||{};
  state={slug,title:v.title||slug.replace(/_/g," "),frames:safeFrames(v.frames),position:0,timer:0,videoURL:null,storyboard:[]};
  $("#preview-heading").textContent=state.title;
  $("#preview-author").textContent=v.author||"";
  $("#preview-status").textContent=state.frames.length ? "Anteprima delle immagini reali disponibili, non un video MP4" :
    "Non ci sono ancora immagini o video pubblicati per questo episodio";
  $("#preview-video-container").hidden=true;
  $("#preview-frame-container").hidden=false;
  $("#preview-scenes-list").textContent="Caricamento scene…";
  $("#preview-github").href="https://github.com/"+REPO+"/actions";
  $("#preview-github").textContent="Vedi video e download in GitHub Actions ↗";
  $("#preview-select").onclick=()=>{onSelect?.(slug);$("#episode-preview").close();};
  showFrame();
  const dlg=$("#episode-preview");
  if(!dlg.open)dlg.showModal();
  // If an episode has scenes, slideshow previews come from original images; not synthesized video.
  if(state.frames.length>1)state.timer=setInterval(()=>{
    if(!dlg.open || !$("#preview-video-container").hidden)return;
    state.position=(state.position+1)%state.frames.length;showFrame();
  },3600);
  state.storyboard=await loadCues(slug);
  // Guard against rapid switching between episodes.
  if(state.slug===slug && dlg.open)cuesRender(state.storyboard);
}
export function initEpisodePreview(){
  const dlg=$("#episode-preview");
  if(!dlg)return;
  dlg.addEventListener("close",stop);
  $("#preview-close").addEventListener("click",()=>dlg.close());
  $("#preview-prev").addEventListener("click",()=>{if(!state.frames.length)return;state.position=(state.position+state.frames.length-1)%state.frames.length;showFrame();});
  $("#preview-next").addEventListener("click",()=>{if(!state.frames.length)return;state.position=(state.position+1)%state.frames.length;showFrame();});
  $("#preview-file").addEventListener("change", e=>{
    const file=e.target.files?.[0];
    if(!file)return;
    if(file.size>500*1024*1024){window.alert("Video troppo grande per un'anteprima locale (> 500 MB).");e.target.value="";return;}
    if(!(file.type.startsWith("video/")|| /\.(mp4|webm|mov)$/i.test(file.name))){window.alert("Scegli un file video MP4/WebM/MOV.");e.target.value="";return;}
    stop();
    state.videoURL=URL.createObjectURL(file);
    $("#preview-frame-container").hidden=true;$("#preview-video-container").hidden=false;
    $("#episode-video").src=state.videoURL;
    $("#preview-status").textContent="Video locale dal tuo telefono — NON caricato online";
    $("#episode-video").play().catch(()=>{});
    e.target.value="";
  });
}
