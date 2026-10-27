# Vidu V45/V46 — usare davvero i 10 € senza esperimenti casuali

## Scena selezionata
**La macchina del tempo — H. G. Wells**. Dopo il rifiuto motivato della finta leva OpenCV, l'azione più promettente da sperimentare nel primo vero video I2V è **il viaggio attraverso il tempo** (il narratore descrive il sole e il paesaggio che scorrono rapidamente). Un personaggio fermo nella macchina mentre l'ambiente esterno accelera è un obiettivo più definito e a rischio inferiore rispetto a deformare braccia/leve/ingranaggi nell'immagine 02.

- Prima immagine pronta in **Libreria ChatGPT > Video da scaricare > VIDU_VIAGGIO_TEMPO_9x16.jpg** (720×1280, crop manualmente valutato da scena_03.jpg originale).
- In **VIDU_VIAGGIO_TEMPO_PRIMA_PROVA.zip** (stessa cartella) ci sono l'immagine, il prompt inglese, il preventivo I2V_PLAN.json e il codice puntuale. Il file **NON** è stato caricato su repository GitHub pubblico.
- Modello primo test: Vidu Q2 Pro Fast, 720p, **5 secondi**, audio disattivato, \`is_rec=false\` per evitare 10 crediti extra non necessari.
- Stima da listino ufficiale 27/10/2026: **8 crediti API off-peak = $0.04**; oppure **16 crediti = $0.08** in modalità normale. Prezzi stimati, non addebiti. Off-peak può richiedere fino a 48 ore; gli URL dell'MP4 Vidu possono scadere dopo 24 ore. Non inviare due richieste per impazienza.
- Nuovi modelli Q3 disponibili, ma per prima connessione scegliere il più conveniente che permetta un movimento autentico e una valutazione qualitativa, non partire da un modello molto più costoso su un input che proviene da un'immagine compressa a 505×761 pixel.
- V46 \`src/vidu_scene_integration_v46.py\` inserisce la clip nel master originale al secondo **16.2**, ne sostituisce **5.0 secondi** e conserva l'audio precedente senza rigenerare voce o musica. Necessita di piano/VIDU_TASK.json con stessa fingerprint e video scaricato con hash corretto. Crea un report V44 in stato DA_REVISIONARE, non approva automaticamente.

## Problema configurazione della chiave, non risolto per supposizione
Il check in pull request iniziale riportava \`VIDU_API_KEY_missing\`; un PR può avere restrizioni sui Secrets, quindi **non è una prova definitiva che l'utente non abbia configurato la chiave**. V45 esegue dopo merge su main un GET autorizzato e **solo in lettura** di \`/ent/v2/credits\`, mostra soltanto se l'API possiede crediti sufficienti per la clip (8/16); non mostra chiave, saldo o dati account e non effettua POST. I crediti dell'abbonamento web possono essere separati da quelli API: non comprare nuovi crediti senza verificarlo.

## Procedura finale per Android
1. Verificare che Vidu API key sia accessibile in GitHub Actions Secret \`VIDU_API_KEY\`: \`https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions\`.
2. Recuperare il file di input dalla Libreria ChatGPT. Siccome il repository è pubblico, **non mettere l'immagine privata direttamente in GitHub** soltanto per collaudo. Se il piano Web Vidu e i relativi crediti non sono gli stessi dell'API, l'immagine può essere usata direttamente nell'interfaccia Vidu web senza acquistare altri crediti, tramite upload dal telefono.
3. Prima della generazione leggere il preventivo e ottenere l'autorizzazione della singola scena. Non confondere l'autorizzazione all'utilizzo della chiave con una spesa automatica.
4. Per pipeline API il workflow \`i2v-low-cost-v41.yml\` offre \`balance\`, \`plan\`, \`submit\` e \`collect\`. Il vecchio workflow può selezionare soltanto asset di episodi già presenti nel repo: **non è ancora possibile avviare questa specifica scena privata direttamente da GitHub senza un passaggio di trasferimento autorizzato dell'immagine**. Non inventare di aver generato la clip. Il collector migliorato supporta \`submit_run_id\` per recuperare ricevuta, fingerprint e video dal run senza duplicare la richiesta pagata.
5. Dopo avere il file MP4 reale, utilizzare V46 con l'MP4 originale, il clip Vidu e la ricevuta collegata. Controllare la clip e il filmato montato a velocità normale; scartare deformazioni facciali, mani aggiuntive, macchina molle, panorami statici, audio fuori sincrono.
6. Confrontare la stessa scena fra **Vidu Q2 Pro Fast** e il master originale prima di acquistare clip di qualità superiore. Riservare eventualmente Q3 ai soli shot veramente decisivi; evitare batch e retry automatici.
7. Consegnare MP4 verificato, ZIP per Android e, se il download chat fallisce, copia **effettivamente presente nella Libreria ChatGPT**. La copia nella libreria non certifica che il link temporaneo della chat funzionerà.

## Regola permanente
Autorizzazione per ogni chiamata a pagamento, preventivo e limite di spesa, nessun retry automatico, criterio artistico V44. L'API key non è un'autorizzazione di spesa. Nessun addebito e nessun video Vidu creato da questo dossier o dai test offline V45/V46.
