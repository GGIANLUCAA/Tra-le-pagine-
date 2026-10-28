#!/usr/bin/env python3
"""V58: offline FFmpeg montage of PRE-COLORED archive scenes; no AI, APIs or paid calls."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

VALID = {"reveal", "archive_color", "archive_bw", "ai_reconstruction"}
ENCODES = ((360, 640), (720, 1280), (1080, 1920))


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(plan):
    errors, scenes = [], plan.get("scenes", [])
    def block(condition, message):
        if not condition:
            errors.append(message)
    block(plan.get("autopublish") is not True, "Autopubblicazione bloccata")
    block(plan.get("allow_paid_calls") is not True, "Nessuna API o credito nel montatore")
    block((plan.get("width"), plan.get("height")) in ENCODES, "Risoluzione non valida")
    block((plan.get("width"), plan.get("height")) != (360, 640) or plan.get("test_only") is True,
          "360x640 consentito solo per test")
    block(isinstance(scenes, list) and 1 <= len(scenes) <= 12, "Numero scene non valido")
    if not isinstance(scenes, list):
        scenes = []
    total, revealed = 0, False
    for i, s in enumerate(scenes):
        label = "Scena %s: " % (i + 1)
        kind = s.get("kind")
        block(kind in VALID, label + "tipo sconosciuto")
        if kind not in VALID:
            continue
        t, d = s.get("start"), s.get("duration")
        block(isinstance(t, (float, int)) and t >= 0, label + "start non valido")
        block(isinstance(d, (float, int)) and .7 <= d <= 30, label + "durata non valida")
        if isinstance(d, (float, int)):
            total += d
        block(s.get("framing_reviewed") is True, label + "inquadratura non controllata")
        mode = s.get("framing", "contain")
        block(mode in ("contain", "safe_crop"), label + "framing non ammesso")
        if mode == "safe_crop":
            block(s.get("no_faces_cut_reviewed") is True, label + "crop volti non controllato")
        if kind.startswith("archive") or kind == "reveal":
            block(bool(s.get("source_id") and s.get("source_page") and s.get("rights_checked")),
                  label + "provenienza o diritti incompleti")
            # V59: non-commercial use is not the requirement for original footage.
            # The historical FILM itself must be PD/CC0.
            license_name = s.get("source_license")
            license_id = license_name.strip().upper() if isinstance(license_name, str) else ""
            block(license_id in {"CC0", "CC0 1.0", "PUBLIC_DOMAIN", "PDM"},
                  label + "V59: la ripresa non e' documentata PD/CC0")
            block(s.get("nonmonetized_publication_rights_checked") is True,
                  label + "V59: diritti pubblicazione non monetizzata assenti")
            if license_id in ("PUBLIC_DOMAIN", "PDM"):
                block(s.get("jurisdiction_reviewed") is True,
                      label + "V59: stato PD/PDM non verificato per Italia e origine")
        if kind == "reveal":
            revealed = True
            block(s.get("same_source_and_frames_verified") is True,
                  label + "B/N e colore non provengono dallo stesso movimento")
            block(s.get("semantic_color_reviewed") is True, label + "colore AI non controllato")
            rs, rd = s.get("reveal_at"), s.get("reveal_seconds")
            block(isinstance(rs, (float, int)) and isinstance(rd, (float, int))
                  and rs >= 0 and rd > 0 and isinstance(d, (float, int)) and rs + rd <= d,
                  label + "rivelazione non valida")
            keys = ("bw_file", "color_file")
        else:
            keys = ("file",)
            if kind == "archive_color":
                block(s.get("semantic_color_reviewed") is True, label + "colore non controllato")
            if kind == "ai_reconstruction":
                block(bool(s.get("story_boundary") and s.get("disclosure")),
                      label + "ricostruzione senza spiegazione")
                block(not s.get("paid_generation_used") or s.get("specific_clip_spend_authorized") is True,
                      label + "Vidu senza autorizzazione per la singola clip")
        for key in keys:
            f = s.get(key)
            block(bool(f and Path(f).is_file() and Path(f).stat().st_size),
                  label + "file mancante: " + key)
        if kind in ("reveal", "archive_color") and not plan.get("test_only"):
            colorfile = s.get("color_file") if kind == "reveal" else s.get("file")
            reportpath = s.get("v57_gate_report")
            if not colorfile or not Path(colorfile).is_file() or not reportpath or not Path(reportpath).is_file():
                errors.append(label + "rapporto V57 assente")
            else:
                try:
                    report = json.loads(Path(reportpath).read_text(encoding="utf8"))
                    block(report.get("ok") is True and report.get("video_sha256") == digest(colorfile)
                          and report.get("method_declared") not in ("sepia_tint", "bw_original", ""),
                          label + "V57 non superato o riferito a filmato diverso")
                except (ValueError, OSError):
                    errors.append(label + "rapporto V57 illeggibile")
    block(revealed, "Manca una vera rivelazione B/N→colore AI")
    block(0 < total <= 60, "Durata totale non idonea")
    music = plan.get("audio", {})
    if music.get("file"):
        block(Path(music["file"]).is_file() and music.get("licensed_for_reuse") is True,
              "Musica senza file/licenza")
    return errors, round(total, 3)


def geom(s, w, h):
    if s.get("framing") == "safe_crop":
        return "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (w, h, w, h)
    return "scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=black" % (w, h, w, h)


def cmd(s, out, w, h):
    start, duration = str(s["start"]), str(s["duration"])
    lead = ["ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "error"]
    def source(path):
        return ["-ss", start, "-t", duration, "-i", str(path)]
    lead += source(s["bw_file"] if s["kind"] == "reveal" else s["file"])
    f = "fps=24," + geom(s, w, h) + ",setsar=1,format=yuv420p,setpts=PTS-STARTPTS"
    if s["kind"] == "reveal":
        lead += source(s["color_file"])
        t, d = float(s["reveal_at"]), float(s["reveal_seconds"])
        alpha = "clip((T-%.3f)/%.3f,0,1)" % (t, d)
        graph = "[0:v]%s[bw];[1:v]%s[col];[bw][col]blend=all_expr='A*(1-%s)+B*%s'[v]" % (f, f, alpha, alpha)
    else:
        graph = "[0:v]%s[v]" % f
    if s["kind"] == "ai_reconstruction":
        graph = graph.replace("[v]", "[pre]", 1)
        graph += ";[pre]drawtext=text='RICOSTRUZIONE AI':fontcolor=white:fontsize=30:box=1:boxcolor=black@0.7:x=(w-text_w)/2:y=h*0.08[v]"
    return lead + ["-filter_complex", graph, "-map", "[v]", "-an", "-r", "24", "-c:v", "libx264",
                   "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", str(out)]


def execff(arguments):
    return subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=True, timeout=300)


def render(plan, destination):
    problems, duration = check(plan)
    if problems:
        raise ValueError("; ".join(problems))
    output = Path(destination).resolve()
    if output.exists():
        raise ValueError("Non sovrascrivere file esistente")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="storia_v58_") as work:
        folder = Path(work)
        parts = []
        for i, scene in enumerate(plan["scenes"]):
            part = folder / ("scene_%02d.mp4" % i)
            execff(cmd(scene, part, plan["width"], plan["height"]))
            parts.append(part)
        listing = folder / "concat.txt"
        listing.write_text("".join("file '%s'\n" % p for p in parts), encoding="utf8")
        temp = folder / "joined.mp4"
        execff(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "concat",
                "-safe", "0", "-i", str(listing), "-c", "copy", str(temp)])
        soundtrack = plan.get("audio", {}).get("file")
        if soundtrack:
            audio_args = ["-stream_loop", "-1", "-i", str(soundtrack)]
        else:
            audio_args = ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        command = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(temp)] + audio_args
        command += ["-map", "0:v", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "128k", "-t", str(duration), "-movflags", "+faststart", str(output)]
        execff(command)
    manifest = {"status": "rendered_needs_review_and_V55_delivery", "video_sha256": digest(output),
                "scene_count": len(plan["scenes"]), "duration_requested_s": duration,
                "music": "user_provided_licensed" if soundtrack else "silent_aac",
                "ai_colorization_performed_here": False, "no_paid_calls": True,
                "archive_and_android_delivery_verified": False}
    Path(str(output) + ".json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8")
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True)
    p.add_argument("--check", action="store_true")
    p.add_argument("--out")
    args = p.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding="utf8"))
    errors, seconds = check(plan)
    print(json.dumps({"ok": not errors, "errors": errors, "duration_seconds": seconds},
                     ensure_ascii=False, indent=2))
    if errors:
        return 2
    if args.check:
        return 0
    if not args.out:
        p.error("--out necessario senza --check")
    try:
        print(json.dumps(render(plan, args.out), ensure_ascii=False, indent=2))
    except (ValueError, subprocess.CalledProcessError) as exc:
        print("Render non certificato: " + str(exc))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
