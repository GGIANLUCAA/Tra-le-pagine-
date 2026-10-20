# ARTVISION — arte autentica in video, senza voce

## VERSIONE APPROVATA — CINEMA V6 (20 ottobre 2026)

**La regia Cinema V6 è ora il riferimento artistico principale confermato dall'utente.** Quando viene richiesto un nuovo video d'arte, NON usare automaticamente gli esperimenti V1–V5 e NON riproporre slideshow, fondali neri con immagini piccole, zoom sistematici o montaggi tutti uguali.

Leggere prima **[VERSIONE_APPROVATA_CINEMA_V6.md](VERSIONE_APPROVATA_CINEMA_V6.md)** e **[REGIA_CINEMA_V6.md](REGIA_CINEMA_V6.md)**, poi usare il motore **`director_cinema_v6.py`** e il workflow dedicato **`artvision-cinema-v6.yml`**. Per artisti diversi da Van Gogh occorre uno storyboard nuovo specifico: il motore corrente contiene ancora la regia personalizzata per Van Gogh.

**Il vecchio `artvision-render.yml` parte ancora con V5 per compatibilità tecnica: NON equivale al nuovo standard approvato.** Seguire il workflow V6 dedicato finché non si predispone un nuovo artista. Conservare intatti libri narrati, vecchi motori e backup. Una sola versione filmica per artista, salvo diversa richiesta.

Modulo indipendente di `Tra le Pagine`. **Non modifica** `render-v3.yml`, Gemini, libri narrati o V5.

## Stato (20 ottobre 2026)

La V1.3 è stata realmente collaudata (vedi esecuzioni in fondo). Dopo il feedback dell'utente è stata progettata una regia cinematografica V2, con modulo e workflow separati. Verificare i test V2 prima di attribuirle qualità finale.

## Accesso Android

1. Apri [ARTVISION - arte autentica](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/artvision-render.yml).
2. Tocca **Run workflow**.
3. Inserisci artista, durata (120-180 secondi), opere massime (6-24).
4. Tocca Run workflow e consulta l'esito della run.
5. Se la run risulta **Success**, apri **Artifacts** e scarica il pacchetto `ARTVISION_...`; estrai il file `ARTVISION_VIDEO.mp4`.
6. Controlla prima di pubblicare il file `OPERE_FONTI_E_DIRITTI.json`, `CREDITI_E_FONTI.txt` e le condizioni d'uso del materiale.

Non sono richieste chiavi Gemini né immagini AI. Il modulo usa Python, Pillow, NumPy, FFmpeg, API pubbliche e una musica sintetica *originale* algoritmica.

## Archivi attivi, esclusivamente con filtri restrittivi

