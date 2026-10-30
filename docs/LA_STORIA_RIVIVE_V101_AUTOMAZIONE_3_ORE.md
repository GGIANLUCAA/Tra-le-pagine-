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
