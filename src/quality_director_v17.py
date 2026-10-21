#!/usr/bin/env python3
"""Offline, additive artistic QA. Never edits or publishes videos or calls paid APIs."""
from __future__ import annotations
import argparse
import html
import json
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'config' / 'quality_director_v17.json'


def command(args, timeout=120):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, check=True, timeout=timeout)


def dhash(path):
    with Image.open(path) as raw:
        data = list(raw.convert('L').resize((9, 8)).tobytes())
    return sum(1 << (y*8+x) for y in range(8) for x in range(8)
               if data[y*9+x] > data[y*9+x+1])


def notice(code, message, scene=None):
    result = {'code': code, 'message': message}
    if scene is not None:
        result['scene'] = scene
    return result


def inspect_project(project_file, profile):
    warnings, blocking, facts = [], [], []
    if not project_file:
        return warnings, blocking, [{'note': 'Nessuna scheda V13: scene non confrontabili con copione'}]
    source = Path(project_file)
    project = json.loads(source.read_text(encoding='utf-8'))
    if project.get('schema') != 'video-project-v13':
        return warnings, [notice('INVALID_PROJECT', 'Scheda diversa da PROJECT_V13.json')], facts
    scenes, assets = project.get('scenes', []), project.get('assets', [])
    if not isinstance(scenes, list) or not isinstance(assets, list):
        return warnings, [notice('INVALID_CONTENT', 'Scene e asset devono essere liste')], facts
    if not scenes:
        warnings.append(notice('NO_STORYBOARD', 'Storyboard senza scene: definire inquadrature prima del render'))
    script = ''
    name = project.get('script')
    if name:
        if not isinstance(name, str):
            blocking.append(notice('INVALID_SCRIPT', 'Percorso copione non valido'))
        else:
            rel = Path(name)
            file = (source.parent / rel).resolve()
            if rel.is_absolute() or not file.is_relative_to(source.parent.resolve()):
                blocking.append(notice('UNSAFE_SCRIPT_PATH', 'Copione fuori dalla cartella del progetto'))
            elif file.is_file():
                script = file.read_text(encoding='utf-8')
            else:
                warnings.append(notice('SCRIPT_MISSING', 'Copione non reperibile per controllo delle frasi'))
    hashes = {}
    for asset in assets:
        if not isinstance(asset, dict) or asset.get('role') != 'visual':
            continue
        ident, name = asset.get('id'), asset.get('file')
        if not isinstance(ident, str) or not isinstance(name, str):
            continue
        rel = Path(name)
        path = (source.parent / rel).resolve()
        if rel.is_absolute() or not path.is_relative_to(source.parent.resolve()):
            warnings.append(notice('UNSAFE_ASSET_PATH', ident + ': percorso immagine non sicuro'))
            continue
        if not path.is_file():
            warnings.append(notice('IMAGE_MISSING', ident + ': immagine mancante'))
            continue
        try:
            with Image.open(path) as image:
                w, h = image.size
            if min(w, h) < profile['minimum_asset_short_side']:
                warnings.append(notice('LOW_SOURCE_RESOLUTION', f'{ident}: immagine {w}x{h}, verificare nitidezza'))
            hashes[ident] = dhash(path)
        except (OSError, ValueError):
            warnings.append(notice('IMAGE_UNREADABLE', ident + ': immagine non valida'))
        if not str(asset.get('rights') or '').strip():
            warnings.append(notice('RIGHTS_UNCHECKED', ident + ': fonte e diritti da verificare'))
    for i, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict):
            warnings.append(notice('INVALID_SCENE', 'Scena non leggibile', i))
            continue
        if len(str(scene.get('description') or '').strip()) < 18:
            warnings.append(notice('SCENE_GENERIC', 'Descrivere soggetto, azione e inquadratura', i))
        if len(str(scene.get('reason') or '').strip()) < 8:
            warnings.append(notice('NO_DIRECTOR_REASON', 'Motivare la scelta di regia', i))
        if scene.get('asset_id') and scene['asset_id'] not in hashes:
            warnings.append(notice('VISUAL_NOT_AVAILABLE', 'Immagine non controllabile', i))
        anchor = scene.get('narration_anchor')
        if profile['narrated'] and not str(anchor or '').strip():
            warnings.append(notice('MISSING_ANCHOR', 'Collegare la scena alla frase pronunciata', i))
        elif profile['narrated'] and script and anchor and anchor not in script:
            warnings.append(notice('ANCHOR_UNMATCHED', 'Frase non trovata nel copione', i))
    for i, (a,b) in enumerate(zip(scenes, scenes[1:]), 2):
        if not isinstance(a,dict) or not isinstance(b,dict):
            continue
        x, y = a.get('asset_id'), b.get('asset_id')
        if x in hashes and y in hashes and (hashes[x] ^ hashes[y]).bit_count() <= 3:
            warnings.append(notice('SIMILAR_ADJACENT_SCENES', 'Immagini consecutive molto simili: controllare il ritmo', i))
    facts.append({'format': project.get('format'), 'scenes': len(scenes), 'visual_assets_checked': len(hashes),
                  'script_checked': bool(script), 'semantic_check': 'required; image hashes cannot certify scene meaning'})
    return warnings, blocking, facts


