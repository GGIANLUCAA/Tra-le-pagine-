# TRA LE PAGINE — STUDIO WEB V9
**Interfaccia mobile vera, add-on di V3–V8, 20 ottobre 2026.**

Repository: https://github.com/GGIANLUCAA/Tra-le-pagine-

## COSA ESISTE DAVVERO
Il nuovo pannello web senza framework ha un layout mobile, navigazione, una PWA installabile, progetto video salvabile nel browser, generatore di brief per ChatGPT Plus, visualizzazione reale degli episodi e delle recenti run GitHub, link ai download degli Artifact e comandi per i workflow:
- V6: storyboard e pianificazione.
- V7: ricerca immagini/video, con Openverse o Pexels.
- V8: piano e preparazione scene (Gate 1 obbligatorio).
- V5: render MP4, che richiede ancora immagini premium complete e il segreto Google configurato.

**La voce predefinita Google Gemini e il codice di tutti i vecchi motori non sono modificati.** Nessun nuovo servizio di sintesi. Il sito non spende crediti AI per aprirsi e leggere lo stato pubblico.

**Due livelli di funzionamento distinti:**
1. **Pannello GitHub Pages, senza login nell'app:** episodi e run sono letti dal repository pubblico via GitHub REST; puoi creare brief locali; i pulsanti di produzione aprono il corrispondente workflow GitHub per eseguirlo tramite il tuo account. È utilizzabile, ma non invia richieste direttamente a GitHub.
2. **Pannello Cloudflare Worker, dopo configurazione OAuth:** stesso sito, stesso dominio del backend, GitHub login e chiamate sicure all'API per avviare workflow. Nessun token GitHub nel JavaScript visibile. Attivazione manuale obbligatoria da account Cloudflare e GitHub.

