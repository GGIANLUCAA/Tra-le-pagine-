# ArtVision 4×1 · Bruegel, The Fall of the Rebel Angels · V200 real Room 68 (7 novembre 2026)

## Stato dell'esecuzione

Quattro **MP4 reali, diversi e integralmente decodificati**, con i due Standard originali V144 e V153 preservati e due nuovi Museum V200. Questo è un **pacchetto tecnico in REVIEW**: il museo e la regia non sono stati approvati artisticamente dall'utente. Non è Gold V25, non autorizza la pubblicazione e **non cambia il conteggio canonico 26/40**.

- Critico Standard V144: 115,8s, 720×1280 20fps, 15.150.574 byte, SHA256 `83aad1da82a091de42aa19ca6bd532a0e2a2b21c27f4c4c34eac5e53c8799f39`.
- **Critico Museum V200:** 115,8s, 720×1280 20fps, 45.581.716 byte, SHA256 `214be6294e8e48df9814253ddd17bc58226ab61c69d10b930d1596f47e4559ac`.
- Cinema Standard V153: 48s, 720×1280 20fps, 13.079.183 byte, SHA256 `dd12618fff53b63c97cff8d1096efa221f8b15d089c4a9a1f2db0e1cba6d8662`.
- **Cinema Museum V200:** 48s, 720×1280 20fps, 20.771.089 byte, SHA256 `708076b42b7a135e5fc49ea16412e686324f809867f1ef125913e71dfc7afe19`.

The **original AAC ADTS tracks are bit-identical within each paired variant**:
- Critico V144/V200: `5675b8de172887d3c451819b91d5ce7116da46b86af985de4325e5a2ad84bb49`, original Gacrux WAV SHA256 `e50f97bf6bf272bdda3a1b8577acf492f974d5c88d2b336d35cf976c5a814ade`.
- Cinema V153/V200: `ee095d8747f3e9aba2769817ec2abedb94f9748427ae96a9c334f58ddc23b2d5`.

**FFmpeg `-xerror` full-stream audio/video decode PASS for all four; same source video masters retained; no paid calls, no new Gemini call.**

## Provenienza documentata della sala e cornice V80/V118/V119

L'immagine d'ingresso e uscita è la vera fotografia di sala 68 dei Royal Museums of Fine Arts of Belgium / Old Masters, con esattamente la tela *The Fall of the Rebel Angels*, tela 117×162 cm, accession 584. **Autore fotografia: FrDr, CC BY 4.0, attribuzione obbligatoria; fotografia adattata alla regia**. Foto originale 5.472×3.648, 7.757.151 B, SHA256 `9992ac6ee8121af95c785fbdb1450dddbf56fbc24bef7eebef61c4440e51cfce`. Fonte:
https://commons.wikimedia.org/wiki/File:Koninklijke_Musea_voor_Schone_Kunsten_van_Belgi%C3%AB_44.jpg

Il quadro puro per le scene interne è la riproduzione `Pieter_Bruegel_the_Elder_-_The_Fall_of_the_Rebel_Angels_-_Google_Art_Project.jpg` Commons, SHA256 `09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5`, 3.840×2.772. L'allestimento reale nella fotografia non implica la conferma dello **stesso allestimento nel 2026** né che la cornice sia **originale del 1562**. Crediti/diritti anche dentro ZIP di consegna.

La nuova regia usa corrispondenze SIFT/RANSAC fra sala vera, vera cornice e fonte quadro: ingresso reale per ~6s; cornice completamente fuori campo per la narrazione e i dettagli; camera inversa verso la stessa sala negli ultimi 8,5s. Nessuna finta parete digitale o cornice generica. I raccordi video e la precisione narrativa devono comunque essere valutati a velocità normale dall'utente, inclusi centro delle persone, scala e nitidezza.

## Consegna

