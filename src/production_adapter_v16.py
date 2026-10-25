"""Allowlisted, offline adapters for already prepared assets. No paid API fallback."""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from video_director_v13 import ROOT, capture, local_file
from editorial_rules import validate as validate_editorial, POLICY

ADAPTERS={'books_gemini_cache':'libri','critico_v2_prepared':'artvision_critico','cinema_v6_vangogh_prepared':'artvision_cinema'}

def path(name, directory=False):
    if not isinstance(name,str) or not name or Path(name).is_absolute():raise ValueError('Percorso relativo richiesto')
    p=(ROOT/name).resolve()
    if not p.is_relative_to(ROOT.resolve()) or not (p.is_dir() if directory else p.is_file()):raise ValueError('Input non disponibile nel progetto: '+name)
    return p

def cache(script,source,out):
    from gemini_voice import _cached_audio, _valid_timing, sentences, SAMPLE_RATE
    source=path(source,True)
    cached=_cached_audio(script,source)
    if cached is None:raise ValueError('Cache voce Google assente, alterata o diversa dal copione; nessuna chiamata acquistata')
    audio,manifest=cached
    if not _valid_timing(manifest.get('timed'),sentences(script),len(audio)/SAMPLE_RATE) or not isinstance(manifest.get('alignment'),dict):raise ValueError('Allineamento cache incompleto: prepararlo prima del render, senza fallback automatici')
    out.mkdir(parents=True,exist_ok=True)
    for name in ('VOCE.wav','VOICE_CACHE_V13.json','VOICE_PROFILE_V13.json','ALLINEAMENTO_VOCE.json'):
        f=source/name
        if f.is_file():shutil.copy2(f,out/name)

