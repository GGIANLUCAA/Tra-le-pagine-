"""Persistent batch executor for prepared, allowlisted render jobs. No paid providers."""
from __future__ import annotations
import argparse
import concurrent.futures
import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
from datetime import datetime, timezone
from pathlib import Path
import production_batch_v15 as batch
from production_adapter_v16 import ADAPTERS
from video_director_v13 import ROOT, read_json, write_json, digest, local_file, probe_video, linked_four_plan

SCHEMA='production-state-v16'
TERMINAL={'rendered_needs_review','qualified'}

def stamp():return datetime.now(timezone.utc).isoformat()

def inside(name,directory=False):
    if not isinstance(name,str) or not name or Path(name).is_absolute():raise ValueError('Percorso relativo richiesto')
    p=ROOT/name
    if p.is_symlink():raise ValueError('Non usare symlink come input')
    p=p.resolve()
    if not p.is_relative_to(ROOT.resolve()) or not (p.is_dir() if directory else p.is_file()):raise ValueError('Input locale mancante: '+name)
    return p

def tree_files(folder):
    files=[]
    for p in folder.rglob('*'):
        if p.is_symlink():raise ValueError('Symlink negli input non consentito')
        if p.is_file():files.append(p)
    return files

def inputs(job):
    if job.get('adapter') not in ADAPTERS:raise ValueError('Adapter non supportato')
    project_file=inside(job['project_file']);project=read_json(project_file)
    if project.get('format')!=ADAPTERS[job['adapter']]:raise ValueError('Adapter e formato diversi')
    files=[project_file]+[local_file(project_file.parent,a['file']) for a in project['assets']]
    if project.get('serial_mode') == 'artvision_4x1':
        # Include the one shared dossier in the fingerprint and staged repository.
        files.append(linked_four_plan(project_file, project.get('artvision_4x1_plan')))
    if project.get('script'):files.append(local_file(project_file.parent,project['script']))
    adapter=job['adapter']
    if adapter=='books_gemini_cache':
        slug=job.get('episode','')
        if not isinstance(slug,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,70}',slug):raise ValueError('Episodio non valido')
        files+=tree_files(inside('episodes/'+slug,True))
    elif adapter=='critico_v2_prepared':files += [inside(job[k]) for k in ('config_file','painting_file','music_file')]
    else:
        files += tree_files(inside(job['assets_dir'],True))
        if adapter=='cinema_v55_prepared':files.append(inside(job['cinema_plan_file']))
    if adapter not in ('cinema_v6_vangogh_prepared','cinema_v55_prepared'):
        folder=inside(job['voice_cache_dir'],True)
        files += [folder/name for name in ('VOCE.wav','VOICE_CACHE_V13.json','VOICE_PROFILE_V13.json','ALLINEAMENTO_VOCE.json') if (folder/name).is_file()]
        if not (folder/'VOCE.wav').is_file() or not (folder/'VOICE_CACHE_V13.json').is_file():raise ValueError('WAV e manifest Google richiesti')
    for p in files:
        if not p.resolve().is_relative_to(ROOT.resolve()) or p.is_symlink() or not p.is_file():raise ValueError('Input non locale o non valido')
    return sorted(set(files))

def fingerprint(job,files):
    # Queue status and retry counters are operational, not creative input changes.
    value={k:v for k,v in job.items() if k not in ('attempts','status','blockers')}
    value['inputs']=[(p.relative_to(ROOT).as_posix(),digest(p)) for p in files]
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def tracked_files():
    names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    return [ROOT/n for n in names if n and (ROOT/n).is_file()]

def stage_repository(stage,files):
    for src in set(tracked_files()+files):
        if src.is_symlink() or not src.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Sorgente fuori repository')
        relative=src.relative_to(ROOT)
        if any(part in ('.git','.env','node_modules') for part in relative.parts):continue
        target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,target)

