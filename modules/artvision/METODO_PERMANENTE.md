# IMPORTANTE — ART VISION V6 APPROVATA\n\n> **VERSIONE APPROVATA (20/10/2026): ARTVISION CINEMA V6 — GOLD MASTER.** L'utente ha approvato esplicitamente il risultato V6 come migliore; è il **riferimento artistico predefinito per i prossimi film**, non V5. Leggere PRIMA [V6_APPROVATA_GOLD_MASTER.md](V6_APPROVATA_GOLD_MASTER.md) e [REGIA_CINEMA_V6.md](REGIA_CINEMA_V6.md). Le indicazioni V1–V5 sotto sono storico, non più default. Backup GitHub dedicato: `ARTVISION_V6_GOLD_MASTER_APPROVATA_2026-10-20`. Per nuovi artisti progettare nuovo storyboard V6 con opere/musica proprie. Non toccare i video narrati.\n\n# ArtVision — PROCEDURA PERMANENTE / RICETTA DI PRODUZIONE

## VERSIONE APPROVATA — CINEMA V6 (20 ottobre 2026)

**La regia Cinema V6 è ora il riferimento artistico principale confermato dall'utente.** Quando viene richiesto un nuovo video d'arte, NON usare automaticamente gli esperimenti V1–V5 e NON riproporre slideshow, fondali neri con immagini piccole, zoom sistematici o montaggi tutti uguali.

Leggere prima **[VERSIONE_APPROVATA_CINEMA_V6.md](VERSIONE_APPROVATA_CINEMA_V6.md)** e **[REGIA_CINEMA_V6.md](REGIA_CINEMA_V6.md)**, poi usare il motore **`director_cinema_v6.py`** e il workflow dedicato **`artvision-cinema-v6.yml`**. Per artisti diversi da Van Gogh occorre uno storyboard nuovo specifico: il motore corrente contiene ancora la regia personalizzata per Van Gogh.

**Il vecchio `artvision-render.yml` parte ancora con V5 per compatibilità tecnica: NON equivale al nuovo standard approvato.** Seguire il workflow V6 dedicato finché non si predispone un nuovo artista. Conservare intatti libri narrati, vecchi motori e backup. Una sola versione filmica per artista, salvo diversa richiesta.

Versione operativa: 20 ottobre 2026. Questa guida va mantenuta nel repository per il futuro: il progetto non deve dipendere dalla memoria di una chat.

## Principio assoluto
Il repository `GGIANLUCAA/Tra-le-pagine-` è uno studio video modulare. **Non rimuovere mai** narrazioni, video libri, workflow `render-v3.yml`, strumenti Gemini, regie V3/V4/V5, modelli precedenti o le loro configurazioni.
Il modulo ArtVision è separato in `modules/artvision`; workflow separato `.github/workflows/artvision-render.yml`.

Ramo storico intatto prima di ArtVision: `backup-prima-artvision-2026-10-20`.

## Quando l'utente chiede: "Fammi un video su [artista]"
1. Aprire il repository e verificare le versioni correnti del codice e workflow (non indovinare lo stato).
2. Recuperare identità artista (controllare omonimi), eventuali soggetti e periodi richiesti.
3. Cercare opere autentiche nei cataloghi museali tramite le API: Art Institute of Chicago, Cleveland Museum of Art, Metropolitan Museum of Art (o estensioni documentate).
4. Filtrare esplicitamente solo immagini con diritti/condizioni di riuso idonei. Conservare artista, titolo, data, fonte, URL scheda e URL originale, licenza/crediti. Se nessuna fonte idonea, interrompere e comunicarlo, non inventare immagini.
5. Rimuovere duplicati e scegliere sequenza coerente, non affidarsi al primo risultato. Mettere al centro la fedeltà all'opera.
6. Per impostazione predefinita: video verticale 9:16, 150 secondi, intro/finale con nome artista, senza narrazione, con musica utilizzabile e camera digitale discreta.
7. Costi standard: nessuna API di immagini o voce a pagamento; installazioni open-source (Pillow, NumPy, FFmpeg). Non abilitare piani a pagamento o pubblicazioni senza approvazione.
8. **Modalità autonoma preferita**: aggiornare `modules/artvision/queue.json` con un `request_id` nuovo, `artist`, `duration`, `max_works`, `approved_for_render: true`, `publish: false`; il push della coda avvia automaticamente il workflow V1.3. Come alternativa manuale, avviare workflow GitHub `artvision-render.yml` scegliendo `artist`, `duration` (120/150/180) e `max_works` (8/12/16/20/24). Per il telefono: repository → Actions → **ArtVision** → **Run workflow**.
9. CONTROLLARE la run fino a `completed / success`; aprire i report, l'MP4, la copertina, il numero di immagini, l'audio, la durata e la presenza di sorgenti/licenze. Non promettere il file se non è stato creato.
10. Consegnare il pacchetto `ARTVISION_<run_number>` da **Artifacts** della run riuscita; preferire un MP4 diretto quando possibile. Mantenere i link ai file di progetto e al workflow per riutilizzo.
11. Registrare tempi effettivi di elaborazione e motivi degli errori per calibrare quante produzioni al giorno sono realistiche.
12. Pubblicazione social sempre separata dalla generazione e subordinata al controllo dei diritti e dell'utente.

