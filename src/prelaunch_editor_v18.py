#!/usr/bin/env python3
"""V18 prelaunch editorial desk. Offline, read-only inputs; no generation or publishing."""
from __future__ import annotations
import argparse
import difflib
import html
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from video_director_v13 import ROOT, get_format, READY

OLD_IDEAS = ROOT / 'templates' / 'CREATOR_IDEAS_V14.json'
NEW_IDEAS = ROOT / 'templates' / 'PRELAUNCH_ADDITIONS_V18.json'
LEARNING = ROOT / 'templates' / 'CREATOR_LEARNING_V14.json'
QUALITY_POLICY = ROOT / 'config' / 'quality_director_v17.json'
RUBRIC_FIELDS = ('visual_impact', 'story_payoff', 'originality', 'asset_feasibility')
RUBRIC_MAX = 3


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def normalize(value):
    value = unicodedata.normalize('NFKD', value.casefold())
    value = ''.join(char for char in value if not unicodedata.combining(char))
    return ' '.join(re.findall(r'[a-z0-9]+', value))


def required_string(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Campo mancante: ' + name)
    return value.strip()


def repo_file(root, relative):
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError('Percorso mancante')
    name = Path(relative)
    path = (root / name).resolve()
    if name.is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError('Percorso fuori dal repository')
    if not path.is_file():
        raise ValueError('File non disponibile: ' + relative)
    return path


def editorial_score(row):
    review = row.get('editorial_review')
    if review is None:
        return None
    if not isinstance(review, dict):
        raise ValueError('Valutazione editoriale non valida: ' + row['id'])
    required_string(review.get('reviewer'), 'reviewer')
    required_string(review.get('reason'), 'reason')
    for field in RUBRIC_FIELDS:
        score = review.get(field)
        if type(score) is not int or not 0 <= score <= RUBRIC_MAX:
            raise ValueError('Valutazione manuale da 0 a 3 richiesta: ' + field)
    return sum(review[field] for field in RUBRIC_FIELDS)


def adapt_legacy(row):
    return {**row, 'opening_draft': row.get('opening', ''),
            'editorial_review': None, 'origin': 'existing_v14',
            'source_refs': [], 'rights_refs': [], 'visual_refs': [],
            'project_file': None}


def validate_idea(row):
    if not isinstance(row, dict):
        raise ValueError('Idea non valida')
    for name in ('id', 'format', 'topic', 'original_angle'):
        required_string(row.get(name), name)
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,80}', row['id']):
        raise ValueError('ID non sicuro: ' + row['id'])
    fmt = get_format(row['format'])
    for field in ('sources_checked', 'rights_checked', 'visual_plan_checked'):
        if type(row.get(field)) is not bool:
            raise ValueError('Stato verifica booleano richiesto: ' + field)
    if not isinstance(row.get('opening_draft', ''), str):
        raise ValueError('Apertura non valida')
    for refs in ('source_refs', 'rights_refs', 'visual_refs'):
        values = row.get(refs, [])
        if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
            raise ValueError('Elenco evidenze non valido: ' + refs)
    return fmt


def check_project(root, row):
    name = row.get('project_file')
    if not name:
        return False, ['Manca la scheda PROJECT_V13.json']
    try:
        file = repo_file(root, name)
        from video_director_v13 import check
        result = check(file)
        if not isinstance(result, dict):
            return False, ['Preflight V13 senza risultato valido']
        return not result.get('blockers'), result.get('blockers', []) + result.get('warnings', [])
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return False, ['Preflight non superato: ' + str(exc)[:160]]


