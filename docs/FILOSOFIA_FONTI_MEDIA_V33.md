# Filosofia fonti e API — V33 (regola permanente approvata 25/10/2026)

**Una regola unica**, nella configurazione `config/editorial_rules.json > media_source_priority`, applicata ai **nuovi** contenuti prodotti con il repository e i suoi agenti: Arte, Critico, Libri, Controluce, Visual Music/HyperLumen. Le istruzioni attive hanno precedenza sulle guide storiche. L'utente può motivatamente scegliere un'alternativa per un singolo video; non cambiare le regole globali senza una nuova approvazione.

## Obiettivo e filosofia non negoziabile

Qualità narrativa + fedeltà alle immagini vere + continuità dei personaggi + uso intelligente del materiale già buono + zero abbonamenti attivati di nascosto + utilizzo solo da Android.

**Prima la scena, poi il servizio**: non riempire un video con immagini stock genericamente belle; cercare l'immagine corretta per ogni frase oppure crearne una originale, senza improvvisare. Scene differenti devono sembrare realmente differenti; no mosaici usati per fingere tante illustrazioni, no teste/mani tagliate, no sovrapposizioni fra quadri. Scegliere quantità e stile sul soggetto, non per un numero prefissato. Conservare copertina, post, voice, musica, regia e prove di licenza nel dossier.

## Gerarchia operativa per tutte le nuove produzioni

1. **Riuso dei materiali già approvati:** controllo hash, licenza, identità dei personaggi, idoneità alla nuova scena e qualità dell'originale. Non riciclare materiale inadatto soltanto per risparmiare.
2. **Ricerca e studio del contenuto:** libro/opera/evento/fonti vere, pubblico di riferimento, storyboard scena-per-frase, fotogramma 0/1/3/5/7, scene difficili e visual bible. Il dato su pubblico deve essere verificabile o chiaramente qualitativo.
3. **Se è un'opera d'arte/documento reale:** privilegiare fonti autentiche già verificate, musei e archivi con diritti verificati (Wikimedia/Openverse V7, Met/Chicago/Cleveland/altre fonti del catalogo V2 quando effettivamente collegate). Nessuna sostituzione AI di un quadro originale presentata come autentica.
4. **Per fotografie, ambienti e clip brevi pertinenti:** consultare Openverse e **Pixabay**, con ricerche mirate/manuali e revisione dei risultati. Pexels solo se la chiave è effettivamente disponibile. Un catalogo documentato non significa che il connettore sia già funzionante.
5. **Per azioni inventate, scene letterarie specifiche e personaggi ricorrenti:** creare illustrazioni originali coerenti se lo stock non rappresenta davvero il racconto. AI Horde è il primo generatore **sperimentale**: max 3 scene per prova; usare modello effettivamente disponibile e con licenza adatta, seed e riferimenti di personaggi; archiviare il risultato. Non dichiarare verificata una produzione giornaliera illimitata. ComfyUI/Kaggle/Z-Image sono candidati, **non integrati**.
6. **Controllo prima del render:** corrispondenza fra narrazione/frase e scena; stessa identità e abiti quando previsti; composizione e formati, niente crop di volti; fonte, licenza, autore, eventuali modifiche, hash, credito e review. Se manca un asset necessario: fermare il render e riparare quella scena, non usare riempitivi casuali.
7. **Rendering/consegna:** Gacrux resta la voce per i format narrati, montaggio precedente preservato. Musica con licenza della registrazione verificata, mix sotto la voce, MP4 con audio effettivo, copertina, social post e scaricamento controllato da Android. Nessuna pubblicazione implicita.

## Ordine per genere: la fonte giusta conta più della classifica astratta

| Format | Prima opzione | Seconda | Vietato |
|---|---|---|---|
| **Libri** | Asset originali coerenti già validati; nuove illustrazioni originali per azioni esatte | Archivi/stock **solo** quando raccontano davvero la scena | Libro cambiato, creatura/oggetto assente nel racconto, protagonista irriconoscibile |
| **ArtVision Cinema** | Opera autentica in alta qualità (museo, Commons, archivio verificato) | Asset autentico già approvato e suoi dettagli | Finta riproduzione AI presentata come quadro vero, trasparenze fra quadri |
| **ArtVision Critico** | Stesso standard autenticità, dettagli sincronizzati alla voce | Immagini d'archivio complementari e pertinenti | Critico senza voce, dettaglio inventato |
| **Controluce** | Fonti documentali primarie/indipendenti | Archivio legale, stock per contesto, ricostruzioni visibilmente dichiarate | Foto AI presentate come prove reali |
| **Musica / HyperLumen** | Audio e dati musicali con diritti, geometria e sincronizzazione verificata | Riutilizzo stili e asset già riusciti | Fingerprint/recording non autorizzate, animazioni non sincronizzate |

