# Centro di controllo V13 — Barra più utile, stime prudenti e regia Android
**10 novembre 2026 · Revisione della PR #251, non pubblicata sul sito live.**

## Decisione del proprietario
Migliorare la barra di avanzamento reale, affidabilità delle stime, leggibilità, design e utilità pratica. Niente percentuali finte, lavori duplicati o spese API inutili.

## Comportamento implementato
- **Barra tecnica reale:** passaggi GitHub completati / passaggi osservati. La percentuale non rappresenta il filmato; non viene simulata, non cresce da sola e può variare se GitHub introduce nuovi passaggi. Senza step si mostra una barra indeterminata.
- **Fase corrente:** raggruppata per materiale/fonti, audio, elaborazione video, controlli, consegna, oppure «passaggio GitHub»; è solo classificazione del nome di uno step reale. Si mostra il nome esatto e da quanto tempo la fase è iniziata se noto.
- **Memoria breve delle fasi:** ultimi quattro step GitHub realmente completati, con orario ed esito, in un pannello richiudibile. Nessuna interpretazione di file/video che non siano stati letti.
- **Stima migliorata:** il Worker esamina fino a 25 esecuzioni dello stesso `workflow_id`, sul ramo `main`, terminate con successo con orari verificabili (solo trigger `schedule`/`workflow_dispatch`). Richiede **almeno 5** campioni validi, usa quantili interpolati 20/50/80, e con almeno 10 esecuzioni esclude valori anomali tramite IQR se rimangono almeno 5 osservazioni. Livello «storico limitato» sotto 10 casi, «storico discreto» da 10; niente promessa di accuratezza.
- **Orari intuitivi:** oltre ai minuti rimanenti, mostra una finestra in ora locale `HH:MM–HH:MM` quando la stima è effettivamente disponibile. Indica sempre che è la **fine tecnica del workflow**, non la consegna MP4.
- **Stima sospesa:** quando lo storico è insufficiente, la run non è confrontabile, manca un tempo di avvio, la durata supera l’80° percentile storico, la run è già conclusa o le prove non sono recenti.
- **Segnali di attenzione:** nessuna nuova transizione GitHub per almeno 30 minuti invita a verificare il log: **non è prova di un render bloccato**. Fallimenti/timeout/cancellazioni sono segnalazioni distinte e aprono la diagnostica GPT. La pagina non riavvia lavori da sola.
- **Freschezza della scheda:** se l’ultima prova di stato risale a più di 5 minuti fa, avvisa e nasconde la finestra ETA. Aggiorna in automatico quando il Centro è aperto, circa ogni 105 secondi.
- **Schermata Android:** gerarchia chiara «adesso» e «fine stimata», barre discrete, spazio per orario/ultimo segnale, azione consigliata e pulsanti con altezza touch adeguata. Dettagli meno importanti chiusi per impostazione predefinita.

## Video identificato dalla run, senza supposizioni
Il Worker prova ora a collegare un'esecuzione GitHub a uno **specifico quadro e variante** quando esiste **un solo** `run_id` corrispondente nella coda ArtVision verificata. Mostra titolo, variante e, se il catalogo dichiara disponibile un MP4 con nome valido, il link alla riproduzione. Se più varianti condividono la stessa run, il pannello indica l'ambiguità e **non** attribuisce quel progresso a un singolo filmato. Le produzioni La Storia Rivive/WOW non vengono abbinate per somiglianza di nome. La corrispondenza con una run non prova che quel file sia già stato prodotto, revisionato o approvato.

## Limiti reali ancora presenti
1. È una barra **della run GitHub**, non del singolo video ArtVision/Storia/WOW prodotto da ChatGPT. I dati pubblici GitHub non collegano automaticamente un job a un MP4 con chiave certa; per una vera ETA video occorrono checkpoint per ogni produttore e prove di file reali.
2. La stima ha base statistica **campionaria**: non è affidabile se lo stesso workflow ha durate estremamente variabili, se l’evento è un altro tipo di lavoro o se la coda è incompleta.
3. Non sono stati aggiunti polling aggressivi o nuove richieste alle API Vidu; il controllo resta GET-only, con cache su GitHub, numero di run limitato e nessun backend di scrittura.
4. La presenza di una barra al 100% non attesta MP4, ZIP, download integrale, audio, diritti, qualità artistica o approvazione Gold. Restano gate indipendenti.

## Verifiche
- Modulo backend `site/control-center-progress-v13-backend.fragment.js` incorporato nel Worker read-only.
- Modulo UI `site/control-center-progress-v13-frontend.fragment.js` incorporato nel Centro.
- Test `tests/control-center-progress-v13.test.mjs` su robustezza, campioni insufficienti, outlier, fase, pausa della stima, orario locale.
- Test DOM `tests/control-center-action-hub-dom.test.cjs` controlla la fase, la barra GitHub, la dicitura «non del video» e la cronologia.
- CI `.github/workflows/artvision-control-center-preview-ci.yml` compila l’anteprima **senza deploy**.
- Le norme di memoria correzioni V321 restano attive. Il monitoraggio del sito per tre giorni già programmato è separato e non viene duplicato.

## Evoluzione successiva da validare
Rendere per-video la stima soltanto dopo aver introdotto nel produttore un `video_id` stabile, heartbeat e `phase_started_at`/completata, SHA/dimensione/output reale, e almeno cinque durate confrontabili per ogni tipologia. Nessuna fase QA o Gold va impostata automaticamente a successo.
