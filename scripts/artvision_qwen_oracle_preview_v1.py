"""Generate a private Qwen voice audition through an existing secured server."""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from artvision_qwen_oracle_tts_v1 import DEFAULT_TEXT, generate_preview


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script-file", type=Path)
    parser.add_argument("--out", default="output/qwen-oracle-preview")
    parser.add_argument("--speaker", default=os.getenv("ARTVISION_QWEN_SPEAKER", "ryan"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    content = args.script_file.read_text(encoding="utf-8") if args.script_file else (
        os.environ.get("ARTVISION_QWEN_PREVIEW_TEXT") or DEFAULT_TEXT
    )
    report = generate_preview(content, args.out, speaker=args.speaker, force=args.force)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
