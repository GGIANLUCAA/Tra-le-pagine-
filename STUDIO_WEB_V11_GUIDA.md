# TRA LE PAGINE — STUDIO WEB V11
## Produci, controlla, guarda e scarica dal telefono

**Stato:** estensione modulare di V3–V10. Voce Google Gemini TTS invariata; renderer FFmpeg storico ancora utilizzato. Nessun vecchio episodio eliminato.

### COSA FUNZIONA NELLA WEB APP
L'interfaccia principale https://ggianlucaa.github.io/Tra-le-pagine-/ ha:
- **Crea video:** modulo breve con titolo, descrizione, tipo e durata. Il pulsante **Produci video (BETA)** richiama `studio-autopilot-v11.yml`; richiede consenso per le quote e, su GitHub Pages, apertura del workflow GitHub con i dati da ricopiare. Se l'app è ospitata sul Worker con OAuth configurato può chiamare il workflow direttamente.
- **Videoteca:** legge le Release GitHub con tag strettamente `tlp-video-<slug>-<run-id>` e MP4 autorizzati; ogni video ha riproduzione, download e copertina reale ricavata dal filmato. Prima che un video venga pubblicato, la videoteca può essere vuota: non mostra esempi falsi.
- **Episodi:** se un episodio possiede una Release, compare **Guarda il video**. Negli altri casi resta l'anteprima immagini V10 / storyboard.
- **Produzioni:** lista di workflow reali GitHub con collegamenti a esecuzioni e relativi Artifact.
- **Strumenti avanzati:** immagini V7, storyboard V6, regia V8 e impostazioni, senza sovraccaricare la schermata principale.

### NUOVI VIDEO: COSA FA LA BETA
Una volta confermata la quota e avviato `studio-autopilot-v11.yml`:
1. Google Gemini genera copione originale italiano e descrizioni delle scene; **non usa l'abbonamento ChatGPT Plus come API**.
2. Cerca immagini realmente presenti in Openverse/Wikimedia, con filtri di licenza V7.
3. Prepara gli asset premium e controlla tutto con il vecchio `episode_v3.py`.
4. **Solo se tutte le immagini richieste sono presenti**, esegue la narrazione originale con Google Gemini TTS e il montaggio storico FFmpeg.
5. Consegna un MP4 e gli altri output in `VIDEO_V11_DA_APPROVARE` (Artifact GitHub). **NON lo pubblica sul sito automaticamente.**

**Limitazioni reali:** non è ancora collaudato un ciclo completo dal titolo all'MP4 con le API Google reali; i test sono offline. Una ricerca fotografica senza immagini valide ferma il processo, non produce disegni brutti per finta. Per evitare false cronache, la beta automatica accetta **libri, fiabe e racconti social**, NON cronaca o documentari che richiedono verifica di fonti.

Attenzione: i titoli, le descrizioni, i log e i file Artifact di workflow in un repository pubblico potrebbero essere accessibili a terzi. Non usarla con dati privati.

### RENDERE IL VIDEO DISPONIBILE NEL SITO
Quando un MP4 è stato prodotto e hai visionato il video:
1. Apri **Videoteca**, seleziona l'episodio o **Nuovo video BETA** e inserisci l'ID della produzione (run ID).
2. Premi **Aggiungi alla videoteca**.
3. Conferma ESPRESSAMENTE che il filmato diventerà **pubblico**, riproducibile e scaricabile da tutti.
4. L'azione `pubblica-video-v11.yml` verifica il completamento della run, il pacchetto MP4, ne estrae un fotogramma per la copertina e crea una GitHub Release pubblica.
5. Ricarica **Videoteca**: appariranno **Guarda** e **Scarica MP4**. Per alcuni browser, se GitHub impedisce lo streaming diretto, sarà disponibile l'apertura/download del file originale.

Su GitHub Pages, senza login OAuth nel sito, il pulsante apre il workflow **Pubblica Video V11** di GitHub; devi compilare il modulo lì. Dal Worker privato autorizzato GitHub, il comando viene eseguito direttamente nel sito. La conferma riguarda la pubblicazione PUBBLICA e non può essere sostituita da approvazione generica.

Per i tuoi video **personali e non pubblici**, NON usare la pubblicazione via Releases: serviranno un archivio privato Cloudflare R2 e autenticazione del sito. GitHub Pages è pubblico e NON può proteggere da solo video riservati.

### RENDER CON LA VECCHIA VOCE GOOGLE
La sezione **Episodi** continua a richiamare il renderer `render-v3.yml` e mantiene tutte le immagini e i metodi precedenti. Nulla è stato riscritto. L'API voce Google richiede la precedente `GEMINI_API_KEY` configurata nei GitHub Secrets; può avere limiti o costi Google indipendenti da ChatGPT Plus.

### COSA NON È ANCORA GARANTITO
- Che ogni idea venga illustrata con 8–12 fotografie coerenti trovate gratis; se non trova immagini la beta non procede alla sintesi.
- Che il modello di testo o la voce siano sempre accessibili alla tua quota Google.
- Che GitHub Releases accetti lo streaming inline in tutti i browser Android: è presente fallback download.
- Che lo Studio Pubblico GitHub Pages possa lanciare Action direttamente senza autorizzazione: per il vero click interno serve il backend OAuth Cloudflare già predisposto in V9, con credenziali da configurare.
- La memorizzazione privata permanente; la videoteca GitHub Releases è pubblica.
- La produzione automatica di cronaca con verifica editoriale autonoma.

### COSTI E QUOTE
- Web GitHub Pages: gratis in un repository pubblico nei limiti d'uso.
- Workflow GitHub Actions: nei limiti e condizioni del piano.
- Openverse/Wikimedia: nessun costo per l'accesso pubblico nei limiti dei servizi.
- Google Gemini (testo + voce): possibili costi, limiti o quota gratuita a seconda del progetto/chiave.
- Non è necessario acquistare una nuova API OpenAI. **ChatGPT Plus non comprende automaticamente le API tradizionali**.

### APP MOBILE — PASSI SEMPLICI
Apri https://ggianlucaa.github.io/Tra-le-pagine-/#nuovo, inserisci la tua idea, seleziona `libri`, `fiabe` o `social` e premi **Produci il video (BETA)**. Conferma solo se intendi consumare la quota Google. Se sei su GitHub Pages, il sito ti porterà al workflow dove devi ricopiare i dati, confermare e premere Run workflow. La produzione può richiedere diversi minuti.

Da **Produzioni** controlli il risultato e scarichi `VIDEO_V11_DA_APPROVARE`. Dopo aver guardato il filmato, puoi scegliere se pubblicarlo dalla Videoteca oppure conservarlo per uso personale senza renderlo accessibile dal sito.

### DOCUMENTAZIONE / TEST
- Interfaccia: `docs/index.html`, `docs/app.js`, `docs/styles.css`, `docs/videoteca_v11.js`.
- Scrittura e immagini: `src/studio_autopilot_v11.py`.
- Workflow beta: `.github/workflows/studio-autopilot-v11.yml`.
- Pubblicazione esplicita: `.github/workflows/pubblica-video-v11.yml`.
- Protezione autenticazione: `worker/index.mjs` con whitelist e conferma.
- Test: `tests/test_studio_autopilot_v11.py`, `tests/test_videoteca_v11.mjs` e regressione Chrome mobile.
