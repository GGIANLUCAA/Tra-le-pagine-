# Video Library Studio — ponte nativo ChatGPT (prototipo)

## Stato attuale

Questo prototipo **non è installato in ChatGPT** e **non trasferisce ancora file**. È il componente di selezione da utilizzare in un plugin MCP autorizzato: `site/gpt-library-picker.html`. Non può funzionare da solo sulla pagina pubblica Cloudflare.

## API verificata

La documentazione ufficiale OpenAI descrive:
- `window.openai.selectFiles()` — scelta autorizzata dei file nella Libreria ChatGPT.
- `window.openai.getFileDownloadUrl({ fileId })` — collegamento di download **temporaneo**, non URL pubblico permanente.
- il metadata `_meta["openai/fileParams"]` negli strumenti MCP per trasferire un file autorizzato al server.

Fonte: https://developers.openai.com/plugins/reference#file-apis

## Architettura per la soluzione completa

1. Plugin MCP **privato**, collegato dall'utente in ChatGPT, con widget di selezione file (autorizzazione esplicita della Libreria).
2. Il widget ricava per ogni file il nome e un fileId autorizzato; il tool import riceve l'oggetto `fileParams` con `download_url` temporaneo.
3. Un backend autenticato acquisisce il contenuto in streaming **una sola volta**; niente copie sul telefono. **Non** memorizza URL temporanei nel catalogo.
4. Deduplica con SHA-256 e confronto dimensioni, nomi e varianti; preserva volutamente versioni differenti.
5. Quando si trova un file già disponibile in R2, lo si associa senza ricaricarlo.
6. Il file finale risiede in uno storage con HTTP Range e link stabile, per poter essere riprodotto sul sito anche fuori dalla sessione ChatGPT. Storage sostituibile: R2, S3, Google Drive via OAuth, NAS.
7. FFmpeg genera poster JPEG e preview MP4 H.264/AAC a bassa risoluzione solo dove richiesto. L'originale rimane uno solo.
8. Le nuove produzioni GitHub sono già sincronizzate; le produzioni native ChatGPT richiedono la prima selezione autorizzata e un tool MCP fileParams con accesso all'originale.

## Formati

- MP4 H.264/AAC e WebM VP8/VP9/Opus: riproduzione nativa dove supportata.
- HEVC, MOV, MKV, AVI: il contenitore NON garantisce codec compatibili nel browser. Creare un preview MP4 480–720p o HLS con FFmpeg, mantenendo l'originale e senza duplicazioni inutili.
- Video.js / hls.js / Shaka Player facilitano player HLS, ma non recuperano file privati senza un'origine autorizzata.

## Prossimi test obbligatori prima di chiamarlo completo

- Collegare il proprio server MCP personalizzato in ChatGPT, installare il plugin, provare `selectFiles()`.
- Effettuare un import test con `Fur_Elise_Music_Motion.mp4` autentico via fileParams.
- Verificare che l'URL temporaneo sia utilizzabile dal backend e che il contenuto abbia esatta dimensione, hash, video/audio validi, niente errore CORS/403.
- Testare il riavvio del sito **dopo** la scadenza URL.
- Confermare mancati duplicati alla seconda importazione, player da telefono e accessi privati.
- Solo dopo rendere automatica l'importazione di massa.

## Sicurezza

Mai pubblicare in pagina, log o repository i downloadUrl privati, token admin o credenziali OAuth. Il backend deve validare utenti, host sorgenti e limiti di dimensione, impedire SSRF e rispettare autorizzazioni. Non mostrare i video privati agli utenti anonimi.
