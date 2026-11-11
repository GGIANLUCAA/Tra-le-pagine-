#!/usr/bin/env python3
"""Narrative reveals V3: offline editorial plan, no AI, no media alteration."""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess
from pathlib import Path

INTENTS = {'hook','introduzione','scoperta','indizio','meraviglia','azione',
           'dialogo','emozione','spiegazione','svolta','climax','finale','passaggio'}
EFFECTS = {'none','stroke_draw','object_stagger','pigment_bloom','director_mix','color_accent'}
MODES = {'illustration','authentic_art','documentary','video'}

def audio_information(path):
    if not path.is_file(): raise ValueError('File audio mancante')
    p=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
        '-of','default=noprint_wrappers=1:nokey=1',str(path)],
        capture_output=True,text=True,check=True)
    duration=float(p.stdout.strip())
    if not math.isfinite(duration) or duration<=0: raise ValueError('Durata audio errata')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for piece in iter(lambda:f.read(1024*1024),b''): h.update(piece)
    return {'path':str(path),'sha256':h.hexdigest(),'duration_seconds':round(duration,3)}

def number(v,name):
    if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v):
        raise ValueError(name+': numero non valido')
    return float(v)

def roi_check(box):
    if not isinstance(box,list) or len(box)!=4:return False
    try:x,y,w,h=[number(z,'roi') for z in box]
    except ValueError:return False
    return 0<=x<1 and 0<=y<1 and 0<w<=1-x+1e-6 and 0<h<=1-y+1e-6

def select_effect(s,previous,fmt):
    if fmt.startswith('artvision') or s.get('visual_mode','illustration')!='illustration':
        return 'none','Conservare opere e documenti autentici.'
    if s.get('visual_review') not in ('approved','editorial_mock'):
        return 'none','Immagine non ancora verificata.'
    override=s.get('effect_override')
    if override is not None:
        if override not in EFFECTS:raise ValueError('Effetto editoriale non valido')
        if override!='none' and s.get('effect_target','full')!='full' and not roi_check(s.get('focus_roi')):
            return 'none','Bersaglio mancante: fallback sicuro.'
        return override,'Scelta motivata dell’editor, non obbligo globale.'
    intent=s['intent']; has_roi=roi_check(s.get('focus_roi'))
    if intent in {'hook','azione','dialogo','emozione','spiegazione','climax','finale','passaggio'}:
        return 'none','Leggibilità immediata o pausa emotiva.'
    if intent=='indizio':
        effect='color_accent' if has_roi else 'none'
    elif intent=='scoperta':
        effect='object_stagger' if has_roi else 'stroke_draw'
    elif intent=='meraviglia':effect='pigment_bloom'
    elif intent=='introduzione':effect='director_mix'
    elif intent=='svolta':effect='color_accent' if has_roi else 'none'
    else:effect='none'
    if effect!='none' and previous==effect:
        return 'none','Tecnica consecutiva ripetuta senza diversa motivazione.'
    return effect,('Funzione narrativa e oggetto scelto.' if effect!='none' else 'Nessun effetto necessario.')

