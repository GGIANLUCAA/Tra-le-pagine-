# ArtVision — gate di regia frase→inquadratura (06/11/2026)

Stato: **scheda operativa di QA preparata, non render e non approvazione**. Feedback proprietario: il Critico visto è accettabile ma nei prossimi video il soggetto nominato deve essere inquadrato meglio, con movimento più lineare e coerente con la spiegazione. Integra V82 senza cambiare master esistenti o altri format.

## Gate obbligatorio prima di dichiarare un Critico pronto

1. Estrarre dalla WAV effettiva gli intervalli parola/frase tramite ASR con controllo d'ascolto; non usare la sola durata stimata del testo.
2. Per ogni frase descrittiva, compilare: `spoken_start_s`, `spoken_end_s`, `quoted_subject`, `painting_polygon_normalized`, `shot_start_s`, `shot_end_s`, `subject_visible_from_s`, `legibility_hold_s`, `source_pixel_crop`, `qa_result`. Poligono da verificare visivamente sulla riproduzione autentica: non inventare coordinate.
3. Inquadrare il soggetto **prima o al più tardi all'inizio della sua menzione**, senza inquadrature generiche durante il passaggio. Mantenere un tempo leggibile; niente volti, gesti, oggetti o corpi tagliati. Se il soggetto è troppo piccolo per essere riconoscibile senza blur, cambiare dettaglio o riscrivere il passaggio.
4. Limitare i movimenti ai raccordi motivati dal testo: traiettorie stabili e senza inversioni arbitrarie, niente zoom avanti-indietro ripetitivi. Una frase complessa può richiedere prima un contesto e poi il particolare, ma entrambi devono corrispondere al parlato.
5. Verificare il **vero MP4 con audio** in playback a velocità normale, marcando ogni frase mismatch, ritardo, crop, sfocatura e durata insufficiente; correggere solo i segmenti falliti. Un PASS FFmpeg non è PASS di regia.
6. Per Critico Museum: **stessa WAV byte-identica** del Critico Standard, percorso continuo e autentica cornice documentata solo in apertura/chiusura. Se la foto della cornice specifica non è verificabile, non renderizzare/approvare Museum.

## Applicazione al prossimo lotto

- *The Death of Sardanapalus*: Critico Standard V169 già esistente e tecnicamente verificato secondo queue; **non ricrearlo né sovrascriverlo**. Applicare il gate a una revisione non distruttiva solo dopo aver recuperato MP4/WAV e ispezionato scene reali. Cinema V168 già accettato artisticamente dal proprietario, nessun nuovo render di quel contenuto.
- Alternative con due Standard esistenti: *The Magic Circle*, *The Garden of Death*, *The Night Watch*, *The Triumph of Death*, *The Ghost of a Flea*. Evitare doppioni. Museum sospesi dove manca cornice specifica documentata.
- *The Temptation of St. Anthony* di Dalí resta SOSPESO.

## Esito di questa scheda

Documento di produzione/QA salvato; **0 nuovi MP4**, **0 nuovi SHA256 di MP4**, **0 slot aggiunti**, **0 spese**. Non considerare il documento un audit artistico eseguito.
