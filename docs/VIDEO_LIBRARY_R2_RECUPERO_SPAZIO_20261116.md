# Video Library Studio — recupero spazio R2 · audit conservativo (16/11/2026)

## Stato e prove
Inventario letto **interamente e in sola lettura** dal bucket `video-library-studio` tramite API Cloudflare R2 (7 pagine, 6.244 oggetti, 13.243.144.361 byte, circa 12,33 GiB). Registro integrale dei **279 MP4 numerati** e dei gruppi a ETag/byte coincidenti: [`reports/video_library_r2_storage_audit_20261116.json`](../reports/video_library_r2_storage_audit_20261116.json).

| Tipo | Numero | Byte |
| --- | ---: | ---: |
| Video MP4 | 729 | 12.948.897.935 |
| Copertine JPG | 1.041 | 290.724.278 |
| Altri oggetti | 4.474 | ~3,5 MB |
| Potenziali duplicati da ETag + dimensione | 12 gruppi | 312.090.019 byte *teorici* |
| Video numerati da confrontare | 279 | 3.515.282.007 byte *non automaticamente eliminabili* |
| Recuperato realmente | — | **0 byte** |

Sono stati consultati inoltre `catalog/info.json`, `catalog/manage.json`, `catalog/deleted.json`, `catalog/ready.json`. I nomi enumerati nel catalogo pubblico sono accessibili anche tramite link diretti: cancellare un oggetto può rompere quei collegamenti anche se il suo contenuto appare sotto un secondo nome. **Non cancellare oggetti dal solo inventario.**

## Candidati concreti, senza confonderli
1. **Duplicazione video verificata con SHA256 integrale:** `ARTVISION_PIRANESI_CINEMA_V6.mp4` e `ArtVision_WOW7_Piranesi_Le_Prigioni_Impossibili.mp4`, ciascuno 41.361.075 byte, SHA256 comune `25e979519e54445a285aea9a19d27215ea0fe4f295067b77ea0f01543b99219a`. I byte di entrambi sono stati letti da R2 e calcolati separatamente. La seconda chiave compare in `catalog/ready.json`: è la prima da **preservare**. Prima di rimuovere l'altra occorre preservare i collegamenti storici, verificare player/metadata, e predisporre rollback. Spazio massimo possibile per la coppia: **41.361.075 byte**. Nessuna eliminazione.
2. **Stessa dimensione ed ETag multipart, SHA256 *non* confermato:** `ARTVISION_PIRANESI_CARCERI_CINEMA_V6__259319285.mp4` e `ArtVision_Piranesi_Carceri_Cinema_V6.mp4` (259.319.285 byte ciascuno, ETag `f827a26d5423291f758ced407120f5e4-31`). Il tentativo di leggere integralmente il file grande tramite il connettore Cloudflare si è arrestato con **limite memoria dello strumento**: questo *non* prova corruzione del file. Serve SHA256 sul server/runner o un accesso streaming autorizzato. Guadagno solo **potenziale**, nessuna eliminazione.
3. Le **altre 278 varianti numerate** non hanno stesso ETag del nome base (salvo la coppia già citata). **Non sono duplicati verificati**. Fra esse ci sono versioni artistiche, master e nomi generici: non si elimina nulla solo perché termina in `__dimensione.mp4`.
4. Le copertine con ETag coincidente occupano circa 11 MB di spazio potenzialmente duplicato; rischio di rompere la scheda/copertina superiore al vantaggio immediato.

## Protocollo prima di qualsiasi liberazione di spazio
- Generare un manifest **immutabile** di SHA256 reali e byte per ogni candidato, senza riscaricare indiscriminatamente tutti i 729 video.
- Cercare la chiave originale nei riferimenti **del sito live**, manifest, player, catalogo gestito, `ready`, `deleted`, `info`, vecchi link e pacchetti social; se è usata, predisporre compatibilità/redirect provato **prima** del cleanup.
- Verificare che esista almeno una copia integra e recuperabile **fuori dal gruppo da cancellare**. Backup in un altro R2 nello stesso account occupa altro spazio e può costare: preferire export locale/PC già disponibile, con SHA/readback, **solo se autorizzato**.
- Valutare le versioni differenti per opera, titolo, anno, variante (Cinema/Critico/Museum), durata, SHA, approvazione e diritti. Mai confondere `REVIEW` con scarto.
- Preparare un elenco di sole chiavi eliminabili, limite massimo per esecuzione, preflight con ETag/dimensione immutati, backup e piano rollback; eseguire cancellazioni solo con consenso specifico per i file e controllo post-intervento di player HTTP 206, download, schede e metadata.
- Fino a quel momento: **nessuna cancellazione automatica, nessuna transcodifica degli originali e nessuna modifica ai master**. Evitare copie private massive senza verifica quota/costi.