def plan(story,audio=None):
    if story.get('schema')!='narrative-reveal-story-v3':raise ValueError('Schema non riconosciuto')
    fmt=story.get('format','libri')
    if fmt not in ('libri','artvision_cinema','artvision_critico','controluce'):
        raise ValueError('Formato non compatibile')
    scenes=story.get('scenes')
    if not isinstance(scenes,list) or not scenes:raise ValueError('Storyboard vuoto')
    evidence=audio_information(Path(audio)) if audio else None
    rows=[]; previous='none'; end_previous=0.
    for index,s in enumerate(scenes):
        if not isinstance(s,dict):raise ValueError('Scena non valida')
        sid=str(s.get('id',f'scena_{index+1:02}')).strip()
        if not sid or any(row['id']==sid for row in rows):raise ValueError('ID scena duplicato')
        start=number(s.get('start_s'),sid+' start'); end=number(s.get('end_s'),sid+' end')
        if start<0 or end<=start or (index and start<end_previous-1e-6):
            raise ValueError('Timeline non ordinata: '+sid)
        if evidence and end>evidence['duration_seconds']+.20:
            raise ValueError('Fine scena oltre la voce: '+sid)
        end_previous=end; duration=end-start
        if s.get('intent') not in INTENTS:raise ValueError('Intento obbligatorio: '+sid)
        if s.get('visual_mode','illustration') not in MODES:raise ValueError('Tipo immagine non valido')
        if not str(s.get('narration_anchor','')).strip() or not str(s.get('visual_reason','')).strip():
            raise ValueError('Mancano frase o motivazione: '+sid)
        anchor=number(s.get('anchor_offset_s',0),sid+' anchor')
        if not 0<=anchor<=duration:raise ValueError('Frase fuori scena: '+sid)
        roi=s.get('focus_roi')
        if roi is not None and not roi_check(roi):raise ValueError('ROI fuori immagine: '+sid)
        effect,reason=select_effect(s,previous,fmt)
        if effect!='none' and duration<2:
            effect,reason='none','Scena troppo breve per rivelazione leggibile.'
        target=s.get('effect_target')
        if target is None:target='roi' if effect in ('color_accent','object_stagger') and roi_check(roi) else 'full'
        if target not in ('full','roi'):raise ValueError('Tipo bersaglio non valido')
        if effect!='none' and target=='roi' and not roi_check(roi):
            effect,reason='none','ROI mancante: non indovinare oggetto.'
        if effect!='none':
            hold=min(max(1.,duration*.30),duration*.50)
            requested=s.get('effect_duration_s')
            requested=number(requested,'durata effetto') if requested is not None else min(2.3,max(.65,duration*.24))
            eff_dur=max(.45,min(requested,duration-hold))
            eff_start=max(0.,min(anchor-.22,duration-hold-eff_dur))
            if target=='full':eff_start=0. # Never late whole-frame blank flash
            hold_after=duration-eff_start-eff_dur
            previous=effect
        else:
            eff_start=0.;eff_dur=0.;hold_after=duration;previous='none'
        ready=(s.get('rights_review')=='approved' and s.get('visual_review')=='approved')
        rows.append({'id':sid,'start_s':round(start,3),'end_s':round(end,3),
            'duration_s':round(duration,3),'narration_anchor':s['narration_anchor'],
            'anchor_offset_s':round(anchor,3),'intent':s['intent'],
            'visual_reason':s['visual_reason'],'visual_mode':s.get('visual_mode','illustration'),
            'image':s.get('image',''),'source_reference':s.get('source_reference',''),
            'rights_review':s.get('rights_review'),'visual_review':s.get('visual_review'),
            'effect':effect,'effect_reason':reason,'effect_target':target,'focus_roi':roi,
            'effect_start_s':round(eff_start,3),'effect_duration_s':round(eff_dur,3),
            'visible_hold_s':round(hold_after,3),'camera':'locked',
            'rights_and_visuals_ready':ready,'needs_semantic_review':True})
    if evidence and abs(end_previous-evidence['duration_seconds'])>.30:
        raise ValueError('I cue non coprono la voce: verificare la durata effettiva')
    gaps=[round(b['start_s']-a['end_s'],3) for a,b in zip(rows,rows[1:])
          if b['start_s']-a['end_s']>.15]
    return {'schema':'narrative-reveal-plan-v3','status':'preview_only_needs_artistic_review',
      'format':fmt,'story':story.get('title',''),'audio_evidence':evidence,
      'timing_assessment':('audio_duration_checked_cues_need_listening' if evidence
                           else 'estimated_not_audio_synchronized'),
      'can_claim_voice_sync':False,'scene_gaps_s':gaps,
      'rights_and_visuals_reviewed':all(r['rights_and_visuals_ready'] for r in rows),
      'effect_count':sum(r['effect']!='none' for r in rows),'api_calls':0,
      'master_modified':False,'autopublish':False,'global_effect_rule':False,'scenes':rows}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--story',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--audio',type=Path)
    args=ap.parse_args()
    if args.out.exists():ap.error('Non sovrascrivere i piani esistenti')
    result=plan(json.loads(args.story.read_text(encoding='utf-8')),args.audio)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'plan':str(args.out),'scenes':len(result['scenes']),
         'effects':result['effect_count'],'timing':result['timing_assessment']},ensure_ascii=False))

if __name__=='__main__':main()
