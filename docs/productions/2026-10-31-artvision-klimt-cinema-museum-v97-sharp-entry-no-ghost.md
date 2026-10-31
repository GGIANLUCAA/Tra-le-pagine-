# ArtVision Klimt Cinema Museum V97 — nitidezza ingresso senza salto (31/10/2026)

## Nuovo difetto V96, misurato su veri fotogrammi

La V96 ha eliminato il ghosting della dissolvenza Museum V92 ma ha lasciato un **grave salto di nitidezza a 11,30 s**. Nel filmato reale V96 la varianza del Laplaciano sulla ROI centrale (x=100:620, y=240:1040) passa da **17,029** al fotogramma 225 (11,25 s) a **542,073** al fotogramma 226 (11,30 s): **31,832×** in un solo frame. Il quadro appariva sfocato e diventava improvvisamente nitido. Il confronto campionato V96/V97 è nel container `/mnt/data/ARTVISION_KLIMT_V97/CONFRONTO_V96_V97_NITIDEZZA_INGRESSO.jpg`, non dichiarato presente nella Libreria.

## Correzione V97 — stesso slot, NON quinto video

Nuovo file reale **`Klimt_Cinema_Museum_V97_SHARP_ENTRY_NO_GHOST_REVIEW.mp4`**, **34.582.402 byte**, SHA256 **`eb66c57e7db9ff5e88a884c9838bec067b68ced04efdd8cbe4c58b240b5500df`**.

- **52 s, 720×1280, 20 fps, 1040 fotogrammi, H264/AAC, FFmpeg full decode PASS**.
- Sostituiti **solo i 16 fotogrammi 210–225 (10,50–11,25 s)**. La camera attraversa la ricostruzione museale con un movimento geometrico già V96, ma il dettaglio nitido proviene **dal fotogramma reale del dipinto già incluso nella stessa V96**; compositing con maschera spaziale sfumata, niente immagini o persone generate e nessuna nuova dissolvenza lunga fra due visi.
- Nel MP4 V97 *decodificato*, varianza Laplaciano **315,243 a 11,25 s** e **382,355 a 11,30 s**, rapporto **1,213×**, rispetto al 31,832× V96. Riduzione del salto di nitidezza: **~96%** in termini di rapporto eccedente 1.
- **AAC demux ADTS SHA256 `5d68dcdf5cd3ad27e3ecd1bf08ec3f04b3e6929227458bfab18e927820804e9d`** bit-identico a V96 e V92; nessuna nuova voce, musica, API o spesa.
- Fotogrammi fuori intervallo ricodificati tecnicamente, non cambiati intenzionalmente: SSIM grayscale su 10 campioni tra 0,5 e 50s **0,977974–0,993715** rispetto alla V96, compreso il ritorno Museum a 41,5 s.
- Master V92, revisione V96, ZIP Klimt 4×1 V92, Socrate V95 e gli altri slot **inalterati**.

## Backup effettivo e verifica di ritorno

- Libreria privata: `/ArtVision/Klimt/V97_CINEMA_MUSEUM_SHARP_ENTRY/Klimt_Cinema_Museum_V97_SHARP_ENTRY_NO_GHOST_REVIEW.mp4`.
- Upload eseguito, **download di ritorno vero** dal file_id `file_00000000079881f88092ca3b55908d87` di **34.582.402 byte**, SHA256 **identico `eb66c57e...`** e **FFmpeg full decode PASS sul file riscaricato**.
- Nella stessa cartella `QA_V97.json`, `LEGGIMI_V97.md`, `revise_klimt_museum_v97_entry_sharpness.py` (tutti upload riusciti).
- **Non è stato creato un nuovo ZIP**, nessun re-render di V96, V92, V95, V94, V93.

## Limiti, qualità e prossimo passo

La V97 è candidata alla valutazione estetica umana: il miglioramento è osservato sui frame e misurato, ma non sostituisce una visione a velocità naturale. Il movimento 10,5–11,3 s è ancora rapido; il colore può variare leggermente tra texture dei fotogrammi già compressi. **V25 Gold = 0**.

La sala e la cornice sono **ricostruzioni digitali artistiche**, non riprese reali del Belvedere. Opera PD Gustav Klimt, *The Kiss*: https://commons.wikimedia.org/wiki/File:Klimt_-_The_Kiss.jpg . La musica esistente resta attribuita nel pacchetto V92.

**Import R2/player Android non verificati**. L'azione Video Library Studio richiede `fileParams` realmente selezionato dal proprietario; non inventare input. Socrate Cinema Museum V61 staged resta la priorità import quando disponibile. Se bloccato, solo QA/correzioni di difetti nuovi e provati. Nessuna sesta opera, social, addebito API, Gold automatico o nuova automazione.
