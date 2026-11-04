#!/usr/bin/env python3
"""Read-only inventory of four deliverable kits; never grants artistic approval."""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path


def inspect(root: Path, ids: list[str]) -> dict:
    if len(ids) != 4 or len(set(ids)) != 4:
        raise ValueError("exactly four distinct episode IDs required")
    results = []
    for episode in ids:
        if not episode.replace("_", "").replace("-", "").isalnum():
            raise ValueError("unsafe episode ID")
        folder = root / episode
        mp4, kit = folder / f"{episode}.mp4", folder / f"{episode}.zip"
        errors = []
        for path in (mp4, kit):
            if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
                errors.append(f"missing_or_invalid:{path.name}")
        if not errors:
            try:
                with zipfile.ZipFile(kit) as z:
                    if z.testzip() is not None:
                        errors.append("zip_crc_error")
                    names = set(z.namelist())
                    if not {mp4.name, "cover.png", "social_posts.json", "qa_report.json"} <= names:
                        errors.append("kit_missing_required_files")
                    if mp4.name in names and z.read(mp4.name) != mp4.read_bytes():
                        errors.append("kit_mp4_mismatch")
            except (OSError, zipfile.BadZipFile):
                errors.append("zip_invalid")
            try:
                proc = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "json", str(mp4)],
                    capture_output=True, text=True, check=True, timeout=20,
                )
                duration = float(json.loads(proc.stdout)["format"]["duration"])
                if not 14 <= duration <= 35:
                    errors.append("duration_out_of_range")
            except (OSError, ValueError, KeyError, subprocess.SubprocessError):
                errors.append("mp4_probe_failed")
        results.append({
            "episode_id": episode,
            "technical_kit_present": not errors,
            "errors": errors,
            "final_approved": False,
        })
    return {
        "technical_kits_present": sum(x["technical_kit_present"] for x in results),
        "final_approved_count": 0,
        "episodes": results,
        "note": "V91/V94/V96/V99, Italy rights and artistic approval require independent verification",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--episode", action="append", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = inspect(args.root, args.episode)
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