## Segreti GitHub — nomi ESATTI / cosa è realmente integrato

- **Pixabay**, nome ufficiale con **y**: il secret GitHub già visibile è `PIXABAY`. Il bridge `src/free_sources_bridge_v1.py` lo utilizza; `PIXABAY_API_KEY` è solo alias di compatibilità. `PRIXIBAY2` è probabilmente un refuso, **NON** viene usato né cancellato automaticamente; non inviare i valori in chat.
- `AIHORDE_API_KEY` è il secret per la prova image V1. `AIHORDE_API_KEY_2` è conservato ma non alternato automaticamente per aggirare quote/limiti; presenza da verificare tramite `status`, perché i nomi erano troncati negli screenshot.
- `GEMINI_API_KEY` serve al motore TTS attuale: eventuali quote API Gemini e il relativo costo sono indipendenti da ChatGPT Plus; non sostituire Gacrux senza richiesta.
- `OPENROUTER2` è riconosciuto dal report di stato, ma **non collegato** a richieste di inferenza; scegliere solo modelli `:free` e verificare condizioni e quota prima di un'eventuale integrazione.
- Openverse/Wikimedia e altre sorgenti pubbliche senza key sono prioritarie per ricerca e materiale autentico; le 45 sorgenti V2 sono catalogate, non tutte implementate.
- I secret si inseriscono esclusivamente in GitHub Actions Settings → Secrets; non vanno pubblicati, mostrati nei log, screenshot o copiati nei prompt.

## Sicurezza, costo, quote, diritti

- **Non pagare automaticamente**: tetto autorizzato delle nuove integrazioni = 0 €, mai assumere che servizi con free tier restino senza limiti. TTS Gemini già in uso resta soggetto a quota separata, da monitorare; nessuna nuova spesa autorizzata da questa regola.
- **Pixabay API:** una ricerca umana mirata e cache per 24 ore prima di ripetere la stessa query. La ricerca V1 esistente è manuale e NON garantisce ancora cache persistente tra run: non lanciarla ripetutamente con la stessa query. Vietate query massive e download sistematici. Mostrare la fonte Pixabay nei risultati. Non fare hotlink permanente. Documentazione: https://pixabay.com/api/docs/.
- AI Horde: usare la coda e rispettare rate limit/attese; su 429/404 interrompere, loggare stato e scegliere fallback consentito. Non ruotare account per eludere limiti, non inserire prompt sensibili.
- Non è permesso usare immagini di Google, siti social o musei solo perché visibili: verificare i diritti della riproduzione e l'uso commerciale dell'asset.
- Metadati di ogni asset: `asset_id`, `source_kind`, `provider`, `source_reference`, `choice_reason`, `scene_match_note`, `rights_review`, `scene_relevance`, `visual_review`. Richiesta una motivazione quando si rinuncia al riuso dell'asset valido.
- Tutti i nuovi progetti V13 includono `editorial_plan.media_sourcing`; `video_director_v13.check` blocca un progetto con asset visivi non documentati. La verifica tecnica delle dichiarazioni **non equivale a validazione artistica automatica**.
- Salvare file originali, diritti, seed/model/versione per AI, hash, crop, frasi/cue e risultati in memoria persistente (non solo Artifact GitHub a scadenza). Riutilizzare senza rigenerare solo materiali davvero adatti.

## Cosa è stato effettivamente automatizzato

**Già operativi:** regola unica in `config/editorial_rules.json`, check V13 su provenienza/pertinenza/revisioni, bridge Pixabay/Openverse manuale e prototipo AI Horde singolo.

**Da sviluppare/validare:** orchestrazione automatica di tutte le 45 fonti; cache Pixabay cross-run; selezione semantica delle migliori immagini; grandi batch di illustrazioni AI gratuite; archiviazione permanente e consegna nel sito. Non dire che una guida o un nuovo campo JSON li rende già automatici.

## Regola di trasferimento tra chat

Le istruzioni GitHub sono vincolanti per i workflow e gli agenti **che leggono il repository**. Una chat indipendente non carica automaticamente i file GitHub. Per replicare gli stessi default, inserire un breve riferimento a `AGENTS.md`, `docs/REGOLE_ATTIVE.md` e questa guida nelle istruzioni del progetto ChatGPT. Le chat senza accesso dichiarano il limite e non inventano la lettura.

Regola approvata dall'utente il 25/10/2026; la revisione modifica i nuovi progetti e non riscrive i master approvati.
