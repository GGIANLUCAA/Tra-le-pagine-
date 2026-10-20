const CACHE="tra-le-pagine-v9-20261020";
const STATIC=["./","./index.html","./styles.css","./app.js","./icon.svg","./manifest.webmanifest"];
self.addEventListener("install",event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(STATIC)).catch(()=>{})));
self.addEventListener("activate",event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
self.addEventListener("fetch",event=>{
  const u=new URL(event.request.url);
  if(event.request.method!=="GET"||u.origin!==self.location.origin||u.pathname.startsWith("/api/")||u.pathname.startsWith("/auth/"))return;
  event.respondWith(fetch(event.request).then(response=>{
    if(response.ok){const copy=response.clone();caches.open(CACHE).then(c=>c.put(event.request,copy)).catch(()=>{});}return response;
  }).catch(()=>caches.match(event.request)));
});