- [Art Institute of Chicago API](https://api.artic.edu/docs/): `is_public_domain=true` e `image_id`, fonte IIIF, attribuzione artista esatta.
- [Cleveland Museum of Art](https://openaccess-api.clevelandart.org/): `share_license_status=CC0` e immagine presente; metadati attribuiti.
- [Met Collection API](https://metmuseum.github.io/): ricerca paginata `v1.1`, scheda opera `v1`, `isPublicDomain=true`, immagine disponibile.

Non usare automaticamente immagini di artisti contemporanei protetti. La classificazione dei metadati museali non sostituisce una verifica giuridica specifica, specialmente per normativa italiana sui beni culturali e diritti sulle fotografie.

## Prodotto

- `ARTVISION_VIDEO.mp4`: 720×1280, 24 fps, H.264, AAC, senza narrazione.
- `COPERTINA.jpg`: copertina coordinata.
- `CREDITI_E_FONTI.txt`, `OPERE_FONTI_E_DIRITTI.json`: collegamenti e tracciabilità.
- `DESCRIZIONE_SOCIAL.txt`, `MONTAGGIO.json`, `REPORT_PRODUZIONE.json`.

Il video mostra opere autentiche per intero con fondali sfocati derivati dalla stessa fotografia: niente completamento generativo o cambiamento dei colori dell'opera al centro. Transizioni volutamente sobrie; il montaggio usa zoom sottili e dissolvenze.

La musica è sintetizzata con oscillatori armonici in Python, senza registrazioni altrui. È un **prototipo musicale**, sostituibile in futuro con brani professionali muniti di licenza.

### Limiti del primo prototipo

- 720×1280 per evitare tempi CPU eccessivi; 1080×1920 arriverà dopo benchmark.
- Minimo 6 opere autentiche adatte, altrimenti non rende il video.
- Non pubblica sui social né attiva spese.
- GitHub ospita solo il codice: immagini in temporaneo e MP4 negli Artifacts con conservazione limitata.
- Non è ancora un'app con pannello web dedicato; GitHub Actions resta la UI da telefono.
- Nessuna quota giornaliera di video garantita: `REPORT_PRODUZIONE.json` consente di misurare i tempi e la quantità sostenibile.

## Esecuzione locale (Linux con FFmpeg)

```bash
python -m pip install numpy Pillow
python modules/artvision/artvision.py --artist "Vincent van Gogh" --duration 150 --max-works 16 --out output/artvision
```

Non avviare più esecuzioni concorrenti con gli stessi percorsi output. Per altri artisti usare cartelle separate. Prima della distribuzione social verificare i diritti e le condizioni musicali e delle immagini nel territorio e nella piattaforma di destinazione.

## Produzione da chat, senza clic su GitHub

Il file `modules/artvision/queue.json` è la **coda automatica**. Quando l'utente richiede un nuovo artista, il modello può aggiornare direttamente questo JSON con `request_id` univoco, `artist`, `duration`, `max_works`, `approved_for_render: true`, `publish: false`. Il workflow ArtVision V1.3 si avvia automaticamente al push della coda. Non toccare i workflow narrati e non pubblicare mai senza autorizzazione. La compilazione manuale `workflow_dispatch` resta disponibile per chi preferisce il telefono.

**Produzione verificata**: 20 ottobre 2026, run 3, 150,17 s, 16 opere, 24 scene, 720×1280, H.264 + AAC, nessuna API a pagamento; render riuscito. **Compressione ottimizzata verificata**: run 4, stesso filmato, MP4 da circa 14,7 MB, tempo totale 179 s. Link run: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39412319602 .

Se la coda contiene lo stesso artista ma si vuole un nuovo montaggio, modificare `request_id`. Se non ci sono almeno 6 opere con immagini e licenze adatte, il motore interrompe il rendering con errore comprensibile e non inventa opere.

**Test definitivo della coda autonoma**: [GitHub Actions run #6](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39412758541) terminata con successo, artifact `ARTVISION_6` da circa 15 MB. Il sistema può quindi creare nuovi video tramite semplice aggiornamento di `modules/artvision/queue.json`, senza premere manualmente Run workflow.


## NUOVA REGOLA PERMANENTE — REGIA CINEMA WOW V2 (20 ottobre 2026)

**Feedback vincolante dell'utente:** il video Van Gogh V1 è stato giudicato troppo simile a una sequenza di fotografie con dissolvenze. Non riproporre la V1 come qualità definitiva. Il modello di riferimento inviato è `Enfermedad-cromtica-fdown.net.mp4`: ritmo rapido, chiaroscuro, motivi che ritornano, focali e dettagli, fusione con la musica. **Non riutilizzare quel filmato o il suo audio.**

La nuova guida editoriale completa è [REGIA_CINEMA_WOW_V2.md](REGIA_CINEMA_WOW_V2.md), da leggere prima di ogni produzione; il file è parte permanente della memoria operativa del progetto.
**Moduli indipendenti:** `artvision.py` mantiene V1; `cinema_wow_v2.py` implementa regia cinema musicale; `artvision_cinema_run.py` è il nuovo orchestratore che importa gli archivi museali dalla V1.
**Nuovo default nel workflow:** `style: cinematic_wow`; per tornare alla V1 usare esplicitamente `style: museum_legacy`. La coda di produzione conserva lo stesso schema e può indicare `style` (se assente assume cinematic_wow).
**Importantissimo:** la sintesi musicale originale è sperimentale e NON deve essere presentata come equivalente a musica professionale selezionata. La visione del rendering finale e il feedback dell'utente sono indispensabili.
Per un episodio nuovo, conservare V1 e testare V2 su un provino di 20–30 secondi e poi sul video completo. Non attestare la qualità artistica senza ispezione del file.

**Backup prima delle modifiche V2:** `backup-artvision-v1-3-prima-regia-wow-2026-10-20`. Nessuna modifica ai motori narrati.


## Aggiornamento definitivo — REGIA ARMONICA V3 (20 ottobre 2026)

L'utente ha valutato V2 migliorata ma **ancora troppo movimentata**. Non usare mai effetti split-screen, doppio quadro diviso, pan casuale, zoom rapido e continuo o musica generativa improvvisata come impostazione ArtVision. Il secondo video campione (`No-Cuesta-Saber-fdown.net.mp4`) privilegia tempi di contemplazione: leggere il dipinto prima dei tagli.

**Nuovo preset raccomandato e workflow predefinito:** `style=harmonic_reveal` in `.github/workflows/artvision-render.yml`; codice `modules/artvision/harmonic_reveal_v3.py`. Ogni quadro deve prevedere un dettaglio significativo *scelto intenzionalmente* e motivato da una mappa per artista, seguito da zoom-out dolcemente rallentato e visione del quadro intero. Impostazioni precedenti `cinematic_wow` e `museum_legacy` restano recuperabili.

**Musica reale:** `Calmant` (Kevin MacLeod, pianoforte, CC BY 4.0, attribution obbligatoria). Sorgente e licenza verificabili: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100859 e https://creativecommons.org/licenses/by/4.0/ . V3 deve fallire quando non è disponibile una registrazione autorizzata: niente sintetizzatore fallback. La musica è soggetta a copyright, ma concessa in licenza gratuita con attribuzione.

**Guida prioritaria da leggere per ogni nuovo video:** [REGIA_ARMONICA_V3.md](REGIA_ARMONICA_V3.md). La sua mappa di dettagli è curata *per Van Gogh*, non per altri pittori. Per ogni nuovo artista aggiungere focali motivate e verificare opere e musica PRIMA di avviare la produzione; non copiare coordinate casuali. La pubblicazione resta sempre separata dalla produzione.
**Backup V2:** `backup-artvision-v2-prima-regia-armonica-v3-2026-10-20`.


## NUOVA PREFERENZA VINCOLANTE: ATELIER V4 · 20 ottobre 2026

L'utente apprezza V3 rispetto alle precedenti ma rifiuta la ripetitività di ogni quadro identico. **V4 è il preset preferito.** Ogni opera deve avere un piano artistico diverso: talvolta un dettaglio soltanto, talvolta 2/3, talvolta iniziare dall'opera completa e poi avvicinarsi. Per Van Gogh usare focali motivati come occhi, petali, alberi, gesti e prospettiva; per nuovi artisti rivedere tutte le coordinate, mai copiarle. Camera quasi ferma sui dettagli: il movimento non è fine a se stesso. Alternare forme narrative, tempi calmi e brevi tensioni; no split screen, no effetti ripetitivi. **1080×1920 Full HD** da riproduzioni originali, non millantare 4K reale. Piccolo titolo del brano e compositore nel video, attribution completa nella descrizione.

**Musica differente nei prossimi video**: utilizzare registrazioni autentiche licenziate; tenere `music_library.json` per storico delle ultime musiche e per scoprire nuove scelte adatte allo stile. Le licenze ufficiali vanno controllate: CC BY 4.0 richiede attribution visibile. Il numero di brani ricercati è maggiore del numero di download già collaudati.

Nuovo motore separato: `modules/artvision/atelier_v4.py` — selezione `style=atelier_v4` (default workflow); impostare `music` per ogni richiesta. V1, V2, V3 e i video libri restano invariati. Backup `backup-artvision-v3-prima-regia-atelier-v4-2026-10-20`. Linea guida completa: [REGIA_ATELIER_V4.md](REGIA_ATELIER_V4.md).

**Consegna futura**: GitHub Actions con coda `modules/artvision/queue.json`, nessuna pubblicazione automatica, collaudo MP4, audio, fonti, licenze e `quality_report_v4.py` (tavola visuale dei dettagli). La run V4 #11 si era fermata su un URL musicale inventato: file corretto ufficiale è `Evening Fall - Piano.mp3`, non `Evening Fall (Piano).mp3`. Controllare l'URL reale nel metadato di [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Evening_Fall_(Piano)_(ISRC_USUAN1100235).mp3) prima dei download. Non generare un brano finto come sostituto silenzioso.
