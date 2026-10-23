#!/usr/bin/env python3
"""ArtVision V28: researched editorial social posts, NEVER process notes.
This tool does not generate generic AI-sounding captions. The author must
first provide a verified per-artwork editorial entry in config/artvision_editorial_v28.json.
Non-destructive: write only if the caller explicitly calls write_posts().
"""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"config/artvision_editorial_v28.json"
FILES={
 "facebook":"POST_FACEBOOK.txt",
 "instagram":"POST_INSTAGRAM.txt",
 "tiktok":"POST_TIKTOK.txt",
 "youtube":"POST_YOUTUBE.txt"
}
# These specific phrases tell the user how we made a film, not why the painting matters.
FORBIDDEN=(
 "ho scelto di partire", "in questo video ho", "in questo filmato ho",
 "ho deciso di mostrare", "regia cinematografica", "regia lenta", 
 "zoom", "inquadratur", "montaggio", "camera", "telecamera", 
 "sequenza di dettagli", "render", "intelligenza artificiale", 
 "ai-generated", "algoritmo", "script", "ti lascerà senza fiato",
 "lasciati trasportare", "un viaggio visivo", "un'opera che parla senza parole",
 "un dipinto che parla senza parole", "scrivi nei commenti", 
 "commenta qui sotto", "metti like", "condividi con tutti"
)
COPY_LIMITS={"facebook":(40,165),"instagram":(26,135),"tiktok":(20,85),"youtube":(40,190)}

def config():
    return json.loads(CATALOG.read_text(encoding="utf-8"))

def editorial_body(text):
    # Source and licensing are kept in a clearly separate footer. Review only
    # the narrative for banned production notes, not legally required credits.
    for split in ("\n\nFallen Angel (", "\n\nThe Wounded Angel (", "\n\nOpera:", "\n\nCrediti:"):
        if split in text: return text.split(split,1)[0].strip()
    return text.strip()

def validate_entry(key,entry):
    errors=[]
    def err(what):errors.append(f"{key}: {what}")
    for k in ("artist","title_en","museum","narrative_angle"):
        if not isinstance(entry.get(k),str) or len(entry[k].strip())<7:
            err(k+" missing")
    if len(entry.get("facts") or [])<1:
        err("at least one primary-sourced editorial fact required")
    if not entry.get("primary_sources"):
        err("museum or other primary reference required")
    for ref in entry.get("primary_sources",[]):
        if not str(ref.get("url","")).startswith("https://") or len(ref.get("supports",""))<15:
            err("source URL with specific supported claim required")
    if not 2<=len(entry.get("hashtags") or [])<=5:
        err("2-5 hashtags, no spam")
    for k in ("facebook","instagram","tiktok","youtube"):
        body=entry.get("captions",{}).get(k,"")
        if not isinstance(body,str):
            err(k+" caption missing");continue
        wc=len(body.split())
        lo,hi=COPY_LIMITS[k]
        if wc<lo or wc>hi:
            err(f"{k} body length {wc} outside editorial guidance {lo}-{hi}")
        lower=body.casefold()
        for phrase in FORBIDDEN:
            if phrase.casefold() in lower:
                err(f"{k} contains production/AI-marketing phrase '{phrase}'")
        if not any(term in lower for term in (
            entry.get("artist","").split(" ")[-1].casefold(),
            entry.get("title_en","").casefold())):
            err(f"{k} lacks the identity of the actual artwork or artist")
        if body.count("?")>1 or body.count("!")>2:
            err(f"{k} too many questions/exclamation marks")
    credits=entry.get("credit_lines",[])
    allcredits="\n".join(credits).casefold()
    for required in (entry.get("artist",""),entry.get("title_en",""),"musica:","cc by", "http"):
        if required.casefold() not in allcredits:err("missing required artwork/music/rights credit: "+required)
    return errors

