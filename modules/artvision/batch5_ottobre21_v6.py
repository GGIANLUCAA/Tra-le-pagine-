#!/usr/bin/env python3
"""Terzo lotto ArtVision: 5 artisti nuovi, Cinema V6 adattata senza cambiare Gold Master.
Eredita da batch5_cinema_v6 i metodi di montaggio/controllo e l'identità V6 fissa.
"""
from __future__ import annotations
import re
from pathlib import Path
import batch5_cinema_v6 as v6
from batch5_cinema_v6 import make as render_artist

v6.ROOT=Path("output/artvision-terzo-lotto-v6")
v6.P.clear()
v6.P.update({
 "munch":{
  "name":"Edvard Munch","duration":108,
  "hero":"Edvard Munch - The Scream - NG.M.00939 - National Museum of Art, Architecture and Design.jpg",
  "featured":["Edvard Munch - The Scream, 1910 (Munch Museum).jpg","Edvard Munch - Madonna (1894-1895).jpg","Edvard Munch - Anxiety - Google Art Project.jpg","Edvard Munch - The Kiss - MM.M.00059 - Munch Museum.jpg","Edvard Munch - The Dance of Life - NG.M.00941 - National Museum of Art, Architecture and Design.jpg","Edvard Munch - The Sick Child - NG.M.00839 - National Museum of Art, Architecture and Design.jpg","Edvard Munch - Jealousy 1895.jpg","Edvard Munch - Melancholy (1894-96).jpg","Edvard Munch - Self-portrait (1886).jpg","Edvard Munch - Self-Portrait - MM.M.01049 - Munch Museum.jpg","Edvard Munch - Melancholy (1893).jpg"],
  "key":["scream","the kiss","madonna","vampire","melancholy","anxiety","sick child","dance of life","self portrait","girls on bridge","jealousy"],
  "find":["Edvard Munch paintings melancholy Madonna","Edvard Munch Anxiety The Kiss painting","Edvard Munch The Scream Vampire"],
  "act":["The Scream: the world bends","Faces, hands and dark longing","Love and isolation","A moving sea of psychic colour","Return to the unforgettable cry"],
  "track":"calmant"},
 "goya":{
  "name":"Francisco Goya","duration":123,
  "hero":"Saturn Devouring His Son.jpg",
  "featured":["Saturno devorando a sus hijos por Goya.jpg"],
  "key":["saturn","third of may","3rd may","sleep of reason","black paintings","witches","dog","disasters","naked maja","clothed maja","writings","portrait"],
  "find":["Francisco Goya black paintings witches","Francisco de Goya Saturn 3 May paintings","Francisco Goya paintings Museo del Prado"],
  "act":["A terrifying gaze","Nightmare, witchcraft and fantasy","Faces of power, ritual and fear","Paintings and the cost of violence","Blackness opens onto a human face"],
  "track":"darkest_child"},
 "arcimboldo":{
  "name":"Giuseppe Arcimboldo","duration":101,
  "hero":"Giuseppe Arcimboldo-The Summer-Kunsthistorisches Museum.jpg",
  "featured":["Arcimboldo Spring 1563.jpg","Arcimboldo Autumn 1572 (private).jpg","Arcimboldo - Les saisons - L'hiver.jpg"],
  "key":["vertumnus","summer","spring","autumn","winter","librarian","water","fire","earth","air","four elements","gardener","vegetables","fruit","flora"],
  "find":["Giuseppe Arcimboldo Vertumnus vegetable fruit portrait","Giuseppe Arcimboldo four elements paintings","Giuseppe Arcimboldo The Seasons series","Arcimboldo librarian flower head"],
  "act":["A human face made of fruit","Seasons become living portraits","Vegetables, flowers, impossible figures","Elements and visual jokes","The first strange face returns"],
  "track":"evening_fall_piano"},
 "leonardo":{
  "name":"Leonardo da Vinci","duration":128,
  "hero":"Leonardo da Vinci - Mona Lisa.jpg",
  "featured":["Mona Lisa.jpg"],
  "key":["mona lisa","last supper","vitruvian","lady with an ermine","saint anne","john the baptist","virgin of the rocks","annunciation","ginevra","portrait","madonna"],
  "find":["Leonardo da Vinci paintings Mona Lisa Last Supper","Leonardo da Vinci Lady with an Ermine Annunciation","Leonardo da Vinci paintings portrait public domain"],
  "act":["A smile opens the mystery","Faces and transparent shadows","Hands and sacred compositions","The mind of an inventor and painter","Return to the enigmatic smile"],
  "track":"dreams_become_real"},
 "hiroshige":{
  "name":"Utagawa Hiroshige","duration":116,
  "hero":"Hiroshige, Sudden shower over Shin-Ōhashi bridge and Atake, 1857.jpg",
  "featured":["Hiroshige, Sudden shower over Shin-Ohashi bridge and Atake, 1857 expanded.jpg"],
  "key":["sudden shower","rain","bridge","one hundred famous views","edo","snow","night","river","plum garden","sea","fuji","tokaido","coast","mountain"],
  "find":["Utagawa Hiroshige One Hundred Famous Views Edo woodblock","Utagawa Hiroshige rain snow bridge prints","Hiroshige Edo Tokaido ukiyo-e"],
  "act":["The rain comes suddenly","Bridges, footsteps, changing skies","The cities and rivers of Edo","Mountains, horizons and snow","Return to the storm's diagonal lines"],
  "track":"music_for_manatees"},
})
v6.SOUND["music_for_manatees"]={
 "title":"Music for Manatees","author":"Kevin MacLeod",
 "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400009",
 "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Music%20for%20Manatees.mp3"],
 "license":"CC BY 4.0","license_url":v6.LICENSE_URL,"expected_seconds":1056,"instrumental":True
}

# Old script is kept INTACT: add artist-name filter for the new five through this wrapper.
ALLOW={
 "munch":["munch"],"goya":["goya","lucientes"],"arcimboldo":["arcimboldo"],
 "leonardo":["leonardo","vinci"],"hiroshige":["hiroshige"]
}
ICONIC={
 "munch":["the scream"],"goya":["saturn devouring","saturno devorando"],
 "arcimboldo":["giuseppe arcimboldo"],"leonardo":["mona lisa"],
 "hiroshige":["sudden shower","hiroshige"]
}
def safe_filename(name,slug):
 n=name.casefold()
 if not n.endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff")):return False
 if any(w in n for w in ("installation view","museum selfie","tshirt","merch","frame of","painting reproduction in","tourist photo","street mural","statue of","portrait of the artist by","movie poster","colouring book")):return False
 return any(w in n for w in ALLOW[slug]) or any(w in n for w in ICONIC[slug])
v6.suitable_filename=safe_filename

# The new batch has a slightly lower artwork threshold for authors with few unique originals;
# 9 genuine images in under two minutes are better than repeating the same image 20 times.
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--artist",choices=sorted(v6.P),required=True)
 arg=p.parse_args()
 render_artist(arg.artist)
