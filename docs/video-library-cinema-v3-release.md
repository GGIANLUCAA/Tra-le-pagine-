# Video Library Studio — Cinema Studio V3

Data: 24 ottobre 2026. Implementazione pubblicata su
https://video-library-studio.600led.workers.dev

## Cos'è cambiato
- Home cinematografica con brand ridisegnato, video in evidenza riproducibile, contatori sintetici.
- Collezioni per genere con anteprime reali e conteggi aggiornati dal catalogo.
- "Appena arrivati" (12 video in uno scorrimento orizzontale).
- Modalità Studio per l'amministratore con "Pronti da pubblicare" e indicatori editoriali.
- Ricerca visibile, filtro riproducibilità, filtri avanzati a scomparsa, gruppi di varianti opzionali.
- 36 schede iniziali con pulsante "Mostra altri" per ridurre il carico sullo smartphone.
- Vista a schede o vista compatta per il catalogo.
- Barra inferiore Android con Home, Video, Raccolte, Studio.
- Lettore video con pulsanti video precedente/successivo, +/- 10 secondi e velocità 1x–2x, mantenendo i controlli nativi.
- Modalità di selezione multipla dopo login e accesso allo Studio: preferiti, finale, provino, archivia. Massimo 40 per operazione, richieste in serie; nessuna cancellazione permanente in blocco.
- Confermata eliminazione definitiva singola protetta da doppia conferma, download e scheda informativa, link social, esportazione CSV.
- Nessuna modifica agli originali né alla struttura R2.

## File e pipeline
- Sorgente attualmente pubblicata: `site/video-library-v2.html` (nome precedente conservato per compatibilità).
- Versione preliminare testata: `site/video-library-v3-preview.html`.
- Backup precedente alla modifica: `site/backups/video-library-before-cinema-studio-2026-10-24.html`.
- Workflow pubblicazione: `.github/workflows/video-library-enrich.yml`. Usa il Worker import ufficiale per pubblicare il sorgente nel bucket come `site/index.html`.
- Test preliminari: `.github/workflows/video-library-v3-preview-test.yml`; controlla markup, JS, ricerca, paginazione, vista compatta, Studio privato.
- Test sito pubblico: `.github/workflows/video-library-site-smoke.yml`; controlla UI, streaming, download e sicurezza delle API.

## Indicazioni d'uso su Android
1. Apri il sito.
2. Premi Home per il video principale, Raccolte per i generi, Video per l'archivio completo.
3. Premi Studio per entrare nella gestione privata con la chiave già in tuo possesso.
4. Apri "Seleziona video", spunta i video (massimo 40), scegli Preferiti, Finale, Provino o Archivia. Verrà richiesta conferma prima del salvataggio.
5. Per recuperare una scheda archiviata, abilita "Mostra archiviati" e ripristinala dalla modifica singola.
6. "Elimina definitivamente" resta disponibile soltanto per una singola scheda autorizzata e cancella il file da R2. Non equivale ad archiviare.

## Note e limiti
- I video registrati esclusivamente nella Libreria ChatGPT continuano a mostrare "Solo ChatGPT": non si simula la riproduzione se l'MP4 non è ancora accessibile dal sito. Il ponte di importazione è un sistema separato.
- Il grouping delle versioni è facoltativo e basato sul nome: non garantisce l'identità dei contenuti.
- Alcuni MOV/MKV/HEVC possono richiedere conversione prima di essere riprodotti dal browser; non si finge supporto completo.
- L'archivio ha diverse centinaia di video, quindi i numeri possono variare dopo le sincronizzazioni.
- Il contenuto del catalogo è pubblico nella modalità vetrina. La gestione privata richiede autenticazione.
- In caso di regressione, ripristina il backup della sorgente in `site/video-library-v2.html` e lascia completare il workflow di pubblicazione.
