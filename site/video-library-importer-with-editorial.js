const AUD='vls-gh-import-2026', REPO='GGIANLUCAA/Tra-le-pagine-', WF=REPO+'/.github/workflows/video-library-r2-import.yml@refs/heads/main';
const PRIVATE_WF=REPO+'/.github/workflows/video-library-private-owner-archive.yml@refs/heads/main';
let jwksCache=null,jwksTime=0;
function from64(s){const z=s.replace(/-/g,'+').replace(/_/g,'/');return Uint8Array.from(atob(z+'='.repeat((4-z.length%4)%4)),x=>x.charCodeAt(0));}
async function authorized(req){
 const hdr=req.headers.get('Authorization')||'';if(!hdr.startsWith('Bearer '))return false;
 const seg=hdr.slice(7).split('.');if(seg.length!==3)return false;
 let head,claims;try{head=JSON.parse(new TextDecoder().decode(from64(seg[0])));claims=JSON.parse(new TextDecoder().decode(from64(seg[1])));}catch{return false;}
 const now=Math.floor(Date.now()/1000);
 if(head.alg!=='RS256'||!head.kid||claims.iss!=='https://token.actions.githubusercontent.com'||claims.aud!==AUD||claims.repository!==REPO||claims.ref!=='refs/heads/main'||!(new URL(req.url).pathname.startsWith('/private-')?[PRIVATE_WF]:[WF,REPO+'/.github/workflows/video-library-enrich.yml@refs/heads/main']).includes(claims.workflow_ref)||!Number.isFinite(claims.exp)||claims.exp<=now||!Number.isFinite(claims.iat)||claims.iat>now+60)return false;
 if(!jwksCache||Date.now()-jwksTime>600000){const res=await fetch('https://token.actions.githubusercontent.com/.well-known/jwks');if(!res.ok)throw Error('GitHub JWKS unavailable');jwksCache=await res.json();jwksTime=Date.now();}
 const jwk=jwksCache.keys.find(x=>x.kid===head.kid&&x.kty==='RSA'&&(!x.alg||x.alg==='RS256'));if(!jwk)return false;
 const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);
 return await crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,from64(seg[2]),new TextEncoder().encode(seg[0]+'.'+seg[1]));
}

