# ArtVision Klimt Cinema Museum — QA nuova sfocatura uscita V97 (31/10/2026)

## Esito reale, non nuova versione video

L'MP4 V97 **esistente** `Klimt_Cinema_Museum_V97_SHARP_ENTRY_NO_GHOST_REVIEW.mp4` è stato letto **dalla Libreria privata** `/ArtVision/Klimt/V97_CINEMA_MUSEUM_SHARP_ENTRY/`, file_id `file_00000000079881f88092ca3b55908d87`, materializzato e verificato localmente:
- **34.582.402 byte**, SHA256 **`eb66c57e7db9ff5e88a884c9838bec067b68ced04efdd8cbe4c58b240b5500df`** (match del file materializzato).
- 52 s, 20 fps, 1040 frame; lettura completa OpenCV **1040/1040** e FFmpeg `-xerror -f null -` **PASS**.
- QA campionata di ingresso 9,8–11,6s e uscita 40,9–42,5s con ROI centrale x=100:620, y=240:1040. Fotogrammi visualizzati in contact sheet nel container locale; **non dichiarare queste immagini salvate in Libreria**.

## Difetto ulteriore provato: uscita 41,30–41,45s

La correzione V97 dell'**ingresso** rimane valida: la varianza del Laplaciano tra **11,25 e 11,30s** è **315,243 → 382,355**, rapporto **1,213×** (V96: **31,832×**).

Nell'**uscita Museum**, tuttavia, lo stesso video V97 perde molto dettaglio in **0,15 secondi**, quando il quadro inizia a rimpicciolire:
- **41,30s:** Laplaciano **1724,862**, Tenengrad **14048,544**.
- **41,45s:** Laplaciano **104,559**, Tenengrad **5399,774**.
- **Crollo Laplaciano: 16,497×**; Tenengrad ~**2,60×**. I fotogrammi campionati mostrano un passaggio improvviso da texture nitida a texture morbida.
- Il problema è **preesistente anche in V96**: Laplaciano **1988,3 → 92,6**, rapporto **21,477×** sugli stessi tempi. V97 ha migliorato l'ingresso, ma non ha corretto questo difetto residuo di uscita. Non attribuirlo alla modifica V97.

**Nota metodologica:** l'intensità del dettaglio varia anche con lo zoom e il contenuto; queste misure, unite al confronto visivo dei fotogrammi, indicano un difetto concreto da correggere/valutare, **non certificano** da sole la qualità artistica. Visione integrale a velocità naturale e giudizio del proprietario **pendenti**.

## Guard di regressione riproducibile

Nuovo script **`src/klimt_museum_transition_qa_v98.py`**, diagnostico e *read-only*, per il file reale:
```bash
python src/klimt_museum_transition_qa_v98.py \
  --video Klimt_Cinema_Museum_V97_SHARP_ENTRY_NO_GHOST_REVIEW.mp4 \
  --expected-sha256 eb66c57e7db9ff5e88a884c9838bec067b68ced04efdd8cbe4c58b240b5500df
```
Richiede `cv2` e `numpy`; controlla frame/timecode e SHA, emette JSON; exit code **2** quando trova una transizione sospetta oltre 8×. Eseguito realmente su **V97** (ingresso PASS, uscita WARNING 16,497×) e **V96** (ingresso WARNING 31,832×, uscita WARNING 21,477×). La soglia è solo per questa opera, non un gate universale; lo script **non** modifica alcun MP4, coda, preset o approvazione.

## Prossima correzione, soltanto se valida su fotogrammi autentici

Valutare una revisione separata **dello stesso slot** dell'uscita 41,30–42,10s, conservando sala, prospettiva, musica AAC e tutti i master. Non usare una semplice maschera di sharpening che inventi texture o introduca aloni; serve una fonte autentica del dipinto sufficientemente dettagliata, geometricamente allineata alla camera, con confronto A/B e assenza di ghosting. **Nessun V98 MP4 è stato renderizzato o dichiarato pronto in questa QA**.

Socrate Cinema Museum V61 resta il **primo import R2** solo dopo selezione genuina `fileParams` del proprietario; R2 e playback Android **non verificati**. V25 Gold **0**, sala/cornice Klimt **ricostruzioni digitali**, non Belvedere reale. V97, V96, V92, Socrate V95, ZIP 4×1, coda e master **inalterati**. Nessuna nuova opera, pubblicazione, task, API, spesa o video duplicato.
