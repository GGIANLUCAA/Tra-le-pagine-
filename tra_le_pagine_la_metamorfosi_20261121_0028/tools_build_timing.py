#!/usr/bin/env python3
"""Tra le Pagine - allineamento sottotitoli e cue di scena.
Usa i tempi parola di Whisper (se disponibili) altrimenti i tempi frase della sintesi."""
import json, os, re, difflib

D = "/workspace/tra_le_pagine_la_metamorfosi_20261121_0028"

raw = open(f"{D}/COPIONE.txt", encoding="utf-8").read().strip()
full = re.sub(r"\s+", " ", raw)

# ---- tokenizza il testo noto, con posizione carattere ----
tokens = []  # (norm, start_char, end_char, trailing_punct)
for m in re.finditer(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", full):
    tokens.append({"t": m.group(0), "cs": m.start(), "ce": m.end(),
                   "punct": full[m.end():m.end()+1]})

def norm(s):
    return re.sub(r"[^a-zà-ÿ0-9]", "", s.lower())

# ---- tempi parola ----
wt = None
wsp = f"{D}/audio/whisper_raw.json"
if os.path.exists(wsp):
    wraw = json.load(open(wsp, encoding="utf-8"))["words"]
    wa = [{"n": norm(w["w"]), "s": w["start"], "e": w["end"]} for w in wraw if norm(w["w"])]
    my = [{"n": norm(t["t"]), "t": t} for t in tokens]
    sm = difflib.SequenceMatcher(None, [x["n"] for x in my], [x["n"] for x in wa], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if i1 == i2:
            continue
        if tag == "equal":
            for k in range(i2 - i1):
                my[i1 + k]["s"] = wa[j1 + k]["s"]; my[i1 + k]["e"] = wa[j1 + k]["e"]
        else:
            span_s = wa[j1]["s"] if j1 < len(wa) else (my[i1-1].get("e", 0) if i1 else 0)
            span_e = wa[j2-1]["e"] if j2-1 >= 0 and j2-1 < len(wa) else span_s + 0.3
            n = i2 - i1
            step = (span_e - span_s) / max(n, 1)
            for k in range(n):
                my[i1 + k]["s"] = span_s + k * step
                my[i1 + k]["e"] = span_s + (k + 1) * step
    # fallback riempi buchi
    last = 0.0
    for x in my:
        if "s" not in x: x["s"] = last; x["e"] = last + 0.25
        last = x["e"]
    wt = my
else:
    # fallback: tempi distribuiti proporzionalmente sulla durata della sintesi
    st = json.load(open(f"{D}/audio/sentence_times.json", encoding="utf-8"))
    total_dur = st[-1]["end"]
    total_chars = len(full)
    for t in tokens:
        frac = t["cs"] / total_chars
        t["s"] = frac * total_dur
        t["e"] = t["s"] + 0.2
    wt = [{"n": norm(t["t"]), "t": t, "s": t["s"], "e": t["e"]} for t in tokens]

for x in wt:
    x["t"]["s"] = x["s"]; x["t"]["e"] = x["e"]

AUDIO_END = max(x["e"] for x in wt)

# ---- costruzione cue sottotitoli ----
MAXC = 84
cues = []
cur = []
def flush():
    global cur
    if not cur: return
    text = " ".join(t["t"] for t in cur)
    cues.append({"start": round(cur[0]["s"], 3), "end": round(cur[-1]["e"], 3), "text": text})
    cur = []

for t in wt:
    cur.append(t["t"])
    length = sum(len(x["t"]) + 1 for x in cur)
    is_end = t["t"]["punct"] in ".!?"
    is_comma = t["t"]["punct"] in ",;:—"
    if is_end or length >= MAXC or (is_comma and length >= MAXC * 0.55):
        flush()

# rimuovi spazi/gap: estendi fine cue fino all'inizio del prossimo (max +0.4)
for i, c in enumerate(cues):
    nxt = cues[i + 1]["start"] if i + 1 < len(cues) else AUDIO_END
    c["end"] = round(min(nxt, max(c["end"] + 0.25, c["start"] + 0.6)), 3)

# ---- cue di scena ----
sc = json.load(open(f"{D}/scene_cues.json", encoding="utf-8"))
scene_times = []
for s in sc:
    ph = s["start_phrase"]
    if ph == "__END_BRAND__":
        scene_times.append({"scene": s["scene"], "asset": s["asset"], "start": round(AUDIO_END, 3)})
        continue
    ci = full.find(ph)
    if ci < 0:
        raise SystemExit(f"frase non trovata: {ph}")
    tok = next((x for x in wt if x["t"]["cs"] >= ci), wt[-1])
    scene_times.append({"scene": s["scene"], "asset": s["asset"],
                        "start": round(tok["s"], 3), "phrase": ph})

json.dump({"audio_end": round(AUDIO_END, 3), "cues": cues, "scene_times": scene_times},
          open(f"{D}/audio/timing.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- SRT ----
def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
with open(f"{D}/subtitles/sottotitoli.srt", "w", encoding="utf-8") as f:
    for i, c in enumerate(cues, 1):
        f.write(f"{i}\n{fmt(c['start'])} --> {fmt(c['end'])}\n{c['text']}\n\n")

# ---- ASS (burn-in) ----
def ass_t(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TLP,DejaVu Sans,62,&H00F6F1E6,&H000000FF,&H00201008,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
def wrap_2(s):
    if len(s) <= 44: return s
    words = s.split(); best = None; acc = 0
    for i, w in enumerate(words):
        acc += len(w) + 1
        if best is None or abs(acc - len(s) / 2) < best[0]:
            best = (abs(acc - len(s) / 2), i)
    i = best[1]
    return " ".join(words[:i + 1]) + "\\N" + " ".join(words[i + 1:])
with open(f"{D}/subtitles/sottotitoli.ass", "w", encoding="utf-8") as f:
    f.write(hdr)
    for c in cues:
        f.write(f"Dialogue: 0,{ass_t(c['start'])},{ass_t(c['end'])},TLP,,0,0,0,,{wrap_2(c['text'])}\n")

print("words aligned:", len(wt), "| cues:", len(cues), "| audio_end:", round(AUDIO_END, 2))
for st in scene_times:
    print("scene", st["scene"], st["asset"], st["start"])
