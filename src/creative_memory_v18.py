#!/usr/bin/env python3
"""Offline index of V13 video recipes. Verify real files; never infer style from a filename."""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path

from video_director_v13 import ROOT


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_entry(folder, entry):
    if not isinstance(entry, dict):
        return False
    name, sha = entry.get('file'), entry.get('sha256')
    if not isinstance(name, str) or not isinstance(sha, str) or len(sha) != 64:
        return False
    rel = Path(name)
    path = (folder / rel).resolve()
    if rel.is_absolute() or not path.is_relative_to(folder.resolve()) or not path.is_file() or path.is_symlink():
        return False
    return digest(path) == sha


def scan(directories, root=ROOT, limit=2000):
    root = Path(root).resolve()
    recipes = []
    seen = set()
    for directory in directories:
        folder = (root / directory).resolve() if not Path(directory).is_absolute() else Path(directory).resolve()
        if not folder.is_relative_to(root) or not folder.is_dir():
            continue
        for path in sorted(folder.rglob('VIDEO_RECIPE_V13.json')):
            if len(seen) >= limit:
                break
            if path.is_symlink() or not path.resolve().is_relative_to(root) or path in seen:
                continue
            seen.add(path)
            try:
                r = json.loads(path.read_text(encoding='utf-8'))
                if r.get('schema') != 'video-recipe-v13':
                    continue
                video = safe_entry(path.parent, r.get('video'))
                cover = safe_entry(path.parent, r.get('cover'))
                sources = r.get('sources', [])
                sources = sources if isinstance(sources, list) else []
                source_matches = sum(safe_entry(path.parent, x) for x in sources)
                verified = video and cover and source_matches == len(sources)
                recipes.append({
                    'recipe': path.relative_to(root).as_posix(),
                    'topic': str(r.get('topic') or 'Senza titolo'),
                    'format': str(r.get('format') or 'sconosciuto'),
                    'reference_status': 'assets_integrity_verified' if verified else 'incomplete_package',
                    'video_verified': video, 'cover_verified': cover,
                    'sources_verified': source_matches, 'sources_total': len(sources),
                    'artistic_approval_proven': False,
                    'actual_preset_from_source_required': True,
                    'note': 'Hash e presenza dei file non dimostrano qualità artistica, voce, diritti o approvazione.'
                })
            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
                continue
    return {'schema': 'creative-memory-v18', 'references': recipes,
            'count': len(recipes),
            'packages_with_verified_assets': sum(x['reference_status'] == 'assets_integrity_verified' for x in recipes),
            'artistic_approval_proven': False, 'paid_calls': 0,
            'note': 'Archivio ricette recuperate realmente dal filesystem; non produce video né inventa preset.'}


def export(result, out):
    target = Path(out)
    if target.exists() and any(target.iterdir()):
        raise ValueError('Non sovrascrivere un archivio precedente')
    target.mkdir(parents=True, exist_ok=True)
    (target/'CREATIVE_MEMORY_V18.json').write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    rows = []
    for item in result['references']:
        title = html.escape(item['topic'])
        rows.append('<li><strong>'+title+'</strong> · '+html.escape(item['format'])+' · '+
                    html.escape(item['reference_status'])+'<small> (ricetta: '+
                    html.escape(item['recipe'])+')</small></li>')
    page = '''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Memoria regia V18</title><style>body{max-width:760px;margin:auto;padding:24px;background:#11202b;color:#f5f5f5;font:16px/1.6 system-ui}
li{margin:14px 0;padding:12px;border-radius:12px;background:#243747}small{display:block;color:#b9cbd9}h1{font-size:30px}</style>
<h1>Memoria delle regie</h1><p>Ricette effettivamente trovate: '''+str(result['count'])+'''. Pacchetti con file verificati: '''+str(result['packages_with_verified_assets'])+'''.
La verifica artistica richiede osservazione reale dei video. Nessuna approvazione viene dedotta dai file.</p><ul>'''+''.join(rows)+'''</ul></html>'''
    (target/'CREATIVE_MEMORY_V18.html').write_text(page, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scan', action='append', default=None,
                    help='Percorso relativo nel repository; ripetibile')
    ap.add_argument('--out', default='output/creative-memory-v18')
    args = ap.parse_args()
    result = scan(args.scan or ['output', 'episodes'])
    export(result, args.out)
    print(f"Ricette trovate: {result['count']}; pacchetti completi: {result['packages_with_verified_assets']}. API 0.")


if __name__ == '__main__':
    main()