def write_posts(key,folder,overwrite=True):
    # Full overwrite only on fresh generation paths (not existing user-modified
    # site entries). Never edits published items, history, or Library assets.
    entries=config()["entries"]
    if key not in entries:
        raise KeyError("No curated researched editorial entry for "+key+"; do NOT fabricate generic filler.")
    entry=entries[key]
    errors=validate_entry(key,entry)
    if errors:raise ValueError("V28_BLOCKED: "+"; ".join(errors))
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    footer="\n\n"+"\n".join(entry["credit_lines"])+"\n\n"+" ".join(entry["hashtags"])+"\n"
    written={}
    for platform,fn in FILES.items():
        path=folder/fn
        if path.exists() and not overwrite:
            raise FileExistsError("Preserve user-modified caption "+str(path))
        path.write_text(entry["captions"][platform].strip()+footer,encoding="utf-8")
        written[platform]=str(path)
    research={
      "schema":"artvision-editorial-research-v28",
      "status":"documented_editorial_draft_not_approved_viral_formula",
      "artist":entry["artist"],"title_en":entry["title_en"],"year":entry["year"],
      "museum":entry["museum"],"chosen_angle":entry["narrative_angle"],
      "verified_references":entry["primary_sources"],
      "claims_and_caveats":entry["facts"],
      "style":"Natural Italian art storytelling, not editing instructions",
      "human_editorial_review_required":True,
      "hashtags":entry["hashtags"],"files":written,
      "metadata_note":"Licensing details are reserved for the quiet footer and SOURCES_AND_RIGHTS.md"
    }
    rp=folder/"POST_EDITORIAL_RESEARCH.json"
    if rp.exists() and not overwrite:
        raise FileExistsError("Preserve user-modified editorial metadata")
    rp.write_text(json.dumps(research,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return written

def validate_folder(path):
    folder=Path(path)
    research=folder/"POST_EDITORIAL_RESEARCH.json"
    errors=[]
    if not research.exists():
        return ["POST_EDITORIAL_RESEARCH.json is missing: need verified facts and primary sources"]
    try:record=json.loads(research.read_text(encoding="utf-8"))
    except Exception as e:return ["Editorial research unreadable: "+str(e)]
    if record.get("schema")!="artvision-editorial-research-v28":
        errors.append("Missing V28 editorial schema")
    if not record.get("verified_references"):
        errors.append("No verified museum/research sources")
    sources=record.get("verified_references",[])
    if not any(str(s.get("url","")).startswith("https://") for s in sources):
        errors.append("At least one actual external source URL required")
    if not record.get("claims_and_caveats"):
        errors.append("No grounded facts recorded")
    for plat,fn in FILES.items():
        path=folder/fn
        if not path.is_file():
            errors.append("Missing caption file "+fn);continue
        txt=path.read_text(encoding="utf-8")
        body=editorial_body(txt)
        for phrase in FORBIDDEN:
            if phrase.casefold() in body.casefold():
                errors.append(fn+" contains forbidden process/AI marketing language: "+phrase)
        if "musica:" not in txt.casefold() or "cc by" not in txt.casefold():
            errors.append(fn+" missing music licence credit")
        if not body or len(body.split())<COPY_LIMITS[plat][0]:
            errors.append(fn+" lacks a substantial independent editorial story")
        if "https://" not in txt:
            errors.append(fn+" missing verifiable music/art source URLs")
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--episode",choices=list(config()["entries"]))
    ap.add_argument("--out")
    ap.add_argument("--validate-folder")
    args=ap.parse_args()
    if args.episode:
        if not args.out:ap.error("--episode requires --out")
        files=write_posts(args.episode,args.out,overwrite=False)
        print(json.dumps({"status":"DRAFT_CREATED","files":files},ensure_ascii=False))
    elif args.validate_folder:
        errors=validate_folder(args.validate_folder)
        print(json.dumps({"status":"BLOCKED" if errors else "PASS_OBJECTIVE_CAPTION_CHECKS",
                          "errors":errors,"note":"Not a certificate of human tone, actual facts or viral potential."},ensure_ascii=False,indent=2))
        return 1 if errors else 0
    else:ap.error("--episode with --out, or --validate-folder required")
    return 0

if __name__=="__main__":sys.exit(main())
