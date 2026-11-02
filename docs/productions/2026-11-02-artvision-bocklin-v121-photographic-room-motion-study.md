# ArtVision Böcklin V121 — studio fisico di sala fotografica, NON Museum approvato

2 novembre 2026. **Nuovo provino video di 8 secondi realmente renderizzato e decodificato**, non revisione dei quattro slot e non nuovo master.

## Motivazione e materiale realmente usato
La QA V120 ha dimostrato sul V106 Critico Museum e V101 Cinema Museum il fondale grigio privo di sala. Il V113 Critico Museum locale, verificato visivamente in questa esecuzione, sostituisce quel vuoto con pannelli, soffitto e pavimento digitali ma rimane una scenografia schematica, non una sala fotografica credibile secondo V118/V119. Non sostituire automaticamente V106/V113 con un semplice sfondo fotografico.

Per una prova di materiale realistico è stata recuperata **la vera fotografia** PH02/GAL02 già verificata nel pacchetto GitHub Actions V120 (run 41395451028, artifact 13119426005): *Museum Barberini Innenraum leer*, Daniel Naber, 2016, **CC BY 4.0**, [pagina e licenza](https://commons.wikimedia.org/wiki/File:Museum_Barberini_Innenraum_leer.jpg), SHA256 `ea95335ef66afa225351e1dd423c49d5e84aeb15574e97b965fa25c1d5b91db2`. **Non** è una sala dell'Alte Nationalgalerie di Berlino.

La fotografia mostra una vera parete, parquet, cornice architettonica, soffitto, illuminazione e prospettiva. Vi è stata composta digitalmente la fotografia della cornice/dipinto già presente nel frame del candidato Böcklin V113, preservando l'opera originale (terza versione 1883, NG 2/80, **80 × 150 cm**). L'ingombro in parete è un'**ipotesi visiva**, non una scala metrica verificata da rilievo della sala.

## Risultato fisico, verificato
- File locale: `/mnt/data/bocklin_qa_v108/BOECKLIN_PH02_PHOTO_ROOM_MOTION_STUDY_V121_8S_REVIEW.mp4`.
- **1.263.737 byte**, SHA256 **`456eb95e0d7a768b0b8d95240d9d079d6a90ac3af6cb03e38e309b5d5359ad0c`**.
- 8 s, H264 720×1280, 20 fps, 160 fotogrammi; FFmpeg `-xerror` decodifica completa **PASS**.
- Prova muta di ingresso/ritorno su un'immagine fotografica compositata. **Non** è una delle quattro varianti complete, non contiene la voce Gacrux, non sostituisce V113 o V106, non è pubblicabile.
- Fotogrammi locali di controllo: `/mnt/data/bocklin_qa_v108/PH02_MOTION_STUDY_V121_FRAMES.jpg` a 0, 2, 4, 6 e 7,9 s.
- Nessuna chiamata AI/TTS/Vidu, nessuna spesa, nessun social; tutti i master e i due Cinema restano intatti.

## Gate V118/V119: **NON APPROVATO**
La scena è fotograficamente più credibile dei fondali procedurali, ma il movimento deriva da crop/zoom 2D **senza vera parallasse 3D**; il piano del quadro è composto su un'altra galleria e la scala fisica non è stata calibrata con elementi misurati. È dunque **soltanto uno studio materiale e fotografico**, non una sala Museum definitiva o un preset GAL02 approvato. Non promuovere a Gold V25, non distribuire come filmato completo e non integrare automaticamente nel Critico Museum. Per una revisione effettiva serve camera spaziale coerente, scala 80×150 cm, raccordo senza ghosting al quadro, QA visiva a velocità normale e approvazione proprietario.

## Persistenza e sito
Il MP4 è fisicamente presente nella sessione locale, ma **non è stato caricato in Library**. Il primo tentativo ha restituito `container_session_expired`; dopo una nuova verifica SHA e un singolo tentativo dal percorso radice `/mnt/data/`, il server ha risposto esplicitamente **`library_storage_limit_exceeded`**. La cartella Library `/ArtVision/Bocklin/V121_PHOTO_ROOM_MOTION_STUDY_NOT_FINAL/` è stata creata, ma non contiene il video; nessun file precedente è stato cancellato. Nessun import Cloudflare R2, nessun playback Android/sito verificato. Gold V25 = **0**.

**Prossimo passo utile**: sviluppare un vero percorso di camera/proiezione della foto su superfici architettoniche o trovare un asset 3D fotografico autorizzato; non ricadere nella semplice parete digitale V112 e non ripetere i Cinema già graditi.