- ZIP locale reale `ARTVISION_REBEL_ANGELS_4X1_V200_REVIEW_COMPLETO.zip`: 115.137.278 byte, SHA256 `158712f2945b27754c82cf2ef2753a6bf4b83e4708369807bcc428f93357264a`; **CRC ZIP PASS, quattro MP4 interni SHA MATCH**.
- Contenuti: 4 MP4, 4 cover coerenti, due contact sheet estratti dal video, fonte quadro, foto originale sala, Gacrux WAV, report QA, crediti e 16 testi social **non pubblicati**.
- **Problema persistente:** caricamento in ChatGPT Libreria tentato, ma tool ha risposto `container_session_expired` per tutti e 3 gli upload. La cartella `/ArtVision/Rebel_Angels_V200` esiste, **file non salvati lì**. Non dichiarare backup persistente, R2/site upload o un download tramite Libreria funzionante senza readback verificato. Il solo ZIP sandbox di conversazione è temporaneo.
- Materiali fonte V199 in workflow GitHub ramo `research/artvision-bruegel-room68-v199`, run `42318836628`, artifact `13551542958`. Le varianti V200 sono state renderizzate nel workspace corrente; **il loro codice non è ancora repository workflow riproducibile, né una GitHub Release con asset verificato**.

## Prossimi gate

1. Salvataggio duraturo (GitHub Release/R2/Library) del pacchetto esatto e readback con hash e apertura Android.
2. Review a velocità normale: credibilità della sala, passaggio fotografia→quadro, corretto taglio dei soggetti e sincronizzazione parola–immagine; Critico V144/V200 **115,8s** potenzialmente troppo lungo rispetto a V82 e va rivisto SOLO con audio comune se necessario.
3. Eventuale autorizzazione editoriale e verifica licenze territoriali; solo allora incrementare due Museum slot come pronti, senza Gold automatico.

**Nessuna spesa API, nessuna pubblicazione, nessun Gold / autoriparazione inventata.**


## CORREZIONE DEL 7 NOVEMBRE 2026 — BACKUP LIBRERIA RISOLTO
Il precedente fallimento di caricamento da `container_path` è stato **risolto** caricando gli stessi file della conversazione attraverso gli identificativi esatti `source_file_ref.file_id`. Il repository non conserva ancora i byte del V200, ma ora la **Libreria ChatGPT contiene tutti e quattro i MP4 distinti e lo ZIP** e una lettura `files.list` ha confermato le dimensioni dopo il salvataggio:

- `/ArtVision/Rebel_Angels_V200/CRITICO_STANDARD_V144.mp4`: 15.150.574 B, `libfile_0addaabb14948191ae462b3366a39559`.
- `/ArtVision/Rebel_Angels_V200/CRITICO_MUSEUM_V200_REAL_ROOM.mp4`: 45.581.716 B, `libfile_7d8f128511b081918a57f3040a1033ce`.
- `/ArtVision/Rebel_Angels_V200/CINEMA_STANDARD_V153.mp4`: 13.079.183 B, `libfile_89a0ce97ab2c8191a219a80ad1e83abe`.
- `/ArtVision/Rebel_Angels_V200/CINEMA_MUSEUM_V200_REAL_ROOM.mp4`: 20.771.089 B, `libfile_045638ae9e548191b0db0f52add927d6`.
- `/ArtVision/Rebel_Angels_V200/REBEL_ANGELS_4X1_V200_COMPLETO.zip`: 115.137.278 B, `libfile_9fca1d5643e48191a7e5e8aabe940b0e`.

**Limite QA:** confermati esistenza, persistenza, nome e dimensioni tramite Libreria dopo la copia; non ancora effettuato un secondo download della Libreria con SHA byte-per-byte, né aperti i video su Android in app. `Gold=false`, `museum_approved=false`, `site_published=false`, `slots_delivered_this_selection=2` restano invariati; il problema iniziale `container_session_expired` va trattato come **storico risolto** per questo pacchetto e non più come blocco attuale. Non duplicare V200 né ricerche della foto di Room 68: continuare con altre opere senza fonte verificata o review.
