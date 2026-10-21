const PREFIX = 'workspace/v1/';
const ID = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
const VIDEO = /^(?:gpt:)?[\w ().-]{1,190}\.(mp4|mov|m4v)$/i;
const ROLES = ['voice','visual','cover','rhythm','music','subtitles'];
const reply = (value, status = 200) => Response.json(value, {status, headers:{'cache-control':'private, no-store'}});
async function readBody(req) {
  if (!req.body) throw Error('Richiesta vuota');
  const reader = req.body.getReader(); let size = 0; const chunks = [];
  while (true) { const {done,value} = await reader.read(); if (done) break;
    size += value.byteLength; if (size > 131072) { await reader.cancel(); throw Error('Richiesta troppo grande'); } chunks.push(value);
  }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk,offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder().decode(bytes));
}
const text = (value, max, required = false) => {
  if (typeof value !== 'string' || value.length > max || (required && !value.trim())) throw Error('Testo non valido');
  return value.trim();
};
export function normalizeRecord(input) {
  if (!input || !ID.test(input.id) || !['style','project','log'].includes(input.type)) throw Error('Scheda non valida');
  if (!Array.isArray(input.refs) || input.refs.length > 200) throw Error('Riferimenti non validi');
  const seen = new Set(), refs = input.refs.map(ref => {
    if (!ref || !VIDEO.test(ref.key) || seen.has(ref.key)) throw Error('Riferimento video non valido'); seen.add(ref.key);
    return {key:ref.key,title:text(ref.title,200,true),category:text(ref.category || '',160),size:Number.isFinite(ref.size) && ref.size >= 0 ? ref.size : 0};
  });
  const roles = {};
  for (const role of ROLES) {
    const value = input.roles?.[role]; if (!value) continue;
    if (value.key && !seen.has(value.key)) throw Error('La sorgente dello stile deve essere tra i riferimenti');
    roles[role] = {key:text(value.key || '',220),note:text(value.note || '',1200)};
  }
  const settings = {};
  for (const field of ['format','duration','language','destination']) settings[field] = text(input.settings?.[field] || '',160);
  return {id:input.id,type:input.type,title:text(input.title,160,true),topic:text(input.topic || '',1500),notes:text(input.notes || '',6000),refs,roles,settings,archived:input.archived === true};
}

export async function handleWorkspace(req, env, authorized) {
  if (!authorized) return reply({ok:false,message:'Accedi alla gestione privata per salvare online o archiviare i video.'},401);
  const url = new URL(req.url);
  try {
    if (url.pathname === '/api/workspace' && req.method === 'GET') {
      const page = await env.VIDEOS.list({prefix:PREFIX,limit:100,cursor:url.searchParams.get('cursor') || undefined});
      const items = [];
      for (let i=0;i<page.objects.length;i+=10) {
        const batch = await Promise.all(page.objects.slice(i,i+10).map(async row => {
          const obj = await env.VIDEOS.get(row.key); if (!obj) return null;
          return {...await obj.json(),etag:obj.etag};
        })); items.push(...batch.filter(Boolean));
      }
      return reply({ok:true,items,cursor:page.truncated ? page.cursor : null});
    }
    if (url.pathname === '/api/workspace' && req.method === 'POST') {
      const body = await readBody(req), record = normalizeRecord(body.record), key = PREFIX + record.id + '.json';
      const current = await env.VIDEOS.get(key);
      if (current && (!body.etag || body.etag !== current.etag)) return reply({ok:false,message:'La scheda è stata modificata altrove. Ricaricala prima di salvare.'},409);
      if (!current && body.etag) return reply({ok:false,message:'La scheda originale non è più disponibile.'},409);
      const old = current ? await current.json() : null;
      const saved = {...record,createdAt:old?.createdAt || new Date().toISOString(),updatedAt:new Date().toISOString(),revision:(old?.revision || 0)+1};
      const put = await env.VIDEOS.put(key,JSON.stringify(saved),{httpMetadata:{contentType:'application/json'},onlyIf:current ? {etagMatches:current.etag} : {etagDoesNotMatch:'*'}});
      if (!put) return reply({ok:false,message:'Salvataggio concorrente. Ricarica la scheda e riprova.'},409);
      return reply({ok:true,record:{...saved,etag:put.etag}});
    }
    if (url.pathname === '/api/bulk' && req.method === 'POST') {
      const body = await readBody(req);
      if (!['archive','restore'].includes(body.action) || !Array.isArray(body.keys) || !body.keys.length || body.keys.length > 200 || body.keys.some(k => typeof k !== 'string' || !VIDEO.test(k))) return reply({ok:false,message:'Selezione non valida (massimo 200 video).'},400);
      const keys = [...new Set(body.keys)];
      const indexObj = keys.some(k => k.startsWith('gpt:')) ? await env.VIDEOS.get('catalog/chatgpt-index.json') : null;
      const index = indexObj ? await indexObj.json() : [];
      const known = new Set(Array.isArray(index) ? index.map(x=>x.name) : []);
      for (let i=0;i<keys.length;i+=10) {
        const exists = await Promise.all(keys.slice(i,i+10).map(k => k.startsWith('gpt:') ? known.has(k.slice(4)) : env.VIDEOS.head(k)));
        if (exists.some(x=>!x)) return reply({ok:false,message:'Uno dei video selezionati non esiste più. Aggiorna il catalogo.'},404);
      }
      const object = await env.VIDEOS.get('catalog/manage.json'), edits = object ? await object.json() : {};
      const before = keys.map(key=>({key,hidden:!!edits[key]?.hidden}));
      for (const key of keys) edits[key] = {...edits[key],hidden:body.action === 'archive'};
      const result = await env.VIDEOS.put('catalog/manage.json',JSON.stringify(edits),{httpMetadata:{contentType:'application/json'},onlyIf:object ? {etagMatches:object.etag} : {etagDoesNotMatch:'*'}});
      if (!result) return reply({ok:false,message:'Il catalogo è cambiato. Aggiorna e riprova.'},409);
      return reply({ok:true,count:keys.length,action:body.action,before});
    }
    return reply({ok:false,message:'Operazione non disponibile'},405);
  } catch (error) { return reply({ok:false,message:error.message || 'Richiesta non valida'},400); }
}
