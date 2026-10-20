#!/usr/bin/env python3
"""Caravaggio: artistic Cinema V6 grammar, bespoke 5-act shadow-and-light montage.
Does not modify frozen, user-approved Van Gogh Cinema V6.
"""
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import director_cinema_v6 as cinema

# [Artwork, shot, normalized focus, relative duration, authored editorial motive, cut type]
# Caravaggio compositions are authored separately from the Van Gogh V6 map.
SHOTS=[
 # ACT I: First contact — a face is revealed, a gesture of doubt, revelation of the light
 ("David with the Head of Goliath","portrait",(.35,.38),3.1,"David's face emerges from darkness","cut"),
 ("David with the Head of Goliath","texture",(.66,.65),2.3,"The severed head and the shadow beneath it","cut"),
 ("The Calling of Saint Matthew","portrait",(.68,.45),2.7,"A hand summons Matthew through a shaft of light","match"),
 ("The Calling of Saint Matthew","texture",(.38,.51),2.5,"The questioning faces and pointing fingers","cut"),
 ("The Calling of Saint Matthew","whole",(.5,.5),3.3,"First release into entire chapel composition","dissolve"),
 ("The Incredulity of Saint Thomas","portrait",(.53,.44),2.75,"Faces gathered around the wound","match"),
 ("The Incredulity of Saint Thomas","texture",(.49,.61),2.25,"Hands and astonishment, tactile drama","cut"),
 ("Supper at Emmaus","portrait",(.45,.42),2.65,"Christ and the startled disciple","match"),
 ("Supper at Emmaus","texture",(.76,.55),2.45,"Arms opening in surprise","cut"),
 ("The Taking of Christ","portrait",(.40,.40),3.05,"Judas and Christ confronting each other in the dark","dissolve"),
 ("The Taking of Christ","texture",(.71,.60),2.4,"The metal armoured glove catching the light","cut"),
 # ACT II: Beauty is material — fruit, music, youth and surprise.
 ("Basket of Fruit","whole",(.5,.5),3.0,"Unexpected still-life quiet after drama","dissolve"),
 ("Basket of Fruit","texture",(.52,.58),2.35,"Fruit skin and dried leaves, passage of time","cut"),
 ("Bacchus","portrait",(.48,.36),3.0,"Bacchus gaze in a flare of warm light","match"),
 ("Bacchus","texture",(.66,.66),2.55,"The wineglass and human hand","cut"),
 ("Young Sick Bacchus","portrait",(.51,.32),2.65,"The pale self-portrait, uneasy youth","match"),
 ("Boy Bitten by a Lizard","portrait",(.54,.37),2.8,"A sudden grimace interrupts composure","cut"),
 ("Boy Bitten by a Lizard","texture",(.49,.65),2.4,"The startled hand near the flowers and lizard","cut"),
 ("The Cardsharps","portrait",(.69,.42),2.9,"The conspiratorial eyes of the cheat","match"),
 ("The Cardsharps","texture",(.51,.68),2.4,"Cards and concealed manipulation","cut"),
 ("The Musicians","portrait",(.39,.35),2.75,"Youthful faces in a pool of concert light","match"),
 ("The Musicians","texture",(.64,.62),2.55,"Hands holding a musical instrument","cut"),
 # ACT III: Sacred touch — flesh, hand and flesh, with greater contemplative pauses.
 ("Rest on the Flight into Egypt","whole",(.5,.5),3.75,"An unusually tender respite for the audience","dissolve"),
 ("Rest on the Flight into Egypt","portrait",(.32,.49),3.0,"The angel musician as quiet luminous presence","match"),
 ("Rest on the Flight into Egypt","texture",(.66,.59),2.5,"Sleeping child, maternal tenderness","cut"),
 ("Saint Jerome Writing","portrait",(.43,.44),3.0,"A solitary scholar in the darkness","dissolve"),
 ("Saint Jerome Writing","texture",(.69,.68),2.4,"Writing hand, page and skull as mortality signs","cut"),
 ("The Conversion of Saint Paul","whole",(.5,.5),3.65,"Body beneath towering horse, a theatrical revelation","dissolve"),
 ("The Conversion of Saint Paul","portrait",(.42,.72),2.8,"The figure with open arms in the light","cut"),
 ("Crucifixion of Saint Peter","portrait",(.39,.56),2.85,"Peter's face and weight of the body","match"),
 ("Crucifixion of Saint Peter","texture",(.68,.66),2.3,"Working hands and ropes bearing weight","cut"),
 ("The Entombment of Christ","portrait",(.48,.62),3.25,"Human weight and tenderness","dissolve"),
 ("The Entombment of Christ","texture",(.32,.41),2.45,"Faces above the white winding sheet","cut"),
 ("The Entombment of Christ","whole",(.5,.5),3.6,"The whole group in a stage of light","dissolve"),
 # ACT IV: Chiaroscuro crescendo and psychological shock, somewhat faster but legible.
 ("Judith Beheading Holofernes","portrait",(.38,.44),2.75,"Judith's tense face against black","cut"),
 ("Judith Beheading Holofernes","texture",(.66,.56),2.15,"A hand and blade intersect the illuminated throat","cut"),
 ("Judith Beheading Holofernes","whole",(.5,.5),2.65,"Full drama revealed, no sensationalistic visual embellishment","match"),
 ("David with the Head of Goliath","portrait",(.60,.62),2.65,"The head in half-light answers Judith","match"),
 ("David with the Head of Goliath","texture",(.34,.39),2.3,"The youth's expression, compassion mixed with violence","cut"),
 ("The Taking of Christ","portrait",(.52,.46),2.55,"The kiss becomes betrayal","match"),
 ("The Taking of Christ","texture",(.76,.57),2.15,"An armoured hand points to the arrest","cut"),
 ("The Incredulity of Saint Thomas","texture",(.47,.57),2.6,"The wound and fingers, mirror of the gesture","match"),
 ("The Cardsharps","portrait",(.67,.35),2.55,"A different deception told by a gaze","cut"),
 ("The Calling of Saint Matthew","portrait",(.57,.40),2.5,"An arm emerging from darkness cuts toward grace","match"),
 ("The Conversion of Saint Paul","portrait",(.49,.53),2.5,"The horse and the fallen man, scale and surrender","cut"),
 ("Supper at Emmaus","portrait",(.56,.42),2.75,"Revelation through one lifted hand","match"),
 # ACT V: After-image — mystery subsides, iconographic motifs come full circle.
 ("Narcissus","whole",(.5,.5),3.5,"A reflective moment, the human being facing himself","dissolve"),
 ("Narcissus","portrait",(.54,.35),2.95,"Narcissus gaze toward the reflected self","cut"),
 ("Narcissus","texture",(.57,.68),2.5,"The image in the dark water","dissolve"),
 ("Bacchus","portrait",(.50,.36),2.8,"A painted face comes back to life","match"),
 ("The Musicians","whole",(.5,.5),3.65,"Music and human encounter as a visual coda","dissolve"),
 ("The Incredulity of Saint Thomas","whole",(.5,.5),3.35,"Whole canvas reveals the intimacy of the gesture","dissolve"),
 ("The Taking of Christ","whole",(.5,.5),3.2,"Dark silhouettes and a single lantern","cut"),
 ("The Calling of Saint Matthew","portrait",(.43,.52),2.9,"The visual arrow of the hand returns","match"),
 ("The Calling of Saint Matthew","whole",(.5,.5),3.5,"Full composition; one final breath","dissolve"),
 ("David with the Head of Goliath","portrait",(.35,.40),3.0,"Return to the first gaze","match"),
 ("David with the Head of Goliath","whole",(.5,.5),4.1,"Final image held in silence-like restraint","dissolve"),
]

