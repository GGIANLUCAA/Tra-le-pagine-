# Centro di controllo V14 — semplificazione prima di tutto
**11 novembre 2026 · Prototipo e deploy sul Worker di anteprima indipendente; NON modifica la videoteca principale.**

## Problemi osservati nella V13
1. **Barra troppo in basso sul telefono.** Una hero editoriale alta, quattro KPI grandi, un riquadro «Da fare» con tre pulsanti e molti pannelli separavano il proprietario dall'informazione principale: lavori e tempi.
2. **Informazioni duplicate.** La stessa salute produzione appariva in Home e in Salute produzioni; categorie e diario riempivano la Home pur avendo già pagine dedicate.
3. **Troppe vie di navigazione.** Cinque pulsanti inferiori e undici tab desktop: il cliente Android vuole riconoscere subito Home, quadri, aiuto, archivio.
4. **Ripara GPT eccessivamente carico.** Header esplicativo, tutti i workflow, directory chat, varianti per quadro, video recenti e storico errori sempre esposti. Difficile trovare l'azione importante.
5. **Aggiornamenti che chiudono i pannelli.** La ricostruzione HTML a ogni refresh del progresso poteva richiudere elementi `details` aperti.

## Modifiche V14
- Homepage mobile senza hero gigante né grandi quattro card statistiche, prima contenuto realmente utile: **Avanzamento dei lavori**; poi **Da controllare** e tre scorciatoie (Quadri, Video disponibili, Ripara). Nessuna categoria ripetuta in Home.
- Indicatore di aggiornamento e raggiungibilità fonti conservati nella testata.
- Le informazioni secondarie sono raggiungibili in **Altri programmi e informazioni** e nelle pagine esistenti; le funzioni non vengono cancellate.
- Navigazione mobile ridotta a quattro scelte: Home, Quadri, Ripara GPT, Archivio. `Da fare`, `Salute`, Qualità, Diario e Statistiche restano accessibili dalle scorciatoie e dalle sezioni esistenti.
- Schermata Ripara: prima le tre azioni per programma, Sblocca, errori tecnici; soltanto se l'utente le apre, le sezioni **Seleziona quadro**, **Altri video**, **Collegamenti ChatGPT** e **Storico errori**.
- Conservati collegamenti chat Android nativi e browser, memoria correzioni per singolo video, recupero senza duplicati, verifica file, log originali, QA.
- Gli elementi avanzati aperti dall'utente rimangono tali dopo l'aggiornamento automatico dei dati. Nessuna modifica alle API di telemetria o stima di durata.
- Nuova dicitura **CONTROL CENTER · V14**.

## Limitazioni esplicitate
- Una run GitHub conclusa NON certifica un video completato né approvato. La barra segue gli step osservabili, non un avanzamento MP4 inventato.
- Le automazioni ChatGPT non espongono necessariamente gli step al Worker. Nessun lavoro «in corso» viene dedotto da silenzio o assenza nel campione.
- Questo sito rimane sola lettura. «Ripara GPT» prepara una richiesta e apre la chat, non modifica di nascosto il repository.
- I link chat locali rimangono nel browser corrente.
- Il Worker Video Library Studio e gli originali MP4 sono fuori ambito.

## Verifica
- CI `.github/workflows/artvision-control-center-preview-ci.yml`: sintassi HTML/JS, componenti senza mutazioni, test del flusso ChatGPT e del modulo di barra.
- Test `tests/control-center-action-hub-dom.test.cjs`: Home con avanzamento sopra diagnostica, quattro comandi mobile, dettagli nascosti per default, ripristino espansione al refresh, richiesta riparazione e nota per video.
- Pubblicazione soltanto dopo CI riuscita e successiva verifica versione Cloudflare.
