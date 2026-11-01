# La Storia Rivive · V183 — produzione pilota: selezione materiale (01/11/2026)

Stato: **PREPRODUZIONE / NON MASTER**. Issue #144; V108 e benchmark V98 vincolanti.

## Candidato prioritario
*A Corner in Wheat* (1909), D. W. Griffith — due link video Library of Congress individuati nel lavoro V176, ma **non ancora verificati** come copie con dettaglio nativo adeguato. Non dichiarare cinque riprese, licenza italiana o qualità HD senza analisi sui byte.

## Prossima esecuzione concreta
1. Recuperare le due risorse LOC già individuate; verificare URL, termini di riuso e restrizioni per l'Italia (se non determinabili: blocco).
2. Scaricare un solo file originale senza upscaling; ffprobe per risoluzione/fps/durata e SHA256; se SD, scartare il candidato.
3. Se la fonte è idonea, estrarre storyboard con almeno cinque vere inquadrature differenti, ciascuna con timecode e frame SHA, e revisione visiva.
4. Soltanto dopo verifiche positive, avviare quattro I2I autentici con QA e un Vidu source-locked usando il gate di autorizzazione per scena. Nessuna spesa automatica implicita.
5. Montaggio 14–35 s e gate V91/V94/V96/V99; MP4/ZIP Android solo dopo test reali, senza pubblicazione.

## Limiti verificati
Questa modifica è un handoff editoriale, **non** un episodio prodotto. Nessun MP4, I2I, Vidu, saldo o diritto verificato in questa esecuzione. V98, ArtVision, WOW LAB e cron esistenti invariati.


## V184 — riscontro archivistico e acquisizione locale fail-closed
- Scheda LOC ufficiale: https://www.loc.gov/item/2012600307/ (film **di finzione** del 1909, NON documentario di eventi realmente accaduti). Il soggetto è la speculazione sul grano; non descrivere le scene recitate come riprese spontanee della vita quotidiana.
- Copia Commons collegata alla LOC: https://commons.wikimedia.org/wiki/File:A_Corner_in_Wheat_(1909).webm . Metadati pubblici della pagina: **1436×1080**, **1.641.628.267 byte**, **820,708 s**, codec/container WebM VP9; checksum pubblicato SHA-1 `3583531ea3d56cc1cc6aa3ef22360b2e3265e524`. Questi sono metadati dichiarati dalla pagina, **non ffprobe o SHA calcolati su byte scaricati**.
- Copia alternativa Commons https://commons.wikimedia.org/wiki/File:Corner_in_Wheat.webm : **480×360**, quindi scartata a monte per V108. La versione 1436×1080 eccede il limite di download automatico V101 **160 MiB**: non aggirare con upscaling o scaricamenti senza limite. Eventuali transcode 720p sono derivati e non scansioni native; richiedono QA del dettaglio effettivo.
- La pagina LOC dichiara che il copyright estero va verificato; la scheda Commons attesta il pubblico dominio **negli USA**, non un'autorizzazione territoriale italiana. Diritti Italia **PENDING**; nessun provider o pubblicazione.
- Nuovo `src/storia_rivive_v184_source_intake.py`: controllo gratuito su file locale già acquisito legittimamente, SHA256 in streaming, ffprobe su byte reali, rifiuto SD/corruzione/SHA errato; report `ASSETS_PENDING` o `SOURCE_REJECTED` con `provider_jobs_may_start=false` e `publish_permitted=false`. Non tenta di scaricare 1,53 GB su GitHub Actions e non dichiara cinque inquadrature o diritti verificati.
- Test offline `tests/test_storia_rivive_v184_source_intake.py` e CI `.github/workflows/storia-v184-source-intake.yml`: sei regressioni + due file video sintetici FFmpeg per prova su byte veri; esito CI da controllare separatamente. Non è ancora stato testato sul film LOC.

**Stato produttivo dopo V184:** nessuna nuova fotografia I2I, clip Vidu o MP4; il candidato resta bloccato per verifica effettiva del file, cinque riprese e diritti Italia. ArtVision, WOW LAB, V98, V101 cron e gateway Vidu invariati.

## V185 — scouting vero sui frame nativi, senza inventare cinque riprese

