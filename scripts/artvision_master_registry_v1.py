#!/usr/bin/env python3
"""ArtVision Archivio Generale: inventory and differential reconciliation, read only."""
from __future__ import annotations
import argparse, csv, io, json, re, unicodedata, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

SITE = "https://video-library-studio.600led.workers.dev"
VARIANTS = ("critico_standard","critico_museum","cinema_standard","cinema_museum")

def load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError): return {}

def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(data,encoding="utf-8")

def jd(data): return json.dumps(data,ensure_ascii=False,indent=2)+"\n"
def norm(x):
    x=unicodedata.normalize("NFKD",str(x or ""))
    x="".join(c for c in x if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+"," ",x.lower()).strip()
def artist_key(x):
    s=norm(x)
    return {"j m w turner":"joseph mallord william turner", "jm w turner":"joseph mallord william turner"}.get(s,s)
def year(x):
    m=re.search(r"\b(?:1[4-9]\d{2}|20\d{2})\b",str(x or ""))
    return m.group(0) if m else ""
def val(o,*keys):
    if not isinstance(o,dict):return ""
    for k in keys:
        v=o.get(k)
        if isinstance(v,(str,int,float)) and str(v).strip():return str(v).strip()
    return ""
def identify(obj):
    base=obj.get("work",{}) if isinstance(obj.get("work"),dict) else {}
    return (val(obj,"artist","artist_as_chosen") or val(base,"artist"),
            val(obj,"title_en","title","title_as_chosen","artwork","work_title","work") or val(base,"title"),
            val(obj,"year") or val(base,"year"),
            val(obj,"museum") or val(base,"museum"),
            val(obj,"accession","object_id") or val(base,"accession","object_id"))
def status(d):
    s=val(d,"status","render_status").lower()
    sha=val(d,"video_sha256","rendered_mp4_sha256","mp4_sha256","hd_sha256","sha256","preferred_v2_mp4_sha256","original_v1_mp4_sha256")
    if any(k in s for k in ("owner_rejected","rejected_wrong","wrong_voice")):return "render_respinto"
    if any(k in s for k in ("rendered","real_mp4","real_new_mp4","technical_pass","mp4_verified")) or re.fullmatch(r"[a-fA-F0-9]{64}",sha):return "render_documentato"
    if "not_started" in s:return "da_produrre"
    if any(k in s for k in ("blocked","failed","unavailable")):return "bloccato"
    if any(k in s for k in ("pending","preflight","planned","source","ready")):return "in_coda_o_preflight"
    return "non_documentato"
def link(p):return "https://github.com/GGIANLUCAA/Tra-le-pagine-/blob/main/"+quote(str(p),safe="/")
def table_row(values):return "| "+" | ".join(str(x).replace("|","/").replace("\n"," ") for x in values)+" |"

def build(root,site,source,stamp):
    works={};duplicates=defaultdict(list);warnings=[]
    def get(obj,path,lane):
        if not isinstance(obj,dict):return None
        artist,title,yr,museum,objid=identify(obj)
        if not artist or not title:return None
        matches=[w for w in works.values() if artist_key(w["artist"])==artist_key(artist) and norm(w["title"])==norm(title)
                 and (not year(yr) or not year(w["year"]) or year(yr)==year(w["year"]))]
        if matches:w=matches[0]
        else:
            sid=re.sub(r"[^a-z0-9]+","-",norm(artist+" "+title+" "+year(yr))).strip("-")
            if sid in works:sid += "-alternate"
            w=dict(id=sid,title=title,artist=artist,year=yr,museum=museum,object_id=objid,
                   lanes=[],sources=[],variants={v:dict(state="non_documentato",evidence=[],site_candidates=[]) for v in VARIANTS},
                   legacy_video_claims=[],site_candidates=[],excluded=False)
            works[sid]=w
        for k,v in (("year",yr),("museum",museum),("object_id",objid)):
            if not w[k] and v:w[k]=v
        if path not in w["sources"]:w["sources"].append(path)
        if lane not in w["lanes"]:w["lanes"].append(lane)
        if "dali" in norm(artist) and ("temptation of saint anthony" in norm(title) or "temptation of st anthony" in norm(title)):
            w["excluded"]=True
        return w
    def put(w,v,obj,path):
        if v not in VARIANTS or not isinstance(obj,dict):return
        stat=status(obj)
        sha=val(obj,"video_sha256","rendered_mp4_sha256","mp4_sha256","hd_sha256","sha256","preferred_v2_mp4_sha256","original_v1_mp4_sha256")
        ev={"source":path,"status_claim":val(obj,"status","render_status") or "non dichiarato","classification":stat}
        if re.fullmatch(r"[a-fA-F0-9]{64}",sha):
            ev["sha256"]=sha.lower()
            duplicates[sha.lower()].append((w["id"],v,path))
        entry=w["variants"][v]
        if ev not in entry["evidence"]:entry["evidence"].append(ev)
        if stat=="render_documentato":entry["state"]=stat
        elif entry["state"]!="render_documentato" and (entry["state"]=="non_documentato" or stat=="bloccato"):
            entry["state"]=stat
    source_defs=[
        ("queue/artvision_four_variants_s01_20261028.json","storico_4x1","groups"),
        ("queue/artvision_owner_selected_ten_20261102.json","selezione_10","works"),
        ("queue/artvision_owner_30_fast_quality_lane_20261109.json","selezione_30","selected_works"),
        ("queue/artvision_new_series_20261114.json","nuova_serie","works")]
    for rel,lane,field in source_defs:
        d=load(root/rel)
        if not isinstance(d,dict) or not isinstance(d.get(field),list):
            warnings.append("Sorgente non leggibile "+rel);continue
        for obj in d[field]:
            w=get(obj,rel,lane)
            if not w:continue
            variant_matrix=obj.get("variants") if isinstance(obj.get("variants"),dict) else obj.get("variant_matrix")
            if isinstance(variant_matrix,dict):
                for variant,detail in variant_matrix.items():put(w,variant,detail,rel)
            if lane=="nuova_serie" and "RENDER" in val(obj,"status").upper():
                put(w,"cinema_standard",{"status":val(obj,"status")},rel)
            if lane=="selezione_10" and obj.get("preexisting_cinema_candidate"):
                w["legacy_video_claims"].append({"source":rel,"status":"legacy_non_4x1"})
            if lane=="selezione_10":
                # This pre-4x1-format queue stores proven MP4s under version-specific keys.
                # Multiple revisions of the same slot count once only.
                for k,detail in obj.items():
                    m=re.match(r"^(?:new_)?(critico_standard|critico_museum|cinema_standard|cinema_museum)_v\d+",k)
                    if m and isinstance(detail,dict):
                        put(w,m.group(1),detail,rel+"#"+k)
                old_cinema=obj.get("v134_cinema_candidate")
                if isinstance(old_cinema,dict) and val(old_cinema,"mp4_sha256") and val(old_cinema,"mp4_filename"):
                    put(w,"cinema_standard",old_cinema,rel+"#v134_cinema_candidate")
                revision=obj.get("critico_short_revision_v218",{})
                if isinstance(revision,dict):
                    for v in ("critico_standard","critico_museum"):
                        sample=revision.get(v,{})
                        if isinstance(sample,dict) and val(sample,"sha256") and val(sample,"filename"):
                            put(w,v,dict(sample,status=val(revision,"production_status")),rel+"#critico_short_revision_v218")
                    for v in ("cinema_standard","cinema_museum"):
                        sample=revision.get(v+"_preserved",{})
                        if isinstance(sample,dict) and val(sample,"sha256"):
                            put(w,v,dict(sample,status="VERIFIED_EXISTING_SAME_SLOT_REAL_MP4"),rel+"#critico_short_revision_v218")
                w["selected_ten_legacy_slots_claim"]=obj.get("slots_delivered_this_selection")
                w["preflight_status_claim"]=val(obj,"preflight_status")
            if lane=="selezione_30":
                w["selection_order"]=obj.get("selection_order")
                w["priority"]=obj.get("provisional_production_priority")
    for path in sorted((root/"queue").glob("*checkpoint*.json")):
        d=load(path);rel=str(path.relative_to(root))
        # Some checkpoints contain two or more independent artworks in works[].
        objects=d.get("works") if isinstance(d,dict) and isinstance(d.get("works"),list) else [d]
        for obj in objects:
            w=get(obj,rel,"checkpoint")
            if not w:continue
            variant_matrix=obj.get("variants") if isinstance(obj.get("variants"),dict) else obj.get("variant_matrix")
            if isinstance(variant_matrix,dict):
                for variant,detail in variant_matrix.items():put(w,variant,detail,rel)
            if isinstance(obj.get("existing_slots"),list):
                for slot in obj["existing_slots"]:
                    if isinstance(slot,dict):put(w,slot.get("variant"),slot,rel)
            if obj.get("variant") in VARIANTS:
                prod=obj.get("production",{}) if isinstance(obj.get("production"),dict) else {}
                verified=obj.get("verified_render",{}) if isinstance(obj.get("verified_render"),dict) else {}
                put(w,obj["variant"],{"status":val(obj,"status"),
                    "mp4_sha256":val(obj,"mp4_sha256","video_sha256") or
                    val(prod,"hd_sha256","mp4_sha256","video_sha256","android_sha256") or
                    val(verified,"mp4_sha256","hd_sha256")},rel)
            if isinstance(obj.get("remaining"),list):
                for v in obj["remaining"]:
                    if v in VARIANTS and w["variants"][v]["state"]=="non_documentato":
                        w["variants"][v]["state"]="da_produrre"

    cycles=load(root/"queue/artvision_autoproduction_v31_state.json")
    for cycle in cycles.get("cycle_log",[]) if isinstance(cycles,dict) else []:
        w=get({"artist":cycle.get("artist"),"title":cycle.get("work")},"queue/artvision_autoproduction_v31_state.json","cicli_v31")
        if w and cycle.get("mp4_verified"):
            w["legacy_video_claims"].append({"cycle_id":cycle.get("cycle_id"),
                   "sha256":cycle.get("sha256_mp4"),"workflow_run":cycle.get("workflow_run_url")})
    # Historical source sets: keep evidence without promoting to four-variant masters.
    for rel,lane,field in (
        ("queue/artvision_museum_scale_s01_20261028.json","museum_scale","episodes"),
        ("queue/artvision_dual_format_s01_20261028.json","legacy_dual_format","pairs")):
        d=load(root/rel)
        for item in d.get(field,[]) if isinstance(d,dict) else []:
            if not isinstance(item,dict):continue
            w=get(item,rel,lane)
            if w:
                w["legacy_video_claims"].append({"source":rel,"status":val(item,"status") or val(d,"status"),
                    "note":"Formato storico; non conteggiare come slot 4x1 senza video specifico."})
    # Research-only source lists: never confuse a shortlist with a render queue.
    future_catalog=load(root/"research/artvision_future_works_index_v1_20261107.json")
    future_100=[{"catalog_id":item.get("catalog_id"),"artist":val(item,"artist"),
        "title":val(item,"title"),"year":val(item,"year"),"category":val(item,"category"),
        "source":"research/artvision_future_works_index_v1_20261107.json",
        "work_status":"banca_idee_non_coda_produttiva",
        "rights_status":val(item,"pixel_file_license_status") or "non_verificato"}
        for item in future_catalog.get("works",[]) if isinstance(item,dict)] if isinstance(future_catalog,dict) else []
    selected_futures=load(root/"research/artvision_owner_selected_30_future_20261109.json")
    future_30=[{"order":item.get("selection_order"),"artist":val(item,"artist_as_chosen","artist"),
        "title":val(item,"title_as_chosen","title"),"status":val(item,"current_stage") or "research_pending",
        "source":"research/artvision_owner_selected_30_future_20261109.json",
        "rights_cleared":bool(item.get("territorial_commercial_reuse_cleared",False)),
        "selection_only_not_completed":True}
        for item in selected_futures.get("works",[]) if isinstance(item,dict)] if isinstance(selected_futures,dict) else []
    production_root=root/"docs/productions"
    production_dossiers=[{"path":str(p.relative_to(root)),"extension":p.suffix.lower(),
        "bytes":p.stat().st_size} for p in sorted(production_root.rglob("*")) if p.is_file()] if production_root.is_dir() else []
    production_dirs=sum(p.is_dir() for p in production_root.rglob("*")) if production_root.is_dir() else 0
    # Independent verified historical technical review files.
    # They remain NOT owner-approved, NOT Gold, and NOT counted as newly approved slots.
    extra_reviews=load(root/"data/archivio-generale/revisioni_storiche_fonti_pubbliche.json")
    historic_review_count=0
    for item in extra_reviews.get("records",[]) if isinstance(extra_reviews,dict) else []:
        if not isinstance(item,dict):continue
        w=get(item,val(item,"source"),"review_storica")
        if w and val(item,"variant") in VARIANTS:
            put(w,item["variant"],{"status":"RENDERED_TECH_REVIEW_ONLY_ARTISTIC_PENDING_NOT_GOLD",
                "mp4_sha256":val(item,"mp4_sha256")},val(item,"source"))
            historic_review_count+=1
    # All literary series dossiers are included without implying completed video delivery.
    literary=[]
    for folder in sorted((root/"episodes").glob("*")):
        if not folder.is_dir():continue
        meta=load(folder/"metadata.json")
        literary.append({"folder":str(folder.relative_to(root)),
            "title":val(meta,"title") or folder.name.replace("_"," "),
            "author":val(meta,"author") or "da_verificare",
            "series":val(meta,"series") or "Tra le Pagine",
            "status_claim":val(meta,"status") or "solo_dossier_non_prova_del_video",
            "publication_claim":val(meta,"publication","social_publish","publications") or "non_verificata",
            "metadata_present":bool(meta),
            "episode":val(meta,"episode")})
    history_candidates=[]
    for rel,field in (("queue/storia_rivive_candidates_v58.json","candidates"),
                      ("queue/storia_rivive_v69_film_scouting_candidates.json","items")):
        d=load(root/rel)
        if isinstance(d.get(field),list):
            for obj in d[field]:
                if isinstance(obj,dict):
                    history_candidates.append({"source":rel,"title":val(obj,"title","event","name") or "da_verificare",
                        "year":val(obj,"year"),"status_claim":val(obj,"status") or val(d,"status") or "ricerca_non_video_finito"})
    queue_files=[]
    for path in sorted((root/"queue").rglob("*.json")):
        d=load(path);rel=str(path.relative_to(root))
        n=next((len(d[k]) for k in ("works","selected_works","groups","candidates","cycle_log")
                if isinstance(d,dict) and isinstance(d.get(k),list)),None)
        queue_files.append({"path":rel,"items":n,"type":"checkpoint" if "checkpoint" in rel else
                      ("principale" if rel in [s[0] for s in source_defs] else "supporto")})
    # Map distinct artist surname aliases to canonical names. A surname alone is
    # NOT evidence of a specific painting; do not bind a 4x1 work on that basis.
    aliases=defaultdict(set)
    stop={"the","elder","younger","of","von","van","de","der","di","da","le","la","del","il"}
    artists={w["artist"] for w in works.values()}
    artists.update(x["artist"] for x in future_100 if x["artist"])
    artists.update(x["artist"] for x in future_30 if x["artist"])
    for artist in artists:
        aa=[t for t in norm(artist).split() if t not in stop]
        if not aa:continue
        # Last meaningful surname in "Pieter Bruegel the Elder" is Bruegel.
        surname=aa[-1]
        if len(surname)>=4:aliases[surname].add(artist)
    site_rows=[];filename_groups=defaultdict(list);site_claims={}
    for x in site.get("items",[]) if isinstance(site,dict) else []:
        if not isinstance(x,dict):continue
        name=val(x,"name","key")
        if not name:continue
        key=val(x,"key","name")
        row={k:x.get(k) for k in ("key","name","title","description","category","project",
             "version","size","duration","uploaded","gptCreatedAt","available","source","cover","width","height","hidden")}
        row.update(artist="da_verificare",artwork="da_verificare",match_quality="nessuna",
                   video_url=SITE+"/video/"+quote(key,safe=""))
        n=norm(name+" "+val(x,"title")).split()
        n_set=set(n)
        possible=[]
        for w in works.values():
            tokens=[t for t in norm(w["artist"]).split() if t not in stop]
            surname=tokens[-1] if tokens else ""
            title_tokens=[t for t in norm(w["title"]).split()
                          if len(t)>=4 and t not in {"with","from","upon","into","over","after","before","between"}]
            if surname and surname in n_set and title_tokens and all(t in n_set for t in title_tokens):
                possible.append(w)
        if len(possible)==1:
            w=possible[0]
            row.update(artist=w["artist"],artwork=w["title"],
                       match_quality="ipotesi_nome_non_hash",work_id=w["id"])
            w["site_candidates"].append(key)
            variant=("critico" if "critico" in n else "cinema" if "cinema" in n else None)
            scene=("museum" if "museum" in n else "standard" if "standard" in n else None)
            if variant and scene:w["variants"][variant+"_"+scene]["site_candidates"].append(key)
        elif len(possible)>1:
            row["match_quality"]="ambiguo"
        else:
            # Artist-only hint: useful for search, NEVER proof of work/video identity.
            artist_guesses=set()
            for token in n_set:
                if token in aliases and len(aliases[token])==1:
                    artist_guesses.update(aliases[token])
            if len(artist_guesses)==1:
                row.update(artist=next(iter(artist_guesses)),match_quality="indizio_solo_artista")
        site_rows.append(row)
        canonical=norm(re.sub(r"__\d+(?=\.)","",name))
        filename_groups[canonical].append({"name":name,"size":x.get("size"),"key":key})
        site_claims[key]=row
    ordered=sorted(works.values(),key=lambda w:(norm(w["artist"]),norm(w["title"]),w["year"]))
    for w in ordered:
        # Historical one-off Cinema/Museum or paired pilots are not automatically
        # four-variant commitments. The owner-selected and checkpoint lanes are.
        w["four_by_one_target"]=not w["excluded"] and bool(set(w["lanes"]) &
            {"storico_4x1","selezione_10","selezione_30","nuova_serie","checkpoint"})
        w["missing_variants"]=[v for v in VARIANTS if w["variants"][v]["state"]!="render_documentato"] if w["four_by_one_target"] else []
        w["render_documented"]=sum(w["variants"][v]["state"]=="render_documentato" for v in VARIANTS)
        w["site_playback_verified"]=False
        w["published_confirmed"]=False
    categories=dict(Counter(x.get("category") or "Senza categoria" for x in site_rows))
    stats={"works":len(ordered),"render_documented_slots":sum(w["render_documented"] for w in ordered),
           "not_documented_slots":sum(len(w["missing_variants"]) for w in ordered),
           "site_items":len(site_rows),"site_cloudflare":sum(x.get("source")=="cloudflare" for x in site_rows),
           "site_unavailable":sum(x.get("available") is False for x in site_rows),
           "possible_site_matches":sum(x["match_quality"]=="ipotesi_nome_non_hash" for x in site_rows),
           "queue_files":len(queue_files),"literary_dossiers":len(literary),"history_candidates":len(history_candidates),
           "research_100":len(future_100),"selected_future_30":len(future_30),
           "production_dossiers":len(production_dossiers),"production_dossier_subdirs":production_dirs,
           "unmatched_site_items":sum(x["match_quality"]=="nessuna" for x in site_rows),
           "site_artist_only_hints":sum(x["match_quality"]=="indizio_solo_artista" for x in site_rows),
           "site_ambiguous":sum(x["match_quality"]=="ambiguo" for x in site_rows),
           "recovered_historical_review_files":historic_review_count,
           "four_by_one_scoped":sum(w["four_by_one_target"] for w in ordered),
           "complete_four_render_documented":sum(w["four_by_one_target"] and w["render_documented"]==4 for w in ordered),
           "categories":categories}
    likely_duplicate_names=[]
    for k,members in filename_groups.items():
        if len(members)<2:continue
        sizes={v["size"] for v in members}
        suspected="same_name_same_size_no_hash" if len(sizes)==1 and None not in sizes else "same_stem_mixed_sizes_revisions_possible"
        likely_duplicate_names.append({"normalized":k,"files":[v["name"] for v in members],
            "comparison":suspected,
            "warning":"Filename/size alone never proves byte-identical video."})
    cross_hashes=[{"sha256":h,"claims":proofs} for h,proofs in duplicates.items()
                  if len(set((w,v) for w,v,_ in proofs))>1]
    return dict(schema="artvision-master-registry-v1",generated_at=stamp,site_state=source,stats=stats,
                works=ordered,site_items=site_rows,queue_files=queue_files,literary=literary,history_candidates=history_candidates,
                future_100=future_100,future_30=future_30,production_dossiers=production_dossiers,
                possible_filename_duplicates=likely_duplicate_names,
                cross_variant_sha_collisions=cross_hashes,warnings=warnings)

def markdown(root,r):
    st=r["stats"];stamp=r["generated_at"]
    intro=["# ArtVision — Archivio Generale","",
       "Generato: "+stamp+" · Verifica sito: "+r["site_state"],"",
       "Fonte: repository GitHub e catalogo pubblico Video Library Studio; nessuna modifica a video, code o sito.",
       "AVVERTENZA: un render documentato non significa file oggi scaricabile, QA artistico approvato o video pubblicato.",
       "Un possibile abbinamento per nome non dimostra l'identità del file. Le lacune non sono ordini di rendering.","",
       "## Conteggi","",
       table_row(["Opere censite",st["works"]]),
       table_row(["Slot render documentati",st["render_documented_slots"]]),
       table_row(["Slot mancanti / non documentati",st["not_documented_slots"]]),
       table_row(["Elementi del catalogo sito",st["site_items"]]),
       table_row(["Elementi Cloudflare",st["site_cloudflare"]]),
       table_row(["Elementi non disponibili",st["site_unavailable"]]),
       table_row(["Code JSON esaminate",st["queue_files"]]),
       table_row(["Banca idee future (non coda)",st["research_100"]]),
       table_row(["Future selezionate (non video finiti)",st["selected_future_30"]]),
       table_row(["Fascicoli di produzione indicizzati",st["production_dossiers"]]),
       table_row(["Review Museum storiche recuperate",st["recovered_historical_review_files"]]),
       table_row(["Opere in scope 4x1",st["four_by_one_scoped"]]),
       table_row(["Schede sito senza indizi artistici",st["unmatched_site_items"]]),
       table_row(["Schede sito con indizio solo artista",st["site_artist_only_hints"]]),
       table_row(["Schede con possibile opera identificata",st["possible_site_matches"]]),"",
       "## Documenti collegati","",
       "- [Opere e tutte le varianti](ARCHIVIO_OPERE_E_VERSIONI.md)",
       "- [Inventario integrale del sito](ARCHIVIO_SITO_COMPLETO.md)",
       "- [Code e produzioni mancanti](ARCHIVIO_CODE_MANCANTI.md)",
       "- [Doppioni potenziali](ARCHIVIO_DOPPIONI_POTENZIALI.md)",
       "- [Libri e ricerche La Storia Rivive](ARCHIVIO_ALTRI_FORMAT.md)",
       "- [Ricerca futura: 100 opere e selezione 30](ARCHIVIO_RICERCA_FUTURA.md)",
       "- [Fascicoli di produzione storici](ARCHIVIO_PRODUZIONI_STORICHE.md)",
       "- [Procedura archivio PRIVATO e antidoppioni](ARTVISION_ARCHIVIO_PRIVATO_E_CONFRONTO_V1.md)","",
       "I file JSON e CSV nella cartella data/archivio-generale sono l'interfaccia leggibile dalle automazioni.",
       "L'Action aggiorna i dati periodicamente; gli errori del sito conservano il precedente snapshot dichiarandolo non attuale.",
       "Nessun dato ricavato da sole conversazioni viene spacciato per verifica di MP4.",
       "LIMITAZIONE: la Libreria privata ChatGPT non è esposta a GitHub Actions. I suoi MP4 non",
       "sono inventariati automaticamente in questo repository pubblico; verificarli separatamente",
       "senza pubblicare ID, percorsi o altri metadati privati. La coincidenza per nome non prova identità."]
    save(root/"docs/ARCHIVIO_GENERALE_ARTVISION.md","\n".join(intro)+"\n")
    chars={"render_documentato":"D","render_respinto":"R","da_produrre":"C","in_coda_o_preflight":"C","bloccato":"B","non_documentato":"—"}
    p=["# Opere, artisti, quattro versioni","",
       "D = render documentato · R = render respinto (non completato) · C = in coda/preflight · B = blocco documentato · — = non documentato.",
       "Questi stati non implicano pubblicazione né playback.","",
       "| Autore | Titolo | Anno | Critico | Critico Museum | Cinema | Cinema Museum | Sul sito? |",
       "|---|---|---|---|---|---|---|---|"]
    for w in r["works"]:
        v=[chars[w["variants"][x]["state"]] for x in VARIANTS]
        note="Possibili "+str(len(w["site_candidates"])) if w["site_candidates"] else "Non abbinato"
        if w["excluded"]:note="ESCLUSO"
        p.append(table_row([w["artist"],w["title"],w["year"] or "?",*v,note]))
    p+=["","## Schede con provenienza",""]
    for w in r["works"]:
        p += ["### "+w["artist"]+" — "+w["title"],"",
              "- Anno: "+(w["year"] or "da verificare")+"; Museo: "+(w["museum"] or "da verificare"),
              "- Code: "+", ".join(w["lanes"]),
              "- Candidati sul sito (nome compatibile soltanto): "+(", ".join(w["site_candidates"]) or "nessuno")]
        for v in VARIANTS:
            e=w["variants"][v];recent=e["evidence"][-5:]
            p.append("- "+v+": "+e["state"]+"; prove: "+("; ".join(x["source"]+" ["+x["status_claim"][:65]+"]" for x in recent) or "nessuna"))
        p.append("")
    save(root/"docs/ARCHIVIO_OPERE_E_VERSIONI.md","\n".join(p)+"\n")
    p=["# Tutto il catalogo pubblico di Video Library Studio","",
       "Generato: "+stamp+"; fonte: "+r["site_state"]+".",
       "Indizio solo artista non identifica un quadro né una variante; mai usarlo per concludere che un MP4 è pubblicato.","Le voci con autore da_verificare non contengono dati sufficienti per identificarlo. Nessuna prova individuale di playback.","",
       "| Nome file | Titolo indicato | Autore candidato | Opera candidata | Categoria | Caricamento UTC | Byte | API disponibile |",
       "|---|---|---|---|---|---|---:|---|"]
    for x in sorted(r["site_items"],key=lambda z:(z.get("uploaded") or ""),reverse=True):
        name=x["name"].replace("|","/")
        p.append(table_row(["["+name+"]("+x["video_url"]+")",x.get("title") or "non indicato",
                 x["artist"],x["artwork"],x.get("category") or "—",x.get("uploaded") or "—",
                 x.get("size") or "?",x.get("available")]))
    save(root/"docs/ARCHIVIO_SITO_COMPLETO.md","\n".join(p)+"\n")
    p=["# Code e versioni da completare","",
       "Questo elenco è un inventario di stati, non una coda aggiuntiva né un ordine di avvio.",
       "Le versioni già rese devono essere verificate prima di ogni possibile rigenerazione.","",
       "| Autore | Opera | Slot senza prova di render | Serie |",
       "|---|---|---|---|"]
    for w in r["works"]:
        if w["missing_variants"] and not w["excluded"]:
            p.append(table_row([w["artist"],w["title"],", ".join(w["missing_variants"]),", ".join(w["lanes"])]))
    p += ["","## Tutti i JSON delle code","",
           "| File | Tipo | Numero record dichiarati |","|---|---|---:|"]
    for x in r["queue_files"]:
        p.append(table_row(["["+x["path"]+"]("+link(x["path"])+")",x["type"],x["items"] if x["items"] is not None else "n.d."]))
    save(root/"docs/ARCHIVIO_CODE_MANCANTI.md","\n".join(p)+"\n")
    p=["# Doppioni potenziali da esaminare","",
       "Non vengono rimossi, esclusi, rinominati o bloccati automaticamente.","",
       "## Somiglianze fra nomi di file", ""]
    if not r["possible_filename_duplicates"]:p.append("Nessuna collisione da normalizzazione.")
    for d in r["possible_filename_duplicates"]:
        p.append("- "+d["normalized"]+": "+", ".join(d["files"]))
    p += ["","## Hash identici dichiarati per opere/versioni distinte",""]
    if not r["cross_variant_sha_collisions"]:p.append("Nessun caso documentato.")
    for d in r["cross_variant_sha_collisions"]:p.append("- "+d["sha256"]+": "+str(d["claims"]))
    save(root/"docs/ARCHIVIO_DOPPIONI_POTENZIALI.md","\n".join(p)+"\n")
    other=["# Altri format — libri e La Storia Rivive","","Generato: "+stamp,
         "Attenzione: una cartella con metadata o una ricerca di fonti NON prova un MP4 finito.","",
         "## Libri raccontati, autore e stato dichiarato","",
         "| Titolo | Autore | Cartella | Stato dichiarato | Pubblicazione dichiarata |",
         "|---|---|---|---|---|"]
    for x in r["literary"]:
        other.append(table_row([x["title"],x["author"],"["+x["folder"]+"]("+link(x["folder"])+")",
                     x["status_claim"],x["publication_claim"]]))
    other += ["","## La Storia Rivive — candidati di ricerca, non video completati","",
              "| Soggetto | Anno | Stato ricerca | Fonte coda |","|---|---|---|---|"]
    for x in r["history_candidates"]:
        other.append(table_row([x["title"],x["year"] or "—",x["status_claim"],
                  "["+x["source"]+"]("+link(x["source"])+")"]))
    other += ["","## Tutti gli altri video realmente segnalati dal catalogo pubblico","",
              "I video delle altre categorie sono inclusi senza esclusioni nell'Archivio sito completo.",
              "Le schede prive di autore o titolo attribuibile restano da verificare."]
    save(root/"docs/ARCHIVIO_ALTRI_FORMAT.md","\n".join(other)+"\n")

    future=["# Ricerca futura — non è una coda di rendering","",
       "Le 100 opere editoriali e le 30 selezionate sono cataloghi di idee, non 130 render ordinati.",
       "La presenza in ricerca non significa file, diritti, qualità o pubblicazione verificata.","",
       "## Catalogo editoriale 100 opere","",
       "| ID | Autore | Opera | Anno | Gruppo | Stato diritti file |",
       "|---|---|---|---|---|---|"]
    for x in r["future_100"]:
        future.append(table_row([x["catalog_id"],x["artist"],x["title"],x["year"] or "?",
                                 x["category"],x["rights_status"]]))
    future+=["","## Le 30 opere selezionate","",
        "| Ordine | Autore | Opera | Stato ricerca | Diritti commerciali |",
        "|---|---|---|---|---|"]
    for x in r["future_30"]:
        future.append(table_row([x["order"],x["artist"],x["title"],x["status"],
                          "dichiarati chiariti" if x["rights_cleared"] else "da verificare"]))
    save(root/"docs/ARCHIVIO_RICERCA_FUTURA.md","\n".join(future)+"\n")
    dossiers=["# Tutti i fascicoli di produzione storici","",
       "Indice dei file realmente presenti in docs/productions, non conferma file MP4 o pubblicazione.",
       "La dimensione indica il file di documentazione, non il video.","",
       "| Fascicolo | Tipo | Byte |","|---|---|---:|"]
    for x in r["production_dossiers"]:
        dossiers.append(table_row(["["+x["path"]+"]("+link(x["path"])+")",
                                    x["extension"] or "altro",x["bytes"]]))
    save(root/"docs/ARCHIVIO_PRODUZIONI_STORICHE.md","\n".join(dossiers)+"\n")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--site-json",type=Path,help="Fixture JSON API per il test")
    parser.add_argument("--offline",action="store_true")
    args=parser.parse_args()
    root=args.root.resolve()
    stamp=datetime.now(timezone.utc).isoformat(timespec="seconds")
    site={};source="non_verificato"
    if args.site_json:
        site=load(args.site_json);source="fixture_offline"
    elif not args.offline:
        try:
            req=urllib.request.Request(SITE+"/api/catalog",headers={"Accept":"application/json","User-Agent":"ArtVision-Inventory-V1"})
            with urllib.request.urlopen(req,timeout=35) as response:
                raw=response.read(8_000_001)
                if len(raw)>8_000_000:raise ValueError("Risposta oltre limite")
                site=json.loads(raw.decode("utf-8"))
                if not isinstance(site,dict) or not isinstance(site.get("items"),list):raise ValueError("API senza items")
                source="live_api"
        except (OSError,ValueError,UnicodeError) as e:
            print("SITE_UNAVAILABLE",str(e)[:250])
    if source=="non_verificato":
        old=load(root/"data/archivio-generale/catalogo_sito.json")
        if isinstance(old,dict) and isinstance(old.get("items"),list):
            site=old;source="cache_precedente_non_attuale"
    registry=build(root,site,source,stamp)
    # A scheduled check must not commit every six hours when nothing changed.
    old=load(root/"data/archivio-generale/opere.json")
    old_site=load(root/"data/archivio-generale/catalogo_sito.json")
    old_queue=load(root/"data/archivio-generale/code.json")
    old_prod=load(root/"data/archivio-generale/fascicoli_produzione.json")
    if isinstance(old,dict) and isinstance(old_site,dict) and isinstance(old_queue,dict) and isinstance(old_prod,dict):
        keys=("works","literary","history_candidates","future_100","future_30","stats","warnings")
        if (all(old.get(k)==registry.get(k) for k in keys)
            and old_site.get("items")==registry["site_items"]
            and old_queue.get("items")==registry["queue_files"]
            and old_prod.get("items")==registry["production_dossiers"]
            and old.get("site_state")==registry["site_state"]):
            stamp=old.get("generated_at") or stamp
            registry["generated_at"]=stamp
    folder=root/"data/archivio-generale"
    save(folder/"opere.json",jd({k:v for k,v in registry.items() if k not in
       ("site_items","queue_files","possible_filename_duplicates","cross_variant_sha_collisions","production_dossiers")}))
    save(folder/"catalogo_sito.json",jd({"schema":"artvision-site-snapshot-v1","checked_at":stamp,
             "source_state":source,"items":registry["site_items"]}))
    save(folder/"code.json",jd({"checked_at":stamp,"items":registry["queue_files"]}))
    save(folder/"fascicoli_produzione.json",jd({"checked_at":stamp,"items":registry["production_dossiers"]}))
    save(folder/"doppioni.json",jd({"filename_suspects":registry["possible_filename_duplicates"],
               "cross_variant_sha_collisions":registry["cross_variant_sha_collisions"]}))
    buffer=io.StringIO()
    fields=["name","title","artist","artwork","category","uploaded","size","duration",
            "available","source","match_quality","video_url"]
    writer=csv.DictWriter(buffer,fieldnames=fields,extrasaction="ignore")
    writer.writeheader();writer.writerows(registry["site_items"])
    save(folder/"catalogo_sito.csv",buffer.getvalue())
    markdown(root,registry)
    print(jd({"result":"generated","site_state":source,"statistics":registry["stats"]}))
if __name__=="__main__":main()
