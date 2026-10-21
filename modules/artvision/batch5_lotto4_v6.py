#!/usr/bin/env python3
"""Quarto lotto ArtVision V6: cinque nuovi artisti, motore precedente invariato."""
from pathlib import Path
import argparse
import batch5_cinema_v6 as studio

studio.ROOT=Path("output/artvision-lotto4-v6")
studio.P.clear()
studio.P.update({
 "frida":{
  "name":"Frida Kahlo","duration":107,"hero":"Frida Kahlo (self portrait).jpg",
  "key":["self portrait","self-portrait","two fridas","broken column","thorn necklace","monkey","roots","wounded deer","diego","frida"],
  "find":["Frida Kahlo paintings self portrait","Frida Kahlo self portraits original paintings","Frida Kahlo paintings art museum"],
  "act":["An unforgettable gaze","A face with symbols","Nature, roots and memory","Portraits of pain and resilience","Return to her gaze"],"track":"calmant"},
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
 "magritte":{
  "name":"René Magritte","duration":112,"hero":"The Son of Man by Rene Magritte.jpg",
  "key":["son of man","treachery of images","golconda","lovers","human condition","empire of light","false mirror","apple","pipe","surreal"],
  "find":["Rene Magritte paintings surrealism","Magritte The Son of Man Golconda paintings","Rene Magritte surrealist artwork museum"],
  "act":["A face hidden by an apple","The impossible becomes ordinary","Clouds, windows and silhouettes","Everyday objects become mysteries","The concealed face returns"],"track":"darkest_child"},
 "hokusai2":{
  "name":"Katsushika Hokusai","duration":103,"hero":"The Great Wave off Kanagawa.jpg",
  "key":["great wave","red fuji","fine wind","mount fuji","thirty-six views","waterfall","bridge","wave","sea","suruga"],
  "find":["Hokusai Great Wave Japanese woodblock","Katsushika Hokusai Thirty Six Views Mount Fuji","Hokusai Japanese print museum"],
  "act":["The wave rises","Mount Fuji beyond the sea","Bridges and rivers","A world of shifting horizons","The wave returns"],"track":"music_for_manatees"}
})
studio.SOUND["music_for_manatees"]={
 "title":"Music for Manatees","author":"Kevin MacLeod",
 "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400009",
 "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Music%20for%20Manatees.mp3"],
 "license":"CC BY 4.0","license_url":studio.LICENSE_URL,"expected_seconds":1056,"instrumental":True}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--artist",required=True,choices=sorted(studio.P))
 studio.make(p.parse_args().artist)
