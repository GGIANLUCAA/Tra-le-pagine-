#!/usr/bin/env python3
"""ArtVision Cinema V6: cinque film dark poetic con singoli brani verificati."""
from pathlib import Path
import argparse
import batch5_cinema_v6 as studio

studio.ROOT=Path("output/artvision-lotto6-inquietudine")
studio.P.clear()
studio.P.update({
"bosch_dark":{
 "name":"Hieronymus Bosch","duration":132,
 "hero":"The Garden of Earthly Delights by Hieronymus Bosch.jpg",
 "key":["garden of earthly delights","temptation","last judgement","haywain","hell","ship of fools","conjurer","st anthony","hermit","cross"],
 "find":["Hieronymus Bosch garden earthly delights","Hieronymus Bosch Temptation Saint Anthony","Hieronymus Bosch Last Judgment paintings","Hieronymus Bosch Ship of Fools","Hieronymus Bosch triptych painting"],
 "act":["A creature from another world","Human figures dissolve into riddles","Creatures and strange machines","The burning darkness","Return to the impossible garden"],
 "track":"darkest_child"},
"gericault":{
 "name":"Théodore Géricault","duration":125,
 "hero":"Théodore Géricault - The Raft of the Medusa.jpg",
 "key":["raft of the medusa","radeau de la méduse","medusa","shipwreck","storm","horse","portrait","insane","wounded","cavalry"],
 "find":["Theodore Gericault paintings raft of the medusa","Théodore Géricault paintings museum","Gericault portraits horse paintings","Gericault sea storm artworks"],
 "act":["The first desperate gesture","Human figures adrift","Between despair and hope","An ocean of dramatic light","The raft comes into full view"],
 "track":"dreams_become_real"},
"fuseli":{
 "name":"Henry Fuseli","duration":107,
 "hero":"Henry Fuseli - The Nightmare.jpg",
 "key":["nightmare","incubus","witch","ghost","dream","lady","apparition","horse","titania","shakespeare","night"],
 "find":["Henry Fuseli The Nightmare painting","Henry Fuseli ghost gothic paintings","Johann Heinrich Füssli paintings","Henry Fuseli Shakespeare paintings"],
 "act":["The first face in the dark","A dream becomes a nightmare","Shadows and theatrical figures","The mysteries of sleep","Return to the impossible visitor"],
 "track":"night_on_the_docks_piano"},
"bocklin":{
 "name":"Arnold Böcklin","duration":118,
 "hero":"Arnold Böcklin - Die Toteninsel III (1883).jpg",
 "key":["isle of the dead","island of the dead","toteninsel","isle of life","island of life","centaur","plague","sea","nymph","forest"],
 "find":["Arnold Böcklin Isle of the Dead painting","Arnold Bocklin painting mysterious island","Arnold Böcklin paintings museum","Arnold Böcklin mythological painting"],
 "act":["An island beyond time","Boats, dark water and cypresses","Ancient figures and shadow","The mystery deepens","The island waits in silence"],
 "track":"evening_fall_piano"},
"redon":{
 "name":"Odilon Redon","duration":112,
 "hero":"Odilon Redon - The Cyclops.jpg",
 "key":["cyclops","eye","spider","balloon","smiling","head","dream","mask","flower","butterfly","black","strange"],
 "find":["Odilon Redon The Cyclops painting","Odilon Redon strange charcoal drawings","Odilon Redon surreal creatures","Odilon Redon paintings flower dreams"],
 "act":["An enormous eye appears","Floating faces and impossible beings","A universe drawn from dreams","The strange becomes beautiful","The eye returns"],
 "track":"calmant"}
})
studio.SOUND["night_on_the_docks_piano"]=studio.SOUND["night_on_the_docks_piano"]
ALIASES={
 "bosch_dark":["bosch"],
 "gericault":["gericault","géricault","géricault","gé́ricault"],
 "fuseli":["fuseli","füssli","fussli"],
 "bocklin":["böcklin","bocklin","boecklin"],
 "redon":["redon"]
}
def filename_ok(name,slug):
 n=name.casefold()
 if not n.endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff")): return False
 if any(k in n for k in ("museum selfie","artwork on wall","poster for exhibition","tshirt","merch","book cover","photograph of artist")):return False
 return any(k in n for k in ALIASES[slug])
studio.suitable_filename=filename_ok
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--artist",required=True,choices=sorted(studio.P))
 studio.make(p.parse_args().artist)
