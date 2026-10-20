/* Tra le Pagine V9 — optional Cloudflare same-origin authenticated GitHub bridge.
   No tokens are ever written into front-end assets, browser storage or log messages.
*/
const OWNER = "GGIANLUCAA";
const REPO = "Tra-le-pagine-";
const BASE = "https://api.github.com/repos/" + OWNER + "/" + REPO;
const EXPECTED_USER = "ggianlucaa";
const ALLOWED_FORMATS = ["libri","cronaca","documentario","fiabe","social"];
const SLUG = /^[A-Za-z0-9][A-Za-z0-9_-]{0,70}$/;
const workflows = Object.freeze({
  v6: "studio-ibrido-v6.yml",
  v7: "archivio-media-v7.yml",
  v8: "orchestratore-v8.yml",
  render: "render-v3.yml",
  publish: "pubblica-video-v11.yml",
  autopilot: "studio-autopilot-v11.yml"
});
const json = (body,status=200) => Response.json(body,{status,headers:{
  "Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}});
const utf8 = new TextEncoder();
const decode8 = new TextDecoder();

function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
function stringValue(value,max=180) {
  return typeof value==="string" && value.length>=1 && value.length<=max && !/[\x00-\x1f\x7f]/.test(value);
}
function slug(value) {return typeof value==="string"&&SLUG.test(value);}
function oneOf(value, values) {return values.includes(value);}
function exactKeys(input, keys) {
  return Object.keys(input).every(x=>keys.includes(x));
}
/** Pure validation: accepts only GitHub workflow inputs that our existing workflow expects. */
export function validateDispatch(payload) {
  if (!isRecord(payload) || !Object.hasOwn(workflows,payload.workflow) || !isRecord(payload.inputs) ||
    !exactKeys(payload,["workflow","inputs","confirmed"])) {
    throw new Error("Richiesta di produzione non valida.");
  }
  const w=payload.workflow,i=payload.inputs;
  if(w==="v6") {
    if(!exactKeys(i,["episodio","formato","budget"]) || !slug(i.episodio) ||
       !oneOf(i.formato,ALLOWED_FORMATS) || !oneOf(i.budget,["zero","basso"]))
      throw new Error("Opzioni storyboard V6 non valide.");
  } else if (w==="v7") {
    if(!exactKeys(i,["mode","provider","kind","query","asset_id"]) ||
       !oneOf(i.mode,["discover","import"]) ||
       !oneOf(i.provider,["openverse","pexels"]) ||
       !oneOf(i.kind,["image","video"]) ||
       (i.provider==="openverse"&&i.kind==="video") ||
       !stringValue(i.query) || i.query.length<2 ||
       typeof i.asset_id!=="string" || i.asset_id.length>80 ||
       (i.mode==="import" && !(
         i.provider==="openverse" ? /^[0-9a-fA-F-]{36}$/.test(i.asset_id) : /^\d{1,14}$/.test(i.asset_id)
       )))
      throw new Error("Opzioni ricerca V7 non valide.");
  } else if (w==="v8") {
    if(!exactKeys(i,["episode","format","mode","gate1_approved"]) ||
       !slug(i.episode) || !oneOf(i.format,ALLOWED_FORMATS) ||
       !oneOf(i.mode,["plan","prepare"]) || typeof i.gate1_approved!=="boolean" ||
       (i.mode==="prepare" && (i.gate1_approved!==true || payload.confirmed!==true)))
      throw new Error("Gate 1 non approvato o parametri V8 errati.");
  } else if (w==="render") {
    if(!exactKeys(i,["episodio","effetti"]) || !slug(i.episodio) ||
       !oneOf(i.effetti,["v4","off"]) || payload.confirmed!==true)
      throw new Error("Montaggio: approvazione esplicita richiesta.");
  } else if (w==="autopilot") {
    if(!exactKeys(i,["title","idea","formato","durata","conferma_costi"]) ||
       typeof i.title!=="string" || typeof i.idea!=="string" ||
       i.title.length<5 || i.title.length>110 ||
       i.idea.length<15 || i.idea.length>1600 ||
       /[\x00-\x1f\x7f]/.test(i.title+i.idea) ||
       !oneOf(i.formato,["libri","fiabe","social"]) ||
       !oneOf(i.durata,["2","3","4"]) ||
       i.conferma_costi!==true || payload.confirmed!==true)
      throw new Error("Produzione AI: approva quota Google e inserisci titolo/descrizione validi.");
  } else if (w==="publish") {
    if(!exactKeys(i,["episode","render_run_id","publish_public"]) ||
       !slug(i.episode) || typeof i.render_run_id!=="string" ||
       !/^\d{6,20}$/.test(i.render_run_id) ||
       i.publish_public!==true || payload.confirmed!==true)
      throw new Error("Pubblicazione PUBBLICA: inserire ID produzione e confermare esplicitamente.");
  }
  return {workflow:workflows[w],inputs:i};
}
function encodeBase64Url(bytes) {
  let binary="";
  for(let i=0;i<bytes.length;i++) binary+=String.fromCharCode(bytes[i]);
  return btoa(binary).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
}
function decodeBase64Url(s) {
  if(typeof s!=="string"||!/^[A-Za-z0-9_-]{1,8000}$/.test(s)) throw Error("Invalid base64url.");
  const binary=atob(s.replace(/-/g,"+").replace(/_/g,"/")+"=".repeat((4-s.length%4)%4));
  return Uint8Array.from(binary, x=>x.charCodeAt(0));
}
function rand(n=32) {return encodeBase64Url(crypto.getRandomValues(new Uint8Array(n)));}
function getCookie(req,name) {
  const header=req.headers.get("Cookie")||"";
  const pair=header.split(";").map(s=>s.trim()).find(x=>x.startsWith(name+"="));
  return pair?pair.slice(name.length+1):"";
}
function cookie(name,value,seconds) {
  return name+"="+value+"; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age="+seconds;
}
async function aesKey(secret) {
  if(typeof secret!=="string"||secret.length<32) throw Error("Missing secure SESSION_SECRET.");
  const hashed=await crypto.subtle.digest("SHA-256",utf8.encode(secret));
  return crypto.subtle.importKey("raw",hashed,"AES-GCM",false,["encrypt","decrypt"]);
}
async function seal(value,secret) {
  const iv=crypto.getRandomValues(new Uint8Array(12));
  const encrypted=new Uint8Array(await crypto.subtle.encrypt(
    {name:"AES-GCM",iv},await aesKey(secret),utf8.encode(JSON.stringify(value))));
  const output=new Uint8Array(iv.length+encrypted.length);
  output.set(iv);output.set(encrypted,iv.length);
  return encodeBase64Url(output);
}
async function unseal(token,secret) {
  const raw=decodeBase64Url(token);
  if(raw.length<29) throw Error("Invalid token.");
  const bytes=await crypto.subtle.decrypt({name:"AES-GCM",iv:raw.slice(0,12)},
      await aesKey(secret),raw.slice(12));
  return JSON.parse(decode8.decode(bytes));
}
export function configured(env) {
  return Boolean(env.GITHUB_CLIENT_ID && env.GITHUB_CLIENT_SECRET &&
    env.STUDIO_SESSION_SECRET && env.STUDIO_SESSION_SECRET.length>=32);
}
function restrictOrigin(req) {
  // same-origin browser POST requests only; CSRF protection for cookie sessions.
  return req.headers.get("Origin")===(new URL(req.url)).origin;
}
async function getSession(req,env) {
  if(!configured(env)) return null;
  const raw=getCookie(req,"tlp_session");
  if(!raw) return null;
  try {
    const session=await unseal(raw,env.STUDIO_SESSION_SECRET);
    if(session.login!==EXPECTED_USER||session.exp<=Date.now()||
      typeof session.access_token!=="string") return null;
    return session;
  } catch {return null;}
}
async function github(url,token,options={}) {
  const response=await fetch(url,{...options,headers:{
    "Accept":"application/vnd.github+json",
    "Authorization":"Bearer "+token,"X-GitHub-Api-Version":"2022-11-28",
    "User-Agent":"Tra-le-Pagine-Studio-Web",...(options.headers||{})
  }});
  return response;
}
async function startAuth(req,env) {
  if(!configured(env)) return json({error:"GitHub OAuth non configurato."},503);
  const url=new URL(req.url);
  const state=rand(32);
  const target=new URL("https://github.com/login/oauth/authorize");
  target.searchParams.set("client_id",env.GITHUB_CLIENT_ID);
  target.searchParams.set("redirect_uri",url.origin+"/auth/callback");
  target.searchParams.set("scope","repo");
  target.searchParams.set("state",state);
  return new Response(null,{status:302,headers:{
    "Location":target.toString(),
    "Set-Cookie":cookie("tlp_oauth_state",state,600),
    "Cache-Control":"no-store"
  }});
}
async function callback(req,env) {
  if(!configured(env)) return json({error:"Backend non pronto."},503);
  const u=new URL(req.url);
  const state=u.searchParams.get("state")||"";
  const code=u.searchParams.get("code")||"";
  const stateCookie=getCookie(req,"tlp_oauth_state");
  if(!stateCookie || stateCookie!==state || !/^[a-zA-Z0-9_-]{10,200}$/.test(code)) {
    return json({error:"Accesso negato: stato OAuth non corrispondente."},403);
  }
  const data=new URLSearchParams({
    client_id:env.GITHUB_CLIENT_ID,client_secret:env.GITHUB_CLIENT_SECRET,code,
    redirect_uri:u.origin+"/auth/callback",state
  });
  const response=await fetch("https://github.com/login/oauth/access_token",{
    method:"POST",headers:{"Accept":"application/json","Content-Type":"application/x-www-form-urlencoded"},body:data.toString()
  });
  if(!response.ok) return json({error:"Scambio OAuth non riuscito."},502);
  const tokenData=await response.json();
  if(!tokenData.access_token||tokenData.error) return json({error:"GitHub non ha autorizzato l'accesso."},403);
  const ownerResponse=await github("https://api.github.com/user",tokenData.access_token);
  if(!ownerResponse.ok) return json({error:"Impossibile verificare l'identità GitHub."},403);
  const owner=await ownerResponse.json();
  if(owner.login?.toLowerCase()!==EXPECTED_USER) return json({
    error:"Questa applicazione può essere usata soltanto dal proprietario previsto."},403);
  // OAuth App token expiration may be shorter: fail closed when known.
  const expiresIn=Math.min(Number(tokenData.expires_in)||28800,28800);
  const sessionCookie=await seal({login:EXPECTED_USER,access_token:tokenData.access_token,
    exp:Date.now()+expiresIn*1000},env.STUDIO_SESSION_SECRET);
  const headers=new Headers({
    "Location":u.origin+"/#studio","Cache-Control":"no-store",
    "Set-Cookie":cookie("tlp_session",sessionCookie,expiresIn)
  });
  headers.append("Set-Cookie",cookie("tlp_oauth_state","",0));
  return new Response(null,{status:302,headers});
}
async function dispatch(req,env) {
  if(!restrictOrigin(req)) return json({error:"Origine richiesta non autorizzata."},403);
  const session=await getSession(req,env);
  if(!session) return json({error:"Devi accedere tramite GitHub."},401);
  const bodyText=await req.text();
  if(bodyText.length>4096) return json({error:"Richiesta troppo grande."},413);
  let payload;try{payload=JSON.parse(bodyText);}catch{return json({error:"JSON non valido."},400);}
  let validated;try{validated=validateDispatch(payload);}catch(e){return json({error:e.message},400);}
  const target=BASE+"/actions/workflows/"+validated.workflow+"/dispatches";
  const res=await github(target,session.access_token,{
    method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({ref:"main",inputs:validated.inputs})
  });
  if(res.status!==204) return json({
    error:res.status===403?"GitHub non ha concesso il permesso Actions: write oppure la quota API è esaurita."
      :"GitHub ha rifiutato l'avvio (HTTP "+res.status+")."
  },res.status===401?401:502);
  return json({ok:true,message:"Richiesta di workflow inviata a GitHub.",workflow:validated.workflow},202);
}
function headerSecurity(resp) {
  const r=new Response(resp.body,resp);
  r.headers.set("X-Content-Type-Options","nosniff");
  r.headers.set("Referrer-Policy","no-referrer");
  r.headers.set("X-Frame-Options","DENY");
  r.headers.set("Content-Security-Policy",
    "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com;"+
    " font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;"+
    " connect-src 'self' https://api.github.com; base-uri 'self';"+
    " frame-ancestors 'none'; form-action 'self'; object-src 'none'");
  return r;
}
export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    try {
      if(url.pathname==="/api/session" && request.method==="GET") {
        const ses=await getSession(request,env);
        return json({ready:configured(env),authenticated:Boolean(ses),login:ses?.login||""});
      }
      if(url.pathname==="/auth/start" && request.method==="GET") return startAuth(request,env);
      if(url.pathname==="/auth/callback" && request.method==="GET") return callback(request,env);
      if(url.pathname==="/api/dispatch" && request.method==="POST") return dispatch(request,env);
      if(url.pathname==="/api/logout" && request.method==="POST") {
        if(!restrictOrigin(request)) return json({error:"Origine non autorizzata."},403);
        return new Response(JSON.stringify({ok:true}),{status:200,headers:{
          "Content-Type":"application/json","Cache-Control":"no-store",
          "Set-Cookie":cookie("tlp_session","",0)
        }});
      }
      if(url.pathname.startsWith("/auth/") || url.pathname.startsWith("/api/")) {
        return json({error:"Endpoint non disponibile."},404);
      }
      const response=await env.ASSETS.fetch(request);
      return headerSecurity(response);
    } catch(e) {
      // Avoid logging secrets or OAuth data.
      return json({error:"Errore temporaneo del servizio. Riprovare oppure usare GitHub Actions."},500);
    }
  }
};
