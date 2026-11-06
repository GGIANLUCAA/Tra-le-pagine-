# ArtVision V188 — The Triumph of Death · ripresa reale delle due Museum · 6 Nov 2026

## Contesto
Opera: Pieter Bruegel the Elder, *The Triumph of Death* (1562–63), Museo del Prado, P001393.
Decisione proprietario: produrre 4 MP4 per opera, realismo fotografico del Museum, cornice visibile soltanto in apertura e al ritorno finale; durante la spiegazione soltanto pittura e dettagli autentici. Le versioni Critico devono avere riprese coerenti con il racconto, evitando zoom ripetitivi e tempi troppo lunghi.

## File effettivamente renderizzati IN SESSIONE (non archiviati stabilmente)
Il 6/11/2026 un render Python locale ha fisicamente generato **due** nuovi MP4 Museum, preservando senza alcuna modifica gli Standard V150/V151. Decodifica ffmpeg completa PASS; copia integrale AAC ADTS bit-identica rispetto al rispettivo Standard PASS; report SHA256 PASS; pacchetto locale ZIP CRC PASS. I video sono disponibili nella sessione ChatGPT che li ha generati, ma **NON** risulta ancora backup permanente su GitHub Releases, sito/R2 o Libreria. Non considerarli reperibili in automazione per sola esistenza di questa nota.

| Slot | Sorgente/master | Durata | SHA256 | Status |
| --- | --- | --- | --- | --- |
| Cinema Standard | V150, run 41840684749, artifact 13329385552 | 48.0s | c460fe7fa72ac29425de67eec40f986add502c42ec9e4166050c7ce107804138 | Existing reviewed technical |
| Critico Standard | V151, run 41841362725, artifact 13328563107 | 129.15s | a02248ce3744c6b0c392f9093360a86c55e74abcb641f51ee935915bbdb1f397 | Existing reviewed technical |
| Cinema Museum NEW | local V188, from Cinema V150; 720×1280 20fps H264/AAC | 48.0s | 56c9cca9f47b79e2f9846bdcf6fc57ed05b615222c3a12b72b019704d55b3069 | **LOCAL ONLY · ARTISTIC REVIEW PENDING** |
| Critico Museum NEW | local V188, from Critico V151; 720×1280 20fps H264/AAC | 129.15s | d9722f3711e5594855d96a1b3c986abf86c479f9a221f663ad8777ef031f67eb | **LOCAL ONLY · ARTISTIC REVIEW PENDING** |

The new Cinema Museum is 35,637,664 bytes; Critico Museum is 85,076,297 bytes. Source originals remain untouched. Gacrux WAV was NOT synthesized again. Vidu costs = 0.

## Genuine documented frame
- **Exact photo**: https://commons.wikimedia.org/wiki/File:Pieter_Bruegel_der_Aeltere_-_Der_Triumph_des_Todes_-_mit_Rahmen.jpg
- Photo: Priscila Costa / Ministério da Cultura, 2013, **CC BY 2.0**; preserve attribution, photographic source and license https://creativecommons.org/licenses/by/2.0/.
- Verified image: 4368×2912 JPEG, 6,770,130 bytes; SHA256 `c7b99abad654ca86c1df05f51b14013cd877eb11b079fde71799636987a73517`. Exact GitHub preflight: run **42200406226**, artifact **13494221466**.
- Source public-domain artwork master 5200×3697, SHA256 `2cbaefc3961b999fc5a916db06dd96b3b95789789a795da83cc1d7947f3e1fbb`. Original from Cinema V150 artifact.
- 2013 exhibition photo does NOT establish historical 16th-century frame provenance nor today's 2026 Prado room. Vertical wallpaper extension in animation is a declared digital extrapolation of the photographed wall tones, NOT a complete genuine 2026 Prado room.

## Regia V188 della copia di prova
- Aprire con foto realistica del dipinto incorniciato alla parete; inglese uniforme; push camera 1.2→7.25 circa.
- La cornice supera il bordo del campo e sparisce perché la camera entra. Quando il dipinto riempie il campo, usare i veri pixel di origine: **mai sfumare artificialmente la cornice**.
- Nelle scene interne Cinema: conservare originale Standard V150. Nelle scene interne Critico: 9 aree del dipinto per i paragrafi V151; traiettoria continua senza cornici, con timestamp **stimati** dalla lunghezza delle frasi, NON allineamento ASR certificato.
- Uscita inversa in ~7.4 s, ritorno alla medesima foto cornice e alla parete.
- Il primo montaggio del Critico Standard dura 129.15 s: potenzialmente troppo lungo rispetto all'obiettivo V82. Non certificare gradimento né sincronizzazione scena-parola prima della review integrale umana.

## Distribuzione e qualità
- Due nuove varianti Museum tecnicamente decodificabili, ma **non promuovere** Gold, non pubblicare sui social, non sovrascrivere sul sito o in Libreria e non aggiornare ufficialmente la coda a 4/4 consegnati finché non esiste **backup persistente degli esatti MP4 con verifiche SHA e lettura completa**.
- Tentativo automatico di upload dei file locali in Libreria: **FAILED `container_session_expired`** (non equivale a file salvato).
- La sessione ChatGPT ha costruito uno ZIP locale da 172,264,582 byte contenente 4 MP4, 4 copertine, 16 bozze social, fonti, SHA e QA con test CRC superato. Come per i MP4 nuovi, non esiste attestazione backup esterno.
- Prossimo passo riproducibile: salvare sorgente del renderer V188 e generare assets dentro GitHub Actions, scaricare davvero l'artifact ed effettuare readback completo, oppure importare gli esatti file dalla sessione in un archivio utente persistente; soltanto in seguito aggiornare la coda.
- **Revisione artistica obbligatoria**: scene centrali Critico non vanno ripetute e l'audio deve descrivere il dettaglio attualmente inquadrato; effettuare controllo a velocità naturale su Android, senza dichiarare risultato Gold prima dell'approvazione.

Nessun altro format è stato modificato da questa nota. Le regole V80/V82/V118/V119 restano vigenti.
