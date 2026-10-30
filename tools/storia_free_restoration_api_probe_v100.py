#!/usr/bin/env python3
"""V100: read-only availability check for public historical photo restoration Spaces.

Only HTTPS GET requests to trusted Hugging Face metadata / API schema hosts.
Never submits images, never consumes inference quota, never calls paid services.
The result is a capability scout, NOT proof of photographic quality.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SPACES = {
    "finegrain": ("finegrain/finegrain-image-enhancer", "finegrain-finegrain-image-enhancer"),
    "codeformer": ("sczhou/CodeFormer", "sczhou-codeformer"),
    "gfpgan_legacy": ("tkawano/GFPGAN", "tkawano-gfpgan"),
}
MAX_READ = 2 * 1024 * 1024


def get_json(url: str) -> tuple[dict | None, str]:
    req = Request(url, headers={"User-Agent": "TraLePagine-FreeRestoration-Availability/1.0",
                                "Accept": "application/json"})
    try:
        with urlopen(req, timeout=15) as response:
            raw = response.read(MAX_READ + 1)
            if len(raw) > MAX_READ:
                return None, "response_too_large"
            data = json.loads(raw.decode("utf-8"))
            return (data, "ok") if isinstance(data, dict) else (None, "not_an_object")
    except HTTPError as exc:
        return None, f"http_{exc.code}"
    except (TimeoutError, URLError, OSError, UnicodeError, json.JSONDecodeError):
        return None, "unavailable"


def run() -> dict:
    report = {
        "schema": "storia-free-restoration-v100-readonly",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "cost_eur": 0,
        "generation_calls": 0,
        "uploads": 0,
        "tests_performed": ["public_space_metadata", "public_gradio_openapi"],
        "warning": "GET-based API reachability is not evidence of usable free inference, quota, or artistic quality.",
        "spaces": [],
    }
    for key, (repo, subdomain) in SPACES.items():
        metadata, metadata_status = get_json(
            f"https://huggingface.co/api/spaces/{repo}?expand=runtime&expand=sdk&expand=private"
        )
        endpoint, endpoint_status = get_json(
            f"https://{subdomain}.hf.space/gradio_api/openapi.json"
        )
        row = {
            "id": key, "space": repo, "metadata_status": metadata_status,
            "schema_status": endpoint_status,
            "runtime_stage": (metadata or {}).get("runtime", {}).get("stage")
                if isinstance((metadata or {}).get("runtime"), dict) else None,
            "sdk": (metadata or {}).get("sdk"),
            "private": (metadata or {}).get("private"),
            "api_paths": [
                p for p in ((endpoint or {}).get("paths") or {})
                if "/call/" in p or "/run/" in p or p.endswith("/predict")
            ][:12],
            "inference_tested": False,
            "free_quota_verified": False,
            "quality_tested": False,
        }
        report["spaces"].append(row)
        print(f"{key} metadata={metadata_status} runtime={row['runtime_stage']} "
              f"gradio_schema={endpoint_status} endpoints={len(row['api_paths'])}", flush=True)
    out = Path("output/storia_free_services_v100")
    out.mkdir(parents=True, exist_ok=True)
    (out / "READONLY_API_SCOUT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    report = run()
    print("READONLY_SCOUT_DONE_NO_API_INFERENCE_NO_CHARGE", flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        lines = [
            "## La Storia Rivive V100 — public free-restoration API scout",
            "",
            "**No image generation, no GPU consumption, no paid calls.**",
            "",
            "| Space | Metadata | Runtime | Gradio API |",
            "|---|---|---|---|",
        ]
        for item in report["spaces"]:
            lines.append(f"| {item['space']} | {item['metadata_status']} | "
                         f"{item['runtime_stage'] or 'unknown'} | {item['schema_status']} |")
        Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