## SCELTA A — ATTIVAZIONE IMMEDIATA SU GITHUB PAGES (GRATUITA)
Apri dal telefono [il tuo repository](https://github.com/GGIANLUCAA/Tra-le-pagine-) e:

1. Tocca **Settings** (su Android potresti dover aprire il browser in **Sito desktop**).
2. Apri **Pages** sotto **Code and automation**.
3. In **Build and deployment → Source** seleziona **Deploy from a branch**.
4. Scegli **Branch: main**, **Folder: /docs**.
5. Premi **Save**. GitHub avvia il rilascio.
6. Nella stessa pagina **Pages** comparirà l'URL reale della tua applicazione: usa quello indicato da GitHub, non un indirizzo indovinato.
7. Apri l'URL con Chrome su Android; menu Chrome **⋮ → Aggiungi alla schermata Home** oppure **Installa app** se mostrato.

**Risultato:** interfaccia web effettiva, collegata in lettura al repository. Per avviare una produzione senza OAuth, ti apre GitHub Actions, dove premi **Run workflow**. Nessun token né segreto da inserire nel pannello pubblico.

Perché `/docs`? È una sorgente supportata nativamente da GitHub Pages, senza bisogno di Cloudflare, nuove API o build complicate.

## SCELTA B — PULSANTI DIRETTI CON CLOUDFLARE E GITHUB OAUTH (FACOLTATIVA)
**Cosa aggiunge:** avvii i workflow dai pulsanti **dentro** Tra le Pagine, senza dover aprire la schermata Actions. Il backend è nel file `worker/index.mjs`, il deploy nel file `wrangler.toml`.

### 1. Crea l'app Cloudflare dal telefono
- Accedi su [Cloudflare dashboard — Workers & Pages](https://dash.cloudflare.com/).
- **Workers & Pages → Create application → GitHub** (o **Import a repository**, secondo l'interfaccia).
- Consenti il collegamento a GitHub e seleziona **GGIANLUCAA/Tra-le-pagine-**, branch **main**. Non è necessario creare un secondo repository.
- Se richiesto, nome progetto **tra-le-pagine-studio**, uguale a `name` in `wrangler.toml`.
- Root directory: `/` (root del repository).
- Build/deploy command, se richiesto: `npx wrangler deploy`.
- Premi **Save and Deploy**, poi apri l'indirizzo HTTPS `*.workers.dev` assegnato al tuo Worker.

**Non inventare l'URL:** Cloudflare lo mostra nel pannello una volta creato il Worker.

### 2. Crea un'app OAuth GitHub dedicata
- Apri [GitHub → Developer settings → OAuth Apps](https://github.com/settings/developers) e scegli **New OAuth App**.
- Nome: `Tra le Pagine Studio`.
- Homepage URL: **l'URL esatto** `https://<indirizzo-assegnato-da-cloudflare>`.
- Authorization callback URL: **lo stesso URL** seguito da `/auth/callback`.
- Salva. GitHub fornisce `Client ID`; scegli **Generate a new client secret** per ottenere `Client secret`.

**Nota sui permessi:** l'OAuth App usa attualmente lo scope GitHub `repo`, più ampio di Actions:write e capace di consentire accesso anche a repository privati. È una limitazione del tipo OAuth App; il backend limita l'uso applicativo ai soli workflow ammessi e all'utente proprietario, ma non riduce l'ampiezza del token OAuth. Se preferisci la superficie di autorizzazioni minima, usa la modalità GitHub Pages guidata finché non viene sostituita dall'autenticazione tramite GitHub App con permessi granulari.

Se il modulo GitHub OAuth propone **Expire user authorization tokens**, considera che il backend V9 supporta la scadenza della sessione ma **non** il rinnovo dei token: quando scade, dovrai autenticarti di nuovo. Non è necessario disabilitare la scadenza.

### 3. Salva i segreti nel Worker (NON SU GITHUB PUBBLICO)
Nel pannello Cloudflare seleziona il tuo Worker → **Settings → Variables and Secrets** (la posizione varia secondo UI) e aggiungi come **Secrets**:
- `GITHUB_CLIENT_ID` → Client ID dell'app OAuth creata.
- `GITHUB_CLIENT_SECRET` → Client secret dell'app OAuth.
- `STUDIO_SESSION_SECRET` → un segreto **casuale, lungo almeno 32 caratteri**, generato con un password manager affidabile. Evita frasi semplici.

Non scriverli nei file del repository, dentro ChatGPT o in una schermata pubblica.

Una volta salvati, visita il dominio **workers.dev** ed entra da **Impostazioni → Accedi con GitHub**. Autorizza soltanto se scope e titolare del servizio corrispondono a quelli che ti aspetti.

Quando il tuo utente GitHub (GGIANLUCAA) autorizza, il Worker conserva il token in un cookie cifrato AES-GCM, HttpOnly, Secure e con durata massima di otto ore. Il browser non ha mai accesso in chiaro al token. I comandi accettati sono solo V6/V7/V8/render e non permettono nomi di workflow arbitrari. Il render Google e la preparazione V8 richiedono conferma separata.

**Non usare questa seconda configurazione dal dominio GitHub Pages:** il backend deve essere ospitato **allo stesso dominio** della web app Cloudflare, per evitare cookie di terze parti e vulnerabilità CORS.

### 4. Costi e limiti
- Github Pages gratis per repository pubblico idoneo.
- Cloudflare Workers piano gratuito soggetto alle proprie quote e ai limiti di CPU/risorse.
- Github Actions pubblico senza costi aggiuntivi standard per minuti dei runner ordinari, secondo policy GitHub; storage Artifact e altri servizi possono avere restrizioni e limiti.
- Google Gemini TTS usa la sua chiave già configurata in GitHub; limiti o costi Google rimangono indipendenti.
- ChatGPT Plus **non fornisce automaticamente credito API OpenAI**. Il pulsante "Prepara con GPT" copia un brief e apre ChatGPT: incolli il testo usando il tuo abbonamento, senza API fatturate separatamente.
- Non si accede a ChatGPT sfruttando cookie o sessioni rubate, né si automatizza il client web in violazione delle condizioni.

## COSA PUOI FARE DA ANDROID (IN ENTRAMBE LE MODALITÀ)
- **Panoramica:** vedere episodi e run recenti, collegamento a GitHub.
- **Nuovo video:** scrivere idea/titolo, scegliere formato e durata; salvare una bozza **sul tuo browser**; copiare un brief in ChatGPT. La bozza non crea ancora un nuovo episodio GitHub.
- **Episodi:** scegliere un episodio già presente; aprire o avviare storyboard V6, piano V8, preparazione e montaggio MP4.
- **Archivio:** lanciare ricerche Openverse e Pexels V7, **importare un elemento tramite ID** mantenendo uguali fonte e tipo, poi verificare gli artifact nelle run GitHub. I media importati non vengono montati automaticamente.
- **Produzioni:** vedere workflow recenti, stato e link ufficiali ai pacchetti disponibili.
- **Impostazioni:** controllare lo stato della connessione, conservazione voce Google, eliminare i brief locali.

## COSA MANCA ANCORA PER LO STUDIO AUTOMATICO COMPLETO
**Non scambiare interfaccia funzionante per un generatore autonomo end-to-end.**
- Il testo di GPT non viene inviato automaticamente dal sito al repository. Le bozze locali non creano da sole i file `testo.txt`, `scene_cues.json` e `metadata.json`.
- L'Orchestratore V8 oggi prepara le immagini e ne verifica la compatibilità, ma non avvia autonomamente il vecchio renderer su un episodio nuovo.
- Non c'è ancora upload di file personali privati, né archiviazione persistente server-side degli asset.
- La sezione nuova storia usa ChatGPT come strumento esterno: nessun accesso diretto al modello dall'app senza integrazione ufficiale autorizzata.
- I due Gate editoriali richiedono una verifica umana vera; il backend valida la conferma, non la qualità della storia.
- Questo progetto **non pubblica automaticamente sui social**.

## ARCHITETTURA E SICUREZZA
```text
Xiaomi Android
 ├─ GitHub Pages /docs (modalità lettura + lanci guidati)
 └─ oppure Cloudflare Workers (stessi file statici + backend OAuth)
       └─ GitHub OAuth → backend edge → GitHub Actions dispatch
                        ├─ Storyboard V6
                        ├─ Archivio media V7
                        ├─ Orchestratore V8
                        └─ Renderer storico V5 (Google Gemini + FFmpeg)
```

- UI: `docs/index.html`, `docs/styles.css`, `docs/app.js`, icona e manifest PWA.
- Backend: `worker/index.mjs`; segreti esclusivamente nell'account Cloudflare.
- Deploy Cloudflare: `wrangler.toml`.
- Controlli: `tests/test_studio_web_v9.mjs`, `.github/workflows/studio-web-v9-check.yml`.
- Nessun cambiamento ai file di V3–V8, alle immagini già approvate o al motore Google.
- Non caricare materiale personale nel repository GitHub pubblico.
- Gli artifact possono essere accessibili ad altri utenti se il repository e i log sono pubblici: niente dati sensibili nelle produzioni.

## Fonti ufficiali
- [GitHub Pages: Deploy from branch /docs](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Actions workflow dispatch](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)
- [Cloudflare Workers GitHub Builds](https://developers.cloudflare.com/workers/ci-cd/builds/)
- [Cloudflare Workers static assets](https://developers.cloudflare.com/workers/static-assets/)
- [Cloudflare Secrets](https://developers.cloudflare.com/workers/configuration/secrets/)
- [GitHub OAuth App setup](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app)
- [ChatGPT e API: fatturazione separata](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform)
