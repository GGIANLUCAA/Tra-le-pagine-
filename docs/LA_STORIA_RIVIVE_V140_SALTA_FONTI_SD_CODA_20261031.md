# La Storia Rivive — V140 · Niente falsa produzione da fonti SD già note

Data 31 ottobre 2026. Solo sotto-progetto **Restauro storico**, issue #144 e mandato V108. Stacked sulla PR #154, nessun merge su main. ArtVision, WOW LAB, V98 e gateway/crediti Vidu invariati.

## Problema verificato

La coda editoriale V58/V121 contiene 10 sorgenti. Le sole tre dichiarate 1080p sono state realmente scaricate e collaudate, ma **nessuna** ha prodotto cinque riprese con movimento idoneo e revisione artistica:
- Francia, filatura 1920, SHA `e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9`: veto V132 per riprese non sufficientemente differenti dopo la revisione.
- Casa Bianca 1917–1921, SHA `db829527e66425bafdcfa9f3e6fc2d0bd17ffc13a43f62d56175e9bef1ac94a9`: [prova V136](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41192886652), una finestra di movimento.
- Versailles 1919, SHA `a29801c567fa7f237fed71a686b853a5c37e1323aed7a53c5a73265b975dadf8`: [prova V138](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41198837596), una finestra di movimento su nove candidati.

Le altre **sette** schede Commons indicano originali a risoluzione inferiore al minimo nativo V109 (altezza 720 px e almeno 400 px di larghezza utilizzabile nel ritaglio 9:16):
- Sei a 768×576 (crop utile circa **324 px**): `paris_swim_1918`, `paris_train_1918`, `beirut_1919_street`, `paris_cafe_strike_1919`, `paris_champs_1918`, `market_rural_1920`.
- Una a 720×480 (crop utile circa **270 px**): `china_daily_life_1928`.

Fonte e link puntuali delle schede: [audit V121 sette originali Commons](https://github.com/GGIANLUCAA/Tra-le-pagine-/blob/storia-v115-motion-window-tests/docs/LA_STORIA_RIVIVE_V121_AUDIT_RASTER_SETTE_FONTI_20261031.md). **Le risoluzioni dichiarate sono del file attualmente pubblicato**, non della pellicola ottica originale: se è disponibile una nuova scansione HD genuina, trattarla come un candidato nuovo dopo verifica di diritti, SHA e PTS.

## V140 — modifica gratuita

- File nuovo `config/storia_rivive_v140_low_raster_sources.json` con esattamente sette ID e URL archivistici, dimensioni nativamente pubblicate, data snapshot e riferimento della verifica. Non contiene file originali, API, token o licenze inventate.
- `src/storia_rivive_autopilot_v101.py` valida ogni voce (ID, URL identico alla coda, raster originale insufficiente, evidenza originale, no duplicati). Blocca un registry incoerente, una pagina cambiata o un raster già sopra soglia invece di dichiarare una fonte scartata senza prova.
- La rotazione V101 ora combina le tre esclusioni già documentate V133/V138 con le sette esclusioni V140; **10/10 candidate attuali risultano inadatte all'attuale pipeline 4+1**. Il lavoro di ricerca ad ogni slot 3h restituisce `SOURCE_RESEARCH_SKIPPED_NO_NATIVE_HD_CANDIDATES`, `skip_source_acquisition=true`, niente download e **nessuna generazione**. `WORK_ORDER.json` registra separatamente fonti rifiutate per movimento/arte e fonti sotto soglia nativa.
- Lo status `CYCLE_STATUS.json` conserva tale motivazione e indica come passo successivo la **scoperta di una nuova sorgente nativa HD**, non fingere che il video sia già `ASSETS_PENDING`.
- Il ciclo programmato rimane **di ricerca**, non viene soppresso e non diventa produttore di MP4; una nuova fonte autentica aggiunta alla coda può essere proposta, sempre con `paid_api_call_permitted=false`, `publish_permitted=false` e `human_approved=false`.

## Sicurezza, test e limiti

- `tests/test_storia_rivive_v140_native_raster_queue.py`: prova dati 6×576p + 1×480p, esito vuoto su 24 slot di tre ore, non elimina ipotetico nuovo candidato HD, URL cambiato, raster/stato incoerente, nessuna spesa o pubblicazione.
- GitHub Actions V109 e workflow 3h includono le regressioni V140; il risultato dei test va confermato sulla PR attuale.
- Nessun uso di DDColor/upscaling per inventare nitidezza, nessun diritto italiano dichiarato, nessun Vidu/I2I, nessun master. **0/3 nuovi piloti completi**.
- V140 non scopre in autonomia nuovi film HD; è soltanto il **filtro anti-spreco** per le dieci fonti conosciute. La successiva attività deve trovare altre pellicole autentiche o scansioni superiori da un archivio legittimo e con permessi territoriali verificabili.

Un rifiuto della scheda correntemente pubblicata non implica che un'altra digitalizzazione di qualità maggiore sia inadatta.