# Additional authored reverse angles and complete-work releases, distributed WITHIN each act,
# never all grouped at the end. Every addition has a visual purpose.
INSERT_AFTER_FIRST={
 "David with the Head of Goliath":[
  ("whole",(.5,.5),2.7,"Entire composition establishes weight and unease","dissolve"),
  ("texture",(.46,.64),2.2,"Sword diagonal divides the bodies","match")],
 "The Calling of Saint Matthew":[
  ("texture",(.65,.26),2.3,"Hand and diagonal ray of illumination","cut"),
  ("portrait",(.29,.61),2.6,"Coins and hands at Matthew's table","match")],
 "Judith Beheading Holofernes":[
  ("texture",(.25,.51),2.2,"The older maid's tense watchfulness","cut"),
  ("texture",(.79,.49),2.2,"Holofernes' expression as emotional counterpoint","cut")],
 "Supper at Emmaus":[("whole",(.5,.5),3.3,"Painted theatrical tableau finally revealed","dissolve")],
 "The Incredulity of Saint Thomas":[("whole",(.5,.5),3.2,"Four figures seen as one intimate composition","dissolve")],
 "Basket of Fruit":[("portrait",(.53,.37),2.7,"The leaf silhouettes against blank wall","cut")],
 "The Cardsharps":[("whole",(.5,.5),2.7,"Three-player geometry of deception","dissolve")],
 "Rest on the Flight into Egypt":[("texture",(.31,.31),2.4,"Angel wings, sheet music and fragile light","cut")],
 "Saint Jerome Writing":[("whole",(.5,.5),3.3,"Red robe, book and skull align as an emblem","dissolve")],
 "Narcissus":[("texture",(.30,.57),2.3,"Curving arm unites figure with reflection","cut")],
 "The Conversion of Saint Paul":[("texture",(.56,.25),2.4,"Horse's body eclipses the upper light","cut")],
}
def compose_full_story(base):
    result=[];visited=set()
    for shot in base:
        result.append(shot)
        title=shot[0]
        if title not in visited and title in INSERT_AFTER_FIRST:
            visited.add(title)
            for mode,focus,duration,reason,trans in INSERT_AFTER_FIRST[title]:
                result.append((title,mode,focus,duration,reason,trans))
    return result
