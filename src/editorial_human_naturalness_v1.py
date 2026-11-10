#!/usr/bin/env python3
"""Editorial naturalness review, not an "AI detector".

This conservative offline pre-TTS gate flags a few recognisable boilerplate
phrases, especially templated philosophical closings. It cannot prove that
content is human-written, factual, compelling, or genuinely reviewed.

Never rewrite factual content automatically or silently modify a cached WAV.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCHEMA = "editorial-human-naturalness-v1"

# Phrases are assessed only in the actual last paragraph: the same words may
# sometimes be meaningful in the narration body. Keep the hard set narrow.
FINAL_BLOCK = [
    ("STOCK_FINAL_QUESTION", r"\b(?:il quadro|l'opera|questa storia|il filmato|il dipinto)\s+(?:ci|ti|vi)\s+lascia\s+(?:con\s+)?(?:una|la)\s+domanda\b"),
    ("STOCK_FINAL_INVITATION", r"\b(?:il quadro|l'opera|questa storia|l'artista|il dipinto)\s+(?:ci|ti|vi)\s+invita\s+a\s+riflettere\b"),
    ("STOCK_UNIVERSAL_MORAL", r"\b(?:forse|in fondo)\s+(?:il vero|la vera)\s+(?:mistero|segreto|risposta|lezione)\s+(?:è|sta)\b"),
]

ALL_REVIEW = [
    ("FORMULA_NOT_JUST_BUT", r"\bnon\s+(?:è|si tratta)\s+(?:solo|soltanto|semplicemente)\b.{0,110}?\bma\s+(?:anche|è)\b"),
    ("SLOGAN_EVEN_TODAY", r"\bancora\s+oggi\s+(?:ci|continua\s+a|il|la)\b"),
    ("EFFECT_FIRST", r"\b(?:preparati|preparatevi)\s+(?:a\s+)?(?:scoprire|essere\s+sorpresi)\b"),
    ("GENERIC_REVEAL", r"\b(?:ma|e)\s+(?:c'è|c’è)\s+(?:di\s+)?più\b"),
]

def _normalize(value):
    if not isinstance(value, str):
        raise TypeError("A real script string is required")
    return re.sub(r"\s+", " ", value).strip()

def review(text, *, format_name="narrated", context="narration"):
    if context not in ("narration","social_copy","on_screen"):
        raise ValueError("Unknown editorial context")
    if not isinstance(format_name,str) or not format_name.strip():
        raise ValueError("Known format required")
    script=_normalize(text)
    if not script:
        return {"schema":SCHEMA,"status":"revision_required",
                "blocking":[{"code":"EMPTY_TEXT","where":"script",
                             "fix":"Scrivere un contenuto verificabile prima di richiedere una voce."}],
                "warnings":[],"human_approved":False,"ai_authorship_detected":False}
    paragraphs=[_normalize(p) for p in re.split(r"(?:\r?\n\s*){2,}",text)
                if _normalize(p)]
    ending=paragraphs[-1] if paragraphs else script
    # If authors write one long paragraph, the last ~55 words are the ending,
    # rather than treating an earlier paragraph's question as the finale.
    if len(paragraphs)==1:
        words=ending.split()
        ending=" ".join(words[-55:])
    blocking=[]
    warnings=[]
    for code,pattern in FINAL_BLOCK:
        if re.search(pattern,ending,re.IGNORECASE|re.UNICODE|re.DOTALL):
            blocking.append({"code":code,"where":"finale",
                             "fix":"Sostituire la formula con un particolare verificato dell'opera/storia e una conclusione sobria; niente morale inventata."})
    for code,pattern in ALL_REVIEW:
        count=len(re.findall(pattern,script,re.IGNORECASE|re.UNICODE|re.DOTALL))
        if count:
            warnings.append({"code":code,"where":"script",
                             "count":count,
                             "fix":"Verificare se la frase aggiunge un fatto o è retorica sostituibile; non eliminare automaticamente ogni figura stilistica."})
    if ending.endswith("?") and not any(x["code"]=="STOCK_FINAL_QUESTION" for x in blocking):
        warnings.append({"code":"FINAL_QUESTION_NEEDS_PURPOSE","where":"finale",
                         "fix":"Domanda finale ammessa soltanto se è concreta e nata dalla storia. Preferire una conclusione osservabile, senza interrogativo di routine."})
    abstract_words = re.findall(r"\b(?:umanità|esistenza|destino|eterno|eternità|bene|male|mistero)\b",
                                ending,re.IGNORECASE|re.UNICODE)
    if len(abstract_words)>=3:
        warnings.append({"code":"ABSTRACT_ENDING","where":"finale",
                         "fix":"Ritorna a un gesto, un dettaglio o un'immagine documentata; niente filosofia generica."})
    return {
        "schema": SCHEMA, "format":format_name, "context":context,
        "status":"revision_required" if blocking else
                 "needs_human_editorial_review" if warnings else "no_stock_phrases_found_not_approved",
        "blocking":blocking, "warnings":warnings,
        "review_questions":[
            "La conclusione dice qualcosa di specifico che si può verificare nelle immagini o nelle fonti?",
            "Le frasi suonano naturali se lette ad alta voce, senza enfasi artificiosa?",
            "Qualche frase potrebbe essere incollata uguale a un video diverso? Se sì, riscriverla.",
            "Il montaggio lascia vedere proprio ciò che si racconta?",
            "L'ultima frase chiude il discorso senza imporre una morale o una domanda generica?"
        ],
        "human_approved":False,"ai_authorship_detected":False,
        "new_tts_calls":0,"rewrote_script":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--script",type=Path,required=True)
    p.add_argument("--format",dest="format_name",default="narrated")
    p.add_argument("--context",choices=("narration","social_copy","on_screen"),default="narration")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    result=review(args.script.read_text(encoding="utf8"),format_name=args.format_name,context=args.context)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({"status":result["status"],
                      "blocking":[x["code"] for x in result["blocking"]],
                      "warnings":[x["code"] for x in result["warnings"]]},
                     ensure_ascii=False))
    return 2 if result["blocking"] else 0

if __name__=="__main__":
    raise SystemExit(main())
