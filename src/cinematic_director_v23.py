#!/usr/bin/env python3
"""ArtVision Cinematic Director V23: advisory selector and motion preflight.
No generation, no alteration of prior videos, no claim of aesthetic approval.
Works offline, from Android via the existing GitHub Actions / V21 workflow.
"""
from __future__ import annotations
import argparse, json, math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "cinematic_techniques_v23.json"
KINDS = {"artvision_critico","artvision_cinema","artvision_enigma",
         "libri","controluce","visual_music","hyperlumen","other"}
BASICS = {
 "artvision_critico":["locked_hold","narration_anchor","nonforced_ending","camera_seasick_gate"],
 "artvision_cinema":["static_tableau","musical_phrase_cut","no_fake_art_motion","camera_seasick_gate"],
 "artvision_enigma":["close_then_wide","promise_payoff","locked_hold","camera_seasick_gate"],
 "libri":["book_v12_scene","narration_anchor","one_claim_one_image","camera_seasick_gate"],
 "controluce":["controluce_facts","one_claim_one_image","credible_uncertainty","camera_seasick_gate"],
 "visual_music":["visual_music_notes","true_onset_sync","music_not_auto","real_frame_gate"],
 "hyperlumen":["hyperlumen_form","true_onset_sync","music_not_auto","real_frame_gate"],
 "other":["static_tableau","story_not_visualizer","camera_seasick_gate"],
}
FAMILY_HINTS = ["opening","composition","editing","camera","artwork","voice","music","narrative","quality","genre"]
LEXICON = {
 "ritratto":"portrait","volto":"portrait","occhi":"portrait","sguardo":"portrait",
 "inferno":"dramatic","orrore":"dramatic","notte":"dramatic","incubo":"dramatic",
 "trittico":"triptych","pannello":"triptych","folla":"dense","dettagli":"dense",
 "mistero":"reveal","enigma":"reveal","rivelazione":"reveal","paesaggio":"landscape",
 "panorama":"landscape","facciata":"architecture","edificio":"architecture",
 "scultura":"sculpture","statua":"sculpture","musica":"music","sincronizzazione":"music",
 "pittura":"painting","dipinto":"painting","quadro":"painting","silenzio":"quiet",
}
MOTIONS={"locked","slow_push","slow_pull","slow_pan_x","slow_pan_y"}
FORBIDDEN={"sine","oscillate","wobble","bounce","spin","whip_pan","dolly_zoom_simulated"}

def load_catalog(path=CATALOG):
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("schema")!="artvision-cinematic-language-v23":
        raise ValueError("Schema catalogo V23 non valido")
    entries=raw.get("techniques")
    if not isinstance(entries,list) or len(entries)<40:raise ValueError("Catalogo incompleto")
    ids=[x["id"] for x in entries]
    if len(set(ids))!=len(ids):raise ValueError("ID tecniche duplicati")
    families={"composition","camera","editing","opening","voice","music","artwork",
              "narrative","genre","quality"}
    for x in entries:
        if x.get("family") not in families or not isinstance(x.get("formats"),list) \
           or not all(x.get(f) for f in ("title","intention","application","avoid")):
            raise ValueError("Tecnica senza scopo, contesto o limiti: "+str(x.get("id")))
    return raw

def kind_of(brief):
    text=str(brief.get("format") or brief.get("video_format") or brief.get("series") or "").lower()
    if text in KINDS:return text
    if "critico" in text:return "artvision_critico"
    if "cinema" in text:return "artvision_cinema"
    if "enigma" in text:return "artvision_enigma"
    if "music" in text:return "visual_music"
    if "libri" in text:return "libri"
    return "other"

def tags_of(brief, kind):
    explicit=brief.get("cinematic_tags",[])
    if not isinstance(explicit,list):explicit=[]
    tags={str(x).lower() for x in explicit if isinstance(x,str)}
    tags.update({"critico" if kind=="artvision_critico" else kind})
    txt=" ".join(str(brief.get(k,"")) for k in ("topic","artwork","title","opening","description","creative_direction"))
    txt=txt.lower()
    # These are HYPOTHESES for the editor, never evidence that an image contains the object.
    for word,tag in LEXICON.items():
        if re.search(r"\b"+re.escape(word)+r"\b",txt):tags.add(tag)
    if kind in ("artvision_critico","artvision_cinema","artvision_enigma"):
        tags.add("painting")
    if kind in ("visual_music","hyperlumen"):tags.add("music")
    if kind in ("libri","controluce"):tags.add("story")
    return tags

