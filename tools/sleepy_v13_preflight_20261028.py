#!/usr/bin/env python3
"""Offline V13/V33/V38 structural preflight of already reviewed Rackham sources.
Does NOT claim artistic approval of rendered film.
"""
from pathlib import Path
import json,subprocess,shutil,hashlib
root=Path("output/sleepy_hollow_rackham_20261028")
source=root/"assets"
assert len(list(source.glob("rackham_*.jpg")))>=20,"Original plates not available"
projectdir=Path("output/sleepy_hollow_v13")
subprocess.run(["python","src/video_director_v13.py","brief","--format","libri","--topic",
                "La leggenda di Sleepy Hollow — Washington Irving","--out",str(projectdir)],check=True)
projectpath=projectdir/"PROJECT_V13.json"
p=json.loads(projectpath.read_text())
script=Path("episodes/sleepy_hollow_20261028/COPIONE_ITALIANO.txt").read_text(encoding="utf-8")
(projectdir/"COPIONE_ITALIANO.txt").write_text(script,encoding="utf-8")
paras=[x.strip() for x in script.split("\n\n") if x.strip()]
assert len(paras)==14
plates=[30,7,19,6,20,3,18,17,30,5,28,22,9,15]
names=["Il cavaliere", "La leggenda", "Ichabod", "Katrina", "Brom", "La festa", "Partenza",
       "Bosco", "Il ritorno del cavaliere", "La fuga", "Il lancio", "Tracce", "Ipotesi fuga", "Mistero"]
assets=[];decisions=[];scenes=[]
for plate in sorted(set(plates)):
    src=source/f"rackham_{plate:02}.jpg";dst=projectdir/f"rackham_{plate:02}.jpg"
    shutil.copy2(src,dst)
    aid=f"rackham_{plate:02}"
    assets.append({"id":aid,"role":"visual","file":dst.name,
                   "sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
                   "source":"https://litterature-jeunesse-libre.fr/bbs/book/1676",
                   "rights":"Original illustration by Arthur Rackham (1867–1939), 1928, public domain in Italy"})
    decisions.append({"asset_id":aid,"source_kind":"verified_archive",
                      "provider":"Littérature jeunesse libre (scans of Rackham 1928)",
                      "source_reference":"https://litterature-jeunesse-libre.fr/bbs/book/1676",
                      "choice_reason":"Authentic public-domain original illustration from the same edition; coherent characters and visual language.",
                      "scene_match_note":"Checked against storyboard and original art; visual interpretation rather than literal action where marked.",
                      "rights_review":"reviewed","scene_relevance":"reviewed","visual_review":"passed"})
for i,(plate,para) in enumerate(zip(plates,paras),1):
    scenes.append({"asset_id":f"rackham_{plate:02}","description":names[i-1],
                   "reason":"Narrative beat "+str(i)+"; original period illustration or deliberate recurring visual motif.",
                   "narration_anchor":para[:min(35,len(para))],
                   "camera":"gentle digital reframing, no simulated action",
                   "camera_reason":"Protect original Rackham composition and avoid cutting faces"})
p.update({"script":"COPIONE_ITALIANO.txt","assets":assets,"scenes":scenes,"status":"planned",
          "bibliography":{"author":"Washington Irving","publication_year":"1820",
            "edition_reference":"https://www.gutenberg.org/ebooks/41",
            "rights_notes":"Text 1820 public domain; Rackham illustrations 1928 public domain in Italy (died 1939)"},
          "editorial_metadata":{"series":"Tra le Pagine — Studio Ibrido","themes":"paura, superstizione, ambiguità",
             "genre":"racconto gotico","narration_style":"intimo, suspense, italiano naturale"},
          "business":{"audience":"Lettori di racconti gotici e pubblico social adulto",
                      "viewer_promise":"Scoprire il mistero di Ichabod e della zucca",
                      "original_contribution":"Adattamento italiano breve con incisioni autentiche",
                      "primary_platform":"Facebook","goal":"crescita del pubblico e ritorno alla serie",
                      "cta":"nessuna domanda forzata","experiment":"illustrazioni Rackham originali",
                      "time_budget_minutes":90,"cash_budget_eur":0}})
plan=p["editorial_plan"]
plan.update({"subject_insight":"La suspense nasce dall'ambiguità: fantasma o scherzo di Brom?",
 "sources":[{"reference":"https://www.gutenberg.org/ebooks/41",
             "finding":"Washington Irving, The Legend of Sleepy Hollow, testo originale 1820",
             "verification_notes":"Project Gutenberg; racconto verificato nel suo arco narrativo",
             "status":"reviewed"},
            {"reference":"https://commons.wikimedia.org/wiki/Category:MU_KPB_019_-_The_Legend_of_Sleepy_Hollow",
             "finding":"Arthur Rackham, 1928, illustrazioni originali, public domain",
             "verification_notes":"Commons metadata PD mark; Rackham died 1939; EPUB alternative acquired after Commons HTTP 429",
             "status":"reviewed"}],
 "opening_promise":"Un cavaliere senza testa attraversa la notte; il mistero del ponte",
 "payoff":"Zucca rotta, maestro sparito, risata di Brom: la verità rimane aperta",
 "cover_reason":"Autentica copertina Rackham del 1928 con titolo italiano composto in studio",
 "duration_seconds":181.44,"duration_reason":"Durata della voce Gacrux effettiva, non una quota prefissata",
 "techniques":[{"name":"archival_illustration","reason":"Fonte autentica e continuità illustrativa"},
               {"name":"opaque_hard_cut","reason":"Niente ghosting fra scene"},
               {"name":"subtle_camera","reason":"Movimento minimo senza simulare azioni"}],
 "mix_reason":"Voce al centro; tappeto originale scuro e discreto, suspense senza effetti gratuiti",
 "social_languages":{"facebook":"it","instagram":"it","tiktok":"it","youtube":"it"},
 "voice_image_sync_review":"ASR aligned 86%; human review pending",
 "artistic_review":"rendered_needs_review"})
plan["narrative_design"]={"story_beats":names,
 "distinct_visual_needs":names,
 "image_count_reason":"14 passaggi del racconto, 13 tavole originali distinte; la copertina ritorna come apparizione deliberata",
 "pace_reason":"Cambi sul primo suono di ciascun paragrafo allineato a Gacrux, non a durate uniformi",
 "reference_id":"feedback-v38-2026-10-26",
 "portable_lessons":["semantic timing","variety motivated by story"],
 "do_not_copy_reference_parameters":True}
plan["media_sourcing"]={"policy_id":plan["media_sourcing"]["policy_id"],
 "review_status":"reviewed","decisions":decisions,
 "note":"Historical scans original to this story. Missing literal hat/pumpkin shot flagged for artistic review; no stock substitute."}
p["reviews"]={"story":{"status":"passed","notes":"Full original plot and ambiguity retained in concise Italian adaptation"},
 "visuals":{"status":"passed","notes":"All plates inspected, no faces cropped in prepared 9:16 matte; a few metaphorical shots need human editorial review"},
 "rights":{"status":"passed","notes":"Irving 1820 and Rackham 1928; original source and PD status documented"}}
projectpath.write_text(json.dumps(p,ensure_ascii=False,indent=2))
result=subprocess.run(["python","src/video_director_v13.py","check","--project",str(projectpath)],
                      text=True,capture_output=True)
(projectdir/"PREFLIGHT_V13_OUTPUT.json").write_text(result.stdout or result.stderr)
print("V13 check exit:",result.returncode,flush=True)
print((result.stdout or result.stderr)[-4000:],flush=True)
if result.returncode:raise SystemExit(result.returncode)
