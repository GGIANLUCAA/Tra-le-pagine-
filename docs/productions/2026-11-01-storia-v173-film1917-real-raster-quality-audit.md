# La Storia Rivive V173–V174 — Moda 1917, scansione ORIGINALE verificata e ricerca scansioni recenti

Data 1 novembre 2026 · issue #144 · benchmark video utente 43055/43056 V165

## Passo reale completato V173

Prima di consumare una sola chiamata I2I o Vidu, è stato effettivamente recuperato da **Internet Archive** il film storico *Modes of the Moment* (1917), Prelinger `Modesoft1917`. Si tratta di un contenuto plausibile editorialmente: 18 riprese storiche secondo il catalogo pubblico, incluse modelle con cappelli, vestiti, scarpe, primi piani e gesti. Questa selezione non costituisce autorizzazione di uso italiano.

- Scheda del singolo film: https://archive.org/details/Modesoft1917
- Archivio: Internet Archive / Prelinger; metadata per il singolo item `licenseurl=http://creativecommons.org/licenses/publicdomain/` (**dichiarazione archivistica, non consulenza legale sui diritti italiani**).
- File esatto acquisito: `Modesoft1917.mpg`, etichettato nell'API `source=original`, 37.644.504 byte.
- **SHA1 verificato sui byte realmente ricevuti**: `7a2a79a36ad7d5d2388a2370c38d2329d266c11a`.
- SHA256: `e5427948ad921cc24b48815af5925194867dfd571908c6f6d7d84c0e34e63476`.
- **FFprobe reale:** codec `mpeg1video`, **352×240**, durata **215,9804s**, sample aspect ratio `200:219`. La definizione misurata non è 4K, HD, 720p, né un buon equivalente per le reference.
- Ci sono almeno **cinque scene diverse realmente decodificate** ai PTS `23,0`, `53,5`, `68,0`, `166,0`, `207,0` s; contatto visivo PRIVATO in artifact GitHub. Le cinque scene contengono modelle in abito 1917 e diversi primi piani, non cinque zoom dello stesso frame.
- Metadati ulteriori: derivati `Modesoft1917.mp4` (22.498.723 byte), `Modesoft1917_512kb.mp4` (15.161.868) e `Modesoft1917.ogv` (14.896.959); la presenza di un MP4 più grande o di uno stream compresso NON prova risoluzione nativa superiore.
- **Esito esplicito: `REJECT_LOW_NATIVE_RASTER_FOR_PHOTOREAL_MOTION`.** Non inviare a Finegrain/Vidu, non girare altro teaser mediocre. Anche una pellicola interessante con primi piani deve avere pixel sorgente verificabili sufficienti per colori/dettagli fotorealistici stabili a 30fps.

**Prova:** [GitHub Actions V173 #41294820297](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41294820297) concluso SUCCESS, 6 test di sicurezza PASS, metadata + fonte filmica vera scaricata/verificata e cinque PNG di archivio in artifact `STORIA_V173_FASHION1917_SOURCE_NATIVE_QUALITY_REVIEW` (id `13079145153`). I video di riferimento utente non sono stati copiati pubblicamente. Il film integrale non è caricato nell'artifact.

## Modifica software e precauzioni

- `src/storia_rivive_v173_fashion1917_source_scout.py`: selezione con dimensioni e nomi di file controllati, verifica SHA1 se l'archivio lo fornisce, verifica raster FFprobe sui byte, cattura cinque shot reali, **status di blocco per sorgenti sotto 960×720**. Questa soglia serve da filtro preliminare prudente, non garantisce da sola realismo o vera scansione ottica nativa se il file è già stato ingrandito.
- `tests/test_storia_rivive_v173_fashion1917_source_scout.py` verifica 6 condizioni incluse licenza esatta, traversal/URL, dimensioni dichiarate non equivalenti ai pixel, no download senza licenza e blocco dei file oltre 160 MiB.
- Il workflow `.github/workflows/storia-v173-fashion1917-source-preflight.yml` su branch/PR di ricerca usa solo API pubbliche e FFmpeg/Pillow gratuiti, nessun segreto provider.
- `src/storia_rivive_v174_recent_high_scan_discovery.py` e relativi test: ricerca **solo metadata** presso Internet Archive per film dal 1895 al 1935 archiviati dal 2023; solo licenze PD dichiarate a livello di singolo item, distinzione anno riprese/anno upload, elenco delle dimensioni file e obbligo di controllo FFprobe. Ricerca e candidati non costituiscono una produzione né licenza verificata Italia.

## Prossimo blocco tecnico

Serve una scansione ottica migliore (possibilmente 2K/4K con persone grandi e cinque riprese coerenti) e una vera pipeline di **restauro video temporale**, non sola fotografia I2I/colore propagato con optical flow. I modelli open source FlashVSR/SeedVR2 usano GPU sostanziali e non sono già eseguibili per magia sul runner GitHub gratuito; prima di invocarli controllare compatibilità e costo effettivo. Non spenderci crediti Vidu né creare richieste non autorizzate per risolvere un difetto di qualità del filmato originale.

Stato di produzione: **nessun nuovo MP4 approvato**, 0 I2I, 0 Vidu, 0 crediti, niente pubblicazione, diritti italiani ancora da verificare. V98, ArtVision, WOW LAB, scheduler delle 3h e gateway Vidu invariati.


## V174 — ricerca archivio scansioni recenti, esito basato sui metadati veri

[GitHub Actions #41295236656](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41295236656) **SUCCESS**, 12/12 test (6 V173 + 6 V174), bitstream originale moda 1917 verificato di nuovo, più ricerca metadata Internet Archive:

- Ricerca limitata a film Prelinger **pubblicati nell'archivio dal 2023** con anno storico dal 1895 al 1935: **54** record trovati.
- Metadati integrali del singolo titolo effettivamente consultati per **24** record più recenti: tutte e **24** le schede **non avevano una dichiarazione Public Domain/CC0 esatta a livello di item**. Il software li ha esclusi per evitare attribuzioni di diritti non verificate.
- Nessun candidato certificato all'interno di questo **campione limitato**; **non** significa che non esistano scansioni HD/4K o film legalmente riutilizzabili in altri cataloghi, né che i 24 titoli siano sicuramente protetti.
- `V174_RECENT_PRELINGER_METADATA_CANDIDATES.json` nell'artifact privato GitHub `13078913329`: 54 identificatori di ricerca, 24 oggetti esaminati, ripartizione `no_film_year=0`, `no_exact_public_domain_item_mark=24`, `no_video_file=0`; **0 media scaricati** in V174, **0 risoluzioni HD dichiarate verificate**.
- **Regola di sicurezza:** come chiarisce anche il titolare dei Prelinger Archives nelle FAQ ufficiali aggiornate il 27 maggio 2026, la licenza va verificata singolarmente: non tutti i suoi film sono Public Domain. Non confondere date di pubblicazione nel catalogo digitale con le date delle scene.

Nessun nuovo episodio prodotto; la priorità rimane reperire almeno una fonte coerente con sufficiente dettaglio **e** chiara provenienza/licenza territoriale, poi prova temporale GPU con disponibilità/quote effettivamente controllate e confronto con i reference 43055/43056.