def motion_check(brief,kind,policy):
    rows=brief.get("shots") or brief.get("scenes") or brief.get("beats") or []
    if not isinstance(rows,list):rows=[]
    issues=[]
    examined=0; moving=0; locked=0
    for index,shot in enumerate(rows):
        if not isinstance(shot,dict):continue
        cam=shot.get("camera")
        if cam is None:continue
        if isinstance(cam,str):cam={"move":cam}
        if not isinstance(cam,dict):
            issues.append({"shot":index+1,"severity":"block","problem":"Camera non valida"})
            continue
        examined+=1
        mode=str(cam.get("move",cam.get("mode","locked"))).lower()
        if mode in FORBIDDEN or mode not in MOTIONS:
            issues.append({"shot":index+1,"severity":"block","problem":"Movimento oscillante/indefinito: "+mode})
        if mode=="locked":locked+=1
        else:moving+=1
        scale=cam.get("scale_delta_fraction",0)
        travel=cam.get("travel_fraction",0)
        for label,val in (("scale_delta_fraction",scale),("travel_fraction",travel)):
            if isinstance(val,bool) or not isinstance(val,(int,float)) or not math.isfinite(val):
                issues.append({"shot":index+1,"severity":"block","problem":label+" non numerico"})
        if kind=="artvision_critico" and isinstance(scale,(int,float)) and not isinstance(scale,bool) and math.isfinite(scale) and abs(scale)>policy["critico_reference_max_scale_delta_fraction_per_shot"]:
            issues.append({"shot":index+1,"severity":"review","problem":"Scala oltre riferimento prudente Critico, motivare eccezione"})
        if kind=="artvision_critico" and isinstance(travel,(int,float)) and not isinstance(travel,bool) and math.isfinite(travel) and abs(travel)>policy["critico_reference_max_travel_fraction_per_shot"]:
            issues.append({"shot":index+1,"severity":"review","problem":"Pan oltre riferimento prudente Critico, controllare reale crop"})
        if mode in ("slow_pan_x","slow_pan_y") and not (shot.get("reason") or shot.get("title_internal") or shot.get("purpose")):
            issues.append({"shot":index+1,"severity":"review","problem":"Pan senza motivo narrativo dichiarato"})
    # Eye-trace is a cross-cut constraint, not an automatic declaration of a bad edit.
    # Only compare explicitly supplied real artwork crop centres. A wide/context
    # establishing shot can legitimately move attention a long distance.
    previous=None; eyes=0
    for idx,shot in enumerate(rows):
        if not isinstance(shot,dict):continue
        p=shot.get("focus_xy",shot.get("focus"))
        if not (isinstance(p,(list,tuple)) and len(p)==2
                and all(isinstance(n,(int,float)) and not isinstance(n,bool)
                        and math.isfinite(n) and 0<=n<=1 for n in p)):
            previous=None
            continue
        eyes+=1
        shot_type=str(shot.get("framing",shot.get("type","detail"))).lower()
        if previous is not None:
            old_idx,old_p,old_type=previous
            distance=math.hypot(float(p[0])-old_p[0],float(p[1])-old_p[1])
            if (distance>.42 and "full" not in (shot_type,old_type)
                    and "whole" not in (shot_type,old_type)
                    and "panel" not in (shot_type,old_type)
                    and not shot.get("reestablish_context")):
                issues.append({"shot":idx+1,"severity":"review",
                    "problem":"Salto eye-trace notevole tra punti lontani: valutare totale/raccordo orientativo, non pan veloce",
                    "distance_fraction":round(distance,3)})
        previous=(idx,(float(p[0]),float(p[1])),shot_type)
    if kind=="artvision_critico" and examined>=4 and moving>locked:
        issues.append({"shot":None,"severity":"review","problem":"Troppi piani mobili: preferire pause e camera ferma"})
    return {"plans_with_camera":examined,"total_shots":len(rows),"locked":locked,
            "moving":moving,"eye_trace_points_checked":eyes,
            "issues":issues,"real_video_inspected":False}

