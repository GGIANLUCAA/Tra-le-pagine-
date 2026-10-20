# ArtVision — PROCEDURA PERMANENTE / RICETTA DI PRODUZIONE

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
