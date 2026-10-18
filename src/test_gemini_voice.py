"""Piccoli test della nuova regia vocale, senza usare chiavi API."""
from pathlib import Path
from gemini_voice import sentences, speech_directed, tokens, _estimated_timing
text=Path("episodes/01_scacchi/testo.txt").read_text(encoding="utf-8")
phrases=sentences(text)
assert len(phrases)==34, f"Numero frasi: {len(phrases)}"
director=speech_directed(text)
assert "<short pause>" in director and "<long pause>" in director
assert all(t in director for t in ("Come sopravvivere?", "Rinuncia alla partita"))
assert len(tokens(phrases[0]))>0
timed=_estimated_timing(phrases,150)
assert len(timed)==34
assert timed[0][1]==0 and abs(timed[-1][2]-150)<1e-5
assert all(timed[i][1]<=timed[i][2]<=timed[i+1][1]+1e-6 for i in range(33))
print("TEST GEMINI VOICE: OK, 34 frasi, pause semantiche, timeline calcolata.")