def plan(brief,catalog=None):
    if not isinstance(brief,dict):raise ValueError("Brief deve essere JSON oggetto")
    lib=catalog or load_catalog()
    kind=kind_of(brief)
    tags=tags_of(brief,kind)
    entries=[x for x in lib["techniques"] if kind in x["formats"]]
    byid={x["id"]:x for x in entries}
    selected=[];families=set()
    def add(x,why):
        if x["id"] in {y["id"] for y in selected}:return
        selected.append({"id":x["id"],"family":x["family"],"title":x["title"],
          "reason":why,"how":x["application"],"avoid":x["avoid"],
          "must_be_reviewed_manually":True})
        families.add(x["family"])
    for id in BASICS[kind]:
        if id in byid:add(byid[id],"Regola-base già approvata per "+kind)
    # Fill uncovered families first; score tags + useful relations, not random or a viral score.
    need=["opening","composition","editing","artwork","voice","music","genre","narrative"]
    for family in need:
        if len(selected)>=8:break
        if family in families:continue
        pool=[x for x in entries if x["family"]==family and x["id"] not in {y["id"] for y in selected}]
        if not pool:continue
        def score(x):
            t=set(x.get("tags",[]))
            return (3*len(tags & t)
                    + (2 if "all" in t else 0)
                    + (2 if kind=="artvision_critico" and x["id"] in ("in_media_res_visual","whole_work_resolution","one_claim_one_image") else 0)
                    + (2 if kind in ("visual_music","hyperlumen") and x["id"]=="music_continuity_cut" else 0))
        chosen=max(pool,key=lambda x:(score(x),-entries.index(x)))
        add(chosen,"Candidato per soggetto/tag "+", ".join(sorted(tags&set(chosen.get("tags",[]))))+
            "; da confermare guardando i materiali reali")
    motion=motion_check(brief,kind,lib["safety"])
    footage=brief.get("shots") or brief.get("scenes") or brief.get("beats") or []
    warnings=[]
    if not footage:warnings.append("Nessuno storyboard: selezione di famiglia, non una regia eseguibile")
    if motion["plans_with_camera"]==0:
        warnings.append("Mancano coordinate e movimento camera per piani: nessuna validazione fisica")
    if kind in ("artvision_critico","libri","controluce"):
        rows=footage if isinstance(footage,list) else []
        if not any(isinstance(x,dict) and (x.get("narration_anchor") or x.get("speech")) for x in rows):
            warnings.append("Sincronia con voce ancora da agganciare a copione/audio reale")
    warnings.append("Solo raccomandazione offline: non prova che il render sia bello, sincronizzato o pubblicabile")
    return {"schema":"cinematic-plan-v23","format":kind,
      "source_library":"config/cinematic_techniques_v23.json",
      "library_count":len(lib["techniques"]),
      "topic":str(brief.get("topic") or brief.get("artwork") or brief.get("title") or ""),
      "derived_tags_hypotheses":sorted(tags),
      "selected":selected,"number_selected":len(selected),
      "camera_preflight":motion,"warnings":warnings,
      "requires_real_preview_and_audio_listening":True,
      "autopublish":False,"modifies_master":False}

def export_plan(result, folder):
    dest=Path(folder);dest.mkdir(parents=True,exist_ok=True)
    (dest/"CINEMATOGRAPHY_PLAN_V23.json").write_text(
       json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Cinema V23 — proposte prima di render","",
      "**Scelte artistiche da confermare, non effetti auto-applicati.**","",
      f"Formato: {result['format']}; catalogo: {result['library_count']}; selezionate: {result['number_selected']}","","## Scelte motivate"]
    for t in result["selected"]:
        lines += ["",f"### {t['title']} ({t['id']})",t["reason"],"Come: "+t["how"],"Da evitare: "+t["avoid"]]
    lines+=["","## Preflight camera",json.dumps(result["camera_preflight"],ensure_ascii=False),
            "","## Limiti e QA richiesti"]
    lines+=["- "+x for x in result["warnings"]]
    (dest/"CINEMATOGRAPHY_NOTE_V23.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--brief",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=plan(json.loads(a.brief.read_text(encoding="utf-8")))
    export_plan(result,a.out)
    print(json.dumps({"status":"review_required","format":result["format"],
      "techniques":result["number_selected"],"camera_issues":len(result["camera_preflight"]["issues"]),
      "autopublish":False},ensure_ascii=False))

if __name__=="__main__": main()
