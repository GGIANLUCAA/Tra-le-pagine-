#!/usr/bin/env python3
"""First scheduled ArtVision V31 autonomous episode: Evelyn De Morgan, The Storm Spirits.

Additive wrapper around tested V30 Cinema engine. Keeps Cinema V6 approved
graphics, V25/V28 release gates, music rights and existing films untouched.
Do not call it a human-approved Gold Master; human review is still pending.
"""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("artvision_cinema_duo_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_autoproduction_20261024_1715.json"

if __name__=="__main__":
    engine.main()
