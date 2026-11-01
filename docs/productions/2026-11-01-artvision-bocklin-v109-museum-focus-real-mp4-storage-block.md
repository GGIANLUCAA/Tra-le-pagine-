# ArtVision Böcklin V109 — correzione REALE inquadratura intero dipinto nel Critico Museum

**1 novembre 2026 · Revisione locale dello stesso slot, non Gold V25 · backup MP4 persistente BLOCCATO per quota Libreria.**

## Nuovo difetto V108 corretto realmente
L'analisi V108 aveva documentato che il Critico Museum V106 mostrava solo un crop centrale dei cipressi durante i capitoli **2 e 8**, mentre il copione prescriveva **intero dipinto**. Le altre varianti sono state lasciate intatte. Non sono stati ripetuti V105, V106, Gacrux o ZIP V107.

Sorgenti esatte recuperate **dal ZIP V107 già presente** in Library, non da un nuovo servizio:
- Standard V102 `01_Critico_Standard.mp4` SHA `096926e6ffb0de921fca72726deb4a136227150d1d1a224ccd42e329ee903777`.
- Museum V106 `02_Critico_Museum_V106_CANDIDATO.mp4` SHA `c1c54dba4f0198df3a8f82e11513378bccf2831647dca01741163250c857a263`.
- ZIP V107 verificato in input: 46.200.145 byte, SHA `e864f4803f5094b4a926c687921a0e64a2f2af24fca8087c1bb2be27cd812dc5`.

### Revisione concreta non distruttiva
Il nuovo `BOECKLIN_CRITICO_MUSEUM_V109_INTERO_QUADRO_REVIEW.mp4` usa esclusivamente la pittura originale già presente nel film Standard: il rettangolo del dipinto **704×375 pixel** dal frame Standard V102 a 24s, senza generazione AI, immagini esterne o fonti diverse. Tramite SIFT/RANSAC (registrazione 27/134 e 80/127 inlier ai confini) riproduce la camera già esistente e crea un **pull-back geometrico** fino al quadro intero; non usa crossfade/doppie esposizioni. Intervalli modificati 17,0–28,15s e 79,1–90,8s (459 frame); fermo quadro intero leggibile 20,0–25,8s e 82,1–88,3s, micro-movimento <1%. Altri frame rimangono gli stessi editorialmente (ricodifica H264, non byte-identici). **Nota limite:** la pittura ricavata dallo Standard è 704×375, quindi è meno nitida dell'originale ad alta risoluzione; questa revisione è candidata, non un miglioramento Gold automatico.

### Nuovo file fisico verificato
- 16.596.092 byte; SHA256 `07944553bf1f1547acc34f54185690f1f0c28c20f12cdc888eb24c8b6854a189`.
- 110,65 secondi; 2213 frame; 720×1280, 20 fps, H264/AAC; **FFmpeg full decode PASS**.
- Audio AAC demux ADTS **identico byte-per-byte** al Museum V106 e Standard V102, SHA `3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e`; zero TTS/API.
- Scansione V57 di **tutti** i frame: picco MAD grayscale 180×320 **31,477/255**, 0 frame sopra 35; transizioni V109 ai confini misurate 4,776 / 4,804 / 4,935 / 4,291, tutte sotto 35.
- I frame campione a 24s e 85s mostrano davvero l'intero quadro, rispetto al crop cipressi V106; confronto visivo effettuato su file reali. MAD medio vs Standard intero quadro a 24s **3,42/255**, a 85s **3,64/255** (ricodifica).
- Renderer offline riproducibile su main: `src/artvision_bocklin_v109_whole_painting_focus.py`.
- QA `QA_V109.json` e renderer sono presenti nella Libreria `/ArtVision/Bocklin/V109_CRITICO_MUSEUM_FOCUS_INTERO_QUADRO/`.

### Blocco nuovo e concreto della persistenza
**Upload del MP4 in Library FALLITO** con `library_storage_limit_exceeded`: quota Libreria esaurita. Non cancellare automaticamente altri master o ZIP. I due JPG di confronto non sono stati caricati: errore `403 Library LPE indexing requires a trusted producer`. Script e JSON di QA sì, caricati. **Non dichiarare SHA readback del nuovo MP4**, né backup persistente, né playback R2/Android. File MP4 creato e verificato nel container di questa esecuzione, link sandbox potenzialmente effimero. La priorità è liberare quota tramite decisione del proprietario oppure usare una destinazione esplicitamente autorizzata, poi fare upload+readback SHA. Nessun tentativo di import senza `fileParams` autentico.

**Stato:** V109 **candidato locale** con QA tecnica PASS; V106 resta selezione archiviata V107; Gold V25=0, ascolto umano completo e verifica parola-scena integrale pending, sito/Android non verificato. Nessuna settima opera, nessun social, nessuna spesa.
