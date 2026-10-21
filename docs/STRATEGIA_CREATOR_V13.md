> Cadenza aggiornata: [produzione intensiva V15](PRODUZIONE_INTENSIVA_V15.md), obiettivo almeno 10 video/giorno in autonomia. La cadenza precedente di due video/settimana è superata.

> Priorità aggiornata: [piano di crescita V14](PIANO_CRESCITA_V14.md). Per ora sono rimandati commissioni, outreach a editori/aziende, sponsor e ads. Le sezioni commerciali sotto restano riferimenti futuri.

# Strategia creator: qualità, pubblico e reddito

Valutazione del 21 ottobre 2026. Questo documento è una proposta operativa per
Gianluca, non una previsione di successo. Non abbiamo ancora gli export degli
account, incassi, costi completi o ore di lavoro: non sappiamo quale serie renda.
L'archivio video dimostra produzione, non domanda o redditività.

## Decisione principale

Concentrare il primo ciclo su contenuti culturali con un punto di vista originale:
**ArtVision Critico e racconti di libri**. È un'ipotesi da confrontare con i dati,
non la prova che siano già i format migliori. Cinema V6 resta la vetrina artistica
approvata. Visual Music e HyperLumen restano sperimentazione finché non abbiamo
sorgenti riproducibili e segnali di domanda. Controluce aggiunge ricerca continua,
verifica dei fatti e aggiornamenti: non è la priorità commerciale iniziale.

Non aprire sei nuovi canali insieme. Scegliere un account principale e una
promessa riconoscibile; distinguere le serie con playlist. L'arte senza parlato
può avere pubblico internazionale, mentre racconti e critica italiana hanno
un'altra fruizione: verificarne la compatibilità prima di mescolare i feed.

Promessa editoriale provvisoria: «Storie e opere che diventano comprensibili e
memorabili attraverso un racconto visivo curato». Pubblico ipotizzato: persone
curiose di cultura che vogliono capire senza una lezione accademica. Validarlo
con commenti, ricerche degli spettatori e risultati reali; non inventare demografie.

## Cosa era eccessivo nella risposta dell'altra AI

I cinque repository esistono, ma non sono cinque motori pronti da collegare.
I prompt richiedono contesto; i blueprint richiedono implementazione; le
percentuali dichiarate non dimostrano performance. Nessuno rende automaticamente
originali, pertinenti o monetizzabili i video. La formula «non devi inventare
nulla» è sbagliata: il valore distintivo deve essere nostro.

| Progetto esaminato | Cosa tenere | Cosa correggere o scartare | Uso nel progetto |
|---|---|---|---|
| rampstackco/claude-skills | Posizionamento, temi, capacità produttiva, calendario e revisione | Nasce soprattutto per contenuti web; non dimostra risultati video | Scheda pubblico/promessa/obiettivo e ciclo editoriale |
| heymarii/ai-blueprints | Raccolta dati → report → prossima prova | Documento progettuale, non connettore funzionante. Reach e views non sono equivalenti. Tempi risparmiati non dimostrati per noi | Report offline, denominatori e finestre separati |
| azizaeffendi/content-creator-monetization-guide | Distinguere servizi, prodotti e ricavi di piattaforma | Scenari in rupie indonesiane senza evidenze trasferibili; follower non equivalgono a ricavi. Alcuni percorsi linkati non esistono nello snapshot | Un'offerta pilota e contabilità del tempo, senza previsioni copiate |
| charlie-morrison/content-creator-prompts | Promessa iniziale, scaletta e indicazioni visive | Una raccolta nel README, con promozione di prodotti. Nessuna prova che i prompt ottimizzino il nostro pubblico | Domande originali del brief, rispettando il divieto di sottotitoli |
| msitarzewski/agency-agents | Ruoli di stratega, autore, revisore e analista | Il file Content Creator è una descrizione di ruolo, non un renderer. KPI come 25% engagement e 5:1 ROI non sono nostri benchmark | Controlli distinti svolti dall'agente; non una squadra autonoma installata |
| coreyhaines31/marketingskills — alternativa | Eventi legati alle decisioni, attribuzione, conversione | Non aggiungere tracciamento o acquisti di strumenti senza un bisogno misurato | Collegamento video → azione → richiesta/incasso |
| gitroomhq/postiz-app — alternativa | Software reale per programmazione e integrazioni social | Hosting, credenziali, autorizzazioni delle piattaforme e manutenzione; stack diverso dal Worker attuale | Candidato successivo, non installato né sostitutivo del sito |

