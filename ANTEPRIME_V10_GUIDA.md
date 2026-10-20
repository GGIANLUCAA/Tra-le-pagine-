# Tra le Pagine — Episodi e Anteprime V10
## Perché fino a ieri non c'erano video nelle schede?
Il pannello V9 mostrava solo i nomi delle cartelle; in `docs/` non erano pubblicati video MP4 né copertine reali. Gli MP4 prodotti vengono solitamente salvati negli **Artifact GitHub Actions**, non sul sito. Gli Artifact non sono URL stabili per lo streaming di un normale elemento HTML `<video>`.

Nell'attuale repository esistono 7 cartelle `episodes/`, ma **solo `01_scacchi` contiene l'archivio scene_premium.zip**. Gli altri episodi hanno principalmente materiale editoriale (copione, istruzioni, scene). Alcuni hanno `metadata.json` con `approved_for_render` o note di produzione: questo non garantisce che vi sia un MP4 ospitato su Pages.

## Come funziona la V10
- Una pagina **Episodi** con copertine vere, titoli e autori, quando i dati esistono.
- La scheda mostra chiaramente se ci sono immagini reali disponibili o **immagini mancanti**.
- **Apri anteprima** mostra una sequenza scorrevole delle fotografie reali recuperate dal repository, mai immagini simulate presentate come autentiche.
- La finestra consulta anche `scene_cues.json` per mostrare le descrizioni delle scene e capire il racconto.
- **Apri un MP4 dal telefono** permette di riprodurre localmente, direttamente nell'app, un file MP4/WEBM/MOV già scaricato o salvato sul tuo Android. Viene creato un `blob:` locale che viene eliminato alla chiusura.
- **Vedi video e download in GitHub Actions** apre le esecuzioni e gli Artifact per il download del file originale. Nei workflow storici, in genere scarichi lo ZIP, lo estrai da Android, poi selezioni il file MP4 nell'app.

La V10 non carica il video dal tuo telefono a GitHub o Cloudflare. **Non pubblica automaticamente MP4 su GitHub Pages**: un sito pubblico renderebbe pubblici quei video.

## Creazione delle copertine automatiche
Il nuovo script `tools/build_episode_previews_v10.py` apre gli ZIP e le immagini **già presenti nelle cartelle episodi**, produce mini-JPG e un `catalog.json`. Nessuna AI, niente API né chiamate a Gemini.
L'azione `episode-previews-v10.yml`, al primo push della nuova versione sul ramo main, produce le mini-copertine e prova a inserirle in `docs/previews/` con il GitHub Actions token, che richiede `contents: write`. Gli eventuali permessi del repository potrebbero impedirlo; in tal caso recupera l'Artifact `ANTEPRIME_EPISODI_V10`, oppure autorizza il workflow dalle impostazioni Actions. La pipeline non modifica i vecchi episodi.

**Prima produzione:** per `01_scacchi` saranno disponibili fino a cinque fotografie di scena. Per gli altri episodi non viene finta la presenza di illustrazioni o video che non esistono in repository.

## Dal telefono — come vedere il video
1. Apri https://ggianlucaa.github.io/Tra-le-pagine-/
2. Tocca **Episodi** e scegli **Apri anteprima**.
3. Quando sono disponibili, guarda le immagini reali e le descrizioni della regia.
4. Se vuoi vedere il vero MP4, premi **Vedi video e download in GitHub Actions** e apri una run video completata. Per l'episodio 01 c'è ad esempio una produzione storica V5 conservata nella [run #39171898138](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39171898138), con Artifact; la disponibilità può cambiare per scadenza.
5. Scarica l'Artifact, estrai l'eventuale ZIP e apri **Apri un MP4 dal telefono** nell'app. La riproduzione è locale e privata.

### Possibili sviluppi
- Biblioteca **privata**, permanente, dei video completi collegata all'app (Cloudflare R2 o un provider gratuito idoneo) con login, metadati ed accesso autorizzato.
- Pubblicazione **esplicitamente approvata** di brevi teaser su Pages, se desideri anteprime cliccabili da chiunque.
- Collegamento automatico delle run agli episodi attraverso metadati macchina, senza affidarsi a nomi ambiguamente simili.
- Controllo qualità delle anteprime su mobile e stato esatto `preparato / montato / disponibile / non disponibile`.

## Sicurezza
Non cambiare motore, voce Google Gemini o episodi originali. La V10 non modifica `render.py`, `gemini_voice.py` e `episode_v3.py`, non avvia sintesi né montaggi, non carica file personali nel repo pubblico. Solo materiale già pubblico viene usato per le miniature.

**Nota:** le immagini o video esistenti sono soggetti ai rispettivi diritti. Il loro uso privato non autorizza automaticamente la pubblicazione su GitHub Pages. L'estrazione delle miniature da un repository già pubblico non equivale a un controllo dei diritti.
