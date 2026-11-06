# Delacroix V171 — QA geometria regia Critico e passaggio a Museum (06/11/2026)

## Azione nuova misurabile
Creato `tests/test_artvision_delacroix_v171_shot_geometry_gate.py` per individuare un difetto oggettivo nella ricetta V169 senza alterare il master già prodotto: l'immagine sorgente è **6875×5358, orizzontale**, mentre il video è **1080×1920, verticale**. I beat 1, 2, 8 e 9 sono etichettati «intero dipinto / intera composizione» ma richiedono `crop_height_px` di 4600, 5200, 4600 e 5350. Un crop 9:16 a quelle altezze copre rispettivamente larghezze di circa 2588, 2925, 2588 e 3009 pixel, su **6875** disponibili: NON mostra l'intero quadro. Questa è una discrepanza di geometria dimostrabile; non è una bocciatura automatica del montaggio V169 senza playback.

## Correzione per i PROSSIMI render, non per i master esistenti
- Beat 1/2/8/9: usare `full_plate` autentico con tutta la superficie pittorica in vista, senza tagli; padding verticale elegante e non falsamente museale. Il quadro resta orizzontale, mai deformato.
- Beat 3: figura del sovrano; beat 4: diagonale del letto; beat 5: drappeggio rosso; beat 6: oggetti e figure in basso; beat 7: cavallo a sinistra. Coordinate V169 soltanto **candidate**: controllo manuale sul vero originale prima di render.
- Dopo recupero della WAV V169: allineamento parola/frase e inizio inquadratura **prima o all'inizio** della menzione, hold leggibile, niente crop di teste, arti o gesti. Non fingere timestamps ASR non ancora recuperati.
- Museum: fonte fotografica Shonagon 03/10/2023, vera cornice del Louvre RF 2346, CC0, 3520×2936, 3376252 byte, SHA-1 Commons `1a1d7e125a15799d2b2631203ee791936906062d`. Foto autentica del 2023, NON prova di cornice originaria del 1827. <https://commons.wikimedia.org/wiki/File:Mort_de_Sardanapale_-_Eug%C3%A8ne_Delacroix_-_Mus%C3%A9e_du_Louvre_Peintures_RF_2346_-_avec_cadre_-_apr%C3%A8s_restauration_octobre_2023.jpg>
- Prima di render Museum: originale scaricato e SHA verificato, fotocredibilità prospettica e scala fisica 392×496 cm, scena di entrata/uscita coerente, **stessa WAV** V169 per Critico Museum, no TTS, nessuna nuova spesa. Un solo rendering pesante contemporaneo.

## Stato verificabile
- Commit test V171: `5a42be4f9f756a4a2e2dff294af038674720d284`. Il test è codice aggiunto su main; esecuzione in CI non ancora attestata.
- Source-preflight V170 richiesto con commit `7a0ee0e8ab634eea3809d2ee1d9b9190b03187a1`; **run e download effettivo non verificati** in questo ciclo. La fotografia è confermata da metadata pubblici, non da readback locale.
- Nessun nuovo MP4/ZIP, nessun nuovo SHA256 video, nessun Gold, nessuna pubblicazione. Conteggio queue invariato **22/40**; Delacroix **2/4**. Dalí sospeso.