Il blueprint heymarii attribuisce watch time e retention alla YouTube Data API:
la fonte tecnica corretta per queste analisi è la YouTube Analytics API, con
accesso autorizzato. Non basta una chiave pubblica. L'importazione manuale di
export resta il percorso iniziale verificabile.

### Riutilizzo e licenze

Ispezionati README, file pertinenti e licenze degli snapshot indicati in
`config/research_sources_v13.json`. RampStack, Agency Agents, la guida di
monetizzazione e Marketing Skills hanno LICENSE MIT. Content Creator Prompts
dichiara MIT nel README, senza LICENSE separata. AI Blueprints non ha una
licenza esplicita nei file esaminati: non ne redistribuiamo testi o codice.
Postiz usa AGPL-3.0: un'eventuale integrazione va progettata con i relativi obblighi,
non incorporando silenziosamente il suo codice. In questa modifica non abbiamo
importato prompt, installato skill esterne o copiato implementazioni di questi
repository: documentazione e codice nuovi sono scritti per questo progetto.

## Monetizzazione: ordine degli esperimenti

1. **Servizio pilota su commissione.** Una piccola libreria, un autore o un'attività
   culturale potrebbe avere bisogno di un video. Preparare una pagina portfolio
   con tre esempi reali e un'offerta precisa: un video verticale, copertina,
   durata concordata, una revisione, materiali autorizzati. Nessuna promessa di
   visualizzazioni o vendite. Verificare la domanda con richieste reali prima di
   comprare strumenti o promettere consegne. Non contattare persone senza
   autorizzazione dell'utente. Il tempo commerciale è parte del costo.
2. **Affiliazioni coerenti**, solo quando programma e account sono ammessi e il
   prodotto è pertinente al video. Registrare clic e commissioni confermate,
   rendere riconoscibile il rapporto commerciale. Non trasformare ogni racconto
   in una promozione. Un clic non è un ordine e un ordine annullato non è un incasso.
3. **Prodotto digitale piccolo**, dopo una domanda ripetuta: ad esempio un
   percorso originale di lettura o una guida ragionata alle opere. Prima raccogliere
   interesse reale; poi produrre. Non iniziare da un corso su come diventare creator
   di successo senza risultati dimostrabili.
4. **Ricavi delle piattaforme**, come percorso parallelo di lungo periodo.
   Requisiti, account e singoli contenuti vanno verificati. Non sono il rimborso
   automatico dei costi di produzione.

Il prezzo del pilota si costruisce da ore previste, costo orario obiettivo scelto
dall'utente, API/materiali, revisioni e commissioni. Senza questi input non
fissiamo prezzi «di mercato» inventati. Il modulo calcola contributo di cassa e
contributo per ora, non utile netto: imposte e costi fissi non allocati restano fuori.

## Vincoli reali delle piattaforme

Fonti ufficiali consultate il 21 ottobre 2026, da ricontrollare prima di una
candidatura o di cambiare strategia:

- YouTube valuta originalità e autenticità del canale. Produzione ripetitiva di
  massa e slideshow con scarso valore narrativo/commento possono essere inidonei.
  Usare AI non sostituisce il contributo editoriale; diritti d'uso e idoneità alla
  monetizzazione sono verifiche diverse. Per noi, un commento critico originale
  e documentato è una base più solida della semplice sequenza di quadri con musica:
  è una valutazione strategica, non garanzia di accettazione.
