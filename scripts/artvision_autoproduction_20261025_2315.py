#!/usr/bin/env python3
"""ArtVision V33 additive runner: authentic Aivazovsky The Ninth Wave.
Uses existing V30 cinema engine, V6 visual identity, V25/V28 gates, no AI repaint.
"""
import importlib.util, json, sys, zipfile, hashlib
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("artvision_cinema_duo_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_autoproduction_20261025_2315.json"
SLUG="aivazovsky_ninth_wave_20261025_2315"

def full_opaque_museum_matte(art):
    """Single authentic full painting on a solid matte: no ghosting or blurred copy."""
    w,h=1080,1920
    bg=Image.new("RGB",(w,h),(5,8,13))
    whole=art.convert("RGB").copy()
    whole.thumbnail((1010,1500),Image.Resampling.LANCZOS)
    x=(w-whole.width)//2;y=(h-whole.height)//2
    ImageDraw.Draw(bg).rectangle((x-8,y-8,x+whole.width+7,y+whole.height+7),fill=(18,20,24))
    bg.paste(whole,(x,y))
    return bg

engine.cinema.full=full_opaque_museum_matte

def add_v32_and_v33():
    out=Path("output/artvision-v31-2315")
    folder=out/SLUG
    config=json.loads(engine.CONFIG.read_text(encoding="utf8"))
    b=config["subjects"]["ninth_wave"]
    candidates=[]
    for item in config["candidates_considered"]:
        candidates.append({
            "artist":item["artist"],"work":item["title"],
            "visual_hook":item["reason"],
            "human_interest":"Fragilità, sopravvivenza e luce dopo la tempesta" if item["title"]=="The Ninth Wave" else "Confronto di curiosità visiva",
            "historical_anchor":item["reason"],
            "asset_rights_notes":"Source/rights to review for non-selected candidate; selected work uses Commons PD-Art and State Russian Museum.",
            "comparison_reason":item["reason"],
            "audience_signal":{"status":"unavailable","reason":"Dati social comparabili non accessibili nel runner; giudizio qualitativo, non popolarità misurata"}
        })
    audience={"schema":"artvision-audience-research-v32","cycle_id":config["cycle_id"],
        "candidates":candidates,"selection_mode":"research_selected","selected_work":"The Ninth Wave",
        "selection_reason":"Opera autentica nuova nel registro; grande contrasto emotivo fra superstiti e alba; Commons 5815x3840 e fonte museale.",
        "viewer_interest":"Dopo la tempesta: saranno salvati? La luce offre una speranza documentata dalla scheda museale.",
        "creative_direction":"Dai superstiti al mare immenso, dalla cresta dell'onda alla luce; ritorno ai volti, chiusura quadro intero su fondale opaco.",
        "signal_limitations":"Nessun dato quantitativo verificato su Facebook/TikTok/YouTube; non si predicono visualizzazioni.",
        "analytics_feedback":"not_yet_published",
        "sources":["https://artsandculture.google.com/asset/wd/jgHuL-7yxgrOSw",
                   "https://commons.wikimedia.org/wiki/File:Aivazovsky,_Ivan_-_The_Ninth_Wave.jpg"],
        "checked_on":"2026-10-25"}
    media={"schema":"artvision-media-sourcing-v33","artwork_file":"ORIGINAL_ARTWORK.jpg",
        "provider":"Wikimedia Commons","source_reference":b["source_page"],
        "choice_reason":"Dipinto originale autentico, non ricostruzione, e nuova opera nel registro.",
        "scene_match_note":"Tutti i dettagli sono ritagli dello stesso dipinto originale.",
        "rights_review":"PD-Art Commons, riproduzione fedele; controllare regole territoriali prima della pubblicazione commerciale.",
        "scene_relevance":"verified_original","visual_review":"human_final_review_pending",
        "music_source":b["music"]["page"],"music_license":"CC BY 4.0"}
    (folder/"AUDIENCE_RESEARCH_V32.json").write_text(json.dumps(audience,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (folder/"MEDIA_SOURCING_V33.json").write_text(json.dumps(media,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    recipe_path=folder/"VIDEO_RECIPE_V13.json"
    recipe=json.loads(recipe_path.read_text(encoding="utf8"))
    recipe["audience_research_file"]="AUDIENCE_RESEARCH_V32.json"
    recipe["media_sourcing_file"]="MEDIA_SOURCING_V33.json"
    recipe["cycle_id"]=config["cycle_id"]
    recipe["rules_version"]="2026-10-25.3"
    recipe["render_status"]="technical_pass_not_gold_master"
    recipe_path.write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    bundle=out/("ARTVISION_V30_"+SLUG.upper()+"_COMPLETE.zip")
    with zipfile.ZipFile(bundle,"a",compression=zipfile.ZIP_DEFLATED) as z:
        for name in ["AUDIENCE_RESEARCH_V32.json","MEDIA_SOURCING_V33.json","VIDEO_RECIPE_V13.json"]:
            z.write(folder/name,name)
    with zipfile.ZipFile(bundle) as z:
        if z.testzip() is not None:raise RuntimeError("Corrupted archive")
    print("V32_V33_ADDENDUM_OK",bundle,flush=True)

if __name__=="__main__":
    engine.main()
    if "--preflight-only" not in sys.argv:add_v32_and_v33()
