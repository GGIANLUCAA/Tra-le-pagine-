# ArtVision Control Center — V2, fase successiva alla preview

Data: 9 novembre 2026.

## Stato e indirizzo
- Anteprima Cloudflare distinta: https://artvision-control-preview.600led.workers.dev/
- Worker: artvision-control-preview.
- Sorgenti GitHub nel ramo: preview/artvision-control-center-v1.
- Sito principale https://video-library-studio.600led.workers.dev/ e workflow video non modificati in main.
- Il collegamento a Centro di controllo è stato PREPARATO in site/video-library-v2.html sul ramo di anteprima, non distribuito sulla home live.
- Non sono previste pubblicazioni automatiche o generazioni AI aggiuntive.

## Cosa fa
- Rilegge in automatico lo stato quando il pannello è visibile (intervallo interfaccia 180 secondi) e al ritorno nell'app se il dato è vecchio.
- Endpoint read-only /api/status; cache breve per non esaurire le chiamate pubbliche GitHub.
- GitHub Actions: ultime 100 esecuzioni pubbliche, stati, data e link reali.
- Coda ArtVision: legge queue/artvision_owner_selected_ten_20261102.json da main, esclude Dalí dal conteggio operativo, separa varianti registrate, schede tecniche e approvazione artistica.
- Quattro varianti per opera: Critico Classico, Critico Museum, Cinema Classico, Cinema Museum.
- Per ciascuna mostra quando possibile titolo file, presenza nel catalogo pubblico, SHA presente nel registro e run GitHub.
- Videoteca: ultime 24 voci visibili del catalogo pubblico, con link al sito originale. Non interpreta l'esistenza nel catalogo come verifica di download.
- Problemi: workflow falliti/annullati e slot non conteggiati. Nessuna attribuzione artificiale di colpe ai renderer.

## Verifica download: perimetro esatto
- La nuova funzione /api/check?key=NOME.mp4 richiede al sito originale un GET con Range: bytes=0-1023.
- Accetta solo nomi .mp4 senza directory e un sito remoto fisso; non è un proxy arbitrario.
- Per esito positivo: HTTP 206, Content-Range nel formato atteso, MIME video/mp4 e Content-Disposition attachment.
- Etichetta: verifica di ACCESSIBILITÀ A BLOCCHI, non checksum integrale del file.
- Per certificare la disponibilità completa del master Android occorre ancora il relativo audit/stream/download integrale e confronto SHA; non spacciare /api/check per questo test.
- Il link di download è rivelato dalla UI dopo l'esito positivo della verifica leggera.

## Sicurezza e limiti
- Resta pubblico SOLO il contenuto già pubblico su GitHub e nel catalogo.
- Il ramo di preview e il Worker non hanno credenziali R2 o autorizzazioni a modificare i video.
- Non possono fermare o riavviare automazioni, modificare master, approvare video, spendere crediti o pubblicare.
- Un workflow success è solo successo tecnico; non dimostra un video finito né un'approvazione artistica.
- Le fonti pubbliche possono essere temporaneamente indisponibili o limitate da rate limit; non assumere che "0 errori osservati" sia "0 errori totali".
- Gli agenti/automazioni ChatGPT sono visibili soltanto nella misura in cui producono tracce GitHub, non tramite l'API ChatGPT.
- Non integrare endpoint privati senza adeguata autenticazione e protezione dei dati.

## Manutenzione e QA
- La fonte UI è site/control-center-preview.html.
- La fonte backend è site/control-center-preview.worker.js.
- Il bundle di deploy è generato da node scripts/build-control-center-preview.mjs. NON distribuire direttamente il file worker.js senza bundling della UI: ha un fallback remoto storico.
- Test: node --test tests/control-center-preview.test.mjs.
- Check GitHub solo sul ramo preview: .github/workflows/artvision-control-center-preview-ci.yml. Non esegue deploy o produzioni.
- QA simulato in chat: tre fonti correttamente aggregate, esclusione Dalí, stati per variante, risposta range e rifiuto dei metodi non GET.
- QA di rete non certificato da questa sessione: DNS esterno non accessibile dall'ambiente locale; effettuare un controllo da browser Android sulla preview e confrontare un caso reale.

## Prossimo punto di integrazione
Dopo test Android della V2 e controllo dei dati, integrare soltanto il link nella gestione privata Video Library Studio. Nessuna sostituzione dei renderer, dei master o delle automazioni esistenti.

## V3 — priorità, salute delle produzioni e diario (9 novembre 2026)

### Nuove viste
- **Da fare per me**: soltanto gli ultimi fallimenti/cancellazioni/timeout per ciascun workflow osservato sul ramo main. Un errore storico seguito da una run riuscita dello stesso workflow non rimane segnalato come incidente corrente. Fallimenti tecnici sono inviti a consultare i log, NON richieste certe di intervento umano e NON autorizzazioni a riavviare o spendere.
- **Revisione artistica non urgente**: conteggio delle opere con slot consegnati nel registro e senza Gold_V25 === true. Non blocca la produzione, non sostituisce la valutazione del proprietario e non certifica la pubblicabilità. Esclude Dalí.
- **Salute delle produzioni**: tre schede ArtVision, La Storia Rivive, WOW LAB. Stato fra running, attention, observed_success, unobserved, unknown, definito solo dalle ultime 100 esecuzioni pubbliche GitHub e limitato alle run sul ramo main o senza ramo dichiarato. unobserved NON significa "fermo"; observed_success riguarda GitHub, NON un MP4 verificato.
- **Diario**: gli eventi GitHub si basano sul campo updated_at dei workflow osservati; gli eventi del catalogo si basano SOLO sul campo uploaded delle schede pubbliche quando contiene una data valida. Non viene generato uno storico permanente e non si inventano video o importazioni.
- La Home V3 mette prima le attenzioni, poi la salute delle produzioni e infine gli ultimi eventi.
- Navigazione mobile a cinque pulsanti: Home, Da fare, Opere, Diario, Video. Le viste tecniche/Salute rimangono accessibili dalla Home.

### Limiti di precisione
- Gli ultimi errori per workflow sono dedotti da workflow_id e head_branch; se il campo manca, si applica un raggruppamento per nome. Il campione può perdere attività meno recenti o attività fuori da GitHub.
- La classificazione dei progetti usa il nome dei workflow GitHub; un nome non riconosciuto rimane other invece di essere assegnato in modo fittizio a un progetto.
- Nessuno stato del pannello certifica gli stati delle automazioni native ChatGPT.
- Nessun dato "verde" implica Gold artistico, integrità completa MP4, diritti di pubblicazione o disponibilità di un download integrale.
- I timestamp del diario sono quelli dichiarati dalla fonte, non eventi push registrati autonomamente.
- La V3 non installa Workflows, D1, cron aggiuntivi, agenti AI o strumenti a pagamento: continua a rileggere le tre fonti V2.

### Test
- tests/control-center-preview.test.mjs: verifica che un fallimento poi recuperato non appaia nelle attenzioni correnti, che una produzione non osservata sia unobserved, che il diario mostri eventi con date e che il monitoraggio non diventi un endpoint di scrittura.
- La UI e il backend vengono incorporati nel Worker separato artvision-control-preview, già richiamato dall'area amministrativa di Video Library Studio.
- Il collaudo visivo su Android deve ancora confermare usabilità e rendering reali dopo la distribuzione; la verifica del Worker distribuito non equivale al test su telefono.
