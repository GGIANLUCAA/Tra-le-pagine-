#!/usr/bin/env python3
"""Bruegel 1559 — revised factual narration and scene-true storyboard.
Speaker must sound Italian, warm, conversational, with expressive pauses.
All pixels are original; do not auto-publish or mark as artistically approved.
"""
BEATS=[
 {"spoken":"Prova a guardare questa chiesa. I ricchi passano dall'ingresso principale. I poveri escono dalla porta laterale. Bruegel lo dipinge senza bisogno di una sola parola.",
  "frames":[("main_church",.87,.28,.33,"in"),("side_church",.69,.29,.25,"left")]},
 {"spoken":"Siamo nelle Fiandre, nel millecinquecentocinquantanove. Una piazza intera, vista dall'alto. Da una parte c'è l'osteria. Dall'altra, la chiesa. E in mezzo, una folla che sembra non fermarsi mai.",
  "frames":[("full",0,0,0,"in"),("inn",.19,.32,.40,"down"),("church_front",.82,.32,.35,"left")]},
 {"spoken":"Guarda in basso. Carnevale cavalca una botte. Al posto della lancia, uno spiedo carico di carne. Non difende un regno. Difende il piacere di mangiare.",
  "frames":[("carnival_duel",.40,.76,.34,"in"),("carnival_close",.41,.80,.22,"right")]},
 {"spoken":"Di fronte avanza la Quaresima: magra, su un carretto. La sua arma è una pala da forno con due aringhe. Il digiuno sfida l'abbondanza. Sembra una burla. Ma Bruegel non si ferma lì.",
  "frames":[("lent",.62,.79,.30,"in"),("lent_details",.62,.80,.22,"left"),("duel_paired",0,0,0,"in")]},
 {"spoken":"Davanti alla chiesa, una pellegrina indica un mendicante, riceve l'elemosina e già si rivolge a qualcun altro. È un gesto minuscolo. E cambia il senso della scena: anche la carità può diventare una rappresentazione.",
  "frames":[("church_beggars",.83,.58,.33,"in"),("pilgrim_detail",.79,.70,.25,"right")]},
 {"spoken":"Ora cerca il buffone, quasi al centro. Cammina con una torcia accesa in pieno giorno. Una fiamma inutile, sotto il sole. O forse no. In questa piazza ogni cosa è visibile. Tranne le intenzioni di chi la attraversa.",
  "frames":[("torch_town",.43,.45,.31,"in"),("torch_close",.43,.47,.21,"left"),("full_final",0,0,0,"out")]}
]
SOURCES=[
 "Kunsthistorisches Museum / Bruegel exhibition, https://bruegel.at/en/carnival-vs-lent/",
 "Web Gallery of Art, fool with torch, https://www.wga.hu/html_m/b/bruegel/pieter_e/04/05carniva.html",
 "Wikimedia Public Domain painting, https://commons.wikimedia.org/wiki/File:The_Fight_Between_Carnival_and_Lent.jpg"
]
if __name__=="__main__":
 print("\n\n".join(b["spoken"] for b in BEATS))
 print("WORDS",sum(len(b["spoken"].split()) for b in BEATS))
