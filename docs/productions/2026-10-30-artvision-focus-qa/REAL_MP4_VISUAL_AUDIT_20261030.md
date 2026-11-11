# ArtVision — audit reale MP4: focus narrativo e cornici (30/10/2026)

**Ambito:** QA non distruttiva di file realmente recuperati dalla Libreria ChatGPT. Nessun render, nuova voce, nuova opera, V25, import privato o pubblicazione. La V74 prevale sulle vecchie note V69: Klimt rimane **4/4 renderizzati e 0/4 approvati**; Socrate **4/4 renderizzati e 0/4 approvati**. I due Wright sono riferimenti di QA aggiuntivi, **non** uno sblocco del terzo pilota.

## Metodo riproducibile e limiti

- Otto MP4 originali recuperati in byte dalla Libreria (uno dei Cinema Socrate estratto dallo ZIP completo V67, con `ZipFile.testzip() == None`); SHA256 calcolato direttamente sui file. `ffprobe` e `ffmpeg -v error -xerror -threads 2 -i INPUT -f null -` eseguiti **con PASS su tutti gli otto**.
- Fotogrammi reali campionati tramite OpenCV `CAP_PROP_POS_MSEC`: 10 midpoint dei beat ASR Socrate per ciascun Critico, più tre campioni (inizio+1 s, midpoint, fine-1 s) sui beat 3, 5, 6, 7, 8, 10. Wright: 13 tempi tra 1 e 114 s per variante. Klimt Critico Museum: 12 tempi da 4 a 197 s; Klimt Cinema Museum: 9 tempi da 1 a 44 s. Socrate Cinema: 9 tempi ciascuno.
- Questa è **QA visiva a campione, non ascolto umano integrale**. L'identità delle tracce AAC è verificata sui bit estratti, non certifica la comprensibilità della narrazione o la perfetta sincronizzazione frase per frase. Nessun `V25 approved` attribuito.
- Gli altri due Klimt V74 (Critico Standard V72, Cinema Standard V72) non sono stati materializzati in questo run: **non** si dichiara QA fresca su di essi, né si deduce che siano inesistenti. Restano 4/4 secondo il dossier V74. La Libreria non equivale a import/player/ZIP sul sito privato.

## Evidenza tecnica: otto MP4 verificati

| Opera/slot | SHA256 reale | Durata, fps | Full decode |
|---|---|---|---|
| Socrate Critico Standard V67 | `f68592a8d65d5d774494f49892a4b8be8f9bbe7842ab19631f85046f0adf19c3` | 168.167 s, 24 fps | PASS |
| Socrate Critico Museum V67 | `c3be9d91b2967df4e484918b6d678b141111130eea991b63493d15b843c090a9` | 168.167 s, 24 fps | PASS |
| Socrate Cinema Standard V59 | `0f946f74397c780c9357f545d0a9712926bf02eb3f43ba4866eba7cda8828540` | 35.042 s, 24 fps | PASS |
| Socrate Cinema Museum V61 | `6ae8a2cb1ad3709bea4bab801ddefdaf8e7a00b3f3f65f50ddd81af8e4414afc` | 38.000 s, 24 fps | PASS |
| Klimt Critico Museum V73 | `814e52f6d4281df14d3064bce6f1295ab6cdc059a5d5c80acf7db0a095cbf1ab` | 207.500 s, 20 fps | PASS |
| Klimt Cinema Museum V73 | `9dc3cf7abcebc3e8b16d105e9e9934cde8775cec1ac6b684519fe0df1875e746` | 52.000 s, 20 fps | PASS |
| Wright Critico Standard | `2122ade02ca4819fa9ee0e212bd22de1c7bf9ded952cebeafd92ed1b821cff38` | 117.067 s, 15 fps | PASS |
| Wright Critico Museum | `02088a83b42b5a8a7b46c079e4732ea0b3cd0a02351229b1a9c5fc5941817818` | 117.067 s, 15 fps | PASS |

Codec: H264/AAC, 9:16; Socrate Cinema Standard e i due Klimt 720×1280; Socrate altri tre e Wright due 1080×1920. I due Critico Socrate hanno **AAC ADTS SHA identico** `3f1374c08615822bd8c2fd41597d98dbcc2335ca3235543e5e978d9feee44669`. I due Wright hanno **AAC ADTS SHA identico** `fc581c27651a29a47ecebcc53baddfd7bdf859f9b70b2a74b4242389362f825b`. Klimt Critico Museum AAC SHA `7e33f4a696f77033afddfad2f18562295b605c39cfd50a999bf94843907a53fe` coincide con il dossier V74; confronto diretto col suo Standard **non ripetuto**.

## Difetti visivi riproducibili: Socrate, focus frase–dettaglio

Fonte tempi: `VOICE_SHARED/GACRUX_SYNC_V66.json` dentro `ARTVISION_SOCRATES_4X1_COMPLETO_PILOTA_V67.zip` (ASR con interpolazioni, quindi i confini di frase richiedono ancora ascolto umano). Sono campioni del **vero video**, non simulazioni del renderer.

