#!/usr/bin/env python3
"""Recover only failed museum #4 with a Wikimedia Commons mirror of the exact Met painting."""
from pathlib import Path
import subprocess,sys
source=Path("tools/artvision_cromatica_batch_ten_20261120.py")
txt=source.read_text(encoding="utf-8")
needle='art_fetch=fetch(meta["primaryImage"],ASSETS/"original_work.jpg",100_000)'
assert txt.count(needle)==1,"Unexpected source revision"
repair='''try:
    art_fetch=fetch(meta["primaryImage"],ASSETS/"original_work.jpg",100_000)
except Exception as original_exc:
    print("PRIMARY_MET_CDN_FAILED, USING VERIFIED WIKIMEDIA SAME PAINTING",str(original_exc)[:200],flush=True)
    alternatives=[
      "https://commons.wikimedia.org/wiki/Special:FilePath/Gifford_Sanford_Robinson_A_Gorge_In_The_Mountains.jpg",
      "https://commons.wikimedia.org/wiki/Special:FilePath/A_Gorge_in_the_Mountains_%28Kauterskill_Clove%29_MET_DT81.jpg",
    ]
    art_fetch=None
    for alt in alternatives:
        try:
            art_fetch=fetch(alt,ASSETS/"original_work.jpg",100_000)
            break
        except Exception as error:
            print("WIKIMEDIA_MIRROR_FAILED",str(error)[:120],flush=True)
    if not art_fetch:raise RuntimeError("Original public-domain painting image unavailable from BOTH museum and Wikimedia mirrors")
'''
patched=txt.replace(needle,repair)
target=Path("/tmp/artvision_10_recovery_gifford.py")
target.write_text(patched,encoding="utf-8")
sys.exit(subprocess.call([sys.executable,"-u",str(target),"--index","4"]))