## Prevenzione della crescita
Non duplicare automaticamente sotto nomi nuovi gli stessi SHA di video già archiviati; distinguere *file fisico* da *variante editoriale* e mantenere riferimenti stabili. Il workflow di importazione è già oggetto della PR #323 (gate di pubblicazione) e la PR #324 (archivio privato): non introdurre una terza modifica concorrente al Worker o al workflow senza risolvere quei conflitti.

L'audit è una preparazione concreta, **non** una promessa di 2–3 GB già liberati. La quantità dimostrata con SHA è 41,4 MB *candidati*, non 41,4 MB cancellati.

## Protezione degli indirizzi prima della prima deduplica (PR #330)

È stata aggiunta una **correzione isolata nel sorgente canonico Worker** `integrations/video_library_laboratorio/workspace-base.mjs`, non ancora distribuita sul sito. Per l'esatta coppia Piranesi già verificata con SHA256, se e soltanto se la vecchia chiave `ARTVISION_PIRANESI_CINEMA_V6.mp4` diventerà assente, il sito potrà effettuare un reindirizzamento **temporaneo 307** verso `ArtVision_WOW7_Piranesi_Le_Prigioni_Impossibili.mp4`.

Il controllo si applica ai percorsi `/media/`, `/download/`, `/watch/`, `/info/` e `/download-info/`. Conserva la stessa origine e la query originale; il browser può quindi ripetere la richiesta con l'header `Range`. Il reindirizzamento rimane inattivo finché entrambi gli MP4 esistono (stato attuale). Restituisce 404 se è presente una tombstone in `catalog/deleted.json`, una delle voci è `hidden`, il file da conservare manca, è cambiato di dimensione o non ha più l'ETag del file verificato. I cataloghi di sicurezza mancanti/illeggibili impediscono di riattivare il vecchio indirizzo (fail-closed). Non si estende automaticamente ad altre opere o versioni.

**Test offline verificati:** `integrations/video_library_laboratorio/piranesi-alias.test.mjs` — URL originali, reindirizzamento condizionale, Range `206` dopo il reindirizzamento, `404` per tombstone/hidden/keeper alterato, `503` per guasto metadati, nessuna modifica al catalogo R2. Il test usa R2 simulato, **non** dimostra ancora un HTTP 206 sul sito live. GitHub CI: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43871849945 .

**Preflight R2 in sola lettura ripetuto:** entrambi i video esistono ancora su R2, 41.361.075 byte ciascuno, ETag `2596f0317268b24c3eeefb522a03ab09-5`, nessuna tombstone o `hidden` nella gestione, solo il keeper è in `catalog/ready.json`. **Byte rimossi: ZERO**.

### Gate vincolanti per un futuro cleanup effettivo

1. Backup e rollback del Worker Cloudflare attualmente distribuito: sorgente script, versione, tutti i binding e settings. Confronto esatto con il sorgente canonico, verificare dipendenze importate e PR concorrenti; deploy solo attraverso procedura già validata e con backup.
2. Eseguire i test su Worker in **preview isolata**, poi sul live solo con controllo Range e dei 5 percorsi originari, verificando entrambi gli MP4 e il catalogo; non rompere le schede/coperte.
3. Conservare una **copia verificata esterna a R2** e un manifest con SHA256 e dimensione dell'oggetto che si vuole togliere; non aggiungere duplicati in R2 per il backup a causa di costi e spazio.
4. Ottenere autorizzazione specifica della chiave da eliminare. Riconfermare SHA/ETag/size e assenza di nuove approvazioni/modifiche prima del DELETE. Non usare l'endpoint `/api/delete` del sito, perché salva una tombstone che disabiliterebbe correttamente il redirect.
5. Eliminare una sola chiave nella finestra controllata, immediatamente verificare HTTPS/Range/metadata/player/download e disponibilità del rollback. Se un test fallisce, ripristinare dall'archivio esterno.

L'intervento corrente **non elimina file**, non attiva il redirect sul Worker live, non avvia download pesanti o copie private a pagamento. Lo spazio liberabile rimane potenziale.
