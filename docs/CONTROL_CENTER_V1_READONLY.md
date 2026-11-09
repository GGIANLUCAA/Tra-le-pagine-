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

### Importazione personale delle chat dalla conversazione ChatGPT
- Se l'utente ha autorizzato il collegamento e sono disponibili ID reali delle conversazioni sorgenti delle automazioni, la chat può fornire un collegamento personale con frammento #linkchats= seguito da JSON codificato.
- I frammenti # dell'URL non vengono inviati via HTTP al Worker. Il browser importa soltanto URL privati con host chatgpt.com o chat.openai.com e percorso /c/<id>, solo per le quattro categorie ammesse.
- Dopo l'importazione, la pagina prova a eliminare subito il frammento dall'indirizzo e memorizza i link nella localStorage locale. Il messaggio "chat collegate" appare solo quando l'importazione è riuscita.
- Nessun conversation_id, thread_id o URL privato viene salvato nel repository pubblico, nella funzione Cloudflare o nel catalogo. La sincronizzazione tra browser/iframe e modalità standalone non è garantita.
- L'utente può continuare a collegare manualmente una chat differente per progetto o per singolo workflow. I collegamenti importati sono un'impostazione iniziale, non una prova che quella conversazione contenga già il dettaglio della run corrente.

## V6.1 — apri la chat nell'app Android (9 novembre 2026)