## Risoluzione errori da non dimenticare
- **20 ottobre 2026, run #1 e #2**, exit code 127: runner `ubuntu-latest` privo di `ffmpeg`. Log effettivo `ffmpeg: command not found`. **Soluzione V1.2**: installare ffmpeg con apt prima dei controlli. Non scambiare per causa la warning Node.js 20. Usare `sed -n '1p'` al posto di `head` nelle pipe sotto `pipefail`.
- Leggere sempre il log dello step fallito, senza attribuire problemi alla cieca.
- Se fallisce una sorgente artistica, eseguire fallback verso gli altri archivi. Non disabilitare il filtro diritti per far passare un video.
- Se manca l'Artifact significa che non è stato consegnato il filmato; una run avviata non è prova di video finito.

## File e output standard
`modules/artvision/artvision.py`, `modules/artvision/README.md`, `.github/workflows/artvision-render.yml`.
Per ogni video produrre `ARTVISION_VIDEO.mp4`, `COPERTINA.jpg`, `OPERE_FONTI_E_DIRITTI.json`, `CREDITI_E_FONTI.txt`, `DESCRIZIONE_SOCIAL.txt`, `MONTAGGIO.json`, `REPORT_PRODUZIONE.json`.

## Per la qualità social
Non dipingere nuovi quadri falsamente attribuiti. Non deformare e non falsare il colore delle opere; privilegiare alta risoluzione, belle copertine, ritmo professionale, musica originale o autorizzata. La modalità automatica è un punto di partenza: controllare veramente il risultato e migliorare montaggio/musica prima di dichiararlo ottimale. In futuro aggiungere 1080×1920, curatela cronologica/tematica, galleria anteprima e più tipologie di opere.

## Istruzioni per futuri ampliamenti
Non riscrivere da zero: aggiungere un modulo o preset e testare che il modello precedente funzioni. Backup, cambi piccoli, verifica sul runner e conservazione report; preferire correzioni incrementali misurate.

## Test di collaudo riusciti
- Run GitHub #3: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39411451722 — esito SUCCESS, 150.167 secondi, 16 opere CC0, 24 inquadrature, audio/video verificati, 0 API a pagamento, 176 secondi di elaborazione. Output iniziale 136 MiB.
- Run GitHub #4: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39412319602 — esito SUCCESS dopo cambio preset x264 `ultrafast` → `veryfast`. MP4 14.7 MiB, 150.167 secondi, 720×1280 H.264/AAC, 16 opere. 179 secondi di elaborazione. Per le prossime puntate conservare il preset compatto, con controllo qualitativo.
- **Coda V1.3 testata con successo**: run #6 https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39412758541 — richiesta JSON approvata, raccolta opere, montaggio e artifact `ARTVISION_6` da circa 15 MB, job SUCCESS. Il test iniziale #5 falliva perché scriveva caratteri letterali `\\n` in `GITHUB_ENV`: correggere in vere sequenze di newline Python `\n` (committed).


## NUOVA REGOLA PERMANENTE — REGIA CINEMA WOW V2 (20 ottobre 2026)

**Feedback vincolante dell'utente:** il video Van Gogh V1 è stato giudicato troppo simile a una sequenza di fotografie con dissolvenze. Non riproporre la V1 come qualità definitiva. Il modello di riferimento inviato è `Enfermedad-cromtica-fdown.net.mp4`: ritmo rapido, chiaroscuro, motivi che ritornano, focali e dettagli, fusione con la musica. **Non riutilizzare quel filmato o il suo audio.**