| Slot e beat ASR | Frase/soggetto | Fotogrammi campionati e osservazione | Esito |
|---|---|---|---|
| Critico Standard, beat 3, 29.90–48.36 s | Due mani di Socrate, una verso coppa, altra verso l'alto | 30.9 / 39.1 / 47.4 s: braccio verso coppa arriva al bordo sinistro, mano/coppa non entrambe leggibili; mano alzata visibile | `FOCUS_PARTIAL`, rivedere inquadratura senza tagliare l'altra mano |
| Critico Standard, beat 8, 107.64–121.40 s | Catene abbandonate sul pavimento | 108.6 / 114.5 / 120.4 s: prevale il giovane vestito di rosso; catene molto piccole in basso, non soggetto chiaramente centrato | `FOCUS_WEAK`, verificare con audio frase e crop sicuro |
| Critico Museum, beat 5, 64.40–76.70 s | Giovane vestito di rosso che porge coppa | 65.4 s: giovane visibile; 70.6 s: camera sul corpo di Socrate; 75.7 s: camera sui discepoli a destra | `FOCUS_DRIFT`, il soggetto nominato non rimane leggibile per tutto il beat |
| Critico Museum, beat 6, 77.273–91.12 s | Discepoli sulla destra | 78.3 s: gruppo visibile; 84.2 s: ritorno al centro su Socrate; 90.1 s: camera su Platone a sinistra | `FOCUS_DRIFT`, la camera anticipa il beat successivo |
| Critico Museum, beat 7, 92.32–106.26 s | Platone sulla sinistra | 93.3 s: Platone; 99.3 s: parte inferiore di Platone; 105.3 s: pavimento/piedi e cornice, volto non più leggibile | `FOCUS_DRIFT`, uscita dal soggetto troppo precoce |
| Critico Museum, beat 8, 107.64–121.40 s | Catene | 108.6 / 114.5 s: catene sul pavimento visibili; 120.4 s: camera ritorna al centro su Socrate | `FOCUS_END_DRIFT`, controllare parole finali e confine ASR |

Il beat 10 Museum 144.1–166.302 s mostra correttamente il rientro alla vista completa della tela; **non** correggere con un taglio secco. I cambi di campo Museum possono essere cinematicamente fluidi ma semanticamente in anticipo: il solo gate V57 sulla continuità non misura questa qualità.

## Wright e Klimt — riscontri visivi

- **Wright Critico Museum, 1 s:** quadro su parete grigia **senza la cornice dorata ottocentesca documentata** per NG725. V80: `frame_status=unverified` per il video, `museum_approved=false`. A 7/15/25 s appare il dettaglio dell'uccello; non promuovere il test a Gold Master. L'assenza di cornice è coerente con la precedente diagnosi V80, qui riconfermata su frame reale.
- **Wright Critico Standard:** campioni 15/25 s stesso dettaglio dell'uccello; 35/45 s stesso profilo; 55/65 s stesso volto di ragazza; 75/85 s stesso gruppo. La durata dei dettagli può essere giustificata dal parlato, ma va verificata contro WAV/ASR; non contare piccoli movimenti come scene nuove.
- **Klimt Critico Museum V73:** nei 12 campioni (4, 15, 28, 44, 60, 79, 98, 117, 138, 156, 176, 197 s) prevale sempre il dipinto quasi intero o un crop molto simile; spesso bordi di cornice/parete. Nessuna chiara alternanza di macro-dettagli dedicati a volti, mani, motivi geometrici e bordo del prato. Questo è un **rischio forte di monotonia/focus**, non ancora un verdetto frase-per-frase perché i timecode ASR Klimt non sono stati recuperati in questo run.
- **Klimt Cinema Museum V73:** 1/3/7 s mostrano ingresso con tela quadrata e cornice creativa; 12–36 s progressivo avvicinamento, 44 s ritorno. Camera visivamente coerente nei campioni, ma scoperte semantiche limitate; non richiede voce.
- **Socrate Cinema Standard/Museum:** campioni 1/3/7 e successivi estratti da file reali, progressione riconoscibile. Non emerso in questi campioni il problema degli spettatori tagliati del precedente V60; non equivale a controllo di ogni frame.

## Correzioni scoped proposte — NON eseguite

1. **Prima** di un nuovo rendering, usare la vera traccia Gacrux e timecode frase-per-frase per affinare i confini dei beat ASR, in particolare Socrate Museum 64–107 s. Salvare una shotlist con soggetto, rettangolo sicuro, inizio/fine effettivo e percorso continuo V57. Non applicare auto-crop cieco e non alterare i due master attuali.
2. Per Socrate Standard controllare la visibilità simultanea delle due mani al beat 3 e la leggibilità delle catene al beat 8. Un confronto A/B richiede un **nuovo MP4 reale** e nuovo SHA, nello stesso slot, soltanto dopo autorizzazione/possibilità tecnica; conservare l'originale.
3. Per Wright Museum cercare e documentare la cornice specifica NG725 e la licenza della fotografia di riferimento; nessuna cornice inventata. La V80 resta bloccante.
4. Per Klimt Critico Museum recuperare ASR reale dei nove beat, valutare se l'immagine nominata sia effettivamente in campo; mantenere WAV condiviso e la cornice dichiarata. Nessun re-render senza difetto e piano dimostrabili.
5. **PR #135 ancora DRAFT:** il gate `src/artvision_narrative_focus_gate.py` estrae un solo frame al midpoint per segmento e usa un unico `camera_crop_xyxy` statico per shot. Questo **non basta per una camera Museum dinamica**: i drift documentati richiedono campioni inizio/metà/fine, intervalli multipli o traiettoria `crop(t)`, più review umana. Non dichiarare il gate attivo su main finché non è integrato e testato.

## Stato finale

**8/8 file recuperati in questa sessione: SHA e full-decode PASS. 8/10 file richiesti con QA visiva a campione; 2 Klimt Standard non campionati. 0 nuovi MP4, 0 nuovi WAV, 0 V25, 0 import sito verificati, 0 social, 0 spese.** Il lock V58 continua a vietare nuove opere automatiche. Questa prova non modifica alcun master.
