# ArtVision — PROCEDURA PERMANENTE / RICETTA DI PRODUZIONE

Versione operativa: 20 ottobre 2026. Questa guida va mantenuta nel repository per il futuro: il progetto non deve dipendere dalla memoria di una chat.

## Principio assoluto
Il repository `GGIANLUCAA/Tra-le-pagine-` è uno studio video modulare. **Non rimuovere mai** narrazioni, video libri, workflow `render-v3.yml`, strumenti Gemini, regie V3/V4/V5, modelli precedenti o le loro configurazioni.
Il modulo ArtVision è separato in `modules/artvision`; workflow separato `.github/workflows/artvision-render.yml`.

Ramo storico intatto prima di ArtVision: `backup-prima-artvision-2026-10-20`.

## Quando l'utente chiede: "Fammi un video su [artista]"
1. Aprire il repository e verificare le versioni correnti del codice e workflow (non indovinare lo stato).
2. Recuperare identità artista (controllare omonimi), eventuali soggetti e periodi richiesti.
3. Cercare opere autentiche nei cataloghi museali tramite le API: Art Institute of Chicago, Cleveland Museum of Art, Metropolitan Museum of Art (o estensioni documentate).
4. Filtrare esplicitamente solo immagini con diritti/condizioni di riuso idonei. Conservare artista, titolo, data, fonte, URL scheda e URL originale, licenza/crediti. Se nessuna fonte idonea, interrompere e comunicarlo, non inventare immagini.
5. Rimuovere duplicati e scegliere sequenza coerente, non affidarsi al primo risultato. Mettere al centro la fedeltà all'opera.
6. Per impostazione predefinita: video verticale 9:16, 150 secondi, intro/finale con nome artista, senza narrazione, con musica utilizzabile e camera digitale discreta.
7. Costi standard: nessuna API di immagini o voce a pagamento; installazioni open-source (Pillow, NumPy, FFmpeg). Non abilitare piani a pagamento o pubblicazioni senza approvazione.
8. **Modalità autonoma preferita**: aggiornare `modules/artvision/queue.json` con un `request_id` nuovo, `artist`, `duration`, `max_works`, `approved_for_render: true`, `publish: false`; il push della coda avvia automaticamente il workflow V1.3. Come alternativa manuale, avviare workflow GitHub `artvision-render.yml` scegliendo `artist`, `duration` (120/150/180) e `max_works` (8/12/16/20/24). Per il telefono: repository → Actions → **ArtVision** → **Run workflow**.
9. CONTROLLARE la run fino a `completed / success`; aprire i report, l'MP4, la copertina, il numero di immagini, l'audio, la durata e la presenza di sorgenti/licenze. Non promettere il file se non è stato creato.
10. Consegnare il pacchetto `ARTVISION_<run_number>` da **Artifacts** della run riuscita; preferire un MP4 diretto quando possibile. Mantenere i link ai file di progetto e al workflow per riutilizzo.
11. Registrare tempi effettivi di elaborazione e motivi degli errori per calibrare quante produzioni al giorno sono realistiche.
12. Pubblicazione social sempre separata dalla generazione e subordinata al controllo dei diritti e dell'utente.

## Risoluzione errori da non dimenticare
- **20 ottobre 2026, run #1 e #2**, exit code 127: runner `ubuntu-latest` privo di `ffmpeg`. Log effettivo `ffmpeg: command not found`. **Soluzione V1.2**: installare ffmpeg con apt prima dei controlli. Non scambiare per causa la warning Node.js 20. Usare `sed -n '1p'` al posto di `head` nelle pipe sotto `pipefail`.
- Leggere sempre il log dello step fallito, senza attribuire problemi alla cieca.
- Se fallisce una sorgente artistica, eseguire fallback verso gli altri archivi. Non disabilitare il filtro diritti per far passare un video.
- Se manca l'Artifact significa che non è stato consegnato il filmato; una run avviata non è prova di video finito.

## File e output standard
`modules/artvision/artvision.py`, `modules/artvision/README.md`, `.github/workflows/artvision-render.yml`.
Per ogni video produrre `ARTVISION_VIDEO.mp4`, `COPERTINA.jpg`, `OPERE_FONTI_E_DIRITTI.json`, `CREDITI_E_FONTI.txt`, `DESCRIZIONE_SOCIAL.txt`, `MONTAGGIO.json`, `REPORT_PRODUZIONE.json`.

## Per la qualità social
Non dipingere nuovi quadri falsamente attribuiti. Non deformare e non falsare il colore delle opere; privilegiare alta risoluzione, belle copertine, ritmo professionale, musica originale o autorizzata. La modalità automatica è un punto di partenza: controllare veramente il risultato e migliorare montaggio/musica prima di dichiararlo ottimale. In futuro aggiungere 1080×1920, curatela cronologica/tematica, galleria anteprima e più tipologie di opere.

## Istruzioni per futuri ampliamenti
Non riscrivere da zero: aggiungere un modulo o preset e testare che il modello precedente funzioni. Backup, cambi piccoli, verifica sul runner e conservazione report; preferire correzioni incrementali misurate.

## Test di collaudo riusciti
- Run GitHub #3: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39411451722 — esito SUCCESS, 150.167 secondi, 16 opere CC0, 24 inquadrature, audio/video verificati, 0 API a pagamento, 176 secondi di elaborazione. Output iniziale 136 MiB.
- Run GitHub #4: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39412319602 — esito SUCCESS dopo cambio preset x264 `ultrafast` → `veryfast`. MP4 14.7 MiB, 150.167 secondi, 720×1280 H.264/AAC, 16 opere. 179 secondi di elaborazione. Per le prossime puntate conservare il preset compatto, con controllo qualitativo.
- **Coda V1.3 testata con successo**: run #6 https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39412758541 — richiesta JSON approvata, raccolta opere, montaggio e artifact `ARTVISION_6` da circa 15 MB, job SUCCESS. Il test iniziale #5 falliva perché scriveva caratteri letterali `\\n` in `GITHUB_ENV`: correggere in vere sequenze di newline Python `\n` (committed).
