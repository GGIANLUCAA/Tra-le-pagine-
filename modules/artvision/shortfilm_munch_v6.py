#!/usr/bin/env python3
"""Recupero singolo artista: Munch, senza modificare il modello Cinema V6 approvato."""
import batch5_ottobre21_v6 as preset
import cinema_v6_curated_shortfilm as engine
engine.ROOT=preset.v6.ROOT
engine.P.clear()
engine.P.update({"munch":preset.v6.P["munch"]})
engine.SOUND.update(preset.v6.SOUND)
engine.suitable_filename=preset.safe_filename
if __name__=="__main__":
    engine.make("munch")