function resp(j,status=200){return Response.json(j,{status,headers:{'Cache-Control':'no-store'}});}
export default{async fetch(request,env){
 const u=new URL(request.url),method=request.method,route=u.pathname;
 if(route==='/health'&&method==='GET')return resp({service:'video-library-import',ready:true});
 try{if(!await authorized(request))return resp({error:'Not authorized'},401);}catch(e){return resp({error:'Authentication temporarily unavailable'},503);}
 // PRIVATE owner archive, isolated from the public VIDEOS bucket and catalogue.
 // Route authorization is restricted to the dedicated main-branch GitHub workflow.
 // There is deliberately no GET of video bytes or public URL for these objects.
 if(route==='/private-ready'&&method==='GET')
  return resp({ready:!!env.PRIVATE_ARCHIVE,private:true,publicCatalogUntouched:true},env.PRIVATE_ARCHIVE?200:503);
 if(route==='/private-status'||route==='/private-single'||route==='/private-stream'||route==='/private-artifact-list'){
  if(!env.PRIVATE_ARCHIVE)return resp({error:'Private archive binding not configured'},503);
  const artifact=u.searchParams.get('artifact')||'',key=u.searchParams.get('key')||'';
  if(!/^[0-9]{4,20}$/.test(artifact)||!/^[A-Za-z0-9_(). -]{1,180}\.(mp4|m4v|mov)$/i.test(key)||key.includes('..')||
     /(^|[_ .-])(SOURCE|SCOUT|CONTACT|FRAMES|ASSETS|PROBE|RAW|NOT_FINAL|NON_FINALE)([_ .-]|$)/i.test(key)||
     /^AUDIO_POLISHED_REVIEW/i.test(key))return resp({error:'Invalid finished-video identity'},400);
  const target='gh-artifacts/'+artifact+'/'+key;
  if(route==='/private-artifact-list'&&method==='GET'){
   const listed=await env.PRIVATE_ARCHIVE.list({prefix:'gh-artifacts/'+artifact+'/',limit:1000});
   return resp({private:true,items:listed.objects.map(x=>({
    key:x.key.slice(('gh-artifacts/'+artifact+'/').length),
    size:x.size,sha256:x.customMetadata?.sha256||null
   })),truncated:!!listed.truncated,cursor:listed.truncated?listed.cursor:null});
  }
  if(route==='/private-status'&&method==='GET'){
   const obj=await env.PRIVATE_ARCHIVE.head(target);
   return resp(obj?{exists:true,private:true,size:obj.size,sha256:obj.customMetadata?.sha256||null}:{exists:false,private:true});
  }
  if(route==='/private-single'&&method==='POST'){
   const expected=u.searchParams.get('sha256')||'';
   if(!/^[a-f0-9]{64}$/i.test(expected))return resp({error:'Missing verified video SHA256'},400);
   const max=30*1024*1024;
   const declared=Number(request.headers.get('content-length')||0);
   if(declared>max)return resp({error:'Video exceeds private single upload limit'},413);
   const bytes=await request.arrayBuffer();
   if(bytes.byteLength<1024||bytes.byteLength>max)return resp({error:'Invalid complete video size'},413);
   const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
   if(hash!==expected.toLowerCase())return resp({error:'Private archive SHA256 mismatch'},400);
   const existing=await env.PRIVATE_ARCHIVE.head(target);
   if(existing){
    if(existing.size===bytes.byteLength&&existing.customMetadata?.sha256===hash)
     return resp({ok:true,private:true,already_exists:true,key:target,size:existing.size,sha256:hash});
    return resp({error:'Private object collision (no overwrite)'},409);
   }
   const contentType=/\.(mp4|m4v)$/i.test(key)?'video/mp4':'video/quicktime';
   const put=await env.PRIVATE_ARCHIVE.put(target,bytes,{
    httpMetadata:{contentType},
    customMetadata:{sha256:hash,artifact,visibility:'private_owner_review'},
    onlyIf:{etagDoesNotMatch:'*'}
   });
   if(!put)return resp({error:'Concurrent private archive write rejected'},409);
   const verified=await env.PRIVATE_ARCHIVE.head(target);
   if(!verified||verified.size!==bytes.byteLength||verified.customMetadata?.sha256!==hash)
    return resp({error:'Private archive readback metadata mismatch'},500);
   return resp({ok:true,stored:true,private:true,key:target,size:verified.size,sha256:hash});
  }
  if(route==='/private-stream'&&method==='POST'){
   // R2.put streams the authenticated request directly without buffering an entire video.
   // The GitHub Actions producer MUST independently hash the complete source MP4;
   // this route verifies declared Content-Length, stored size and source SHA metadata.
   const expected=u.searchParams.get('sha256')||'';
   const expectedSize=Number(u.searchParams.get('bytes')||0);
   const declared=Number(request.headers.get('content-length')||0);
   if(!/^[a-f0-9]{64}$/i.test(expected)||!Number.isSafeInteger(expectedSize)||
      expectedSize<1024||expectedSize>512*1024*1024||declared!==expectedSize||!request.body)
    return resp({error:'Missing or conflicting source SHA256/content-length/size'},400);
   const existing=await env.PRIVATE_ARCHIVE.head(target);
   if(existing){
    if(existing.size===expectedSize&&existing.customMetadata?.sha256===expected.toLowerCase())
     return resp({ok:true,private:true,already_exists:true,key:target,size:existing.size,sha256:expected.toLowerCase(),
                  sha256Proof:'github_source_checked'});
    return resp({error:'Private object collision (no overwrite)'},409);
   }
   const contentType=/\.(mp4|m4v)$/i.test(key)?'video/mp4':'video/quicktime';
   const uploaded=await env.PRIVATE_ARCHIVE.put(target,request.body,{
    httpMetadata:{contentType},
    customMetadata:{sha256:expected.toLowerCase(),artifact,visibility:'private_owner_review',
                    sha256Proof:'github_source_checked'},
    onlyIf:{etagDoesNotMatch:'*'}
   });
   if(!uploaded)return resp({error:'Concurrent private archive write rejected'},409);
   const verified=await env.PRIVATE_ARCHIVE.head(target);
   if(!verified||verified.size!==expectedSize||verified.customMetadata?.sha256!==expected.toLowerCase())
    return resp({error:'Private R2 streaming size/source-digest metadata mismatch'},500);
   return resp({ok:true,private:true,stored:true,key:target,size:verified.size,
                sha256:expected.toLowerCase(),sha256Proof:'github_source_checked'});
  }
  return resp({error:'Private archive method not allowed'},405);
 }
 if(route==='/editorial-seed'&&method==='POST'){
  let input;try{const text=await request.text();if(text.length>170000)return resp({error:'Manifest too large'},413);input=JSON.parse(text)}catch{return resp({error:'Invalid JSON'},400)}
  if(!Array.isArray(input?.items)||input.items.length>800)return resp({error:'Expected up to 800 video entries'},400);
  const valid=/^[\w ().-]{1,190}\.(mp4|m4v|mov)$/i;
  const candidates=[...new Set(input.items.filter(x=>typeof x==='string'&&valid.test(x)))];
  const listed=await env.VIDEOS.list({prefix:'catalog/editorial/',limit:1000});
  const existing=new Set(listed.objects.map(x=>x.key));
  const pending=candidates.filter(k=>!existing.has('catalog/editorial/'+k+'.json'));
  const batch=pending.slice(0,18);let created=0,unavailable=0;
  for(const key of batch){
   if(!await env.VIDEOS.head(key)){unavailable++;continue}
   const rec={schemaVersion:1,key,createdAt:new Date().toISOString(),authoring:'autogenerated',rule:'VLS-EDITORIAL-1.0',seededBy:'github-enrichment'};
   await env.VIDEOS.put('catalog/editorial/'+key+'.json',JSON.stringify(rec),{httpMetadata:{contentType:'application/json'}});
   created++;
  }
  return resp({ok:true,created,pending:Math.max(0,pending.length-batch.length),unavailable,total:candidates.length,existing:existing.size});
 }
 // Archive import and public release are distinct: previews must be archived privately.
 if(route==='/ingest-stage'&&method==='POST'){
  const key=u.searchParams.get('key')||'';
  if(!/^[\\w(). -]{1,180}\\.(mp4|mov|m4v)$/i.test(key)||key.includes('..'))return resp({error:'Invalid video name'},400);
  for(let attempt=0;attempt<5;attempt++){
   const o=await env.VIDEOS.get('catalog/manage.json');
   let entries={};try{if(o)entries=await o.json()}catch{return resp({error:'Unable to read current private catalog'},503)}
   if(entries[key])return resp({ok:true,staged:!!entries[key].hidden,existing:true});
   entries[key]={hidden:true,version:'draft',note:'Importato automaticamente in Studio: revisione artistica e diritti in attesa.'};
   const written=await env.VIDEOS.put('catalog/manage.json',JSON.stringify(entries),{httpMetadata:{contentType:'application/json'},onlyIf:o?{etagMatches:o.etag}:{etagDoesNotMatch:'*'}});
   if(written)return resp({ok:true,staged:true,created:true});
  }
  return resp({error:'Concurrent catalog update; retry later'},409);
 }
 const aid=u.searchParams.get('artifact')||'';
 if(route==='/artifact-status'&&method==='GET'){
  if(!/^[0-9]{4,20}$/.test(aid))return resp({error:'Bad ID'},400);
  const o=await env.VIDEOS.get('sync/gh/'+aid+'.json');
  if(!o)return resp({synced:false});
  let m={};try{m=await o.json()}catch{}
  return resp({synced:m.state==='complete',legacy:!m.state,state:m.state||'legacy'});
 }
 if(route==='/artifact-mark'&&method==='POST'){
  if(!/^[0-9]{4,20}$/.test(aid))return resp({error:'Bad ID'},400);
  const d=await request.json();
  const state=['complete','no-video'].includes(d.state)?d.state:'complete';
  await env.VIDEOS.put('sync/gh/'+aid+'.json',JSON.stringify({id:aid,name:String(d.name||'').slice(0,160),state,visibility:String(d.visibility||'').slice(0,30),when:new Date().toISOString()}),{httpMetadata:{contentType:'application/json'}});
  return resp({synced:state==='complete',state});
 }
 if(route==='/manifest'&&method==='POST'){
   const t=await request.text();if(t.length>900000)return resp({error:'Manifest too large'},413);
   let data;try{data=JSON.parse(t)}catch{return resp({error:'Invalid JSON'},400)}
   if(!data||typeof data!=='object'||Array.isArray(data))return resp({error:'Expected object'},400);
   await env.VIDEOS.put('catalog/info.json',t,{httpMetadata:{contentType:'application/json'}});
   return resp({success:true,count:Object.keys(data).length});
 }
 if(route==='/publish-html'&&method==='POST'){
   const t=await request.text();if(t.length>220000||!/^<!doctype html>/i.test(t.trim()))return resp({error:'Invalid HTML'},400);
   await env.VIDEOS.put('site/index.html',t,{httpMetadata:{contentType:'text/html; charset=utf-8'}});
   return resp({success:true,bytes:t.length});
 }
// V55: transfer genuine post texts and reproducible notes with the exact MP4.
// Authenticated GitHub Actions only; NEVER overwrite existing owner-curated material.
 if((route==='/production-file'&&(method==='POST'||method==='GET'))||(route==='/production-file-status'&&method==='GET')){
  const video=u.searchParams.get('video')||'',name=u.searchParams.get('name')||'';
  if(!/^[\w ().-]{1,190}\.(?:mp4|m4v|mov)$/i.test(video)||video.includes('..')||
     !/^[A-Za-z0-9_(). -]{1,110}\.(?:txt|md|json)$/i.test(name)||name.includes('..'))
   return resp({error:'Invalid video or attachment filename'},400);
  if(!await env.VIDEOS.head(video))return resp({error:'MP4 not in archive'},409);
  const storage='production/files/'+encodeURIComponent(video)+'/'+encodeURIComponent(name);
  if(method==='GET'){
   const existing=await env.VIDEOS.head(storage);
   return resp(existing?{exists:true,size:existing.size,video,name}:{exists:false,video,name});
  }
  const n=Number(request.headers.get('content-length')||0);
  if(n>250000)return resp({error:'Attachment too large'},413);
  const bytes=await request.arrayBuffer();
  if(bytes.byteLength===0||bytes.byteLength>250000)return resp({error:'Attachment empty or too large'},413);
  const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  const expected=u.searchParams.get('sha256')||'';
  if(!/^[0-9a-f]{64}$/i.test(expected)||expected.toLowerCase()!==digest)
   return resp({error:'Attachment hash mismatch'},400);
  const old=await env.VIDEOS.get(storage);
  if(old){
   const current=await old.arrayBuffer();
   const oldHash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',current)),x=>x.toString(16).padStart(2,'0')).join('');
   if(oldHash!==digest)return resp({error:'Curated attachment already exists with different content',conflict:true},409);
   return resp({ok:true,already_exists:true,video,name,size:current.byteLength,sha256:oldHash});
  }
  const typ=/\.json$/i.test(name)?'application/json':/\.md$/i.test(name)?'text/markdown':'text/plain';
  await env.VIDEOS.put(storage,bytes,{httpMetadata:{contentType:typ+'; charset=utf-8'}});
  const stored=await env.VIDEOS.head(storage);
  if(!stored||stored.size!==bytes.byteLength)return resp({error:'Attachment storage verification failed'},500);
  return resp({ok:true,stored:true,video,name,size:stored.size,sha256:digest});
 }
const key=u.searchParams.get('key')||'';
 if(!/^[\w(). -]{1,180}\.(?:mp4|m4v|mov|jpe?g|png|webp)$/i.test(key)||key.includes('..'))return resp({error:'Invalid filename'},400);
 try{
 if(route==='/status'&&method==='GET'){const tombstone=await env.VIDEOS.get('catalog/deleted.json');if(tombstone){let d={};try{d=await tombstone.json()}catch{};if(d[key])return resp({key,deleted:true,exists:false});}const obj=await env.VIDEOS.head(key);return resp(obj?{exists:true,size:obj.size,key}:{exists:false,key});}
 if(route==='/single'&&method==='POST'){if(!request.body)return resp({error:'Empty body'},400);const typ=/\.(?:mp4|m4v|mov)$/i.test(key)?'video/mp4':/\.png$/i.test(key)?'image/png':/\.webp$/i.test(key)?'image/webp':'image/jpeg';const obj=await env.VIDEOS.put(key,request.body,{httpMetadata:{contentType:typ}});return resp({key:obj.key,size:obj.size,etag:obj.etag});}
 if(route==='/init'&&method==='POST'){const typ=/\.(?:mp4|m4v|mov)$/i.test(key)?'video/mp4':'application/octet-stream';const job=await env.VIDEOS.createMultipartUpload(key,{httpMetadata:{contentType:typ}});return resp({key:job.key,uploadId:job.uploadId});}
 if(route==='/part'&&method==='PUT'){const id=u.searchParams.get('uploadId'),num=Number(u.searchParams.get('number'));if(!id||!Number.isInteger(num)||num<1||num>10000||!request.body)return resp({error:'Invalid part'},400);const job=env.VIDEOS.resumeMultipartUpload(key,id),part=await job.uploadPart(num,request.body);return resp({partNumber:part.partNumber,etag:part.etag});}
 if(route==='/complete'&&method==='POST'){const id=u.searchParams.get('uploadId'),parts=await request.json();if(!id||!Array.isArray(parts)||!parts.length||parts.length>10000||parts.some((p,i)=>p.partNumber!==i+1||typeof p.etag!=='string'))return resp({error:'Invalid completion'},400);const obj=await env.VIDEOS.resumeMultipartUpload(key,id).complete(parts);return resp({key:obj.key,size:obj.size,etag:obj.etag});}
 if(route==='/abort'&&method==='POST'){const id=u.searchParams.get('uploadId');if(!id)return resp({error:'Missing ID'},400);await env.VIDEOS.resumeMultipartUpload(key,id).abort();return resp({aborted:true});}
 return resp({error:'Not found'},404);
 }catch(e){return resp({error:String(e.message||e).slice(0,240)},500);}
}};