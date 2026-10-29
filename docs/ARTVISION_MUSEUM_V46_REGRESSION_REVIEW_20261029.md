# ArtVision Museum Immersion — regressione verificata (29 ottobre 2026)

## Decisione editoriale: NON APPROVARE i nuovi Museum V55 come modelli

La segnalazione dell'utente è confermata dal confronto **sui quattro filmati MP4 reali**, non da schede/preview:

- **The Cyclops — SENZA STRISCE CORRETTO**, master approvato V46, recuperato dal Drive ID `1w9mb1N5hrGAaB870JANHoKk98MiibtpW`, 89.672.847 byte.
- **Hiroshige — Sudden Shower, Museum Scale**, master approvato V46, recuperato dal Drive ID `14X8_TObXEijGlBg8HuyR6ITTlPjJk0dA`, 66.691.253 byte.
- **Hokusai — The Great Wave, Cinema Museum V55C**, MP4 SHA256 `92d017fc9b65b63799d161a33e9e9902cfb1e20c7fbbf6ba878b1d54035a6547`.
- **Winslow Homer — The Gulf Stream, Cinema Museum V55B**, MP4 SHA256 `2c50c5f94c2fefbdf23b1a03086245afed3e25b06a159845c8947fcd9ee1a5b8`.

I campioni estratti realmente a tempo 0.2/2/4/6/8/10/12/14 s e vari punti successivi mostrano:

| Problema | Cyclops / Hiroshige approvati | Hokusai / Homer V55 regressi |
|---|---|---|
| Sala | Materiali, ombre, pavimento, prospettiva credibili; visitatore e scala per Hiroshige | Parete digitale piatta beige/chiara e stanza senza dimensioni umane visibili |
| Cornice | Profilo profondo, modanatura tridimensionale, labbro con dipinto dietro, luce di contatto | Rettangoli `ImageDraw`, falsi rilievi, effetto di stampa appoggiata |
| Entrata | Avvicinamento e attraversamento fisicamente coerenti, raccordo artwork ↔ museo | `ffmpeg zoompan` sulla stanza JPEG e **cut netto** verso JPEG di un dettaglio del dipinto |
| Uscita | Ritorno fluido alla stessa prospettiva | **Cut** dalla vista dell'opera a nuova ripresa della parete |
| Scala | Hiroshige: stampa di 35 cm vicino a una persona adulta; solo l'ottica la ingrandisce | Misure annotate nel JSON, ma camera/sala non tarate con persona/porta e distanza |
| Priorità della cornice autentica | Ricerca del riferimento prima della ricostruzione, foto e diritti | Cornice nuova inventata senza `frame_research` visuale approfondita |

## Prova numerica dei raccordi

Misura: media assoluta RGB sui **veri fotogrammi consecutivi** del video, ridotti a 180×320; massimo nell'intorno di ciascun salto (±0,25 s). Valori elevati confermano una discontinuità, non valutano da soli la bellezza.

| MP4 V55 | Entrata nel quadro | Uscita verso sala |
|---|---:|---:|
| Hokusai Museum V55C | 8,208 s: **74,4 / 255** | 33,917 s: **130,2 / 255** |
| Homer Museum V55B | 8,375 s: **66,9 / 255** | 38,750 s: **92,7 / 255** |

Riferimenti precedenti: documenti originali Cyclops e Hiroshige riportano ~**3,1** e ~**2,9 / 255** rispettivamente sui raccordi di ingresso/uscita dopo correzione. Le misure dei nuovi file sono state ripetute sulle sorgenti MP4 di questa sessione. Le misure storiche provengono dai report dei rispettivi master, non da un nuovo confronto numerico completo.

**Blocco V56:** sul singolo passaggio Museum usare `src/artvision_museum_v46_regression_gate.py`, rifiutando un picco superiore a 12 / 255. Una soglia numerica serve a bloccare raccordi palesemente interrotti, ma NON certifica cornice, prospettiva, realism o qualità artistica. Resta necessaria visione completa dell'MP4 e confronto con i due riferimenti realmente recuperati.

## Causa radice nel software

- `scripts/artvision_hokusai_cinema_museum_v55.py`: `gallery()` crea **parete 2D** con `ImageDraw`, incolla la stampa su un rettangolo e `encode()` concatena nove JPEG; l'entrata tra scena 1 e scena 2 non proietta progressivamente la scena nella sorgente del dipinto. La sola dimensione della stampa non definisce camera, adulto di riferimento né profondità.
- `scripts/artvision_homer_four_v55.py`: `gallery()` usa un'immagine di parete beige con cornice 2D; `ffmpeg_render()` applica un **zoompan** generico ai still; `cinema_museum()` concatena l'ultima vista parete e il primo dettaglio originale senza ponte. Pur avendo misurato la tela e la dimensione ESTERNA della cornice del Met, il profilo e le modanature mostrate non sono stati documentati con una fotografia della stessa opera.

L'esistenza di `ARTVISION_4X1_PLAN.json`, `ffprobe`, H264/AAC, quattro post e ZIP CRC NON equivale a V46 rispettata: la validazione era prevalentemente strutturale.

## Decisioni operative

1. **Preservare** i MP4 V55 e tutti i master migliori; non cancellare file e hash storici.
2. **Segnare Hokusai Museum V55C e Homer Museum V55B come regressione artistica respinta**, mantenendo `rendered_needs_review` come stato tecnico; evitare di citarli come riferimenti di produzione.
3. **Bloccare la generazione/consegna di nuovi Museum** con renderer a parete piatta e taglio netto; riutilizzare il modello **Cyclops per oggetto/cornice/continuità** e **Hiroshige per prospettiva/scala**.
4. Prima di ogni nuovo render cercare fotografie attribuite all'**esatto esemplare** e diritti; se la cornice è visibile replicarla, distinguendo originale/storica/attuale; altrimenti ricostruzione dichiarata e materica.
5. Camera POV unica fra stanza, tela e ritorno: renderizzare fotogrammi **intermedi** del passaggio con coordinate continue tra quadro incassato e sorgente originale ad alta risoluzione, senza dissolve/ghosting/edge-stretch.
6. Gate V56 automatizzato su entrata/uscita e gate manuale su stanza, modanature, angoli, battuta, ombre, rapporto scala umana e visione normale smartphone. **Non consegnare** un file solo per rispettare il calendario.
7. Cinema Standard può avanzare separatamente solo se supera le sue regole; Critico richiede sempre Gacrux autentico e sincronizzazione.

Stato: **regressione identificata e guardia di qualità introdotta**; non ancora disponibile un nuovo renderer Museum che ricrei il livello del master Cyclops. Nessun nuovo Museum conforme è stato prodotto in questa revisione. Nessuna nuova API a pagamento invocata.
