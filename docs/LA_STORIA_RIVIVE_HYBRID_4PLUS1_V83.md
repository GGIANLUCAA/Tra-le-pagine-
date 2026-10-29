# LA STORIA RIVIVE · V83 / V83.1 — Montage 4+1 · Moving Color

**Decisione editoriale del 29/10/2026.** Questa modalità integra il format V82 (film storico autentico in movimento B/N → fotogramma originale fermo → fotografia AI moderna dello stesso soggetto) con **UN solo inserto Vidu di circa 5 secondi**, in cui la scena si muove per tutta la durata. Non sostituisce V82 né modifica i preset ArtVision 4×1.

## Effetto finale, non spezzettato
Un solo MP4 verticale con una colonna sonora continua, generalmente 19–26 secondi, composto da **cinque scene storiche diverse**: 4 scene V82 tradizionali e 1 scena Vidu. I cinque luoghi/soggetti reali non devono essere dichiarati un unico piano sequenza della stessa camera: utilizzare match cut sulla direzione del movimento, angoli e tagli a tempo musicale, senza transizioni fantasma su facce/oggetti. La posizione Vidu può essere **prima, centrale o finale** e va scelta con motivazione narrativa (hook, climax, chiusura) anziché sempre allo stesso posto.

## 4 scene classiche
1. Film originale realmente in movimento, non foto pan/zoom, proveniente da un originale individualmente controllato come PD/CC0 in Italia e nel paese d'origine.
2. Arresto sul fotogramma ESATTO, senza cambiare numero e posizione dei soggetti.
3. Restauro fotografico AI coerente con V82, nitido e realistico, ma **non identità e colori storicamente certi**. Evitare blur generalizzato V77, ritocco beauty e oggetti↔persone.
4. Foto restaurata ferma circa 1.2–2.5 secondi: un forte contrasto prima/dopo, non un'animazione finta. Scene differenti, senza duplicare la stessa inquadratura con zoom.

## 1 scena Vidu — differenza cruciale
1. Ingresso sulla scena originale con fotogramma della stessa inquadratura, poi Vidu prosegue da quell'ancora senza tagli di prospettiva.
2. Entro **~1.0–1.15 s** il B/N diventa colore naturale e fotorealistico.
3. Nei successivi **almeno 3.5–4 s**, deve essere visibile **movimento effettivo coerente** degli stessi personaggi, strade, tram, folla, acqua ecc. NON generare soltanto una foto, un fermo, un semplice zoom o una dissolvenza immobile.
4. Nessun uomo↔ruota, variazioni di count, volti plastici, arti extra, oggetti che cambiano natura, cambi di inquadratura non motivati; salvaguardare proporzioni e geometria.
5. Se la generazione Vidu porta a colori troppo lentamente, V83.1 può usare l'**effettiva sequenza video Vidu già esistente** e anticiparne il colore con trasporto di crominanza guidato dal flusso ottico, preservando luminanza e movimento. È una rifinitura post-produzione, **non un nuovo video generato da Vidu né una prova di restauro storicamente vero**. Test di movimento, colore e allineamento obbligatori.
6. Le clip Vidu devono essere legate al corretto frame sorgente e alla loro vera ricevuta task. Una singola autorizzazione individuale con modello, immagine, prompt, secondi, tariffa e codice prima del POST; nessuna duplicazione o retry a pagamento. Bilancio prima, spesa effettiva, saldo dopo. Preferire l'uso di video già disponibili e 0 nuovi crediti durante gli esperimenti del montaggio.

## Raccordi che creano una sola esperienza
- Prima della clip, l'ultimo frame storico si deve allineare all'esatto primo frame generato; rifiutare se prospettiva o persone divergono.
- Dopo la clip NON aggiungere necessariamente un hold: preservare il movimento fino al raccordo. Il taglio verso un differente spezzone storico è naturale se collegato da composizione, gesto o battuta musicale.
- Ogni scena nel master ha identico crop/proporzione 9:16, FPS 30, gamma/colore e audio in un'unica traccia. Non fondere due volti differenti con dissolvenze fantasma.
- Apertura inglese sobria **luogo · anno/periodo accurato**. Nessun cartello pubblicitario finale.

## Verifica fail-closed
- Verificare 5 scene, esattamente 4 fotografiche e 1 Vidu, tutte da eventi originali distinti; hash sorgenti e rapporto foto/frame originali.
- Misurare saturazione al primo secondo e durante i 4 successivi, movimento reale DOPO l'entrata a colori, coerenza fra frame e clip, luma/struttura, duration e MP4 H264/AAC.
- Esaminare visivamente ogni scena e il film completo a velocità normale: metrica automatica **NON garantisce** integrità semantica delle persone/oggetti. Se fallisce, scartare la scena o ripristinare la versione classica, non rispendere automaticamente crediti.
- Fornire MP4, ZIP Android, cover, quattro post distinti, fonti, diritti, report QA, URL esterno GitHub Release con file presenti davvero. Pubblicare nel sito/R2 solo dopo controllo diritto, revisione umana e controllo import del sito (V55/V25).

## Realizzazione nel repository
- Regole machine-readable: `config/storia_rivive_hybrid_4plus1_v83.json`
- Renderer pilota: `src/storia_rivive_hybrid_v83.py`
- Correzione colore su vero movimento esistente: `src/storia_rivive_vidu_chroma_retime_v83.py`
- Workflow scaricabile/Android: `.github/workflows/storia-v83-hybrid-five-scenes.yml`
- Fonti video pilota: Parigi **1900** (pellicola Lumière, clip Vidu ID `1013429649004335104` già pagata) e quattro fotogrammi differenti di Parigi **1918** dal pacchetto V68 (4 foto vere generate gratuitamente). **Attenzione: due epoche non identiche**: anteprima tecnica di integrazione, NON dimostrazione di continuità documentaria, non approvata artisticamente.
- Nella produzione futura usare obbligatoriamente la **stessa epoca e lo stesso soggetto storicamente coerente** oppure indicare in modo evidente il montaggio attraverso periodi diversi; non riusare i materiali del pilota come stampino fisso.

## Esiti e limiti del pilota
1. V83 prototipo originario: cinque scene/21,73 s, MP4+ZIP e link esterno verificati. Il vecchio Vidu mostrava colore tardi: **non approvato** come nuovo effetto.
2. V83.1: applica al vecchio video Vidu una post-colorizzazione di circa 1 secondo conservando il movimento reale generato. Output ancora da valutare artisticamente: il trattamento cromatico NON ricostruisce dettagli assenti nel video e non trasforma in filmato d'epoca originale la parte AI.
3. Necessario per il prodotto definitivo: un nuovo test su un soggetto **della stessa sequenza storica**, con movimento/colori Vidu adeguati già in partenza, preventivo e singola approvazione.
