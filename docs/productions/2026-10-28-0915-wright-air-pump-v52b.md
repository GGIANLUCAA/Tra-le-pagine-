# ArtVision Cinema V52B — Joseph Wright 'of Derby', *An Experiment on a Bird in the Air Pump* (1768)

**Stato effettivo: `rendered_needs_review` — non Gold Master, non pubblicato.**
Data esecuzione: 28 ottobre 2026. Format Cinema V6 senza voce, con musica licenziata.

## Produzione verificata

- Workflow GitHub Actions V52B: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40649283319
- Artifact GitHub V52B: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40649283319/artifacts/12798647211
- MP4: 1080×1920, 24 fps, H.264/AAC, **55,90 secondi**, **6.690.474 byte**.
- SHA256 MP4: `ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2`.
- ZIP di produzione completo: **22.243.048 byte**, `zipfile.testzip() == None`, file sorgente, MP4, JPEG, quattro post V28, ricerca, storyboard, ricetta, diritti, musica e QA presenti.
- Verifiche: ffprobe, decodifica integrale FFmpeg (runner e seconda verifica locale), CRC ZIP, quattro testi V28 con validator, cover e primo fotogramma confrontati contro branding generato dalla medesima funzione.
- Cover MAD 0,867; primo frame MAD 2,511 nella banda identitaria (rispetto al riferimento esatto generato dal renderer); entrambi mostrano il titolo inglese integrale su due righe e **JOSEPH WRIGHT 'OF DERBY'**. Controllo visivo manuale della cover e della contact sheet effettuato.
- MP4 e ZIP salvati nella Libreria ChatGPT: `/ArtVision/Wright_Air_Pump_V52B/`. Upload della JPEG separata in Libreria fallito per **403 trusted producer indexing**; JPEG è comunque presente nel pacchetto ZIP e nella conversazione.
- Non sono stati usati servizi video a pagamento, né pubblicati post social.

## Ricerca e scelta

Tre candidati: Wright, *An Experiment on a Bird in the Air Pump* (scelto, nuova opera con forte tensione etica); Bruegel, *The Tower of Babel* (scartato per prossimità al precedente Bruegel e fonte non ancora completata); Rembrandt, *The Night Watch* (scartato per presenza di altri lavori Rembrandt). Nessuna statistica inventata sul pubblico. La ricerca per duplicati ha esaminato `docs/productions` e le corrispondenze di codice nel repository.

**Museo e dimensioni:** National Gallery, Londra, NG725; 183×244 cm. Il museo segnala prestito a Derby Museums fino al 1° novembre 2026. Non è stata usata una sala museale ricostruita, dunque nessuna falsa scala prospettica.

**Opera autentica:** riproduzione Wikimedia Commons 5639×4226, PD-Art / Public Domain Mark, https://commons.wikimedia.org/wiki/File:An_Experiment_on_a_Bird_in_an_Air_Pump_by_Joseph_Wright_of_Derby,_1768.jpg . Fonte museale: https://www.nationalgallery.org.uk/paintings/joseph-wright-of-derby-an-experiment-on-a-bird-in-the-air-pump . Valutare limitazioni territoriali prima di distribuzione commerciale.

**Registrazione musicale distinta:** *The Descent* — Kevin MacLeod, ISRC USUAN1200094, CC BY 4.0; https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200094 . Registrazione originale inclusa nello ZIP e attribuita nei quattro post. Eventuali claim di piattaforma non esclusi automaticamente.

## Regia, errore e correzione

10 inquadrature: uccello nella campana, dimostratore, bambina turbata, adulto che la consola, spettatore incuriosito, coppia distratta, teschio illuminato, ragazzo alla gabbia, ritorno all'uccello e quadro intero. Nessuna falsa animazione dei personaggi, nessuna sovrapposizione fra dipinti. Momento narrativo: il dimostratore ci guarda mentre la bambina distoglie gli occhi, trasformando l'osservatore in testimone.

La **prima esecuzione V52** (run 40648937339, hash `0a9d475ee6c4e0b24f12196ea427bca21d254b6e1a327bd1cc591ffa0e589eba`) è stata **scartata artisticamente**: il primo fotogramma inquadrava la gabbia vuota anziché l'uccello, per una coordinata normalizzata errata. Non è stata cancellata o spacciata per migliorata. V52B ha corretto tutte le coordinate contro l'originale autentico, riprodotto da zero, confrontato copertina e fotogrammi intermedi.

L'incidente storico di *The Temptation of Saint Anthony* (titolo/artista assenti nell'apertura) è annotato nel QA come difetto bloccante da non ripetere.

## Tre punti per il ciclo successivo

1. Alcuni dettagli di persone sul lato destro potrebbero essere troppo vicini narrativamente: controllare il ritmo a velocità normale.
2. Valutare su smartphone se il cacatua bianco nella campana è sufficientemente riconoscibile e se il titolo rimane leggibile con luminosità bassa.
3. Ascoltare l'intera curva musicale e verificare la chiusura; la presenza AAC e la normalizzazione non certificano il gusto artistico.

**Revisione estetica e ascolto umano integrale ancora pendenti**. Non importare tra gli approvati, non chiamare Gold Master. La coda S01 rimane invariata: Turner Critico E02 bloccato finché non sia disponibile la vera voce Google Gacrux; Goldfinch E01 e Seurat E03 sono già `rendered_needs_review`.
