/**
 * Tra le Pagine V11 — Video library.
 * Reads only explicitly published GitHub Releases with prefix "tlp-video-".
 * No passwords, tokens, upload, download scraping or auto-publication.
 */
const OWNER="GGIANLUCAA", REPO="Tra-le-pagine-";
const API="https://api.github.com/repos/"+OWNER+"/"+REPO+"/releases?per_page=100";
const RELEASE_PREFIX=/^tlp-video-([a-zA-Z0-9][a-zA-Z0-9_-]{0,70})-(\d{6,20})$/;
const EPISODE=/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,70}$/;
const BASE="https://github.com/"+OWNER+"/"+REPO+"/releases/download/";
const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let listed=[], loaded=false, hasError="";
const at = s=>{try{return new Date(s).toLocaleDateString("it-IT",{day:"numeric",month:"short",year:"numeric"})}catch{return ""}};

export function normalizeRelease(release){
  if(!release||release.draft||release.prerelease)return null;
  const match=RELEASE_PREFIX.exec(String(release.tag_name||""));
  if(!match)return null;
  const [_,episode,run]=match;
  if(!EPISODE.test(episode))return null;
  const asset=(release.assets||[]).find(a=>
    a?.name==="TRA_LE_PAGINE_VIDEO.mp4" &&
    Number(a.size)>100000 && Number(a.size)<=120000000 &&
    a.state==="uploaded" &&
    typeof a.browser_download_url==="string" &&
    a.browser_download_url.startsWith(BASE+release.tag_name+"/")
  );
  if(!asset)return null;
  const thumb=(release.assets||[]).find(a=>
    a?.name==="VIDEO_COPERTINA.jpg" &&
    Number(a.size)>10000 && Number(a.size)<=12000000 &&
    a.state==="uploaded" &&
    typeof a.browser_download_url==="string" &&
    a.browser_download_url.startsWith(BASE+release.tag_name+"/")
  );
  return {
    slug:episode,run,tag:release.tag_name,
    title:String(release.name||episode).replace(/^Tra le Pagine · /,"").slice(0,130),
    cover:thumb?.browser_download_url||"",
    url:asset.browser_download_url, bytes:asset.size,
    date:release.published_at||release.created_at,
    download_count:asset.download_count||0,
    public:true,
    source_run:"https://github.com/"+OWNER+"/"+REPO+"/actions/runs/"+run
  };
}
export async function refreshVideoLibrary(){
  hasError="";
  try{
    const r=await fetch(API,{cache:"no-store",headers:{Accept:"application/vnd.github+json"}});
    if(!r.ok)throw Error("HTTP "+r.status);
    const releases=await r.json();
    if(!Array.isArray(releases))throw Error("Invalid releases JSON");
    listed=releases.map(normalizeRelease).filter(Boolean);
    listed.sort((a,b)=>new Date(b.date)-new Date(a.date));
    loaded=true;
  }catch(e){
    hasError=e.message;listed=[];loaded=false;
  }
  return listed.slice();
}
export const getPublishedVideos=()=>listed.slice();
export const videoForEpisode=slug=>listed.find(x=>x.slug===slug)||null;
function formatSize(bytes){return (bytes/1048576).toFixed(1)+" MB";}
function tile(video){
  const slug=esc(video.slug);
  const cover=video.cover?'<img loading="lazy" alt="Fotogramma reale del video" src="'+esc(video.cover)+'">':"";
  return '<article class="video-tile"><div class="video-tile-art">'+cover+'<span>▶</span></div>'+
    '<div class="video-tile-info"><span class="video-tile-label">VIDEO COMPLETO · '+esc(at(video.date))+'</span>'+
    '<h3>'+esc(video.title)+'</h3><p>'+formatSize(video.bytes)+' · Archivio permanente GitHub Release</p>'+
    '<div class="video-tile-actions"><button data-watch="'+slug+'" class="btn primary">▶ Guarda</button>'+
    '<a class="btn outline" target="_blank" rel="noopener" download href="'+esc(video.url)+'">↓ Scarica MP4</a></div></div></article>';
}
function render(){
  const grid=document.querySelector("#videos-grid");
  if(!grid)return;
  const count=document.querySelector("#videos-count");
  if(count)count.textContent=String(listed.length);
  if(!loaded){
    grid.innerHTML='<div class="empty">Impossibile leggere la videoteca al momento.'+
      ' <a href="https://github.com/'+OWNER+'/'+REPO+'/releases" target="_blank" rel="noopener">Apri le Release GitHub</a></div>';
    return;
  }
  if(!listed.length){
    grid.innerHTML='<div class="empty video-empty"><span>◷</span><strong>Nessun MP4 pubblicato nella videoteca.</strong>'+
      '<p>I video possono già esistere negli Artifact GitHub: rimangono privati o non pubblicati finché non approvi '+
      'esplicitamente il loro inserimento nel sito, che è pubblico.</p>'+
      '<a href="https://github.com/'+OWNER+'/'+REPO+'/actions/workflows/pubblica-video-v11.yml" target="_blank" rel="noopener" class="btn outline">Aggiungi un video dalla produzione ↗</a></div>';
    return;
  }
  grid.innerHTML=listed.map(tile).join("");
}
export function watchVideo(v){
  const dialog=document.querySelector("#public-video-dialog");
  if(!dialog||!v)return;
  const title=dialog.querySelector("#public-video-title");
  const player=dialog.querySelector("#public-video-player");
  const download=dialog.querySelector("#public-video-download");
  const backup=dialog.querySelector("#public-video-backup");
  const warning=dialog.querySelector("#public-video-warning");
  title.textContent=v.title;
  player.src=v.url;
  player.load();
  warning.textContent="Questo video è pubblicamente accessibile tramite GitHub Releases.";
  download.href=v.url;
  backup.href=v.url;
  dialog.showModal();
  player.play().catch(()=>{});
}
export function initVideoLibrary(){
  const dialog=document.querySelector("#public-video-dialog");
  if(dialog){
    dialog.querySelector("#public-video-close").addEventListener("click",()=>dialog.close());
    dialog.addEventListener("close",()=>{
      const player=dialog.querySelector("#public-video-player");
      player.pause();player.removeAttribute("src");player.load();
    });
    dialog.querySelector("#public-video-player").addEventListener("error",()=>{
      dialog.querySelector("#public-video-warning").textContent=
      "Il server non ha consentito lo streaming diretto: usa Scarica MP4 per guardarlo sul telefono.";
    });
  }
  const grid=document.querySelector("#videos-grid");
  grid?.addEventListener("click",e=>{
    const b=e.target.closest("[data-watch]");
    if(b)watchVideo(listed.find(x=>x.slug===b.dataset.watch));
  });
  document.querySelector("#refresh-videos")?.addEventListener("click",async()=>{
    await refreshVideoLibrary();render();window.dispatchEvent(new Event("studio-videos-updated"));
  });
  return refreshVideoLibrary().then(()=>{render();window.dispatchEvent(new Event("studio-videos-updated"));});
}
