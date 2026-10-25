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

## Passo successivo
Integrare il pulsante "Schede grafiche" nel Dossier Video Library Studio, solo dopo verifica del sito live e del collegamento V13. A quel punto generare automaticamente 3 schede al completamento del video senza duplicare MP4; Release Pack on-demand.
