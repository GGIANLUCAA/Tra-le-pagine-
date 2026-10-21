#!/usr/bin/env python3
"""Quarto lotto ArtVision V6: cinque nuovi artisti, motore precedente invariato."""
from pathlib import Path
import argparse
import batch5_cinema_v6 as studio

studio.ROOT=Path("output/artvision-lotto4-v6")
studio.P.clear()
studio.P.update({
 "modigliani":{
  "name":"Amedeo Modigliani","duration":107,"hero":"Amedeo Modigliani - Jeanne Hébuterne.jpg",
  "key":["jeanne","portrait","woman","red nude","reclining nude","self portrait","seated","elongated","blue eyes"],
  "find":["Amedeo Modigliani portraits paintings","Amedeo Modigliani Jeanne Hebuterne art","Amedeo Modigliani nude painting"],
  "act":["An elongated gaze","Faces as sculpted silhouettes","Blue eyes and warm tones","Women and quiet interiors","A final portrait"],"track":"calmant"},
 "durer":{
  "name":"Albrecht Dürer","duration":118,"hero":"Albrecht Dürer - Self-Portrait at 28 - Google Art Project.jpg",
  "key":["self portrait","hare","rhinoceros","praying hands","adam and eve","melencolia","four apostles","watercolour","young hare","portrait"],
  "find":["Albrecht Dürer paintings self portrait","Albrecht Dürer young hare praying hands","Albrecht Dürer artworks museum"],
  "act":["The face of the Renaissance","Hands and impossible precision","Animals drawn like living beings","Geometry, light and allegory","The artist's eyes return"],"track":"evening_fall_piano"},
 "turner":{
  "name":"J. M. W. Turner","duration":126,"hero":"Turner - The Fighting Temeraire.jpg",
  "key":["fighting temeraire","rain steam speed","slave ship","snow storm","sunset","burning","venice","sea","storm","ship","light"],
  "find":["JMW Turner painting sea storm","Joseph Mallord William Turner landscape painting","J M W Turner Fighting Temeraire painting"],
  "act":["A ship vanishes into light","Sea and storm","The elements dissolve","Golden sunsets and distant cities","Light takes the frame"],"track":"dreams_become_real"},
 "chagall":{
  "name":"Marc Chagall","duration":112,"hero":"Marc Chagall - I and the Village.jpg",
  "key":["village","lovers","flying","dream","birthday","blue","fiddler","paris","circus","window"],
  "find":["Marc Chagall I and the Village painting","Marc Chagall early paintings artwork","Marc Chagall lovers dream painting"],
  "act":["A village becomes a dream","Flying figures and memories","Animals, lovers and colour","An impossible world","Return to the village"],"track":"darkest_child"},
 "kandinsky":{
  "name":"Wassily Kandinsky","duration":103,"hero":"Wassily Kandinsky, 1913 - Composition VII.jpg",
  "key":["composition","improvisation","yellow red blue","circles","abstract","blue rider","landscape","colour","color"],
  "find":["Wassily Kandinsky Composition VII paintings","Wassily Kandinsky abstract paintings museum","Wassily Kandinsky circles painting"],
  "act":["Colour explodes","Lines like instruments","Shapes in motion","An abstract universe","The composition returns"],"track":"music_for_manatees"}

})
studio.SOUND["music_for_manatees"]={
 "title":"Music for Manatees","author":"Kevin MacLeod",
 "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400009",
 "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Music%20for%20Manatees.mp3"],
 "license":"CC BY 4.0","license_url":studio.LICENSE_URL,"expected_seconds":1056,"instrumental":True}
# Adapt the old engine's artist whitelist without modifying its approved source.
ALLOW={
 "modigliani":["modigliani"],"durer":["dürer","durer","duerer"],
 "turner":["turner"],"chagall":["chagall"],"kandinsky":["kandinsky"]
}
def safe_filename(name,slug):
 n=name.casefold()
 if not n.endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff")):return False
 if any(v in n for v in ("museum selfie","tshirt","merchandise","reproduction on wall","statue of","poster for exhibition","photograph of the artist","book cover")):return False
 return any(v in n for v in ALLOW[slug])
studio.suitable_filename=safe_filename

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--artist",required=True,choices=sorted(studio.P))
 studio.make(p.parse_args().artist)
