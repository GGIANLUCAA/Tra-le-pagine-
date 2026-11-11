# ArtVision OWNER 30 — controllo duplicati storici per #3 Dadd e #14 Avalon (11/11/2026)

**Ambito:** ricerca documentale, senza autorizzazione a nuovi video, nessun intervento su code, workflow, rendering, cornici, pubblicazione. Le intestazioni originali dell'owner e il loro ordine rimangono immutati nel JSON.

## Risultato concreto: due opere già prodotte storicamente, non nuove

### #3 The Fairy Feller's Master-Stroke — Richard Dadd
- **Identità museale:** Tate, **T00598**; https://www.tate.org.uk/art/artworks/dadd-the-fairy-fellers-master-stroke-t00598
- **Dossier già esistente:** `research/artvision_owner_30_dadd_fairy_feller_source_20261110.md`. Non duplicarlo.
- **Prova interna di precedente video:** `docs/productions/2026-10-27-0815-richard-dadd-fairy-feller.md` dichiara un MP4 Cinema V6 reale, 76,5 s, 1080×1920, SHA256 MP4 `401a3a802d42d045d3261ed143d9f302879db2bbc53876c6a11c2b52529fc693`; run https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40466527715 . Questa è **prova documentale di produzione storica**, non verifica fisica indipendente dei byte in questa esecuzione.
- **Asset storico dichiarato nel report:** Commons https://commons.wikimedia.org/wiki/File:The_Fairy_Feller%27s_Master-Stroke.jpg , 1800×2500 px; report dice scaricato e verificato allora, ma **SHA256 del file sorgente non riportato qui / NON ricalcolato in questo ciclo**.
- **Stato diritti:** uso commerciale dell'esatto file e territori NON ricontrollati; non presumere READY.
- **Esito anti-duplicato:** **DUPLICATO STORICO CON DOCUMENTAZIONE**, NON conteggiare come nuova opera. Se l'owner volesse un rifacimento, servirebbe autorizzazione separata.

### #14 King Arthur in Avalon — Edward Burne-Jones
- **Alias museale:** *The Sleep of King Arthur in Avalon*. Museo de Arte de Ponce, inventario **63.0369**; https://emuseum.museoarteponce.org/objects/3644/the-sleep-of-king-arthur-in-avalon
- **Dimensioni documentate nel report storico:** 279,4×650,2 cm; data 1881–1898.
- **Prova interna:** `docs/productions/2026-11-01-artvision-v114-quattro-nuove-opere-sedici-mp4-verificati.md` registra **4 varianti MP4** (Critico Standard/Museum, Cinema Standard/Museum), run https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41319811187 , artifact 13089630001; report dichiara decode completo e SHA dei master. Anche qui non ho riscaricato i video.
- **File storico dichiarato:** https://commons.wikimedia.org/wiki/File:Burne-Jones_Last_Sleep_of_Arthur_in_Avalon_v2.jpg ; 3120×1312 px; SHA256 riportato nel report `d9770b1f16f0bc6d58d13890b51debe23859f579cce45bc1f29713e774796f2d`. **Hash storico, non ricalcolato oggi**.
- **Stato diritti:** dichiarazione PD del report da distinguere dalle condizioni del singolo file e dalla destinazione commerciale. NON certificato in questa esecuzione.
- **Esito anti-duplicato:** **DUPLICATO STORICO 4×1 CON DOCUMENTAZIONE**, NON conteggiare come nuovo.

## Ulteriori verifiche di ordine e gate
- Caravaggio: dossier già presenti `research/caravaggio_cardsharps_bacchus_deep_dossier_20261108.md` e `research/caravaggio_medusa_deep_dossier_20261109.md`; nessuna nuova scheda duplicata, nessun diritto dedotto.
- #4 Sadko, #8 The Last Day of Pompeii e #9 The Bulls and Bears: dossier esistenti, rispettivamente `research/artvision_owner_30_repin_sadko_source_20261110.md`, `research/artvision_owner_30_bryullov_pompeii_deep_source_20261110.md`, `research/artvision_owner_30_beard_bulls_bears_deep_source_20261110.md`; **file e diritti non verificati** nei rispettivi fascicoli. #8 ha anche vecchie configurazioni di produzione: controllare master reali prima di chiamarla nuova.
- La verifica precedente nel JSON owner delle 30 dichiarava esplicitamente `full_historic_render_archive_checked=false`: questo audit dimostra perché il solo confronto con la coda 10 e il catalogo 100 era insufficiente.
- **Livelli di evidenza:** fonte museale = identificazione; rapporto storico GitHub = prova documentale di precedente produzione; file originale verificato = richiede byte/hash/pixel effettivamente ricontrollati; READY = richiede anche gate editoriali e diritti pertinenti. Nessuno dei due soggetti è dichiarato READY in questo audit.
- **Handoff:** mantenere entrambe le opere nella lista delle 30 così come scelta, ma etichettarle in ogni futura decisione editoriale come **già prodotte storicamente / non nuove**, senza toccare il JSON di selezione o la queue. Continuare il controllo duplicati sugli altri titoli prima di suggerire una nuova produzione.
