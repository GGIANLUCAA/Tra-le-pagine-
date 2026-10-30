# La Storia Rivive — V99 · Sistema anti-regressione dal V98 accettato

**Decisione dell'utente, 30/10/2026:** «Questo lo posso considerare un lavoro accettabile» per **San Francisco 1906 V98**, che diventa il **minimo qualitativo di riferimento**, non lo stampino obbligatorio per qualunque soggetto.

## Riferimento autentico, non inventato
- Release pubblica verificata: https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/tag/storia-rivive-san-francisco-1906-v98-4-real-i2i-1-real-vidu
- MP4: `LA_STORIA_RIVIVE_SF1906_V98_FOUR_REAL_I2I_ONE_REAL_VIDU.mp4`
- SHA-256 IMMODIFICABILE: `b20726893e067bbae493859ae1c51379c4abab8c2c8768d5c6f2d4ab324b47a8`
- Media: 720×1280, 30 fps, H.264/AAC, 19,567 secondi.
- `src/storia_rivive_v99_golden_benchmark.py` apre **i veri fotogrammi** del riferimento, misura visibilità del colore, movimento originale e movimento Vidu dopo il reveal.
- Workflow di test: `.github/workflows/storia-v99-golden-regression.yml`, senza API a pagamento.
- Eseguite 12 verifiche di regressione sul file originale; non sostituire l'MP4 con un nome o un rapporto simulato.

**Nota importante del vero benchmark:** la terza fotografia di V98 ha colore tenue (guadagno di saturazione modesto ~2,89 in una misurazione). Quindi le soglie sono tarate sul V98 **reale**, non su valori inventati che boccierebbero proprio il video accettato. Questo non impedisce di migliorare una fotografia poco vivida quando la sua fonte lo consente.

## Come deve procedere ogni produzione
1. **Storyboard prima delle API:** almeno cinque riprese storiche differenti, fonte verificabile, filmato autentico in movimento, identità di persone/oggetti, timecode esatto e diritti. Il filmato non deve diventare cinque zoom dello stesso fotogramma.
2. **Restauro fotografico:** quattro veri image-to-image source-locked. DDColor da solo NON è una foto moderna; niente volti inventati, auto trasformate in persone, facce plastiche. Il file immagine reale e la sua impronta SHA sono input obbligatori.
3. **Solo una scena Vidu:** il primo frame della clip Vidu deve coincidere con la stessa inquadratura/freeze del filmato autentico. B/N in movimento → primo secondo di colore su frame animati → circa altri quattro secondi di movimento reale generato. Un solo POST a pagamento, registro prima dell'invio, tetto del credito già autorizzato; mai tentativi di pagamento ambigui ripetuti. Riutilizzare clip pagate solo se *la medesima scena autentica* è coerente.
4. **Montaggio sul metodo V98:** solitamente 1–2s B/N, transizione breve, 1–2,5s per apprezzare la fotografia restaurata; tempi variabili per contenuto, senza riempitivi, con audio unico continuo. Titoli brevi in inglese in zona libera, senza fasce opache che coprono mani/volti/oggetti.
5. **QA tecnico SU VERO MP4:** il gate V99 legge il filmato finale, 4 foto, 5 immagini B/N autentiche, sorgente originale integrale e MP4 Vidu; confronta gli SHA e i fotogrammi REALI. Controlla durata, H.264/AAC, corrispondenza filmato↔foto↔Vidu, presenza di colore, movimento Vidu dopo la colorazione, differenze rispetto al benchmark V98. Esito `BLOCKED` significa che **non** è pronto.
6. **QA artistico distinto:** guardare il video completo con audio a velocità naturale e verificare davvero volti, mani, occhi, oggetti, colore, scelte registiche, primi secondi e finale. Confrontare il contact sheet con V98. Nessuna metrica automatica può certificare che un volto sia fedele al passato o che il pubblico reagirà bene. Risolvere i problemi e ricontrollare; non scrivere `approved=true` per evitare una bocciatura.
7. **Gate di consegna:** il `src/storia_rivive_final_gate_v91.py` integra V94+V96 e ora richiede anche **V99 ricalcolato sui byte dell'MP4**. Senza sorgente d'archivio, immagini reali e reference V98 verificabile, **niente etichetta «finale»**. Per nuove workflow è obbligatorio invocare questo gate prima della GitHub Release finale. È consentito pubblicare *solo una prerelease di revisione* chiaramente etichettata come tale, e non sui social/sito senza approvazione e diritti.
8. **Consegna verificata:** MP4 vero e decodificabile, musica, ZIP Android con copertina, 4 descrizioni social, report QA, link GitHub Release diretto funzionante. Non chiamare `Library file not found` un risultato consegnato.

