"""Daily production readiness and verified-delivery ledger. No model calls or publishing."""
from __future__ import annotations
import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from video_director_v13 import ROOT, read_json, write_json, check, probe_video, digest

POLICY=ROOT/'config/production_v15.json'
REVIEWS=('editorial','visual','audio','rights')

def today():return datetime.now(ZoneInfo('Europe/Rome')).date().isoformat()

def local(name):
    if not isinstance(name,str) or not name or Path(name).is_absolute():raise ValueError('Percorso relativo al repository richiesto')
    p=(ROOT/name).resolve()
    if not p.is_relative_to(ROOT.resolve()):raise ValueError('Percorso fuori progetto')
    if not p.is_file():raise ValueError('File non disponibile: '+name)
    return p

def valid_day(day):
    from datetime import date
    date.fromisoformat(day)
    return day

def ledger_or_empty(path):
    if not Path(path).exists():return {'schema':'production-ledger-v15','deliveries':[]}
    x=read_json(path)
    if not isinstance(x,dict) or x.get('schema')!='production-ledger-v15' or not isinstance(x.get('deliveries'),list):raise ValueError('Registro non valido')
    return x

def plan(queue,ledger,day):
    policy=read_json(POLICY);valid_day(day)
    if not isinstance(queue,dict) or queue.get('schema')!='production-queue-v15' or not isinstance(queue.get('items'),list):raise ValueError('Coda non valida')
    if not isinstance(ledger,dict) or ledger.get('schema')!='production-ledger-v15' or not isinstance(ledger.get('deliveries'),list):raise ValueError('Registro non valido')
    deliveries=ledger['deliveries']
    # A receipt remains valid only while the hashed final and recipe still exist.
    verified=[];stale=[]
    for receipt in deliveries:
        try:
            if not isinstance(receipt,dict) or any(not isinstance(receipt.get(k),str) or not receipt[k].strip() for k in ('item_id','content_key','day')):raise ValueError('Ricevuta incompleta')
            if any(receipt.get('reviews',{}).get(k,{}).get('status')!='passed' for k in REVIEWS):raise ValueError('Revisioni mancanti')
            if digest(local(receipt['video_file']))!=receipt['video_sha256'] or digest(local(receipt['recipe_file']))!=receipt['recipe_sha256']:raise ValueError('Hash cambiato')
            verified.append(receipt)
        except (ValueError,KeyError,OSError,TypeError,AttributeError):stale.append(receipt.get('item_id','unknown') if isinstance(receipt,dict) else 'unknown')
    completed_ids={r['item_id'] for r in verified};completed_keys={r['content_key'] for r in verified}
    day_receipts=[r for r in verified if r['day']==day]
    unique_today=len({r['video_sha256'] for r in day_receipts})
    target=policy['target_qualified_videos_per_day'];missing=max(0,target-unique_today)
    ready=[];blocked=[];seen_ids=set();seen_keys=set()
    for item in queue['items']:
        if not isinstance(item,dict):raise ValueError('Elemento coda non valido')
        ident=item.get('id');content=item.get('content_key')
        if not isinstance(ident,str) or not ident.strip() or ident in seen_ids:raise ValueError('ID mancante o duplicato')
        seen_ids.add(ident)
        if not isinstance(content,str) or not content.strip():raise ValueError('Identità editoriale richiesta')
        if ident in completed_ids or content in completed_keys:continue
        reason=[]
        if content in seen_keys:reason.append('Stesso contenuto già in coda: una variante non vale un video nuovo')
        seen_keys.add(content)
        if item.get('status')!='prepared':reason.append('Preparazione editoriale e asset ancora da completare')
        attempts=item.get('attempts',0)
        if type(attempts) is not int or attempts<0:raise ValueError('Tentativi non validi')
        if attempts>=policy['max_attempts_per_item']:reason.append('Tentativi esauriti: diagnosticare prima del riavvio')
        cost=item.get('new_paid_calls_required')
        if cost is not False:reason.append('Nuove chiamate a pagamento da quantificare o sostituire con cache verificata')
        try:
            preflight=check(local(item.get('project_file')))
            reason.extend(preflight['blockers'])
        except (ValueError,OSError,KeyError,TypeError,AttributeError) as exc:reason.append('Preflight: '+str(exc))
        row={**item,'blockers':reason}
        if reason:blocked.append(row)
        else:ready.append(row)
    slots=min(len(ready),missing+2 if missing else 0,policy['max_jobs_per_batch'])
    return {'schema':'production-batch-v15','day':day,'timezone':policy['timezone'],
      'target':target,'qualified_today':unique_today,'missing_to_target':missing,'ready':ready[:slots],
      'backlog_ready':len(ready)-slots,'blocked':blocked,'stale_receipts':stale,
      'max_parallel_renders':policy['max_parallel_renders'],'target_met':unique_today>=target,
      'autonomous_renderer_started':False,'note':'Questo comando verifica la coda. Non genera MP4 né certifica capacità giornaliera.'}

