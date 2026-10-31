# ArtVision Klimt Cinema Museum V98 — uscita nitida, MP4 reale e readback (31/10/2026)

## Difetto provato e intervento

La V97 aveva risolto il salto di nitidezza dell'ingresso 10,50–11,30 s, ma la transizione d'uscita 41,30–41,45 s manteneva un crollo della varianza del Laplaciano **16,497×**, documentato in `docs/productions/2026-10-31-artvision-klimt-cinema-museum-v97-exit-blur-qa.md`. La V98 corregge **solo il nuovo difetto concreto**, senza modificare master, ZIP o gli altri tre slot Klimt.

Il nuovo MP4 è **`Klimt_Cinema_Museum_V98_SHARP_EXIT_AUTHENTIC_REVIEW.mp4`**, **35.545.958 byte**, SHA256 **`e55901639f5bb524a052d1d9767bdaae9dad851c6de45deaac8a80e39a6cf2d3`**. Fonte V97 verificata SHA `eb66c57e7db9ff5e88a884c9838bec067b68ced04efdd8cbe4c58b240b5500df`.

### Metodo verificabile

- Frame originale V97 **41,30 s** del dipinto, già esistente e autentico, registrato su 75 frame 41,30–45,00 s con corrispondenze SIFT e affine RANSAC, almeno **92 inlier**; maschera spaziale feathered e uscita graduale a 45,00 s. **Nessuno sharpening sintetico, nuova AI o doppia esposizione lunga.**
- V98 codificato: **52 s, 720×1280, 20 fps, 1040 frame, H264/AAC**, FFmpeg full decode **PASS**.
- Misure **sui frame V98 decodificati**: uscita 41,30→41,45 s Laplaciano **1430,367→1143,228**, rapporto **1,251×** (V97 **16,497×**). Ingresso 11,25→11,30 s **283,130→338,393**, rapporto **1,195×**, senza regressione V97.
- Audio AAC ADTS SHA256 **`5d68dcdf5cd3ad27e3ecd1bf08ec3f04b3e6929227458bfab18e927820804e9d`**, bit-identico a V97/V96/V92.
- SSIM grayscale su 13 frame fuori dall'intervallo 41,30–45,00 s **minimo 0,982477** vs V97 (solo ricodifica tecnica). Frame 44,95→45,00 senza salto evidente nelle misure; QA artistica a velocità naturale resta da effettuare.

### Backup fisico verificato

Upload in Libreria privata **`/ArtVision/Klimt/V98_CINEMA_MUSEUM_SHARP_EXIT/`**:
- MP4 file_id **`file_00000000948881f5b8f5f7539eb6e8d0`**;
- `QA_V98.json`, `LEGGIMI_V98.md`, `revise_klimt_museum_v98_exit_detail.py`, `transforms_refined.json`.

**DOWNLOAD DI RITORNO REALE** del MP4 dalla Libreria, 35.545.958 byte, SHA256 **identico `e55901639f5bb524a052d1d9767bdaae9dad851c6de45deaac8a80e39a6cf2d3`**, FFmpeg `-xerror -f null -` **PASS sul file riscaricato**. Nessun nuovo ZIP.

### Stato e limiti

V98 è revisione **dello stesso slot Cinema Museum**, NON quinto video. V97, V96, V92, Socrate V95, ZIP 4×1 e tutti i master rimangono **inalterati**. **V25 Gold=0**; QA artistica integrale e visione del proprietario pendenti. Sala e cornice sono **ricostruzioni digitali**, non il Belvedere reale.

**Import R2/player Android non verificati**. Socrate Cinema Museum V61 resta prima priorità e richiede `fileParams` genuino selezionato dal proprietario: non inventare import o playback. Nessuna sesta opera, social, costo API, nuovo task o rigenerazione di MP4 già prodotti.