- La pagina YPP indica 1.000 iscritti più 4.000 ore pubbliche idonee in 12 mesi,
  oppure 10 milioni di visualizzazioni Shorts idonee in 90 giorni. Le ore nel feed
  Shorts non valgono per il percorso delle 4.000 ore. Raggiungere le soglie non
  garantisce l'ammissione. L'accesso anticipato ad alcune funzioni ha criteri distinti:
  non confonderlo con i ricavi pubblicitari completi.
- Meta descrive Facebook Content Monetization come programma su invito nella
  comunicazione di marzo 2026. Verificare l'area Monetizzazione dell'account;
  non presumere che ogni visualizzazione generi entrate.
- Per TikTok, disponibilità territoriale e account sono da verificare nel pannello
  personale. Non abbiamo confermato l'idoneità dell'utente. Le fonti indicizzate
  indicano contenuti originali e durata minima di un minuto per Creator Rewards;
  l'accesso completo alla pagina è stato limitato. Nessuna previsione di ricavo
  TikTok è inclusa. Non suggeriamo account esteri o aggiramenti territoriali.
- Per Instagram non abbiamo verificato funzioni di guadagno attive sull'account.
  Trattarlo inizialmente come distribuzione e relazione, non rendita garantita.

## Ciclo di 30 giorni proposto

È un piano di apprendimento, non una scadenza per guadagnare. Cadenza iniziale:
**due video curati alla settimana**, ridotta se eccede il tempo disponibile.
Niente rinnovi o spese aggiuntive automatiche.

| Periodo | Produzione e verifica | Decisione attesa |
|---|---|---|
| Giorni 1–7 | Selezionare account principale; raccogliere dati degli ultimi video; scegliere tre esempi portfolio; preparare due episodi | Baseline e offerta concreta, senza inventare pubblico |
| Giorni 8–14 | Due episodi dello stesso percorso; provare un'apertura diversa mantenendo stile e durata simili; bozza pagina offerta | Le persone restano e capiscono la promessa? |
| Giorni 15–21 | Due nuovi episodi; leggere commenti e richieste; verificare una proposta commerciale se autorizzata | Segnali di interesse qualificato, costo effettivo per video |
| Giorni 22–30 | Due episodi con la migliore ipotesi; confronto a sette giorni dalla pubblicazione | Continuare, correggere o ridurre il format, motivando con dati |

Esempi editoriali da sviluppare con fonti: «Il dettaglio che cambia la lettura di
un quadro» (Critico), «La scelta del protagonista e il suo prezzo» (libri),
«Un'opera, tre passaggi visivi motivati» (Cinema V6). Nessun aneddoto inventato
per rendere più forte l'apertura. Un invito finale, coerente con l'obiettivo:
seguire la serie, vedere l'approfondimento o richiedere un lavoro, non tutti insieme.

## Istruzioni per GPT a ogni nuovo video

Prima del copione compilare `business` in `PROJECT_V13.json`: pubblico, promessa,
contributo originale, piattaforma, obiettivo, invito finale, una sola ipotesi da
provare, budget di tempo e costo (null se ignoti). Leggere le ultime osservazioni
private disponibili. Non dichiarare vincente un formato senza evidenza.

Proporre internamente tre aperture e scegliere quella che promette qualcosa che
il video mantiene. Non produrre tre MP4. Conservare la voce e lo stile approvati,
fonti e ricetta. Dopo la pubblicazione autorizzata registrare ID/URL e osservazioni
alla stessa età del contenuto (es. 7 e 28 giorni), separando le finestre.

Per il report: `python src/creator_metrics_v13.py --input osservazioni.json --out report`.
Lo schema vuoto è in `templates/CREATOR_OBSERVATIONS_V13.json`. Il report non
si connette agli account, non pubblica e non programma esecuzioni. È eseguibile
senza API a pagamento; i futuri connettori dovranno produrre lo stesso schema.

