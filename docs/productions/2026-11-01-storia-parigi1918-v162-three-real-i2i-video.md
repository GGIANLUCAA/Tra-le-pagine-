# La Storia Rivive · Parigi 1918 V162 — tre I2I VERI e nuovo MP4 da revisione
Data: 1 novembre 2026 · issue #144 · mandato V108 · **NON master V98 e NON pubblicabile**.

## Risultato reale
- Fonte unica: Musée Albert-Kahn, AI139599, 1918, dichiarata CC0 su Wikimedia (licenza e file da verificare editorialmente per Italia). Originale **11.148.380 byte**, SHA1 `aa471da773d14f422d1387654601ca03b5224455`, provenienza accertata.
- Sequenze archivistiche: cinque riprese diverse e autentiche dello stesso file (inizio rispettivamente `22.90`, `86.80`, `132.10`, `208.65`, `238.90` secondi). Diversi giorni/occasioni di Parigi, NON un singolo evento del 1918.
- Modello colore **realmente eseguito** sui byte della pellicola: DDColor ONNX (`edgetools/ddcolor/ddcolor-tiny-fp16.onnx`, checkpoint SHA256 `2653da00dc15e54a45e5200b61dbf82ee9ceaf56b02bb9b9657569ac775e82e6`).
- Modello fotografico **realmente chiamato**: Space pubblico Finegrain, tre output PNG I2I di scene 1, 2, 3 ritornati e tecnicamente validati (corr 0.9829, 0.9768 e 0.9737). SHA256 rispettivamente:
  - scena 1: `5648bc952703a31dfbfec7501be04ff34a9297437a180cfd73a2f12258f7f64c`
  - scena 2: `fd6eaee3c6e4ba070b4f6ffeb357284360b102d3c2e9a2b47daa282a2e7e1fc0`
  - scena 3: `d2d1d0eef1c2fd0bd195c914d45652345c2c5282d7f2bbcefee7fb133c81d442`
- Quarta prova **AppError** dal provider gratuito, senza retry né pagamento. Scena 4: SOLO DDColor, saturazione moderata; **non chiamarla I2I**.
- Scena 5: **VERA pellicola originale in movimento** con colore DDColor allineato con flusso ottico all'esatta scena, **NON Vidu**.
- Fonte film SD 720×576 pixel encoded, SAR non quadrato; export 4:3 corretto in canvas verticale 720×1280, non scansione HD né 4K.
- Musica di accompagnamento originale, titolo discreto `PARIGI · 1918`, fonte piccola, quattro bozze social. Zero pubblicazione.

## Risultato audiovisivo V162 creato in ChatGPT
- `LA_STORIA_RIVIVE_PARIGI_1918_V162_NEURAL_REVIEW_NON_FINALE.mp4`: **17,000s**, **510 frame** a 30fps, **720×1280**, H264/AAC, **2.992.359 byte**, SHA256 `3bbdcaa05e7176c9b2906308f0ddf60c91ac7090631cd65e1c39abcfa2c9a8a0`.
- **FFmpeg full-decode PASS**, FFprobe video+audio PASS, ZIP CRC test PASS.
- `LA_STORIA_RIVIVE_PARIGI_1918_V162_KIT_ANDROID.zip`: **3.088.211 byte**, SHA256 `7bbbdb9620b63508436eb6eda16fe359aac800ed78ef964a5957c25035d6c81e`.
- MP4 e ZIP sono stati creati e forniti come veri download nella conversazione, **non** come GitHub Release o pubblicazione sul sito. Non dedurre dal documento che siano in archivio GitHub.
- Evidenza di chiamata inferenza e 3 fotografie autentiche in [run GitHub #41258480694](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41258480694), artifact privato `V162_PARIS1918_REAL_NEURAL_PHOTO_CANDIDATES_PRIVATE` (ID 13064595063). Questa Action produce i PNG e il report, NON è la prova FFmpeg del MP4 montato localmente.
- QA visivo campionato sui cinque capitoli, ma **approvazione artistica completa assente**. Le misure di correlazione non sono garanzia di fedeltà di volti/mani/insegne.

## Stato e vincoli aperti
`rendered_needs_review`; **3/4** vere foto generative source-locked; **0/1** clip Vidu; **0 crediti Vidu**, nessuna API a pagamento, nessuna pubblicazione e nessuna falsa autorizzazione; **V91/V94/V96/V99 master gate NON PASSATI**.

Per avanzare al video completo: ottenere quarta fotografia I2I fedele e rivista, produrre quinta clip Vidu con autentica animazione solo dopo saldo/preventivo/consenso esatto previsto dal gateway, confrontare V98 su byte finali, revisionare diritti Italia e QA artistico. Non avviare scheduler seriale.
