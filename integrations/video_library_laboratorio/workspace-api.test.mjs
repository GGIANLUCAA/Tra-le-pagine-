import assert from 'node:assert/strict';
import {handleWorkspace} from './workspace-api.mjs';

class Bucket {
  rows=new Map();counter=0;conflict=false;
  object(key){const row=this.rows.get(key);return row?{key,etag:row.etag,json:async()=>JSON.parse(row.value)}:null;}
  async get(key){return this.object(key);}
  async head(key){return this.object(key);}
  async list({prefix,limit}){return {objects:[...this.rows.keys()].filter(k=>k.startsWith(prefix)).slice(0,limit).map(key=>({key})),truncated:false};}
  async put(key,value,options={}){
    const old=this.rows.get(key),condition=options.onlyIf;
    if(this.conflict){this.conflict=false;return null;}
    if(condition?.etagMatches&&old?.etag!==condition.etagMatches)return null;
    if(condition?.etagDoesNotMatch==='*'&&old)return null;
    const etag='e'+(++this.counter);this.rows.set(key,{value,etag});return {etag};
  }
}
const bucket=new Bucket(),env={VIDEOS:bucket};
const request=(path,body)=>new Request('https://test.invalid'+path,body?{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}:{});
const call=async(path,body,auth=true)=>{const res=await handleWorkspace(request(path,body),env,auth);return {status:res.status,data:await res.json()};};
assert.equal((await call('/api/workspace',null,false)).status,401,'Private diary must never be public');
assert.equal((await call('/api/bulk',{action:'archive',keys:['a.mp4']},false)).status,401);
const record={id:crypto.randomUUID(),type:'style',title:'Voce X + immagini Z',topic:'Nuovo racconto',notes:'Nota privata',refs:[{key:'a.mp4',title:'Voce X'},{key:'b.mp4',title:'Immagini Z'}],roles:{voice:{key:'a.mp4',note:'Voce lenta'},visual:{key:'b.mp4',note:'Colori caldi'}},settings:{format:'9:16'}};
const saved=await call('/api/workspace',{record});assert.equal(saved.status,200);assert.equal(saved.data.record.revision,1);
assert.equal((await call('/api/workspace',{record})).status,409,'A stale create cannot overwrite a saved style');
const updated=await call('/api/workspace',{record:{...record,title:'Stile aggiornato'},etag:saved.data.record.etag});assert.equal(updated.status,200);assert.equal(updated.data.record.revision,2);
assert.equal((await call('/api/workspace',{record,etag:saved.data.record.etag})).status,409);
assert.equal((await call('/api/workspace',{record:{...record,id:crypto.randomUUID(),roles:{voice:{key:'unselected.mp4'}}}})).status,400,'Unselected source must be rejected');
assert.equal((await call('/api/workspace')).data.items.length,1);
await bucket.put('a.mp4','{}');await bucket.put('b.mp4','{}');await bucket.put('catalog/manage.json',JSON.stringify({'a.mp4':{title:'Titolo personalizzato',favorite:true}}));
assert.equal((await call('/api/bulk',{action:'archive',keys:['a.mp4','missing.mp4']})).status,404);
assert.equal(JSON.parse(bucket.rows.get('catalog/manage.json').value)['a.mp4'].hidden,undefined,'Invalid batch must leave all existing records untouched');
const archived=await call('/api/bulk',{action:'archive',keys:['a.mp4','a.mp4','b.mp4']});assert.equal(archived.data.count,2);
let edits=JSON.parse(bucket.rows.get('catalog/manage.json').value);assert.equal(edits['a.mp4'].title,'Titolo personalizzato');assert.equal(edits['a.mp4'].favorite,true);assert.equal(edits['a.mp4'].hidden,true);assert(bucket.rows.has('a.mp4'),'Archiving must never delete the MP4');
assert.equal((await call('/api/bulk',{action:'restore',keys:['a.mp4','b.mp4']})).status,200);
edits=JSON.parse(bucket.rows.get('catalog/manage.json').value);assert.equal(edits['a.mp4'].hidden,false);
bucket.conflict=true;assert.equal((await call('/api/bulk',{action:'archive',keys:['a.mp4']})).status,409);assert.equal(JSON.parse(bucket.rows.get('catalog/manage.json').value)['a.mp4'].hidden,false,'Concurrent update must not be reported as saved');
console.log('Workspace checks passed: private access, style version conflicts, selected sources, atomic bulk validation, metadata preservation, reversible archive.');
