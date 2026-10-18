# 🎬 TRA LE PAGINE — Studio video automatico

**Da Android, senza Colab, senza carta di credito e senza editor.**

Questa cartella produce un video MP4 verticale narrato in italiano a partire dal copione e dalle illustrazioni di un episodio.

## Primo episodio
**La novella degli scacchi** — Stefan Zweig, episodio 01.

La cartella `episodes/01_scacchi/` contiene:
- `testo.txt`: copione narrato.
- `scenes.json`: 20 scene in ordine.
- `metadata.json`: titolo e autore.
- `DESCRIZIONE_SOCIAL.txt`: descrizione per Instagram, Facebook e YouTube.

**Per la versione bella** basta caricare un solo file `episodes/01_scacchi/scene_premium.zip` contenente **12 immagini** chiamate `scena_01.jpg` ... `scena_12.jpg` (accetta anche PNG e WEBP). Il programma le estrae automaticamente e costruisce **16 cambi di scena sincronizzati alle frasi pronunciate** tramite `scene_cues.json`. **Non caricare una sola immagine collage**: nello ZIP devono esserci 12 immagini separate. Finché questo archivio non c'è, il sistema usa disegni di test NON adatti alla pubblicazione.

## Come scaricare il video dal telefono
1. Apri **[Actions → Tra le Pagine - Video automatico](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/produci-video.yml)**.
2. Tocca l'ultima esecuzione del progetto. Un segno verde significa che l'elaborazione è riuscita; una croce rossa significa che è fallita e richiede diagnosi.
3. Scorri in basso fino ad **Artifacts**.
4. Tocca **TRA_LE_PAGINE_EP01_MP4_e_audio** e scarica il file ZIP.
5. Estrai lo ZIP su Android; dentro trovi `TRA_LE_PAGINE_EP01.mp4`, `VOCE.wav`, `SOTTOTITOLI.srt`, `MUSICA_ORIGINALE.wav`, copione/descrizione e dettagli tecnici.

Per produrre una nuova versione vai nella stessa pagina, premi **Run workflow**, seleziona `kokoro` e avvia. In alcune versioni Android serve attivare *Sito desktop* per visualizzare il pulsante.

**Il workflow si avvia anche automaticamente quando ChatGPT aggiorna il codice o il contenuto degli episodi.**

## Qualità e trasparenza
- La prima scelta è **Kokoro TTS**, voce italiana maschile `im_nicola`. Se installazione o generazione falliscono, il sistema riprova con `espeak-ng` (voce italiana robotica, inferiore qualitativamente).
- I sottotitoli sono sincronizzati sulla durata di ogni frase ma i singoli segmenti usano una stima proporzionale.
- I video sono 720×1280, 24 fps, musica sintetizzata in modo originale, movimento lento sulle immagini.
- Il codice non pubblica automaticamente sui social e non genera un cartoon animato AI: serve una revisione prima della pubblicazione.
- Il repository è pubblico e i file sono visibili a chiunque. **Non caricare documenti personali o contenuti riservati.**
- La sintesi Kokoro usa pesi con licenza Apache 2.0; le immagini sintetiche create dal codice non usano materiale fotografico esterno.
- GitHub Actions per repository pubblici usa runner gratuiti, ma GitHub può modificare disponibilità e limiti.

## Tecnico
La pipeline è nel workflow `.github/workflows/produci-video.yml` e nel programma `src/render.py`. Non devi eseguirli sul telefono.

Quando chiederai un altro libro a ChatGPT, potremo aggiungere una cartella `episodes/02_nome_libro` e aggiornare l'avvio per selezionarlo.
