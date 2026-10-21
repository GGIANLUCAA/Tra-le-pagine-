"""Capacity-aware editorial queue. Plans work; never renders, pays or publishes."""
from __future__ import annotations
import argparse
import json
import math
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from video_director_v13 import ROOT, get_format, READY, write_json

POLICY = ROOT / 'config/creator_growth_v14.json'

def text(value):
    return isinstance(value, str) and bool(value.strip())

def positive(value):
    return type(value) in (int,float) and math.isfinite(value) and value > 0

def key(value):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(c)).split())

def plan(data, start, weekly_minutes=None, weeks=None):
    policy=json.loads(POLICY.read_text())
    start=date.fromisoformat(start)
    weeks=policy['planning_weeks'] if weeks is None else weeks
    if type(weeks) is not int or not 1<=weeks<=12:
        raise ValueError('Orizzonte da 1 a 12 settimane')
    capacity=policy['provisional_weekly_minutes'] if weekly_minutes is None else weekly_minutes
    if not positive(capacity):
        raise ValueError('Tempo settimanale positivo obbligatorio')
    review=policy['review_minutes_per_week']
    if capacity<=review:
        raise ValueError('Il budget deve includere tempo oltre alla revisione settimanale')
    if not isinstance(data,dict) or data.get('schema')!='creator-ideas-v14' or not isinstance(data.get('ideas'),list):
        raise ValueError('Schema idee non valido')
    backlog, deferred, seen_ids, seen_topics = [], [], set(), set()
    for row in data['ideas']:
        if not isinstance(row,dict):raise ValueError('Idea non valida')
        for field in ('id','topic','format','viewer_promise','original_angle','opening','next_episode'):
            if not text(row.get(field)):raise ValueError('Campo idea obbligatorio: '+field)
        if row['id'] in seen_ids:raise ValueError('ID idea duplicato')
        seen_ids.add(row['id'])
        fmt=get_format(row['format'])
        reason=None
        if row['format'] not in policy['active_formats']:reason='Formato fuori dal ciclo principale: mantenere come laboratorio/vetrina'
        elif fmt['status'] not in READY:reason='Motore non pronto: recuperare sorgenti'
        experiment=row.get('experiment')
        if not isinstance(experiment,dict) or experiment.get('variable') not in policy['experiment_variables'] or not text(experiment.get('hypothesis')) or not text(experiment.get('measure')):
            raise ValueError('Una variabile, ipotesi e misura richieste per ogni idea')
        topic=(row['format'],key(row['topic']),key(row['original_angle']))
        if topic in seen_topics:reason='Argomento e angolo già in coda: evitare duplicazione meccanica'
        seen_topics.add(topic)
        estimate=row.get('estimated_minutes')
        if not positive(estimate):reason='Stimare il tempo prima di occupare uno slot'
        elif estimate+review>capacity:reason='Non entra nella capacità settimanale: ridurre lavorazione o rinviare'
        if reason:
            deferred.append({'id':row['id'],'topic':row['topic'],'reason':reason});continue
        ready=all(row.get(k) is True for k in ('sources_checked','rights_checked','visual_plan_checked'))
        backlog.append({**row,'stage':'ready_for_preflight' if ready else 'research_and_preparation',
                        'next_action':'Creare scheda V13 e fare preflight' if ready else 'Controllare il catalogo e recuperare i materiali già riusciti; verificare fonti, diritti e storyboard prima di generare' ,
                        'semantic_accuracy_certified':False})
    calendar=[]
    for n in range(weeks):
        remaining=capacity-review;selected=[]
        for candidate in list(backlog):
            if len(selected)>=policy['max_videos_per_week']:break
            if candidate['estimated_minutes']<=remaining:
                selected.append(candidate);backlog.remove(candidate);remaining-=candidate['estimated_minutes']
        calendar.append({'week':n+1,'from':(start+timedelta(days=n*7)).isoformat(),
            'to':(start+timedelta(days=n*7+6)).isoformat(),'review_minutes':review,
            'estimated_production_minutes':sum(x['estimated_minutes'] for x in selected),
            'remaining_minutes':remaining,'ideas':selected,'publication_scheduled':False})
    deferred += [{'id':r['id'],'topic':r['topic'],'reason':'Capacità o orizzonte esaurito; conservata in backlog'} for r in backlog]
    return {'schema':'creator-plan-v14','mode':policy['mode'],'weekly_minutes':capacity,
            'capacity_source':'provisional_assumption' if weekly_minutes is None else 'provided_budget_not_measured_time',
            'calendar':calendar,'deferred':deferred,'monetization_campaigns':False,
            'note':'Stime di lavoro, non date di pubblicazione. Ordine editoriale delle idee, non previsione di viralità. Ricerca pendente non autorizza produzione.'}

def markdown(result):
    safe=lambda s:str(s).replace('|','/').replace('\n',' ')
    lines=['# Coda editoriale di crescita', '',result['note'], '',
           f"Tempo disponibile: {result['weekly_minutes']} minuti/settimana ({result['capacity_source']}).", '',
           '| Settimana | Argomento | Formato | Prova | Stato |', '|---|---|---|---|---|']
    for week in result['calendar']:
        for item in week['ideas']:
            lines.append('| '+ ' | '.join(map(safe,[str(week['week'])+' · '+week['from'],item['topic'],item['format'],item['experiment']['variable'],item['stage']]))+' |')
    lines+=['','## Prossime azioni','']
    for week in result['calendar']:
        for r in week['ideas']:
            lines += [f"- {safe(r['id'])}: {safe(r['next_action'])}. Promessa: {safe(r['viewer_promise'])}. Collegamento successivo: {safe(r['next_episode'])}."]
    lines+=['','## Idee conservate per dopo','']+[f"- {safe(r['id'])}: {safe(r['reason'])}." for r in result['deferred']]
    return '\n'.join(lines)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ideas',required=True);p.add_argument('--start',required=True)
    p.add_argument('--minutes',type=float);p.add_argument('--weeks',type=int);p.add_argument('--out',required=True)
    a=p.parse_args();result=plan(json.loads(Path(a.ideas).read_text()),a.start,a.minutes,a.weeks)
    out=Path(a.out)
    if out.exists() and any(out.iterdir()):raise ValueError('Usare una nuova cartella per conservare i piani precedenti')
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/'GROWTH_PLAN_V14.json',result)
    (out/'GROWTH_PLAN_V14.md').write_text(markdown(result))
    print('Piano salvato; nessun render, costo API o pubblicazione eseguiti.')

if __name__=='__main__':main()
