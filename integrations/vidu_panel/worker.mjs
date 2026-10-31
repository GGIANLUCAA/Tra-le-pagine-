import {verifyGithub} from './github-oidc.mjs';
import { HTML, CLIENT, CSS } from './ui.mjs';
const PREFIX = 'private-vidu/v1/';
const API = 'https://api.vidu.com';
const enc = new TextEncoder();
const ID = /^[a-f0-9]{64}$/;
const PRICE_DATE = '2026-10-28';
const PRICE_UNTIL = Date.parse('2026-11-04T23:59:59Z');
const headers = {'cache-control':'private, no-store','x-content-type-options':'nosniff','referrer-policy':'no-referrer','x-frame-options':'DENY'};
const reply = (v,status=200) => Response.json(v,{status,headers});
class InputError extends Error {}
const fail = message => {throw new InputError(message);};
const hash = async data => [...new Uint8Array(await crypto.subtle.digest('SHA-256', typeof data==='string'?enc.encode(data):data))].map(v=>v.toString(16).padStart(2,'0')).join('');
const get = async (env,key) => {const o=await env.VIDEOS.get(PREFIX+key);return o?o.json():null;};
const put = (env,key,data,options={}) => env.VIDEOS.put(PREFIX+key,JSON.stringify(data),{httpMetadata:{contentType:'application/json'},...options});
function clean(value,max,min=1){if(typeof value!=='string'||value.trim().length<min||value.length>max||/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(value))fail('Compila tutti i campi richiesti.');return value.trim();}
export async function readJSON(req,max=9_000_000){
 const reader=req.body?.getReader();if(!reader)fail('Richiesta vuota.');let total=0;const chunks=[];
 while(true){const {done,value}=await reader.read();if(done)break;total+=value.length;if(total>max){await reader.cancel();fail('File troppo grande (massimo 6 MB).');}chunks.push(value);}
 const bytes=new Uint8Array(total);let offset=0;for(const c of chunks){bytes.set(c,offset);offset+=c.length;}
 try{return JSON.parse(new TextDecoder().decode(bytes));}catch{fail('Richiesta non valida.');}
}
export function imageInfo(uri){
 if(typeof uri!=='string'||uri.length>8_100_000)fail('Immagine troppo grande.');
 const m=/^data:image\/(png|jpeg);base64,([A-Za-z0-9+/]+={0,2})$/.exec(uri);if(!m)fail('Carica un JPG o PNG.');
 let b;try{b=Uint8Array.from(atob(m[2]),c=>c.charCodeAt(0));}catch{fail('Immagine non valida.');}
 if(b.length<100||b.length>6_000_000)fail('Immagine non valida o oltre 6 MB.');
 const v=new DataView(b.buffer);let w=0,h=0;
 if(m[1]==='png' && v.getUint32(0)===0x89504e47 && v.getUint32(4)===0x0d0a1a0a && v.getUint32(12)===0x49484452){w=v.getUint32(16);h=v.getUint32(20);}
 else if(m[1]==='jpeg' && b[0]===255&&b[1]===216){
  let p=2;while(p+4<b.length){if(b[p++]!==255)break;while(b[p]===255)p++;const marker=b[p++];if(marker===0xda||marker===0xd9)break;
   if(marker===0x01||(marker>=0xd0&&marker<=0xd7))continue;
   const n=v.getUint16(p);if(n<2||p+n>b.length)break;
   if([0xc0,0xc1,0xc2].includes(marker)&&n>=7){h=v.getUint16(p+3);w=v.getUint16(p+5);break;}p+=n;
  }
 }
 if(Math.min(w,h)<256||Math.max(w,h)>16000||Math.max(w/h,h/w)>=4)fail('JPG/PNG: minimo 256 px per lato, proporzioni inferiori a 4:1.');
 return {bytes:b,width:w,height:h,mime:'image/'+m[1]};
}
export function estimate(seconds,offPeak,first=8,extra=2){
 if(!Number.isInteger(seconds)||seconds<2||seconds>10||typeof offPeak!=='boolean')fail('Scegli da 2 a 10 secondi.');
 const standard=first+extra*(seconds-1);return offPeak?Math.ceil(standard/2):standard;
}
export async function makePlan(body,now=Date.now(),pricing={first:8,extra:2,date:PRICE_DATE,expiresAt:PRICE_UNTIL}){
 if(now>pricing.expiresAt)fail('Listino da verificare e aggiornare prima di nuove generazioni.');
 const img=imageInfo(body.image), credits=estimate(body.duration,body.offPeak,pricing.first,pricing.extra);
 const plan={project:clean(body.project,120),format:clean(body.format,40),scene:clean(body.scene,160),
  narration:clean(body.narration,1500),startSeconds:body.startSeconds,reason:clean(body.reason,1000,10),
  prompt:clean(body.prompt,2000,30),model:'viduq2-pro-fast',resolution:'720p',duration:body.duration,
  offPeak:body.offPeak,credits,usdEstimated:credits*.005,priceDate:pricing.date,priceExpiresAt:pricing.expiresAt,firstCredit:pricing.first,extraCredit:pricing.extra,
  imageHash:await hash(img.bytes),width:img.width,height:img.height,mime:img.mime};
 if(!['libri','racconto','artvision','altro'].includes(plan.format)||!Number.isFinite(plan.startSeconds)||plan.startSeconds<0)fail('Progetto o punto di inserimento non valido.');
 const id=await hash(JSON.stringify(plan));return {...plan,id,approvalCode:id.slice(0,12).toUpperCase(),createdAt:now,expiresAt:now+600_000};
}
async function encryptionKey(env){
 if(!env.CONFIG_SECRET||env.CONFIG_SECRET.length<32)throw Error('config');
 return crypto.subtle.importKey('raw',await crypto.subtle.digest('SHA-256',enc.encode(env.CONFIG_SECRET)),{name:'AES-GCM'},false,['encrypt','decrypt']);
}
async function keyFor(env){
 if(env.VIDU_API_KEY)return env.VIDU_API_KEY;
 const saved=await get(env,'connection.json');if(!saved)fail('Collega prima il tuo account Vidu nelle impostazioni.');
 const raw=Uint8Array.from(atob(saved.data),c=>c.charCodeAt(0));
 return new TextDecoder().decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:raw.slice(0,12)},await encryptionKey(env),raw.slice(12)));
}
async function saveKey(env,key){
 const iv=crypto.getRandomValues(new Uint8Array(12));const encrypted=new Uint8Array(await crypto.subtle.encrypt({name:'AES-GCM',iv},await encryptionKey(env),enc.encode(key)));
 const raw=new Uint8Array(iv.length+encrypted.length);raw.set(iv);raw.set(encrypted,12);
 await put(env,'connection.json',{data:btoa(String.fromCharCode(...raw)),updatedAt:Date.now()});
}
async function api(key,path,method='GET',body){
 const r=await fetch(API+path,{method,headers:{Authorization:'Token '+key,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(25000),redirect:'error'});
 if(!r.ok)throw Error('provider');return r.json();
}
export function balanceRows(data){
 const rows=data.remains??data.remaining_credits;
 if(!Array.isArray(rows)||!rows.length||rows.some(r=>!Number.isFinite(r.credit_remain)||r.credit_remain<0))fail('Saldo API non interpretabile: controlla la console Vidu.');
 // Show separate billing pools; never infer that overlapping packs can be summed.
 return rows.map(r=>({type:String(r.type||'crediti'),credits:r.credit_remain}));
}
async function authenticate(req,env){
 const token=req.headers.get('authorization')||'';
 if(!/^Bearer [^\r\n]{32,180}$/.test(token)||!env.STUDIO)return false;
 const response=await env.STUDIO.fetch(new Request('https://video-library-studio.600led.workers.dev/api/workspace?limit=1',{headers:{authorization:token}}));
 if(response.status!==200)return false;
 try{return (await response.json()).ok===true;}catch{return false;}
}
function validId(id){if(!ID.test(id||''))fail('Identificativo non valido.');return id;}
export async function submit(env,body,now=Date.now()){
 const id=validId(body.id),plan=await get(env,'plans/'+id+'.json');
 if(!plan||now>plan.expiresAt||now>plan.priceExpiresAt||body.code!==plan.approvalCode||body.confirmed!==true)fail('Approva il preventivo esatto e ancora valido.');
 const existing=await get(env,'jobs/'+id+'.json');if(existing)return existing;
 const pricing=await get(env,'pricing.json');if(pricing&&(pricing.first!==plan.firstCredit||pricing.extra!==plan.extraCredit))fail('Il listino è cambiato: prepara un nuovo preventivo.');
 const key=await keyFor(env);const rows=balanceRows(await api(key,'/ent/v2/credits'));
 if(!rows.some(x=>x.credits>=plan.credits))fail('Saldo insufficiente in un singolo portafoglio API.');
 const img=await env.VIDEOS.get(PREFIX+'images/'+plan.imageHash+'.bin');if(!img)fail('Immagine non disponibile.');
 const bytes=new Uint8Array(await img.arrayBuffer());if(await hash(bytes)!==plan.imageHash)fail('Immagine cambiata: prepara un nuovo preventivo.');
 let binary='';for(let p=0;p<bytes.length;p+=16384)binary+=String.fromCharCode(...bytes.subarray(p,p+16384));
 // Atomic permanent reservation BEFORE the only billable POST. Timeout is ambiguous.
 const job={id,plan,status:'submission_unknown',createdAt:now,updatedAt:now,review:'needs_review'};
 const lock=await put(env,'jobs/'+id+'.json',job,{onlyIf:new Headers({'If-None-Match':'*'})});
 if(!lock)return await get(env,'jobs/'+id+'.json');
 try{
  const result=await api(key,'/ent/v2/img2video','POST',{model:plan.model,images:['data:'+plan.mime+';base64,'+btoa(binary)],prompt:plan.prompt,duration:plan.duration,resolution:plan.resolution,off_peak:plan.offPeak,audio:false,is_rec:false,payload:id});
  if(typeof result.task_id!=='string'||!/^[A-Za-z0-9_-]{1,120}$/.test(result.task_id))throw Error('task');
  job.taskId=result.task_id;job.status='processing';job.creditsReported=result.credits??null;
  await put(env,'active/'+id+'.json',{id});
  await put(env,'jobs/'+id+'.json',job);
 }catch{/* The reservation is intentionally retained. No retry or fallback. */}
 return job;
}
export async function collect(env,id){
 validId(id);const job=await get(env,'jobs/'+id+'.json');if(!job)fail('Generazione non trovata.');
 if(!job.taskId||['ready','failed','cancelled'].includes(job.status))return job;
 const data=await api(await keyFor(env),'/ent/v2/tasks/'+job.taskId+'/creations');
 job.updatedAt=Date.now();job.creditsReported=data.credits??job.creditsReported;
 if(data.state==='success'){
  const url=new URL(data.creations?.[0]?.url);if(url.protocol!=='https:'||url.username||url.password)throw Error('url');
  // Only provider-returned URLs; redirects are not followed and no credentials are sent.
  const r=await fetch(url,{redirect:'error',signal:AbortSignal.timeout(60000)});
  const size=Number(r.headers.get('content-length'));
  if(!r.ok||!Number.isFinite(size)||size<1000||size>60_000_000)throw Error('media');
  const bytes=await r.arrayBuffer();if(bytes.byteLength!==size||new TextDecoder().decode(bytes.slice(4,8))!=='ftyp')throw Error('mp4');
  // .bin keeps unreviewed, private clips out of the existing public MP4 catalog.
  await env.VIDEOS.put(PREFIX+'clips/'+id+'.bin',bytes,{httpMetadata:{contentType:'video/mp4'}});
  job.sha256=await hash(bytes);job.bytes=bytes.byteLength;job.status='ready';
 }else if(['failed','cancelled'].includes(data.state))job.status=data.state;
 else job.status='processing';
 await put(env,'jobs/'+id+'.json',job);
 if(['ready','failed','cancelled'].includes(job.status))await env.VIDEOS.delete(PREFIX+'active/'+id+'.json');
 return job;
}
export async function sweep(env){
 // Read/download only. Iterate all pages; no paid submission exists in this path.
 let cursor;do{const page=await env.VIDEOS.list({prefix:PREFIX+'active/',limit:20,cursor});
 for(const item of page.objects){const id=item.key.split('/').pop().replace('.json','');try{await collect(env,id);}catch{/* Next sweep retries only status/download. */}}
 cursor=page.truncated?page.cursor:undefined;}while(cursor);
}
export default {
 async scheduled(event,env,ctx){ctx.waitUntil(sweep(env));},
 async fetch(req,env){
  const u=new URL(req.url),p=u.pathname;
  if(req.method==='GET'&&['/','/app.js','/app.css'].includes(p))return new Response(p==='/'?HTML:p==='/app.js'?CLIENT:CSS,{headers:{...headers,'content-type':p==='/'?'text/html; charset=utf-8':p==='/app.js'?'text/javascript; charset=utf-8':'text/css; charset=utf-8','content-security-policy':"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"}});
  if(!p.startsWith('/api/'))return reply({error:'Pagina non trovata.'},404);
  try{
   if(p==='/api/github-connect'&&req.method==='POST'){
    // No browser auth bypass: exact short-lived GitHub OIDC signature is required.
    try{await verifyGithub((req.headers.get('authorization')||'').replace(/^Bearer /,''),env);}catch(e){return reply({error:'Importazione GitHub non autorizzata.',reason:['disabled','token','claims','jwks','key','signature'].includes(e.message)?e.message:'token'},403);}
    const b=await readJSON(req,4096),key=clean(b.key,500,20);if(/\s/.test(key))fail('Chiave non valida.');
    const receipt='imports/'+env.IMPORT_COMMIT+'.json';
    if(await get(env,receipt))return reply({connected:true,alreadyImported:true});
    balanceRows(await api(key,'/ent/v2/credits'));
    await saveKey(env,key);
    await put(env,receipt,{connected:true,at:Date.now(),commit:env.IMPORT_COMMIT});
    return reply({connected:true,verifiedReadOnly:true});
   }
   if(req.method!=='GET'&&req.headers.get('origin')!==u.origin)return reply({error:'Origine non autorizzata.'},403);
   if(!await authenticate(req,env))return reply({error:'Accedi con la chiave di gestione del tuo Video Library Studio.'},401);
   if(p==='/api/status'&&req.method==='GET')return reply({connected:Boolean(env.VIDU_API_KEY||await get(env,'connection.json')),priceDate:pricing.date,priceExpiresAt:pricing.expiresAt,firstCredit:pricing.first,extraCredit:pricing.extra,priceValid:Date.now()<=PRICE_UNTIL});
   if(p==='/api/connect'&&req.method==='POST'){
    const b=await readJSON(req,4096),key=clean(b.key,500,20);if(/\s/.test(key))fail('Chiave non valida.');
    const rows=balanceRows(await api(key,'/ent/v2/credits'));await saveKey(env,key);return reply({connected:true,balances:rows});
   }
   if(p==='/api/balance'&&req.method==='GET')return reply({balances:balanceRows(await api(await keyFor(env),'/ent/v2/credits'))});
   if(p==='/api/plan'&&req.method==='POST'){
    const b=await readJSON(req),pricing=await get(env,'pricing.json'),plan=await makePlan(b,Date.now(),pricing||undefined),img=imageInfo(b.image);
    await env.VIDEOS.put(PREFIX+'images/'+plan.imageHash+'.bin',img.bytes,{httpMetadata:{contentType:img.mime}});
    await put(env,'plans/'+plan.id+'.json',plan);return reply(plan);
   }
   if(p==='/api/submit'&&req.method==='POST')return reply(await submit(env,await readJSON(req,4096)),202);
   if(p==='/api/jobs'&&req.method==='GET'){
    const page=await env.VIDEOS.list({prefix:PREFIX+'jobs/',limit:30,cursor:u.searchParams.get('cursor')||undefined});
    const items=await Promise.all(page.objects.map(o=>get(env,o.key.slice(PREFIX.length))));
    return reply({items,cursor:page.truncated?page.cursor:null});
   }
   const m=/^\/api\/jobs\/([a-f0-9]{64})\/(refresh|download|recipe)$/.exec(p);
   if(m&&m[2]==='refresh'&&req.method==='POST')return reply(await collect(env,m[1]));
   if(m&&req.method==='GET'){
    const job=await get(env,'jobs/'+m[1]+'.json');if(!job)return reply({error:'Clip non trovata.'},404);
    if(m[2]==='recipe')return reply({...job,usage:'Clip da revisionare. Montaggio e approvazione artistica separati.',downloadPath:'/api/jobs/'+m[1]+'/download'});
    if(m[2]==='download'&&job.status==='ready'){
     const obj=await env.VIDEOS.get(PREFIX+'clips/'+m[1]+'.bin');if(!obj)return reply({error:'Archivio non disponibile.'},404);
     return new Response(obj.body,{headers:{...headers,'content-type':'video/mp4','content-length':String(obj.size),'content-disposition':'attachment; filename="VIDU_'+m[1].slice(0,12)+'.mp4"'}});
    }
   }
   return reply({error:'Operazione non disponibile.'},404);
  }catch(e){return reply({error:e instanceof InputError?e.message:'Operazione non completata. Se avevi premuto Genera, controlla la raccolta e la console Vidu prima di riprovare.'},e instanceof InputError?400:502);}
 }
};
