#!/usr/bin/env python3
"""V134 public-facing naming guard for *AI drafts*, not an artistic QA approval.

ECC-inspired deterministic rule enforcement: do not rely on a model remembering
prompts. Existing production/publication gates still take precedence.
"""
from __future__ import annotations

import re

FORBIDDEN_PUBLIC_LABELS = (
    re.compile(r"\bartvision\b", re.IGNORECASE),
    re.compile(r"\btra\s+le\s+pagine\b", re.IGNORECASE),
    re.compile(r"\bcinema\s+standard\b", re.IGNORECASE),
    re.compile(r"\bcritico\s+standard\b", re.IGNORECASE),
    re.compile(r"\bstandard\b", re.IGNORECASE),
)


def public_copy_violations(text: str) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return ["empty_public_copy"]
    errors = []
    for phrase in FORBIDDEN_PUBLIC_LABELS:
        if phrase.search(text):
            errors.append("forbidden_public_label")
            break
    return errors
