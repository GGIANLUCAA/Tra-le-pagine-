# Visual Boards V34 · Zero AI per scheda
**Stato: prototipo proposto e testabile, non ancora integrato nel Video Library Studio live.**
Decisione editoriale: richiesta esplicita 26 ottobre 2026 di adottare le schede grafiche in tutti i video senza chiamate AI aggiuntive per ciascuna scheda.

## Perché
Generare 20 video × 4 immagini di riepilogo con un modello di generazione consumerebbe almeno 80 richieste. Questa alternativa usa **il dossier V13 già compilato**: testi, copertina, anteprime degli asset, fonti e verifiche. Non altera i master né la filosofia V33.

## Output del prototipo
- `CONCEPT_BOARD.png`: scheda iniziale tipo pitch; copertina già esistente, promessa, durata, regia, prime scene.
- `PRODUCTION_BOARD.png`: dati tecnici, fonti visuali, status revisioni con "DA VERIFICARE" quando necessario.
- `SCENE_CONTACT_SHEET.jpg`: tutte le scene registrate, con miniatura di asset esistenti e funzione narrativa.
- `BOARD_MANIFEST.json`: tracciabilità dell'origine (hash del PROJECT_V13.json), file mancanti, revisioni non complete.

**Release Pack** non deve duplicare il master: usare `docs/VIDEO_LIBRARY_DOSSIER_V1.md` e ZIP a richiesta.

## Funzionamento
Il generatore usa solo **Pillow**, carica esclusivamente immagini locali nella cartella della scheda, non invoca API esterne e non genera nuove immagini narrative. Una stessa illustrazione può essere usata per più tagli del video; la contact sheet mostra le scene registrate, non fotogrammi inventati.

### Un episodio
```bash
python -m pip install pillow
python src/video_boards_v34.py --project output/episodio/PROJECT_V13.json --out output/episodio/boards
```

### Venti o più episodi
```bash
python src/video_boards_v34.py --root output --out output/boards_batch
```

Ogni cartella PROJECT_V13 valida riceve il proprio sottodossier con nome differenziato; se mancano gli asset, la scheda riporta una miniatura segnaposto e un blocco non approvato.

## Costi / Android
- **Chiamate ai modelli immagini per scheda: 0**.
- **Chiamate Gemini Gacrux per scheda: 0** (il parlato del video resta gestito altrove).
- CPU e memoria per creare PNG/JPG: consumo computazionale locale/Actions, non API.
- GitHub Actions runner standard su **repo pubblico**: attualmente gratuiti; verificare limiti di esecuzione, storage e condizioni del servizio.
- Mobile Android: avvio da GitHub Actions, scaricamento artifact o apertura via Video Library Studio dopo integrazione verificata.
- Non inserire nuove credenziali; non attivare modelli Premium, pubblicazione o ripetizione in loop.
- Ridurre storage con JPEG per contact sheet, anteprime ridimensionate e retention artifact breve.

## Garanzie e limiti
- Questa scheda visuale **NON sostituisce PROJECT_V13**, `check`, licenze o revisione del MP4.
- Una `source_reference` compilata NON dimostra che i diritti siano validi; lo stato "REVISIONI REGISTRATE" significa solo che i campi di revisione sono marcati come tali nel progetto.
- Nessuna voce `reviewed`, `passed` o etichetta "video finito" è aggiunta o cambiata dal generatore.
- Le copertine dei video sono riutilizzate, non rigenerate; un segnaposto non è un asset finale.
- Ogni storyboard oltre otto scene continua nella contact sheet completa; il board concept è un sommario.
- Adatto a libri, cinema e critico perché il contenuto viene letto dal V13; non alterare regie o voci dei format.
- Produzione batch gratuita non significa che la sintesi vocale, l'illustrazione originale o lo storage siano illimitati.

## Interfaccia Video Library Studio V34 (26/10/2026)
La scheda privata Dossier / ZIP include la sezione **▣ Schede grafiche** con tre opzioni (Concept, Production, Scene Contact Sheet), preview mobile e download PNG.
Le tavole vengono **calcolate su richiesta nel browser**, senza nuove chiamate a GPT, Gemini, Pixabay o un motore immagini.
Dopo la pubblicazione della pagina tramite `.github/workflows/video-library-enrich.yml`, per ogni video presente nel catalogo l'utente può aprire Dossier → Schede grafiche → scegliere → scaricare.

- Progetto `PROJECT_V13.json` e codice `src/video_boards_v34.py`: disponibili per batch server-side con asset locali.
- Schede nel **sito**: derivano dal dossier online e dalla copertina già nel catalogo, non sono copie PNG archiviate in R2.
- La Contact Sheet del sito mostra **descrizioni** da `storyboard`; non inventa una miniatura per una scena che non abbia un asset accessibile. Per anteprima delle immagini reali di scena usare il generatore Python quando gli asset esistono.
- Se la copertina non è disponibile compare un segnaposto dichiarato.
- Se modifichi il dossier e non hai ancora salvato, l'anteprima riflette le modifiche aperte nel form; il PNG non salva automaticamente il dossier.
- Restano necessari controlli V13, diritti e revisione artistica prima di chiamare un video approvato.

### Limiti espliciti
Questa integrazione non crea immagini nuove, non sincronizza fotogrammi del MP4 e non carica nuovi asset in R2. La versione del sito non equivale al generatore locale V34 completo e non sostituisce il Release Pack. Nessun upload o pubblicazione social viene attivato dall'apertura delle schede.

### Verifica
`tests/video-library-boards-v34-ui.test.cjs` valida tre layout, il testo dello storyboard, il rispetto dei diritti non verificati, il download PNG e l'assenza di nuove chiamate API. `.github/workflows/video-library-editorial-test.yml` include la verifica del sito.