### Funzionalità
- Nel dialogo "Ripara con GPT", quando il browser è Android e la chat originale è associata, mostra **Apri chat nell'app ChatGPT** come scelta primaria, mantenendo il pulsante separato **Apri chat nel browser**.
- Quando la chat non è associata, mostra **Apri app ChatGPT** verso la home (con fallback https://chatgpt.com/) e il normale link browser.
- Nella lista delle quattro chat principali, su Android compaiono un'azione dedicata "Apri nell'app ChatGPT" e l'alternativa "Apri nel browser".
- Utilizza l'Android Intent standard di Chrome (intent://chatgpt.com/c/...#Intent;scheme=https;package=com.openai.chatgpt;S.browser_fallback_url=...;end), generato esclusivamente dopo aver validato il dominio della conversazione. Il package com.openai.chatgpt è quello dell'app ufficiale sul Play Store.
- Il collegamento prova ad aprire la conversazione privata originaria, non una copia o una nuova conversazione, se l'app installata gestisce quel percorso. Lo stesso link HTTPS viene fornito come fallback in caso di mancato riconoscimento.
- L'attivazione avviene soltanto da tocco dell'utente, in un'ancora, non con redirect o timer. Chrome Android richiede un gesto diretto; a seconda del browser e delle protezioni iframe possono essere bloccati.
- Non garantisce l'apertura nella chat specifica su ogni versione Android: servono test su dispositivo, app ChatGPT installata, accesso allo stesso account e autorizzazione ai link supportati nelle impostazioni dell'app Android.
- Per problemi da iframe, aprire direttamente il Centro di controllo da Chrome Android, toccare "Apri nell'app ChatGPT" oppure abilitare la gestione di chatgpt.com in Impostazioni → App → ChatGPT → Apri per impostazione predefinita.
- La diagnosi è sempre da copiare e incollare nella chat; il link non invia un messaggio in automatico.
- Nessuna modifica a master, flussi di produzione o credenziali. I link privati alle chat restano in localStorage e non sono committati nel repository.

### QA
- Test della forma del deep link, del package corretto, dell'ID conversazione e del fallback al medesimo indirizzo.
- Rifiutati link /share/, domini esterni e URL non HTTPS.
- Verifica manuale necessaria su Chrome Android per il lancio effettivo della app e l'apertura della conversazione, specialmente se il pannello è incorporato in Video Library Studio.

## V7 — tutte le categorie e produzioni, inclusi Libri narrati (9 novembre 2026)

- La pagina Categorie raccoglie 13 mondi editoriali: Libri narrati, Racconti e fiabe, Artisti e pittura, Critica d’arte, La Storia Rivive, Restauri storici, Musica e visual, WOW LAB, Cinema e cortometraggi, Documentari e curiosità, Cronaca e attualità, Provini e backstage, Altri progetti.
- Tutte le categorie sono sempre visibili. Quando il catalogo non contiene una corrispondenza, sono etichettate "In preparazione" senza fingere video esistenti.
- Il numero di schede, di file con disponibilità dichiarata, offline e con stato sconosciuto proviene soltanto da /api/catalog. La categorizzazione dei file è una classificazione editoriale: non prova la presenza di una voce narrante, la qualità Gold, il diritto di riuso o la disponibilità effettiva del download integrale.
- L'etichetta storica "Libri raccontati" viene presentata come "Libri narrati" senza modificare automaticamente i dati originali su R2. Fiabe e racconti riconoscibili hanno una categoria distinta.
- La pagina mostra fino a 18 schede recenti per categoria e un link diretto al filtro del Video Library Studio con ?category=..., supportato dalla nuova interfaccia del sito. Nell'archivio ufficiale rimangono tutti i video.
- Anche la Home include la griglia categorie; su Android la barra inferiore apre la pagina Categorie.
- La sezione "Salute delle produzioni" passa da 3 a 7 programmi osservabili: ArtVision, Storia Rivive, WOW LAB, Libri narrati, Musica e visual, Documentari e curiosità, Cinema e cortometraggi.
- Un genere senza workflow GitHub riconosciuto mostra "Non rilevato": non equivale a fermo, errore o produzione autonoma attiva. Le automazioni native ChatGPT non sono monitorate da questa rilevazione GitHub.
- Le nuove tipologie dispongono di filtri GitHub e collegamenti di chat personali nel pannello Ripara GPT, ma nessun URL privato è codificato nel Worker o pubblicato su GitHub.
- Il monitoraggio rimane GET-only e senza crediti o servizi a pagamento. Nessuna modifica ai master, ai workflow GitHub produttivi o ai metadati del catalogo.


## V8 · Qualità e prove: metadati verificabili
- Pagina Android **Qualità e prove** e API `GET /api/quality` del Worker separato.
- Ricerca su richiesta le esecuzioni `workflow_dispatch` della regia `quality-director-v17.yml` e, per le esecuzioni completate, l'eventuale artifact GitHub `quality-v17-report`.
- Controlli senza crediti API di generazione; `POST`/scritture respinte. Il sito principale e gli automatismi video non vengono modificati.
- Se il workflow specifico non è raggiungibile, fallback dichiarato alle ultime **100** run pubbliche generali, non scambiato per storico completo.
- `artifact_present` indica **solo un record nell'indice degli artifact**. Il JSON interno, i byte del MP4, gli SHA-256, le licenze e l'approvazione artistica non vengono letti né attestati da questa funzione. I campi di verifica e pubblicazione restano `false`.
- Quando l'owner sceglie **Analizza con GPT**, la UI prepara un contesto con la run GitHub e l'incertezza esplicitata, senza intervenire autonomamente sul video.
- L'integrazione con un rapporto JSON verificabile per singolo file e i controlli integrali MP4/ZIP richiede ancora un successivo passaggio con prova reale. Nessuna falsa promessa di sincronizzazione o Gold.
- Implementazione inizialmente su `preview/control-center-quality-v8-20261109`, con unit-test e build offline in GitHub Actions.

## V8.1 · Cloudflare service binding e prova HTTPS

**Problema confermato dal test esterno**: il sito originale `video-library-studio.600led.workers.dev` ha restituito HTTP 200 per `/api/catalog` e HTTP 206 per tre MP4 serviti con Range `bytes=0-1023`, mentre le chiamate da un Worker Cloudflare verso il dominio pubblico dell'altro Worker restituivano catalogo indisponibile e 404 nei download.

**Correzione**: l'anteprima `artvision-control-preview` richiede il binding Cloudflare di tipo `service` con `name=VIDEO_LIBRARY` e `service=video-library-studio`, aggiunto alla configurazione di caricamento del Worker. Il codice passa esplicitamente il binding all'accesso al catalogo e ai controlli Range (GET soltanto). Le chiamate GitHub rimangono indipendenti. Non è cambiato il Worker principale e non è stato assegnato alcun token di amministrazione al pannello.

**Conferma**: i test online su GitHub Actions [run #42699342427](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42699342427) passano; `sources.catalog.ok=true`, i primi 1024 byte di tre MP4 sono stati letti via pannello e confrontati con HTTP 206 del sito originale. **Non equivalgono** a una verifica dell'intero MP4, dello ZIP, dell'hash SHA-256 o del Gold artistico.

**Manutenzione**: qualsiasi nuovo deployment deve includere il binding `VIDEO_LIBRARY`; il solo output di `scripts/build-control-center-preview.mjs` non configura automaticamente i binding Cloudflare. Nel sito principale il Centro di controllo è già raggiungibile tramite l'area amministratore incorporata. Il Worker dell'anteprima mostra esclusivamente metadati pubblici anche se il link è nella sezione privata.
