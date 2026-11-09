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

## V4 — quattro anteprime per quadro e scheda qualità (9 novembre 2026)

### Galleria Museum
- Vista ArtVision 4×1 con un fascicolo espandibile per ciascuna opera: quattro riquadri allineati su desktop e due colonne su Android.
- Ogni riquadro è assegnato a una variante distinta: Critico Classico, Critico Museum, Cinema Classico, Cinema Museum.
- L'etichetta di disponibilità dipende da un **nome MP4 esplicito nel registro** e da una **corrispondenza esatta del nome nel catalogo pubblico** con valore available diverso da false. Se manca il file, la variante, la fonte o una corrispondenza certa, il tasto di riproduzione rimane disabilitato.
- Le anteprime sono ricavate soltanto dagli endpoint pubblici /cover e /media del Video Library Studio originale. Il video HTML5 carica il file solo su pressione del pulsante Guarda; chiudendo il lettore viene interrotta la riproduzione e liberato il collegamento.
- Per alcune varianti il registro attesta una produzione ma non fornisce un nome MP4 esplicito. Queste vengono mostrate come schede tecniche e **non vengono abbinate arbitrariamente** a un nome simile del catalogo.
- Dalí resta escluso dalla coda operativa come da indicazioni del proprietario.

### Controlli documentati per singola variante
- Presenza nel catalogo e indicazione disponibile/offline.
- SHA-256 presente nella scheda, senza equipararlo alla verifica attuale del file.
- Test di decodifica FFmpeg PASS registrato, se presente in un campo esplicito.
- Test ZIP/CRC PASS registrato, se presente in un campo esplicito.
- Verifica storica di download integrale con SHA PASS, solo se attestata testualmente.
- Verifica storica di streaming a blocchi, solo se attestata testualmente.
- Gold artistico V25 solo se esplicitamente true; tutti gli altri stati rimangono non attestati.
- Dimensione e durata sono etichettate come dati dichiarati nel registro, non rimisurate nel browser.
- Note di revisione artistica e diritti vengono mostrate come tali, senza dedurne approvazioni.
- Pulsante di controllo live limitato a 1.024 byte con verifica HTTP 206 e intestazioni; il controllo **non** certifica checksum integrale o intero MP4.

### Sicurezza e compatibilità
- Per la riproduzione il Worker ha il CSP media-src ristretto a https://video-library-studio.600led.workers.dev, con frame-ancestors limitato al medesimo sito.
- L'iframe dello Studio privato continua a caricare il pannello V4 senza una modifica ulteriore del sito principale.
- Nessun upload R2, modifica master, approvazione, pubblicazione, rigenerazione, azione GitHub o chiamata video a pagamento.
- Il sistema continua a leggere soltanto GitHub Actions, coda ArtVision main e catalogo esistente.

### Verifiche
- Test in tests/control-center-preview.test.mjs per varianti disponibili, offline, non catalogate, senza nome, SHA, PASS/PENDING/FAIL, Gold e scelta di sostituzione cinema corrente.
- QA di codice ed endpoint effettuato in sessione con dati di prova; la riproduzione completa di MP4 reali su Android rimane una prova distinta da eseguire nel browser del proprietario.

## V5 — statistiche, ricerca e accesso Android (9 novembre 2026)

### Statistiche rigorose
- Nuova pagina Statistiche accessibile dalla Home o dalle schede desktop: filtri "ultime 24 ore" e "ultimi 7 giorni".
- Conteggi di workflow GitHub osservati, successi tecnici, ultime run fallite/annullate e workflow ancora in esecuzione. Campione limitato alle ultime 100 run pubbliche e al ramo main. NON sono conteggi di video prodotti o approvati.
- Distribuzione delle esecuzioni fra ArtVision, La Storia Rivive, WOW LAB, sito e workflow non classificati. La classificazione per progetto deriva dai nomi esistenti dei workflow e può non coprire tutti i job.
- Riepilogo ArtVision: opere, slot previsti, consegne registrate, varianti con file identificabile, esistenza nel catalogo, disponibilità dichiarata, SHA storico, Gold attestato.
- Riepilogo archivio: voci totali, disponibili TRUE, offline FALSE, disponibilità non dichiarata, importazioni datate in 7 giorni. L'ultimo contatore usa soltanto il campo uploaded, quando presente, e non mostra come vere date inferite.
- Quando GitHub, registro o catalogo non rispondono, la relativa statistica resta non disponibile: niente zeri inventati.
- Il KPI degli errori in Home mostra soltanto ultime esecuzioni dei workflow pertinenti, non errori vecchi già risolti.

### Ricerca veloce dei quadri
- In ArtVision 4×1 si può cercare per titolo o artista, da Android, con filtri tutte, con anteprime, anteprime mancanti e da revisionare.
- La ricerca agisce sui dati già recuperati, senza richieste a servizi esterni o nuovi consumi API.
- Il filtro "da revisionare" significa che il registro conta delle consegne ma non attesta ancora Gold: non è una nuova diagnosi artistica.
- Le schede vengono filtrate senza alterare la coda owner o il catalogo.

