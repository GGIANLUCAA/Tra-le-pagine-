# ArtVision Böcklin — Critico Museum V106, revisione micro-movimento
31/10/2026 · Candidato **REVIEW**, non V25 Gold.

Opera: Arnold Böcklin, *Die Toteninsel*, terza versione 1883, NG 2/80, 80×150 cm.

## Difetto provato, V105
L'analisi di 2213 frame (720×1280, 20 fps) ha identificato 9 intervalli di immobilità video (soglia MAD grayscale consecutivo su 180×320, <0,16) di durata 5,4–12,0 s, all'interno della sezione esplicativa, senza includere l'ingresso/uscita Museum. La porzione dei frame con MAD <0,16 tra 5 e 102,5 s era **68,51%**.

## Modifica concreta V106
Applicazione offline di minimi movimenti geometrici (scala massima circa 3,7%, spostamenti massimi 5px orizzontali / 6px verticali) con inviluppo smooth a estremi identici, soltanto nei 9 tratti statici. Nessun cambio di quadro, inquadratura semantica o montaggio; nessuna nuova AI, sintesi vocale, TTS, crediti video, servizi o pubblicazione. **Il nuovo movimento non è movimento interno al dipinto**: è movimento virtuale della videocamera sulla riproduzione originale.

- V105 input 14.442.272 byte SHA256 `a90df875f26532137d1fd0e415bb3795be4f68f1c3ab9d854edb52ba087c662c`.
- V106 output **18.673.966 byte**, SHA256 `c1c54dba4f0198df3a8f82e11513378bccf2831647dca01741163250c857a263`.
- **110,65 s**, **2213 frame**, **720×1280**, H.264/AAC; FFmpeg -xerror decodifica integrale PASS.
- Audio AAC demux ADTS **bit-identico** a V105/V102: SHA256 `3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e`.
- Frame con MAD <0,16 nella finestra 5–102,5 s: **68,51% → 14,31%**. È un indicatore di movimento, NON un giudizio estetico.
- Nitidezza media come varianza Laplaciano su scala 180×320 nella stessa finestra: **360,14 → 354,76 (−1,49%)**; controllo numerico non sostitutivo della visione.
- MAD di passaggio 5,00s **1,68 → 1,58**, 103,65s **0,44 → 0,37**. I raccordi V105 restano invariati editorialmente, ma il video è ricodificato.
- Intro Museum prima di 5,05 s e outro dopo 102,50 s non subiscono nuove trasformazioni geometriche.
- 9 intervalli modificati, 1.342 frame di video passati attraverso la trasformazione (inclusi estremi pixel-identici), da 5,05–17,05; 20,90–28,30; 32,25–39,75; 43,50–50,60; 54,25–61,25; 64,70–70,75; 73,75–79,15; 83,45–90,95; 95,35–102,50 s.

## Archiviazione e stato
Tutti i master e altri 3 slot Böcklin restano intatti; nessuna settima opera. **V106 candidata in QA tecnica, non sostituisce V105 né V102 selezionato**, e non entra nel pacchetto V103 già completo. 2 Cinema approvati positivamente in passato, non Gold; tutte le varianti Gold V25=0. Il QA numerico non certifica la sincronizzazione semantica voce/scene, ascolto integrale, qualità estetica artistica, né il player Cloudflare R2/Android. Queste verifiche restano pendenti.

File: MP4 V106, `BOECKLIN_V106_QA.json`, confronto a coppie V105/V106 e renderer Python ripetibile con nessuna dipendenza da servizi esterni. Nessun workflow è stato avviato.
## Verifica fisica archivio e readback (eseguita)
Caricati nella Libreria privata `/ArtVision/Bocklin/V106_CRITICO_MUSEUM_MICRO_MOTION_REVIEW/` il MP4 V106, il file QA JSON, il confronto V105/V106, il renderer e questo README. **Il MP4 è stato poi materializzato nuovamente dalla Libreria** in un file separato: `18.673.966` byte e SHA256 `c1c54dba4f0198df3a8f82e11513378bccf2831647dca01741163250c857a263`, identico a quello generato. `ffmpeg -v error -xerror -i FILE -f null -` sul **file riscaricato**: PASS. Il readback non certifica il playback Android/R2: ancora PENDING. Codice ripetibile `src/artvision_bocklin_v106_micro_motion.py` su main. Nessuna modifica alla coda Gold né ai master storici.
