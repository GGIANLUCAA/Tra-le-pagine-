# La Storia Rivive — V138 · Versailles 1919 · dossier fonte, NON approvato

**Data di ricerca:** 31 ottobre 2026. **Stato:** `SOURCE_RESEARCH_ONLY`; 0 I2I, 0 Vidu, 0 autorizzazioni social/sito. Integrazione esclusiva PR #154 / issue #144.

## Provenienza identificata, non congetture

- Fonte scelta nella coda `queue/storia_rivive_candidates_v58.json`: `versailles_treaty_1919`; filmato Commons [The signing of the peace treaty of Versailles (16 fps).webm](https://commons.wikimedia.org/wiki/File:The_signing_of_the_peace_treaty_of_Versailles_(16_fps).webm).
- Wikimedia Commons riporta **film muto statunitense**, **1919**, **produzione: United States Department of Defense**, origine negli archivi USA (NARA Identifier **24746**); originale WebM VP8/Vorbis `1920×1080`, **497,467 s**, **46.244.117 byte**. Non asserire «scansione HD nativa» dal raster web: bitrate nominale ~744 kbps e dettagli volti da verificare nei byte.
- Riscontro indipendente presso [DocsTeach, National Archives Foundation, *The Signing of the Peace Treaty of Versailles*](https://docsteach.org/document/signing-treaty-versailles/): identificatore NARA **24746**, materiale `Motion Picture 111-H-1243`, **28 giugno 1919**, archivio **Records of the Office of the Chief Signal Officer, Record Group 111**. Personaggi in descrizione: delegazioni, firmatari, folle. **La presenza di un nome nella descrizione del film intero non è la prova della sua identità in un fotogramma**.
- Dossier nasce per scouting editoriale di un fatto storicamente documentato; **non** dichiara che il film sia poco utilizzato sui social, né attribuisce le singole riprese o volti non esaminati.

## Diritti: distinzione obbligatoria

- La pagina Commons sul file HD dichiara il **pubblico dominio negli Stati Uniti** (per alcune opere USA antecedenti al 1931), ma avverte esplicitamente che tale situazione **può non valere fuori dagli Stati Uniti**; la fonte è attribuita a un ente governativo federale USA, come la scheda DocsTeach.
- DocsTeach riporta `Rights: No Known Copyright`. Questo dato NON equivale automaticamente a licenza libera per sfruttamento in Italia e per qualsiasi montaggio con AI.
- **`rights_italy_verified=false`**, **`author_year_italy_term_review_pending=true`**. Servono verifica dei diritti residui e degli eventuali diritti connessi applicabili al film specifico, dell'eventuale versione composta e della natura della produzione prima di usare le scene su sito e social. Evitare un «diritti Italia OK» senza prova giuridica documentata.
- Mai allegare i media originali ai workflow artifact pubblici, salvo autonoma verifica dei diritti; i workflow tecnici conservano solo JSON e fogli contatto per analisi.

## Criteri di selezione per procedere a I2I e Vidu

1. Scaricare e verificare SHA dei byte originali dalla pagina ufficiale e PTS originali della pellicola mediante V101/V124/V125. Se non verificabili: `SOURCE_REJECTED`.
2. Selezionare 5 **veri cambi inquadratura in movimento**, non semplici crop, titoli o cinque frame della stessa ripresa. Preferire presenze umane leggibili, gesti e folle non ridondanti, senza ricostruire tratti inventati.
3. Verificare leggibilità *9:16* su viso, mani, oggetti, continuità, nitidezza sufficiente per standard **V98 San Francisco 1906**, senza spacciare `1920×1080` del file digitale per scansione d'epoca 4K.
4. Se anche uno dei cinque frame non è restituibile con un I2I realmente fotografico e fedele, cambiare shot o respingere la fonte; la classificazione tecnica `SOURCE_RESEARCH_REVIEW_REQUIRED` non dà approvazione editoriale.
5. Solo dopo diritti Italia verificati, piano di costo e approvazione Vidu appropriata, 4 veri I2I + 1 clip Vidu source-locked, V91/V94/V96/V99 sul vero MP4, 3 piloti distinti e controlli Android/download.

**Nessuna spesa, nessuna pubblicazione, nessuna modifica ArtVision/WOW LAB/V98.**


## Esito reale della prima acquisizione V138 (31 ottobre 2026)

La [GitHub Action V138 #41198837596](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41198837596) è terminata **SUCCESS** come job di ricerca. L'[artifact #13041891851](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41198837596/artifacts/13041891851) è stato materialmente scaricato, estratto e il `REAL_SOURCE_AUDIT_V138.json` letto; il contact sheet originale dei nove campioni è stato aperto e osservato.

- Impronta originale: `a29801c567fa7f237fed71a686b853a5c37e1323aed7a53c5a73265b975dadf8`, raster decodificato `1920×1080`, SHA e frame originali verificati da V134.
- V124: soltanto **9 candidati fotografici** campionati; nel contact sheet si distinguono monumenti, folla, veicoli e delegati, con diverse pose ripetitive presso automobili e scale.
- V125: **1 sola finestra** con movimento B/N verificato con l'attuale algoritmo. V126: nessuna cinquina valida; V128 e V129 bloccati per mancanza di input. Stato finale reale: `SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY`.
- Questo è un rifiuto **dell'attuale selezione e metodologia di sampling**, non una sentenza storica che il film non contenga cinque cambi camera nel suo complesso. Prima di considerare un eventuale riesame occorre una nuova prova, conservando SHA e limiti. **Nessun I2I, Vidu, MP4 finale o diritti Italia autorizzati.**

È stata aggiunta al registro V133 una esclusione **con ID + pagina + SHA + audit GitHub verificato**, così che i cicli V101 non riscarichino inutilmente anche questa stessa fonte. Identica regola per la pellicola White House 1917–1921 (V136) e la filatura 1920 (V132). Le esclusioni si possono riesaminare con nuova evidenza, non rappresentano divieti di diritto d'autore.

**CI del fix**: [V109 #41199149983](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41199149983), **133/133 test PASS** (14 suite, inclusi 4 nuovi test sul registro). I workflow V138 finali sono **solo manuali/riutilizzabili** (`workflow_dispatch`/`workflow_call`), niente nuovo scheduler o nuovi job Vidu.
