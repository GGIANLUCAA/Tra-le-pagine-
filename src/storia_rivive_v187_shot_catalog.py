#!/usr/bin/env python3
"""V187: detect camera-cut hints and extract diverse native film review frames.

The input is a SHA-locked *compressed derivative* (not the native archive).
No provider requests, no claims of Italian rights, five human-approved shots,
I2I restorations, exact freeze, publication or final master.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from storia_rivive_v184_source_intake import inspect_local
from storia_rivive_v185_storyboard_scout import extract_frame

PTS_RE = re.compile(r'\bpts_time:([0-9]+(?:\.[0-9]+)?)')


def scan_cuts(source, duration, threshold=0.14):
    """Decode true source frames, then 2 fps analysis for approximate cuts."""
    if not (0.02 <= threshold <= 0.85):
        raise ValueError('BAD_THRESHOLD')
    cmd = ['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-loglevel', 'info',
           '-i', str(source), '-map', '0:v:0', '-an',
           '-vf', f"fps=2,scale=320:-2,select='gt(scene,{threshold:.3f})',showinfo",
           '-f', 'null', '-']
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True,
                          timeout=max(180, min(1500, int(duration * 1.8))))
    times = []
    for line in proc.stderr.splitlines():
        if 'Parsed_showinfo' not in line:
            continue
        match = PTS_RE.search(line)
        if match:
            t = float(match.group(1))
            if 1 < t < duration - 1 and (not times or t - times[-1] >= 2.5):
                times.append(round(t, 3))
    return times


def choose_intervals(cuts, duration, count=12, min_seconds=4.0):
    """Choose one center per distinct cut-delimited interval; spread across film."""
    if not 5 <= count <= 20 or duration < 30:
        raise ValueError('INVALID_CATALOG_SETTINGS')
    boundaries = [0.0] + sorted(set(t for t in cuts if 0 < t < duration)) + [duration]
    intervals = []
    for index, (a, b) in enumerate(zip(boundaries, boundaries[1:])):
        if b - a >= min_seconds:
            intervals.append({'shot_interval_index': index,
                              'interval_start_seconds': round(a, 3),
                              'interval_end_seconds': round(b, 3),
                              'sample_seconds': round((a+b)/2, 3)})
    if len(intervals) < 5:
        raise ValueError('FEWER_THAN_FIVE_CUT_DELIMITED_INTERVALS')
    remaining = intervals[:]
    selected = []
    for j in range(min(count, len(remaining))):
        target = duration * (j + .5) / min(count, len(intervals))
        best = min(remaining, key=lambda r: (abs(r['sample_seconds'] - target),
                                            -(r['interval_end_seconds']-r['interval_start_seconds'])))
        selected.append(best)
        remaining.remove(best)
    return sorted(selected, key=lambda r: r['sample_seconds'])


def grayscale_signature(source, seconds):
    """Return 9x8 luma grid for conservative near-duplicate rejection."""
    p = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error',
                        '-ss', f'{seconds:.3f}', '-i', str(source), '-map', '0:v:0',
                        '-frames:v', '1', '-vf', 'scale=9:8,format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True, check=True, timeout=90)
    if len(p.stdout) != 72:
        raise ValueError('SIGNATURE_FRAME_NOT_DECODED')
    return list(p.stdout)


def near_duplicate(a, b):
    if len(a) != 72 or len(b) != 72:
        raise ValueError('INVALID_SIGNATURE')
    mean_diff = sum(abs(x-y) for x, y in zip(a,b)) / 72
    bits_a = [a[row*9+x] > a[row*9+x+1] for row in range(8) for x in range(8)]
    bits_b = [b[row*9+x] > b[row*9+x+1] for row in range(8) for x in range(8)]
    hamming = sum(x != y for x,y in zip(bits_a,bits_b))
    return mean_diff < 10 and hamming <= 8



def dark_or_title_like(signature):
    """Reject unreadable near-black samples, including black intertitle cards.

    This is only a conservative frame heuristic, NOT semantic title detection.
    """
    if len(signature) != 72:
        raise ValueError('INVALID_SIGNATURE')
    return (sum(signature) / 72 < 20
            and sum(x < 35 for x in signature) / 72 >= 0.85)


def catalog(source, sha256, out_dir, count=12, threshold=0.14):
    source, out_dir = Path(source), Path(out_dir)
    report = {'version': 'V187', 'status': 'CATALOG_BLOCKED', 'source_sha256': sha256,
              'candidates': [], 'blocking_issues': [], 'provider_jobs_may_start': False,
              'publish_permitted': False, 'rights_italy_verified': False,
              'five_distinct_shots_verified': False, 'native_scan_verified': False,
              'human_visual_qa_approved': False, 'freeze_pts_verified': False}
    if out_dir.exists():
        report['blocking_issues'].append('OUTPUT_DIR_ALREADY_EXISTS')
        return report
    if any(p.is_symlink() for p in (source, *source.parents, out_dir, *out_dir.parents)):
        report['blocking_issues'].append('SYMLINK_SOURCE_OR_OUTPUT_REJECTED')
        return report
    try:
        intake = inspect_local(source, sha256)
        if intake['status'] != 'ASSETS_PENDING' or intake['source_sha256'] != sha256:
            raise ValueError('SOURCE_SHA_OR_FFPROBE_NOT_READY')
        duration = intake['media']['duration_seconds']
        report['source_media'] = intake['media']
        cuts = scan_cuts(source, duration, threshold)
        report['algorithmic_cut_seconds'] = cuts
        options = choose_intervals(cuts, duration, count)
        out_dir.mkdir(parents=True)
        signatures = []
        for candidate in options:
            signature = grayscale_signature(source, candidate['sample_seconds'])
            if dark_or_title_like(signature):
                report.setdefault('excluded_dark_or_title_like', []).append(candidate)
                continue
            if any(near_duplicate(signature, old) for old in signatures):
                report.setdefault('excluded_near_duplicates', []).append(candidate)
                continue
            dest = out_dir / f"shot_{len(report['candidates'])+1:02}.png"
            digest = extract_frame(source, candidate['sample_seconds'], dest)
            report['candidates'].append(dict(candidate, png_filename=dest.name,
                                              png_sha256=digest,
                                              camera_shot_human_verified=False,
                                              source_frame_exact_pts_verified=False))
            signatures.append(signature)
        if len(report['candidates']) < 5:
            raise ValueError('FEWER_THAN_FIVE_DIVERSE_REVIEW_FRAMES')
        report['status'] = 'DIVERSE_CUT_CANDIDATES_NEED_VISUAL_REVIEW'
        report['blocking_issues'] = ['CAMERA_CUTS_ALGORITHMIC_NOT_HUMAN_VERIFIED',
                                     'ITALIAN_RIGHTS_UNVERIFIED',
                                     'COMPRESSED_DERIVATIVE_NOT_NATIVE_SCAN',
                                     'NO_REAL_I2I_OR_VIDU', 'EXACT_FREEZE_PTS_PENDING']
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        report['blocking_issues'].append(type(exc).__name__ + ':' + str(exc)[:150])
    finally:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / 'V187_SHOT_CATALOG.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--file', required=True)
    ap.add_argument('--expected-sha256', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--count', type=int, default=12)
    args = ap.parse_args()
    r = catalog(args.file, args.expected_sha256, args.out_dir, args.count)
    print(json.dumps({'status':r['status'], 'candidates':len(r['candidates']),
                      'issues':r['blocking_issues']}))
    return 0 if r['status'] == 'DIVERSE_CUT_CANDIDATES_NEED_VISUAL_REVIEW' else 2

if __name__ == '__main__':
    raise SystemExit(main())
