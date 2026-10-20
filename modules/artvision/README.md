# ARTVISION — arte autentica in video, senza voce

Modulo indipendente di `Tra le Pagine`. **Non modifica** `render-v3.yml`, Gemini, libri narrati o V5.

## Stato (20 ottobre 2026)

Motore di partenza creato; test reale su GitHub Actions da verificare tramite workflow. La prima puntata dimostrativa prevista è **Vincent van Gogh, 150 secondi**, immagini autentiche provenienti da API museali. Non affermare che è stata prodotta se manca il report riuscito.

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
