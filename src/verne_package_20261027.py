#!/usr/bin/env python3
"""Nautilus: branded cover, illustrated presentation and searchable complete dossier."""
from __future__ import annotations
import json,textwrap,zipfile,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
EP=Path("episodes/nautilus_20261027")
OUT=Path("output/nautilus_20261027")
NAVY=(15,34,49);GOLD=(212,177,116);INK=(20,38,53);PAPER=(241,235,222)
SOURCE="https://www.gutenberg.org/ebooks/54873"
def font(size,serif=False,bold=False):
 suffix="DejaVuSerif" if serif else "DejaVuSans"
 if bold:suffix+="-Bold"
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+suffix+".ttf",size)
def wrapped(d,text,xy,maxwidth,size=26,color=INK,spacing=9,bold=False,limit=None):
 face=font(size,bold=bold);words=str(text).split();lines=[];line=""
 for word in words:
  maybe=(line+" "+word).strip()
  if line and d.textbbox((0,0),maybe,font=face)[2]>maxwidth:
   lines.append(line);line=word
  else:line=maybe
 if line:lines.append(line)
 if limit is not None:lines=lines[:limit]
 x,y=xy
 for line in lines:
  d.text((x,y),line,font=face,fill=color);y+=size+spacing
 return y
def create_presentation(plan,meta,manifest,quality,social):
 W,H=2600,4490
 im=Image.new("RGB",(W,H),PAPER);d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,960),fill=NAVY)
 cover=ImageOps.fit(Image.open(OUT/"COPERTINA_SERIE.jpg").convert("RGB"),(490,835),centering=(.5,.4))
 im.paste(cover,(88,60))
 d.text((670,85),"TRA LE PAGINE  /  STUDIO IBRIDO",font=font(40,bold=True),fill=GOLD)
 d.text((670,155),"VENTIMILA LEGHE",font=font(92,True),fill=(251,247,236))
 d.text((670,268),"SOTTO I MARI",font=font(104,True),fill=(251,247,236))
 d.text((677,402),"JULES VERNE  ·  1869–1870",font=font(39),fill=(237,206,150))
 d.text((678,476),"CLASSICI CHE PARLANO ANCORA",font=font(33,bold=True),fill=(231,231,225))
 wrapped(d,"Il capitano Nemo era padrone del mare. Ma quale dolore lo aveva spinto a scomparire dal mondo?",(678,572),1710,34,(244,241,231),11)
 d.rounded_rectangle((675,765,2430,905),radius=20,fill=(40,68,83),outline=GOLD,width=3)
 d.text((712,790),"LIBRO RACCONTATO",font=font(31,bold=True),fill=(246,238,217))
 d.text((1238,790),f"{quality['duration_s']:.0f} s",font=font(31),fill=(246,238,217))
 d.text((1580,790),f"{len(plan)} SCENE",font=font(31),fill=(246,238,217))
 d.text((1940,790),"ITALIANO · GACRUX",font=font(26),fill=(246,238,217))
 d.text((90,1004),"STORYBOARD · IMMAGINI STORICHE AUTENTICHE",font=font(47,True),fill=NAVY)
 d.text((90,1073),"Scelte per il significato del racconto, non per raggiungere una quota.",font=font(29),fill=(101,90,78))
 # Five visual rows of five positions; incomplete last row remains empty.
 start_y=1155;pitch_x=500;pitch_y=404
 for i,row in enumerate(plan):
  col,rr=i%5,i//5
  x=74+col*pitch_x;y=start_y+rr*pitch_y
  d.rounded_rectangle((x,y,x+468,y+381),radius=16,fill=(255,251,241),outline=(211,190,157),width=3)
  art=Image.open(EP/"images"/f"scena_{i+1:02d}.jpg").convert("RGB")
  thumb=ImageOps.contain(art,(448,285),Image.Resampling.LANCZOS)
  im.paste(thumb,(x+(468-thumb.width)//2,y+8+(285-thumb.height)//2))
  d.rectangle((x+13,y+13,x+67,y+63),fill=NAVY)
  d.text((x+23,y+23),str(i+1).zfill(2),font=font(25,bold=True),fill=(255,246,226))
  wrapped(d,row["visual_intent"],(x+16,y+301),440,23,INK,6,True,limit=2)
 d.line((74,3235,2520,3235),fill=GOLD,width=5)
 d.text((83,3280),"PERCHÉ RACCONTARE QUESTA STORIA",font=font(39,True),fill=NAVY)
 wrapped(d,"Un classico che trasforma la scoperta scientifica in un conflitto umano: la libertà assoluta del capitano Nemo diventa prigionia per i suoi ospiti.",(85,3350),2380,28,INK,10)
 d.text((83,3512),"TRE CHIAVI DI LETTURA",font=font(35,True),fill=NAVY)
 themes=[
 ("MERAVIGLIA","Le città sommerse, le foreste marine, le invenzioni impossibili."),
 ("MISTERO","Il segreto del Nautilus e la storia taciuta di Nemo."),
 ("CONTRASTO","Lo stesso uomo capace di compassione e di terribili vendette.")]
 for i,(name,desc) in enumerate(themes):
  x=85+i*828;y=3578
  d.rounded_rectangle((x,y,x+797,y+180),radius=15,fill=(226,220,206))
  d.text((x+25,y+18),name,font=font(26,bold=True),fill=NAVY)
  wrapped(d,desc,(x+25,y+75),748,24,INK,6,limit=3)
 d.text((83,3800),"DESCRIZIONI SOCIAL · ANTEPRIMA",font=font(35,True),fill=NAVY)
 for i,(platform,body) in enumerate(social.items()):
  x=85+(i%2)*1245;y=3855+(i//2)*167
  d.rounded_rectangle((x,y,x+1195,y+147),radius=14,fill=(255,252,244),outline=(201,188,162),width=2)
  d.text((x+16,y+13),platform.upper(),font=font(23,bold=True),fill=NAVY)
  words=body.split()
  clean=" ".join(words[:27])+"…"
  wrapped(d,clean,(x+18,y+54),1150,20,INK,5,limit=3)
 d.rectangle((0,4240,W,H),fill=NAVY)
 d.text((80,4265),"FONTI E CREDITI",font=font(32,bold=True),fill=GOLD)
 wrapped(d,"Jules Verne, Vingt mille lieues sous les mers (1869–1870). Incisioni di Alphonse de Neuville ed Édouard Riou, edizione illustrata Hetzel.",(80,4320),2420,24,(252,249,238),8,limit=3)
 d.text((80,4412),"Project Gutenberg 54873  ·  Musica originale  ·  Stato: revisione artistica / voce commerciale pendenti",
        font=font(20),fill=(233,211,176))
 path=OUT/"SCHEDA_PRESENTAZIONE.jpg";im.save(path,quality=91,optimize=True)
 return path

def storyboard_image(plan):
 W=2400;cols=4;rows=(len(plan)+cols-1)//cols
 H=165+rows*470+115
 im=Image.new("RGB",(W,H),(239,233,217));d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,135),fill=NAVY)
 d.text((70,37),"VENTIMILA LEGHE SOTTO I MARI · TUTTE LE SCENE",font=font(46,True),fill=(249,243,224))
 for i,row in enumerate(plan):
  x=50+(i%cols)*586;y=165+(i//cols)*470
  d.rounded_rectangle((x,y,x+558,y+440),radius=15,fill=(255,252,246),outline=(193,171,131),width=3)
  picture=Image.open(EP/"images"/f"scena_{i+1:02d}.jpg").convert("RGB")
  thumb=ImageOps.contain(picture,(530,350),Image.Resampling.LANCZOS)
  im.paste(thumb,(x+(558-thumb.width)//2,y+12+(350-thumb.height)//2))
  d.text((x+14,y+374),f"{i+1:02d} · "+row["visual_intent"][:38],font=font(20,bold=True),fill=NAVY)
  d.text((x+14,y+409),row["source_image_id"]+" · de Neuville / Riou",font=font(17),fill=(105,96,77))
 out=OUT/"STORYBOARD_COMPLETO.jpg";im.save(out,quality=91,optimize=True)
 return out

def write():
 from episode_v3 import branded_cover
 OUT.mkdir(parents=True,exist_ok=True)
 plan=json.loads((EP/"scene_plan_verne.json").read_text(encoding="utf-8"))["scenes"]
 meta=json.loads((EP/"metadata.json").read_text(encoding="utf-8"))
 provenance=json.loads((EP/"PROVENIENZA_IMMAGINI.json").read_text(encoding="utf-8"))
 qa=json.loads((OUT/"QUALITY.json").read_text(encoding="utf-8"))
 branded_cover(OUT,EP,meta)
 social={p.lower():(EP/f"POST_{p}.txt").read_text(encoding="utf-8") for p in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")}
 for plat,copy in social.items():(OUT/f"POST_{plat.upper()}.txt").write_text(copy,encoding="utf-8")
 create_presentation(plan,meta,provenance["images"],qa,social)
 storyboard_image(plan)
 opening="C'era un uomo che aveva rinunciato alla terraferma. Il capitano Nemo."
 lines=[
 "# TRA LE PAGINE — DOSSIER COMPLETO","",
 "## Ventimila leghe sotto i mari — Jules Verne",
 "**Serie:** Classici che parlano ancora",
 "**Soggetto:** mistero di Nemo e meraviglia degli abissi.",
 f"**Durata master:** {qa['duration_s']} secondi.",
 f"**Scene e incisioni distinte:** {len(plan)} (numero derivato dalla storia).",
 "**Voce:** Google Gemini Gacrux; sincronizzazione da audio effettivo.",
 "**Musica:** composizione strumentale originale, realizzata per l'episodio.",
 "**Copertina:** serie Tra le Pagine, titolo e autore.",
 f"**Hook:** {opening}",
 "**Output:** verticale 720×1280, MP4 H.264 + AAC, senza sottotitoli.",
 "**Stato:** prodotto tecnicamente; revisione artistica e verifica commerciale del servizio TTS ancora necessarie.",
 "**Importazione videoteca:** non eseguita. **Pubblicazione:** non eseguita.",
 "",
 "## Motivazione editoriale",
 "Un'avventura in cui l'ingegno tecnologico convive con solitudine e vendetta: Nemo ha costruito il proprio regno, ma non riesce a sottrarsi al suo passato.",
 "",
 "## Storyboard dettagliato, collegamento parlato/incisioni"
 ]
 for i,(row,im) in enumerate(zip(plan,provenance["images"]),1):
  lines += ["",f"### {i:02d} · {row['visual_intent']}",
    "**Narrato:** "+row["narration"],
    "**Immagine originale:** "+im["original_caption"],
    "**Fonte immagine:** "+im["source_url"],
    "**Movimento previsto:** "+row["camera_style"].replace("_"," "),
    "**Scelta artistica:** "+row["justification"]]
 lines+=["","## Testo integrale narrato","",(EP/"testo.txt").read_text(encoding="utf-8"),
    "","## Fonti, uso commerciale e limiti delle verifiche",
    "- Jules Verne, *Vingt mille lieues sous les mers* (1869–1870).",
    "- Original engraved illustrated edition by Alphonse de Neuville (1835–1885) and Édouard Riou (1833–1900).",
    "- Source digitized and catalogued: "+SOURCE,
    "- In Italia i diritti patrimoniali sulle opere originali di questi autori sono scaduti; verificare sempre i termini del file digitalizzato.",
    "- Crediti conservati per ciascuna fonte originale nel JSON allegato.",
    "- TTS: Google Gemini Gacrux; le condizioni di utilizzo commerciale non sono qui attestate.",
    "- Musica generata come composizione originale del progetto, senza file musicali di terzi.",
    "- Il controllo automatico MP4 non sostituisce l'ascolto e la visione artistica.",
    "","## Descrizioni pubbliche, distinte per piattaforma"]
 for name,copy in social.items():lines+=["",f"### {name.capitalize()}","",copy]
 lines+=["","## File consegnati",
    "- TRA_LE_PAGINE_VENTIMILA_LEGHE_SOTTO_I_MARI.mp4",
    "- COPERTINA_SERIE.jpg",
    "- SCHEDA_PRESENTAZIONE.jpg e STORYBOARD_COMPLETO.jpg",
    "- SCHEDA_TESTO.md",
    "- POST_FACEBOOK.txt, POST_INSTAGRAM.txt, POST_TIKTOK.txt, POST_YOUTUBE.txt",
    "- PROVENIENZA_IMMAGINI.json",
    "- SINCRONIA_SCENE.json, ALLINEAMENTO_VOCE.json e QUALITY.json",
    "- DOSSIER_SITO.json",
    "- SOLO_VIDEO.zip e PACCHETTO_COMPLETO.zip"]
 (OUT/"SCHEDA_TESTO.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 (OUT/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding="utf-8")
 site={"status":"ready_to_import_not_imported","sourceVideo":qa["file"],
    "editorial":{"publicTitle":meta["title"],"project":"Tra le Pagine",
    "seriesTitle":meta["series"],"category":"Libri raccontati","language":"it",
    "bookAuthor":meta["author"],"publicationYear":str(meta["year"]),
    "hook":opening,"shortDescription":"A bordo del Nautilus, il misterioso capitano Nemo custodisce meraviglie e una ferita impossibile da dimenticare.",
    **social,"storyboard":"\n".join(f"{i+1}. {row['visual_intent']}" for i,row in enumerate(plan)),
    "script":(EP/"testo.txt").read_text(encoding="utf-8"),
    "imageCredits":"Alphonse de Neuville and Édouard Riou (original illustrated edition)",
    "imageSources":SOURCE,"voiceCredits":"Google Gemini Gacrux",
    "musicTitle":"Nautilus — abissi e memoria","musicAuthor":"Tra le Pagine — Studio Ibrido",
    "musicLicense":"Original composition",
    "rightsStatus":"da_verificare","publicationStatus":"bozza",
    "publicationNotes":"Rights and artistic review pending; not published or uploaded to site."}}
 (OUT/"DOSSIER_SITO.json").write_text(json.dumps(site,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 video=OUT/qa["file"]
 if not video.is_file() or video.stat().st_size<200000:raise RuntimeError("Master MP4 missing")
 with zipfile.ZipFile(OUT/"SOLO_VIDEO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  z.write(video,video.name)
 with zipfile.ZipFile(OUT/"PACCHETTO_COMPLETO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=2) as z:
  for p in sorted(OUT.iterdir()):
   if p.is_file() and p.name not in ("SOLO_VIDEO.zip","PACCHETTO_COMPLETO.zip","VOCE.wav","MUSICA_ORIGINALE.wav"):
    z.write(p,p.name)
  for p in sorted((EP/"images").glob("scena_*.jpg")):z.write(p,"ILLUSTRAZIONI/"+p.name)
  z.write(EP/"testo.txt","COPIONE_ORIGINALE.txt")
  z.write(EP/"scene_plan_verne.json","STORYBOARD_DATI.json")
 print("DOSSIER_READY",json.dumps({"MP4":video.stat().st_size,
         "board":(OUT/"SCHEDA_PRESENTAZIONE.jpg").stat().st_size,
         "zip":(OUT/"PACCHETTO_COMPLETO.zip").stat().st_size,
         "images":len(plan)},ensure_ascii=False),flush=True)

if __name__=="__main__":write()