- Nuovo `src/storia_rivive_v185_storyboard_scout.py`: legge una pellicola **locale** e SHA-locked, richiama V184 (rifiuto SD), decodifica realmente con FFmpeg, individua possibili stacchi con `scene` su proxy 320 px e salva cinque **PNG originali a risoluzione nativa** con SHA-256 distinti. La proxy è soltanto per la ricerca, **non** una foto restaurata né un upscaling.
- Non riutilizza la stessa inquadratura per riempire la cinquina se ci sono pochi tagli; `SCOUT_BLOCKED` se meno di cinque candidati, hash errato, media SD, symlink o errore FFmpeg. Non sovrascrive una cartella già esistente.
- Il manifest `V185_STORYBOARD.json` dichiara sempre `five_distinct_shots_verified=false`, `freeze_pts_verified=false`, `rights_italy_verified=false`, `provider_jobs_may_start=false`, `publish_permitted=false`. I tagli rilevati automaticamente NON provano che cinque riprese siano diverse, né l'esatto frame finale di freeze. Per gli errori si può salvare `--report /percorso/report.json`.
- Uso quando il vero film HD sarà stato acquisito legittimamente: `python src/storia_rivive_v185_storyboard_scout.py --file /percorso/film.webm --expected-sha256 <sha256-reale> --out-dir /percorso/storyboard --report /percorso/report.json`. **Non eseguire finché manca il file vero**.
- Test locali eseguiti su byte di MP4 sintetici reali: **8/8 PASS** (sei scene, una sola scena, SD, SHA errato/mancante, symlink padre, output preesistente, errore FFmpeg). CI separata `.github/workflows/storia-v185-storyboard-scout.yml` da verificare sul commit.
- Nessun film LOC 1,64 GB acquisito, nessuna revisione diritti Italia, nessun I2I/Vidu, nessun MP4 finale, nessuna spesa. V98, ArtVision, WOW LAB, gateway e cron V101 non modificati.

**CI V185 verificata:** [GitHub Actions run 41326318434](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41326318434) **SUCCESS**, 8/8 test real-byte sintetici. Primo run 41326254841 fallito perché FFmpeg non era installato sul runner; corretto installando FFmpeg nel workflow (commit 558c6b3). V184 in parallelo [run 41326318442](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41326318442) **SUCCESS**. Questi test non equivalgono alla prova sul film archivistico HD.


## V186 — primo tentativo reale di scouting HD su derivato Commons (01/11/2026)
- `src/storia_rivive_v186_commons_preview.py` interroga la API ufficiale Commons, seleziona **soltanto** il transcode 1080p WEBM su `upload.wikimedia.org` (se presente), blocca redirect esterni, download >420 MiB o >420 secondi, calcola SHA-256 sui **byte realmente scaricati**, passa V184 con ffprobe e campiona cinque PNG di fotogrammi della vera pellicola (non immagini AI).
- Questo è esplicitamente un **derivato compresso 1080p**, NON la fonte originale da 1,64 GB né prova di qualità artistica/nativa; cinque istanti distanti non certificano cinque inquadrature diverse, il frame esatto, né I2I/Vidu. Rimuove il WEBM grande dopo l'analisi; artifact GitHub Actions solo con PNG e rapporto, retention 3 giorni. Il job di rete è un singolo tentativo gratuito, mentre il job test genera e decodifica un MP4 sintetico 720p reale.
- Workflow: `.github/workflows/storia-v186-commons-hd-preview.yml` sulla PR del ramo corrente; eventuali errori di rete devono apparire nel JSON `SOURCE_PREVIEW_BLOCKED` e **mai** essere riportati come successo di acquisizione solo perché il job workflow è verde.
- **Revisione normativa preliminare, non approvazione alla pubblicazione**: L. 633/1941 art. 32, fine protezione economica 70 anni dopo la morte dell'ultimo tra regista/sceneggiatori/autore dialoghi/autore musica creata per l'opera: https://www.wipo.int/wipolex/en/legislation/details/21564 . LOC identifica D. W. Griffith (morto 1948) e Frank E. Woods come scrittori: https://www.loc.gov/item/2012600307/ . Woods morto 1939 secondo ACMI: https://www.acmi.net.au/creators/82186--frank-woods/ . Questa cronologia rende plausibile dominio pubblico in Italia per l'opera cinematografica originale dal 2019 **solo se non emerge un altro avente diritto rilevante**; la dichiarazione PD-US di Commons non basta, restano da verificare diritti della specifica copia, nuovi contributi, musica, condizioni d'archivio e destinazione italiana.
- Stato di questa modifica prima del controllo artifact: **PREVIEW/SCOUTING**, non quattro vere foto I2I, non clip Vidu, non MP4 finito, non pubblicazione. V98, altri formati, gateway e cron V101 invariati.


