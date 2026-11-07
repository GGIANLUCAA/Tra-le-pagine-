# ArtVision · Centro ricerca nuove opere e fonti — 7 novembre 2026

**Scopo:** supportare le chat di produzione con materiali e verifiche su nuove opere, *senza* renderizzare, pubblicare o duplicare la coda già assegnata. Non è la chat cornici/musei. Passare al gruppo cornici solo metadati identificativi quando necessari.

## Fonti pregresse recuperate
- [Catalogo editoriale 100 opere](ARTVISION_100_QUADRI_PIANO_EDITORIALE_20261028.md): 50 impatto visivo, 50 critica; **è una banca candidati, non una coda autorizzata**.
- [Catalogo 100 opere in JSON](../config/artvision_100_opere_editoriali_20261028.json), conservato e non modificato.
- [Coda proprietario 10 opere / 40 varianti](../queue/artvision_owner_selected_ten_20261102.json) — non modificarla, non anticipare rendering.
- [Ricerca fonti automatica V4](AUTOMATIC_SOURCE_RESEARCH_V4.md) — già in funzione ogni tre ore; i risultati sono *candidati*, non licenze approvate.
- [Regole attive](REGOLE_ATTIVE.md) — in particolare revisioni su diritti, source QA e divieto di duplicati.

**Nuovo archivio operativo strutturato:** [artvision_future_works_index_v1_20261107.json](../research/artvision_future_works_index_v1_20261107.json). Contiene i 100 candidati, i 10 titoli nella coda attuale, link museo preesistenti, diritti preliminari, campi per licenza del file e prime verifiche mirate. Titoli ripetuti già identificati: Rembrandt *The Night Watch* (catalogo #14) e Waterhouse *The Lady of Shalott* (#35). Per altre somiglianze servirà controllare oggetto/inventario, non solo il titolo.

## Prime tre verifiche mirate fuori dalla coda corrente

### 1. Claude Monet, *The Japanese Footbridge* (1899) — **fonte ufficiale CC0 individuata**
- Museo: [National Gallery of Art, opera 74796](https://www.nga.gov/artworks/74796-japanese-footbridge), numero inventario **1992.9.1**, olio su tela **81,3 × 101,6 cm**.
- [File Commons fornito da NGA](https://commons.wikimedia.org/wiki/File:Claude_Monet,_The_Japanese_Footbridge,_1899,_NGA_74796.jpg): dichiarato **CC0 1.0**; **4000 × 3225 px** secondo scheda del file, da scaricare e confrontare per hash e colore prima dell'utilizzo.
- Contenuto narrativo verificabile: nel 1899 Monet dipinse un gruppo di dodici opere dedicate al ponte del giardino d'acqua; non confondere varianti o altri *Water Lilies*.
- **Esito:** fonte promettente per future ricerche e storyboard. Il file esatto NON è stato scaricato/controllato e nessun video è approvato.

### 2. Vermeer, *Girl with a Pearl Earring* (ca. 1665) — **alta qualità, uso da chiarire**
- [Mauritshuis, inventario 670](https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring/): **44,5 × 39 cm**, opera definita *tronie*, non ritratto documentato di una persona specifica.
- La pagina inglese del museo indica il download in alta risoluzione per **usi non commerciali**. [File su Commons](https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_670_-_Mauritshuis.jpg) è marcato PD-Art, **5068 × 6000 px**, ma questa classificazione va tenuta distinta dalle condizioni del download museale e dalle norme territoriali. La pagina del museo in italiano ha una formulazione più ampia: non assumere che equivalga a licenza commerciale.
- **Esito:** non autorizzare automaticamente il riuso della foto finché le condizioni per l'esatto file, la destinazione e il territorio non siano risolte.

### 3. Van Gogh, *The Starry Night* (1889) — **soggetto confermato, file da licenziare**
- [MoMA, opera 79802](https://www.moma.org/collection/works/79802) conferma l'opera; [FAQ MoMA](https://press.moma.org/faqs/) rimanda a Scala Archives per riproduzioni della collezione oltre i limitati usi stampa.
- **Esito:** non trattare un'immagine del sito o del press kit MoMA come liberamente riutilizzabile. Cercare riproduzione indipendentemente autorizzata oppure autorizzazione specifica.

## Processo di consegna alle altre chat
Ogni opera futura riceve una **scheda fonte distinta**, con: identità esatta (artista/titolo/data/numero inventario), fatti narrativi con URL e citazione, sorgente immagine *specifica*, file URL + formato + pixel, licenza della **fotografia**, condizioni per Italia/altre destinazioni, attribuzione, possibilità di ritaglio 9:16 e dettaglio ad alta risoluzione, rischi visuali o contenuti sensibili, storyboard suggerito, materiali da evitare, verifica di duplicati e stato *ready / needs review / blocked*.

**Stati:** `candidate` = solo catalogo; `source_verified` = fonte identificata e condizioni documentate; `asset_verified` = file originale letto, hash, pixel e diritti del singolo asset verificati; `ready_for_production` = anche QA redazionale e diritti pertinenti superati. Non passare al livello successivo senza evidenze. La scheda può essere usata per pianificare anche se non autorizza ancora un video.

## Dipendenze e confini
Le cornici e le sale restano al **gruppo dedicato**, non qui. L'attuale proprietario della produzione resta unico, e i suoi 40 slot non vengono modificati. Le nuove opere che il proprietario comunicherà saranno **aggiunte e deduplicate nell'archivio di ricerca**, non inserite in automatico nella produzione esistente. Nessuna nuova spesa API, Vidu, TTS, rendering o pubblicazione per conto di questa ricerca.

## Stato verificato oggi
- Recuperato e conservato senza modifiche: catalogo di 100 opere, coda attuale di 10 opere, regole e workflow fonti V4.
- **Tre verifiche pubbliche iniziali**: Monet/NGA CC0 dichiarato, Vermeer/Mauritshuis diritti specifici da chiarire, Van Gogh/MoMA riproduzione specifica da licenziare.
- **Nessuna licenza completa per pubblicazione certificata da questo file, nessun master prodotto.**


## Tre nuovi Caravaggio non religiosi (richiesta del proprietario, 7/11/2026)
Scheda condivisa aggiornata: [I bari, Bacco e Medusa — immagini, fonti, regia e riuso](../research/caravaggio_tre_opere_laiche_20261107.md). Fonti primarie Kimbell/Uffizi; nuove candidate PDM, CC BY e CC BY-SA; avviso ufficiale Uffizi sugli usi promozionali/commerciali (artt. 107–108 Codice dei beni culturali). I file originali **non sono ancora stati scaricati/verificati tramite hash**; nessuna autorizzazione museale ottenuta e nessuna nuova produzione avviata. Prima di trasformare la scheda in `ready_for_production` serve QA dei byte originali e verifica dei diritti dell'esatto utilizzo.

Una ricerca indipendente ricorrente **ArtVision · Ricerca opere e fonti** è stata attivata per continuare a lavorare sui dossier e sugli altri candidati, senza toccare le chat/automazioni di produzione o cornici.
