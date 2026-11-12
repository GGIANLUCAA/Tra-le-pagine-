# ArtVision V332 — Biblioteca di sale fotocredibili riutilizzabili, cornici specifiche e 4×1

**Direttiva proprietario, 12 novembre 2026.** Gli ambienti di museo AI che abbiamo creato possono essere riutilizzati in due formati: **Cinema Museum** (solo musica) e **Critico Museum** (identica voce Google Gacrux del relativo Standard). Si preservano le versioni Standard già prodotte. La sala è una **scenografia inventata ma fotorealistica**; non la si presenta come la stanza storica di Tate, Prado, ecc. La documentazione dell'**opera e della sua specifica cornice** resta invece autentica e prioritaria.

## Stato reale della biblioteca

- **12 immagini** già nella **Libreria ChatGPT** `ArtVision/Museum_AI_Rooms_V332` (file 01–12); hash SHA256 di ogni PNG, dimensioni pixel e identificativo Library registrati in `config/artvision_ai_room_library_v332.json`.
- **10** immagini con una parete al centro libera **candidate per provini**; **G09 e G10 sono disabilitate** perché hanno già una cornice artificiale integrata. Prima bisogna eliminarla con vera riparazione visiva e nuova QA. **0 sale ancora approvate Gold come ambienti di ripresa**.
- File fotografici AI **non caricati nel repository GitHub**: sono nella Libreria proprietaria privata, non sono ancora disponibili automaticamente alle GitHub Actions. Non dichiarare che la pipeline GitHub possa scaricarli da sola: usare `files.materialize`/esportazione dei PNG nel job che effettua il rendering, oppure effettuare un futuro sync autenticato verso storage del progetto, con controllo SHA. Il catalogo GitHub e il codice CI invece sono disponibili.
- La biblioteca può crescere a **10–30 sale**. Aggiungere un'identità stabile, file reale, licenza/provenienza, SHA, area centrale sicura, scala, tag e review prima di abilitarne una. Non alterare i 12 hash esistenti quando si migliora una foto: creare una revisione esplicita.

## Integrazione esistente, non una pipeline parallela

- V46: proporzioni e ingresso/ritorno; V64: traiettoria continua; V69/V70/V71: fonte, scala fisica e sceneggiatura; V80/V118: **cornice specifica**, realismo e sincerità dell'ambientazione; V119: archivio di ambienti riutilizzabili, V331: **frontale e centrato**.
- `src/artvision_ai_room_integrator_v332.py` seleziona la stanza per **misure centimetriche** + **mood** + uso recente, poi combina fotografia della sala con l'opera **senza distorcere**. La stessa scelta `room_id` viene bloccata per `cinema_museum` e `critico_museum`; si usa la stessa fotografia documentata della cornice.
- `src/creative_director_v21.py`: output aggiuntivo `museum_ai_room_v332` per brief Museum, **non render automatico**. Il direttore non deve sostituire la fonte artistica, la musica V330 o la voce.
- `src/artvision_ai_room_video_v332.py`: prototipo **2D frontale** che riutilizza il video Standard e copia l'AAC bit-identico; esegue decodifica FFmpeg integrale e misura i salti ai raccordi. Il salto causa `REJECTED_NEEDS_CONTINUOUS_CAMERA_REPAIR`. Non rappresenta una vera camera 3D o una sala museale ripresa in movimento.

## Scelta della cornice — ordine vincolante

1. **Cornice documentata dell'esemplare preciso**, anche se è la cornice *attuale* e non quella del secolo dell'artista. Fonte istituzionale o fotografia del dipinto incorniciato, autore, licenza, immagine e SHA, inquadratura possibilmente frontale. NON definire «originale dell'artista» una cornice attuale solo perché è documentata.
2. Ricostruzione fedele della stessa cornice, solo con fonte sufficiente, geometria controllata e revisione.
3. Se non disponibile, una **cornice editoriale coerente con stile/periodo** (oro sobrio, legno, bronzo o nero), *mai dichiarata storica*, e solo con provino approvato per il quadro. Nessuna cornice generica dentro la foto della stanza. Se il risultato è brutto, NON consegnare e cambia sala o cornice.