def record(ledger,receipt):
    """Agent supplies real review evidence after playback; structural checks are not AI vision."""
    for field in ('item_id','content_key','day','video_file','recipe_file'):
        if not isinstance(receipt.get(field),str) or not receipt[field].strip():raise ValueError('Campo consegna richiesto: '+field)
    valid_day(receipt['day'])
    reviews=receipt.get('reviews',{})
    if not isinstance(reviews,dict):raise ValueError('Revisioni non valide')
    for name in REVIEWS:
        review=reviews.get(name,{})
        if not isinstance(review,dict) or review.get('status')!='passed' or not isinstance(review.get('notes'),str) or not review['notes'].strip():raise ValueError('Revisione agente da completare: '+name)
    if not isinstance(ledger,dict) or ledger.get('schema')!='production-ledger-v15' or not isinstance(ledger.get('deliveries'),list):raise ValueError('Registro non valido')
    video=local(receipt['video_file']);recipe_file=local(receipt['recipe_file']);technical=probe_video(video)
    recipe=read_json(recipe_file)
    if recipe.get('schema')!='video-recipe-v13' or recipe.get('video',{}).get('sha256')!=digest(video):raise ValueError('Ricetta non corrispondente al video')
    for entry in [recipe.get('cover',{}),*recipe.get('sources',[])]:
        name=entry.get('file')
        if not isinstance(name,str) or Path(name).is_absolute():raise ValueError('Percorso nella ricetta non valido')
        asset=(recipe_file.parent/name).resolve()
        if not asset.is_relative_to(recipe_file.parent.resolve()) or not asset.is_file() or digest(asset)!=entry.get('sha256'):raise ValueError('Pacchetto ricetta incompleto o modificato')
    if any(r.get('item_id')==receipt['item_id'] or r.get('content_key')==receipt['content_key'] or r.get('video_sha256')==digest(video) for r in ledger['deliveries']):raise ValueError('Consegna già registrata: contenuto, ID o MP4 duplicato')
    clean={**receipt,'video_sha256':digest(video),'recipe_sha256':digest(recipe_file),'technical':technical,
           'review_basis':'agent_declaration_with_notes_not_automatic_semantic_certification'}
    return {**ledger,'deliveries':ledger['deliveries']+[clean]}

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('plan');p.add_argument('--queue',default='queue/production_v15.json');p.add_argument('--ledger',required=True);p.add_argument('--day',default=today());p.add_argument('--out',required=True)
    r=sub.add_parser('record');r.add_argument('--ledger',required=True);r.add_argument('--receipt',required=True)
    a=ap.parse_args();ledger=ledger_or_empty(a.ledger)
    if a.cmd=='plan':
        result=plan(read_json(a.queue),ledger,a.day);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
        write_json(out/'BATCH_V15.json',result)
        lines=[f"# Produzione {result['day']}",'',f"Obiettivo: {result['target']}; verificati nel registro: {result['qualified_today']}; mancanti: {result['missing_to_target']}.",f"Pronti nel lotto: {len(result['ready'])}; bloccati: {len(result['blocked'])}.",'',result['note']]
        for row in result['blocked']:lines+=['',row['id']+': '+'; '.join(row['blockers'])]
        (out/'BATCH_V15.md').write_text('\n'.join(lines)+'\n');print(lines[2]);print(lines[3])
    else:
        result=record(ledger,read_json(a.receipt));Path(a.ledger).parent.mkdir(parents=True,exist_ok=True);write_json(a.ledger,result)

if __name__=='__main__':main()
