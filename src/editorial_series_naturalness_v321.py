#!/usr/bin/env python3
"""Offline, read-only audit of repeated narrative habits across REAL recipe files.

It does not detect AI authorship or approve a story. It reads actual chapter text
from selected production recipes, and optionally legacy renderer camera constants.
No network, voice generation, new videos, publication, master modification or API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from editorial_human_naturalness_v1 import review as script_review

SCHEMA = "editorial-series-naturalness-v321"
MAX_FILES = 40

# Suggestions, not prohibitions: a lyrical ending can be legitimate.
# Only the LAST SPOKEN SENTENCE is checked, never earlier quotations or context.
ABSTRACT_ENDING_PATTERNS = [
    r"\b(?:ci|ti|vi)\s+invita\s+a\b",
    r"\bquanto\s+sia\s+(?:fragile|importante|compless[oa])\b",
    r"\b(?:la|il)\s+(?:sua\s+)?forza\s+nasce\b",
    r"\bsta\s+(?:gran\s+parte\s+)?della\s+(?:sua|loro)\s+forza\b",
]


def _normalize(text):
    return " ".join(re.findall(r"[^\W_]+(?:['’][^\W_]+)?", text.lower(), re.UNICODE))


def _sentences(text):
    return [t.strip() for t in re.split(r"(?<=[.!?])\s+", text) if t.strip()]


def _extract(path):
    path = Path(path)
    raw = path.read_bytes()
    data = json.loads(raw)
    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise ValueError(f"{path}: chapters array is required; no fabricated text")
    texts = [x.get("text") if isinstance(x, dict) else None for x in chapters]
    if any(not isinstance(x, str) or not x.strip() for x in texts):
        raise ValueError(f"{path}: every real chapter must contain text")
    script = "\n\n".join(texts)
    opening = _sentences(texts[0])[0]
    ending = _sentences(texts[-1])[-1]
    return {
        "recipe_path":str(path),
        "recipe_sha256":hashlib.sha256(raw).hexdigest(),
        "title":data.get("public_title") or data.get("work_id") or path.stem,
        "source_work_id":data.get("work_id") or path.stem,
        "variant":data.get("variant", "unspecified"),
        "chapter_count":len(texts),
        "sentence_count":sum(len(_sentences(x)) for x in texts),
        "word_count":len(_normalize(script).split()),
        "opening":opening,
        "ending":ending,
        "first_chapter":texts[0],
        "last_chapter":texts[-1],
        "all_script":script,
    }


def _static_director(renderer):
    """Inspect literals as documentary evidence, never assume they rendered."""
    if renderer is None:
        return None
    p=Path(renderer)
    raw=p.read_text(encoding="utf-8")
    match=re.search(r"(?m)^\s*DELAY\s*,\s*TAIL\s*=\s*([0-9.]+)\s*,\s*([0-9.]+)\s*$",raw)
    if not match:
        return {"file":str(p),"opening_delay_s":None,"outro_tail_s":None,
                "note":"No static opening/tail literals detected: no inference"}
    return {"file":str(p),"opening_delay_s":float(match.group(1)),
            "outro_tail_s":float(match.group(2)),
            "note":"Source-code constants only, not measured in a rendered MP4"}


def _similarity(a,b):
    # Designed to spot literal repeated phrasing, not synonymous descriptions.
    a,b=_normalize(a),_normalize(b)
    return round(SequenceMatcher(None,a,b,autojunk=False).ratio(),3) if a and b else 0


def _issue(code, where, fix, detail, episodes=None):
    result={"code":code,"where":where,"detail":detail,"fix":fix,
            "severity":"editorial_review_only"}
    if episodes:
        result["episodes"]=episodes
    return result


def inspect_paths(recipes, renderers=None):
    paths=list(map(Path,recipes))
    if not (2 <= len(paths) <= MAX_FILES):
        raise ValueError("Compare between 2 and 40 existing scripts, not one guessed text")
    if len({str(p.resolve()) for p in paths})!=len(paths):
        raise ValueError("Do not count duplicate recipe files as separate episodes")
    if renderers is not None and len(renderers)!=len(paths):
        raise ValueError("Renderers must be one-to-one with recipes")
    episodes=[_extract(p) for p in paths]
    warnings=[]
    for i,ep in enumerate(episodes):
        v320=script_review(ep["all_script"],format_name="artvision_critico")
        ep["v320_blocking"]=[x["code"] for x in v320["blocking"]]
        ep["v320_warnings"]=[x["code"] for x in v320["warnings"]]
        ep["renderer"]=_static_director(renderers[i]) if renderers is not None else None
        # Existing recordings are never automatically invalidated or redone.
        ep["existing_voice_must_remain_untouched"]=True
        ep["requires_artistic_relisten"]=True
        if ep["v320_blocking"]:
            warnings.append(_issue("LEGACY_STOCK_ENDING","episode",
                "Per eventuale NUOVO copione: finale specifico dell'opera; NON toccare il WAV attuale.",
                f"{ep['title']}: {', '.join(ep['v320_blocking'])}",[ep["recipe_path"]]))
        if any(re.search(pattern, ep["ending"], re.IGNORECASE | re.UNICODE)
               for pattern in ABSTRACT_ENDING_PATTERNS):
            warnings.append(_issue("ABSTRACT_STOCK_LIKE_ENDING","episode",
                "Rileggere il finale: preferire gesto, immagine o fatto documentato. "
                "Non cancellare automaticamente una chiusa intenzionalmente poetica.",
                f"{ep['title']}: {ep['ending'][:160]}",[ep["recipe_path"]]))

    pairs=[]
    for i,a in enumerate(episodes):
        for b in episodes[i+1:]:
            oscore=_similarity(a["opening"],b["opening"])
            escore=_similarity(a["ending"],b["ending"])
            pairs.append({"a":a["recipe_path"],"b":b["recipe_path"],
                          "opening_phrase_similarity":oscore,
                          "ending_phrase_similarity":escore})
            if oscore>=.76:
                warnings.append(_issue("SIMILAR_OPENING","cross_episode",
                    "Rivedere soltanto l'apertura della nuova puntata: partire dal suo dettaglio distinto.",
                    f"{a['title']} / {b['title']}: similarità letterale {oscore}",
                    [a["recipe_path"],b["recipe_path"]]))
            if escore>=.76:
                warnings.append(_issue("SIMILAR_CLOSING","cross_episode",
                    "Riscrivere il finale nuovo perché chiuda questa storia soltanto.",
                    f"{a['title']} / {b['title']}: similarità letterale {escore}",
                    [a["recipe_path"],b["recipe_path"]]))

    counts=Counter(e["chapter_count"] for e in episodes)
    common, count=counts.most_common(1)[0]
    if len(episodes)>=3 and count >= max(3, int(len(episodes)*.8)):
        warnings.append(_issue("UNIFORM_CHAPTER_COUNT","cross_episode",
           "Non imporre sempre lo stesso numero di beat; scegliere il numero in base al racconto.",
           f"{count}/{len(episodes)} ricette hanno {common} capitoli; indice di struttura ripetitiva, non errore certo."))

    if renderers is not None:
        known=[e for e in episodes if e["renderer"] and
               e["renderer"]["opening_delay_s"] is not None]
        if len(known)>=3:
            patterns=Counter((e["renderer"]["opening_delay_s"],
                              e["renderer"]["outro_tail_s"]) for e in known)
            pair,count=patterns.most_common(1)[0]
            if count>=3:
                warnings.append(_issue("UNIFORM_RENDERER_PACING","cross_episode",
                    "Valutare A/B della vera apertura/finale prima di imporre un nuovo tempo. "
                    "I costanti sono del CODICE, non misure del video finale.",
                    f"{count}/{len(known)} renderer hanno delay {pair[0]}s e coda {pair[1]}s."))
    doc_episodes=[{k:v for k,v in ep.items() if k!="all_script"} for ep in episodes]
    return {
        "schema":SCHEMA,"status":"editorial_review_required" if warnings else "no_pattern_reported_review_still_required",
        "episode_count":len(episodes),
        "episodes":doc_episodes,
        "pairwise_literal_similarity":pairs,
        "observations":warnings,
        "priority_recommendations":warnings[:6],
        "limitations":(
          "Text comparisons notice near-identical phrasing only, not semantic repetition, "
          "historical truth, performance or how rendered shots actually look. "
          "Source-code camera constants are not measured MP4 evidence."
        ),
        "human_approved":False,"video_reviewed":False,
        "changed_audio":False,"changed_master":False,
        "published":False,"paid_calls":0,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--recipe",action="append",type=Path,required=True)
    p.add_argument("--renderer",action="append",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    r=inspect_paths(args.recipe,args.renderer)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":r["status"],"episode_count":r["episode_count"],
                      "issues":[x["code"] for x in r["observations"]]},
                     ensure_ascii=False))
    return 0  # Historical scripts must not retroactively block old accepted MP4s.


if __name__=="__main__":
    raise SystemExit(main())
