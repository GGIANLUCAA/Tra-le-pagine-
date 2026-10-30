# ArtVision Wright V85 — Quinta opera, quattro MP4 autentici, 30/10/2026

## Autorizzazione e identificazione
L'utente ha chiesto «Ok procedi con un'altra serie di 4» dopo Socrate, Klimt, Hokusai e Bosch. Questa istruzione autorizza il quinto quadro ArtVision 4×1: Joseph Wright of Derby, **An Experiment on a Bird in the Air Pump** (1768), National Gallery **NG725**. L'olio su tela è **183×244 cm**. La National Gallery lo indica prestato per la mostra Wright "From the Shadows" a Derby Museums dal 12 giugno al 1 novembre 2026; **non dichiarare che il film mostra l'attuale allestimento Londra**. Fonte: https://www.nationalgallery.org.uk/paintings/joseph-wright-of-derby-an-experiment-on-a-bird-in-the-air-pump .

## Identità di quattro slot e output realmente verificati

| Slot | MP4 originale | Durata | Byte | SHA256 |
| --- | --- | ---: | ---: | --- |
| 1 Critico Standard Gacrux | `01_Wright_Critico_Standard_Gacrux_V85.mp4` | 216,5s | 11.744.210 | `0d3a171f5a760463e66f16d6eaab50eac7c44fb72115dc2a734fe822be6b8323` |
| 2 Critico Museum Gacrux | `02_Wright_Critico_Museum_Gacrux_V85.mp4` | 216,5s | 11.387.470 | `462f0afd6643a023110f48ce287cfada56d15293d375ac905098e6778f9cb94c` |
| 3 Cinema Standard musica | `03_Wright_Cinema_Standard_V52B.mp4` | 55,9s | 6.690.474 | `ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2` |
| 4 Cinema Museum musica | `04_Wright_Cinema_Museum_V85.mp4` | 52s | 5.299.687 | `ae5af74ed0a35e1d6ebfe31081b543b2778ce5b1a1c7b88dcfe712f516192a99` |

Cinema Standard V52B è il **master storico recuperato byte-per-byte** dall'artifact GitHub Actions `12798647211` nel run `40649283319` e ZIP verificato; **non rigenerato**. Cinema Museum V85 è un **nuovo montaggio differente**. Precedente Cinema Museum V55 SHA `5352f3f49546b97d70c58478120a71855727a3c4b3a25db4bbb071acbb7d04b3` è mantenuto come versione dello **STESSO SLOT**, non quinto filmato. I due Critico V85 sono nuovi.

## Voce autentica condivisa (non imitazione)

- Copione originale professionale 486 parole, **10 beat semantici**, `modules/artvision_critico/production_series/wright_air_pump_v85.json`; SHA del solo copione `133de71cf67a6cf280fd2bfc41ab32e7038269d9d0f6a32fa5e3659f0e5350f9`.
- Una sola vera chiamata a **Google Gemini 3.8 Flash TTS, voce Gacrux** nel run GitHub `41030305113`, artifact originale WAV `12966285611`.
- WAV mono 24 kHz 215,0 secondi SHA256 `d31a0bb8ea3a53af4c45d88db3e7d3e3e9a478115618fb73c8ad99e5268885ef`; allineamento offline ASR `asr_with_interpolation`: **39 frasi, 91,8327% parole abbinate**, mancanti interpolati e richiedono ascolto.
- Un unico file `WRIGHT_CRITICO_SHARED_AUDIO_AAC.m4a` mixato una volta con musica, SHA `2a79a9ea9b1dfd54f2ac5bbd4aad6fce912f176e22d66ba2e63a39072a2282bd`. La traccia AAC estratta dai **due** MP4 Critico è **identica bit-per-bit** in entrambe, SHA ADTS `f7d399e2e7fb2b08e3dbcfa8daff9f313bf32c902472dd9e10deb45f4c54d5c4`.
- Il workflow `.github/workflows/artvision-wright-v85-one-gacrux.yml` è stato convertito a `workflow_dispatch` **senza chiamate automatiche successive**. Il costo di una chiamata Google non è verificato, non dichiararlo gratuito. Zero API video IA a pagamento usate.

