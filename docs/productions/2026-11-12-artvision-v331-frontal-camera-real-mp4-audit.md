# ArtVision V331 · Audit reale dell'angolo di camera Bruegel Critico Museum V218 · 12 novembre 2026

**Esito artistico: REJECTED — quadro non frontale.** Il proprietario ha esplicitamente rifiutato in generale inquadrature Museum inclinate e prospettive scorrette. Ho verificato materialmente un esempio precedente già presente nella Libreria: *The Fall of the Rebel Angels*, Critico Museum V218. Non lo promuovere a Gold, non pubblicarlo e NON contarlo come versione Museum approvata. Le quattro versioni e lo ZIP storico NON devono essere eliminati o sovrascritti.

## Provenienza del video analizzato
- Archivio privato `/ArtVision/Rebel_Angels_V218/ARTVISION_REBEL_ANGELS_V218_4_VIDEO_ANDROID.zip`, materializzato e aperto senza rigenerazione, contiene `CRITICO_MUSEUM_V218.mp4` 29.778.503 B.
- SHA256 MP4 effettivamente letto: `23743fc5eec772c65d5671e36b78497843824b447dfb38ec22851183fe68bf2b`.
- Frame ingresso PNG estratto con OpenCV dal MP4 al secondo circa **1,2**, SHA256 `2c64dbf92f0d6353e351100eb1fb44822ab5d38c39f1973aeaee8e317c63f5d9`.
- Frame ritorno PNG estratto al secondo circa **82**, SHA256 `3db403a3bf0a01b8a17d31d0f50f6cb4238693010f355f838592484490454d35`.

## Riscontro visivo preciso
La fotografia reale del museo mostra il quadro su una parete rossa, ma ripreso da un'angolazione laterale e inclinata: il bordo interno superiore scende verso destra, quello inferiore risale, e i bordi sinistro/destro hanno altezze apparenti diverse. Questa prospettiva è visibile all'inizio e al ritorno del video, esattamente l'errore riferito dal proprietario.

Annotazioni **visive approssimate a mano** (non detector perfetto), ordine TL,TR,BR,BL, coordinate su veri frame 720×1280:
- ingresso 1,2s: `[[24,233],[617,257],[614,673],[31,695]]`. Inclinazione massima ~**2,32°**, differenza altezza lati ~**9,96%**, centro orizzontale spostato ~**5,35%**.
- ritorno 82s: `[[37,240],[584,256],[583,651],[38,676]]`. Inclinazione massima ~**2,63°**, differenza altezza lati ~**9,40%**, centro spostato ~**6,88%**.
- entrambe le riprese non rispettano i limiti V331: max roll 1,75°, convergenza lati 4,5%, centro 6,5%; **due fallimenti indipendenti**. Numeri orientativi perché gli angoli sono stati selezionati manualmente, ma il difetto è visivamente inequivocabile.
- La foto autentica e il full FFmpeg decode precedente NON risolvono la composizione. Il titolo alto, il paletto davanti al quadro e il pavimento prospettico non correggono l'errore; l'angolo è inadatto come inquadratura hero frontale.
- Lo stesso studio fotografico viene utilizzato in altre versioni Rebel: **richiedere V331 su ciascun vero MP4**, NON dichiarare automaticamente che tutti falliscono senza misurarli.

## Decisione per il sistema di produzione
1. `museum_approved=false`; `museum_perspective_v331_status=REJECTED` soltanto per questa Critico Museum V218; non degradare Standard V218, Cinema Standard V153, voce o registrazioni originali.
2. Per la sostituzione cercare una **vera vista frontale della medesima opera incorniciata**, con fonte e licenza individuali verificate e un reale punto di vista perpendicolare al muro. Se disponibile una fotografia frontale ravvicinata della vera cornice ma non tutta la stanza, NON etichettarla come museo frontale ricostruito.
3. Non correggere tutta la fotografia obliqua con una homografia deformando le pareti: verrebbe presentato un museo fotograficamente falso. Solo una correzione limitata alla superficie pittorica con proporzioni originali può essere usata per i dettagli all'interno (senza cornice).
4. Prima di consegnare la variante sostitutiva: V331 PNG + angoli annotati e SHA; test V203 continuità; V118 controllo video completo a velocità normale; autorizzazione artistica finale dell'utente.

## Regola attiva e test CI
- `docs/ARTVISION_V331_PROSPETTIVA_FRONTALE_OBBLIGATORIA.md` (divieto globale e rare eccezioni motivate).
- `src/artvision_museum_frontal_gate_v331.py` con test negativi trapezio/inclinazione/decentramento.
- `src/artvision_museum_v119_guard.py`: nessun pass verso Gold senza V331 e human frontality review.
- Run test CI V331 **43280669212 PASS**, test e gate V119 verificati.

**Stato**: revisione/documentazione eseguite, **nessun nuovo MP4 riparato**, nessuna spesa API, pubblicazione o cancellazione. Non dichiarare che la correzione visiva sia già presente nei file storici.