def spawn(stage,job_file,out,log,timeout):
    env={k:os.environ[k] for k in ('PATH','HOME','LANG','LC_ALL','TMPDIR') if k in os.environ}
    env.update({'PYTHONUNBUFFERED':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'1'})
    args=[sys.executable,'src/production_adapter_v16.py','--job',str(job_file),'--out',str(out)]
    with log.open('ab') as stream:
        process=subprocess.Popen(args,cwd=stage,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=process.wait(timeout=timeout)
        except BaseException:
            with contextlib.suppress(ProcessLookupError):os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(ProcessLookupError):os.killpg(process.pid,signal.SIGKILL)
                process.wait()
            raise
    if code:raise RuntimeError('Adapter fallito, exit '+str(code)+'; controllare il log del lavoro')

def review_kit(video,out):
    """Sample frames + full mixed audio; not a completed artistic review."""
    from PIL import Image, ImageDraw
    duration=probe_video(video)['duration_seconds'];frames=[]
    for n in range(8):
        t=max(0,duration*n/8);target=out/f'REVIEW_FRAME_{n:02}.jpg'
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(max(0,t)),'-i',str(video),'-frames:v','1','-vf','scale=270:-2',str(target)],check=True,timeout=90)
        with Image.open(target) as im:
            tile=Image.new('RGB',(270,510),'#111827');im.thumbnail((270,480));tile.paste(im,((270-im.width)//2,0));ImageDraw.Draw(tile).text((8,488),f'{t:.1f}s',fill='white');frames.append(tile)
    sheet=Image.new('RGB',(1080,1020),'#111827')
    for n,im in enumerate(frames):sheet.paste(im,((n%4)*270,(n//4)*510))
    sheet.save(out/'REVIEW_CONTACT.jpg',quality=88)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(video),'-vn','-c:a','libmp3lame','-b:a','96k',str(out/'REVIEW_AUDIO.mp3')],check=True,timeout=120)
    (out/'REVIEW_REQUIRED.txt').write_text('Campioni visivi e audio completo per la revisione dell’agente. Non certificano pertinenza di tutte le scene. Visione completa e controllo fonti ancora richiesti.\n')

def valid_result(row):
    try:
        return row.get('status') in TERMINAL and digest(inside(row['video_file']))==row['video_sha256'] and digest(inside(row['recipe_file']))==row['recipe_sha256']
    except (ValueError,OSError,KeyError,TypeError):return False

def load_state(path,fallback=None):
    values=[]
    for p in (path,fallback):
        if p and Path(p).exists():
            x=read_json(p)
            if not isinstance(x,dict) or x.get('schema')!=SCHEMA or not isinstance(x.get('jobs'),dict):raise ValueError('Stato non valido')
            values.append(x)
    state={'schema':SCHEMA,'jobs':{}}
    def age(r):return (r.get('qualified_utc') or r.get('finished_utc') or r.get('started_utc') or '',r.get('attempts',0))
    for x in values:
        for ident,row in x['jobs'].items():
            if not isinstance(row,dict):raise ValueError('Stato lavoro non valido')
            if ident not in state['jobs'] or age(row)>age(state['jobs'][ident]):state['jobs'][ident]=row
    return state

def run(queue_file,workspace,fallback_state=None,timeout=7200):
    workspace=Path(workspace).resolve()
    if not workspace.is_relative_to(ROOT.resolve()):raise ValueError('Workspace richiesto nel repository')
    workspace.mkdir(parents=True,exist_ok=True)
    with (workspace/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return run_locked(queue_file,workspace,fallback_state,timeout)

def run_locked(queue_file,workspace,fallback_state,timeout):
    statefile=workspace/'state.json';state=load_state(statefile,fallback_state);mutex=threading.Lock()
    policy=read_json(batch.POLICY);max_attempts=policy['max_attempts_per_item']
    def save():state['updated_utc']=stamp();write_json(statefile,state)
    ledger=batch.ledger_or_empty(workspace/'ledger.json')
    queue=read_json(queue_file);skipped=[];blocked=[];candidate_items=[]
    for job in queue['items']:
        old=state['jobs'].get(job.get('id'),{})
        if old.get('status') in TERMINAL:
            try:
                sig=fingerprint(job,inputs(job))
                if sig!=old.get('input_sha256'):raise ValueError('Input cambiati: creare una revisione esplicita')
                if not valid_result(old):raise ValueError('Master precedente mancante/modificato: recuperare il checkpoint')
                skipped.append(job['id'])
            except (ValueError,OSError,KeyError) as exc:blocked.append({'id':job.get('id'),'reason':str(exc)})
        else:candidate_items.append(job)
    report=batch.plan({**queue,'items':candidate_items},ledger,batch.today());pending=[]
    awaiting_review=sum(v.get('status')=='rendered_needs_review' for v in state['jobs'].values())
    available_slots=max(0,policy['max_jobs_per_batch']-awaiting_review)
    for job in report['ready']:
        ident=job['id']
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,70}',ident):blocked.append({'id':ident,'reason':'ID non utilizzabile come cartella'});continue
        try:files=inputs(job);sig=fingerprint(job,files)
        except Exception as exc:blocked.append({'id':ident,'reason':str(exc)});continue
        old=state['jobs'].get(ident,{})
        if old and old.get('input_sha256')!=sig:
            blocked.append({'id':ident,'reason':'Input cambiati: usare una nuova revisione esplicita, senza sovrascrivere il precedente lavoro'});continue
        if old.get('status') in TERMINAL:
            if valid_result(old):skipped.append(ident)
            else:blocked.append({'id':ident,'reason':'Master precedente non disponibile o cambiato: recuperare il pacchetto, non rigenerare silenziosamente'})
            continue
        if any(r.get('content_key')==job['content_key'] and r.get('status') in TERMINAL for r in state['jobs'].values()):
            blocked.append({'id':ident,'reason':'Contenuto già renderizzato con altro ID'});continue
        if max(old.get('attempts',0),job.get('attempts',0))>=max_attempts:blocked.append({'id':ident,'reason':'Tentativi esauriti: diagnosi richiesta'});continue
        if len(pending)>=available_slots:
            blocked.append({'id':ident,'reason':'Completare prima le revisioni dei master in attesa, per non accumulare render senza controllo'});continue
        pending.append((job,files,sig))
    def work(entry):
        job,files,sig=entry;ident=job['id'];folder=workspace/'jobs'/ident;stage=folder/'repo';out=stage/'output'/'final';folder.mkdir(parents=True,exist_ok=True)
        with mutex:
            old=state['jobs'].get(ident,{})
            state['jobs'][ident]={'status':'running','input_sha256':sig,'content_key':job['content_key'],'attempts':max(old.get('attempts',0),job.get('attempts',0))+1,'started_utc':stamp(),'workflow_run_id':os.getenv('GITHUB_RUN_ID')};save()
        try:
            stage_repository(stage,files);jobfile=folder/'job.json';write_json(jobfile,job)
            spawn(stage,jobfile,out,folder/'render.log',timeout)
            result=read_json(out/'ADAPTER_RESULT_V16.json')
            video=Path(result['video']).resolve();recipe=Path(result['recipe']).resolve()
            if not video.is_relative_to(out) or not recipe.is_relative_to(out):raise ValueError('Output fuori dalla cartella assegnata')
            info=probe_video(video);rec=read_json(recipe)
            if rec.get('schema')!='video-recipe-v13' or rec.get('video',{}).get('sha256')!=digest(video):raise ValueError('Ricetta e master non corrispondenti')
            review_kit(video,out)
            # V17 is additive: its failure never deletes a master or changes V16 qualification.
            try:
                from quality_director_v17 import inspect as quality_inspect_v17
                quality_inspect_v17(video=video, project=stage/job['project_file'], out=out)
            except Exception as qa_error:
                (out/'QUALITY_V17_ERROR.txt').write_text(
                    type(qa_error).__name__ + ': ' + str(qa_error)[:500] + '\n',
                    encoding='utf-8')
            # Standard creativo V21 per TUTTI i nuovi master V16: senza toccare
            # film/preset/cover. Un errore produce un blocco di qualifica, non distrugge l'MP4.
            creative_package=None
            try:
                from creative_director_v21 import write_package
                write_package(read_json(stage/job['project_file']), out, video=video)
                creative_package=out/'CREATIVE_PACKAGE_V21.json'
            except Exception as creative_error:
                (out/'CREATIVE_V21_ERROR.txt').write_text(
                    type(creative_error).__name__ + ': ' + str(creative_error)[:500] + '\n',
                    encoding='utf-8')
            with mutex:
                state['jobs'][ident].update({'status':'rendered_needs_review','finished_utc':stamp(),'video_file':video.relative_to(ROOT).as_posix(),'video_sha256':digest(video),'recipe_file':recipe.relative_to(ROOT).as_posix(),'recipe_sha256':digest(recipe),'technical':info,'review':'pending_agent_playback_and_sources','creative_v21_required':True,'creative_v21_file':creative_package.relative_to(ROOT).as_posix() if creative_package else None,'creative_v21_sha256':digest(creative_package) if creative_package else None,'creative_v21_status':'needs_editorial_review' if creative_package else 'packaging_failed'});save()
        except Exception as exc:
            with mutex:
                state['jobs'][ident].update({'status':'failed','finished_utc':stamp(),'error':type(exc).__name__+': '+str(exc)[:600]});save()
    save()
    with concurrent.futures.ThreadPoolExecutor(max_workers=policy['max_parallel_renders']) as pool:list(pool.map(work,pending))
    summary={'schema':'runner-report-v16','day':report['day'],'target':report['target'],'qualified_today':report['qualified_today'],'started':len(pending),'awaiting_agent_review':sum(v.get('status')=='rendered_needs_review' for v in state['jobs'].values()),'reused_without_render':skipped,'queue_blocked':report['blocked'],'runner_blocked':blocked,'states':{k:v['status'] for k,v in state['jobs'].items()},'paid_provider_calls_enabled':False,'social_publication':False}
    write_json(workspace/'RUN_REPORT_V16.json',summary)
    return summary

def pack(workspace,target):
    workspace=Path(workspace).resolve();target=Path(target).resolve()
    if target.is_relative_to(workspace):raise ValueError('Pacchetto esterno al workspace richiesto')
    target.parent.mkdir(parents=True,exist_ok=True)
    # MP4 are nested in a tar file, not exposed to the existing automatic MP4 importer.
    with tarfile.open(target,'w') as archive:
        for p in workspace.rglob('*'):
            if p.is_symlink():raise ValueError('Symlink nel workspace')
            if p.is_file() and p.name!='runner.lock':archive.add(p,arcname=p.relative_to(workspace),recursive=False)

def restore(source,workspace):
    workspace=Path(workspace).resolve();workspace.mkdir(parents=True,exist_ok=True)
    with tarfile.open(source,'r') as archive:
        for m in archive.getmembers():
            target=(workspace/m.name).resolve()
            if not target.is_relative_to(workspace) or not m.isfile():raise ValueError('Pacchetto non valido: percorso o tipo speciale')
        archive.extractall(workspace,filter='data')

def qualify(workspace,ident,review_file):
    workspace=Path(workspace);statefile=workspace/'state.json'
    # Share the execution lock: a review cannot race with an active render.
    with (workspace/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);state=load_state(statefile);row=state['jobs'][ident]
        if not valid_result(row):raise ValueError('Master non disponibile o modificato')
        if row.get('creative_v21_required'):
            package_name=row.get('creative_v21_file')
            if not package_name or not row.get('creative_v21_sha256'):
                raise ValueError('Creative Director V21 assente: completare packaging e revisione')
            package=inside(package_name)
            if digest(package)!=row['creative_v21_sha256']:
                raise ValueError('Pacchetto creativo V21 mancante o alterato')
            creative=read_json(package)
            if creative.get('schema')!='creative-director-v21' or creative.get('video_sha256')!=row['video_sha256']:
                raise ValueError('Creative V21 non corrisponde al master corrente')
            # Il V21 non dichiara MAI da solo la pubblicazione pronta.
            # La qualifica tecnica avviene dopo revisione editoriale V16 gia prevista.

        receipt={'item_id':ident,'content_key':row['content_key'],'day':batch.today(),'video_file':row['video_file'],'recipe_file':row['recipe_file'],'reviews':(lambda x:x.get('reviews',x))(read_json(review_file))}
        ledger_path=workspace/'ledger.json';ledger=batch.record(batch.ledger_or_empty(ledger_path),receipt);write_json(ledger_path,ledger)
        row['status']='qualified';row['qualified_day']=receipt['day'];row['qualified_utc']=stamp();row['review']='passed_agent_declaration';write_json(statefile,state)

def apply_reviews(workspace,folder,fallback_state='queue/runner_state_v16.json'):
    workspace=Path(workspace);workspace.mkdir(parents=True,exist_ok=True)
    statefile=workspace/'state.json'
    with (workspace/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);state=load_state(statefile,fallback_state);write_json(statefile,state)
    result=[]
    for file in sorted(Path(folder).glob('*.json')):
        review=read_json(file);ident=review.get('item_id');row=state['jobs'].get(ident,{})
        if row.get('status')=='qualified':continue
        if row.get('video_sha256')!=review.get('video_sha256') or row.get('recipe_sha256')!=review.get('recipe_sha256'):
            result.append({'id':ident,'status':'not_applied','reason':'Revisione non legata agli hash del master corrente'});continue
        try:
            qualify(workspace,ident,file)
            result.append({'id':ident,'status':'qualified'})
            state=load_state(statefile)
        except (ValueError,OSError,KeyError,TypeError) as exc:result.append({'id':ident,'status':'not_applied','reason':str(exc)})
    write_json(workspace/'REVIEW_REPORT_V16.json',result)
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    runp=sub.add_parser('run');runp.add_argument('--queue',default='queue/production_v15.json');runp.add_argument('--workspace',default='output/production-v16');runp.add_argument('--fallback-state',default='queue/runner_state_v16.json')
    for name in ('pack','restore'):
        p=sub.add_parser(name);p.add_argument('--workspace',default='output/production-v16');p.add_argument('--archive',required=True)
    rp=sub.add_parser('reviews');rp.add_argument('--workspace',default='output/production-v16');rp.add_argument('--folder',default='queue/reviews_v16')
    p=sub.add_parser('qualify');p.add_argument('--workspace',default='output/production-v16');p.add_argument('--id',required=True);p.add_argument('--reviews',required=True)
    a=ap.parse_args()
    if a.cmd=='run':print(json.dumps(run(a.queue,a.workspace,a.fallback_state),ensure_ascii=False,indent=2))
    elif a.cmd=='pack':pack(a.workspace,a.archive)
    elif a.cmd=='restore':restore(a.archive,a.workspace)
    elif a.cmd=='reviews':print(json.dumps(apply_reviews(a.workspace,a.folder),ensure_ascii=False,indent=2))
    else:qualify(a.workspace,a.id,a.reviews)

if __name__=='__main__':main()
