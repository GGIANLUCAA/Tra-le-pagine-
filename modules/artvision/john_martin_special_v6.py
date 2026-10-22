#!/usr/bin/env python3
"""JOHN MARTIN — Visioni della fine. Regia originale autonoma sopra Cinema V6.
Le scene sono motivate dalle opere: nessuna alterazione dei dipinti e nessun costo API.
V6 Gold Master rimane immutato. V17 segue come controllo additivo.
"""
from pathlib import Path
import argparse, json, re
import john_martin_enriched_engine_v6 as v6
import director_cinema_v6 as cinema
from atelier_v4 import audio_download as original_download

SLUG="john_martin"
v6.ROOT=Path("output/artvision-john-martin-v6-special")
v6.P.clear()
v6.P[SLUG]={
 "name":"John Martin", "duration":118,
 "hero":"John Martin - The Great Day of His Wrath - Google Art Project.jpg",
 "featured":[
  "John Martin Le Pandemonium Louvre.JPG",
  "John Martin - Belshazzar's Feast - Google Art Project.jpg",
  "John Martin - The Last Judgement - Google Art Project.jpg",
  "John Martin - The Plains of Heaven - Google Art Project.jpg",
  "John Martin - Destruction of Tyre - Google Art Project.jpg",
  "John Martin - The Deluge - Google Art Project.jpg",
  "John Martin - Joshua Commanding the Sun to Stand Still - Google Art Project.jpg",
  "John Martin - Sodom and Gomorrah.jpg",
  "John Martin, Belshazzar's Feast, 1826, NGA 56798.jpg",
  "Martin, John - The Seventh Plague - 1823.jpg",
  "John Martin - Pandemonium - WGA14149.jpg",
  "John Martin - Great Day of His Wrath - WGA14150.jpg"
 ],
 "key":["great day of his wrath","pandemonium","belshazzar","joshua commanding",
        "seventh plague","destruction of tyre","sodom","deluge",
        "last judgement","plains of heaven","fallen angels","eve of the deluge",
        "destruction of pharaoh","country of the iguanodon","city of god"],
 "find":[
  "John Martin paintings Google Art Project the great day wrath",
  "John Martin Pandemonium Belshazzar's Feast paintings",
  "John Martin The Deluge Destruction of Tyre Seventh Plague",
  "John Martin Last Judgement Plains of Heaven Joshua commanding",
  "John Martin painting ruin biblical apocalypse landscape"],
 "act":[
  "I — La frattura: pietre e cielo in collisione",
  "II — La città: scale impossibili e folle minuscole",
  "III — Il disastro: fuoco e mare",
  "IV — Il giudizio: il mondo si apre",
  "V — La luce: un respiro oltre la rovina"],
 "track":"the_descent"
}
v6.SOUND["the_descent"]={
 "title":"The Descent","author":"Kevin MacLeod","isrc":"USUAN1200094",
 "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200094",
 "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20Descent.mp3"],
 "license":"CC BY 4.0","license_url":v6.LICENSE_URL,
 "expected_seconds":192,"instrumental":True
}
def safe(name,slug):
 n=name.casefold()
 if not n.endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff")):return False
 if any(bad in n for bad in ("poster","book cover","souvenir","museum wall","selfie","portrait of john martin","photo of","framed","statue","exhibition")):return False
 return "john martin" in n or "martin, john" in n or "martin john" in n
v6.suitable_filename=safe

# Stronger documentable alternate: if the specific new score cannot be retrieved,
# do NOT substitute unlicensed music. Use a tested CC BY recording and record it.
def tested_music(music,folder,seconds):
 try: return original_download(music,folder,seconds)
 except Exception as exc:
  print("Music primary unavailable, validated license fallback:",str(exc)[:150],flush=True)
  music.clear();music.update(v6.SOUND["darkest_child"])
  return original_download(music,folder,seconds)
v6.audio_download=tested_music

orig_sources=v6.sources
def curate_sources(slug,cfg,folder):
 artworks,errors=orig_sources(slug,cfg,folder)
 # No gallery of identical scans of a famous painting: choose one per composition
 # whenever nine or more distinct motifs are available.
 def composition(rec):
  text=rec["title"].casefold().replace("_"," ")
  for motif in cfg["key"]:
   if motif in text:return motif
  return re.sub(r"[^a-z]+","",text)[:45]
 unique=[];used=set();others=[]
 for rec in artworks:
  motif=composition(rec)
  if motif in used:others.append(rec);continue
  used.add(motif);unique.append(rec)
 result=(unique+others[:max(0,9-len(unique))])[:15]
 if len(result)<6:raise RuntimeError("Fewer than six verified original artworks")
 print("Curated",len(result),"of",len(artworks),"verified artworks",flush=True)
 return result,errors
v6.sources=curate_sources

