#!/usr/bin/env python3
"""Create illustrated + textual Oz dossier from the actual rendered episode."""
import json,textwrap,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from episode_v3 import branded_cover
EP=Path("episodes/oz_dorothy_20261026")
OUT=Path("output/oz_dorothy_20261026")
SERIES="TRA LE PAGINE  ·  CLASSICI CHE PARLANO ANCORA"
def font(size,serif=False):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+("DejaVuSerif.ttf" if serif else "DejaVuSans.ttf"),size)
def paragraph(draw,xy,s,fill,size=25,width=65,spacing=7):
 x,y=xy
 for block in textwrap.wrap(str(s),width=width,break_long_words=False,break_on_hyphens=False):
  draw.text((x,y),block,font=font(size),fill=fill);y+=size+spacing
 return y
def make_board(plan,meta):
 cream="#f1ede4";navy="#132638";gold="#dfb875"
 poster=Image.new("RGB",(1800,2850),cream);d=ImageDraw.Draw(poster)
 d.rectangle((0,0,1800,770),fill=navy)
 cover=Image.open(OUT/"COPERTINA_SERIE.jpg").convert("RGB")
 cover=ImageOps.fit(cover,(388,648),centering=(.5,.5))
 poster.paste(cover,(68,68))
 d.text((515,85),SERIES,font=font(29),fill=gold)
 d.text((515,154),"Il meraviglioso",font=font(67,True),fill="#fff7e9")
 d.text((515,239),"mago di Oz",font=font(92,True),fill="#fff7e9")
 d.text((519,359),"L. Frank Baum  ·  1900",font=font(31),fill="#e8cba0")
 d.text((519,435),"Una casa nel ciclone. Quattro desideri.",font=font(32),fill="#f2efe5")
 d.text((519,480),"E un Mago che non è ciò che sembra.",font=font(32),fill="#f2efe5")
 paragraph(d,(519,580),"Nella Città di Smeraldo tutti vedono verde per colpa degli occhiali. Ma l'inganno più grande deve ancora essere svelato.",fill="#e2e8e8",size=25,width=67)
 d.text((68,796),"STORYBOARD  ·  25 MOMENTI DEL RACCONTO",font=font(38,True),fill=navy)
 for i,row in enumerate(plan):
  col,rownum=i%5,i//5
  x,y=68+col*347,862+rownum*314
  d.rounded_rectangle((x,y,x+326,y+292),radius=14,fill="#fffaf1",outline="#d9c4a6",width=2)
  art=Image.open(EP/"images"/f"scena_{i+1:02d}.jpg").convert("RGB")
  thumb=ImageOps.contain(art,(295,208))
  poster.paste(thumb,(x+(326-thumb.width)//2,y+8))
  d.text((x+12,y+223),f"{i+1:02d}  "+textwrap.shorten(row["intent"],width=32,placeholder="…"),
         font=font(17),fill=navy)
  d.text((x+12,y+258),row["camera_style"].replace("_"," "),font=font(16),fill="#94734b")
 y=2475
 d.rectangle((68,y,1734,2812),fill="#e4dfd1",outline="#b5a58c",width=2)
 d.text((91,y+20),"FONTI, DIRITTI E PRODUZIONE",font=font(28,True),fill=navy)
 d.text((91,y+80),"Opera: The Wonderful Wizard of Oz — L. Frank Baum (1900)",font=font(24),fill=navy)
 d.text((91,y+123),"Illustrazioni: W. W. Denslow, prima edizione del 1900 (pubblico dominio)",font=font(22),fill=navy)
 d.text((91,y+168),"Voce: Google Gemini Gacrux  ·  Musica: composizione strumentale originale",font=font(21),fill=navy)
 d.text((91,y+211),"Fonte: Library of Congress e Project Gutenberg 43936",font=font(22),fill=navy)
 d.text((91,y+260),"Stato: render tecnico completo; revisione artistica e termini voce da verificare",font=font(19),fill="#71532a")
 path=OUT/"OZ_SCHEDA_PRESENTAZIONE.jpg";poster.save(path,quality=92,optimize=True)
 return path
def make_files():
 OUT.mkdir(parents=True,exist_ok=True)
 plan=json.loads((EP/"scene_plan_oz.json").read_text())["scenes"]
 meta=json.loads((EP/"metadata.json").read_text())
 quality=json.loads((OUT/"QUALITY.json").read_text())
 provenance=json.loads((EP/"PROVENIENZA_IMMAGINI.json").read_text())
 branded_cover(OUT,EP,meta)
 board=make_board(plan,meta)
 social={}
 for label in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
  content=(EP/f"POST_{label}.txt").read_text(encoding="utf-8")
  social[label.lower()]=content
  (OUT/f"POST_{label}.txt").write_text(content,encoding="utf-8")
 lines=["# TRA LE PAGINE — SCHEDA DI PRESENTAZIONE","",
  "## Il meraviglioso mago di Oz","**L. Frank Baum (1900) | Illustrazioni di W. W. Denslow (1900)**",
  "**Serie:** Classici che parlano ancora",
  "**Format:** libro raccontato in italiano; Google Gemini Gacrux",
  "**Stato:** render tecnico prodotto, ancora da valutare artisticamente; nessuna pubblicazione.",
  "**Durata finale:** "+str(quality["duration_s"])+" secondi",
  "**Scene:** "+str(len(plan))+" illustrazioni originali, senza numero obiettivo imposto.",
  "**Promessa:** chi cerca cuore, cervello e coraggio scopre di possedere già qualcosa di importante.",
  "**Hook:** Nella Città di Smeraldo tutti vedono verde perché portano occhiali verdi.","",
  "## Storyboard e scelte visuali"]
 for i,row in enumerate(plan):
  info=provenance["images"][i]
  lines.extend(["",f"### Scena {i+1:02d} — {row['intent']}",
                "- Voce: "+row["narration"],
                "- Illustrazione originale: "+info["source_alt"],
                "- URL fonte: "+info["source_url"],
                "- Regia motivata: "+row["camera_style"]])
 lines.extend(["","## Testo integrale della narrazione","",(EP/"testo.txt").read_text(encoding="utf-8"),
               "","## Fonte e diritti",
               "- Libro originale: https://www.gutenberg.org/ebooks/43936",
               "- Riproduzione originale: https://www.loc.gov/item/03032405/",
               "- Illustrazioni W. W. Denslow, 1900: pubblico dominio secondo la Library of Congress.",
               "- Sono state usate illustrazioni storiche, non fotogrammi o elementi del film del 1939.",
               "- Musica composta per questo video, nessuna registrazione di terzi.",
               "- Licenza/condizioni del provider vocale da confermare per la monetizzazione.",
               "- Valutazione artistica umana ancora richiesta.","",
               "## Descrizioni pronte per i social (soggette a revisione finale)"])
 for platform,body in social.items():
  lines.extend(["","### "+platform.title(),"",body])
 lines.extend(["","## File consegnati",
               "- TRA_LE_PAGINE_IL_MERAVIGLIOSO_MAGO_DI_OZ.mp4",
               "- COPERTINA_SERIE.jpg",
               "- OZ_SCHEDA_PRESENTAZIONE.jpg",
               "- OZ_SCHEDA_TESTO.md",
               "- POST_FACEBOOK/INSTAGRAM/TIKTOK/YOUTUBE.txt",
               "- PROVENIENZA_IMMAGINI.json",
               "- SINCRONIA_SCENE.json",
               "- QUALITY.json"])
 (OUT/"OZ_SCHEDA_TESTO.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 (OUT/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
 (OUT/"OZ_DOSSIER_SITO.json").write_text(json.dumps({
  "sourceVideo":quality["video"],"status":"ready_to_import_not_imported",
  "editorial":{"publicTitle":meta["title"],"project":"Tra le Pagine","seriesTitle":meta["series"],
   "category":"Libri raccontati","language":"it","bookAuthor":meta["author"],
   "publicationYear":"1900","hook":"Nella Città di Smeraldo tutti vedono verde: perché?",
   "shortDescription":"Dorothy e Toto incontrano amici che cercano cuore, cervello e coraggio.",
   "facebook":social["facebook"],"instagram":social["instagram"],
   "tiktok":social["tiktok"],"youtube":social["youtube"],
   "storyboard":"\n".join(f"{i+1}. {p['intent']}" for i,p in enumerate(plan)),
   "imageCredits":"W. W. Denslow, original 1900 edition (public domain)",
   "imageSources":"https://www.loc.gov/item/03032405/",
   "voiceCredits":"Google Gemini Gacrux",
   "musicTitle":"Oz — tema strumentale originale",
   "musicAuthor":"Tra le Pagine — Studio Ibrido",
   "musicLicense":"Composizione originale del progetto",
   "rightsStatus":"da_verificare","publicationStatus":"bozza",
   "publicationNotes":"Verificare termini di uso Gacrux e revisione artistica. Non importato automaticamente."}
  },ensure_ascii=False,indent=2))
 (OUT/"COPERTINA_OZ.jpg").write_bytes((OUT/"COPERTINA_SERIE.jpg").read_bytes())
 video=OUT/quality["video"]
 with zipfile.ZipFile(OUT/"OZ_SOLO_VIDEO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:z.write(video,video.name)
 full=OUT/"OZ_PACCHETTO_COMPLETO.zip"
 with zipfile.ZipFile(full,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for p in OUT.iterdir():
   if p.is_file() and p.name not in (full.name,"OZ_SOLO_VIDEO.zip","VOCE.wav","MUSICA_ORIGINALE.wav"):
    z.write(p,p.name)
  for im in sorted((EP/"images").glob("scena_*.jpg")):z.write(im,"ILLUSTRAZIONI/"+im.name)
 print("DELIVERY: cover, illustrated board, complete text dossier, 4 posts, video ZIP and full package",flush=True)
if __name__=="__main__":make_files()
