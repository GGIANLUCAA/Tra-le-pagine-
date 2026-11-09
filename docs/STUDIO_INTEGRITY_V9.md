# Studio Integrity V9 — audit mirato e ZIP V55 (09/11/2026)

## Perché
Il Centro di controllo V8 ha verificato la connettività dell'archivio con HTTP 206 e i **primi 1024 byte** di alcuni MP4. Non equivale alla verifica integrale né all'approvazione artistica. V161 già copre con SHA l'intero insieme di 17 master pinnati, ma rilanciare tutti i download per controllare un singolo dubbio è inefficiente.

## Funzionalità
- `src/studio_integrity_v9.py` seleziona **solo** uno dei 17 master già elencati da `src/video_library_site_download_audit_v161.py::expected()`. Il percorso, la dimensione e lo SHA sono dichiarati e controllati nel registro owner, non inviati da una pagina web.
- Richiede prima HTTP 206 con `Content-Range: bytes 0-1023/<dimensione>` e legge esattamente 1024 byte; quindi, con una seconda richiesta GET, scarica in streaming l'**intero MP4**, calcolando SHA-256 e byte reali. Rifiuta redirect, dimensione diversa, MIME errato, hash errato e file maggiori di 250 MiB. Tutto in sola lettura, una sola prova per volta, senza pagare provider video.
- `verify_zip`: quando esiste un **file ZIP locale V55** con SHA atteso, confronta SHA-256, struttura contenuti (MP4, copertina, quattro post, fonti), CRC di ogni elemento, presenza di percorsi sicuri, limiti per file/numero totale. Non estrae e non pubblica niente. Il workflow online NON afferma di avere un ZIP se il file non è disponibile.
- `STUDIO_INTEGRITY_V9_ONE_MASTER`: GitHub Actions `workflow_dispatch` **manuale**, scegliendo l'indice del singolo master (1–17). Il rapporto `INTEGRITY_REPORT_V9.json` è allegato come artifact per 14 giorni anche se il test fallisce. Nessun `schedule`, render, codice master alterato o deploy.
- Centro di controllo: `GET /api/integrity` e pagina **Qualità e prove** con gli ultimi audit manuali e il link per avviarli su GitHub. Il pannello consulta soltanto i **metadati degli artifact**, NON apre i loro JSON: quindi non trasforma mai una run GitHub riuscita in prova SHA o Gold senza leggerne i risultati.

## Come usarlo
1. Apri **Qualità e prove** → **Seleziona MP4 e avvia su GitHub**. Scegli il numero 1–17, seguendo lo stesso ordine dei master dichiarati nella lista `selected` del file V161.
2. Aspetta il completamento GitHub Actions. Apri **Vedi il rapporto GitHub**, poi l'artifact `STUDIO_INTEGRITY_V9_ONE_MASTER` e leggi `INTEGRITY_REPORT_V9.json`.
3. Il campo `mp4_full_download_verified: true` richiede Range, byte integrali e hash corretti; `false` oppure artifact mancante significa **non verificato**.
4. Quando si dispone di un ZIP V55 in una cartella locale e di uno SHA noto:
```bash
python src/studio_integrity_v9.py --zip-path /percorso/PACCHETTO.zip \
 --expected-zip-sha256 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
 --out output/integrity/zip.json
```
L'hash è un segnaposto di esempio: sostituirlo con quello **vero registrato**, non dedotto dal nome.
5. Nessun `true` in un controllo tecnico costituisce approvazione artistica, Gold V25 o autorizzazione alla pubblicazione. Rispettare V55/V80/V118/V119 e le regole di licenza.

## Protezioni
- Non accetta URL esterni per l'audit MP4, né hash arbitrari per i master: selezione fissata in V161.
- Nessun secret, token amministrativo, scrittura su R2 o GitHub; un solo download per run manuale, massimo 250 MiB.
- Un link nell'interfaccia apre GitHub, NON avvia autonomamente l'audit.
- I log e gli artifact dei repository pubblici non devono contenere segreti.
- Il sito `video-library-studio` e i workflow di produzione restano invariati.