## Scelta sala / dimensioni

- **Ogni quadro ha larghezza e altezza reali**. La stanza è selezionata anche per dimensioni stimate: un Blake di 21×16 cm non si espande magicamente in una tela enorme; una tela monumentale usa una sala con campo visivo sufficiente. Se nessuna stanza soddisfa la parete, il selettore blocca, non deforma.
- Le sale sono **foto AI con prospettiva propria** e NON geometrie 3D calibrate: `design_camera_distance_cm` è una stima cinematografica da controllare, non una misura fisica del luogo. Il frame deve stare nella parete delimitata `safe_wall_box_norm`, non sopra cornici già presenti, colonne, panchine o pavimento. La camera vede la tela di fronte (V331).
- Scegliere una sala che valorizzi il dipinto, senza ripetere meccanicamente l'ambiente appena usato. Per la stessa opera, le due Museum devono mantenere **identica** sala e cornice, mentre le due Standard restano immutate.

## Prova concreta già eseguita (non Gold)

- Opera: Pieter Bruegel il Vecchio, *The Fall of the Rebel Angels* (1562), 117×162 cm, inventario RMFAB 584.
- Sala G02: generata con AI, rossa e frontale. Cornice: fotografia documentata del quadro di Sailko, licenza CC BY 3.0 (la foto dimostra la **cornice attualmente fotografata**, NON che sia originale del 1562). Immagine quadro da fonte autentica con hash.
- `cinema_museum_G02_REVIEW.png` e `critico_museum_G02_REVIEW.png`: prova **reale** del compositing: **stessa immagine** di ingresso perché la sala e la cornice devono coincidere in entrambe le varianti. Nessuna nuova voce e nessuna spesa.
- `V332_BRUEGEL_FRONT_ON_ROOM_DEMO.mp4`: 8s **demo senza audio**, 540×960 a 18fps, FFmpeg full decode PASS, zoom 2D frontale; non è una versione Cinema/ Critico completa.
- Seconda prova su video Standard reale `V153` 48s, AAC bit-identico, full decode PASS, ma i due salti ai raccordi misurano **58,631 e 60,435** contro limite **18,0**: correttamente **BOCCIATA**, non pubblicata, NON da contare nella coda come nuova versione Museum. La camera deve essere raccordata all'ultima/alla prima inquadratura centrale prima di rendere il renderer V332 disponibile come produzione finale.
- Le due colonne `critico_museum` e `cinema_museum` **non sono state consegnate come nuovi master** per questo esperimento.

## Comandi di prova, Android/Codex Cloud

Avendo materializzato i PNG originali della sala in `ASSET_DIR`, e il quadro e la cornice esatti come file locali:

```bash
python src/artvision_ai_room_integrator_v332.py \
  --catalog config/artvision_ai_room_library_v332.json \
  --assets-dir "$ASSET_DIR" --painting "$PAINTING_JPEG" \
  --width-cm 162 --height-cm 117 \
  --moods dramatic,historic,epic --room-id G02 \
  --authentic-frame-photo "$FRAMED_SPECIMEN_JPEG" \
  --frame-source-url "$FRAME_SOURCE_URL" --frame-license 'CC BY 3.0' \
  --variant cinema_museum --out-dir /tmp/artvision_review
```

Per il Critico usare lo **stesso `room-id`, gli stessi asset e la stessa cornice**, cambiando solo `--variant critico_museum`. Nessun comando di upload/pubblicazione è implicito. I file `QA.json` confermano SHA, scala di progetto, cornice e stato `museum_approved=false`.

Solo dopo la scena **foto QA** e lo storyboard frase→inquadratura eseguire un video, con la stessa traccia audio dei due Standard e test V203, V331, V119, FFmpeg, ZIP, e revisione artistica a velocità normale. Se un raccordo salta o la stanza sembra finta, **rifiutare e correggere la sola Museum**. Lo scopo di V332 è eliminare ripetizioni e rifacimenti della sala, **non** abbassare il livello qualitativo.