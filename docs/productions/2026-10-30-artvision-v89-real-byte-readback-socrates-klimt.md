# ArtVision V89 — verifica fisica dei piloti, 30 ottobre 2026

## Socrate — byte recuperati e backup verificato
Recuperato dalla Libreria privata il vero `ARTVISION_SOCRATES_4X1_COMPLETO_PILOTA_V67.zip` (117.280.478 byte; SHA256 `bd075b4f39600eea64712970e812a2ca967128326f27674a79d3cc7da40ed462`). ZIP 87 membri, CRC PASS, quattro MP4, quattro copertine, 16 post. SHA e byte dei quattro MP4 confrontati con i manifest:

| Variante | SHA256 verificato | Byte | Durata |
|---|---|---:|---:|
| Critico Standard V67 | `f68592a8d65d5d774494f49892a4b8be8f9bbe7842ab19631f85046f0adf19c3` | 15.575.097 | 168,167s |
| Critico Museum V67 | `c3be9d91b2967df4e484918b6d678b141111130eea991b63493d15b843c090a9` | 53.582.121 | 168,167s |
| Cinema Standard V59 (revisione dello slot V55) | `0f946f74397c780c9357f545d0a9712926bf02eb3f43ba4866eba7cda8828540` | 17.855.540 | 35,042s |
| Cinema Museum V61 | `6ae8a2cb1ad3709bea4bab801ddefdaf8e7a00b3f3f65f50ddd81af8e4414afc` | 22.854.775 | 38s |

Tutti e quattro H264/AAC con `ffprobe` e **decodifica integrale FFmpeg video+audio PASS**. I due Critico hanno lo **stesso AAC estratto bit-identico**: SHA256 ADTS `3f1374c08615822bd8c2fd41597d98dbcc2335ca3235543e5e978d9feee44669`.

Recuperato il vero WAV Gacrux dall'artifact già conservato nella Libreria: `VOCE.wav`, 8.000.684 byte, 166,680s, SHA256 `b26b6826380c8dcc9b27a590bb6ecd43dd12107dafd367e429ad43351bd8a476`. Zero nuove chiamate TTS.

**Backup privato reale** in Libreria: `/ArtVision/Socrate/V89_recupero_originali/ARTVISION_SOCRATES_4X1_COMPLETO_PILOTA_V67_BACKUP.zip` (file_id `file_00000000c47c81f4a9065f617327d4f7`, library_file_id `libfile_4e8ed3559f6c8191ad88b2c47b2db807`). Il backup è stato materializzato nuovamente, SHA256 confrontato byte-per-byte tramite hash e ZIP CRC verificato: identico a `bd075b...ed462`. **Non** implica playback Android o import nel sito privato.

**QA registica osservata:** fotogrammi campionati ai 10 beat narrativi mostrano grossolana coerenza tra dettagli e parole (mani/coppa, giovane in rosso, discepoli, Platone, catene). **Difetto concreto Critico Museum al secondo 111:** mentre la voce descrive le catene, il bordo dorato inferiore della cornice è ancora visibile per una parte consistente dell'immagine; contrasta con V89 (cornice solo ingresso e ritorno). Serve revisione NON distruttiva della stessa variante, QA sull'intera camera e feedback artistico. Campionamento visivo non equivale a visione/ascolto umano integrale. Gold V25 = 0.

## Klimt — controllo parziale, non end-to-end
Dropbox conferma metadata ZIP `/ARTVISION_KLIMT_4X1_PACCHETTO_COMPLETO.zip` 65.968.295 byte e quattro MP4 nella cartella estratta, con dimensioni coerenti con la coda: 17.136.945 / 13.583.486 / 3.774.837 / 4.343.198 byte. **Non è un hash di download di ritorno**.

Recuperati fisicamente dalla Libreria e decodificati interamente due MP4: Critico Museum SHA `814e52f6d4281df14d3064bce6f1295ab6cdc059a5d5c80acf7db0a095cbf1ab`, Cinema Museum SHA `9dc3cf7abcebc3e8b16d105e9e9934cde8775cec1ac6b684519fe0df1875e746`. Il tentativo di materializzare il pacchetto Dropbox e Cinema Standard ha fallito con `Dropbox file materialize failed`: hash remoto e due MP4 restanti non ricontrollati fisicamente. Nessun claim di backup Dropbox verificato o playback.

## Decisione
Socrate 4/4 render preesistenti, QA tecnica byte PASS, backup Libreria con readback SHA PASS, regia Museum da correggere; Klimt 4/4 render preesistenti, QA fisica in questo ciclo 2/4 e blocco recupero Dropbox. Gold V25 zero, sito e playback Android non verificati. Non sbloccare la serie; non rifare i render esistenti; non pubblicare né consumare crediti.
