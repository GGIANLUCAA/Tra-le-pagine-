# La Storia Rivive V98.1 · Bombay gennaio 1929 · revisione tecnica (30/10/2026)

**Stato:** MP4 reale di 19,133 s, H264/AAC, 720×1280 a 30fps, GitHub Release e ZIP Android verificati; **revisione artistica dell'utente e diritti in Italia ancora da confermare**. Non è stato pubblicato su social/sito.

## Correzioni realmente applicate rispetto a V92 / New York V95
- Cinque riprese storiche diverse: **#2** edificio/folla, **#7** mercato, **#4** lavoratori, **#5** strada/negozi, **#8** gruppo di uomini.
- Quattro fotografie #2/#7/#4/#5 effettivamente rigenerate con **Finegrain image-to-image gratuito**, non soltanto colore DDColor; per tutte sono conservati fotogramma originale, SHA e confronto visivo. Il modello gratuito ha raggiunto il limite di quota dopo tre foto, e le altre due sono state ottenute in un secondo runner gratuito, SENZA pagare immagini né riusare foto precedenti inappropriatamente.
- Unica scena Vidu #8, Q2 Pro Fast 5s, **task 1013676856496373760**, **16 crediti API prepagati**, ledger unico `queue/vidu_api_attempts/20261030_V98_BOMBAY_1929_PEOPLE_08_SINGLE.json`. Un solo POST a pagamento, nessun retry.
- La quinta scena mostra **prima la propria pellicola B/N autentica in movimento**, non il taglio arbitrario da un'altra inquadratura che aveva rovinato New York. La prima immagine della generazione Vidu corrisponde al fotogramma originale con correlazione geometrica circa **0,987**, poi il colore arriva nel primo secondo della clip generata e il movimento continua davvero a colori. Il confronto è tecnico, non certificazione delle identità storiche.
- Titolo inglese piccolo `BOMBAY · 1929`, senza fascia opaca su persone/merci; cinque scene distinte in **19,133 s**, 4 effetti film→freeze→foto e 1 Vidu, unico audio originale continuo.
- Nel primo MP4 V98 un tappeto rosso e un fondale turchese della scena lavoratori risultavano troppo saturi. **V98.1** corregge SOLO il segmento **6,60–9,76 s** mediante riduzione cromatica a ~68%, NON altera il Vidu né le foto sorgenti. Codifica completa e ZIP verificati.
- **Limitazioni:** alcuni volti minuscoli nei campi lunghi restano interpretativi perché i fotogrammi storici non contengono dettagli sufficienti. Vidu introduce sottili microgesti facciali e possibili discrepanze d'interpretazione: non dichiarare il video prova storica colorata, né approvato artisticamente senza revisione umana completa.

## Download verificati
- MP4 V98.1: https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/storia-rivive-bombay-1929-v981-natural-color-real-vidu/BOMBAY_1929_V981_NATURAL_COLOR_4PLUS1.mp4
- ZIP Android: https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/storia-rivive-bombay-1929-v981-natural-color-real-vidu/BOMBAY_1929_V981_ANDROID.zip
- Release review: https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/tag/storia-rivive-bombay-1929-v981-natural-color-real-vidu

## Ricetta riproducibile
`src/storia_v98_bombay_five_photos.py` e `src/storia_v98_bombay_complete_remaining.py` per foto source-locked; `src/storia_v98_bombay_vidu_once.py` per unica clip; `src/storia_v98_bombay_hybrid_compose.py` per video; workflows `.github/workflows/storia-v98-bombay-one-vidu-video.yml` e `.github/workflows/storia-v981-bombay-natural-color.yml` per creazione/rifinitura. Regole V91/V94/V96 rimangono vincolanti: **H264/AAC e movimento misurato non equivalgono ad approvazione artistica**.