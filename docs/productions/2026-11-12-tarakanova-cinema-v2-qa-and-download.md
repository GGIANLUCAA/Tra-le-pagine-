# ArtVision · Princess Tarakanova — una sola opera, Cinema Standard V2

**Video originale completato in questa sessione**. L'opera selezionata dall'owner è il dipinto **Tretyakov** (Konstantin Flavitsky, inv. 347; dipinto nel 1863/esposto nel 1864), non la prima versione del 1862 a Ekaterinburg e non lo studio del Museo Russo.

## Produzione e QA
- V1 GitHub Actions [#43266815311](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43266815311), render e independent readback PASS. 51 s, 10 scene. L'esame reale del foglio contatti ha segnalato inquadrature troppo ripetitive su vestito/letto/finestra.
- Correzione V2: PR [#289](https://github.com/GGIANLUCAA/Tra-le-pagine-/pull/289) incorporata senza cancellare V1. Filmato **43,5 secondi**, **8** inquadrature semanticamente distinte, H264 720×1280, AAC score originale sintetizzato in locale; 2.545.253 byte, SHA256 **`3dc80b148f4de5ae1f7a0827fbd53288e847b52021d8752b0bcf89e69977f9d2`**.
- Render V2 [#43267711601](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43267711601), artifact #13967410907; produttore PASS. Il secondo job del workflow originale fallisce **solo per nome artifact V1 obsoleto**; non per corruzione del MP4. Originale V2 riscaricato e decodificato integralmente localmente (video e audio), SHA e ZIP CRC **PASS**.
- Prova indipendente originale riscattata **senza nuovo rendering** da CI PR [#290](https://github.com/GGIANLUCAA/Tra-le-pagine-/pull/290), run [#43268362183](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43268362183): `readback_existing_v2_without_render` **PASS**; FFmpeg full stream, SHA256, ZIP CRC e hash MP4 interno confrontati con gli stessi byte dell'artifact #13967410907. La run V2 iniziale rimane storicamente `failure` per nome errato, NON va occultata.
- Fotografia Commons esatta `Tarakanova.jpg` 1400×1845, 463.191 byte, SHA1 `4e96a98a1d6a4568119f54c348ca329ad6fc2521`, SHA256 `749e30f146b61886c5d342c7da8f204afdadc73e5a3fe953221ba4dbdbe5f948`. Foto dichiarata PD-Art/PDM su Wikimedia; **riuso commerciale territoriale ancora non approvato**.
- Copertina inglese, storyboard, testi social distinti e fonti nello ZIP; zero nuove API a pagamento, zero voce AI, zero pubblicazioni.

## QA artistico separato
Il contatto V2 è meno ripetitivo, ma il dipinto verticale relativamente piccolo rende comunque alcune inquadrature simili. Non approvare automaticamente Gold e non presentare analisi del contatto come review umana integrale a velocità normale. Conservare V1/V2 e migliorare **solo in revisione**, senza ricontare la medesima opera.

## Avanzamento
Una nuova variante Cinema della seconda coda owner da 30: registro checkpoint 25 distinti dopo il 24 precedente. **NON** venticinque pacchetti 4×1, NON corregge arretrato originario 26/36. Dadd Fairy Feller e Burne-Jones King Arthur in Avalon hanno già prove storiche di master, evitare rifacimenti.
