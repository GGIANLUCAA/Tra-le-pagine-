# ArtVision Music Director V330 — venti registrazioni stabili + primo video realmente modificato

**Data:** 12 novembre 2026. **Stato:** catalogo e selezione testati, un file musicale reale verificato e applicato a un nuovo MP4 di revisione privata. Non tutti i venti file sono già scaricati o verificati. Non è stato modificato alcun master approvato.

## Richiesta editoriale
Per tutti i futuri quadri ArtVision, riutilizzare una **libreria fissa di 20 musiche**, scegliendo in primo luogo la traccia adatta alla storia e all'emozione del dipinto, **non** con rotazione meccanica. Su opere diverse evitare gli ultimi tre brani ripetuti, ma non sacrificare la coerenza espressiva. Le quattro varianti 4×1 dello stesso quadro condividono una scelta musicale, modulata per durata e mix; Critico con voce sempre dominante.

## Codice realmente aggiunto e collegamenti
- `config/artvision_music_20_v1.json`: esattamente 20 registrazioni, ID/ISRC univoci, 20 URL su pagina ufficiale del compositore, durata e atmosfera, CC BY 4.0; `recording_verified:false` iniziale per tutte, mai dichiararle già materializzate.
- `src/artvision_music_selector_v330.py`: classifica mood e tema, evita ultime tre opere diverse, permette il pin di un unico brano sulle quattro varianti, rispetta durata. `--prepare` scarica la registrazione ufficiale, controlla file/codec/durata/hash SHA-256 e salva prova della licenza; `--review-video` crea solo una copia con musica reale, preservando il video originale, con FFmpeg; `--voice-wav` richiede una voce isolata nei Critico.
- `src/creative_director_v21.py`: funzione `licensed_music_suggestions` collegata alla libreria fissa V330, restituisce tre proposte pertinenti e **non** dichiara pronto un brano solo perché catalogato.
- `.github/workflows/artvision-music-v330-check.yml`: pipeline vera con test offline, selezione per Munch, Arbo, Waterhouse e primo download ufficiale At Rest. Run: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43278371273 — **due job success**; artefatto con registrazione e prova originale #13971252910.
- Regole globali `docs/REGOLE_ATTIVE.md` e `AGENTS.md` aggiornate in testa con V330. Rimangono V20 licenze/attribuzioni, V320/V326 regia e V80/V118 Museum, no-autopublish.

## Prova reale Munch Death and the Child — V2 Music At Rest
- Dipinto **MM.M.00420**, 1899. Master di partenza V2 preesistente **4.626.630 byte**, SHA-256 `3f86aff803bbab5c4e7dad393cb113825eb9d47cc9ace919230308ee9e0a76d1`.
- Brano **At Rest**, Kevin MacLeod, ISRC **USUAN1100748**; fonte https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100748 , licenza **CC BY 4.0** https://creativecommons.org/licenses/by/4.0/ .
- MP3 originale scaricato nella run di verifica, prova file/FFprobe/SHA256; **prima registrazione reale** validata della libreria.
- Nuova copia separata: `DEATH_AND_THE_CHILD_AT_REST_NEW_MUSIC_V330_REVIEW.mp4` — **4.814.319 byte**, SHA-256 `7ab70ac33dab71d28d084c110d65dda9563e51c9529572706fb77dcdf224831c`.
- Full stream decoding MP4 H264/AAC **PASS**, bitstream video **esattamente identico** al master d'origine (solo audio sostituito), originale invariato e SHA ricontrollato **PASS**.
- Pacchetto Android `ARTVISION_MUNCH_V330_MUSICA_AT_REST_ANDROID.zip` — **4.880.049 byte**, SHA-256 `550cad6fa7e7457c334d5adb89ae6684321136571a55c216fe5622009aefd62f`; ZIP CRC/MP4 all'interno SHA **PASS**.
- Rilettura vera di MP4/ZIP dalla Libreria privata e decodifica completa indipendente **PASS**:
  `/ArtVision/Music20_V330/Munch_At_Rest_Pilot/DEATH_AND_THE_CHILD_AT_REST_V330_REVIEW.mp4` — libfile `libfile_374f7322affc8191b1b2511e2c65915f`;
  `/ArtVision/Music20_V330/Munch_At_Rest_Pilot/DEATH_AND_THE_CHILD_V330_ANDROID_PACKAGE.zip` — libfile `libfile_2856ed8ff35c81919e9ff86964933325`.
- Sono inclusi video, copertina, crediti CC BY 4.0, bozza social e QA. L'MP3 completo non è stato incluso nello ZIP del filmato, soltanto usato per il video. Non sono stati fatti nuovi acquisti o chiamate API a pagamento.

## Gate aperti — non confondere con approvazione
- **19/20** tracce non ancora verificate a livello di byte/audio nel workflow V330: catalogate e con URL/licenza documentati, da scaricare, analizzare ed ascoltare al primo reale impiego.
- Verifica uditiva umana del montaggio e appropriatezza emotiva del brano **PENDING**; nessuna metrica su viralità.
- Licenza della **fotografia** del dipinto e autorizzazione commerciale/territoriale generale dei video indipendenti da licenza CC BY musicale — **PENDING**.
- Le versioni Critico/Museum originali non sono state automaticamente convertite. La soluzione è operativa come selettore + CLI + Creative Director, **non cablata a tutti i workflow legacy**; per nuovi renderer owner invocare esplicitamente il V330 senza fingere copertura universale.

## Crediti obbligatori
> “At Rest” Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License https://creativecommons.org/licenses/by/4.0/ — edited excerpt, volume and fades.

L'autore chiarisce che si possono utilizzare le sue opere in video monetizzati a condizione di attribuzione appropriata: https://incompetech.com/music/royalty-free/faq.html . Solo l'uso musicale resta coperto dalla sua licenza, non le immagini del quadro.

## Nuove lavorazioni
1. Prima del prossimo rendering ArtVision: calcolare la scheda mood con V330, proporre tre candidate, recuperare e verificare esattamente una registrazione; conservare `MUSIC_REPORT` e prova SHA nel pacchetto.
2. Non ricomprimere immagini se serve soltanto una variante musicale; non sostituire la voce Critico e non cambiare master.
3. Fare controlli reali su ascolto, regia, ducking, rumore, durata e finale, quindi approvazione esplicita e diritti separati prima di Gold/pubblicazione.
