# ArtVision Hokusai V74/V76 — Terzo quadro 4×1, fatto con source autentica e Gacrux

**Autorizzazione**: l'utente ha scritto «Continua a produrre nuovi video» il 30 ottobre 2026, dopo aver ricevuto Socrate e Klimt 4×1. È una richiesta esplicita di proseguire la produzione; questa PR applica la transizione al terzo soggetto editorialmente già concordato, senza liberare indiscriminatamente ogni altra opera o fingere approvazioni artistiche.

## Fonte autentica e ricostruzione Museum

- Il soggetto esatto è **Katsushika Hokusai — Under the Wave off Kanagawa**, ca. 1830–32. Esemplare **Met JP1847**, object **45434**, **xilografia su carta 25,7 × 37,9 cm**.
- Fonte ufficiale https://www.metmuseum.org/art/collection/search/45434
- Imagen originale Met Open Access CC0/public domain: https://images.metmuseum.org/CRDImages/as/original/DP130155.jpg
- SHA256 originale verificato da download effettivo nel GitHub Action del 30/10: `cbb9988f2f18b9180a1cc0cf5dbb0e3bbf8f2e85d17930cf6ca9ab36fac36303`, pixel 3859×2594. **Identico** alla fonte di Cinema Standard/Museum V55 precedenti. Nessuna confusione tra esemplari diversi.
- Critico Museum V76 visita una **sala interamente RICOSTRUITA digitalmente**, con montaggio conservativo contemporaneo INESISTENTE nell'originale; **NON è un'immagine del Met né una riproduzione di una cornice storica**. Fonte del background originale del progetto: immagine generata di sala neutra; tutti i pixel della stampa a ogni zoom da Met JP1847, non inventati. Sala senza persone, ingresso/uscita sulla stessa stanza, camera continua. V80: fonte e proporzioni devono essere esplicite, non può essere Gold Master senza revisione umana.

## Voce originale Critico

- Copione consolidato `modules/artvision_critico/production_series/hokusai_grande_onda.json`: **11 capitoli**, **565 parole**, 52 frasi.
- Un solo autentico WAV Google Gemini 3.8 Flash TTS **Gacrux**, 24kHz mono, durata **231,04s**, SHA256 `9ddb4843356843d84994b12b3db05c47119311f9cb42626aff1acf59ff03f913`. Una sola chiamata API Google; costo effettivo **non verificato**; nessuna generazione video IA a pagamento.
- Metodo allineamento `asr_with_interpolation` (Whisper), corrispondenza `0.8747855917667239` cioè 87,48% parole, richiede QA umana dei passaggi intermedi.
- I due filmati Critico devono avere **la stessa traccia AAC copiandola byte-for-byte** dal singolo master mixed Gacrux, con musica Water Lily CC BY4, audio non rigenerato per Museum.
- Registrazione musicale originale Water Lily / Kevin MacLeod, SHA256 `b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6`, https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035 , https://creativecommons.org/licenses/by/4.0/ .

## Quattro slot esatti, nessuna duplicazione

1. **Critico Standard**: nuova regia dettagli autentici, voice Gacrux allineata 52 frasi, filmato 232,7 secondi, 720×1280 H264/AAC. Basato sulle regole Bosch/Ofelia e Socrate/Klimt, copertina standard. Storico master preservato e MP4 Android H264 ricompresso senza cambiare audio.
2. **Critico Museum**: STESSO IDENTICO audio, filmato 232,7 sec, visita ingresso/uscita camera V57 e la stampa su scala corretta. Primo test V74/v75 scartato per una didascalia ingrandita e movimenti di camera troppo veloci; V76 corregge entrambe le criticità, scena/QA da verificare prima di dichiarare successo.
3. **Cinema Standard**: riutilizzo ORIGINALE V55 dallo storico workflow artifact `12882622228`, SHA256 `f253f21ea327e17a16ac453a18059f8e468c98f3b7e468574d5ced630fcc8689`, 31,25 sec, 1080×1920, H264/AAC, licenze già verificate. È un vero MP4 precedente, non un filmato nuovo contato due volte.
4. **Cinema Museum**: riutilizzo ORIGINALE V55C dall'artifact `12884916219`, SHA256 `92d017fc9b65b63799d161a33e9e9902cfb1e20c7fbbf6ba878b1d54035a6547`, 42,71 sec, 1080×1920, H264/AAC. Ricostruzione contemporanea dichiarata e non sala Met, non Gold Master V80.

**V25**: tutti i video restano **rendered_needs_review**, mai auto-approvati. Archive Dropbox/sito privato non verificato finché non viene effettuato un caricamento autorizzato effettivo e un download di controllo. Nessuna pubblicazione social automatica.

## Memoria/regole e prossima opera

- Non ripetere il formato dei due Critico con voci differenti.
- Non rimpiazzare materiali originali Met con differenti esemplari della stampa.
- Non trasformare il piccolo foglio di carta in una grande tela di museo: rispetto misure.
- Non considerare una cornice creativa come se fosse presente nell'allestimento reale.
- Non duplicare i 2 slot Cinema esistenti al solo scopo di creare contenuti nuovi.
- Non riprodurre una camera Museum che insegua ogni frase troppo velocemente: percorsi per blocchi narrativi e revisioni V57 prima di consegna.
- Non dare per avvenuto l'archivio privato né dichiarare completata la revisione umana a velocità normale.

**Owner**: automazione ArtVision unica ID `6adca191603c8191a90d5190901cd034`. Nuovi futuri soggetti solo secondo protocollo editoriale V32 e un lavoro alla volta. Nuove specifiche utente prevalgono sui vecchi blocchi ma non aboliscono QA e permessi finanziari.
