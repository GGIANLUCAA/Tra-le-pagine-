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


## V35 · Dossier ricco, con provenienza documentata (26 ottobre 2026)
Le infografiche precedenti di *Alice* e *Il piccolo principe* erano composizioni editoriali elaborate dall'AI, **non database originali verificati**. Le etichette "verificato" e le licenze presentate nelle immagini precedenti non dimostrano di per sé un controllo reale.

**Distinguere sempre quattro origini:**
1. **Fatto bibliografico**: autore, anno, prima edizione, personaggi e svolgimento; richiede URL consultabile e riscontro effettuato.
2. **Proposta editoriale**: hook, durata, storyboard, regia, pubblico, promessa iniziale; è una scelta creativa, non un fatto ricavato dalla fonte.
3. **Asset specifico**: immagine usata, file, URL, licenza, attribuzione richiesta e stato di verifica. Ogni asset ha una riga distinta; la fonte del libro non autorizza automaticamente le sue illustrazioni.
4. **Master effettivo**: durata, codec, voce, scene renderizzate, link e controlli tecnici vengono da strumenti o file reali, non dallo storyboard prospettico.

### Record dati
I nuovi brief `PROJECT_V13.json` possono includere, **senza creare un secondo progetto**:
```json
{
  "bibliography": {
    "author": "",
    "publication_year": "",
    "edition_reference": "",
    "rights_notes": ""
  },
  "editorial_metadata": {
    "series": "",
    "themes": "",
    "genre": "",
    "narration_style": ""
  }
}
```
Rimangono anche `editorial_plan.sources` (reference, finding, verification), `editorial_plan.subject_insight`, `editorial_plan.mix_reason`, `business.audience`, `scenes`, `assets` e `editorial_plan.media_sourcing.decisions`.

Video Library Studio ha ora una sezione **◈ Ricerca e libro** e la quarta tavola **4 · Dossier illustrato completo**. Un **vero** `PROJECT_V13.json` allegato come `production/files/<video_codificato>/PROJECT_V13.json` viene letto solo nella sezione privata, se pesa al massimo 250 kB: vengono importati i campi disponibili; le correzioni già presenti nel dossier prevalgono. Se il file non è collegato compare la dicitura di origine **"Solo dati del dossier"**, senza pretendere il recupero automatico.

La quarta tavola riunisce autore, anno, serie, hook, ragione della scelta, temi, pubblico, format, durata, voce, regia, scene, fonti, registro asset, social, musica, crediti e stato dei diritti. Eventuali campi mancanti sono **Da completare**. Una tavola illustrata non è un archivio verificato, e la versione del sito resta una sintesi visiva: il dossier testuale conserva i dati integrali.

### Verifiche bibliografiche esemplificative: da NON trapiantare a un altro video
- **Alice**: Lewis Carroll, prima edizione 1865; vedi Morgan Library https://www.themorgan.org/printed-books/246978 e illustrazioni Tenniel al V&A https://www.vam.ac.uk/articles/alice-through-the-pages . I diritti delle singole riproduzioni e i termini dei fornitori devono essere controllati sul file effettivamente riutilizzato.
- **Il piccolo principe**: pubblicato nel 1943; i disegni dell'autore non sono da dichiarare automaticamente di pubblico dominio in Francia. Il Syndicat national de l'édition indica **1 gennaio 2033** per l'ingresso nel pubblico dominio francese: https://www.sne.fr/editeur-et-auteur/duree-des-droits-dauteurs/ . Anche leggi e territori diversi vanno controllati prima dell'uso commerciale. La copertina generata da AI non è la prova di licenza delle illustrazioni originali.

### Costi e sicurezza
- **Zero chiamate extra AI** per generare le tavole: CSS/Canvas o Pillow da materiali e metadati già esistenti.
- Nessuna duplicazione di MP4 e nessuna pubblicazione automatica.
- Senza V13 allegato il sito **non può ricostruire retroattivamente** dati che non sono stati archiviati.
- Non importare una fonte fittizia, non marcare "verificato" per sola presenza di URL.