### V186 — esito verificato sui byte reali (run 41328767134)
- **8/8 test PASS** GitHub Actions, compreso un MP4 sintetico codificato e decodificato; job di acquisizione **eseguito e riuscito**, non soltanto preparato.
- Derivato Wikimedia realmente scaricato: 317.953.864 byte, VP9 **1436×1080**, 820,709 s, SHA-256 `eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9`. Il SHA documenta il **transcode** 1080p e non l'originale archivistico da 1,64 GB.
- 5 veri PNG estratti dal derivato, SHA-256 ricalcolati sullo ZIP dell'artifact e tutti corrispondenti al manifest. PTS richiesti: **82,071; 205,177; 344,698; 492,425; 656,567 s** (PTS del frame decodificato non ancora verificati).
- **Revisione visiva reale su contact sheet, non approvazione artistica**: (1) campo con contadini lontani e piccoli; (2) vivace scena di borsa/affollamento; (3) e (4) stessa situazione di banchetto ricco con punti di vista/gesti simili, **non utilizzabili entrambe** nella cinquina finale; (5) negozio del pane con cartello inglese molto evidente. La fotografia 1 rischia di restare poco leggibile nel 9:16. La cinquina così com'è **NON passa** la revisione sulle cinque riprese varie e fotogeniche.
- Artifact GitHub Action `v186-authentic-film-previews-review-only`, ID `13092427221`, 5.182.810 bytes, scadenza **04/11/2026 16:55 UTC**, scaricato e controllato byte-per-byte dal connettore; report e PNG verificati, **nessun MP4 finale**. Run https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41328767134 .
- Prossimo intervento: scouting più fitto degli stacchi di camera per scegliere davvero cinque inquadrature VISIVAMENTE diverse e con soggetti leggibili; mantenere blocchi I2I/Vidu/diritti finché non completata la review. Nessuna spesa, nessuna pubblicazione.


## V187 — catalogo reale di stacchi + correzione anti-intertitoli (01/11/2026)
- Nuovo `src/storia_rivive_v187_shot_catalog.py`: legge solo derivato HD SHA-locked già identificato da V186; FFmpeg cerca **stacchi reali ipotizzati** su proxy 320px/2fps, sceglie intervalli delimitati da tagli, estrae PNG del film a risoluzione originale del derivato con SHA e prova a scartare quasi-duplicati. Il proxy è solo per analisi, **mai** presentato come foto I2I.
- Workflow `.github/workflows/storia-v187-shot-catalog.yml` con sei test (incluse sequenze MP4 sintetiche realmente decodificate), un solo download ufficiale Wikimedia entro limiti V186 e controllo obbligatorio SHA `eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9`. **Run reale verificato** https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41331040749 : **SUCCESS**, 6/6 test; **31 tagli algoritmici**, **10 fotogrammi di revisione** estratti e SHA verificati su file artifact `13093366066` (9.316.263 bytes). I 10 PNG non sono dieci riprese umanamente certificate.
- Revisione umana della contact sheet **effettivamente eseguita**: il frame `shot_05` a 321,25s è un **cartello narrativo su fondo nero**, NON una ripresa utile; la coppia `shot_01/07` riprende l'ambiente rurale, `shot_03/09` l'ufficio, `shot_02/10` il campo; il detector ha già scartato due candidati per somiglianza grezza. La shortlist **solo editoriale, NON approvata** è `shot_01` 34,25s (contadini), `shot_03` 162,25s (finanzieri), `shot_04` 226s (borsa), `shot_06` 449,25s (banchetto), `shot_08` 641s (granaio). Tutti sono scene **recitate di finzione del 1909**, non eventi documentari spontanei. La qualità dei volti/scene per restauro V98 resta **NON VALIDATA**.
- Correzione V187 successiva: `dark_or_title_like` scarta frame quasi neri/intertitoli come il vero `shot_05` (firma 9×8: luminanza media circa 3,7 su 255, 100% campioni <35). Nuovo test di regressione; è un filtro conservativo che potrebbe scartare scene molto scure, non riconoscimento semantico garantito. **Non dichiarare che questa correzione sia stata verificata sul film HD finché non rieseguito il catalogo con il nuovo commit**.
- Per evitare ripetuti download di ~318MB a ogni commit della PR, i job di acquisizione V186/V187 sono stati resi **manual-only**; V187 ha una singola eccezione per il commit esplicito `RUN_REAL_SCOUT_V187_ONCE`. Nessun job automatico a pagamento, nessuna modifica al cron V101 o al gateway Vidu.
- **Blocco attuale**: verifica territoriale italiana e qualità della fonte, scelta finale delle 5 riprese con movimento B/N e freeze esatto, quattro restauri generativi I2I, singola clip Vidu autorizzata e QA V91/V94/V96/V99. Zero MP4 finale, zero addebiti, zero pubblicazioni.

- **Prova aggiuntiva sul vero intertitolo**: estratto `shot_05.png` dall'artifact V187 e passato realmente a FFmpeg `scale=9:8,format=gray`; media luma **0,64/255**, frazione campioni <35 **100%**, `dark_or_title_like=True`. I fotogrammi reali `shot_01/03/04/06/08` hanno invece `False`. **7/7 test locali PASS** con media sintetici realmente codificati; la CI del nuovo filtro va verificata separatamente, senza confonderla con il precedente run 6/6.