### Scorciatoia Android
- Worker /manifest.webmanifest con display standalone e icona scalabile; Worker /icon.svg.
- La pagina include il manifest e il favicon. Aprire direttamente https://artvision-control-preview.600led.workers.dev/ in Chrome Android e usare menu browser > Aggiungi a schermata Home o Installa app, quando disponibile.
- A seconda del browser, la creazione dell'app installabile può richiedere icone raster aggiuntive o essere proposta soltanto come collegamento; non dichiarare installazione garantita senza un test reale sul dispositivo.
- Il link dello Studio privato continua ad aprire il pannello incorporato. La scorciatoia standalone apre solo i dati pubblici del Centro di controllo.
- Nessun service worker offline: senza Internet, i dati non si aggiornano e non vanno presentati come correnti.
- Nessuna notifica push o permesso aggiuntivo attivati.

### Sicurezza e prove
- Test unitari di statistiche, filtri, manifest, controllo GET-only e nessuna falsa produzione.
- Il nuovo Worker rimane separato dal sito, senza binding di scrittura R2, credenziali private o azioni su GitHub.
- Verificare dal telefono l'eventuale installazione dell'icona e le statistiche su dati reali dopo il rilascio.

## V6 — riparazione assistita con ChatGPT e collegamenti alle conversazioni (9 novembre 2026)

### Nuovo Centro riparazioni
- La pagina Problemi è stata promossa anche alla barra inferiore su Android con nome «Ripara GPT».
- Mostra gli **ultimi** errori tecnici per workflow GitHub del ramo principale come «da controllare», non gli errori storici già superati.
- I guasti non recuperati sono separati dai dati temporaneamente irraggiungibili e dagli slot ArtVision mancanti (che NON sono automaticamente guasti).
- Gli errori storici del campione sono consultabili in un elenco secondario, segnalati come potenzialmente già recuperati.
- Ogni errore/elemento può aprire un fascicolo «Ripara con GPT», con pulsanti per GitHub, copia del contesto, ChatGPT nuovo e chat principale associata.

### Diagnosi GitHub verificabile
- Nuovo endpoint SOLO GET: /api/diagnose?run=123.
- Accetta soltanto ID numerici di run già contenute nel campione pubblico GitHub del monitoraggio.
- Recupera su richiesta fino a 100 job GitHub della run e riporta solo fino a 8 job in stato critico e 10 step critici per job, con nomi e conclusioni. I log completi vanno aperti su GitHub: il pannello non li interpreta automaticamente come cause certe.
- Se i job non sono raggiungibili, usa i riferimenti reali disponibili (run ID, ramo, evento, stato, URL) e dichiara che la diagnosi è incompleta.
- Non esistono endpoint di avvio workflow, correzione, GitHub write o generazione AI.
- La chiamata a GitHub è on-demand alla pressione del pulsante, con cache di breve durata. Non è un polling aggiuntivo continuo.

### Richiesta preparata per ChatGPT
- Il pulsante «Ripara con GPT» prepara un messaggio in italiano con programma, repository, riferimento alla run, eventuali job/step critici, prova del registro o titolo della sorgente e link verificabili.
- La richiesta dice a GPT di rileggere GitHub e i log prima di stabilire la causa, preservare owner/master approvati, usare modifiche minime in ramo/PR e non spendere crediti o riavviare produzioni concorrenti.
- Il messaggio viene mostrato in una textarea selezionabile e copiato negli appunti solo mediante un clic esplicito dell'utente; il pannello non invia conversazioni/diagnosi ad API AI.
- L'apertura del sito https://chatgpt.com/ NON inserisce automaticamente il messaggio nella chat: l'utente lo incolla e invia.

### Riapertura chat esistente
- Per sicurezza non è disponibile una API affidabile del pannello per cercare la cronologia ChatGPT privata e associare automaticamente i vecchi thread alle run.
- In assenza di un link diretto, **nessun link a conversazioni viene inventato**.
- L'utente può incollare l'URL privato della chat aperta nel browser, normalmente https://chatgpt.com/c/<id>, collegandolo per progetto o per singolo workflow. La UI accetta soltanto domini ChatGPT e URL della forma /c/.... e rifiuta link condivisi /share/, che non sono chat private continuabili.
- I link sono conservati esclusivamente nella localStorage del browser di quel contesto (con fallback temporaneo se lo storage è bloccato), NON nel repository, nel backend, in R2 o in GitHub. Non è garantita la sincronizzazione tra browser, modalità standalone e iframe con storage partizionato.
- Se la chat è collegata, «Apri chat principale» apre il collegamento in una nuova scheda. È necessario copiare/incollare la richiesta, non viene immessa nella chat in automatico.
- Non utilizzare link di condivisione ChatGPT per una conversazione privata: i link condivisi possono esporre contenuti a persone che li possiedono.

### Test e limiti
- Test di diagnosi GET-only, run ammesse solo nel campione, recupero nomi job e step, link chat sicuri e rifiuto link /share/, prompt con istruzioni conservative.
- Non sostituisce l'automazione di produzione, non esegue autoriparazione, non aggiorna i video.
- Collaudo Chrome Android, copia appunti in iframe e navigazione alla chat privata da confermare dopo la distribuzione.