def plan(existing=None, additions=None, lessons=None, root=ROOT):
    root = Path(root)
    existing = load(OLD_IDEAS) if existing is None else existing
    additions = load(NEW_IDEAS) if additions is None else additions
    lessons = load(LEARNING) if lessons is None else lessons
    if existing.get('schema') != 'creator-ideas-v14' or not isinstance(existing.get('ideas'), list):
        raise ValueError('Idee V14 non valide')
    if additions.get('schema') != 'prelaunch-additions-v18' or not isinstance(additions.get('ideas'), list):
        raise ValueError('Nuove idee V18 non valide')
    if lessons.get('schema') != 'creator-learning-v14' or not isinstance(lessons.get('lessons'), list):
        raise ValueError('Memoria V14 non valida')
    policy = load(root / 'config' / 'quality_director_v17.json')
    items = [adapt_legacy(x) for x in existing['ideas']] + [
        {**x, 'origin': 'addition_v18'} for x in additions['ideas']]
    ids, exact = set(), {}
    evaluations = []
    for row in items:
        fmt = validate_idea(row)
        ident = row['id']
        if ident in ids:
            raise ValueError('ID già presente: ' + ident)
        ids.add(ident)
        score = editorial_score(row)
        fingerprint = (row['format'], normalize(row['topic']), normalize(row['original_angle']))
        flags = ['sources_checked', 'rights_checked', 'visual_plan_checked']
        refs = ['source_refs', 'rights_refs', 'visual_refs']
        issues = []
        if fingerprint in exact:
            issues.append('Stesso argomento e taglio di ' + exact[fingerprint])
        else:
            exact[fingerprint] = ident
        # Reviewer declarations must be tied to inspectable evidence, not checkboxes.
        for flag, evidence in zip(flags, refs):
            if not row[flag] or not row.get(evidence):
                issues.append(flag + ': conferma e riferimento verificabile mancanti')
        preview_ready, project_findings = check_project(root, row) if row.get('project_file') else (False, [])
        if row.get('project_file') and not preview_ready:
            issues.append('Preflight V13 non superato')
        if fmt['status'] not in READY:
            issues.append('Renderer ancora da recuperare: ' + fmt['status'])
        if fingerprint in exact and exact[fingerprint] != ident:
            stage = 'duplicate_review'
        elif fmt['status'] not in READY:
            stage = 'editorial_lab'
        elif not issues and preview_ready:
            stage = 'verified_for_manual_v16_preparation'
        elif row.get('project_file'):
            stage = 'project_needs_evidence'
        else:
            stage = 'idea_to_research'
        # Similar titles are hints only: different editorial angles may be valuable.
        near = []
        for prior in evaluations:
            if prior['format'] != row['format']:
                continue
            similarity = difflib.SequenceMatcher(None, normalize(prior['topic']), normalize(row['topic'])).ratio()
            if similarity >= .78 and prior['id'] != ident:
                near.append({'id': prior['id'], 'title_similarity': round(similarity, 2),
                             'note': 'Controllare angolo e archivio, non scartare automaticamente'})
        questions = policy['formats'].get(row['format'], policy['default'])['questions']
        evaluations.append({'id': ident, 'format': row['format'], 'format_label': fmt['label'],
                            'topic': row['topic'], 'original_angle': row['original_angle'],
                            'opening_draft': row.get('opening_draft', ''),
                            'origin': row['origin'], 'stage': stage,
                            'editorial_score_manual_12': score,
                            'priority_forecast': None, 'issues': issues,
                            'project_findings': project_findings, 'similar_titles': near,
                            'questions': questions,
                            'verified_final_mp4': False, 'scheduled_to_publish': False})
    confirmed_lessons = [
        x for x in lessons['lessons'] if isinstance(x, dict) and
        x.get('status') in ('supported', 'confirmed') and x.get('evidence')]
    by_stage = dict(Counter(x['stage'] for x in evaluations))
    return {'schema': 'prelaunch-plan-v18',
            'channel_status': 'not_launched',
            'count_ideas': len(evaluations), 'count_original_v14': len(existing['ideas']),
            'count_added_v18': len(additions['ideas']),
            'count_verified_final_mp4': 0, 'count_social_metrics': 0,
            'count_confirmed_lessons': len(confirmed_lessons),
            'stage_counts': by_stage, 'ideas': evaluations,
            'zero_paid_api_calls': True, 'published': False,
            'note': 'Priorità senza previsioni di viralità. Le idee e le checklist non sono video pronti; '
                    'ricerca, diritti, asset, regia e visione del master finale restano da svolgere.'}