SHOTS=compose_full_story(SHOTS)

# Dal prossimo rendering si utilizza il MODELLO GRAFICO UNICO della serie.
# La versione del video Caravaggio già approvata non viene modificata;
# il codice originale è conservato nel branch di backup dedicato.
from identita_visiva_v6 import signature as artvision_signature

def label_caravaggio(img,t):
    return artvision_signature(img, t, "Caravaggio", "Kevin MacLeod")

def main():
    root=Path("output/caravaggio-cinema-sources")
    out=Path("output/caravaggio-cinema-film")
    artworks=cinema.load_artworks(root)
    cinema.STORY=SHOTS
    cinema.label_title=label_caravaggio
    shots=cinema.resolve_items(artworks,150)
    if len(shots)<43:raise RuntimeError("Not enough curated Caravaggio shots: "+str(len(shots)))
    distinct={s.art["title"] for s in shots}
    if len(distinct)<12:raise RuntimeError("Only "+str(len(distinct))+" Caravaggio artworks, refusing generic slideshow")
    print("CARAVAGGIO V6 FILM",len(shots),"directed shots,",len(distinct),"genuine works",flush=True)
    path,timeline=cinema.render(shots,root,out,duration=150)
    finished=out/"ARTVISION_CARAVAGGIO_CINEMA_V6.mp4"
    path.replace(finished)
    old=out/"COPERTINA_CINEMA_V6.jpg"
    old.replace(out/"COPERTINA_CARAVAGGIO.jpg")
    source_meta=json.loads((root/"artworks.json").read_text())
    used={s.art["id"] for s in shots}
    verified=[x for x in source_meta["metadata"] if x["id"] in used]
    soundtrack=json.loads((root/"music_rights.json").read_text())
    soundtrack.update({"public_caption_attribution_required":True,"on_screen_credit":"MUSIC BY KEVIN MACLEOD"})
    (out/"RIGHTS_AND_SOURCES.json").write_text(json.dumps({
        "artist":"Caravaggio","style":"approved_Cinema_V6",
        "works":verified,"music":soundtrack,
        "publishing_approved":False,
        "license_note":"Before commercial publishing, verify photographic rights and any Italian cultural-heritage restrictions."},
        ensure_ascii=False,indent=2),encoding="utf-8")
    credit=['CARAVAGGIO — ART VISION CINEMA','', '"Darkest Child" Kevin MacLeod (incompetech.com)',"Creative Commons Attribution 4.0",
            "https://creativecommons.org/licenses/by/4.0/","Music edited (excerpt, fades, volume adjustment).","","Image sources:"]
    credit += [f'{x["title"]} — {x["source"]} — {x["url"]} — {x["license"]}' for x in verified]
    (out/"DESCRIPTION_AND_CREDITS.txt").write_text("\n".join(credit)+"\n",encoding="utf-8")
    report={"artist":"Caravaggio","format":"1080x1920 24fps H264 AAC",
            "works":len(verified),"shots":len(timeline),"duration_seconds":150,
            "source":"Wikimedia Commons per-file verified rights","music":"Darkest Child - Kevin MacLeod CC BY 4.0",
            "voice":"none","paid_api":False,"published":False}
    (out/"PRODUCTION_REPORT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("CARAVAGGIO V6 SUCCESS",json.dumps(report,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
