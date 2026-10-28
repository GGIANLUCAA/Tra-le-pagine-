# V56 — LA STORIA RIVIVE | Contratto permanente del format archivistico
**Data:** 28 ottobre 2026. **Richiesta:** creare una categoria autonoma, riconoscibile e di alta qualità da filmati d'archivio autentici; evitare discussioni ripetute, spese ingiustificate e false consegne.

## Gerarchia
Richiesta specifica > `docs/REGOLE_ATTIVE.md` e `config/editorial_rules.json` > questo contratto V56 > scheda episodio > guide storiche. **V55 vale per OGNI nuovo MP4, V28 per i 4 post social, V33 per le fonti, V25 per rilascio e divieto autopubblicazione; V38 vieta lo stampino.** V54 4x1 e V46 Museum sono SOLO ArtVision, non si applicano qui. Non cambiare altri format/master/automazioni.

## Identità e standard
- Chiave: `storia_rivive`. Label `LA STORIA RIVIVE | Filmati autentici restaurati`; categoria autonoma nell'archivio privato, non un ArtVision/Critico rinominato.
- Promessa: «Guardare per alcuni secondi la vera vita di un'altra epoca». Priorità alla qualità del **film originale**, non alla spettacolarità artificiale.
- Durata tipica 12–25 secondi, estendibile solo per storia; vertical 9:16 H264/AAC per social, master di archivio separato quando disponibile; no «4K originale» se è upscale da 480/576p. 24/25/30 fps di output solo se conversione corretta: non spacciare frame duplicati o interpolati per frequenza originale.
- **Variante 1** gratuita/autentica: bianco e nero → viraggio monocromatico caldo, esplicitamente `sepia_tint`, NON «restauro a colori». **Variante 2** `ai_colorized`: video della stessa ripresa con vera colorizzazione AI controllata nel tempo. Mai cambiare le persone, mimica, oggetti, edifici o il movimento con un generatore per chiamarla ripresa autentica. Eventuali ricostruzioni generative sono un prodotto separato, con avviso inequivocabile e nuove approvazioni.

## 1. Scelta autonoma e ricerca pubblico (pre-produzione, costo zero)
1. Cercare almeno 3 candidati quando non è imposto un tema; privilegiare vita quotidiana, mestieri, trasporti, infanzia, città perdute, trasformazioni urbane e gesti umani. Confrontare importanza umana, qualità visiva/aggancio, originalità, documentazione, licenza e adattabilità 9:16. I numeri sono selezione editoriale, NON visualizzazioni previste.
2. Catalogare data/luogo/fonte/autore/istituzione, segnare precisione `exact|approximate|unknown`. Non dedurre data/luogo dalla sola descrizione generata automaticamente. Filtrare incoerenze tra titolo e scena.
3. Ricercare prima i materiali già approvati; poi raccolte con diritti chiari (es. Musée Albert-Kahn su Wikimedia Commons, per singolo file), altre biblioteche ufficiali. YouTube/Facebook/TikTok **non** sono una licenza. Non usare watermark, filmati rubati o riprese moderne presentate come antiche.
4. Esaminare l'ORIGINALE completo o almeno i frammenti candidati: scegliere un atto visibile e intrigante, non una scena genericamente vecchia. Dossier con timecode start/end e descrizione esatta di ciò che si vede; non inventare dettagli.
5. Controllo diritti per singolo file: pagina fonte stabile, URL master, autore/istituto, licenza testuale, URL licenza, data di verifica, restrizioni territoriali/diritti connessi/ritratti/musica se applicabili; annotare hash del master scaricato. `CC0` consente il riuso alle condizioni dichiarate, ma non elimina tutte le altre responsabilità. `public domain` senza valutazione del Paese di origine e d'uso NON basta per approvazione automatica. Se dubbio `rights_blocked`.

