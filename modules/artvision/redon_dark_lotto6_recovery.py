#!/usr/bin/env python3
"""Redon final: 112s, at least seven individually verified public art sources."""
import artvision_dark_lotto6 as cfg
import redon_shortfilm_v6 as cinema
cinema.ROOT=cfg.studio.ROOT
cinema.P.clear()
cinema.P["redon"]=cfg.studio.P["redon"]
cinema.suitable_filename=cfg.filename_ok
if __name__=="__main__":
 cinema.make("redon")