# Original authorial decisions by composition, not random auto-focus.
# Five narrative acts. Each work receives a different visual grammar.
ORDER=[
 ("great day of his wrath","The fracture",(.53,.38),(.69,.72)),
 ("pandemonium","The infernal metropolis",(.43,.57),(.76,.37)),
 ("belshazzar","The banquet of power",(.46,.56),(.72,.61)),
 ("joshua commanding","The stalled sun",(.61,.34),(.38,.68)),
 ("seventh plague","The darkening sky",(.54,.33),(.64,.71)),
 ("destruction of tyre","Fire on the sea",(.69,.42),(.41,.66)),
 ("sodom","The burning horizon",(.65,.52),(.33,.70)),
 ("deluge","The flood",(.46,.62),(.64,.32)),
 ("last judgement","The final division",(.58,.44),(.37,.69)),
 ("plains of heaven","A horizon of light",(.49,.43),(.73,.62)),
]
def make_film_shots(works,cfg,slug):
 # Identify these actual works, then join additional distinct authentic paintings.
 selected=[];used=set()
 for token,act,a,b in ORDER:
  item=next((w for w in works if token in w["title"].casefold() and w["id"] not in used),None)
  if item:
   selected.append((item,act,a,b));used.add(item["id"])
 extras=[w for w in works if w["id"] not in used]
 # Use 11-13 distinct works with the final hopeful chapter reserved for the end.
 light=[x for x in selected if "plains of heaven" in x[1].casefold() or "horizon of light" in x[1].casefold()]
 selected=[x for x in selected if x not in light]
 for w in extras[:max(0,12-len(selected)-len(light))]:
  selected.append((w,"Visions beyond the frame",(.42,.41),(.65,.59)))
 selected+=light
 # If an art archive enforces temporary download limits, keep an authorial film:
 # a second camera movement on a major work instead of unlicensed filler images.
 if selected:
  unique_first=list(selected)
  for j in range(max(0,10-len(selected))):
   work=unique_first[(j*2+1)%len(unique_first)][0]
   selected.append((work,"Ripresa tematica — dettagli monumentali",(.31+.08*(j%3),.48),(.67,.58)))
 # Circular return to the opening picture after the light; it is a cinematic epilogue.
 if selected: selected.append((selected[0][0],"Coda — memory of the first catastrophe",(.5,.52),(.5,.5)))
 shots=[]
 modes=[
  [("texture","left"),("glide","right"),("whole","centre")],
  [("portrait","right"),("whole","centre"),("texture","left")],
  [("whole","centre"),("glide","left"),("portrait","right")],
  [("texture","right"),("portrait","left"),("whole","centre")],
  [("glide","right"),("texture","left"),("whole","centre")],
  [("portrait","left"),("glide","right"),("whole","centre")],
 ]
 for i,(work,act,focus_a,focus_b) in enumerate(selected):
  seq=modes[i%len(modes)]
  if i==0:seq=[("texture","right"),("glide","left"),("whole","centre")]
  if i==len(selected)-2:seq=[("portrait","left"),("glide","right"),("whole","centre")]
  if i==len(selected)-1:seq=[("glide","left"),("whole","centre")]
  for j,(kind,where) in enumerate(seq):
   f=focus_a if where=="left" else (focus_b if where=="right" else (.5,.5))
   note=(f"{act} — {work['title']}: "+
     {"texture":"materia pittorica e forme emergenti","portrait":"scala monumentale vista da un dettaglio",
      "glide":"spostamento lento tra masse di luce e oscurità","whole":"rivelazione leggibile della composizione intera"}[kind])
   join=("dissolve" if (kind=="whole" and j==0 and i in (2,5,8,len(selected)-2))
         else ("match" if j==0 and i%3==1 else "cut"))
   weight={"texture":2.15,"glide":2.8,"portrait":2.9,"whole":3.25}[kind]
   if i==0:weight*=1.05
   if i==len(selected)-2:weight*=1.18
   if i==len(selected)-1 and j==len(seq)-1:weight*=1.26
   shots.append(cinema.Shot(len(shots),work,kind,f,weight,note,join))
 if len(shots)<29:raise RuntimeError(f"Only {len(shots)} directed shots")
 factor=cfg["duration"]/sum(s.duration for s in shots)
 for shot in shots:shot.duration*=factor
 # Persist V13 project for genuine V17 quality checks and Android editorial history.
 root=v6.ROOT/slug
 assets=[{
  "id":w["id"],"role":"visual",
  "file":str(Path("sources/original_images")/Path(w["file"]).name),
  "rights":w["license"]+" — "+w["url"]
 }for w in works]
 scenes=[{
  "asset_id":s.art["id"],"description":s.why,
  "reason":s.why,"camera_mode":s.kind,"focus":list(s.focus),
  "duration":round(s.duration,3)
 }for s in shots]
 project={
  "schema":"video-project-v13","format":"artvision_cinema","title":"John Martin — Visioni della fine",
  "artist":"John Martin","duration":cfg["duration"],"assets":assets,"scenes":scenes,
  "music":{"title":v6.SOUND[cfg["track"]]["title"],"license":"CC BY 4.0"},
  "status":"rendering_needs_visual_review","automatic_publication":False,
  "director":"ArtVision Cinema V6 Gold Master plus independent authored Martin sequence",
  "business":{"audience":"international art and culture","promise":"epic artworks in cinematic visual stories",
    "goal":"original artistic retention not guaranteed","budget":"zero paid API"}
 }
 (root/"PROJECT_V13.json").write_text(json.dumps(project,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return shots
v6.directed_shots=make_film_shots

if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--artist",default=SLUG,choices=[SLUG])
 _=ap.parse_args()
 v6.make(SLUG)
