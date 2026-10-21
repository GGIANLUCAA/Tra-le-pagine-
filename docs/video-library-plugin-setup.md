# Video Library Studio — import dalla Libreria ChatGPT

## Stato (21 ottobre 2026)
- Worker MCP: `video-library-chatgpt-bridge`, attivo sulla subdomain Cloudflare `video-library-chatgpt-bridge.600led.workers.dev`.
- MCP privato su URL segreto, **non da inserire nel repository**.
- Collegato al bucket R2 `video-library-studio`.
- Tool `open_importer` con widget per `window.openai.selectFiles()`.
- Tool `import_chatgpt_video` con `_meta["openai/fileParams"]=["file"]` e file schema ufficiale.
- Streaming in parti da 8 MiB, fino a 400 MiB per file, con deduplicazione per ID file ChatGPT e dimensione contro i file già disponibili.
- Nessuna cancellazione dei file ChatGPT. Per i nuovi import le immagini e i metadati verranno poi gestiti dal workflow esistente `video-library-enrich.yml`.
- Test automatico `.github/workflows/video-library-chatgpt-bridge-test.yml`: endpoint pubblico di salute, autenticazione negativa, descrizione dei tool, widget, import di prova, deduplica, multipart da 10 MiB.
- **Da verificare**: collegamento del plugin in ChatGPT Work e download_url autentico di uno specifico MP4 ChatGPT.

## Collegamento utente (azione esplicita richiesta)
1. Aprire ChatGPT dal browser e andare su Plugins -> (+) -> Add custom MCP server.
2. Nome `Video Library Studio Import`.
3. Incollare l'URL riservato fornito separatamente al proprietario, che termina con `/mcp`. NON pubblicare l'URL in GitHub o condividere con estranei.
4. Selezionare la connessione HTTP esterna; per questo primo prototipo la chiave riservata è nel percorso (No authentication nell'interfaccia del plugin). In seguito è opportuno passare a OAuth 2.1 se il plugin dovrà essere condiviso.
5. Autorizzare la connessione, creare e installare il plugin.
6. Aprire una chat in Work, selezionare `@Video Library Studio Import`, chiedere `Apri l'importatore dei video ChatGPT`.
7. Selezionare come primo test un MP4 di pochi megabyte (per esempio `Fur_Elise_Music_Motion.mp4`), confermare la pubblicazione e importarlo.
8. Verificare in `https://video-library-studio.600led.workers.dev` che il video compaia e si riproduca. Solo allora importare il resto.

## Avvertenze
- I file importati nello storage R2 dell'attuale sito sono visibili a chi conosce il link pubblico. Importare solo video destinati a essere condivisi o aggiungere in seguito un sistema di autenticazione alla pagina video.
- URL temporanei ChatGPT non vanno conservati: il backend li usa una sola volta per trasferire il contenuto nel proprio storage stabile.
- I primi formati accettati sono MP4/MOV/M4V. WebM/MKV/AVI e file con codec non supportati dal browser richiedono un aggiornamento della pagina o un proxy/transcoding con FFmpeg.
- Tutto il trasferimento autentico resta da confermare con l'account ChatGPT del proprietario. Il test automatico usa video simulati, non accessi alla Libreria reale.
- In caso di file su host temporaneo non riconosciuto, il tool riporta soltanto il nome host e blocca il trasferimento, senza esporre gli URL completi.