La nuova guida editoriale completa è [REGIA_CINEMA_WOW_V2.md](REGIA_CINEMA_WOW_V2.md), da leggere prima di ogni produzione; il file è parte permanente della memoria operativa del progetto.
**Moduli indipendenti:** `artvision.py` mantiene V1; `cinema_wow_v2.py` implementa regia cinema musicale; `artvision_cinema_run.py` è il nuovo orchestratore che importa gli archivi museali dalla V1.
**Nuovo default nel workflow:** `style: cinematic_wow`; per tornare alla V1 usare esplicitamente `style: museum_legacy`. La coda di produzione conserva lo stesso schema e può indicare `style` (se assente assume cinematic_wow).
**Importantissimo:** la sintesi musicale originale è sperimentale e NON deve essere presentata come equivalente a musica professionale selezionata. La visione del rendering finale e il feedback dell'utente sono indispensabili.
Per un episodio nuovo, conservare V1 e testare V2 su un provino di 20–30 secondi e poi sul video completo. Non attestare la qualità artistica senza ispezione del file.

**Backup prima delle modifiche V2:** `backup-artvision-v1-3-prima-regia-wow-2026-10-20`. Nessuna modifica ai motori narrati.


## Test reale della nuova regia V2 — riuscito il 20 ottobre 2026

