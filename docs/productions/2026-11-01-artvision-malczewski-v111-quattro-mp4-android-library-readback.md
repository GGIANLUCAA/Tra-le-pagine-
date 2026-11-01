# ArtVision V111 — Jacek Malczewski, Błędne koło (1895–1897): 4 MP4 REALI + Libreria readback
Data 2026-11-01 · **REVIEW NON Gold V25** · settima opera esplicitamente autorizzata dal proprietario.

## Identità e diritti
- Opera esatta: Jacek Malczewski, *Błędne koło / Il circolo vizioso*, Museo Nazionale di Poznań, **MNP FR 56**, olio su tela **174×240 cm**. Fonte istituzionale https://mnp.art.pl/en/project/bledne-kolo-2 .
- Riproduzione PD esatta Wikimedia https://commons.wikimedia.org/wiki/File:Bledne_kolo.jpg ; **5026×3557 pixel**, SHA1 **94a56db15afd68bad5d1322e8b13a7d8970335e3** e SHA256 **0ff83e09be9465a696b8956065f93ddd78f9fb3c1f1e8ebd87b98bc792cad5b9**. Il renderer ha verificato la SHA1 PRIMA di ogni generazione.
- Museum: **sala e cornice ricostruite digitalmente**, NON vera sala di Poznań e NON cornice storica documentata. I dettagli centrali sono derivati da pixel dell'opera, senza generare personaggi.
- Musica originale strumentale sintetizzata offline dal renderer, non registrazione di terzi.

## Workflow realmente eseguiti
- **V110** GitHub Actions SUCCESS https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41260215643 ; artifact reale **13064523700**, **677.283.117 B** (supera il limite di trasferimento diretto 512MB del connettore; NON rigenerare nessuno dei 4 master).
- 4 originali V110: Cinema Standard 47s SHA **906c456a01add38556ae6798a26cf128c195ab91b6415a41ef6ad40287942732**; Cinema Museum 52s SHA **4693214a38b8594d146b34c20012d776708bc00a52d43771e6aa2bc1848f0990**; Critico Standard 89,08s SHA **a54148eb6c56679e16395af661bd319bd86bf97164b66c5106bfef2e5bb2a2b7**; Critico Museum 89,08s SHA **43300566a571ca2635dcbf0175b14df535e0d4e7292e82d284aacf0536c61025**. Tutti H264/AAC 720x1280 20fps, full decode PASS.
- Unica voce naturale **Google Gacrux** per i due Critico, 78,52s WAV SHA **18fe7ae45e1fcc403014dc105be1a2f2c1fc1b2a087818e24b17c262568d2f21**, ASR matched_fraction **0,9096045197740112**; ascolto umano e sincro esatta pendenti. Contesto economico: sola seconda chiave dell'account Free/no-billing **dichiarato dal proprietario**, fattura indipendente non verificata. **NO RIGENERARE VOCE.**
- **V111** recovery-only GitHub Actions SUCCESS https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41260460701 ; recuperato artifact V110 mediante GH_TOKEN read-only, riconosciuti 4 hash originali, **zero TTS e zero API AI**. Ricodificata SOLO la componente video x264 CRF24 per consegna Android, **AAC stream copy** identico nei due Critico, ADTS SHA **414df92a01acc866cd17d31435940d8b2f9aac80b618f890cd2f65274913728f**. Nuovo artifact **13065162413**, circa 91MB, materializzato e ZIP CRC PASS.

## Quattro MP4 V111 DAVVERO scaricati e ricontrollati localmente e dalla Libreria
| Slot | Filename | Byte | SHA256 | Decoder/readback |
|---|---|---:|---|---|
| Critico Standard | MALCZEWSKI_CRITICO_STANDARD_V111_ANDROID_REVIEW.mp4 | 9.292.892 | be5fca2d01fdb7e8584ebf1319a16f35b04420412d0ea9de6a38114bc997412b | PASS |
| Critico Museum | MALCZEWSKI_CRITICO_MUSEUM_V111_ANDROID_REVIEW.mp4 | 9.252.608 | 53350cef4614ab5a30f9db0dc796fcda0a3825e30cc612b235a3ed52eee5c7b2 | PASS |
| Cinema Standard | MALCZEWSKI_CINEMA_STANDARD_V111_ANDROID_REVIEW.mp4 | 5.456.682 | c7543e9515b4c60c21a484232a571476fed265cd9e5c735b70d0b66ce034107a | PASS |
| Cinema Museum | MALCZEWSKI_CINEMA_MUSEUM_V111_ANDROID_REVIEW.mp4 | 6.047.307 | 87dbe26bb8a7a1b9fc89719a540240835715ed54bccf239636f25655ba3002b9 | PASS |

**Libreria privata:** `/ArtVision/Malczewski/V111_QUATTRO_VIDEO_REVIEW/`. 4 MP4 singoli + 2 ZIP + 4 cover + 16 post social BOZZA + QA/align/voice state + README + foglio provini JPG. **Upload effettivo e materializzazione di ritorno dei 4 MP4 e di 2 ZIP, SHA256 identici**. Decodifica FFmpeg full -xerror dei quattro MP4 RISCaricati PASS.
- Android ZIP `MALCZEWSKI_4_VIDEO_ANDROID_V111.zip`, **29.986.872 B** SHA **4bcf4adf1f0f7323f9932cc4a052f05ffa58d9472aa9c743c30fb7c06721db1f** CRC PASS + readback identical.
- Completo ZIP `MALCZEWSKI_4X1_COMPLETO_V111.zip`, **30.617.733 B** SHA **07a3de798f6178a8b9504fd88b4f7a7b708f0826604b7bb761bfe4c05d5a44f7** CRC PASS + readback identical.

## Requisiti di qualità e divieti
- Verifica immagini: 24 fotogrammi estratti da 4 file MP4 realmente decodificati; fonte autentica, Museum digitale esplicitato. Revisione artistica integrale ascolto/visione ancora pendente.
- **0 Gold V25** finché utente non approva; test R2/site/Android playback **NON verificato** dalla sola verifica decoder/Library.
- Tutti i 24 video slot delle sei opere precedenti (Socrate/Klimt/Hokusai/Bosch/Wright/Böcklin) e master V110 inalterati. La compressione V111 è revisione tecnica degli stessi 4 slot, NON otto video.
- **NO nuovo TTS, NO rerun V110/V111, NO altri quadri automatici, NO social pubblicato, NO nuova automazione periodica, NO acquisti.**
