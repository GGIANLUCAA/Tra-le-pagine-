"""Shared editorial checks: local files only, no provider calls or publication."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'config/editorial_rules.json'


def policy():
    return json.loads(POLICY.read_text(encoding='utf-8'))


def new_contract(kind):
    rules = policy()
    fmt = rules['formats'][kind]
    return {
        'rules_version': rules['version'],
        'policy_sha256': hashlib.sha256(POLICY.read_bytes()).hexdigest(),
        'requested_format': kind,
        'narrated': fmt['narrated'],
        'voice': fmt['voice'],
        'speech_language': fmt['speech_language'],
        'subtitles': fmt['subtitles'],
        'format_change_authorization': None,
    }


def new_plan():
    return {'subject_insight': '', 'sources': [], 'opening_promise': '',
            'payoff': '', 'cover_reason': '', 'duration_seconds': None,
            'duration_reason': '', 'techniques': [], 'mix_reason': '',
            'social_languages': {}, 'comparison_reference': None,
            'voice_image_sync_review': 'pending', 'artistic_review': 'pending'}


def validate(project):
    """Validate intent and planning declarations, never infer spoken audio from AAC."""
    errors, warnings = [], []
    contract = project.get('editorial_contract')
    if contract is None:
        warnings.append('Scheda storica senza contratto editoriale: migrare prima di un nuovo lotto; nessuna protezione aggiuntiva del format certificata.')
        return errors, warnings
    if not isinstance(contract, dict):
        return ['Contratto editoriale non valido'], warnings
    rules = policy()
    if contract.get('rules_version') != rules['version'] or contract.get('policy_sha256') != hashlib.sha256(POLICY.read_bytes()).hexdigest():
        errors.append('Versione regole cambiata: rivedere e migrare esplicitamente la scheda, senza aggiornamenti silenziosi')
    requested = contract.get('requested_format')
    actual = project.get('format')
    if requested not in rules['formats'] or actual not in rules['formats']:
        return errors + ['Formato richiesto o operativo sconosciuto'], warnings
    if actual != requested:
        # Preserve the original request; an explicit exception must name both ends.
        auth = contract.get('format_change_authorization')
        if not (isinstance(auth, dict) and auth.get('from') == requested
                and auth.get('to') == actual and auth.get('approved_by') == 'user'
                and isinstance(auth.get('instruction'), str) and auth['instruction'].strip()):
            errors.append('Il formato richiesto è cambiato senza istruzione esplicita: ' + requested + ' → ' + actual)
    fmt = rules['formats'][actual]
    if contract.get('narrated') is not fmt['narrated']:
        errors.append('Presenza della voce incompatibile con il format: il Critico deve restare narrato')
    if project.get('subtitles') is not contract.get('subtitles') or contract.get('subtitles') is not fmt['subtitles']:
        errors.append('Impostazione sottotitoli diversa dal profilo di questo percorso')
    if fmt['narrated']:
        if contract.get('voice') != fmt['voice']:
            errors.append('Voce diversa dal riferimento Gacrux: preparare una variante esplicitamente approvata')
        if not isinstance(contract.get('speech_language'), str) or not contract['speech_language'].strip():
            errors.append('Lingua del parlato mancante')
    plan = project.get('editorial_plan')
    if not isinstance(plan, dict):
        return errors + ['Piano editoriale mancante'], warnings
    for key in ('subject_insight', 'opening_promise', 'payoff', 'cover_reason', 'duration_reason', 'mix_reason'):
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            errors.append('Piano editoriale da completare: ' + key)
    duration = plan.get('duration_seconds')
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        errors.append('Durata proposta positiva e finita richiesta, motivata dal contenuto')
    languages = plan.get('social_languages')
    if not isinstance(languages, dict) or not languages or any(not isinstance(v, str) or not v.strip() for v in languages.values()):
        errors.append('Definire piattaforme e lingue dei post')
    sources = plan.get('sources')
    if not isinstance(sources, list) or not sources:
        errors.append('Ricerca del soggetto senza fonti documentate')
    else:
        for source in sources:
            if not isinstance(source, dict) or any(not isinstance(source.get(k), str) or not source[k].strip() for k in ('reference', 'finding', 'verification_notes')) or source.get('status') != 'reviewed':
                errors.append('Fonte senza riscontro e nota di verifica: non inventare approvazioni')
    entries = json.loads((ROOT / rules['technique_catalog']).read_text(encoding='utf-8'))['techniques']
    catalog = {x['id']: x for x in entries}
    techniques = plan.get('techniques')
    if not isinstance(techniques, list) or not techniques:
        errors.append('Scegliere almeno una tecnica motivata, anche solo una camera ferma')
    else:
        seen = set()
        for item in techniques:
            if not isinstance(item, dict) or not isinstance(item.get('id'), str):
                errors.append('Tecnica non valida')
                continue
            tid = item['id']
            if tid in seen:
                errors.append('Tecnica duplicata: ' + tid)
            seen.add(tid)
            if tid not in catalog or actual not in catalog[tid]['formats']:
                errors.append('Tecnica inesistente o incompatibile con il format: ' + tid)
            if not isinstance(item.get('reason'), str) or not item['reason'].strip():
                errors.append('Motivazione tecnica mancante: ' + tid)
            if item.get('status') not in ('trial', 'approved_option'):
                errors.append('Tecnica: indicare trial oppure approved_option')
            elif item['status'] == 'approved_option' and tid not in rules['technique_approvals']:
                errors.append('Approvazione della tecnica non registrata: ' + tid)
    if fmt['narrated']:
        warnings.append('Prima della consegna ascoltare la voce effettiva e verificare immagini/frasi e tempi reali; una traccia audio può contenere solo musica.')
    return errors, warnings
