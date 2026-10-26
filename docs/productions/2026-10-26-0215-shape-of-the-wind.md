# ArtVision — The Shape of the Wind
**Ciclo:** 2026-10-26 02:15 Europe/Zurich  
**ID:** `artvision_20261026_0215_shape_of_the_wind`  
**Formato:** Collection (motore editoriale `artvision_cinema` / firma Cinema V6)  
**Stato:** `technical_pass_not_gold_master`; revisione artistica utente in attesa; non pubblicato.

## Consegna effettiva
- MP4: `VIDEO_MASTER.mp4`, 75.2 s misurati, H.264 + AAC, 1080×1920, 24 fps.
- Dimensione MP4: 21,853,918 bytes; SHA256: `48b45dc7640e6c622fc6c4e377ff9fa98fff66376ea4ec742f11f8bb151198b2`.
- ZIP: `ArtVision_20261026_0215_The_Shape_Of_The_Wind_COMPLETE.zip`, 61,118,185 bytes; SHA256: `a24ed7fd3cebf86379d22351a99f5117b59772c20a05f64250ca9dd440621d8f`.
- **Archivio dei byte:** allegati della conversazione ChatGPT in cui è stato prodotto. **Non** sono file pubblicati nel repository né artifact di GitHub Actions. Il registro non inventa URL GitHub per MP4 o ZIP.
- Copertina JPEG, 4 post social in italiano, licenze foto/registrazione, V32, V33, ricetta V13, regia e istruzioni di replica incluse nello ZIP.
- Nessuna pubblicazione social né importazione Video Library Studio.

## Tre opere e ricerca V32
1. Ivan Aivazovsky, *The Ninth Wave* (1850) — State Russian Museum / Commons PD-Art.
2. Utagawa Hiroshige, *Sudden Shower over Shin-Ōhashi Bridge and Atake* (1857) — museo Cleveland (documentazione), riproduzione Commons PD-Art.
3. Evelyn De Morgan, *The Storm Spirits* (c. 1900) — De Morgan Collection / Commons PD-Art.

**Importante:** le tre riproduzioni originali provengono da archivi ArtVision precedenti, riutilizzate senza alterare le immagini originali. **Il film è un montaggio nuovo**, non una copia di un MP4 già creato. Per selezionare il soggetto sono stati confrontati anche Thomas Cole (*The Course of Empire: Destruction*) e Gustave Caillebotte (*Paris Street; Rainy Day*), ma i rispettivi asset non erano scaricabili in questo ambiente; metriche social non disponibili e non inventate.

## Regia e audio
18 inquadrature semantiche, apertura grafica V6 (banda, font e linea), tagli opachi senza crossfade, camera statica e pochi micro-allontanamenti motivati. La sequenza confronta la tempesta marina, la pioggia nella stampa giapponese e l'allegoria delle forze atmosferiche, poi torna al mare. Nessuna voce né sottotitoli. Google Gacrux non verificabile come risorsa gratuita in questo ciclo; nessuna voce sostitutiva.
Musica: *Echoes of Time* — Kevin MacLeod (incompetech.com), registrazione originale CC BY 4.0, estratto e dissolvenze. Fonte: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300029 ; licenza: https://creativecommons.org/licenses/by/4.0/ .

## Controlli eseguiti
- FFprobe: H.264 1080×1920, 24 fps; AAC 48 kHz; durata 75.2 s.
- Decodifica FFmpeg integrale audio e video: senza errori.
- Campioni reali 0, 1, 3, 5, 7 secondi, 5 raccordi e finale: contatti visivi controllati.
- Volume audio misurato: media −21.0 dB, picco −5.9 dB.
- ZIP: test CRC passato e presenza MP4 + cover verificata.
- QA artistico non equivale a certificazione Gold Master; i diritti locali sulle riproduzioni e i claim musicali social richiedono ricontrollo prima di pubblicazione commerciale.

## Origine e limite tecnico
Produzione locale FFmpeg/Pillow su immagini originali già presenti negli ZIP precedenti. Non è stata avviata una nuova GitHub Action di rendering né usato un adapter Collection inesistente. La nuova pipeline è replicabile su un runner compatibile, ma il sito Video Library non è stato aggiornato.
