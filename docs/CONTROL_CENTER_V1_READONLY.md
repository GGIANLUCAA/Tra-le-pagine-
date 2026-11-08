# ArtVision Control Center V1 — anteprima separata

## Link di anteprima
https://artvision-control-preview.600led.workers.dev/

## Stato
- Branch isolato: preview/artvision-control-center-v1 (non main).
- Worker dedicato: artvision-control-preview. Non modifica video-library-studio.
- Sito live, processi di produzione, queue, MP4, R2 e automazioni esistenti non modificati.
- Il bundle HTML viene incorporato nel Worker distribuito, così non dipende da una chiamata GitHub all'apertura.
- Interfaccia mobile responsive, home, ArtVision 4×1, workflow, videoteca, problemi.
- Ricarica nel browser ogni 180 secondi quando visibile, e al ritorno sullo smartphone.

## Fonti: SOLO LETTURA
- GitHub API pubblica: ultime 100 esecuzioni workflow della repo pubblica.
- Queue GitHub main: queue/artvision_owner_selected_ten_20261102.json, escluso Dalí.
- Catalogo pubblico: https://video-library-studio.600led.workers.dev/api/catalog
- Non invia token, non accede a Secrets GitHub, chiavi API o archivio R2 privato.
- In caso di errore o rate limit le metriche mostrano un trattino e un numero di fonti raggiungibili, non inventano successo.
- La classificazione delle esecuzioni per progetto dipende dal nome dei workflow e può omettere workflow non identificabili.

## Limiti
- Workflow riuscito non dimostra un MP4 finito, scaricabile o artisticamente approvato.
- Anteprime video e copertine dipendono dal catalogo pubblico. Per download/playback il pannello rimanda al sito corrente.
- Le automazioni ChatGPT non sono direttamente lette dalla V1; eventuali aggiornamenti arrivano soltanto dai risultati GitHub che producono.
- L'anteprima workers.dev è pubblica e visualizza solo dati già pubblici. Non usa la chiave amministratore né espone gli endpoint privati.
- Nessuna routine di recupero, auto correzione, modifica di PR, approvazione, pubblicazione o generazione AI è attiva.
- Questa versione non è ancora integrata nella sezione privata del sito live.

## Da collaudare su Android
1. Aprire l'anteprima e controllare il badge 3/3 fonti raggiungibili.
2. Aprire Attività e confrontare un workflow con GitHub Actions.
3. Aprire ArtVision e confrontare il conteggio con la queue attuale.
4. Aprire Videoteca e verificare che le copertine e il link catalogo siano navigabili.
5. Aprire Problemi e verificare una run fallita (se presente).
6. Ripristinare l'app dopo qualche minuto e verificare che l'orario di aggiornamento cambi.

## Regola di rilascio
Non fondere nella home live prima di test Android, verifica fonti e autenticazione dell'eventuale sezione amministrativa.