- [GitHub Actions run #7](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39416219435) conclusa con **SUCCESS**, nuovo motore `modules/artvision/cinema_wow_v2.py` invocato da `artvision_cinema_run.py` tramite workflow V2.
- Artista: Vincent van Gogh; **16 opere**, **101 inquadrature** (contro 24 della V1), circa **149,834 s** a **720×1280** con codec H.264/AAC e **0 chiamate API a pagamento**. Render riportato: **235,2 secondi** complessivi. L'artifact GitHub `ARTVISION_7` include opere/fonti, storyboard regia e report.
- QA creativo: il primo render automatico aveva una copertina basata sullo schizzo monocromatico «Wheat Field», giudicata debole per il gancio. È stato quindi corretto il motore per **scegliere deliberatamente l'immagine d'apertura**, con «Two Poplars in the Alpilles» come preferenza Van Gogh e scelta cromatico-compositiva per altri artisti.
- È stata poi creata una versione di consegna localmente con nuovo incipit colorato, tipografia visibile, compressione del film a circa **25 MB** e normalizzazione audio. Questa **versione post-prodotta** non va confusa con l'artifact GitHub #7; quando si fa un nuovo render dal repository usare il codice di copertina aggiornato.
- Audio V2: musica algoritmica composta nel sistema. È **provvisoria**, non un brano professionale; per valutazione qualitativa definitiva serve una musica di alta qualità con licenza verificabile.
- La nuova regia ha superato il collaudo **tecnico**, non equivale all'approvazione estetica dell'utente. Chiedere feedback sul video anziché affermare automaticamente che l'effetto wow è perfetto.

Per le prossime produzioni: `cinematic_wow` è il default, `museum_legacy` resta selezionabile esplicitamente. Non alterare la generazione dei libri narrati.


## Aggiornamento definitivo — REGIA ARMONICA V3 (20 ottobre 2026)

L'utente ha valutato V2 migliorata ma **ancora troppo movimentata**. Non usare mai effetti split-screen, doppio quadro diviso, pan casuale, zoom rapido e continuo o musica generativa improvvisata come impostazione ArtVision. Il secondo video campione (`No-Cuesta-Saber-fdown.net.mp4`) privilegia tempi di contemplazione: leggere il dipinto prima dei tagli.

**Nuovo preset raccomandato e workflow predefinito:** `style=harmonic_reveal` in `.github/workflows/artvision-render.yml`; codice `modules/artvision/harmonic_reveal_v3.py`. Ogni quadro deve prevedere un dettaglio significativo *scelto intenzionalmente* e motivato da una mappa per artista, seguito da zoom-out dolcemente rallentato e visione del quadro intero. Impostazioni precedenti `cinematic_wow` e `museum_legacy` restano recuperabili.

**Musica reale:** `Calmant` (Kevin MacLeod, pianoforte, CC BY 4.0, attribution obbligatoria). Sorgente e licenza verificabili: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100859 e https://creativecommons.org/licenses/by/4.0/ . V3 deve fallire quando non è disponibile una registrazione autorizzata: niente sintetizzatore fallback. La musica è soggetta a copyright, ma concessa in licenza gratuita con attribuzione.

**Guida prioritaria da leggere per ogni nuovo video:** [REGIA_ARMONICA_V3.md](REGIA_ARMONICA_V3.md). La sua mappa di dettagli è curata *per Van Gogh*, non per altri pittori. Per ogni nuovo artista aggiungere focali motivate e verificare opere e musica PRIMA di avviare la produzione; non copiare coordinate casuali. La pubblicazione resta sempre separata dalla produzione.
**Backup V2:** `backup-artvision-v2-prima-regia-armonica-v3-2026-10-20`.


## V3 prima produzione COMPLETATA / verificata — 20 ottobre 2026
- GitHub Actions [run #9](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39422133252) **SUCCESS**, artifact `ARTVISION_9` verificato.
- Van Gogh, 16 opere di museo con metadati, 16 scene intenzionali (ognuna dettaglio → camera rallenta → intero), 150,000 secondi, 720×1280, H.264/AAC.
- Vera registrazione scaricata dal sito ufficiale di Kevin MacLeod `Calmant.mp3`; SHA-256 `145d51e68117d5dc47b68cd2ac0577fd3c9d8c7464b49c32b3c25ad882c106c5`. Manifest e licenza CC BY 4.0 in `MUSICA_LICENZA_E_CREDITI.json`; allegare crediti ai post.
- ArtVision V3 0 API a pagamento. Il report riporta 244,5 secondi end-to-end.
- È stato verificato un campione di 27 fotogrammi da 9 opere (dettaglio, reveal, intero). Niente split-screen. Nota visiva: dipinti orizzontali interi usano bande scure verticali per preservare il rapporto d'aspetto, non tagliare l'opera.
- MP4 originale ~35 MB; successiva ricompressione H.264 CRF24 preservando 150s/AAC ~16 MB, volume medio -18 dB, picco -0.8 dB.
- Per evitare doppi render inutili durante gli aggiornamenti, il trigger GitHub Actions automatico ora ascolta solamente modifiche a `modules/artvision/queue.json` (resta anche workflow_dispatch manuale).
- La registrazione è **copyrighted ma licensed CC BY 4.0**, NON 'priva di copyright'; crediti pubblici obbligatori per monetizzazione/licenza.
- ArtVision V1/V2 e tutti i motori libro/narrati sono conservati. V3 per altri artisti richiede mappa di soggetti ragionata, non sempre stessa selezione.
- Verifica creativa finale deve seguire il gusto dell'utente. Il render green dimostra solo affidabilità tecnica.


## NUOVA PREFERENZA VINCOLANTE: ATELIER V4 · 20 ottobre 2026

L'utente apprezza V3 rispetto alle precedenti ma rifiuta la ripetitività di ogni quadro identico. **V4 è il preset preferito.** Ogni opera deve avere un piano artistico diverso: talvolta un dettaglio soltanto, talvolta 2/3, talvolta iniziare dall'opera completa e poi avvicinarsi. Per Van Gogh usare focali motivati come occhi, petali, alberi, gesti e prospettiva; per nuovi artisti rivedere tutte le coordinate, mai copiarle. Camera quasi ferma sui dettagli: il movimento non è fine a se stesso. Alternare forme narrative, tempi calmi e brevi tensioni; no split screen, no effetti ripetitivi. **1080×1920 Full HD** da riproduzioni originali, non millantare 4K reale. Piccolo titolo del brano e compositore nel video, attribution completa nella descrizione.

**Musica differente nei prossimi video**: utilizzare registrazioni autentiche licenziate; tenere `music_library.json` per storico delle ultime musiche e per scoprire nuove scelte adatte allo stile. Le licenze ufficiali vanno controllate: CC BY 4.0 richiede attribution visibile. Il numero di brani ricercati è maggiore del numero di download già collaudati.

Nuovo motore separato: `modules/artvision/atelier_v4.py` — selezione `style=atelier_v4` (default workflow); impostare `music` per ogni richiesta. V1, V2, V3 e i video libri restano invariati. Backup `backup-artvision-v3-prima-regia-atelier-v4-2026-10-20`. Linea guida completa: [REGIA_ATELIER_V4.md](REGIA_ATELIER_V4.md).

**Consegna futura**: GitHub Actions con coda `modules/artvision/queue.json`, nessuna pubblicazione automatica, collaudo MP4, audio, fonti, licenze e `quality_report_v4.py` (tavola visuale dei dettagli). La run V4 #11 si era fermata su un URL musicale inventato: file corretto ufficiale è `Evening Fall - Piano.mp3`, non `Evening Fall (Piano).mp3`. Controllare l'URL reale nel metadato di [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Evening_Fall_(Piano)_(ISRC_USUAN1100235).mp3) prima dei download. Non generare un brano finto come sostituto silenzioso.


## PRIMO RENDER V4 REALE SUPERATO — 20 OTTOBRE 2026
- [GitHub Actions #12](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39426478495) **success**, artifact `ARTVISION_12` verificato e MP4 esaminato.
- Vincent van Gogh: 12 opere museali, 49 fasi di inquadratura curate, alternanza effettiva di 1/2/3 dettagli e apertura con opera intera; senza split-screen.
- Video 150,000 secondi, 1080×1920 Full HD, 24fps H.264 + AAC; file master 93.4 MB (89.1 MiB). Questa è **alta qualità Full HD**, non 4K nativo.
- Musica reale: `Evening Fall (Piano)`, Kevin MacLeod, ISRC USUAN1100235, registrazione 165,07 secondi verificata con ffprobe. Licenza attuale riportata dal sito dell'autore CC BY 4.0; la copia archivio Wikimedia indica CC BY 3.0. Credito esplicito nel MP4 e `DESCRIZIONE_SOCIAL.txt`.
- Il download da `https://incompetech.com/music/royalty-free/mp3-royaltyfree/Evening%20Fall%20(Piano).mp3` era **errato (404) sulla run #11**. URL ufficiale corretto è `Evening%20Fall%20-%20Piano.mp3` (fonte Wikimedia) e fallback verificato Commons `Evening Fall (Piano) (ISRC USUAN1100235).mp3`. Non inventare download URL in futuro.
- Il primo V4 #12 ha utilizzato il file Wikimedia Commons: hash SHA256 `5195c266275c694f9186dceb23e667c45ed74767d97f6615df01021fed3f048e`.
- Audio picco massimo misurato a -3.3 dBFS, senza clipping; durata e flussi controllati.
- Tempo di produzione effettivo circa 321 secondi, 0 API a pagamento; upload video non è pubblicazione.
- **Controllo visuale**: contact sheet con 3 campioni per ciascuna delle 12 opere preparato dalla run e esaminato: ritmo variato, quadro completo, dettagli, credit musicale visibile nei primi/ultimi secondi. Alcune immagini museali hanno risoluzioni inferiori a 1080 e alcuni soggetti sono disegni: non sostenere che tutti i dettagli siano 4K.
- Script permanente `modules/artvision/quality_report_v4.py` e workflow aggiornato per includere `CONTATTO_REGIA_V4.jpg` e `CONTROLLO_ATELIER_V4.json` nei prossimi render, senza rifare il sistema.
- La pubblicazione resta disabilitata; l'utente deve giudicare il gradimento artistico e l'idoneità dei diritti nel proprio territorio.


## V5 REALMENTE PRODOTTA E VALIDATA — 20 ottobre 2026
- Single final film: Vincent van Gogh, **150.000 sec, 1080×1920, H.264/AAC**, 12 opere autentiche, 49 passaggi diversificati, sola firma artista e piccolo MUSIC BY nei primi secondi; nessun testo nel resto del video.
- [GitHub Actions run #14](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39435930028) SUCCESS, artifact `ARTVISION_14` verificato, MP4 realmente scaricato e cover visionata. Non distribuire la precedente run #13 come versione finale: aveva una copertina eccessivamente vuota.
- Copertina V5 aggiornata: fotografia autentica degli *Irises* avvicinata e pieno schermo, nome artista + MUSIC BY Kevin MacLeod in serif minimale su un velo scuro. Non aggiungere ulteriori testi nel video.
- **Cinque immagini Cleveland Museum migliorate da web JPG 900px a JPEG print originali CC0**: Adeline Ravoux 3400×3389, The Large Plane Trees 3400×2713, Two Poplars 2543×3400, Landscape with Wheelbarrow 3400×2400, Dr. Gachet 2654×3400. Fonte e risultato per immagine in `QUALITA_SORGENTI.json`.
- Nuovo brano, diverso dalla V4: `Dreams Become Real`, Kevin MacLeod, registrazione originale strumentale ~410.07sec da https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreams%20Become%20Real.mp3 ; scheda https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027 ; **CC BY 4.0**. SHA256 `a8ea5df5f969ed8d898af7fe07eb4712233f03e9d83f7ebcc88d1c851f3171b0`. Informazione completa di attribuzione nella descrizione pubblica del post e file licenze; il solo MUSIC BY nel filmato non sostituisce l'attribuzione CC obbligatoria.
- Durata elaborazione V5 con upgrading museale **318,56 s**; 0 API a pagamento, nessuna pubblicazione automatica, dimensione MP4 43.148.391 byte (~41.15 MiB).
- Quality report: 18 dettagli, 17 inquadrature whole, 6 push, 8 reveal; 5 opere con multipli dettagli, 2 con tre dettagli, 6 che iniziano dal quadro intero. Contatto regia allegato, H264/AAC e durata controllati; **success tecnico NON garantisce valutazione estetica perfetta**.
- A differenza di V1–V4, la V5 introduce un limite zoom in base ai pixel sorgenti, evita macro estremi su immagini sfocate e conserva accuratamente i colori. Può diminuire la spettacolarità degli zoom quando i master sono piccoli: è una scelta a favore della qualità museale.
- Git branch `backup-artvision-v4-prima-cinema-universal-v5-2026-10-20`, precedenti motori e workflow narrati conservati.
- FUTURI ARTISTI: costruire e verificare prima un piano soggetti e dettagli specifico; attualmente la mappa esplicita implementata per V5 è di Van Gogh. Non dichiarare altri artisti supportati automaticamente se il piano non è stato preparato.


## 20/10/2026 — NUOVA REGIA CINEMATOGRAFICA V6 DOPO CRITICA SEVERA ALLA V5

**PREFERENZA AGGIORNATA DELL'UTENTE:** V5 è considerata una regressione: slideshow con quadri piccoli su nero, foto piatte, troppo tempo per opera. I riferimenti riconsegnati sono `No-Cuesta-Saber-fdown.net.mp4` e `Enfermedad-cromtica-fdown.net.mp4`. Sono SOLO riferimenti visivi, NON riutilizzare video/audio/loghi. L'utente vuole **un unico film vendibile e internazionale senza narrazione**, con introduzione elegante sempre uguale (nome artista + piccolo MUSIC BY), musica strumentale reale, fotografia museale, materia pittorica spettacolare, ritmo variabile, immagine quasi sempre pieno schermo e regia umana studiata. Non confondere tanti effetti con qualità.

**Soluzione indipendente V6**:
- Script: `modules/artvision/director_cinema_v6.py`.
- Guida: `modules/artvision/REGIA_CINEMA_V6.md`.
- Fonti: `modules/artvision/export_v6_assets.py`, scaricate 26 immagini museali autentiche ad alta risoluzione + brano `Dreams Become Real` (Kevin MacLeod, CC BY 4.0, full attribution in post description).
- Workflow separato: `.github/workflows/artvision-cinema-v6.yml`; NON toccare il workflow originale per libri/narrati o ArtVision V1–V5.
- Prima regia V6 Van Gogh: film 150 sec, 19 dipinti selezionati, 55 inquadrature curate a mano, 5 movimenti tematici, per lo più close-up verticali full-bleed, 2.2–4 sec per shot. Niente split-screen, nero invadente, foto AI inventate, sottotitoli o effetti compulsivi. Alcuni “whole” solo come pause deliberate su sfondi cromatici ricavati dal dipinto.
- **COLLAUDO LOCALE COMPLETO SUCCESS**: `ARTVISION_VAN_GOGH_CINEMA_V6.mp4` generato, MP4 finale ricompresso 1080×1920, H.264/AAC, durata verificata ~150s, audio normalizzato circa -17.3 dB medio, picco -1.4 dB senza clipping, ~83MB. 19 fonti CC0 documentate e manifesto dei diritti, 55 scelte e motivazioni nello storyboard; pacchetto completo creato e consegnabile.
- Il workflow GitHub V6 è stato predisposto per repliche future, ma il primo render era locale: **non indicare una run GitHub V6 come riuscita se non testata**.
- Branch backup precedente V5: `backup-artvision-v5-prima-regia-cinema-2026-10-20`.
- **Non proclamare WOW universalmente riuscito**: convalidare gusto finale dell'utente prima di rendere V6 default globale; migliorare su base feedback senza cancellare le versioni.
- **Per artisti nuovi**: creare un piano di regia dedicato con 15–25 riproduzioni valide, una vera colonna sonora differente e foci motivati (vietato riciclare le coordinate Van Gogh), poi render con lo stesso motore e licenze verificate.