## 2. Storyboard e primi 7 secondi — BLOCCANTE
- Aprire **sul dettaglio più espressivo che appartiene davvero al filmato**, non con logo, quadro nero o spiegazione. Primo frame: data/luogo corti e leggibili su mobile; formula di esempio «BEIRUT · 1919» SOLO se documentata. Mai claim generici «non crederai ai tuoi occhi».
- 0–3 s: fermare lo scroll con azione umana vera e soggetto leggibile. 3–7 s: prima rivelazione o inizio transizione B/N → colore; non imporre la stessa durata/effetto a ogni clip. Dopo 7 s: scena e finale motivati, loop naturale quando adatto.
- Se il filmato 4:3 è largo, non ritagliarlo ciecamente: **priorità mani, volti, soggetti, movimento**. Usare composizione 9:16 con fotogramma intero e cornice/letterbox elegante, oppure crop dinamico ispezionato (safe area per UI social). Niente facce/manine/animali tagliati, sfocatura finta riempitiva o zoom aggressive. Confrontare almeno frame reali 0.1/1/3/5/7 s e punti intermedi; testare playback sul telefono.
- Titolo copertina = luogo, anno ed eventuale microtema documentato, grafica di serie riconoscibile ma non copiatura delle cover libri/ArtVision. Copertina JPEG dedicata estratta da **frame vero dello stesso MP4**, con possibile tipografia aggiuntiva. No poster AI spacciato per frame archivistico. Verificare leggibilità 9:16 e miniatura.

## 3. Restauro fedele
- Conservare sempre sorgente originale e una versione B/N. Preparare deinterlacciamento solo quando serve, rimozione polvere/stabilizzazione **moderata**, protezione del moto e della grana storica; evitare plastificazione, HDR finto, sharpening aggressivo, color grading Hollywood.
- Colorizzazione: usare un modello gratuito/localmente disponibile se legalmente e tecnicamente consentito; **DDColor è per fotogrammi** e può creare flicker temporale. Il passaggio frame-by-frame non passa il gate finché non è revisionato il movimento reale e la stabilità di volti/vestiti/oggetti. Evitare shift/ghosting, arti aggiunti, colori che saltano, movimento rallentato/accelerato senza nota.
- Dissolvenza B/N → colorizzato soltanto se sono **i medesimi fotogrammi sincronizzati** (tolleranza manuale: nessuna doppia sagoma in azioni/volti). Niente cambio sorgente mascherato da restauro. Colori sempre «ricostruzione interpretativa».
- Il titolo di una data e/o evento sensibile richiede verifica con fonte primaria; non rappresentare 1919 come 1945, né una scena con soldati come «solo civili». Niente storia alternativa non dichiarata.

## 4. Audio
- Nessun obbligo di voce: default **musica strumentale discreta licenziata**, quando disponibile; assenza di audio se non è disponibile una traccia con diritti idonei. Se la storia merita voce, può essere una variante distinta con testo controllato e Google Gacrux secondo il format, non frase obbligatoria.
- Musica d'epoca o «canzone anni 40» non equivale a public domain: composizione, registrazione, interprete e master hanno diritti separati. Niente imitazioni ingannevoli di veri cantanti, niente canzoni protette. «Suono ricostruito» dichiarato se si inventano foley/ambienze; mai etichettare come suono del film originale.
- Testare volume, fade, assenza di click, sincronizzazione e codec AAC; audio silenzioso non dichiarato come voce reale. Niente musica che sovrasti volti/parole.

## 5. Crediti, API, costo e privacy — BLOCCANTI
- **Budget predefinito 0 € e 0 crediti Vidu.** La presenza di VIDU/VIDUOK in GitHub Secrets NON autorizza una singola chiamata. Proibiti batch, retry automatici a pagamento e fallbacks che spendono in autonomia.
- Qualsiasi uso a pagamento richiede scelta esplicita per **quella singola clip**, stima costo/crediti prima, scopo verificato, approvazione specifica e limite massimo; esito fallito NON autorizza un nuovo tentativo. API key mai nei log, file, post o ZIP.
- Prima di ogni elaborazione: `dry_run` o verifica dei materiali a costo zero; selezione clip, licenza, crop e storyboard approvati editorialmente dal processo, senza chiedere all'utente di ridire preferenze già definite. Evitare di scaricare 100 file: Wikimedia API usa User-Agent identificabile, caching, poche richieste e rispetto 429/Retry-After.
- L'assenza di GPU gratuita o l'impossibilità di scaricare un video è blocco reale `colorization_pending`/`source_download_blocked`, mai motivazione per spendere Vidu in automatico.

