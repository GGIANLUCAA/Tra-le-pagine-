# Vidu mobile — Tra le Pagine

Pannello autonomo per generare una singola scena con Vidu, da telefono e senza ChatGPT Work.
Il servizio è separato dal sito storico e riusa autenticazione proprietario e archivio R2 del Video Library Studio. Nessun master o catalogo pubblico viene modificato.

## Funzioni

- Accesso con la chiave di gestione Studio, verificata dal servizio originale tramite binding interno; solo memoria del browser.
- Collegamento API Vidu una sola volta: verifica GET del saldo, chiave cifrata AES-GCM in R2; chiave di cifratura in un secret Worker separato. Nessuna API restituisce la chiave.
- JPG/PNG entro 6 MB, progetto, scena, frase narrata, secondo di inserimento, ragione narrativa e prompt.
- Preventivo gratuito Q2 Pro Fast 720p, 2–10 s, audio/raccomandazione prompt disattivati. Listino iniziale verificato il 28/10/2026. Stima, non promessa di prezzo bloccato dal provider.
- Validità preventivo 10 minuti. Prezzi verificabili/aggiornabili dal proprietario nelle impostazioni ogni 7 giorni. Se cambia la regola off-peak occorre aggiornare il codice.
- Codice legato a immagine, prompt, scena, narrazione, parametri e prezzo; conferma esplicita per ogni invio.
- Prenotazione R2 atomica prima dell'unico POST a pagamento. Timeout = stato incerto da verificare nella console, mai reinvio automatico.
- Recupero automatico ogni 10 minuti dei soli task già approvati. Il cron non può generare nuovi video. Salvataggio MP4 privato, scheda JSON e player/download autenticati.
- Video salvati come `.bin` nella cartella `private-vidu/v1/`, per tenerli fuori dal catalogo pubblico che elenca MP4. Scaricati con nome `.mp4`.

## Stato e limiti

Questa versione genera e archivia clip. La scheda conserva progetto, frase e punto di inserimento, ma NON esegue il montaggio FFmpeg del libro e NON dichiara approvazione artistica. L'immagine viene decodificata dal browser; il server verifica intestazione, dimensioni e hash, non la qualità narrativa. Il download verifica dimensione, firma MP4 e SHA256: non sostituisce ffprobe/visione/ascolto V44.

Il collegamento richiede la chiave API Vidu del proprietario nella pagina privata: i secret GitHub non sono esportabili e non vengono copiati dai log o dal browser. Nessun abbonamento nuovo richiesto dal codice; l'utilizzo Cloudflare/R2 rimane soggetto alle quote del proprio account, non garantito gratis illimitatamente.

Test con provider simulato: nessun credito Vidu consumato. Una generazione reale richiederà autorizzazione della scena/preventivo e servirà a verificare end-to-end l'account collegato.

## Esercizio

`wrangler.toml` configura `STUDIO` → `video-library-studio` e `VIDEOS` → bucket esistente. Impostare `CONFIG_SECRET` casuale di almeno 32 caratteri tramite Worker Secrets; conservarlo durante ogni deploy, altrimenti la chiave Vidu cifrata diventa illeggibile. Non utilizzare un secret condiviso con altri servizi.

Deploy: `npx wrangler deploy --config integrations/vidu_panel/wrangler.toml`. Non inserire credenziali nei sorgenti. Non cambiare piani di fatturazione né acquistare quote automaticamente.

Test: `node --test tests/test_vidu_panel.mjs`.
Fonti: https://platform.vidu.com/docs/pricing e https://platform.vidu.com/docs/api-reference/video-models/vidu-q2/image-to-video ; https://developers.cloudflare.com/r2/reference/consistency/ .
