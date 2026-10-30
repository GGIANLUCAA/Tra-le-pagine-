# WOW LAB — preflight isolato, 30 ottobre 2026

Stato: **BLOCCATO, nessun nuovo MP4 distribuito**. Questo documento non certifica un video finito.

## Controlli verificati

- Repository: `GGIANLUCAA/Tra-le-pagine-`, percorso esclusivo `wow_lab/`.
- Ultime release WOW LAB: `wow-lab-madame-x-silhouette-v2-20261030`, `wow-lab-madame-x-silhouette-v1-20261030`, `wow-lab-hokusai-45434-android-20261029`. Le prime due rappresentano lo **stesso soggetto**, non due nuovi contenuti.
- Run autonomo WOW LAB `41011230248`: fallito nello step «Generate original-source CC0 2.5D candidate» con `invalid literal for int() with base 10: '0T'`; test di isolamento e installazione FFmpeg superati. Nessuna release da quel run.
- Run Madame X `41010951763`: concluso con successo tecnico; la release V2 dichiara comunque `human artistic review pending`.
- Esiste anche un esperimento Horse Fair (Met 435702) su branch dedicato; non è una nuova release verificata. Non riutilizzare automaticamente soggetti già in prova.
- Nessun run WOW LAB in corso fra gli ultimi 100 run esaminati.

## Correzioni sul solo branch sperimentale

1. In `wow_lab/engine.py`, il giorno UTC ora viene letto con `stamp[6:8]` anziché `stamp[-4:-2]`: il secondo indice attraversava la lettera `T` e provocava il crash.
2. La selezione rifiuta tutti gli ID presenti negli ultimi sei record di cronologia (prima saltava soltanto l'ultimo).
3. Due test di regressione aggiunti in `wow_lab/tests/test_engine.py`: selezione slot UTC e blocco di soggetti recenti.

**Limite importante:** la cronologia del motore V1 riconosce soltanto release `wow-lab-v1-*` con metadati `WOWLAB_META`; le release sperimentali `wow-lab-madame-x-*` e `wow-lab-hokusai-*` non vengono ancora importate automaticamente. Pertanto il controllo completo degli ultimi sei contenuti non è garantito. Non considerare questo fix sufficiente per sbloccare la produzione.

## Gate artistico mancante

Il motore generale `wow_lab/engine.py` applica prospettiva all'intera tela e non genera alcuna maschera del soggetto: **non è un pop-out della figura**. Il test Madame X usa invece una sagoma manuale specifica per il solo Met object 12127, con audit tecnico della maschera. Questa maschera non è riutilizzabile su altre opere. Il quadro Horse Fair ha più figure e non soddisfa il requisito «un soggetto semplice» senza scelta e segmentazione ulteriore.

Prima di distribuire un nuovo WOW LAB: selezionare fonte singola CC0 con licenza verificata, produrre maschera e sovrapposizione di controllo, controllare visivamente contaminazione dello sfondo e contorno, poi soltanto eseguire render, full decode, ffprobe, confronto still e release Android. Il passaggio automatico di test non equivale a giudizio artistico.

## Isolamento

Nessuna modifica a `main`, `.github/workflows/`, `AGENTS.md`, `docs/REGOLE_ATTIVE.md`, ArtVision 4×1, Storia Rivive, Vidu, code, archivio o sito. Nessun costo API, nessuna pubblicazione social, nessun link di video inventato.
