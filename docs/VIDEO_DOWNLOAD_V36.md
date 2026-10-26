# Video Download V36 — consegna che non dipenda da un solo link MP4

## Perché
L'utente ha segnalato più volte che alcune immagini e ZIP ChatGPT si scaricano, mentre il link al video MP4 riporta "file not found" o non apre un file scaricabile su Android. Il problema può essere nel trasporto file/link dell'app o nelle sue anteprime; un MP4 valido sul runner non prova che un link sandbox temporaneo funzioni sul telefono.

Il **26/10/2026** il video `LA_COLLANA_VIDEO_FINALE.mp4` è stato verificato con `ffprobe` e decodificato integralmente con `ffmpeg -f null`: H.264 High, AAC LC, durata 164.67s; `moov` già iniziale (faststart), file ~12MB. Lo ZIP originale è stato verificato CRC OK. Non attribuire automaticamente un eventuale 404 al codec.

## Regola pratica di consegna
Per ogni MP4 narrato, pubblicare almeno:
1. **Master MP4** con hash, durata, codec audio/video, file esistente.
2. **ZIP SOLO VIDEO**: un archivio contenente esclusivamente quel master MP4, per aggirare limitazioni di anteprima o mime dell'app. È una copia e consuma storage: retention limitata.
3. **Android 480p** solo quando serve: H.264 Main, AAC LC, yuv420p (TV), 480×854, moov all'inizio. ZIP della versione leggera come alternativa.
4. **VERIFICA_DOWNLOAD.json**: SHA256, stato del master e avvertenza che il controllo locale non prova il link ChatGPT.
5. Collegamento permanente in Video Library Studio/R2 solo dopo importazione reale del video. Non inventare URL R2 se il file è ancora esclusivamente nella conversazione.

### Uso gratuito su file già creati
```bash
# Una versione completa e un singolo ZIP per scaricare il MP4 senza il resto del progetto
python src/video_download_fallback_v36.py --input ./mio_video.mp4 --output-dir ./DOWNLOAD_FACILE

# Se il download MP4 da ChatGPT/Android continua a fallire, creare anche una versione più compatibile
python src/video_download_fallback_v36.py --input ./mio_video.mp4 --output-dir ./DOWNLOAD_FACILE --android

# Con motore episodi (un master TRA_LE_PAGINE_EP*.mp4 in output)
python src/video_download_fallback_v36.py --source-dir output --output-dir output/DOWNLOAD_FACILE
```

Il workflow `.github/workflows/render-v3.yml` ora inserisce automaticamente `DOWNLOAD_FACILE` nell'artifact già previsto, con **solo ZIP master**. La variante Android è **on demand**, per evitare di moltiplicare costi di CPU e storage in grandi lotti.

### Android
Se il link MP4 dà "file not found", scaricare **SOLO_VIDEO.zip**, aprirlo con Files/Archivio file, estrarre MP4 e aprirlo nel lettore locale. Gli ZIP vengono controllati con CRC e contenuto hash identico al master. Questo non equivale a garantire che tutti i link sandbox persistano: utilizzare Video Library Studio/R2 per un archivio stabile quando il video è stato importato.

### Controlli del codice
- Esiste MP4, traccia video e audio, durata positiva, nessun sottotitolo V12.
- Decodifica completa senza errori prima di consegnare alternative.
- ZIP contiene esattamente un MP4 e l'hash ricostruito coincide con il master.
- Originale mai sovrascritto.
- Conversione mobile condizionata all'opzione `--android`.
- Nessuna chiamata a Gemini, GPT, servizi Premium o pubblicazione.

### Limite vero
Né Python né GitHub Actions possono riparare il sistema di link sandbox del client ChatGPT. Consegna alternativa verificata è diversa da "problema della piattaforma risolto".