def execute(job,out):
    adapter=job.get('adapter')
    if adapter not in ADAPTERS:raise ValueError('Adapter non supportato')
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    # A prepared adapter cannot accidentally activate a provider or Edge fallback.
    os.environ.pop('GEMINI_API_KEY',None)
    project_file=path(job['project_file']);project=json.loads(project_file.read_text())
    if project['format']!=ADAPTERS[adapter]:raise ValueError('Adapter e formato non corrispondenti')
    editorial_errors, _ = validate_editorial(project)
    if editorial_errors:raise ValueError('; '.join(editorial_errors))
    sources=[project_file,Path(__file__).resolve()]
    if project.get('editorial_contract'):sources.append(POLICY)
    for asset in project['assets']:
        sources.append(local_file(project_file.parent,asset['file']))
    approved={local_file(project_file.parent,a['file']) for a in project['assets']}
    if adapter=='books_gemini_cache':
        slug=job.get('episode','')
        if not isinstance(slug,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,70}',slug):raise ValueError('Episodio non valido')
        ep=path('episodes/'+slug,True)
        if (ep/'testo.txt').read_text().strip()!=local_file(project_file.parent,project['script']).read_text().strip():raise ValueError('Copione del brief diverso dal renderer')
        actual_visuals=[ep/'scene_premium.zip'] if (ep/'scene_premium.zip').is_file() else [p for p in (ep/'images').glob('scena_*.jpg') if p.is_file()]
        if not actual_visuals or any(p.resolve() not in approved for p in actual_visuals):raise ValueError('Le immagini/ZIP effettivi del renderer devono essere nel preflight approvato')
        subprocess.run([sys.executable,'src/episode_v3.py','--episode',slug],cwd=ROOT,check=True)
        cache((ep/'testo.txt').read_text(),job['voice_cache_dir'],out)
        subprocess.run([sys.executable,'src/regia_narrativa_v12.py','--episode',str(ep)],cwd=ROOT,check=True)
        subprocess.run([sys.executable,'src/render.py','--episode',str(ep),'--engine','gemini','--effects',job.get('effects','off'),'--out',str(out)],cwd=ROOT,check=True)
        subprocess.run([sys.executable,'src/episode_v3.py','--episode',slug,'--out',str(out),'--post'],cwd=ROOT,check=True)
        videos=list(out.glob('TRA_LE_PAGINE_EP*.mp4'))
        if len(videos)!=1:raise ValueError('Atteso un solo master libro')
        video,cover=videos[0],out/'COPERTINA_SERIE.jpg'
        sources += [p for p in ep.rglob('*') if p.is_file()]
    elif adapter=='critico_v2_prepared':
        sys.path.insert(0,str(ROOT/'modules/artvision_critico/production_series'))
        sys.path.insert(0,str(ROOT/'modules/artvision_critico'))
        import render_series_v2 as series
        from render_dali import audio_gemini
        import cv2
        cfgfile=path(job['config_file']);cfg=json.loads(cfgfile.read_text())
        if not isinstance(cfg.get('beats'),list) or not cfg['beats']:raise ValueError('Critico richiede beat curati e pertinenti al copione')
        if not isinstance(cfg.get('id'),str) or not re.fullmatch(r'[a-z0-9_-]{1,70}',cfg['id']):raise ValueError('ID configurazione Critico non valido')
        script='\n\n'.join(b['speech'] for b in cfg['beats'])
        if script.strip()!=local_file(project_file.parent,project['script']).read_text().strip():raise ValueError('Copione del brief diverso dai beat Critico')
        painting=path(job['painting_file']);music=path(job['music_file'])
        if painting not in approved or music not in approved:raise ValueError('Quadro e musica effettivi devono essere nel preflight approvato')
        from PIL import Image
        with Image.open(painting) as im:series.check_image(cfg,im)
        cache(script,job['voice_cache_dir'],out)
        voice,sec,bounds,engine=audio_gemini(cfg['beats'],out)
        series.produce(cfg,cv2.imread(str(painting)),{'file':str(painting),'sha256':__import__('hashlib').sha256(painting.read_bytes()).hexdigest()},voice,sec,bounds,engine,music,{'status':'prepared_local_asset_reviewed_in_project'},out)
        rights={a['file']:{'source':a['source'],'rights':a['rights']} for a in project['assets']}
        (out/'DIRITTI_E_FONTI.txt').write_text('Fonti e diritti del pacchetto preparato, da verificare per la destinazione. Nessuna licenza dedotta dal nome del renderer.\n'+json.dumps(rights,ensure_ascii=False,indent=2)+'\n')
        video=out/('ARTVISION_'+cfg['id'].upper()+'.mp4');cover=out/'COPERTINA.jpg'
        sources += [cfgfile,painting,music,ROOT/'modules/artvision_critico/production_series/render_series_v2.py']
    else:
        if job.get('artist')!='Vincent van Gogh':raise ValueError('Questo adapter usa solo la regia Van Gogh V6; altri artisti richiedono un adapter specifico')
        assets=path(job['assets_dir'],True)
        if not (assets/'music_rights.json').is_file():raise ValueError('Provenienza musica V6 mancante')
        # Legacy projects retain their historic duration; new briefs carry a motivated value.
        duration = math.ceil(project.get('editorial_plan', {}).get('duration_seconds', 150))
        if duration < 4:raise ValueError('Il renderer storico Van Gogh richiede almeno 4 secondi per le dissolvenze audio; scegliere un motore adatto alla durata richiesta')
        subprocess.run([sys.executable,'modules/artvision/director_cinema_v6.py','--assets',str(assets),'--out',str(out),'--duration',str(duration)],cwd=ROOT,check=True)
        video=out/'ARTVISION_VAN_GOGH_CINEMA_V6.mp4';cover=out/'COPERTINA_CINEMA_V6.jpg'
        sources += [p for p in assets.rglob('*') if p.is_file()]
        sources += [ROOT/'modules/artvision/director_cinema_v6.py']
    sources += [p for p in out.iterdir() if p.is_file() and p.suffix.lower() in ('.json','.txt','.wav') and p.name not in ('VIDEO_RECIPE_V13.json','ADAPTER_RESULT_V16.json')]
    recipe=capture(project['format'],project['topic'],video,cover,out,sources)
    # Reuse a single recipe so later verification can identify the exact final.
    result={'schema':'adapter-result-v16','video':str(video),'cover':str(cover),'recipe':str(out/'VIDEO_RECIPE_V13.json'),'video_sha256':recipe['video']['sha256'],'status':'rendered_needs_review'}
    (out/'ADAPTER_RESULT_V16.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--job',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    execute(json.loads(Path(a.job).read_text()),a.out)
