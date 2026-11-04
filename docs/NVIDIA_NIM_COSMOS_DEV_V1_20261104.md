# NVIDIA NIM + Cosmos3 Nano — collegamento sperimentale 04/11/2026

## Contesto deciso dal proprietario
Tutti i filmati attualmente in preparazione per ArtVision e La Storia Rivive sono
**prove R&D non destinate alla pubblicazione**. Possiamo quindi valutare anche
modelli NVIDIA del programma Developer se il loro trial lo consente. Non significa
che una API sia gratuita per sempre; non utilizzare modelli o GPU a pagamento
senza verificare il piano e stabilire esplicitamente un budget.

## Due integrazioni tecniche REALI, entrambe opt-in

1. `src/nvidia_nim_dev_v1.py`: API chat `https://integrate.api.nvidia.com/v1/chat/completions`
   compatibile con le API OpenAI, per `narration`, `storyboard`, `source_notes`,
   `social`, `qa_second_opinion`. Un solo modello NVIDIA dichiarato e una sola
   chiamata per prova. Il risultato è **bozza editoriale**, non render MP4.
2. `src/nvidia_cosmos3_video_dev_v1.py`: endpoint Cosmos3 Nano
   `https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano` in modalità
   `text2video` o `image2video` con file immagine locale PNG/JPEG/WebP.
   La demo produce **25 fotogrammi a 24fps (circa 1,04 secondi)** nel preset
   `480_9_16`, un MP4 sintetico sperimentale, **non** un video finito 25–35 s,
   **non** 4K, **non** prova di restauro autentico. Watermark SynthID e sistemi
   di sicurezza del provider NON vengono rimossi o aggirati. Per clip più lunghe
   servono test aggiuntivi, montaggio e controlli di coerenza/diritti.

La documentazione Cosmos indica MP4 con video VP9: il workflow conserva il
file originale e prova a creare una versione H264 compatibile con Android
senza rimuovere la filigrana, quando ffmpeg è disponibile sul runner.

## Collegare la chiave (unico passaggio manuale necessario)

1. Accedere a **https://build.nvidia.com/**, aprire l'account NVIDIA Developer,
   controllare che il modello desiderato abbia endpoint abilitato e accesso
   per R&D, e verificare quota, limiti e possibili addebiti reali.
2. Generare la chiave nel proprio account NVIDIA
   (`https://build.nvidia.com/settings` o la pagina chiavi del provider).
3. Aprire **https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions**
   e creare un repository secret chiamato **NVIDIA_API_KEY**.
   Non inviare chiavi in chat, screenshot, repository o file di configurazione.

Il connettore GitHub non può inserire il secret al posto del proprietario.

## Come provarlo senza far partire una produzione

Da GitHub Actions:
`.github/workflows/nvidia-nim-dev-v1.yml`
(**NVIDIA NIM e Cosmos3 - prove sviluppo**).

- Selezionare `check_secret`: controlla soltanto la presenza della chiave
  (nessun consumo inferenza).
- Selezionare `nim_text`: una richiesta con modello NIM dichiarato
  (esempio `nvidia/llama-3.3-nemotron-super-49b-v1.5`, verificare nell'account).
- Selezionare `cosmos_video`: una prova testuale di scena storica
  **inventata/sintetica**; non trasferita alla produzione vera.
- Per le due prove con inferenza, confermare espressamente le condizioni
  Developer R&D e che il proprio account permette il test senza addebiti.
- Recuperare l'artifact `NVIDIA_DEV_TEST_UNREVIEWED_<run>` con draft
  oppure file MP4 sperimentale. Nessuna pubblicazione o caricamento in
  Video Library Studio.

Test automatizzati Python con risposte simulate e senza credenziali:
`tests/test_nvidia_nim_dev_v1.py`,
`tests/test_nvidia_cosmos3_video_dev_v1.py`.
**Test del codice non equivalgono a collaudo vivo dell'account**:
la prima chiamata NVIDIA reale richiede il secret e la scelta esplicita.

## Sicurezza e diritti

Nessuna chiamata NVIDIA nelle automazioni orarie V101 o ArtVision owner.
Nessun fallback a un modello a pagamento, nessun retry su 429, nessun
addebito API imposto dal repository. I dati originali degli archivi devono
essere trattati secondo i rispettivi termini anche quando il video resta privato.
Non mescolare la scena sintetica con un autentico restauro storico senza
comunicare internamente l'origine; non attribuire al film originale dettagli
inventati dall'AI. Restano obbligatorie le regole dei video, le cornici reali,
i titoli inglesi uniformi e la revisione tecnica/artistica.

## Riferimenti ufficiali

- https://docs.api.nvidia.com/nim/docs/product
- https://docs.api.nvidia.com/nim/reference/llm-apis
- https://docs.api.nvidia.com/nim/reference/nvidia-llama-3_3-nemotron-super-49b-v1_5-infer
- https://build.nvidia.com/nvidia/cosmos3-nano/modelcard
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
