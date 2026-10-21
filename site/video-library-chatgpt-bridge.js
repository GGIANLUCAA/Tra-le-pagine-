const VERSION="0.2.0";
const NAME="Video Library Studio - Import ChatGPT";
const CHUNK=8*1024*1024, MAX=400*1024*1024;
const fileSchema={type:"object",properties:{
 download_url:{type:"string"},file_id:{type:"string"},mime_type:{type:"string"},file_name:{type:"string"}
},required:["download_url","file_id"],additionalProperties:false};
const tools=[
{name:"open_importer",title:"Apri importatore Libreria ChatGPT",description:"Mostra un pannello per selezionare video già presenti nella Libreria ChatGPT e importarli una sola volta nella videoteca personale, senza scaricarli sul telefono.",inputSchema:{type:"object",properties:{},additionalProperties:false},annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},_meta:{ui:{resourceUri:"ui://video-library/import.html"},"openai/outputTemplate":"ui://video-library/import.html"}},
{name:"import_chatgpt_video",title:"Importa video autorizzato dalla Libreria ChatGPT",description:"Importa un video originale MP4/MOV/M4V autorizzato dalla Libreria ChatGPT nello storage della videoteca, senza creare duplicati. Richiede esattamente un file selezionato dal proprietario tramite ChatGPT fileParams.",inputSchema:{type:"object",properties:{file:fileSchema},required:["file"],additionalProperties:false},annotations:{readOnlyHint:false,destructiveHint:false,openWorldHint:true},_meta:{"openai/fileParams":["file"],"openai/widgetAccessible":true,ui:{visibility:["model","app"]},"openai/toolInvocation/invoking":"Importazione video in corso...","openai/toolInvocation/invoked":"Importazione completata"}},
{name:"video_library_status",title:"Stato videoteca",description:"Mostra quanti MP4 sono già conservati nell'archivio R2 e quanti importi dalla Libreria ChatGPT sono stati completati.",inputSchema:{type:"object",properties:{},additionalProperties:false},annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false}}
];
const UI_RESOURCE="ui://video-library/import.html";
const IMPORTER_HTML="<!doctype html><html lang=\"it\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>\n:root{color-scheme:dark}*{box-sizing:border-box}body{background:#0e1727;color:#edf2fb;font:14px/1.5 system-ui,Arial,sans-serif;margin:0;padding:18px}h2{font-size:21px;margin:0 0 9px}p{color:#bdc9da;margin:8px 0 16px}.actions{display:flex;gap:10px;flex-wrap:wrap}button{border:1px solid #63748f;border-radius:10px;background:#283a54;color:white;font:inherit;padding:10px 14px;cursor:pointer}button.primary{background:#c5a6f1;color:#20142b;font-weight:700;border-color:#c5a6f1}button:disabled{opacity:.45;cursor:default}.entry{display:flex;gap:10px;align-items:center;border:1px solid #33435b;padding:10px;border-radius:10px;margin:7px 0;background:#17233a;word-break:break-word}.entry input{flex:none}.muted{color:#98aec9;font-size:12px}pre{overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;color:#c4d1e2;font:12px/1.5 ui-monospace,monospace;background:#131f32;padding:12px;border-radius:10px;min-height:62px}.good{color:#9ce5b0}.bad{color:#ffc1bd}a{color:#c7aef8}\n</style></head><body><h2>✦ Importa i video dalla Libreria ChatGPT</h2><p>Seleziona i video MP4 che hai già creato in ChatGPT. Il trasferimento avviene direttamente dal servizio al tuo archivio, senza scaricarli sul telefono. I file già presenti non vengono duplicati.</p><p class=\"muted\">⚠ I video importati diventano riproducibili dalla videoteca online, che attualmente è pubblica. Seleziona solo filmati che vuoi rendere disponibili sul sito.</p><p><label><input type=\"checkbox\" id=\"publish\"> Confermo di voler pubblicare i video selezionati nella videoteca.</label></p><div class=\"actions\"><button id=\"pick\" class=\"primary\">Seleziona dalla Libreria ChatGPT</button><button id=\"start\" disabled>Importa i selezionati</button></div><div id=\"list\"></div><pre id=\"status\">In attesa della selezione. L'originale nella Libreria ChatGPT non verrà cancellato.</pre><p class=\"muted\">Prima prova: importa un solo video musicale. Quando avrai verificato la riproduzione, potrai selezionarne più di uno. La funzione richiede il plugin privato collegato a ChatGPT.</p><script>\nlet chosen=[],busy=false;const $=s=>document.querySelector(s),message=s=>{$('#status').textContent=s};const api=()=>window.openai;\n$('#pick').onclick=async()=>{if(busy)return;try{if(!api()?.selectFiles){message('Questo ambiente non espone ancora la selezione dei file ChatGPT. Apri il plugin da ChatGPT Work sul web.');return}const files=await api().selectFiles();chosen=files.filter(f=>/\\.(mp4|mov|m4v)$/i.test(f.fileName||'')||/^(video\\/mp4|video\\/quicktime|video\\/x-m4v)$/i.test(f.mimeType||''));$('#list').replaceChildren();for(const item of chosen){const div=document.createElement('label');div.className='entry';const check=document.createElement('input');check.type='checkbox';check.checked=true;check.value=item.fileId;const span=document.createElement('span');span.textContent=item.fileName||item.fileId;div.append(check,span);$('#list').append(div)}$('#start').disabled=!chosen.length;message('Trovati '+chosen.length+' video compatibili. Inizia con un solo video per il primo test.');}catch(e){message('Selezione non riuscita: '+String(e.message||e))}};\n$('#start').onclick=async()=>{if(busy)return;if(!$('#publish').checked){message('Prima conferma che i video selezionati possono essere pubblicati sul sito.');return;}const selected=chosen.filter(x=>Array.from($('#list').querySelectorAll('input:checked')).some(c=>c.value===x.fileId));if(!selected.length){message('Seleziona almeno un video.');return}if(!api()?.getFileDownloadUrl||!api()?.callTool){message('Il collegamento ChatGPT non supporta i metodi necessari.');return}busy=true;$('#start').disabled=true;$('#pick').disabled=true;let done=0,success=0,fail=0,notes=[];for(const f of selected){try{message('Trasferimento '+(done+1)+'/'+selected.length+': '+(f.fileName||'video')+'\\nNon chiudere il pannello durante il trasferimento.');const u=await api().getFileDownloadUrl({fileId:f.fileId});if(!u?.downloadUrl)throw Error('ChatGPT non ha restituito un collegamento temporaneo');const call=await api().callTool('import_chatgpt_video',{file:{download_url:u.downloadUrl,file_id:f.fileId,mime_type:f.mimeType||'video/mp4',file_name:f.fileName||'video.mp4'}});const output=call?.structuredContent||call?.result?.structuredContent||{};if(call?.isError||output?.ok===false)throw Error(output?.message||JSON.stringify(call?.content||'errore'));notes.push('✓ '+f.fileName+': '+(output.reused?'già presente':output.key?'acquisito':'richiesta inviata'));success++;}catch(e){notes.push('✗ '+f.fileName+': '+String(e.message||e));fail++}done++;message('Completati '+done+'/'+selected.length+'. Riusciti '+success+', errori '+fail+'.\\n'+notes.join('\\n'))}busy=false;$('#pick').disabled=false;$('#start').disabled=false;const l=document.createElement('a');l.href='https://video-library-studio.600led.workers.dev';l.target='_blank';l.rel='noopener';l.textContent='Apri Video Library Studio';$('#list').append(l)};\n</script></body></html>";
const status=(c)=>({content:[{type:"text",text:JSON.stringify(c)}],structuredContent:c});
const error=(msg)=>({isError:true,content:[{type:"text",text:msg}],structuredContent:{ok:false,message:msg}});
const mkResult=(id,value)=>({jsonrpc:"2.0",id,result:value});
const mimeOf=(name)=>/\.mp4$/i.test(name)?"video/mp4":/\.mov$/i.test(name)?"video/quicktime":"video/x-m4v";
async function authorized(req,env) {
 const route=new URL(req.url).pathname;const match=route.match(/^\/mcp\/([a-f0-9]{64})$/i)||route.match(/^\/([a-f0-9]{64})\/mcp$/i);const segment=match?.[1]||"";
 if(!/^[a-f0-9]{64}$/i.test(segment)||!env.BRIDGE_TOKEN_SHA256)return false;
 const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(segment));
 const hex=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,"0")).join("");
 const a=String(env.BRIDGE_TOKEN_SHA256);if(a.length!==64)return false;
 let diff=0;for(let i=0;i<64;i++)diff|=a.charCodeAt(i)^hex.charCodeAt(i);
 return diff===0;
}
function hostAllowed(host) {
 const h=host.toLowerCase();
 return ["openai.com","chatgpt.com","oaiusercontent.com","oaistatic.com","oaiusercontent.net"].some(x=>h===x||h.endsWith("."+x));
}
function safeName(value) {
 if(typeof value!=="string")return "";
 const name=value.replaceAll("\\","/").split("/").pop().normalize("NFKD").replace(/[\u0300-\u036f]/g,"").replace(/[^A-Za-z0-9_ ().-]/g,"_").replace(/ +/g,"_").replace(/_{2,}/g,"_").slice(0,160);
 if(!/\.(mp4|mov|m4v)$/i.test(name))return "";
 return name;
}
async function getJSON(env,key){try{const r=await env.VIDEOS.get(key);return r?await r.json():{}}catch{return {}}}
async function archiveStatus(env) {
 const objects=[];let cursor;do{const page=await env.VIDEOS.list({limit:1000,cursor});objects.push(...page.objects.filter(o=>/\.(mp4|mov|m4v)$/i.test(o.key)));cursor=page.truncated?page.cursor:undefined}while(cursor);
 const bridge=await getJSON(env,"catalog/chatgpt-bridge.json");
 return {ok:true,videoCount:objects.length,chatgptImports:Object.keys(bridge).length,watch:"https://video-library-studio.600led.workers.dev"};
}
async function importFile(file,env){
 if(!file||typeof file!=="object"||typeof file.download_url!=="string"||typeof file.file_id!=="string")return error("Manca un file selezionato dalla Libreria ChatGPT.");
 if(file.file_id.length>160||!/^[A-Za-z0-9_-]+$/.test(file.file_id))return error("Identificativo file non valido.");
 const name=safeName(file.file_name||"");if(!name)return error("Formato non ancora supportato dal ponte: usare MP4, MOV o M4V. WebM/MKV richiederanno una conversione per il browser.");
 let source;try{source=new URL(file.download_url)}catch{return error("Collegamento temporaneo non valido.");}
 if(source.protocol!=="https:"||source.username||source.password||source.port&&source.port!=="443"||!hostAllowed(source.hostname))return error("L'indirizzo temporaneo fornito non appartiene a un'origine OpenAI riconosciuta. Host: "+source.hostname+". Nessun dato è stato trasferito.");
 const ledger=await getJSON(env,"catalog/chatgpt-bridge.json");
 if(ledger[file.file_id]?.key){
  const found=await env.VIDEOS.head(ledger[file.file_id].key);
  if(found)return status({ok:true,reused:true,key:found.key,size:found.size,watch:"https://video-library-studio.600led.workers.dev/media/"+encodeURIComponent(found.key)});
 }
 let download;
 try{download=await fetch(source.toString(),{redirect:"manual",headers:{"Accept":"application/octet-stream,video/*"}})}catch(e){return error("Collegamento temporaneo non accessibile dal ponte: "+String(e.message||e).slice(0,160));}
 for(let redirects=0;download.status>=300&&download.status<400&&redirects<4;redirects++){
  const target=download.headers.get("location");if(!target)return error("Reindirizzamento privo di destinazione.");
  const dst=new URL(target,source);if(dst.protocol!=="https:"||dst.port&&dst.port!=="443"||!hostAllowed(dst.hostname))return error("Il servizio ha reindirizzato il download su un host non autorizzato: "+dst.hostname);
  source=dst;download=await fetch(source.toString(),{redirect:"manual"});
 }
 if(!download.ok||!download.body)return error("ChatGPT non ha fornito il video: HTTP "+download.status);
 const expected=Number(download.headers.get("content-length"))||0;
 if(expected>MAX)return error("Video troppo grande per la prima versione del ponte (limite 400 MB).");
 const listing=[];let cur;do{const page=await env.VIDEOS.list({limit:1000,cursor:cur});listing.push(...page.objects.filter(o=>/\.(mp4|mov|m4v)$/i.test(o.key)));cur=page.truncated?page.cursor:undefined}while(cur);
 if(expected){const same=listing.filter(o=>o.size===expected);if(same.length===1){
  const reused=same[0];ledger[file.file_id]={key:reused.key,size:reused.size,sourceName:name,importedAt:new Date().toISOString(),reused:true};
  await env.VIDEOS.put("catalog/chatgpt-bridge.json",JSON.stringify(ledger),{httpMetadata:{contentType:"application/json"}});
  await download.body.cancel();
  return status({ok:true,reused:true,key:reused.key,size:reused.size,watch:"https://video-library-studio.600led.workers.dev/media/"+encodeURIComponent(reused.key)});
 }}
 let key=name;
 const collision=await env.VIDEOS.head(key);
 if(collision){const short=file.file_id.replace(/[^A-Za-z0-9]/g,"").slice(-12);key=name.replace(/\.(mp4|mov|m4v)$/i,"__GPT_"+short+"$&");}
 let current=new Uint8Array(CHUNK),used=0,total=0,mp=null,parts=[],number=1;
 try{
  const reader=download.body.getReader();
  while(true){
    const {done,value}=await reader.read();if(done)break;
    if(!value)continue;total+=value.byteLength;if(total>MAX)throw Error("Dimensione eccessiva oltre 400 MB");
    let offset=0;while(offset<value.byteLength){
      if(used===CHUNK){if(!mp)mp=await env.VIDEOS.createMultipartUpload(key,{httpMetadata:{contentType:mimeOf(key)},customMetadata:{source:"chatgpt-library",fileId:file.file_id}});const chunk=await mp.uploadPart(number,current);parts.push({partNumber:number,etag:chunk.etag});number++;current=new Uint8Array(CHUNK);used=0;}
      const count=Math.min(CHUNK-used,value.byteLength-offset);current.set(value.subarray(offset,offset+count),used);used+=count;offset+=count;
    }
  }
  if(!total)throw Error("Video vuoto");
  if(expected&&expected!==total)throw Error("Il contenuto scaricato non corrisponde alla dimensione indicata");
  if(mp){if(used){const part=await mp.uploadPart(number,current.subarray(0,used));parts.push({partNumber:number,etag:part.etag});}await mp.complete(parts);}
  else await env.VIDEOS.put(key,current.subarray(0,used),{httpMetadata:{contentType:mimeOf(key)},customMetadata:{source:"chatgpt-library",fileId:file.file_id}});
 }catch(e){if(mp)try{await mp.abort()}catch{}return error("Importazione interrotta, originale non modificato: "+String(e.message||e).slice(0,200));}
 const verified=await env.VIDEOS.head(key);if(!verified||verified.size!==total)return error("File ricevuto ma controllo dimensione non superato. Non dichiarato completato.");
 ledger[file.file_id]={key,size:total,sourceName:name,importedAt:new Date().toISOString(),reused:false};
 await env.VIDEOS.put("catalog/chatgpt-bridge.json",JSON.stringify(ledger),{httpMetadata:{contentType:"application/json"}});
 return status({ok:true,reused:false,key,size:total,watch:"https://video-library-studio.600led.workers.dev/media/"+encodeURIComponent(key)});
}
export default {async fetch(req,env){
 const path=new URL(req.url).pathname;
 if(path==="/health")return Response.json({ok:true,service:NAME,version:VERSION,importReady:true,connectionRequired:true});
 if(!path.startsWith("/mcp/")&&!/^\/[a-f0-9]{64}\/mcp$/i.test(path))return new Response("Not found",{status:404});
 if(!await authorized(req,env))return new Response("Not found",{status:404});
 if(req.method==="GET")return new Response("Use MCP Streamable HTTP POST",{status:405,headers:{"allow":"POST, OPTIONS"}});
 if(req.method!=="POST")return new Response("Method not allowed",{status:405});
 if(Number(req.headers.get("content-length")||0)>262144)return new Response("Payload too large",{status:413});
 let data;try{data=await req.json()}catch{return Response.json({jsonrpc:"2.0",id:null,error:{code:-32700,message:"Parse error"}},{status:400});}
 if(!data||data.jsonrpc!=="2.0"||typeof data.method!=="string")return Response.json({jsonrpc:"2.0",id:data?.id??null,error:{code:-32600,message:"Invalid Request"}},{status:400});
 if(data.id==null)return new Response(null,{status:202});
 let result;
 switch(data.method){
  case "initialize":result={protocolVersion:data.params?.protocolVersion||"2025-06-18",capabilities:{tools:{},resources:{}},serverInfo:{name:NAME,version:VERSION},instructions:"Utilizza open_importer per selezionare video dalla Libreria ChatGPT. Importa gli MP4 con fileParams usando import_chatgpt_video; il file resta in ChatGPT e viene acquisito una sola volta in Video Library Studio."};break;
  case "ping":result={};break;
  case "tools/list":result={tools};break;
  case "resources/list":result={resources:[{uri:UI_RESOURCE,name:"Selettore video ChatGPT",mimeType:"text/html;profile=mcp-app"}]};break;
  case "resources/read":
   if(data.params?.uri!==UI_RESOURCE)return Response.json({jsonrpc:"2.0",id:data.id,error:{code:-32002,message:"Resource not found"}});
   result={contents:[{uri:UI_RESOURCE,mimeType:"text/html;profile=mcp-app",text:IMPORTER_HTML,_meta:{ui:{prefersBorder:true,domain:"https://video-library-chatgpt-bridge.600led.workers.dev",csp:{connectDomains:[],resourceDomains:[]}},"openai/widgetDescription":"Selezione dalla Libreria ChatGPT e importazione diretta nel catalogo video"}}]};break;
  case "tools/call":
   if(data.params?.name==="open_importer")result=status({ok:true,action:"select_files",help:"Seleziona video ChatGPT con il pannello e importa in automatico."});
   else if(data.params?.name==="video_library_status")result=status(await archiveStatus(env));
   else if(data.params?.name==="import_chatgpt_video")result=await importFile(data.params?.arguments?.file,env);
   else return Response.json({jsonrpc:"2.0",id:data.id,error:{code:-32601,message:"Unknown tool"}});
   break;
  default:return Response.json({jsonrpc:"2.0",id:data.id,error:{code:-32601,message:"Method not found"}});
 }
 return Response.json(mkResult(data.id,result),{headers:{"cache-control":"no-store"}});
}};