def inspect_video(video, profile, out):
    warnings, blocking, facts = [], [], []
    info = json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',video]).stdout)
    streams = info.get('streams', [])
    visual = next((s for s in streams if s.get('codec_type') == 'video'), None)
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    if visual is None:
        blocking.append(notice('NO_VIDEO', 'Manca traccia video'))
    if audio is None:
        blocking.append(notice('NO_AUDIO', 'Manca traccia audio'))
    if any(s.get('codec_type') == 'subtitle' for s in streams):
        blocking.append(notice('UNEXPECTED_SUBTITLES', 'I preset correnti escludono sottotitoli'))
    length = float(info.get('format',{}).get('duration') or 0)
    if length <= 0:
        blocking.append(notice('INVALID_DURATION', 'Durata non valida'))
    if visual:
        w,h = int(visual.get('width',0)), int(visual.get('height',0))
        if min(w,h) < profile['minimum_video_short_side']:
            warnings.append(notice('LOW_MASTER_RESOLUTION', f'Master {w}x{h}: sotto lo standard previsto'))
        if h <= 0 or abs(w/h - 9/16) > .035:
            warnings.append(notice('ASPECT_RATIO', f'Master {w}x{h}: controllare verticale 9:16'))
        facts.append({'duration_seconds': round(length,2), 'resolution':[w,h],
                      'video_codec':visual.get('codec_name'), 'audio_codec':audio.get('codec_name') if audio else None})
    # Reuse V16 frames. Deliberately no extra video rendering or GPU calls.
    frames = sorted(out.glob('REVIEW_FRAME_*.jpg'))
    dark = []
    for frame in frames:
        try:
            with Image.open(frame) as original:
                im = original.convert('L')
                im.thumbnail((64,64))
                data = im.tobytes()
            if sum(v < 7 for v in data) / max(len(data),1) >= .985:
                dark.append(frame.name)
        except OSError:
            warnings.append(notice('FRAME_UNREADABLE', frame.name + ' illeggibile'))
    if dark:
        warnings.append(notice('DARK_SAMPLES', f'{len(dark)} campioni quasi neri su {len(frames)}: verificare se intenzionali'))
    facts.append({'sampled_frames':len(frames), 'nearly_black':dark,
                  'coverage':'only sampled frames, not a full scene or semantics audit'})
    if audio and length > 1:
        seconds = 3.5 if profile['narrated'] else 9
        try:
            scan = command(['ffmpeg','-hide_banner','-nostats','-i',video,'-vn',
                            '-af',f'silencedetect=noise=-42dB:d={seconds}','-f','null','-'], timeout=180)
            n = len(re.findall(r'silence_start:\s*[\d.]+', scan.stderr))
            if n:
                warnings.append(notice('AUDIO_SILENCES', f'{n} pause lunghe da ascoltare: potrebbero essere volute'))
            facts.append({'long_silences_detected':n, 'scan':'silencedetect'})
        except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
            warnings.append(notice('SILENCE_SCAN_UNAVAILABLE', type(exc).__name__))
    return warnings, blocking, facts


