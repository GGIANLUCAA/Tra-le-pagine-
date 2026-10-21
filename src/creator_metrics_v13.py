"""Offline creator decision report. No account access, publishing or revenue forecasts."""
import argparse
import json
import math
from pathlib import Path
from collections import defaultdict
from statistics import median

METRICS = ('views', 'watch_seconds', 'clicks', 'orders', 'net_receipts_eur', 'cash_cost_eur', 'hours', 'followers_gained', 'shares', 'saves', 'video_seconds')
GROUP = ('platform', 'account', 'format', 'window_days', 'view_definition')

def number(value, label):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError('Numero non valido: ' + label)
    return value

def analyze(data):
    if not isinstance(data, dict) or data.get('schema') != 'creator-observations-v13':
        raise ValueError('Schema non riconosciuto')
    rows = data.get('observations')
    if not isinstance(rows, list):
        raise ValueError('observations deve essere una lista')
    seen, groups, details = set(), defaultdict(list), []
    for r in rows:
        if not isinstance(r, dict):
            raise ValueError('Osservazione non valida')
        for k in ('video_id', 'platform', 'account', 'format', 'view_definition', 'source', 'observed_at'):
            if not isinstance(r.get(k), str) or not r[k].strip():
                raise ValueError('Campo obbligatorio: ' + k)
        window = number(r.get('window_days'), 'window_days')
        if window is None or window <= 0:
            raise ValueError('Finestra di osservazione obbligatoria')
        key = (r['platform'], r['account'], r['video_id'], window)
        if key in seen:
            raise ValueError('Snapshot duplicato: usare una sola osservazione per video e finestra')
        seen.add(key)
        m = {k: number(r.get(k), k) for k in METRICS}
        def ratio(a, b):
            return a / b if a is not None and b is not None and b > 0 else None
        margin = m['net_receipts_eur'] - m['cash_cost_eur'] if all(m[k] is not None for k in ('net_receipts_eur', 'cash_cost_eur')) else None
        d = {**{k:r[k] for k in ('video_id', *GROUP)}, 'metrics': m,
             'avg_watch_seconds': ratio(m['watch_seconds'], m['views']),
             'followers_per_1000_views': None if ratio(m['followers_gained'],m['views']) is None else 1000*ratio(m['followers_gained'],m['views']),
             'shares_per_1000_views': None if ratio(m['shares'],m['views']) is None else 1000*ratio(m['shares'],m['views']),
             'average_watch_fraction': ratio(ratio(m['watch_seconds'],m['views']),m['video_seconds']),
             'cash_contribution_eur': margin,
             'contribution_per_hour_eur': ratio(margin, m['hours']),
             'missing': [k for k,v in m.items() if v is None]}
        details.append(d)
        groups[tuple(r[k] for k in GROUP)].append(d)
    summaries = []
    for key, items in groups.items():
        values = [d['metrics']['views'] for d in items if d['metrics']['views'] is not None]
        summaries.append({**dict(zip(GROUP,key)), 'n': len(items), 'views_observed_n': len(values),
            'median_views': median(values) if values else None,
            'decision': 'raccolta_dati' if len(items) < 5 else 'confronto_descrittivo',
            'note': 'Nessuna causalità o significatività statistica dimostrata; controllare argomento, durata e distribuzione.'})
    return {'schema':'creator-report-v13', 'observations':details, 'cohorts':summaries,
            'account_connections':False, 'revenue_forecast':None,
            'growth_note':'Tassi descrittivi sul denominatore dichiarato; replay possono superare il 100%. Iscritti attribuiti al singolo video, non variazione totale del canale.',
            'note':'Contributo di cassa prima di imposte e costi fissi non allocati; non è utile netto. Finestre diverse non si sommano.'}

def markdown(result):
    def show(x): return 'n/d' if x is None else f'{x:.2f}'
    lines=['# Report creator', '', result['note'], '',
           'Dati mancanti restano sconosciuti. Le righe confrontano la stessa piattaforma, account, formato, finestra e definizione di visualizzazione.', '',
           '| Piattaforma / account / formato | Giorni | Video | Mediana visualizzazioni | Stato |',
           '|---|---:|---:|---:|---|']
    def safe(x): return str(x).replace('|','/').replace('\n',' ')
    for c in result['cohorts']:
        lines.append(f"| {safe(c['platform'])} / {safe(c['account'])} / {safe(c['format'])} | {c['window_days']} | {c['n']} | {show(c['median_views'])} | {c['decision']} |")
    lines += ['', '| Video | Finestra | Contributo € | €/ora | Dati mancanti |', '|---|---:|---:|---:|---|']
    for d in result['observations']:
        lines.append(f"| {safe(d['video_id'])} | {d['window_days']} | {show(d['cash_contribution_eur'])} | {show(d['contribution_per_hour_eur'])} | {', '.join(d['missing']) or 'nessuno'} |")
    lines += ['', '## Crescita osservata', '', result['growth_note'], '', '| Video | Iscritti / 1.000 views | Condivisioni / 1.000 views | Tempo medio / durata |', '|---|---:|---:|---:|']
    for d in result['observations']:
        lines.append(f"| {safe(d['video_id'])} | {show(d['followers_per_1000_views'])} | {show(d['shares_per_1000_views'])} | {show(d['average_watch_fraction'])} |")
    lines += ['', '## Prossima revisione', '',
              '1. Leggere la curva di ritenzione e i commenti originali prima di attribuire una causa.',
              '2. Scegliere una sola ipotesi (apertura, argomento, copertina o invito finale).',
              '3. Confrontare nuovi episodi a pari età di pubblicazione; non duplicare lo stesso filmato.',
              '4. Annotare decisione, costo e limite della prova. Non abbandonare una serie per un singolo risultato.',
              '5. Priorità attuale: pubblico che guarda e torna. Nessuna proposta di commissioni o sponsor; monetizzazione solo quando pertinente e richiesta.']
    return '\n'.join(lines)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True);p.add_argument('--out',required=True)
    args=p.parse_args()
    result=analyze(json.loads(Path(args.input).read_text()))
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'CREATOR_REPORT_V13.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (out/'CREATOR_REPORT_V13.md').write_text(markdown(result))
    print(f'Report pronto: {out}; nessuna API o pubblicazione eseguita.')

if __name__=='__main__': main()
