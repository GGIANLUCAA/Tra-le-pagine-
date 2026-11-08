# ArtVision V220 — due NUOVI quadri, due Cinema Standard originali (8 novembre 2026)

## RISULTATO REALE, NO DUPLICATI
Per richiesta dell'utente di **nuovi video e soggetti non ripetuti**, si è lavorato in un filone separato dalla coda owner delle 10 opere selezionate. Verifica preventiva sul repository non ha restituito video precedenti per Carlos Schwabe / `Death and the Gravedigger` o Viktor Vasnetsov / `Knight at the Crossroads`.

**Sono stati creati fisicamente due MP4 autentici Cinema Standard, uno per ciascuna opera** (non due varianti dello stesso video e non Museum/4×1 completo). Durata 44,0s ciascuno, verticale 720×1280 20fps, H264/AAC, 880 fotogrammi, dieci inquadrature editoriali sul quadro originale e musica ambient sintetizzata originale, senza tracce/campioni commerciali. Titoli pubblici inglesi senza nome progetto/Standard. Nessuna generazione AI di contenuti visivi e nessuna spesa API.

### MP4 scaricabili e SHA completi

1. Carlos Schwabe — *Death and the Gravedigger* (ca. 1895–1900):
   - MP4: `ARTVISION_SCHWABE_DEATH_AND_THE_GRAVEDIGGER_CINEMA_V220.mp4`
   - **5.307.019 B**, SHA256 `5e05cb18c9d57ce2a6fd4d1985a8833a2946739c363aee204d88fe234d58a2d0`
   - Fonte reale alternativa: https://eclecticlight.co/wp-content/uploads/2020/01/schwabedeathgravedigger.jpg, **1.021×1.428 px**, SHA256 `a77622371ff9e793587e2e1ab43b5414f48c2451902eb5ee5119cc177cc2b7b2`.
   - Commons originale di riferimento: https://commons.wikimedia.org/wiki/File:Der_Tod_des_Totengrabers.jpg (fotografia Vitold Muratov CC BY-SA 4.0, originale 1524×2131, SHA1 `61224e341e6f206d6cca51672223d52b1d4bfeee`). **ATTENZIONE**: il file video è montato dalla fedele immagine alternativa su Eclectic Light, NON dai byte originali di Commons (HTTP429); non attribuire falsamente SHA1 originale alla riproduzione utilizzata. Revisione di diritti della riproduzione effettiva pendente prima della pubblicazione.

2. Viktor Vasnetsov — *Knight at the Crossroads* (1882), Russian Museum, tela 167×299 cm:
   - MP4: `ARTVISION_VASNETSOV_KNIGHT_AT_THE_CROSSROADS_CINEMA_V220.mp4`
   - **4.574.734 B**, SHA256 `04e87d301312a98a3abd6e04e06906dbb8126f16f989b26324e2e2f91a1fbaa7`
   - Commons Google Art Project: https://commons.wikimedia.org/wiki/File:Victor_Vasnetsov_-_Knight_at_the_Crossroads_-_Google_Art_Project.jpg, **5.527×3.065 px**, bytes originali SHA1 `ffb5fcb8cd0b76fbd4fba73be998ffc95542bbf0` verificati con Commons API, SHA256 `46d427591e748baefac27128f09206113da640add2a7088dfc10bb9895a3ecf3`, artwork PD-Art.

## Consegna verificata dalla Libreria ChatGPT

Cartella: `/ArtVision/Two_New_Works_V220`. Caricati e listati:
- `SCHWABE_DEATH_GRAVEDIGGER_V220.mp4`: `libfile_e8ef6cea1f708191a534e07460231058`, 5.307.019 B;
- `VASNETSOV_KNIGHT_CROSSROADS_V220.mp4`: `libfile_48e38cef54b88191978602b38ae07b05`, 4.574.734 B;
- `DUE_NUOVI_QUADRI_V220_COMPLETO.zip`: `libfile_acb61b0aee3881919fa8589405958fe5`, 40.681.807 B, SHA256 `ba5af0fb25566d9d92af53c2bb293f4463713727f495ff48cee8d272f16a44ad`.

**READBACK INDIPENDENTE PASS:** tutti e 3 i file sono stati materializzati ex novo dalla Library, SHA256 identici alle copie prodotte, ZIP CRC=PASS e i due MP4 interni hanno SHA identici agli originali. Entrambi i MP4 validati con `ffmpeg -xerror -map 0 -f null -`, ffprobe H264/AAC 720×1280, 880 frame, 44.0s. File realmente creati nel sandbox di questa conversazione e nel backup Library, non semplicemente nominali; test di apertura effettivo nell'app Android dell'utente **NON confermato**.

ZIP contiene due video, cover, contact sheet dei 10 soggetti, musica originale WAV, riproduzioni originali usate, script completo `artvision_new_v220_render.py`, post social BOZZA, fonti/crediti e JSON QA. Cinematografia vera del dipinto senza cornici disegnate, non animazioni I2I/3D. QA artistica umana *non completata* e niente Gold automatico.

## STATO E LIMITI

- **2 MP4 nuovi fisici prodotti** per due opere diverse, **solo variante Cinema Standard di ciascuna**, **non 4×1 completo**. I due Critico richiedono scrittura+voce naturale Google Gacrux e allineamento V82. I due Museum richiedono prima una cornice dell'esatto esemplare e una sala credibile documentata, V80/V118/V119 e scala reale; non crearle automaticamente senza verifica.
- Nessun aggiornamento della coda owner `queue/artvision_owner_selected_ten_20261102.json`: il conteggio canonico delle dieci opere resta **26/40** perché questi sono due piloti extra distinti, non slot delle dieci scelte. Non sostituire titoli o oscurare i vecchi video.
- **REVIEW soltanto**, nessuna pubblicazione sul sito o sui social, nessuna spesa, nessuna approvazione artistica. Necessari diritti del supporto fotografico, QA a velocità normale e prove su dispositivo prima dell'eventuale Gold.

Source-gate automatizzato riproducibile su ramo `pilot/artvision-two-new-paintings-v220`, GitHub Actions run `42464068915`, artifact `13611540002`; riproduzione tecnica completa e fonti nel ZIP della Libreria.
