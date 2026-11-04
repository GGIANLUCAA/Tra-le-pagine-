#!/usr/bin/env python3
"""GitHub Actions secret-presence audit; NO network/credential contents.

Boolean checks only. A present secret does not prove account entitlement,
key validity, spending limits, commercial terms, or a usable API.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

# Note: duplicate/reserve credentials are NEVER automatically selected
# for remote API calls or to evade provider throttling or charges.
SECRETS = (
    "AIHORDE_API_KEY", "AIHORDE_API_KEY_2",
    "GEMINI_API_KEY", "GEMINI_API_KEY2", "GEMINI_API_KEY_2",
    "GROQ_API_KEY", "GROQ",
    "NVIDIA_API_KEY", "NVIDIA", "NVIDIA_NIM_API_KEY", "NVIDIA_NIM",
    "NGC_API_KEY", "INVIDIA", "INVIDIA_API_KEY",
    "HF_TOKEN", "HUGGINGFACE_TOKEN",
    "OPENROUTER_API_KEY", "OPENROUTER2",
    "PIXABAY", "PIXABAY_API_KEY", "PRIXIBAY2",
    "VIDUOK", "VIDU_API_KEY", "VIDU", "VIDU2",
)
PROVIDERS = (
    ("AI Horde primary", ("AIHORDE_API_KEY",), "manual_image_pilot"),
    ("AI Horde reserve", ("AIHORDE_API_KEY_2",), "reserved_not_active"),
    ("Gemini TTS primary", ("GEMINI_API_KEY",), "voice_workflows_conditional"),
    ("Gemini TTS second", ("GEMINI_API_KEY2", "GEMINI_API_KEY_2"), "voice_workflows_conditional"),
    ("Groq", ("GROQ_API_KEY", "GROQ"), "draft_adapter_disabled_by_zero_cost_policy"),
    ("NVIDIA NIM", ("NVIDIA_API_KEY", "NVIDIA", "NVIDIA_NIM_API_KEY",
                     "NVIDIA_NIM", "NGC_API_KEY", "INVIDIA",
                     "INVIDIA_API_KEY"), "developer_trial_research_only_no_live_calls"),
    ("Hugging Face", ("HF_TOKEN", "HUGGINGFACE_TOKEN"), "restoration_jobs_conditional"),
    ("OpenRouter", ("OPENROUTER_API_KEY", "OPENROUTER2"), "recognized_no_inference"),
    ("Pixabay primary", ("PIXABAY", "PIXABAY_API_KEY"), "manual_search_bridge"),
    ("Pixabay secondary", ("PRIXIBAY2",), "reserved_unverified_not_used"),
    ("Vidu API primary", ("VIDUOK", "VIDU_API_KEY"), "balance_and_video_workflows_guarded"),
    ("Vidu other", ("VIDU", "VIDU2"), "not_auto_selected_for_api"),
)


def make_report(environ: dict[str, str] | None = None) -> dict:
    env = environ if environ is not None else os.environ
    flags = {name: bool(env.get("AUDIT_" + name, "").strip()) for name in SECRETS}
    providers = []
    for service, aliases, use in PROVIDERS:
        matches = [name for name in aliases if flags[name]]
        providers.append({
            "service": service,
            "secret_present": bool(matches),
            "matching_secret_names": matches,
            "integration_stage": use,
            "api_validated": False,
            "billing_verified": False,
            "live_api_called": False,
        })
    return {
        "schema": "studio-secrets-audit-v1",
        "scope": "GitHub Actions repository/environment resolution during this run",
        "never_report_values": True,
        "provider_calls": 0,
        "calls_to_paid_services": 0,
        "secret_presence": flags,
        "providers": providers,
        "important": (
            "Present only means available to the workflow. It does not verify "
            "key authorization, paid plan, free tier, available credits, "
            "API validity, or actual completed video delivery."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = make_report()
    print("PRESENCE_ONLY_AUDIT")
    for item in report["providers"]:
        state = "PRESENT" if item["secret_present"] else "NOT_DETECTED"
        print(f'{item["service"]}: {state} | {item["integration_stage"]}')
    print("NO_PROVIDER_API_CALLS; NO_KEY_VALUES_EXPOSED")
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