## 6. Social V28 e archivio V55 — OGNI MP4
- Quattro post **diversi e originali** `POST_FACEBOOK.txt`, `POST_INSTAGRAM.txt`, `POST_TIKTOK.txt`, `POST_YOUTUBE.txt`. Parlarne come storia vera, indicare fatti tracciati, emozione e contesto; niente statistiche inventate, clickbait ingannevole, copione fotocopia, hashtag spam o descrizione tecnica interna. Ogni testo va conservato con il video; note di produzione separate dal copy.
- Etichetta pubblica quando applicabile: «Filmato d'archivio autentico; immagini restaurate/colori ricostruiti digitalmente». Nei metadati distinguere originalità del master da elaborazioni. Credito archivio/autore e link origine anche quando CC0 (buona prassi); rispettare attribuzione obbligatoria se diversa.
- Kit completo per video: `VIDEO.mp4` H264/AAC, `COVER.jpg`, quattro POST, `FONTI_DIRITTI.json`, `RICETTA.json`, `QA.json` con timestamp campionati e hash SHA256, `STATUS.json` e `ZIP_COMPLETO.zip` integro (CRC). Salvataggio master originale non deve appesantire lo ZIP distribuito salvo esigenza reale; conservare URL/hash sorgente in dossier.
- ChatGPT Android: link **solo a file davvero presenti nella sessione** MP4+ZIP e fallback ZIP MP4-only se problema «library file not found». GitHub Actions artifacts sono temporanei, NON link Android permanenti. Su Video Library Studio: stesso video e cover/post/ZIP nel dossier, verificare davvero catalogo, playback, cover, 4 post e ZIP; tentativo di import solo mediante percorsi autorizzati, stato `archive_sync_pending` se manca prova. **Nessuna pubblicazione social senza conferma esplicita.**
- Scheda privata comprende titolo, luogo/anno, cosa è documentato, fonte originale, licenza e autore, riprese/timecode, asset/hash, musica e licenza, modello/colorizzazione, crop, post, ricetta, qualità, data produzione, stato distribuzione e limiti. NON far apparire `ready` una bozza automatica.

## 7. Quality gates e stati verificabili
`discovered → rights_checked → shot_reviewed → storyboard_approved → free_rendered → colorized_pending|rendered → technical_qa → artistic_qa → package_verified → chatgpt_links_verified|archive_sync_pending → archive_verified → delivery_ready`.
- `technical_qa`: ffprobe H264/AAC, aspect ratio verticale, no corruzione/decodifica fallita, audio ove previsto, durata reale, CRC ZIP, hash e source URL.
- `artistic_qa`: visionare/ascoltare MP4 intero; revisione del crop e 0/1/3/5/7s, stacco/continuità B/N→colore, focus umano, flicker, artefatti, aderenza dei titoli al reale, finale, cover e musica. Registrare 2–3 difetti **con timecode reale** e correggere prima della consegna; se non visionato = `rendered_needs_review`. Non dichiarare automaticamente «virale» o Gold Master.
- Se manca anche uno dei componenti V55, stato `delivery_incomplete`, con componente nominato; la completezza del pacchetto non è la pubblicazione né l'importazione remota.
- Dati post-pubblicazione (se disponibili) da confrontare: retention primi 3s, durata media, completamento, condivisioni/salvataggi, commenti. Sono osservazioni, mai promesse.

## 8. Pilot e rollout prudente
**Pilot proposto:** `BEIRUT 1919 — LA VITA IN STRADA`, film `Scènes de rue - AI13347.webm`, Lucien Le Saint/Musée Albert-Kahn; fonte https://commons.wikimedia.org/wiki/File:Sc%C3%A8nes_de_rue_-_AI13347.webm; CC0 indicata sulla scheda Commons alla data 28/10/2026. Il contenuto di una singola inquadratura e il punto start/end **sono ancora da controllare sul film originale**: non inventarli. Iniziare con estratto gratuito e **solo quando** pronta colorizzazione coerente produrre la versione a colori; non etichettare la prova virata come AI.
**Ordine dei lavori:** 1) integrare fonte/renderer offline; 2) ottenere MP4 autentico visibile e verificarlo; 3) colorizzazione multiframe e anti-flicker dopo test; 4) copertina e 4 post verificati; 5) ZIP e download Android; 6) import+verifica Video Library Studio; 7) solo allora abilitare lotti nuovi. **Mai sacrificare i gate in cambio di quantità.**