## Opera e cornice reali, stanza ricostruita con trasparenza
- Originale autenticato Commons PD-Art fedele al dipinto, `5639×4226 px`, SHA `7cd47076a35df791965ee25b9a62e343c40b5366cdbd545e192b96050b2849cb`. Fonte https://commons.wikimedia.org/wiki/File:An_Experiment_on_a_Bird_in_an_Air_Pump_by_Joseph_Wright_of_Derby,_1768.jpg .
- **Fotografia della VERA CORNICE di questa opera esatta**: fotografo **Sailko**, Wikimedia Commons **CC BY 3.0**, 2017, `4098×3270 px`, SHA `ef5c2f7bbc60984222226ba9ef392601d748e86233db970c1c58dc10b1c6964b`; artifact GitHub `12856189910` run `40780957444`. Source https://commons.wikimedia.org/wiki/File:Joseph_wright_of_derby,_esperimento_di_un_uccello_in_una_pompa_penumatica,_1768,_01.jpg . Il sito National Gallery documenta una **cornice inglese ottocentesca dorata in stile italiano seicentesco**, non una cornice inventata.
- Sala chiara, architettura e pavimento sono **un set digitale creato artisticamente**, NON una fotografia dell'allestimento National Gallery o Derby Museums. Si entra nella foto della cornice specifica, che scompare durante i dettagli; torna in chiusura. **Sempre dichiarare questa distinzione nella descrizione social**.
- Registrazione `The Descent` — Kevin MacLeod, **CC BY 4.0**, pagina ufficiale https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200094 e licenza https://creativecommons.org/licenses/by/4.0/ , SHA MP3 `f097d51700b970efffc62499473ea3a31e09aad4172e787978bc9c2a644d53a2`.
- Original artwork, music and source photo must be cited in user-facing social releases; licensing can vary territorially.

## QA tecnico reale vs giudizio artistico umano
- Tutti gli **4 MP4 H264/AAC** esistono nel container e hanno superato **FFmpeg decode -xerror** e ffprobe.
- Scene regia Critico Standard e Museum guidate dai **10 capitoli narrati**, nessuna voce differente e nessun copyright indebito.
- Gate V57 su film completo:
   - Critico Standard: 4330 frame, grayscale MAD massimo `24.149/255`, zero oltre 35;
   - Critico Museum: 4330 frame, grayscale MAD massimo `24.155/255`, zero oltre 35;
   - Cinema Museum: 1040 frame, grayscale MAD massimo `28.147/255`, zero oltre 35.
- Il gate quantitativo **non prova** che tutto sia allineato perfettamente all'orecchio: controllo a velocità reale e V25 utente restano **PENDING**.
- Le copertine sono artisticamente consistenti con preset V2, senza metadati tecnici nel video; **16 post originali** (FB/IG/TikTok/YT, 4 per slot) nel ZIP completo.

## Pacchetti realmente creati con verifica CRC
- ZIP completo **`WRIGHT_4X1_PACCHETTO_COMPLETO_V85.zip`**, **66.195.617 byte**, **46 file**, SHA256 `dc1ffd7e89e7ff169d66008fa0c05a771865dbfe5d5c30f98f75d0f9726f372e`, CRC PASS.
- ZIP Android **`WRIGHT_4_VIDEO_ANDROID_V85.zip`**, **34.480.167 byte**, 5 file (4 MP4 + README), SHA256 `ab2ff562a8d770b8915122443e9ff9be82ce3987aa014780eabe51d0a67c89c3`, CRC PASS.
- Anche **quattro ZIP individuali**, video + copertina + diritti + 4 post, CRC PASS:
   - `WRIGHT_CRITICO_STANDARD_COMPLETO_V85.zip`
   - `WRIGHT_CRITICO_MUSEUM_COMPLETO_V85.zip`
   - `WRIGHT_CINEMA_STANDARD_COMPLETO_V85.zip`
   - `WRIGHT_CINEMA_MUSEUM_COMPLETO_V85.zip`.
- Il renderer esatto Python `render_wright_four_v85.py` e packager `package_wright_v85.py` sono inclusi come codice nel ZIP completo ma **non ancora persistiti come file sorgenti su GitHub**. L'archivio GitHub contiene ricetta, fonti, hash e artefatti vocali temporanei; non garantisce la permanenza dei grossi bytes master.
- **Dropbox/site import NON verificato; nessun upload Dropbox Wright autorizzato espressamente** in questa conversazione (il consenso precedente specificava soltanto Klimt). Richiedere autorizzazione esatta per il percorso di deposito se si vuole upload.
- Social auto-publicazione: NON effettuata. Stato `rendered_needs_review` per tutti, 0/4 certificati Gold.

## Preservazione seriale
La prima serie di 5 quadri ha ora **20 varianti-slot**: Socrate, Klimt, Hokusai, Bosch e Wright. Non affermare che 20 sono tutte nuove in questo turno: standard Cinema Wright V52B e alcune altre varianti sono state riutilizzate immutate. Ogni file un checksum reale, ogni revisione uno stesso slot. Il sesto quadro resta bloccato in `config/artvision_pilot_lock_v58.json`, finché richiesta esplicita futura. Proseguire con revisione V25 e deposito privato verificato, non duplicare in modo automatico.
