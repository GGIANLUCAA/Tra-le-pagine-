# ArtVision Klimt Cinema Museum V96 — ingresso/uscita senza doppia esposizione (31/10/2026)

## Difetto nuovo, verificato su V92

Ispezione di frame reali dell'MP4 `Klimt_Cinema_Museum_V92_REVIEW.mp4` (SHA256 `abc53905dda19f66e3bed9bed4bfc96e7627c583b52ca976dbff3dc70131cd10`) mostra un difetto visivo concreto **non ancora corretto**: a **10,75–11,25 s** la dissolvenza lunga fra sala/cornice e primo piano produce due immagini trasparenti sovrapposte, con barre nere che attraversano capelli/volto e parte bassa del quadro. A **41,5–42,0 s** un'altra dissolvenza fra dettagli e sala produce doppia esposizione e bordi orizzontali fantasma. Il difetto è coerente con il renderer V92: `cv2.addWeighted(old,1-u,new,u,0)` da 10,5 a 11,3 s e l'inverso da 41,3 a 42,0 s. I fotogrammi V92 e V96 sono stati ispezionati a intervalli di 0,1–0,25 s.

## Revisione fisica non distruttiva

Nuovo MP4 reale: **`Klimt_Cinema_Museum_V96_CLEAN_ENTRY_EXIT_REVIEW.mp4`**.

- **36.373.510 byte**, SHA256 **`ef4c96d6d1882e3288f4105d76983e871f63290bb25d3af66fc7426019237522`**.
- **52,0 s, 720×1280, 20 fps, 1040 frame, H.264 CRF16 / AAC**. FFmpeg `-xerror` full decode PASS.
- AAC estratto ADTS SHA256 **`5d68dcdf5cd3ad27e3ecd1bf08ec3f04b3e6929227458bfab18e927820804e9d`**, **bit-identico** al V92. Nessuna nuova musica, TTS, Vidu o chiamata AI.
- **10,5–11,3 s**: sostituita dissolvenza con zoom in progressivo e allineato geometricamente fra frame del Museum e frame pulito del dipinto. La cornice viene oltrepassata e scompare; non resta un volto doppio.
- **41,3–42,1 s**: zoom out allineato con ripresa museale autentica **del video digitale già prodotto**, senza sovrapposizione prolungata.
- Nessun altro capitolo modificato intenzionalmente; ricodifica tecnica di tutto il video, perciò i bit H.264 fuori dalle transizioni non sono identici. SSIM grayscale su 11 frame fuori dalle due finestre: **0,96858–0,99378** rispetto al V92, differenze compatibili con ricodifica CRF16. Nessun taglio audio o durata.
- L'opera è il PD di Gustav Klimt *The Kiss*, https://commons.wikimedia.org/wiki/File:Klimt_-_The_Kiss.jpg. Sala/cornice sono **ricostruzioni digitali artistiche**, NON documentazione Belvedere. Musica originale Kevin MacLeod, *Dreams Become Real*, CC BY4, con attribuzione nel pacchetto V92.

## Archivio verificato

- Upload MP4 in **`/ArtVision/Klimt/V96_CINEMA_MUSEUM_ENTRY_EXIT/Klimt_Cinema_Museum_V96_CLEAN_ENTRY_EXIT_REVIEW.mp4`**.
- **Download di ritorno fisico** dal file_id `file_0000000030b881f68438048208120dcf`, **36.373.510 byte, SHA identico** all'MP4 locale, **FFmpeg full decode sul file riscaricato PASS**.
- Nella stessa cartella `QA_V96.json`, `LEGGIMI_V96.md` e `revise_klimt_museum_v96.py`. Preview JPG di ingresso/uscita nel container `/mnt/data/ARTVISION_KLIMT_V96/QA_ENTRY_V96.jpg`, `QA_EXIT_V96.jpg`; **NON dichiarati caricati nella Libreria**.
- Master V92, Critico V91/V91S, Cinema Standard V92 e pacchetto 4×1 Klimt V92 **INALTERATI**. Questa è una revisione dello **stesso slot Cinema Museum**, non quinto video. **Non ricreare ZIP 4×1**, non rifare V95 Socrate.

## Limiti e prossime priorità

- **QA visiva campionata**, non visione integrale umana; la revisione potrebbe mostrare un piccolo cambio di nitidezza attorno a 11,3 s perché si passa da zoom di un frame del museo al dettaglio originale già compresso nel V92. Richiede valutazione del proprietario. **V25 Gold 0**.
- **R2/site/Android playback NON verificato**; import Video Library Studio richiede `fileParams` selezionato genuinamente dal proprietario, non inventare né dichiarare import completato. V61 Socrate staged rimane prima priorità quando selezione possibile.
- Nessuna nuova opera, social, acquisto, costo API, automazione o pacchetto ripetitivo. Evitare altri render se non emerge un difetto specifico osservato.

