# La Storia Rivive · V101: autopilota archivistico ogni tre ore

Aggiornamento 30/10/2026. Implementazione reale nel repository, separata da ArtVision 4×1 e WOW LAB.

## Meccanismo attivo
- Workflow: `.github/workflows/storia-rivive-v101-auto-3h.yml`; pianificazione UTC: `17 */3 * * *` (ogni 3 ore, con possibili ritardi GitHub). Trigger manuale disponibile nelle GitHub Actions.
- Modulo decisionale: `src/storia_rivive_autopilot_v101.py`, profilo `config/storia_rivive_autopilot_v101.json`, coda editoriale di fonti `queue/storia_rivive_candidates_v58.json`.
- Un solo ciclo per esecuzione; concorrenza limitata e cicli idempotenti per fascia oraria; scelta deterministica tra i candidati. **Rotazione delle fonti non significa nuovi video unici**.
- Selezione e acquisizione: `src/storia_rivive_scout_v101.py`, solo pagine Wikimedia Commons note e media da dominio ufficiale, con download limitato a 160 MiB per fonte, test ffprobe e 12 fotogrammi B/N originali per storyboard. Solo fonti controllate; gli errori sono registrati senza spacciarli per successo.
- Ranking: `src/storia_rivive_frame_rank_v101.py`, stima qualità dei frame originali a risoluzione nativa, propone cinque candidati senza attribuire identità, HD, diritti o qualità restaurata mai verificati.
- Titolo e bandiera: `src/storia_rivive_flag_title_v101.py`; PNG RGBA 720×1280, discreto e senza fascia opaca. In questa versione è supportato il tricolore storico francese per i soggetti Parigi con metadati periodo verificati. Per Stati con bandiere cambiate (es. Stati Uniti 1906, Regno d'Italia) **non** utilizzare bandiere moderne anacronistiche; estendere solo con asset/vettori storici revisionati. L'anteprima deve essere verificata anche sul filmato reale per non coprire volti/oggetti.
- Artefatti dell'esecuzione: ordine `WORK_ORDER.json`, stato `CYCLE_STATUS.json`, scheda immagini originali, ranking qualità, PNG titolo e fonte/provenienza; non pubblicare automaticamente.
- I media sono recuperati e conservati tramite cache GitHub soltanto in caso di successo dell'acquisizione. In caso di errori di rete non segnare i file come preparati.

## Ciò che NON fa ancora
Questa è la fase automatizzata di preparazione e scouting. **Non genera automaticamente quattro fotografie moderne I2I, la clip Vidu, il master MP4, la voce o il ZIP**. Non è corretta una dichiarazione di otto video prodotti al giorno. Prima di un'attivazione autonoma di rendering/animazione occorre verificare la disponibilità effettiva del servizio Finegrain o altro provider, i diritti reali, la sostenibilità di quota giornaliera, i timelock dei frame, i crediti Vidu prepagati e il gate di qualità sul video reale.

Non usare ChatGPT Plus come se concedesse chiamate API illimitate. Questo workflow non riceve credenziali né autorizzazione a usare provider a pagamento. GitHub Actions ha limiti/condizioni proprie e l'esecuzione di un job non equivale a consumo API fotografiche o Vidu.

## Contratto rigido per la fase di produzione futura
- Soltanto filmati originali legittimamente riutilizzabili come PD/CC0, verificati anche per il territorio e l'uso previsto. Separare colore/video ricostruito da contenuto storico originale.
- Conservare V98 San Francisco 1906 come benchmark minimo; V91/V94/V96/V99 obbligatori, e video completo guardato e ascoltato realmente. Nessun QA umano fittizio.
- Per adesso preset ufficiale: **quattro vere fotografie I2I + una clip Vidu** generata dalla stessa inquadratura/fotogramma storico. La seconda clip Vidu è solo una futura estensione che richiede modifica dei gate e preventivo crediti, mai aggirare il blocco esistente.
- Regia contenuto-dipendente: movimento autentico B/N → freeze sul vero frame → fotografia realistica fedele; clip Vidu con movimento realmente continuo e coerenza prospettica. Mai DDColor-only, volti/oggetti mutati, titoli troppo grandi, effetto seppia o palette incoerente.
- Verificare il MP4 effettivo H264/AAC, fps/risoluzione effettivi, continuità sonora, cover, post social e ZIP Android; link e playback reali prima della consegna. Pubblicazione social/sito separata e solo quando autorizzata.
- Loop qualità: log con SHA dei file, difetti scena/tempo e causa, comparazione A/B con V98, promozione dei miglioramenti solo dopo test; saltare il ciclo se materiale insufficiente.
- Bloccare spese, rinnovi, ricariche, retry di provider a pagamento e pubblicazione non autorizzati. Le quote e condizioni dei servizi si verificano prima di ogni nuovo regime.

## Comandi gratuiti di diagnostica
```bash
python -m unittest discover -s tests -p test_storia_rivive_v101.py -v
python src/storia_rivive_autopilot_v101.py --now 2026-10-30T15:00:00Z --out output/storia_v101/WORK_ORDER.json
```

Gli stati tecnici possibili comprendono `SOURCE_PREFLIGHT_REVIEW_REQUIRED`, `SOURCE_SCOUT_BLOCKED_NO_PRODUCTION`, `REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW`; non equivalgono mai a `FINAL` o `PUBLISHED`.


## Estensione V102 — contratti I2I source-locked (30/10/2026)
- `src/storia_rivive_i2i_prepare_v102.py` trasforma cinque fotogrammi PNG autentici estratti dal filmato in cinque richieste I2I con SHA256 di origine, prompt anti-allucinazione e ruoli (4 fotografie + 1 riferimento per Vidu).
- Output in ogni esecuzione: `I2I_INPUT_MANIFEST_V102.json`. L'output contiene **zero fotografie generate**, **zero chiamate API**, nessuna attestazione di volti approvati e nessuna autorizzazione di pubblicazione.
- Il modulo verifica presenza, decodificabilità, dimensioni e unicità dei cinque frame. Non confondere fotogrammi distinti per tempo con cinque inquadrature realmente differenti: serve controllo visivo.
- La successiva integrazione con un provider gratuito/approvato deve consumare solo queste richieste, controllare quota/costi reali, registrare input/output SHA e scartare qualsiasi scena con geometria/identità alterate. Non usare provider a pagamento in automatico senza consenso esplicito.

## Estensione V109 — qualità nativa e fonte verificata (30/10/2026)

Nel run V101 [41069093458](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41069093458) l'ordine Beirut aveva `SOURCE_PREFLIGHT_REVIEW_REQUIRED`, ma V102 preparava comunque cinque job I2I. Questo era un **falso avanzamento del preflight**, non una generazione fotografica. Il precedente China V107 (720×480) aveva dimostrato un altro limite: il crop 9:16 contiene appena ~270 pixel nativi orizzontali e non consente di ricostruire fedelmente volti minuti con il solo ingrandimento.

**Patch V109 (PR #145, in revisione):** il ranking V101 ora pre-seleziona cinque frame solo quando il crop verticale nativo raggiunge almeno **400 px di larghezza** e la sorgente ha almeno **720 px di altezza**; in caso contrario restituisce `SOURCE_NATIVE_DETAIL_INSUFFICIENT_FOR_FIVE_SHOTS` e zero frame pre-selezionati. Questo è un **filtro minimo tecnico**, non prova di cinque riprese diverse, volti nitidi, autenticità o diritti. V102 blocca inoltre la preparazione se `blocking_issues` del V101 è assente o non vuoto (inclusa verifica diritti Italia), se `SCOUT_REPORT.json` manca/non è pronto, se SHA del film non coincide con il rapporto, se un frame non soddisfa le dimensioni native o se due frame sono identici per SHA nonostante nomi differenti. `CYCLE_STATUS.json` espone `SOURCE_REJECTED` per insufficienza nativa, oppure `ASSETS_PENDING` per verifiche/asset ancora da completare.

Nessuna spesa Vidu, nessuna I2I eseguita, nessuna pubblicazione. Un `SOURCE_REJECTED` significa **cambiare fonte** (oppure trovare una scansione nativa migliore), non aggirare il gate con upscale, crop multipli o dichiarazioni fittizie. Anche con V109 PASS, servono cinque **vere riprese diverse** accertate, quattro I2I fedeli, un Vidu source-locked, V91/V94/V96/V99 e revisione artistica prima di chiamare un video completo. Le soglie sono conservative e potranno essere calibrate soltanto con esempi reali confrontati al benchmark V98, non per ottenere PASS artificiosi.

## V110 — blocco composizioni quasi identiche prima del provider I2I (30/10/2026)

In estensione alla PR #145, V102 applica ora `visual_near_duplicate_guard` ai **cinque PNG realmente estratti**. Confronta le composizioni in scala di grigi normalizzata su griglia 64×64, così una stessa inquadratura salvata con luminosità/contrasto leggermente diversi e SHA differenti non può più passare come cinque fonti diverse. La presenza di una coppia quasi identica produce `I2I_INPUTS_BLOCKED` con motivo `VISUAL_NEAR_DUPLICATE_SOURCE_FRAMES`, **prima** di qualsiasi chiamata a provider. Il controllo è offline, economico e non usa chiavi.

**Limite esplicito:** la mancanza di coppie quasi identiche NON certifica cinque riprese/cambi camera autentici. Il manifest conserva `historical_shot_distinctness_verified=false` e `scene_distinctness_gate=PENDING`; sono ancora obbligatori confronto del girato, confini delle riprese, timecode reali, fonte e diritti Italia, volti e oggetti. Il controllo è conservativo e può rifiutare scene volutamente simili: in quel caso scegliere un'altra ripresa realmente diversa, non abbassare arbitrariamente la soglia. Non si sono generate foto I2I, clip Vidu o master con questa patch.

Test offline: una scena con cinque PNG a esposizioni diverse viene bloccata; cinque composizioni sintetiche diverse non producono falsi PASS artistici. La suite del workflow V109 verifica anche i gate V101/V102 già esistenti. Nessun impatto su ArtVision/WOW LAB e nessuna modifica al cron di master.

## V111 — SHA dei frame estratti legato al film originale (30/10/2026)

Problema reale: V102 controllava lo SHA del film e gli SHA dei PNG *presenti al momento della preparazione*, ma il rapporto scout non conservava alcuna impronta dei singoli frame. Un PNG sostituito in cache dopo l'estrazione poteva quindi diventare una richiesta I2I formalmente «source-locked» pur non essendo più il frame prodotto dallo scout.

Correzione proposta nella PR #145: lo scout salva in `SCOUT_REPORT.json` la lista `frame_provenance` con nome, SHA-256 di ogni PNG, indice di estrazione e SHA del film. V102 confronta i byte effettivi di ciascun frame selezionato con questa lista e rifiuta frame sostituiti, non elencati o report legacy privi della prova. La cache dello scout passa da v3 a v4 per rigenerare i rapporti anziché riutilizzare vecchie cache incompatibili. Tutto offline, nessuna richiesta I2I o Vidu.

**Limite esplicito:** l'hash dimostra corrispondenza al PNG estratto e al report del ciclo, NON certifica il timecode originale esatto né cinque veri cambi di camera. Il campionamento FFmpeg `fps` rimane approssimativo; `exact_source_timecode_verified=false` e `historical_camera_shot_verified=false`. Per un freeze esatto e una clip Vidu dalla quinta ripresa serve un'ulteriore verifica temporale sul video originale, oltre a diritti Italia e revisione visiva. La modifica non cambia i gate economici né la schedulazione dei master.