Ogni osservazione richiede: `video_id`, `platform`, `account`, `format`,
`window_days` (numero positivo), `view_definition` (es. views_native o engaged_views),
`source` (export/pannello), `observed_at` (data). Campi numerici facoltativi:
`views`, `watch_seconds`, `clicks`, `orders`, `net_receipts_eur`, `cash_cost_eur`, `hours`.
Usare null per sconosciuto; zero solo se misurato. Incassi al netto di rimborsi e
commissioni, stessa finestra; tempo include ricerca, revisione e distribuzione.
Allocare i costi una volta per destinazione quando un video è riutilizzato.
Non pubblicare dati commerciali o personali nel repository pubblico.

Il confronto è separato per piattaforma, account, formato, finestra e definizione
di view. La mediana è descrittiva. Cinque osservazioni sbloccano un confronto,
non dimostrano significatività. Non sommare snapshot a 7 e 28 giorni. Non inventare
CTR da visualizzazioni: serve il denominatore corretto. Non attribuire un successo
all'orario, al prompt o al montaggio da una semplice correlazione.

## Il sito: cosa deve fare e cosa manca

Durante il lavoro è arrivata su main anche `docs/creator-business.html`, dashboard
manuale con salvataggio locale. Questa revisione ne corregge i valori economici
mancanti trattati come zero e rimuove la selezione automatica di una categoria
vincente basata su metriche non confrontabili. Il codice è verificato localmente;
la sua disponibilità pubblica dipende dal deploy del sito.

Il sito/archivio conserva video e riferimenti; da solo non acquisisce clienti.
Il Laboratorio recuperato conserva selezioni, progetti e stile: non dimostra
pubblicazione social né acquisizione automatica delle metriche.

Estensione proposta per il prossimo rilascio del sito:

1. Scheda privata per video: `project_id`, ricetta, obiettivo, stato, costo, tempo,
   destinazioni e ID social. Import/export dello schema osservazioni e collegamento
   al report. Non esporre questi dati nell'API del catalogo pubblico.
2. Pagina pubblica «Video per libri e cultura»: tre esempi verificati, servizio e
   limiti, richiesta di preventivo verso un contatto scelto dall'utente. Nessuna
   recensione inventata, prezzo fittizio o pulsante di pagamento non funzionante.
3. Misurare richiesta effettiva e provenienza senza inserire dati personali negli
   URL. Se si aggiunge analytics, definire raccolta e consenso prima del rilascio.
4. Distribuzione assistita: preparare titolo, descrizione e file per la piattaforma;
   aggiungere scheduler solo dopo la scelta degli account e verifica dei permessi.
   Un servizio esterno come Postiz va valutato in base al tempo realmente risparmiato.

**Stato di questa consegna:** implementati routing, ricette, cache voce, provenienza,
brief commerciale e report offline. Conservati i sorgenti del Laboratorio.
Corretto il sorgente della dashboard esistente; deploy live non verificato.
Nessun nuovo account collegato, nessuna campagna
commerciale inviata e nessun incasso dichiarato. Il deployment web e l'accesso
alle metriche richiedono la configurazione reale del servizio/account.

## Fonti primarie

- Repository e commit: `config/research_sources_v13.json`.
- YouTube originalità: https://support.google.com/youtube/answer/1311392?hl=en
- YouTube YPP: https://support.google.com/youtube/answer/72851?hl=it
- YouTube metriche: https://developers.google.com/youtube/analytics/metrics
- Meta: https://about.fb.com/news/2026/03/creator-fast-track-grow-your-audience-earn-money-on-facebook/
- TikTok (accesso parziale): https://support.tiktok.com/en/business-and-creator/creator-rewards-program

## Coerenza con Creator Business Lab V1

Questo documento precisa il precedente `CREATOR_MONETIZZAZIONE_V1.md`:
la cadenza iniziale è due video/settimana finché non misuriamo la capacità;
i prezzi V1 sono semplici ipotesi, da validare con costi e domanda.
La voce «profitto netto operativo» della V1 va letta come contributo di cassa
prima delle voci non registrate. Nessun nuovo consenso ripetuto è richiesto per
azioni già autorizzate nella sessione; diritti incerti non si risolvono con un
semplice clic di approvazione.
