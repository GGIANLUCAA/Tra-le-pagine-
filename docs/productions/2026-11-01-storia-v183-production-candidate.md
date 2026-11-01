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
