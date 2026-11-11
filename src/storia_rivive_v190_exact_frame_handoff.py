#!/usr/bin/env python3
"""V190: validate V189 *decoded* final freeze frames and stage 4+1 source anchors.

No I2I or Vidu API calls, no rights or artistic approvals, no publication.
All five original B/W frame anchors are SHA-locked; four are proposed for
photographic I2I, the fifth for Vidu *after* separate authorization.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HEX = re.compile(r"[0-9a-f]{64}\Z")
CLIP = re.compile(r"\d{2}_[a-z0-9-]+_real_film_bw\.mp4\Z")
FREEZE = re.compile(r"\d{2}_[a-z0-9-]+_last_real_film_frame\.png\Z")
PROMPT = (
    "Image-to-image photographic restoration of THIS exact historical film frame. "
    "Preserve camera geometry, every visible person, face, pose, clothing, hand, "
    "building and object. Period-appropriate realistic colors. Never invent "
    "unrecoverable identity, text, limbs, objects or architectural details."
)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def local_file(root, name, pattern):
    if not isinstance(name, str) or not pattern.fullmatch(name):
        raise ValueError('UNSAFE_ASSET_FILENAME')
    path = root / name
    if not path.is_file() or path.is_symlink():
        raise ValueError('ASSET_MISSING_OR_SYMLINK:' + name)
    return path


def check_hash(path, expected):
    if not isinstance(expected, str) or not HEX.fullmatch(expected) or sha(path) != expected:
        raise ValueError('ASSET_SHA_MISMATCH:' + path.name)


def probe(path):
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
           '-show_entries', 'stream=codec_name,width,height,nb_read_frames',
           '-of', 'json', str(path)]
    obj = json.loads(subprocess.run(cmd, capture_output=True, text=True,
                                    check=True, timeout=45).stdout)
    if len(obj.get('streams', [])) != 1:
        raise ValueError('MISSING_VIDEO_STREAM')
    return obj['streams'][0]


def rgb_frame(path, frame_index=None):
    cmd = ['ffmpeg', '-hide_banner', '-nostdin', '-loglevel', 'error', '-i', str(path)]
    if frame_index is not None:
        cmd += ['-vf', f'select=eq(n\\,{frame_index})']
    cmd += ['-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    return subprocess.run(cmd, capture_output=True, check=True, timeout=60).stdout


def build(report, root, expected_dimensions=(720, 1280)):
    if report.get('version') != 'V189' or report.get('status') != 'REAL_BW_MOTION_PROOF_REVIEW_ONLY':
        raise ValueError('NOT_A_V189_MOTION_PROOF')
    if (report.get('four_real_i2i') != 0 or report.get('real_vidu_clips') != 0
            or report.get('publish_permitted') is not False
            or report.get('rights_italy_verified') is not False
            or report.get('provider_jobs_may_start') is not False):
        raise ValueError('UNSAFE_PROOF_PERMISSIONS')
    if not HEX.fullmatch(str(report.get('source_sha256', ''))):
        raise ValueError('SOURCE_SHA_INVALID')
    scenes = report.get('scenes')
    if not isinstance(scenes, list) or len(scenes) != 5:
        raise ValueError('FIVE_AUTHENTIC_SCENES_REQUIRED')
    if len({s.get('v187_png') for s in scenes}) != 5 or len({s.get('v187_sha256') for s in scenes}) != 5:
        raise ValueError('DUPLICATE_ARCHIVE_SHOT')
    if len({s.get('v187_interval', [None])[0] for s in scenes}) != 5:
        raise ValueError('DUPLICATE_SOURCE_INTERVAL')
    if not all(s.get('freeze_from_last_encoded_motion_frame') is True and
               s.get('v187_png_is_not_the_frozen_frame') is True for s in scenes):
        raise ValueError('NOT_AN_EXACT_V189_FREEZE')
    if [s.get('index') for s in scenes] != [1, 2, 3, 4, 5]:
        raise ValueError('SCENE_ORDER_INVALID')
    root = Path(root)
    anchors = []
    for scene in scenes:
        movie = local_file(root, scene.get('motion_mp4'), CLIP)
        still = local_file(root, scene.get('freeze_png'), FREEZE)
        check_hash(movie, scene.get('motion_mp4_sha256'))
        check_hash(still, scene.get('exact_last_decoded_frame_sha256'))
        meta = probe(movie)
        if (meta.get('codec_name') != 'h264' or
                (int(meta['width']), int(meta['height'])) != expected_dimensions or
                int(meta.get('nb_read_frames', 0)) < 25):
            raise ValueError('MOTION_CLIP_CODEC_OR_GEOMETRY_INVALID')
        image = probe(still)
        if (image.get('codec_name') != 'png' or
                (int(image['width']), int(image['height'])) != expected_dimensions):
            raise ValueError('FREEZE_PNG_GEOMETRY_INVALID')
        decoded = rgb_frame(movie, int(meta['nb_read_frames']) - 1)
        original = rgb_frame(still)
        expected_bytes = expected_dimensions[0] * expected_dimensions[1] * 3
        if len(decoded) != expected_bytes or decoded != original:
            raise ValueError('FREEZE_NOT_LAST_DECODED_FRAME:' + still.name)
        anchors.append({
            'scene': scene['index'], 'editorial_label': scene['label'],
            'source_archive_derivative_sha256': report['source_sha256'],
            'source_shot_png': scene['v187_png'],
            'source_shot_png_sha256': scene['v187_sha256'],
            'source_timecode_approx_s': scene['v187_sample_seconds'],
            'real_motion_file': movie.name, 'real_motion_sha256': sha(movie),
            'exact_freeze_file': still.name, 'exact_freeze_sha256': sha(still),
            'source_crop_native_px': scene['source_crop_px'],
            'encoded_raster_px': list(expected_dimensions),
            'encoded_video_upscaled_from_archival_crop': True,
            'last_decoded_frame_pixel_identical_to_freeze': True,
            'source_lock_verified': True,
            'role': 'PHOTO_I2I_INPUT_NOT_GENERATED' if scene['index'] < 5
                    else 'VIDU_SOURCE_FRAME_NOT_SUBMITTED',
        })
    if len({a['exact_freeze_sha256'] for a in anchors}) != 5:
        raise ValueError('DUPLICATE_FREEZE_IMAGE')
    return {
        'version': 'V190_EXACT_FRAME_I2I_VIDU_HANDOFF',
        'status': 'FIVE_REAL_SOURCE_FRAMES_VERIFIED_PROVIDER_BLOCKED',
        'source_page': report['source_page'],
        'source_kind': report['source_kind'],
        'film_sha256': report['source_sha256'],
        'source_frames': anchors,
        'i2i_requests': [{
            'scene': a['scene'], 'source_file': a['exact_freeze_file'],
            'source_sha256': a['exact_freeze_sha256'], 'prompt': PROMPT,
            'provider': None, 'provider_request_sent': False,
            'restored_photo_file': None, 'restored_photo_approved': False,
        } for a in anchors[:4]],
        'vidu_anchor': {
            'scene': 5, 'source_file': anchors[4]['exact_freeze_file'],
            'source_sha256': anchors[4]['exact_freeze_sha256'],
            'source_clip': anchors[4]['real_motion_file'],
            'plan_created': False, 'balance_checked': False,
            'user_approved_this_exact_scene': False, 'generation_submitted': False,
        },
        'photos_generated': 0, 'vidu_clips_generated': 0,
        'provider_requests_sent': 0, 'credits_spent': 0,
        'rights_italy_verified': False, 'artistic_review_completed': False,
        'publication_permitted': False,
        'blocking_issues': [
            'ITALIAN_RIGHTS_NOT_VERIFIED', 'SOURCE_IS_COMPRESSED_DERIVATIVE',
            'FOUR_REAL_I2I_RESTORATIONS_NOT_GENERATED',
            'VIDU_SCENE_SPECIFIC_AUTHORIZATION_AND_BALANCE_NOT_VERIFIED',
            'VISUAL_FIDELITY_AND_V98_COMPARISON_PENDING',
            'FINAL_V91_V94_V96_V99_GATES_NOT_RUN',
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', required=True)
    p.add_argument('--assets', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    result = build(json.loads(Path(a.report).read_text(encoding='utf-8')), Path(a.assets))
    out = Path(a.out)
    if out.exists() or out.is_symlink():
        raise SystemExit('OUTPUT_EXISTS_REFUSE_OVERWRITE')
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('V190_SOURCE_ANCHORS_VERIFIED', len(result['source_frames']),
          'I2I_CREATED', result['photos_generated'], 'VIDU_CREATED', result['vidu_clips_generated'],
          'PAID_CALLS', result['provider_requests_sent'])


if __name__ == '__main__':
    main()