## Uso tecnico della comparazione
Per ogni nuovo video storico finale, preparare una cartella di asset verificati con:
- film originale integrale, 5 fotogrammi originali sorgente (con SHA e timecode), 4 foto realmente generate image-to-image, 1 vero MP4 Vidu;
- manifest `format=storia_rivive`, `project_format=4classic_1vidu`, scene in ordine con `kind`, `start_s`, `duration_s`, `bw_motion_s`, `source_film_sha256`, `source_timecode_s`;
- per ogni classica: `reveal_s`, `color_photo_hold_s`, `restoration_model`, `source_frame_file`, `source_frame_sha256`, `restored_photo_file`, `restored_photo_sha256`, `source_crop={left,width}`;
- per Vidu: `source_frame_file`, `source_frame_sha256`, `vidu_clip_file`, `vidu_clip_sha256`, `source_crop`;
- globali: `historical_film_file`, `historical_film_sha256`, `final_video_sha256`, dati di QA artistico e diritti.

Esempi di esecuzione sul runner GitHub (nessuna API Vidu necessaria):

```bash
python src/storia_rivive_v99_golden_benchmark.py --mode reference \
  --video riferimento_V98.mp4 --output V98_REFERENCE.json

python src/storia_rivive_v99_golden_benchmark.py --mode candidate \
  --video NUOVO_VIDEO.mp4 --reference riferimento_V98.mp4 \
  --manifest NUOVO_MASTER_QA.json --assets dir_asset_verificati/ \
  --output V99_CANDIDATE_TECHNICAL_QA.json

python src/storia_rivive_final_gate_v91.py \
  --video NUOVO_VIDEO.mp4 --manifest NUOVO_MASTER_QA.json \
  --v99-golden-reference riferimento_V98.mp4 \
  --v99-source-assets dir_asset_verificati/
```

I controlli sono **fail-closed**: se il soggetto del frame reale non corrisponde al frame usato in Vidu, se la foto non compare nel video, se manca il file Vidu o se il video non si muove a colori, il risultato è **BOCCIATO**. Non rigenerare Vidu a pagamento per correggere errori che dipendono dal montaggio.

## Non promettere ciò che non è stato fatto
- La V99 automatizzata può dare soltanto `TECHNICAL_PASS_REVIEW_PENDING`, non «perfetto», «approvato dall'utente» o «pubblicato».
- Il controllo CI V99 per il golden **non verifica automaticamente tutti gli altri workflow**: ogni nuova pipeline di produzione deve invocarlo prima del rilascio o usare il gate V91.
- Comparazione visiva A/B con il V98, revisione dei volti e autorizzazione di pubblicazione restano passaggi separati, reali.
- I quadri ArtVision 4×1 non sono interessati: questo è per `La Storia Rivive` soltanto.

## Migliorare senza rompere
Cambiare una sola causa qualitativa significativa alla volta (per esempio dettaglio foto oppure raccordo colore), generare la variante, confrontare fianco a fianco col V98 e con gli ultimi esempi dell'utente, misurare se migliora. Se peggiora, scartare la variante e tornare all'ultimo video buono. Conservare MP4, seed, sorgenti e parametri dei lavori approvati per regressioni future.
