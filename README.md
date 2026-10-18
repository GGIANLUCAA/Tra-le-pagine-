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

## Voci italiane — aggiornamento ottobre 2026
Nel menu **Run workflow → Voce narrante italiana** puoi scegliere:
- **supertonic (predefinita)**: voce maschile M1 italiana, modello open-weight archivio Supertonic 3, nessuna API né pagamento per episodio; esegue la sintesi CPU direttamente su GitHub. OpenRAIL-M richiede di rispettare restrizioni d'uso e trasparenza sui contenuti generati. Descrizione social aggiornata con dichiarazione IA.
- **edge**: voce neurale italiana Diego con intonazione per paragrafi completi, più naturale da valutare ad orecchio; richiede il servizio online gratuito Edge Read Aloud. **Diritti commerciali di tale accesso non chiariti da Microsoft**: utile per test, non presumere di poterlo usare per contenuti monetizzati.
- **kokoro**: voce maschile im_nicola, modello open-weight Apache 2.0, ma è risultata poco naturale in italiano.
- **espeak**: emergenza tecnica, non adatta per la pubblicazione.

Ogni cambio di motore rigenera automaticamente audio, sottotitoli e tempi delle inquadrature. Non è necessario modificare o rigenerare le immagini. 
La voce Supertonic viene sintetizzata localmente dal runner GitHub; per accelerare le successive generazioni, la cache conserva il modello di circa 400 MB.

**I 2 provini Supertonic e i 2 provini Edge sono nel progetto come workflow separati**; serve ascoltare e approvare la voce prima di pubblicare.

## Narratore più naturale — Gemini 3.8 Flash TTS (facoltativo)

Per avere una lettura interpretata, con **pause organiche, domande, enfasi ed emozioni**, il generatore offre ora la voce `gemini` che usa **Gemini 3.8 Flash TTS** (modello Google specializzato in audiolibri). Il motore interpreta il racconto in una generazione continua, invece di registrare 34 frasi sconnesse. I tag `<short pause>` e `<long pause>` sono usati solo nei punti narrativi importanti. Una trascrizione Whisper permette di ricollocare sottotitoli e scene dopo le pause.

### Impostazione UNA VOLTA SOLA da Android
1. Apri [Google AI Studio — API keys](https://aistudio.google.com/api-keys), accedi con Google e crea una nuova chiave nel **livello gratuito**. Il modello ha una quota gratuita, con limiti. **Non attivare fatturazione per questa prova.**
2. Copia la chiave generata. **Non scriverla nella chat e non inserirla in un file pubblico del repository.**
3. Apri [GitHub — Secrets del repository](https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions) → *New repository secret*: nome esatto `GEMINI_API_KEY`; nel campo *Secret* incolla la chiave → *Add secret*.
4. Apri [Actions — Video automatico](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/produci-video.yml) → *Run workflow* → nel menu **Voce narrante italiana** scegli `gemini` → *Run workflow*. Dal telefono usa *Sito desktop* se il menu è nascosto.
5. Quando la spunta diventa verde, apri l'esecuzione e scarica l'artifact ZIP con l'MP4 e l'audio. Se fallisce, verifica i registri di errore, senza mai incollare la chiave.

Questa integrazione è configurata e il codice ha superato i test senza chiave, ma **la generazione reale Gemini non è stata testata**: serve la tua chiave inserita su GitHub per fare il primo provino. In caso di quota gratuita esaurita il workflow segnala errore, senza addebiti automatici se non attivi fatturazione.

**Privacy:** sul livello gratuito Google può usare i contenuti inviati per migliorare i servizi, secondo le condizioni del servizio. Invia soltanto copioni destinati alla pubblicazione, mai dati riservati.

**Importante:** la chiave va inserita come *secret*, non come normale variabile, commento o file. Il repository è pubblico; chiunque può leggere i file, ma non il valore dei GitHub Actions secrets.