def render_html(report, folder):
    blocks = []
    for key, heading in [('blocking','Blocchi tecnici'),('warnings','Da ricontrollare')]:
        items = ''.join('<li><b>'+html.escape(x['code'])+'</b> — '+html.escape(x['message'])+
                        (f' (scena {x["scene"]})' if 'scene' in x else '')+'</li>' for x in report[key])
        blocks.append('<section><h2>'+heading+'</h2><ul>'+(items or '<li>Nessuna segnalazione</li>')+'</ul></section>')
    questions = ''.join('<li>'+html.escape(q)+'</li>' for q in report['artistic_review_questions'])
    previews = ''.join('<img loading="lazy" alt="Campione reale" src="'+html.escape(f.name)+'">' for f in sorted(folder.glob('REVIEW_FRAME_*.jpg')))
    return f'''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Revisione V17</title><style>body{{font:16px system-ui;background:#111827;color:#f8fafc;max-width:820px;margin:auto;padding:20px;line-height:1.5}}section{{background:#1e293b;border-radius:14px;padding:16px;margin:14px 0}}h2{{font-size:1.15rem}}li{{margin:8px 0}}.frames{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}}img{{width:100%;border-radius:7px}}@media(max-width:560px){{.frames{{grid-template-columns:repeat(2,1fr)}}}}</style><h1>Regia e qualità V17</h1><p>{html.escape(report['format'])} · {html.escape(report['status'])}</p><p>Questo controllo non certifica bellezza, accuratezza storica o pertinenza visiva. Revisione artistica ancora obbligatoria.</p>{''.join(blocks)}<section><h2>Domande per il regista</h2><ul>{questions}</ul></section><section><h2>Anteprime reali</h2><div class="frames">{previews}</div></section></html>'''


def inspect(video=None, project=None, out='output/quality-v17', format_name=None, policy_path=POLICY):
    folder = Path(out)
    folder.mkdir(parents=True, exist_ok=True)
    policy = json.loads(Path(policy_path).read_text(encoding='utf-8'))
    pdata = json.loads(Path(project).read_text(encoding='utf-8')) if project else {}
    name = format_name or pdata.get('format') or 'libri'
    profile = policy['formats'].get(name, policy['default'])
    warnings, blocking, facts = inspect_project(project,profile)
    if video:
        w,b,f = inspect_video(Path(video),profile,folder)
        warnings.extend(w); blocking.extend(b); facts.extend(f)
    report = {'schema':'quality-director-v17','format':name,
              'status':'technical_blocked' if blocking else ('needs_review_with_warnings' if warnings else 'needs_artistic_review'),
              'video':str(video) if video else None,'blocking':blocking,'warnings':warnings,
              'findings':facts,'artistic_review_questions':profile['questions'],
              'review_basis':'automatic technical hints only; agent must verify actual visuals and narration',
              'paid_calls':0,'published':False}
    (folder/'QUALITY_REPORT_V17.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (folder/'QUALITY_REVIEW_V17.html').write_text(render_html(report,folder),encoding='utf-8')
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--video',type=Path)
    ap.add_argument('--project',type=Path)
    ap.add_argument('--format',dest='format_name')
    ap.add_argument('--out',type=Path,default=Path('output/quality-v17'))
    args = ap.parse_args()
    report = inspect(video=args.video,project=args.project,out=args.out,format_name=args.format_name)
    print(json.dumps({'status':report['status'],'blocking':len(report['blocking']),'warnings':len(report['warnings'])},ensure_ascii=False))
    return 2 if report['blocking'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
