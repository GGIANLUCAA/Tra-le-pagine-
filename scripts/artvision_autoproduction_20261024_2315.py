#!/usr/bin/env python3
"""ArtVision V31 scheduled 23:15: Hugo Simberg, The Wounded Angel (1903).
Use tested V30 Cinema renderer; approved V6 graphics, V25/V28 gates,
museum-authentic image and independent CC BY recording. No social posting.
"""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("artvision_cinema_duo_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_autoproduction_20261024_2315.json"
if __name__=="__main__":
    engine.main()