def to_html(result):
    escape = lambda x: html.escape(str(x), quote=True)
    cards = []
    for item in result['ideas']:
        issues = ''.join('<li>' + escape(s) + '</li>' for s in item['issues'][:5])
        questions = ''.join('<li>' + escape(s) + '</li>' for s in item['questions'][:3])
        score = ('Giudizio manuale '+str(item['editorial_score_manual_12'])+'/12'
                 if item['editorial_score_manual_12'] is not None else 'Valutazione non compilata')
        cards.append('<article class="card" data-kind="'+escape(item['format'])+
                     '" data-stage="'+escape(item['stage'])+'"><div class="meta">'+escape(item['format_label'])+
                     ' · '+escape(item['stage'])+'</div><h2>'+escape(item['topic'])+'</h2>'+
                     '<p><strong>Angolo:</strong> '+escape(item['original_angle'])+'</p>'+
                     ('<p><strong>Apertura, da verificare:</strong> '+escape(item['opening_draft'])+'</p>'
                      if item['opening_draft'] else '')+
                     '<p class="meta">'+escape(score)+'</p>'+
                     '<details><summary>Verifiche e regia</summary><h3>Da verificare</h3><ul>'+
                     (issues or '<li>Nessuna segnalazione documentale</li>')+
                     '</ul><h3>Domande artistiche</h3><ul>'+questions+'</ul></details></article>')
    return '''<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0c1722">
<title>Studio pre-lancio V18</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{font:16px/1.5 system-ui;margin:0;background:#0c1722;color:#f5f5f5}
header,main{max-width:1100px;margin:auto;padding:20px}
h1{font-size:clamp(28px,7vw,45px);line-height:1.1}h2{font-size:18px;margin:8px 0}h3{font-size:15px}
.muted,.meta{color:#b4c4d1}.meta{font-size:13px}.controls{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0}
input,select{background:#1e3042;color:white;border:1px solid #60748a;border-radius:10px;padding:13px;font:inherit;min-width:0;flex:1}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,295px),1fr));gap:13px}
.card{background:#1b2a3a;border:1px solid #344c63;border-radius:16px;padding:16px}
.card p{overflow-wrap:anywhere}details{border-top:1px solid #344c63;padding-top:8px}summary{cursor:pointer;color:#efce93}
li{padding-bottom:7px}a{color:#efce93}.summary{background:#17283a;border-radius:14px;padding:14px}
</style></head><body>
<header><p class="meta">Tra le Pagine · Piano creativo V18</p><h1>Uno studio pronto a scegliere bene.</h1>
<p class="muted">Idee editoriali, non master realizzati. Nessun account social attivo collegato, nessuna metrica inventata, nessun costo API.</p>
<div class="summary"><strong>'''+escape(result['count_ideas'])+''' idee</strong> · '''+
escape(result['count_original_v14'])+''' recuperate · '''+escape(result['count_added_v18'])+
''' nuove bozze<br><span class="muted">Master verificati in questa lista: 0 · Pubblicazioni: 0 · Risultati social: non disponibili</span></div></header>
<main><div class="controls"><input id="search" aria-label="Cerca" placeholder="Cerca argomento o autore">
<select id="kind" aria-label="Filtra genere"><option value="">Tutte le categorie</option>
<option value="libri">Libri narrati</option><option value="artvision_critico">Critica d'arte</option>
<option value="artvision_cinema">Arte senza voce</option></select></div>
<p class="muted" id="visible"></p><div class="cards" id="cards">'''+''.join(cards)+'''</div>
<p class="muted">Ogni episodio richiede ricerca, controlli sui diritti, storyboard, sorgenti e revisione del master.
Questa pagina è consultabile offline anche su Android: non modifica le pipeline di produzione.</p></main>
<script>const cards=[...document.querySelectorAll('.card')];const s=document.querySelector('#search'),k=document.querySelector('#kind'),v=document.querySelector('#visible');
function refresh(){let n=0;for(const c of cards){const ok=c.textContent.toLocaleLowerCase('it').includes(s.value.toLocaleLowerCase('it'))&&(!k.value||c.dataset.kind===k.value);c.hidden=!ok;if(ok)n++;}v.textContent=n+' idee visibili';}
s.addEventListener('input',refresh);k.addEventListener('change',refresh);refresh();</script></body></html>'''


def run(out, existing=None, additions=None, lessons=None, root=ROOT):
    result = plan(existing, additions, lessons, root=root)
    target = Path(out)
    if target.exists() and any(target.iterdir()):
        raise ValueError('La cartella contiene già un report: non sovrascrivere')
    target.mkdir(parents=True, exist_ok=True)
    (target/'PRELAUNCH_PLAN_V18.json').write_text(
        json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (target/'PRELAUNCH_DASHBOARD_V18.html').write_text(to_html(result), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='output/prelaunch-v18')
    args = parser.parse_args()
    result = run(args.out)
    print(f"{result['count_ideas']} idee; {result['count_added_v18']} nuove; "
          "0 video dichiarati pronti. Report HTML e JSON disponibili, costo API 0.")


if __name__ == '__main__':
    main()
