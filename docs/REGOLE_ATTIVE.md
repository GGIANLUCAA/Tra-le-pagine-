# Regole attive — 25 ottobre 2026 (revisione 3, Audience V32 + Fonti V33)

## NUOVA REGOLA ANTI-REGRESSIONE V99 — V98 resta livello minimo (30/10/2026)
L'accettazione esplicita del filmato San Francisco 1906 V98 costituisce una **baseline concreta e preservata SHA**, non una garanzia che tutti i lavori futuri siano buoni. Il processo **prima di consegnare un nuovo 4+1 «La Storia Rivive»** deve confrontare il vero MP4 al V98 attraverso `src/storia_rivive_v99_golden_benchmark.py`: cinque sequenze diverse, 4 fotogrammi reali→4 foto Finegrain/I2I con reveal e hold naturali, 1 Vidu 5s dalla stessa fonte/frame, vero movimento dopo 1s di colorazione, nessun DDColor-only, nessun errore di SHA/fonte e MP4 H264/AAC. Tutte le scene e prove devono passare V94/V96/V99 tramite `src/storia_rivive_final_gate_v91.py`. Regole, workflow e limiti oggettivi/artistici spiegati in `docs/LA_STORIA_RIVIVE_V99_ANTI_REGRESSIONE.md`. Se bocciato: correggere e rifare QA, **non** consegnare come definitivo o ripiegare sulle vecchie pipeline. La qualità dei volti e la bellezza si giudicano osservando il video reale, non con numeri automatici. Nessuna pubblicazione senza diritti e QA.


## VINCOLO NUOVO V96 · bloccare gli errori ripetuti PRIMA del video finito (30/10/2026)
Il video utente NY `44486.mp4` contiene 4 hold fotografici di ~3–4s e una clip Vidu da sorgente diversa incollata al secondo 12, con tinta arancione discordante; la schermata Bombay `44371.jpg` mostra un restauro DDColor morbido e poco fotografico e una grande fascia del titolo che copre soggetti (~12–13% altezza). Il workflow legacy NY ha ignorato deliberatamente `NOT_THE_USER_APPROVED_EFFECT`. **Gate vincolanti già integrati**: `src/storia_rivive_final_gate_v91.py` richiama V94 + V96 per ogni nuovo preset storico 4classiche+1Vidu, `src/storia_rivive_v96_guard.py` controlla cinque sorgenti distinte, quattro foto realmente image-to-image con QA umano, una sola Vidu da *identico* fotogramma originale (film B/N in movimento + colore animato), ritmo realistico, title area <8% opaco e no occlusioni, palette coerente, diritti e audio. Il passaggio H264/AAC, saturazione, hash o ZIP NON significa 'master approvato'. **Non inviare né pubblicare come finito** un video bocciato. Foto V92/V95 DDColor-only e NY V95/V95.1 sono esempi NON approvati di qualità; non copiarne la pipeline. Auditing visivo e dettagli: `docs/LA_STORIA_RIVIVE_V96_AUDIT_ERRORI_RIPETUTI_20261030.md`. Il workflow NY V95 è congelato e non esegue più generation; nessun credito aggiuntivo speso per questa QA.


## Vidu ChatGPT condiviso — contratto V1 (30/10/2026)
**Per qualsiasi nuova chat del progetto Restauro storico** che possiede accesso al connettore GitHub, il gateway già installato è `.github/workflows/vidu-chatgpt-project-gateway.yml` con richieste file `requests/vidu/*.json` e guida completa `docs/VIDU_CHATGPT_GATEWAY_TUTTE_LE_CHAT_V1.md`. Usa la pipeline Vidu esistente e `VIDUOK`/ `VIDU_API_KEY` SOLO in GitHub Secrets, senza chiavi nei messaggi. Saldo gratuito, preventivo gratuito, singola spesa autorizzata e deduplicata, recupero gratis GET. Richiesta a pagamento solo previa verifica semantica foto↔prompt e consenso esplicito per quella clip con importo e codice di piano. Tutte le clip restano tecniche fino a QA artistico e diritti; GitHub Release pubblica solo con consenso e link Android verificato. Il gateway NON modifica da solo i 4×1 ArtVision né i 4+1 storici approvati, non lancia batch e non autorizza nuove spese per Vidu in assenza di richiesta. Il repository è condiviso, ma strumenti/permessi della singola chat devono essere effettivamente presenti.


## Audit psicovisivo Wright/Klimt e perfezionamento ritmo (30/10/2026)

Prima di nuovi montaggi, usare come **guida di studio complementare** `docs/REGIA_PSICOVISIVA_WRIGHT_KLIMT_E_STORIA_RIVIVE_2026_10_30.md`: l'audit dei quattro MP4 distingue le criticità reali dei quadri dalle ipotesi sul B/N→colore storico; ogni dettaglio mostrato deve rispettare il tempo di comprensione e la frase narrata, senza immagini ripetute. La proposta sperimentale dà normalmente più tempo al fotogramma restaurato a colori che alla fase B/N, rispettando sempre il planner/gate V70, la clip Vidu V94, la cornice autentica V80 e la precedenza V58 sui nuovi quadri. **Non sono nuovi tempi universali o autorizzazioni di render, spesa, approvazione o pubblicazione**: i confronti A/B con materiale identico devono precedere qualsiasi cambio obbligatorio al renderer.

## ArtVision V80 — cornice museale autentica, regola globale obbligatoria (30/10/2026)

**Priorità assoluta di regia nei due Museum per OGNI nuovo quadro:** leggere `docs/ARTVISION_MUSEUM_CORNICI_V80_REGOLA_GLOBALE.md` prima di generare camere, sala o cornici. Ricerca per opera precisa: museo, inventario, dimensioni reali, fotografia/documentazione della cornice esattamente associata a quel dipinto. La cornice deve essere **vera/documentata** oppure una **ricostruzione fedele, motivata da fonti e dichiarata**; mai cornici dorate inventate, decorative o ripetute per quadri diversi. Se la cornice non è documentabile, non rivendicarne l'autenticità e non approvare il master Museum.

**Regia V46/V57/V73:** vista esterna con opera e cornice proporzionate, avanzamento continuo, cornice che ESCE NATURALMENTE dal campo durante i dettagli (non svanisce per effetto digitale), e STESSA cornice che RIENTRA quando la camera torna alla sala. Nessun bordo persistente dentro il dipinto. QA obbligatorio a 6 momenti: apertura, esterno, avvicinamento, interno, ritorno, finale; audit artistico e fedeltà della fonte prima dell'approvazione V25. Vale per Critico Museum e Cinema Museum; non cambiare la regia Critico Standard, Cinema Standard, voce Gacrux, o video precedenti.

**Richiamo Wright V78/V79:** pur con quattro MP4 tecnicamente renderizzati, la cornice storica documentata della National Gallery non è presente nella sorgente usata. Il Museum resta `rendered_needs_review` e non va etichettato `Gold Master` per la sola riuscita del rendering. Riferimento tecnico centrale: `config/artvision_four_variants_presets_v68.json` (v1.2.0).

## ArtVision V68 — preset creativo Socrate approvato come BASE (29/10/2026)

Feedback utente: il primo pacchetto dello stesso quadro è **buono, migliorabile**, e in particolare Museum, cornice e spiegazione sono piaciuti. **Quattro MP4 Socrate su quattro esistono**, ma restano `rendered_needs_review` con **0 V25 Gold Master formali** e senza import privato certificato. Da ora **non rispiegare le regole da zero**: consultare `docs/ARTVISION_START_HERE_QUATTRO_VIDEO_RIPRODUCIBILE_V68.md`, `config/artvision_four_variants_presets_v68.json`, `docs/productions/2026-10-29-socrates-pilot-v68/BASELINE_CREATIVE_MANIFEST_V68.json`. Quattro video diversi, WAV Gacrux IDENTICO per i due Critico, Cinema musicali, Museum V57 continuo, no persone tagliate V61, fonti/diritti e QA veri. **Le nuove richieste modificano solo le ricette delle opere interessate** (durata, centratura, cornice dichiarata, ritmo); per aggiornare le regole PER TUTTE LE OPERE serve una nuova versione globale e relativi test. Non assumere che una cornice alternativa sia autentica. Il blocco V58 per nuovi render rimane attivo finché l'utente non autorizza il successivo pilota.


## ARTVISION — DIRETTIVA V58 PRIORITARIA (29/10/2026)

Per la serie di dipinti ArtVision è obbligatorio `docs/ARTVISION_CONTRATTO_MADRE_4X1_V58_20261029.md`: **un quadro, quattro video realmente diversi** (Critico Standard e Museum con identico audio Gacrux, Cinema Standard e Museum musicali), un unico dossier e quattro pacchetti V55. **Congelare i nuovi quadri**: prima completare e far approvare artisticamente tutti e quattro i filmati di The Death of Socrates, poi eventualmente un secondo pilota approvato dall'utente; solo successivamente e previo consenso riattivare la serie. Seguire `config/artvision_pilot_lock_v58.json`; nessun MP4 in review è finale. La presente direttiva prevale su V53 (due versioni) e sui programmi storici di nuove opere ad ogni intervallo. Restano validi V25/V46/V54/V55/V57 e i divieti di spesa/pubblicazione.


Questa revisione applica le decisioni di Gianluca sulla regia modulare.
La configurazione consultabile dal programma è `config/editorial_rules.json`.
La revisione sostituisce i vincoli generali incompatibili nelle guide storiche;
non riscrive filmati, materiali o approvazioni già esistenti.

## Ogni video deve essere completo prima della consegna — regola trasversale (29/10/2026)

**Decisione esplicita dell'utente:** «Quando mi consegni un video deve essere finito; se un video ha bisogno di testo e voce deve contenerlo». Il requisito vale per **tutti i format**, mantenendo le differenze creative previste: LIBRI/RACCONTI e Critico d'arte richiedono copione, narrazione vera Google Gemini Gacrux (salvo deroga dell'utente) e sincronizzazione scena-parola; i film Cinema/Museum Immersion concepiti musicali **non devono ricevere una voce inventata**. Dove il progetto prevede testo visibile (ad esempio titolo, autore, crediti) va incluso e verificato; dove vieta sottotitoli, non aggiungerli automaticamente.

**Gate prima di inviare un video come risultato:** non basta un file MP4 decodificabile. Verificare in concreto che durata, trama o progressione, voce se richiesta, audio/musica, testo se richiesto, immagini/gesti coerenti, copertina, diritti, QA artistico e pacchetto MP4 + ZIP/Android rispettino le regole specifiche del format V13/V33/V35/V36/V44/V55. Un video che richiede voce e ne è privo, o richiede testo e ne è privo, è **incompleto e NON consegnabile come prodotto finito**, anche se è bello o tecnicamente integro. Le anteprime e i test sono materiali di lavorazione, da fornire soltanto quando richiesti esplicitamente come tali, non come surrogato del risultato. In caso di blocchi di strumenti o quote, dichiarare il blocco e non cambiare i requisiti senza consenso. Divieti di spesa video IA a credito e pubblicazione social automatica invariati.

## La Storia Rivive V94 — volti fotografici e UNA clip Vidu obbligatoria (30/10/2026)

**Decisione permanente esplicita dell'utente, dopo il confronto dei filmati 44356, 44357, 44358, 44359 con il master Bombay 44376:** i nuovi video storici devono ricostruire **volti credibili come fotografie moderne**, soprattutto occhi, pelle, capelli ed espressioni; semplici colori DDColor/ONNX e sharpen non bastano per dichiarare un volto HD. Video social allegati sono SOLTANTO riferimenti qualitativi, non materiale riutilizzabile; scritte «144P»/«4K» non provano 4K reale (tutti i file campione verificati hanno 720×1280). Cercare migliori originali e scegliere primi piani con pixel nativi utili, due varianti vere image-to-image quando si lavora sui volti e confronto con frame prima/dopo, senza inventare identità, gesti o oggetti. Se la fonte è troppo debole, cambiare ripresa o soggetto, non falsificare la fotografia.

**Ogni NUOVO video La Storia Rivive deve includere almeno UNA sequenza Vidu effettiva di ~5s** nello stesso MP4, con movimento a colori continuativo e coerente per almeno ~3,5s dopo reveal entro ~1–1,15s. Posizione in base a regia, non fissa. Il resto delle scene conserva il formato movimento B/N originale → fermo fotogramma esatto → foto moderna. Nessun Vidu finto (zoom su foto, falsa dissolvenza, solo colore su video originale) e nessuna scena AI con altro volto, persone nuove, arti errati, mutazioni di veicoli o fondali. Il modello preferito Vidu Q2 Pro Fast, 720p, 5s, massimo 16 crediti per video, **una sola richiesta fatturabile per episodio** con saldo e costo freschi verificati, prenotazione immutabile nel ledger GitHub prima del POST, mai retry ambiguo. L'utente autorizza come preferenza ricorrente l'uso **solo dei crediti API prepagati già disponibili** entro questo tetto per nuove produzioni; **NON autorizza acquisti automatici di crediti, rinnovi o superamento dei 16 crediti**. L'off-peak a 8 va usato solo quando provider effettivamente disponibile. Se manca saldo, fonte valida, frame idoneo o Vidu fallisce, fermare episodio in review e segnalarlo; NON consegnare un filmato privo di Vidu come prodotto finito, NON rispendere per correggerlo automaticamente.

**Implementazione vincolante:** `config/storia_rivive_quality_v94.json`; `src/storia_rivive_quality_gate_v94.py` per pre-spesa e consegna, collegato al gate V91 di qualità finale. Tutti i nuovi renderer e automazioni del formato storico devono creare il dossier V94, eseguire il preflight prima della chiamata API e QA reale dopo il download. Mai aggirare il controllo cambiando il nome al formato o dichiarando approvazione umana inesistente. I vecchi film restano leggibili come storico, ma il master Bombay V92 (solo DDColor/zero Vidu) NON è un esempio del nuovo livello V94. I 4 video per quadro ArtVision sono fuori da questa regola e restano invariati.

## La Storia Rivive V83 — fonte HD e benchmark campioni SOLO qualitativo (29/10/2026)

**Nuova istruzione esplicita:** `43054.mp4`, `43055.mp4`, `43056.mp4` sono riferimento **esclusivamente per qualità fotografica delle ricostruzioni**, non per montaggio, tempi, numero scene o outro. Le misure temporali V61/V82 descrivono gli esempi, non impongono uno stampino. **PRIMA di produrre un altro video storico**, eseguire il precheck di `docs/LA_STORIA_RIVIVE_SORGENTI_HD_PRECHECK_V83.md`: confrontare almeno tre sorgenti PD/CC0 autentiche, preferire scansioni vere recenti HD/2K/4K rispetto a file compressi, controllare dimensioni e dettagli nativi dopo crop 9:16 e volti/oggetti su frame adiacenti. Restauro image-to-image fotorealistico e fedele, nessuna regressione V77, nessuna persona generata al posto di un oggetto; se fonte/motore/gate non sono pronti, bloccare il master. Confermate V59/V66/V78/V82 per diritti, semantica, qualità, V55 e nessuna spesa senza consenso. Il format storico resta SEPARATO dalle quattro varianti ArtVision.

## La Storia Rivive V66 — FERMO FOTOGRAFICO DAVVERO MODERNO, SOLO SE FEDELE (28/10/2026)

**Risposta al feedback su Parigi V65:** non bastano colori/Real-ESRGAN, occhi e dettagli umani devono sembrare una foto moderna. Prova generativa sul fotogramma della venditrice a 265 s: è più fotografica, MA ha alterato persona, postura, vestiti e scena → `REJECT_NOT_SOURCE_FAITHFUL`, non inserirla come restauro in un video storico. Obiettivo non negoziabile: due o più varianti image-to-image dal VERO frame, almeno una ad alta fedeltà, QA delle facce su frame adiacenti e della geometria/oggetti/numero persone; scegliere una candidata soltanto se resta fedele e raggiunge resa fotografica alta. Nuovo controllo `src/storia_rivive_v66_photo_guard.py`: confronto compositivo grossolano, blocco su incompatibilità, approvazione umana obbligatoria, nitidezza numerica non basta. HYPIR/DiffBIR/SUPIR possibili se licenze e GPU autorizzate; **Hugging Face Jobs GPU costa a minuto** e non va avviato automaticamente, Google Colab gratuito non garantito. V66 resta in prova, nessun HYPIR realmente eseguito o MP4 finale qualificato. Documento `docs/LA_STORIA_RIVIVE_RESTAURO_V66.md`, config `config/storia_rivive_v66.json`. V59 fonti solo PD/CC0, V55 archivio completo, niente spese né autopubblicazione.

## La Storia Rivive V64 — FOTOGRAFIA REALISTICA E FEDELE, NON FALSO RESTAURO (28/10/2026)

**Feedback esplicito dopo V63:** i ~2s FOTO FERMA devono apparire davvero come fotografie moderne nitide: volti, occhi, pelle, capelli, mani, abiti e ambienti convincenti e corrispondenti al film originale. **V63 NON approvato come master definitivo**: crop originale da film Beirut 720×576→~324×576, DDColor+Real-ESRGAN non ricreano dettagli umani sufficienti. Test con AI generativa ha prodotto volti fotorealistici ma **persone/abiti differenti**, quindi scartare come falso restauro. Priorità: nuova fonte PD/CC0 con **vera scansione HD/2K**, volti già abbastanza grandi nel frame; confronto più fotogrammi reali per estrarre dettaglio verificabile; restauro conservativo, ricostruzione image-to-image con vincoli di identità/struttura e controllo umano. **Il file bello ma infedele è REJECT**, così pure il filtro sfocato 1080p. Nessun nuovo master se non supera `src/storia_rivive_quality_policy_v64.py`: `docs/LA_STORIA_RIVIVE_FOTO_FEDELE_V64.md`; `config/storia_rivive_v64.json`. Preferire scartare scena o cambiare fonte piuttosto che inventare lineamenti. V59,V55 e nessuna spesa GPU/HF/Vidu senza autorizzazione.

## La Storia Rivive V63 — REGIA PRIMA DEL RESTAURO (28/10/2026)

Dopo V62 (18,2s): meglio 20–28 s quando serve; studiare l'intero filmato e confrontare i ritagli 9:16, fermandosi sui volti, gesti e momenti davvero importanti. Priorità al contenuto, NON a scene panoramiche riempitive. Fotografia dal ritaglio originale prima di Real-ESRGAN, NO downscale distruttivo V62, denoise leggero, DDColor, render 1080×1920, hold 1.8–2.8s secondo importanza. Il 1080p NON è 4K. Un image-to-image generativo davvero fotografico può superare il semplice ESRGAN, ma serve compute, licenze e valutazione fedeltà, non è integrato. `docs/LA_STORIA_RIVIVE_DIREZIONE_FOTOGRAFICA_V63.md`, `config/storia_rivive_v63.json`, `src/storia_rivive_director_cut_v63.py`. Provino a verifica artistica; V59, V55 e 0 crediti Vidu invariati.

## La Storia Rivive V61 — CORREZIONE PRIORITARIA: MOVIMENTO B/N → FOTO AI A COLORI FERMA (28/10/2026)

**Feedback decisivo dopo visione del V60 e studio dei tre NUOVI esempi `43054.mp4`, `43055.mp4`, `43056.mp4`:** il modello estetico NON è un filmato interamente colorizzato in movimento (V60), bensì, per OGNI scena pertinente, **video archivistico B/N in movimento** → **congelamento sul fotogramma migliore** → **trasformazione in una FOTOGRAFIA AI nuova, ricostruita ad alta qualità fotografica e a COLORI distinti** → **fotografia ferma/solo minimo microzoom** → nuova ripresa B/N. Ritmo `slow`: ~2s B/N + ~2s FOTO (43054); `fast`: ~0,9s B/N + ~0,9s FOTO (43055/43056), con transizione rapida adattata alla musica e alla scena. Qualità percepita 720p/1080p > 4K cosmetico; AI deve ricreare una **fotografia**, non fare solo DDColor su ogni frame. Una foto AI richiede fonte frame reale, modello/prompt/diritti/controllo di identità e geometria; non presentare dettagli generati come storicamente certi. V55/V59 e zero crediti senza consenso restano validi. **Contratto:** `docs/LA_STORIA_RIVIVE_FOTOGRAMMA_FOTO_AI_V61.md`. **Render montaggio:** `src/storia_rivive_photo_freeze_v61.py` (richiede foto AI già reali; il compositore NON genera immagini). **Config:** `config/storia_rivive_v61.json`. La V60 rimane una prova tecnicamente completa ma artisticamente NON corrispondente ai nuovi esempi. Non consegnare di nuovo filmati completamente colorizzati in movimento spacciandoli per questo effetto.

## La Storia Rivive V59 — SOLO video di pubblico dominio/CC0; senza monetizzazione (28/10/2026)

**Decisione utente vincolante:** per la nuova categoria usare filmati originali **esclusivamente di pubblico dominio verificato o CC0 sul singolo file**. La serie sarà pubblicata senza monetizzazione; NON chiedere prova di riuso commerciale e NON scartare strumenti AI solo per il loro limite commerciale, purché i termini ne consentano realmente l'uso e la pubblicazione non commerciale. Verificare sempre licenza del modello e dei pesi separatamente: `academic research only` non equivale a libera pubblicazione non commerciale. Per PDM/PD serve controllo giurisdizione Italia e origine; per CC0 resta il controllo di altri diritti e privacy. Audio e musica verificati separatamente. **Non monetizzare non esclude la promozione indiretta**: niente finalità promozionali preimpostate. La pubblicazione resta da autorizzare separatamente, nessuna autopubblicazione né crediti Vidu senza consenso. Documento: `docs/LA_STORIA_RIVIVE_DOMINIO_PUBBLICO_V59.md`; config `config/storia_rivive_v59.json`. V55/V57/V58 invariati per qualità, regia e consegna.

## La Storia Rivive V58 — regia multi-clip open source e priorità qualità percepita (28/10/2026)

**Richiesta esplicita:** la risoluzione nativa 4K NON interessa; contano dettaglio percepito sul telefono, colori semantici coerenti, apertura emozionante, scelta autonoma dei soggetti più interessanti e montaggio di più frammenti quando raccontano qualcosa. Prevedere un eventuale breve inserto Vidu **solo in futuro**, chiaramente marcato come ricostruzione AI e autorizzato per singola clip/credito, mai automatico.

**Fonte unica supplementare V58:** `docs/LA_STORIA_RIVIVE_OPEN_SOURCE_E_MONTAGGIO_V58.md`, configurazione `config/storia_rivive_v58.json`, 6 fonti archivistiche candidate `queue/storia_rivive_candidates_v58.json`, compositore gratuito `src/storia_rivive_montage_v58.py`. Distingue ricerca e scelta della scena, colorizzazione DDColor non ancora integrata, propagazione temporale da sviluppare, montaggio FFmpeg reale e consegna V55. Nessun falso «MP4 pronto» se manca la vera traccia colorizzata. **Allerta licenze:** HAVC codice MIT non implica licenza commerciale dei componenti ColorMNet/CMNET2 (BY-NC-SA 4.0 per original ColorMNet e uso accademico), quindi NON usare automaticamente quei pesi per video monetizzabili. Confrontare >=3 fonti quando il soggetto è libero; ritmo e numero scene determinati dal racconto; niente stampini. Conservare V56/V57 e tutte le regole di diritti, post e download.

## Correzione vincolante La Storia Rivive V57 — 28/10/2026

**Feedback esplicito dell'utente dopo visione del pilota:** viraggio seppia e dissolvenza NON somigliano ai tre esempi, che appaiono fotorealistici, ricchi di colori distinti e dettagli moderni. **Vietato consegnare come finali reference-grade semplici LUT, seppia, dissolvenze o upscale cosmetici.** La priorità assoluta per questa categoria è **restauro AI semantico con stabilità temporale, nitidezza credibile e fedeltà documentaria**, oppure ricostruzione generativa chiaramente etichettata come tale (mai falsa prova storica). 4K significa 2160×3840 effettivi, non qualità percepita; i tre MP4 di riferimento misurano tutti 720×1280. Il pilot Beirut resta bocciato come target estetico, senza chiedere di visionarlo di nuovo. Leggere `docs/LA_STORIA_RIVIVE_QUALITA_V57.md`, `config/storia_rivive_quality_v57.json` e usare `src/storia_rivive_visual_gate_v57.py` come controllo tecnico addizionale, NON sostituto della visione reale. Restano vincolanti V56 (fonti/costi/download), V55 e divieto di usare crediti senza autorizzazione.

**Correzione di qualità V91 — feedback esplicito dell'utente sul filmato Parigi 1900 (29/10/2026):** il reel da 14,33 s con quattro riprese della stessa danzatrice è **RESPINTO come modello**, pur rientrando matematicamente nei 14–35 s. **25 s resta media desiderata, non quota obbligatoria**: la fascia 14–19,99 s è ammessa come finale solo con giustificazione documentata di *micro-storia davvero compiuta*, hook e ultimo payoff approvati; NON come ripiego dopo aver scartato una scena importante. Se Vidu (o qualunque scena) fallisce fedeltà/personaggi, scartare l'inserto, poi **riprogettare il montaggio e la chiusura, cercare altre scene realmente distinte, ripassare il gate artistico**; vietato spedire la mera versione tagliata etichettata «completa». Una scena con IA che modifica identità/numero/pose è respinta anche se Vidu è costato crediti; NO retry a pagamento automatico. Le inquadrature del medesimo soggetto e fondale non sono automaticamente scene nuove: valutarne **cambi di evento, gesto, emozione e progressione**. Il renderer custom NON deve aggirare il planner e il controllo qualità. **Gate finale obbligatorio** `src/storia_rivive_final_gate_v91.py` con evidenza di review umana/video visto con audio, diritti e fonte, freeze originale, finale, differenziazione delle scene, replan dopo scarti, MP4/ZIP/cover/4 copy. Il QA tecnico (ffprobe, hash, colore, continuità) è necessario, ma NON sostituisce l'approvazione visiva. Nessun titolo di «video finito» con gate non superato.

**Integrazione vincolante V70, 29/10/2026 (ritmo psicovisivo):** ogni NUOVO video storico B/N→FOTO AI a colori deve essere valutato scena per scena **prima** del montaggio e passare il gate `src/storia_rivive_pacing_v70.py` (guida `docs/LA_STORIA_RIVIVE_RITMO_ADATTIVO_V70.md`, policy `config/storia_rivive_pacing_v70.json`). Durata 14–35 secondi; 25 s è la media desiderata su più contenuti, mai una durata imposta al singolo film. Variabilità motivata da soggetto, gesto, emozione, leggibilità e complessità; niente 3 scene/cicli uguali, niente riempitivi, primo reveal ≤1,5 s. Foto a colori ancorata al vero frame storico, non spostare il freeze per il ritmo. Fail closed se mancano osservazione originale, diritti, prove e QA. Questo modulo NON modifica Socrate/ArtVision 4×1, V59/V64/V66/V55, il divieto di spesa e autopubblicazione; è un planner e QA strutturale, **non** restauro AI né certificazione artistica.

## La Storia Rivive V56 — NUOVO FORMAT AUTONOMO (28 ottobre 2026)

**Regole richieste e approvate esplicitamente dall'utente:** nuova categoria per montare vere riprese d'archivio con passaggio B/N→colorizzazione fedele, senza stampini e senza spreco di crediti. Contratto vincolante: [LA_STORIA_RIVIVE_CONTRATTO_V56.md](LA_STORIA_RIVIVE_CONTRATTO_V56.md); policy machine-readable `config/storia_rivive_v56.json`; profilo `config/video_formats_v13.json > formats.storia_rivive`.

**Blocchi non negoziabili:** luogo/data/diritti verificati per il file esatto; niente scene generate presentate come fonti; non chiamare sepia «AI a colori»; verificare volti/crop e coerenza tra fotogrammi; copertina da frame autentico; primi 0/1/3/5/7 secondi visti e ascoltati; quattro post V28 diversi; MP4 + cover + fonti + musica/diritti + QA + ZIP completo; download ChatGPT Android e importazione/playback/dossier sul sito verificati separatamente. Budget predefinito **0 € e 0 crediti Vidu**; avere una key non autorizza a spenderla; niente social automatici. Il nuovo format non altera la regola ArtVision 4x1 e non certifica un video prima del vero render. Priorità V55 generale, V33 fonti, V25 autorizzazioni e V38 variabilità.

## ArtVision V55 — primi 7 secondi e consegna completa verificata (28/10/2026)

**Nuova richiesta esplicita dell'utente, priorità massima per OGNI video ArtVision, incluso ciascuno dei quattro video 4x1.** Un render riuscito non è una consegna completa. Prima di descrivere un film come pronto, l'agente deve preparare e verificare **l'MP4 H264/AAC verticale, la copertina JPEG dedicata nel branding approvato, quattro descrizioni social ORIGINALI e diverse per Facebook/Instagram/TikTok/YouTube, le fonti e licenze, la ricetta/QA, lo ZIP completo**. Devono esistere anche **percorsi MP4 e ZIP realmente recuperabili da ChatGPT Android** e **la scheda nel sito privato Video Library Studio** con MP4 riproducibile, copertina, post e generazione ZIP disponibili. Dossier sul solo GitHub, solo JPG o solo video in R2 NON soddisfa l'intero requisito.

**Regia 0–7 secondi bloccante in preflight:** per ognuna delle quattro varianti 4x1 compilare \`opening_0_7\` con titolo inglese esatto+artista leggibili sul primo frame, particolare AUTENTICO localizzato, composizione telefonica, rivelazione iniziale 0–3s e secondo passaggio 3–7s legati all'opera, con cue musicale o voce naturale. Non ritardare per secondi inutili la prima scoperta facendo soltanto corridoi museali generici o loghi; l'effetto Museum deve servire il quadro. Non imporre un identico numero di tagli o lo stesso tempo per ogni quadro. Confrontare una vera anteprima a 0,1/1/3/5/7 secondi con il master approvato; verificare il testo, la leggibilità della protagonista/composizione, tagli e musica/voce a velocità reale. Un fotogramma estratto **non certifica** la forza del gancio; se non si vede davvero il film, lo stato resta \`rendered_needs_review\`.

**Confezionamento verificabile:** usare \`src/artvision_delivery_v55.py pack\` sull'MP4 reale con copertina, quattro post, diritti e ricetta. Il programma esegue ffprobe, decodifica integrale, estrae campioni reali dei primi 7s, controlla i file e compone ZIP integro, senza spendere crediti. La scheda \`templates/ARTVISION_OPENING_REVIEW_V55.json\` può essere completata **solo dopo visione/ascolto effettivi** e deve corrispondere al vero SHA256 del film. Il rapporto di output distingue \`local_verified\`, \`chatgpt_mp4_link\`, \`chatgpt_zip_link\`, \`archive_video\`, \`archive_cover\`, \`archive_social\`, \`archive_zip\`; non convertirli tutti in \`verified\` per supposizione.

**Consegna ChatGPT/Android:** nella risposta mostrare link MP4 diretto e ZIP completo, facoltativamente anche la copertina, usando SOLO percorsi verificati nella sessione corrente; link sandbox verificato localmente ≠ link provato nell'app Android. Se l'MP4 dà \`library file not found\`, usare ZIP integrale o \`src/video_download_fallback_v36.py\` per lo ZIP solo MP4, più link al sito solo dopo importazione vera. Non inventare collegamenti remoti o file da una sessione precedente.

**Sito archivio subito dopo il render:** avviare senza passaggi manuali superflui il percorso di importazione privato già autorizzato (ChatGPT Library → Video Library Studio Import, oppure GitHub artifact idoneo con contratto V25 approvato → workflow R2). L'importazione **non è pubblicazione social** e non aggira i gate V25/V44. Verificare dopo l'importazione che il nuovo MP4 risulti nel catalogo, sia riproducibile, abbia copertina e che i QUATTRO testi social siano recuperabili dalla scheda, con pulsante ZIP completo funzionante; i test privati necessitano accesso autenticato e non si deducono dalla sola API pubblica. \`python src/artvision_delivery_v55.py site-check --key VIDEO.mp4\` prova SOLO catalogo/Range MP4 e presenza di riferimento cover, non il dossier privato. Se import o dati social non riescono, marcare \`archive_sync_pending\` e indicare il blocco effettivo, mantenendo il file in coda per ritentare in modo idempotente, senza affermare "già sul sito". Non sovrascrivere elementi o modifiche dell'utente.

**Precedenze:** questa V55 integra V54 4x1, V46 museo, V25/V44 release, V28 post, V36 download e \`docs/VIDEO_LIBRARY_DOSSIER_V1.md\`. Non forza la pubblicazione sociale, non autorizza crediti a pagamento, non modifica master già approvati. L'obiettivo "subito" impone tentativo nel medesimo ciclo; nessun sistema può garantire assenza di ritardi di rete, GitHub Actions o ChatGPT.

## ArtVision 4x1 — regola prioritaria approvata 28/10/2026 (V54, autocritica continua)

**Questa regola sostituisce il limite storico di DUE video per opera descritto nella V53 qui sotto, conservandone gli altri vincoli** (ricerca, qualità, voce, diritti, nessuna spesa senza consenso, no duplicati e automazione già esistente). Per OGNI nuovo quadro, creare UN DOSSIER MADRE e progettare QUATTRO video distinti: (1) Critico Standard, (2) Critico Museum Immersion, (3) Cinema Standard, (4) Cinema Museum Immersion. Due Critico condividono identico testo e voce naturale Google Gacrux, ma regie differenti; due Cinema senza voce condividono la direzione musicale, ma regie differenti. Ogni video ha quattro descrizioni social editoriali V28: **16 testi per un'opera 4x1 completa**. Non spacciare versioni incomplete per quattro video pronti.

**Vincolo operativo prima del render:** leggere `docs/ARTVISION_FOUR_VARIANTS_CONTRACT_20261028.md`. Compilare il dossier JSON attraverso `python src/video_director_v13.py four-brief --topic "Opera" --artist "Autore" --out PERCORSO/ARTVISION_4X1_PLAN.json`; compilare le fonti autentiche, le dimensioni, la mappa dei dettagli e quattro storyboard con direzione emotiva concreta. Eseguire `python src/video_director_v13.py four-check --plan PERCORSO/ARTVISION_4X1_PLAN.json`. Il check è **bloccante per i nuovi lotti seriali 4x1**, non per vecchi progetti singoli o altri format. Per un progetto singolo V13 nel lotto, impostare `serial_mode="artvision_4x1"` e `artvision_4x1_plan` sul file condiviso **nella stessa cartella oppure in quella madre del gruppo** (es. `../ARTVISION_4X1_PLAN.json`), così il preflight V13 lo verifica. Non aggiungere dichiarazioni `approved` o `passed` fittizie.

**Regia emozionale obbligatoria:** scegliere una tensione umana/visiva/historica verificabile, 1-2 emozioni significative, almeno tre dettagli distinti localizzati e attribuiti, la progressione delle rivelazioni, il significato del momento forte, l'apertura e la chiusura. Una scena richiede motivo, movimento funzionale, effetto emotivo e durata; niente "zoom a caso" o stampini. Museum = sala e cornice credibili a scala reale, ingresso e ritorno alla stessa sala con modelli Cyclops/Hiroshige. Critico = voce effettiva sincronizzata. **Il gate JSON analizza la struttura, NON certifica emozione, bellezza, diritti o qualità del MP4.**

**Autocritica documentata:** dopo la visione reale e l'ascolto di ogni MP4, registrare 2-3 difetti specifici con secondo della scena, gravità, causa ipotizzata, cambiamento misurabile e verifica; collegare l'analisi all'hash esatto del file mediante `src/artvision_learning_loop_v1.py`. Suggerire **una sola modifica importante per ciclo**, confrontarla prima/dopo e conservare preset riusciti; non promuovere automaticamente un video a Gold Master. Se non si riesce a visionare il filmato, registrare il blocco e NON inventare autocritica osservativa. La frequenza di due ore è un'opportunità di progresso e non una garanzia di quattro MP4. Nessuna spesa o pubblicazione social automatica.

La sezione V53 che segue resta storico operativo e guida di migrazione della coda preesistente; in caso di conflitto numerico o di format **prevale V54**.

## V55 — apertura decisiva e consegna sempre recuperabile (approvazione 28/10/2026)

**Regola prioritaria per OGNI NUOVO VIDEO di ogni formato**, integrativa a V28/V36/V44/V46/V54. Non confondere `render finito`, `file locale verificato`, `file ChatGPT realmente scaricabile`, `MP4 effettivamente importato sul sito`, `dossier completo` e `pubblicazione sui social`: sono sei verifiche diverse. Un video incompleto rimane `rendered_needs_review` o `delivery_pending`; non etichettarlo pronto per l'utente. Non inventare link o esiti.

**Ogni singolo video deve avere, con nome coerente e hash:**
- MP4 H264/AAC verticale reale e decodificabile integralmente, una versione Android scaricabile senza conversioni inutili;
- JPEG copertina separato, stessa identità approvata, titolo esatto del quadro in inglese e artista già nel primo fotogramma, leggibili su schermo piccolo;
- QUATTRO post social originali e differenziati `POST_FACEBOOK.txt`, `POST_INSTAGRAM.txt`, `POST_TIKTOK.txt`, `POST_YOUTUBE.txt`, con informazioni storiche corrette, crediti obbligatori e senza informazioni tecniche pubbliche;
- fonti/licenze di immagine e registrazione musicale, ricetta/scene per replica, dossier editoriale, ZIP completo verificato con CRC e hash e, per problemi Android, ZIP alternativo solo-video V36.

**I primi 7 secondi sono un gate creativo e di QA.** Progettare un primo fotogramma riconoscibile (titolo+autore), una ragione reale per fermarsi nei primi 1–3 secondi, un dettaglio/rivelazione motivata tra 3–7 secondi, ritmo e audio pertinenti, nessun nero accidentale, soggetti tagliati o testi sotto overlay social. Un ingresso Museo può iniziare con una sala magnifica ma deve creare subito curiosità: niente lenta passeggiata vuota. Non copiare sempre la stessa apertura o velocità. Estrarre e osservare sul MP4 reale i fotogrammi a circa 0, 1, 3, 5, 7 secondi e l'intero segmento riprodotto a velocità normale, con audio. Nei Critico frase/voce Gacrux e dettaglio devono combaciare. Documentare la revisione riferita al SHA256 esatto, distinguendo le osservazioni umane/agentiche dai controlli tecnici.

**Consegna verificata su ChatGPT:** materializzare il file nel runtime della conversazione, controllare percorso esatto, bytes e codec, fornire collegamento MP4 e ZIP che si riferiscono a file realmente esistenti nella sessione. Il controllo locale non prova che il collegamento si apra nell'app Android: se l'utente riferisce `Library file not found`, risolvere con ZIP o copia alternativa effettivamente disponibile, NON riproporre lo stesso link inventando una nuova destinazione.

**Archivio Video Library Studio:** avviare l'importazione nella cineteca privata non appena il filmato originale e i materiali sono disponibili, senza attendere la pubblicazione sui social. Verificare per ciascun video che il record del catalogo sia disponibile e riproducibile, la copertina associata sia quella autentica, i quattro post e la scheda siano realmente persistiti, e che il comando ZIP completo del dossier restituisca un file valido quando autenticati. La funzione sito genera gli ZIP su richiesta con link firmato temporaneo: questo è preferibile a copie ZIP permanenti duplicate in R2. Se archivio/MP4/post/ZIP non sono verificabili, segnare `archive_sync_pending` e segnalare il blocco specifico. **Non dire mai che è già online soltanto perché il pacchetto è nel repository o in ChatGPT.** Importare solo video di produzione autorizzati, preservare modifiche del proprietario e file eliminati.

**Implementazione operativa:** ArtVision usa `src/artvision_delivery_v55.py pack` (ffprobe, decodifica, copertina, quattro post, fotogrammi veri iniziali, ZIP CRC e SHA256) e `site-check --key NOME.mp4` per *una parte* del controllo pubblico; gli esiti di ChatGPT, dossier privato e ZIP del sito vanno verificati separatamente. Gli altri format applicano gli stessi requisiti con i propri generatori. Workflow GitHub import ed enrichment + automazione Libreria ChatGPT restano percorsi di sincronizzazione distinti; l'eventuale trigger al completamento di un render accelera la richiesta ma non garantisce disponibilità istantanea.

**Release finale =** asset reali + revisione artistica/diritti + consegna ChatGPT effettiva + archivio privato effettivamente verificato, salvo blocco dichiarato. La promessa che un link esterno sia sempre disponibile non è certificabile senza verifica sul dispositivo e sul servizio; applicare sempre fallback e stato onesto. Non implica pubblicazione sui social e non autorizza costi.

## Produzione seriale ArtVision a coppie — regola approvata 28/10/2026 (V53)

**Nuova richiesta dell'utente:** per ogni quadro selezionato realizzare **due video originali collegati**: (A) Cinema / Museum Immersion, senza voce, ingresso nel quadro seguendo proporzioni e cornici V46; (B) Critico d'arte narrato, con studio approfondito, copione italiano naturale, voce Google Gacrux effettiva e dettagli strettamente sincronizzati alle frasi. Studio del soggetto comune per non rispendere risorse, ma montaggio e regia separati, senza copie travestite. Vale per qualunque tipologia di opera purché l'autenticità, le dimensioni e le capacità del renderer siano verificabili.

**Cadenza richiesta:** un ciclo automatico ogni **due ore**, obiettivo un video artisticamente buono e revisionato per ciclo (non due video insieme ogni due ore). Se il Cinema già esiste, iniziare dal Critico mancante; completare entrambi prima di considerare terminata la coppia. La qualità prevale sul conteggio: se assenti voce vera, foto/diritti o review, segnalare stato esatto e passare ad attività sicura nella coda, senza inventare risultati.

**Fonte operativa:** [ArtVision V53 — produzione a coppie](ARTVISION_PRODUZIONE_A_COPPIE_V53.md) e `queue/artvision_dual_format_s01_20261028.json`; riutilizzare l'automazione ArtVision esistente, non creare un secondo programma concorrente. Preservare la minisérie Museum Scale S01, master, file review e gate V44; budget IA video pagato pari a zero fino ad autorizzazione per singola generazione, nessuna autopubblicazione social.

## Quattro ambiti comprensibili

| Ambito | Cosa significa | Esempio |
|---|---|---|
| Sempre | Requisito comune | Fonti reali, Android, consegna scaricabile |
| Per questo format | Identità che va protetta | Critico con voce, Cinema senza voce |
| Per questo video | Scelta motivata | Apertura, durata e musica di questo soggetto |
| Da provare | Esperimento, non ancora approvato | Nuovo mix o nuova chiusura |

Un esempio dell'utente resta uno spunto. L'approvazione di un filmato non significa
che ogni suo dettaglio diventi obbligatorio in tutti i film futuri. Per una nuova
regola riutilizzabile registrare ambito, motivo, riferimento, approvazione e versione.

## Crediti IA video a pagamento — REGOLA PERMANENTE VINCOLANTE (27/10/2026)

**Approvazione esplicita dell'utente:** i soldi per i crediti di generazione video sono limitati e vanno rispettati. Il semplice acquisto dei crediti, la presenza di una chiave API, frasi come "fatto", "continua", "prosegui" o il numero-obiettivo "20 clip al giorno" **NON autorizzano a spendere nemmeno un credito**.

1. **Nessuna generazione video pagata per prove casuali.** Prima di consumare crediti preparare GRATIS una scheda della singola scena: progetto/episodio, immagine effettiva visionabile, testo narrato e punto temporale preciso, azione fisica che deve avvenire, prompt positivo e vincoli negativi, modello, durata, formato, preventivo e utilita prevista nel montaggio finale. Confrontare con immagini/personaggi preesistenti; NON generare stock narrativamente scorrelato.
2. **Preflight editoriale approfondito e autocritico, a costo zero.** Verificare fonte e diritti, composizione originale, volti, mani, ambiente, epoca, movimenti plausibili, formato/crop, continuita personaggi e dialogo, coerenza del modello scelto. Chiedere chiarimenti se lo scopo o la qualita attesa sono incerti, invece di tentare a pagamento. Non promettere un risultato "wow" certo: la generazione IA e probabilistica.
3. **APPROVAZIONE ESPLICITA PER OGNI GENERAZIONE** legata a immagine, prompt, modello, durata, costo massimo e scena; usare codice univoco derivato dal preventivo approvato nel workflow Vidu. L'operatore deve vedere la scheda e autorizzare il singolo submit dopo averne compreso contenuto e costo. Ogni variazione richiede un nuovo piano e una nuova approvazione. API key = permesso tecnico, NON assenso economico. Vietata autoapprovazione dell'assistente.
4. **Niente lotti, rinnovi, retry, fallback pagati, programmazioni ricorrenti o generazioni speculative** senza autorizzazione separata e limiti espliciti. Un fallimento non autorizza una seconda spesa. In caso di timeout controllare lo stato del task nel provider prima di qualsiasi tentativo; non inviare alla cieca. Limitare le chiamate per run e impedire re-run di job a pagamento.
5. **Tracciabilita dei crediti**: preservare preventivo, codice approvato, data, scena, modello, durata, ID task, stato, esito, costo provider quando disponibile e hash degli asset. Indicare le stime come tali, non come addebiti verificati; budget giornaliero predefinito ZERO, fino a esplicita autorizzazione del singolo costo.
6. **Qualita prima della quantita**: i modelli economici vanno scelti solo se adeguati alla scena. Per un effetto importante meglio zero clip che un esperimento scadente. Una clip prodotta resta DA_REVISIONARE fino al controllo reale; non dichiararla buona per il progetto solo perche l'API ha generato un MP4.
7. **Consegna affidabile**: scaricare il video completato dal provider prima della scadenza del link, verificare bytes/formato, salvare originale e ZIP Android, predisporre collegamento recuperabile, senza inventare percorsi.

**Ambito:** tutti i fornitori a credito IA image-to-video, text-to-video, restauro video a pagamento, incluse Vidu, Wan, Kling, Seedance, Runware e provider futuri. Si applica a produzioni manuali, agenti automatici e workflow GitHub. Questa regola prevale su qualsiasi indicazione generale di autonomia, target numerici e routine di produzione. Nessuna spesa e stata autorizzata con questa modifica documentale.

## Vidu come motore cinematografico prioritario — V45 (27/10/2026)

L'utente ha acquistato circa 10 euro di servizio Vidu e richiede esplicitamente che venga **usato e valorizzato davvero** per scene image-to-video cinematografiche del progetto, senza sostituire le richieste con motion finti OpenCV/FFmpeg. Le regole di autorizzazione per SINGOLA spesa restano vincolanti e non significano "non utilizzare mai Vidu". Ogni nuovo episodio con azioni visive importanti deve valutare gratuitamente se Vidu può aumentarne davvero l'impatto; preparare una proposta precisa invece di ignorare lo strumento.

Selezione per ogni scena: usare l'immagine originale in migliore qualità recuperabile; individuare gesto fisico interamente visibile e sincronizzato alla voce; stabilire durata adeguata, modello e risoluzione; confrontare il rapporto crediti/risultato per Q2/Q3 tenendo conto dei prezzi correnti; NON assumere che un modello più costoso sia automaticamente migliore. Confermare il saldo **API** con GET /ent/v2/credits senza addebiti: un abbonamento consumer potrebbe non alimentare lo stesso wallet API. In assenza di credito API, NON acquistare automaticamente altri pacchetti: usare, ove consentito e disponibile, il servizio web Vidu già sottoscritto o chiedere la soluzione praticabile.

Per la clip scegliere il movimento con attenzione, usare un prompt singolo preciso, generare soltanto la scena approvata, recuperarla e revisionarla prima di qualsiasi altro pagamento. Conservare master originali, clip autentica, task ID, costo, confronto prima/dopo, motivazione, esito V44, montaggio con voice sync, MP4/ZIP Android. Una clip fallita resta scartata, NON genera retry o addebiti impliciti.

La prima proposta concreta: La macchina del tempo di H.G. Wells, gesto della leva intorno 10,9–15,9 secondi, 5 sec Q2 Pro Fast 720p offpeak circa 8 crediti ($0,04) oppure Q3 Turbo 720p circa 30 crediti ($0,15) in offpeak. Prezzi da verificare sulla console prima del singolo pagamento. Il sorgente 505×761 resta un rischio qualitativo: non confondere upscale con recupero dei dettagli.

## Qualita animazioni e blocco anti-consegna scadente — VINCOLANTE V44 (27/10/2026)

**Incidente approvato come feedback correttivo:** il video \`MACCHINA_DEL_TEMPO_ANIMATA_FINALE.mp4\` del 27/10 NON e approvato. Una ruota ruotata localmente e una leva deformata non realizzano la vera azione "l'uomo tira una leva". La visione critica deve avvenire PRIMA della consegna, non dopo il rifiuto dell'utente. Dettagli e prove: \`docs/VIDEO_INCIDENT_2026-10-27_V44.md\`.

**No auto-promozione dei render.** Quando un video gia esistente riceve scene animate nuove, tanto gratuite quanto a pagamento, creare un contratto V44 con originale, clip inserita, MP4 completo, hash e frase/secondi esatti. Confrontare prima/dopo a velocita normale, osservare gesto completo, sincronizzazione con la voce, identita di volto e mani, meccanica plausibile, artefatti, raccordi, musica e miglioramento rispetto al master. Difetti visibili determinano **SCARTATO**, non "buono abbastanza".

Se la richiesta esplicita e vera animazione generativa image-to-video, **vietato surrogarla** con warp, rotazioni di frammenti, dolly-zoom, semplici pan o morphing artificioso presentati come scena IA. Puo essere una bozza dichiarata, mai l'adempimento della richiesta. Il modulo \`src/animated_video_release_gate_v44.py\` deve rifiutare un \`final delivery\` di genere generativo senza provenienza reale e revisione del medesimo SHA-256.

**Stati:** \`planned\` → \`rendered_needs_review\` → \`approved_for_final_delivery\` soltanto dopo verifica effettiva di tutte le prove. In mancanza di un revisore realmente coinvolto, lo stato resta \`rendered_needs_review\` e non si usa nel sito fra i video finiti, non si pubblica, non si manda come "finale" o "ottimo". L'esito artistico resta valutazione umana: nessun flag software garantisce la bellezza.

La regola prevale su target numerici, urgenza, export tecnico, istruzioni dei vecchi workflow e qualsiasi scorciatoia di chat. NON comporta alcun consumo di crediti.

## Museum Immersion V46 — modello approvato per ArtVision Cinema e Critico (27/10/2026)

**Approvazione esplicita dell'utente:** la versione **The Cyclops — Odilon Redon, SENZA STRISCE CORRETTO** è un riferimento positivo da **usare spesso**, sia nei video ArtVision Cinema sia nei video Critico d'arte. Recuperare prima **`docs/ARTVISION_MUSEUM_IMMERSION_MODELLO_APPROVATO_V46.md`** e confrontare il file esatto conservato su Google Drive, non le varianti con difetti.

**Regia ricorrente opzionale, non stampino:** museo fotorealistico, quadro realmente incassato dietro il labbro interno della cornice, centratura e ombre credibili, POV visitatore che entra nell'opera, scene pittoriche significative, ritorno alla stessa sala. In Cinema mantenere regia musicale senza voce secondo V6; nei Critico preservare voce naturale e sincronizzazione con le parole secondo V2. Applicarla spesso quando motivata, alternando altri ingressi.

**QA BLOCCANTE:** niente fasce di colore ottenute replicando o stirando l'ultima riga di pixel nella parte alta o bassa durante pan/zoom, niente quadro sovrapposto alla cornice o raccordi visivamente bruschi. Verificare tutti i movimenti e i bordi, prima e dopo i passaggi e a velocità normale; i soli test ffmpeg non bastano. Sala ricostruita dichiarata, fotografia pittorica autentica e diritti controllati. Non confondere questa approvazione di riferimento con un nuovo Gold Master automatico.

### V56 — blocco delle regressioni Museum (29/10/2026)

**Feedback esplicito dopo aver visto i nuovi Hokusai e Homer:** le due nuove versioni Museum non rispettano il precedente livello di sala/cornice e l'ingresso fluido. Confronto reale concluso con i due **MP4 approvati** recuperati dal Drive (Cyclops `1w9mb1N5hrGAaB870JANHoKk98MiibtpW`; Hiroshige `14X8_TObXEijGlBg8HuyR6ITTlPjJk0dA`). Diagnosi ed evidenze misurate: `docs/ARTVISION_MUSEUM_V46_REGRESSION_REVIEW_20261029.md`.

- È **vietato** produrre la parte Museum con una parete JPG piatta e un semplice `ffmpeg zoompan` a cui segue un taglio diretto verso il dettaglio pittorico. L'ingresso deve attraversare fisicamente la battuta interna con trasformazione spaziale continua nei pixel originali e l'uscita deve ripercorrere il medesimo sistema di coordinate della sala. Niente dissolve che mascherano il salto, sovrapposizioni, strisce o stretching.
- La cornice non è un contorno rettangolare: ricerca fotografica e diritti sull'esatta opera; replica fedele della cornice documentata quando possibile, altrimenti ricostruzione scenografica dichiarata con spessore reale, sezioni, materiale, giunti, luci e ombre di contatto, quadro fisicamente dietro il labbro interno.
- Scala con **riferimento umano/porta e distanza camera** oltre ai centimetri della tela; fotorealismo dell'ambiente e leggibilità su telefono paragonabili a Cyclops e Hiroshige. Non appiattire tutte le opere in sale identiche.
- **Gate obbligatorio sui veri MP4:** `src/artvision_museum_v46_regression_gate.py`, controllando entrata e uscita (continuity gate V57 sul PICCO ISOLATO rispetto ai fotogrammi vicini (picco ≥30/255, rapporto ≥2,7 e differenza ≥18 solo se simultaneamente presenti), non sul MAD massimo assoluto: nel V46 Cyclops APPROVATO la camera fluida arriva a ~22,81/255. Il test è solo un veto tecnico e non sostituisce una revisione artistica.); un gate numerico che passi non certifica la bellezza, quindi necessaria revisione completa umana del materiale, quattro angoli, prima/ultima vista e confronto con entrambi master approvati.
- Hokusai Museum V55C e Homer Museum V55B sono **tecnicamente renderizzati ma bocciati dalla direzione artistica**, non sono nuovi master approvati e non devono fare scuola. Conservarli per diagnosi e ripristino, non registrarli come quattro varianti finite. Se non è implementato il vero V46, segnare `blocked_quality_museum_v46_not_met` e **non consegnare un nuovo Museum mediocre** per rispettare la cadenza.

**Non modificare** i master approvati, non sostituire l'effetto Museum con un Cinema Standard rinominato, non spendere crediti video IA senza permesso per singola clip.

### V57 — provino pratico su vera camera V46, regia distinta per le 4 varianti (APPROVATO 29/10/2026)

L'utente ha approvato lo stile del provino Cyclops V57 da 34 secondi, SHA256 4d746edb3cd1083605ff11b0dce2bbfbe0e37eda01b836b8243894c732d509bb. Modello per la camera continua delle due varianti Museum: ingresso/uscita nella stessa sala, opera allineata e incassata, dettagli riproiettati dall'originale, dimensioni reali. Rimangono riferimenti complementari Cyclops V46 per qualita' della cornice e Hiroshige per scala umana. Per ogni nuova opera sala e cornice devono essere specifiche, non ripetute automaticamente. Le quattro varianti restano distinte: Critico Standard voce Gacrux, Critico Museum medesima voce e camera museo V57, Cinema Standard musica soltanto, Cinema Museum musica e camera museo V57. Ogni futuro MP4 richiede revisione artistica e V25; il consenso sul provino non autorizza pubblicazione automatica o spese.



**Nuovo filmato pilota REALE:** `ARTVISION_CYCLOPS_V46_PROVINO_ANDROID.mp4`, 34 s, SHA256 `4d746edb3cd1083605ff11b0dce2bbfbe0e37eda01b836b8243894c732d509bb`. Non è un nuovo quadro né master approvato: è un nuovo percorso ottico sul materiale ArtVision Cyclops già approvato, con immagine originale Redon ad alta risoluzione riproiettata continuamente nello stesso piano della cornice e ritorno alla stessa stanza. Prima prova bocciata per disallineamento opera/cornice; corretto attraverso vera registrazione feature SIFT/RANSAC dell'immagine sul master. **Nessun costo video API.** Regole operative + quattro versioni specifiche: `docs/ARTVISION_QUATTRO_VARIANTI_REGIA_V57_20261029.md`.

**Correzione gate V56:** il solo MAD consecutivo ≤12/255 aveva falsi positivi su zoom fluido del Cyclops APPROVATO. Confronto vero: approvato 22,81/255 con vicini ~21,37 (rapporto 1,07); nuovo provino 22,02 con vicini ~20,92 (1,05); Hokusai V55C jump 72,28 su base 2,30 (31,42). Usare ora lo **spike relativo** del gate V57 e mantenere separata la valutazione artistica del quadro, museo e cornice. **Non auto-approvare il provino** e non adottare la stessa sala per tutte le opere.

## Scala reale delle opere nei video Museum Immersion

**Conferma positiva 28/10/2026 — due modelli complementari approvati:** *The Cyclops* di Redon, **versione senza strisce**, per cornice realistica e regia pulita; *Sudden Shower* di Hiroshige, **Museum Scale 20261027**, per rapporto dimensionale corretto tra piccola stampa, visitatore e sala. L'utente ha valutato espressamente ben studiate le proporzioni di Hiroshige e ha chiesto di riutilizzare entrambi come modello. Leggere `docs/ARTVISION_MUSEUM_IMMERSION_MODELLO_APPROVATO_V46.md` prima dei nuovi video Cinema o Critico con effetto museo. Non adottare dimensioni uniformi: verificare la misura museale e adattare architettura, camera e inquadratura. L'approvazione non equivale a Gold Master globale.
 — regola approvata (27/10/2026)

**Indicazione esplicita dell'utente:** ogni quadro o stampa deve sembrare delle sue dimensioni fisiche reali. Una piccola tavoletta da 20–40 cm va mostrata piccola in una sala credibile; una tela da 5–10 m deve occupare un'immensa parete con prospettiva, distanza di osservazione e architettura coerenti. Non trattare tutti i dipinti come della stessa grandezza.

Per ogni nuovo video Museum Immersion registrare nel piano/ricetta **larghezza e altezza in cm**, fonte museale verificata, eventuali variazioni fra esemplari/edizioni, distinzione tra quadro e cornice, presenza di autentica cornice o ricostruzione, dimensioni indicative della sala e punto di vista della telecamera. Usare scale note (visitatore adulto circa 1,7 m, porte, pavimento, targhette) come riferimenti prospettici. La proporzione del dipinto e della cornice deve rimanere corretta durante l'avvicinamento e il ritorno. Non rimpicciolire i quadri monumentali, non ingigantire le stampe, non deformare la pittura.

In caso di misura non documentata dichiarare `unknown`, non inventarla. L'illustrazione della sala, se generata e non documentale, deve essere descritta come ricostruzione e non come allestimento museale reale. La cornice deve contenere fisicamente l'opera nel suo vano interno con occlusione e ombre, mai sembrare un'immagine incollata. Controllare il tutto su still e sui fotogrammi intermedi; seguire anche il modello V46 del Cyclops corretto senza strisce.

**Episodio di prova scala piccola:** Hiroshige, `Sudden Shower over Shin-Ōhashi Bridge and Atake` (1857); esemplari museali comparabili circa 35 × 24 cm, fonte Cleveland Museum of Art 1921.318 e Met Museum JP644. La fotografia autentica d'archivio può rappresentare un'altra impressione dello stesso disegno e non va attribuita senza prova a uno di questi due esemplari.


## Cornici museali di alta qualità — regola permanente (feedback 28/10/2026)

**Richiesta esplicita dell'utente:** nelle sequenze in prima persona / Museum Immersion la cornice deve valorizzare davvero l'opera, con qualità visiva superiore a quella degli ultimi tentativi. Prendere come riferimenti *The Cyclops — SENZA STRISCE CORRETTO* (incasso e integrazione) e *Hiroshige — Museum Scale* (proporzioni), senza copiare meccanicamente una cornice unica.

- **Scelta specifica per opera:** cercare prima fotografie verificabili della cornice reale e la sua provenienza. Se non è verificata, indicare «cornice scenografica ricostruita» nel dossier, senza spacciarla per autentica. Disegnare una cornice credibile per epoca, tecnica, dimensioni e carattere del dipinto; non applicare sempre una cornice dorata, barocca o esagerata. Per una stampa modesta può servire una cornice discreta con passe-partout appropriato; per una tela monumentale una struttura robusta ma proporzionata.
- **Valore visivo e materiali:** cornice tridimensionale con sezioni e modanature plausibili, legno/metallo/doratura materici ma non pacchiani, grana e imperfezioni sobrie, angoli coerenti, fonte luminosa definita, ombre di contatto sotto il labbro interno, profondità reale nel vano, eventuale vetro solo se plausibile e senza riflessi che coprono l'opera. L'opera va dietro il bordo interno, mai sovrapposta alla cornice o deformata per riempirla.
- **Proporzioni non negoziabili:** dimensioni del dipinto originali in cm, proporzione esatta lato/lato, spessore e larghezza della cornice coerenti con misure reali, scala della sala e del visitatore adulto (~170 cm). Documentare anche le dimensioni dell'insieme tela+cornice, se note, separando misure verificate da scelte scenografiche. Un dipinto piccolo resta piccolo sulla parete, e un grande quadro conserva la sua presenza monumentale; i dettagli possono diventare grandi soltanto con l'avvicinamento della camera.
- **Regia e branding:** nell'apertura il pubblico deve percepire bellezza dell'oggetto *quadro + cornice* e rapporto con la sala; l'ingresso e l'eventuale uscita devono risultare fisici e progressivi, senza ghosting, bordi allungati, pixel ripetuti, jumps o cambi di proporzione. Testi iniziali di titolo e artista come da preset, leggibili ma senza coprire il fulcro.
- **QA BLOCCANTE prima di chiamare l'episodio consegnabile:** confrontare una vista della cornice con i riferimenti approvati V46/Hiroshige, controllare a dimensioni telefono **apertura, quattro angoli, modanatura, incasso, ombre, eventuale vetro, scala relativa, ingresso/uscita e fotogrammi intermedi**; verificare bordi video e rapporto d'aspetto. Rifiutare/correggere cornice piatta, artificiale, pacchiana, sproporzionata, quadro incollato o dettagli dell'opera nascosti. Annotare foto/asset della cornice, natura autentica o illustrativa, misure, revisione visiva ed eventuali limiti nel dossier/ricetta. Un controllo automatico non sostituisce revisione artistica reale.

### Priorità alla replica della cornice autentica — approvata il 28/10/2026

**Regola di scelta obbligatoria prima del render Museum Immersion:**
1. Cercare prima la cornice **effettivamente visibile oggi** nelle fotografie del museo, catalogo, conservazione o archivio autorizzato, e individuare **l'esatto esemplare dell'opera**. Se documentata in immagini sufficienti, **replicare quella cornice** (profilo, rapporto larghezza/opera, materiali, finiture, ornamenti, angoli, battuta interna, eventuale vetro o passe-partout) senza sostituirla con una cornice genericamente più lussuosa. Anche una cornice semplice può essere la scelta corretta.
2. Distinguere sempre **cornice originale dell'artista / cornice storica successiva / cornice attualmente esposta**. Una foto del museo prova al massimo l'aspetto della cornice nella data della fotografia, non necessariamente la sua originalità o l'installazione attuale. Se esistono versioni diverse scegliere quella pertinente alla narrazione e riportare data e fonte, senza mescolare parti di cornici differenti.
3. Se la cornice reale è solo parzialmente visibile, creare una **replica parziale con dettagli ipotizzati dichiarati**. Se non esistono immagini e misure affidabili, utilizzare una **ricostruzione scenografica storicamente plausibile** dichiarata; non usare etichette «replica fedele» o «cornice originale» senza prova.
4. **Autenticità e diritti separati:** salvare URL/ente/data/autore della foto della cornice e diritto di riuso dell'immagine; documentare separatamente licenza della riproduzione dell'opera. Non prelevare automaticamente foto museali protette per pubblicarle. È possibile usarle come riferimento visivo solo nel rispetto dei diritti applicabili, senza sostenere che il fotogramma ricostruito sia una foto del museo reale.
5. **Scala in centimetri:** registrare altezza/larghezza esatte dell'opera; per cornice registrare larghezza esterna, spessore, larghezza modanatura o `unknown` e distinguere **valori documentati** dalle stime scenografiche. Non derivare misure fisiche sicure da una sola foto priva di riferimento metrico. Mantenere la cornice allineata e proporzionata alla tela lungo tutti i movimenti.
6. **Scheda obbligatoria nel dossier/ricetta:** `frame_research` con `authenticity_status` (`documented_current`, `documented_historical`, `partial_reconstruction`, `scenic_reconstruction`), `source_urls`, `photo_date_or_unknown`, `rights_status`, `evidence_notes`, `artwork_size_cm`, `frame_size_cm_or_unknown`, `assumptions`, `reference_visual_compared`, `qa_visual_result`. Segnalare indisponibilità e prove mancanti invece di compilare valori inventati.
7. **Gate bloccante:** nella vista museale controllare replica rispetto alla fotografia di riferimento, angoli, profilo, doratura/patina e legno, contatto reale tra tela e battuta, prospettiva, illuminazione, proporzioni rispetto a visitatore e sala, eventuale ritorno alla medesima cornice. Se replica somiglia poco alla cornice documentata, correggere o declassare con chiarezza a ricostruzione; non dichiararla autentica. Il gate qualità estetica e i precedenti divieti V44/V46 restano indipendenti.

**Scelta di gusto:** la cornice deve aumentare il valore percepito attraverso fedeltà, materiali, profondità e illuminazione, non con ornamenti inventati. Non forzare l'effetto museo su tutti gli episodi e non approvare automaticamente il filmato dopo il solo QA tecnico.

**Ambito:** tutte le nuove produzioni Cinema V6, Critico V2 e Collection quando adottano effetto visita museale in prima persona. Questa regola aggiorna la qualità delle cornici; non obbliga l'effetto museo in ogni video, non sostituisce i due riferimenti precedenti, non modifica master esistenti e non autorizza alcuna spesa o pubblicazione.

## Decisioni consolidate

| Prima | Ora |
|---|---|
| Apertura unica o sempre dettaglio → totale | Repertorio di aperture; scelta motivata sul soggetto |
| Quota fissa di scene, effetti, tipi di inquadratura | Nessuna quota estetica: ogni scelta deve avere una funzione |
| 3–8 tecniche sempre | Il mix esplicito può essere più semplice o articolato; nessun riempimento automatico |
| Finestre di durata prese come obbligo | Durata proposta motivata; per narrati revisione sull'audio effettivo |
| Musica obbligatoriamente nuova ogni volta | Riuso consentito quando coerente, senza rotazione meccanica |
| Domanda, CTA o hashtag standard obbligatori | Elementi pertinenti, secondo post e piattaforma |
| Post Facebook sempre italiano | Lingua esplicita per piattaforma; testi Cinema a schermo internazionali |
| Copertina uguale pixel per pixel | Firma invariata, composizione adeguata al soggetto; vecchie cover preservate |
| Più effetti o versione più recente = migliore | Confronto sullo stesso obiettivo e revisione del risultato |
| Audio presente = voce corretta | Verificare parlato, identità vocale e corrispondenza con immagini |
| MP4 generato = finito | Tecnica, revisione artistica e consegna sono verifiche distinte |

Restano i controlli no ghosting, fonti/diritti, voce di riferimento, format,
conservazione degli originali e assenza di pubblicazione implicita.
I limiti tecnici del renderer vanno dichiarati e non confusi con regole artistiche.
Un formato nuovo o una variante con sottotitoli/voce diversa richiede un profilo
compatibile: il percorso attuale mantiene i profili approvati.

## Ricerca pubblico e regia motivata — VINCOLANTE per ArtVision (25/10/2026, V32)

Approvazione esplicita dell'utente: non scegliere un quadro soltanto perché è bello o famoso.
**Prima di ogni nuovo ArtVision Cinema, Critico o Collection**, se il soggetto
è da scegliere confrontare **almeno tre** opere/temi distinti e scegliere in base a una ragione umana di visione: interesse
pubblico verificabile quando disponibile, impatto visivo iniziale, storia vera,
possibilità di regia, originalità del catalogo, riproduzioni e diritti. Ampliamento
facoltativo a 10–20 candidati quando le fonti lo rendono davvero utile, senza
trasformarlo in una quota burocratica.

Se l'utente indica già l'opera, non sostituirla: la ricerca sul suo interesse
resta obbligatoria, ma il confronto con tre altre opere è facoltativo e va
registrato il vincolo esplicito della richiesta.

I segnali di Google Trends, Facebook, Instagram, TikTok, YouTube o altre fonti
si registrano con URL, data, contesto e osservazione, **senza inventare numeri
di visualizzazioni o viralità**. Se un segnale non è accessibile: annotare
`unavailable` e motivo, ragionare qualitativamente e non presentare ipotesi
come dati. Una scelta artistica può privilegiare un'opera meno cercata per
una motivazione documentata.

**La regia nasce dall'opera e dall'interesse umano**, non da 8/10 crop ripetuti:
apertura, dettagli, andamento, musica/voce e finale devono rispondere a una
promessa concreta al pubblico, rispettando stile del format, no ghosting
e controlli 0/1/3/5/7. Dopo una pubblicazione, confrontare solo metriche
realmente accessibili (retention, completamento, durata media, condivisioni).
Nessun KPI inventato, nessun automatismo di approvazione Gold Master.

La guida `docs/ARTVISION_AUDIENCE_RESEARCH_V32.md` specifica la griglia
qualitativa /100 e i campi per `editorial_plan.audience_research`.
Per nuovi progetti ArtVision il preflight V13/V16 blocca il render senza
confronto documentato, scelta e ragione di regia. Altri renderer che non
chiamano quel preflight devono applicare la stessa regola esplicitamente.
Questa è una regola **sempre** per ArtVision, non un esperimento e non
un nuovo preset visivo. Non modifica video/master esistenti.

## Priorità opere WOW — 28/10/2026

**Feedback esplicito su Van Eyck V53:** realizzazione e cornice gradite, ma il dipinto non ha abbastanza forza visiva per gli obiettivi social del progetto. Nella scelta libera di nuove opere ArtVision dare priorità a quadri straordinari e sorprendenti **per merito dell'opera stessa**, prima di curare cornice, museo e movimenti.

Confrontare almeno tre candidati e controllare catalogo/duplicati. Valutare sul telefono la forza del primo fotogramma in 9:16, qualità compositiva e colori, meraviglia, mistero, scene epiche, dettagli nascosti davvero significativi, storia verificabile, fonti e diritti, dimensioni e cornice museale. Alternare temi e regie: niente sequenza ripetitiva di soggetti cupi o singoli primi piani. Se nessuna opera ha un motivo forte per catturare l'attenzione, non sprecare una produzione. La scelta artistica non garantisce viralità.

**Gate:** prima del render annotare `phone_first_frame_hook`, `discovery_detail`, `narrative_turn`, `vertical_fit`, `catalog_duplicate_check` e prove disponibili. Una cornice lussuosa non sostituisce un soggetto poco interessante. Se un'opera è scelta espressamente dall'utente, rispettare la scelta e progettare la migliore interpretazione possibile. Applicare anche V32, V28, V44, V46, autenticità cornice e divieto di crediti IA video a pagamento non approvati.

## Filosofia fonti e API V33 — VINCOLANTE per tutti i nuovi contenuti (25/10/2026)

Approvazione esplicita dell'utente: priorità a sistemi e API gratuiti già disponibili,
senza perdere qualità né cambiare il linguaggio del singolo format.
**Prima recuperare asset approvati; poi scegliere fonti autentiche o archivi quando
servono fatti/opere reali, stock pertinente quando serve ambientazione, illustrazione
originale quando il racconto richiede personaggi o azioni precise**.
La preferenza di provider è guidata da pertinenza narrativa, diritti e autenticità,
non da una classifica rigida o dalla quantità di immagini generate.

**Pixabay** è il nome corretto del servizio. Il segreto già inserito `PIXABAY`
ha priorità nell'adapter; `PIXABAY_API_KEY` è alias facoltativo;
`PRIXIBAY2` non viene utilizzato automaticamente senza verifica.
AI Horde resta sperimentale (chiave principale `AIHORDE_API_KEY`), Google
Gacrux mantiene `GEMINI_API_KEY`, OpenRouter `OPENROUTER2` non autorizza
modelli a pagamento e non è ancora attivo per inferenza.
Secondi account non si usano per aggirare quote; niente API costose automatiche.
Pixabay richiede ricerche reali e cache 24h; il bridge non ha ancora cache
persistente, quindi evitare richieste duplicate e volumi massivi.

Per ogni nuovo progetto V13 annotare in `editorial_plan.media_sourcing` la
sorgente e la decisione **di ogni asset visivo**. Il check V13 blocca mancanza
di verifica di diritti, pertinenza, fonte, esame visivo, oppure l'uso di immagini AI
come quadro autentico/prova di cronaca. Nessun campo tecnico certifica bellezza.
Risultati/diritti/seed/hash sono riusabili solo se registrati; gli asset già approvati
non vengono riscritti. Le 45 API V2 sono un catalogo, non 45 connettori attivi.

Dettagli e differenze tra format: `docs/FILOSOFIA_FONTI_MEDIA_V33.md`.
Le nuove chat indipendenti devono leggere o ricevere le regole esplicitamente:
il repository non può imporle a una chat che non lo consulta.

## LIBRI / RACCONTI — SOLO EPISODI COMPLETI IN CONSEGNA (29/10/2026)

**Feedback esplicito dopo le anteprime non narrate di Alice, Pifferaio, Rip Van Winkle e Pinocchio:** «Cerca di darmi sempre prodotti video completi». Per le richieste di produzione LIBRI / RACCONTI la consegna attesa è **un racconto concluso** con inizio, sviluppo, finale, voce italiana **Google Gemini Gacrux effettivamente prodotta e controllata**, immagini pertinenti sincronizzate, montaggio 9:16 720×1280 H.264/AAC, qualità artistica verificata, copertina, storyboard/V13/V35, fonti e diritti, musica, quattro post e **MP4 + ZIP solo-video V36 + dossier completi realmente scaricabili**. Il vecchio schema «solo 20–40 secondi di immagini mute e musica» **non soddisfa** questa richiesta: non usarlo come sostituto automatico del video narrato. Né Edge/Diego né altro TTS può prendere il posto di Gacrux senza consenso esplicito.

Se Gacrux, quote o diritti non sono confermati, continuare il lavoro gratuito consentito e riportare in modo esatto il blocco: **non dichiarare un episodio completo né produrre abitualmente anteprime mute da consegnare come video richiesto**. Il successo di FFmpeg o di uno ZIP non dimostra qualità, idoneità dei diritti o approvazione artistica. Un'eventuale anteprima richiesta appositamente resta una bozza separata e chiaramente etichettata. Nessuna chiamata Vidu/API video a pagamento e nessuna pubblicazione social implicita. **Fonte operativa:** `docs/LIBRI_CONSEGNA_COMPLETA_20261029.md`; configurazione `config/editorial_rules.json > formats.libri`. Non modifica ArtVision né master storici.

## Descrizioni social di alta qualita e recuperabili nel sito — VINCOLANTE (26/10/2026)

**Conferma e irrigidimento della V28**, non un nuovo format. Ogni nuovo video ha post **differenziati** per Facebook, Instagram, TikTok e YouTube, con fatti verificati e taglio narrativo scelto sul contenuto (autore, vicenda, interpretazione prudente, contesto storico, museo, personaggi, emozione). Identita editoriale riconoscibile ma apertura, ritmo e prospettiva mai meccanicamente identici.

**Pubblico:** solo contenuto interessante su opera/storia e crediti realmente obbligatori; niente montaggio, zoom, render, script, prompt, metodologia, algoritmi o informazioni che lo spettatore non deve conoscere. **Privato:** regia, ricette, prompt e conti restano nel dossier tecnico.

La consegna include quattro file social curati, **scheda visuale** nello stile editoriale approvato e **scheda testuale** corrispondente. Per i video importati realmente, queste descrizioni devono essere salvate nella scheda del singolo video su Video Library Studio ed esportabili dal telefono. Nessun testo generico generato dalla categoria vale come post pronto. Se il video non e ancora sul sito, dichiararlo e non simulare il salvataggio.

Il sito applica filtri strutturali contro campi vuoti/identici/cliche e dettagli tecnici, ma revisione umana del contenuto e verifica di fonti/diritti restano indispensabili. Vedere `docs/ARTVISION_EDITORIAL_POST_STANDARD_V28.md` e `docs/VIDEO_LIBRARY_DOSSIER_V1.md`.

## Riferimento positivo e originalita narrativa — VINCOLANTE (26/10/2026, V38)

**Feedback approvato:** *La macchina del tempo* di H. G. Wells e stato giudicato un **buon risultato**, piu bello dei video precedenti soprattutto per una maggiore ricchezza/varieta delle immagini; restano migliorie possibili. Registrare questa valutazione come **riferimento qualitativo positivo**, non come `GOLD MASTER`, licenza, promessa di successo o istruzione per copiare il suo montaggio.

**Regola permanente anti-stampino:** ogni storia/opera deve determinare autonomamente durata, quantita di immagini *distinte*, ordine e durata delle scene, ritmo, variazioni di camera, apertura, musica e finale. La copertina mantiene la firma della serie ma il racconto non deve ripetersi meccanicamente. Vietato trarre dalla *Macchina del tempo* una durata standard, 16 illustrazioni obbligatorie, un numero prefissato di effetti o transizioni e un medesimo schema di montaggio.

Prima di acquisire asset, individuare beat narrativi, luoghi, azioni, emozioni e cambi di significato; motivare scelte di durata e mix e allinearle alle parole e all'audio reale. **Più immagini è positivo solo quando aumenta pertinenza e interesse, non se introduce ripetizioni o filler.** Per racconti diversi sono validi anche pochi quadri lunghi o molti cambi, quando servono alla storia.

Documento operativo `docs/FEEDBACK_REGIA_NARRATIVA_V38.md`; configurazione `config/editorial_rules.json > creative_variation, creative_references`. Il controllo strutturale non certifica la bellezza né trasforma automaticamente il filmato in master approvato.

## Consegna file verificabile su Android — regola permanente (27/10/2026)

**Richiesta esplicita dell'utente dopo ripetuti errori "Library file not found":** per ogni nuovo file generato e consegnato in ChatGPT (MP4, immagini, ZIP, PDF, documenti o altri allegati) non basta stampare un link o affermare che il render è riuscito.

1. Verificare nella sessione corrente il **percorso effettivo** del file, che esista, sia non vuoto e del formato richiesto; per MP4 controllare con ffprobe e, quando possibile, la decodifica completa; per ZIP testare CRC e contenuti. Non inventare link sandbox.
2. Consegnare il **file singolo principale con nome breve ASCII**, preferibilmente direttamente in /mnt/data senza sottocartelle. Per video e consegne soggette a errori Android fornire **anche ZIP con soltanto i file finali**, separato dai sorgenti; verificare entrambi. Creare copia leggera H.264/AAC solo se serve, senza sostituire l'originale.
3. Non confondere **file verificato localmente**, **collegamento sandbox accessibile sul telefono**, **Artifact GitHub ancora disponibile** e **asset davvero ospitato su Video Library Studio**: sono verifiche distinte. Non si può certificare dal server che l'app ChatGPT risolverà sempre i link; non promettere che la sola ridenominazione o lo ZIP eliminino un errore della piattaforma.
4. Se il download via ChatGPT fallisce, offrire un secondo percorso realmente esistente (ZIP, Artifact GitHub oppure, previa autorizzazione e verifica del caricamento, URL stabile su Video Library Studio/R2). Non pubblicare file privati su un repository pubblico né creare URL immaginari.
5. Segnalare con precisione l'eventuale limite di accesso e non chiamare "consegnato" un file assente o un link non verificato. La preferenza vale per ogni nuova consegna, non soltanto per i video.

Per gli episodi con audio resta disponibile V36 in docs/VIDEO_DOWNLOAD_V36.md e src/video_download_fallback_v36.py. Per i microclip senza audio usare un confezionamento ZIP equivalente senza alterare il video originale.

## Dal soggetto al risultato

1. Registrare richiesta, format, presenza della voce, lingua e obiettivo. Se si
   migliora un Critico, non convertirlo in Cinema per ottenere un'immagine migliore.
2. Studiare il soggetto: fonti, dettagli, storia, fatti documentati e incertezze.
   Un mistero/furto/ritrovamento è una possibilità narrativa, mai un fatto inventato.
3. Formulare una promessa interessante e indicare dove verrà mantenuta. Primo
   fotogramma, titolo e copertina devono corrispondere al contenuto. I checkpoint
   0/1/3/5/7 servono al controllo e non impongono un'introduzione di sette secondi.
4. Selezionare tecniche dal catalogo esistente. Per ogni scelta indicare motivo e
   stato. `trial` significa prova; `approved_option` richiede approvazione registrata.
   La presenza nel catalogo V23 non equivale all'approvazione di Gianluca.
5. Nei narrati sviluppare copione e scene insieme, poi allineare all'audio reale.
   Ogni dettaglio citato deve apparire quando serve. Trama e spiegazioni devono
   restare complete anche quando si accorcia. Finale pertinente, voce naturale.
6. Stimare durata, musica, copertina e lingue social. Per un mix nuovo provare una
   sequenza rappresentativa prima del lotto, se utile; se la produzione è già
   autorizzata non imporre ulteriori conferme operative.
7. Prima del render eseguire preflight; dopo render controllare il file realmente
   prodotto. Non valutare la durata finale di un Critico su una versione senza voce.
8. Consegnare MP4, copertina, post differenziati, fonti/crediti e dati di replica.\n   V36 download: verificare che il file MP4 esista e sia interamente decodificabile;\n   quando si consegna in ChatGPT fornire anche uno ZIP con SOLO il video,\n   separato dal pacchetto sorgenti. Per errori Android preparare a richiesta un\n   MP4 H.264/AAC leggero. Usare `docs/VIDEO_DOWNLOAD_V36.md` e\n   `src/video_download_fallback_v36.py`. Un controllo locale non garantisce che\n   un link sandbox dell'app ChatGPT sia funzionante; per archivio stabile\n   usare Video Library Studio/R2 solo dopo importazione reale dell'asset.
   Salvare lo stato reale, il percorso verificabile e una versione identificabile.
9. Raccogliere correzioni per video e regole riutilizzabili. Una proposta di regola
   non si autoapprova. Metriche reali, quando disponibili, informano esperimenti;
   nessuna previsione certa di viralità o promozione automatica a master approvato.

## Avvio facile per un video o una serie

- Quando Gianluca chiede di creare un video o più video, avviare il menu breve
  `docs/ISTRUZIONI_MENU_VIDEO_NUOVE_CHAT.md`: singolo/serie, idea o prompt, categoria,
  format e stile. Usare i valori già proposti; mostrare le altre impostazioni solo
  se desidera cambiarle.
- Se la richiesta contiene già queste informazioni, precompilare il menu e chiedere
  soltanto le decisioni essenziali mancanti. La frase “usa le impostazioni consigliate
  e procedi” significa che può iniziare il lavoro senza ripetere l'intero riepilogo.
- Per una serie proporre un elenco degli episodi con identità condivisa e regie
  variate. Una correzione del singolo episodio non modifica le impostazioni globali.
- Nel sito il pulsante “Prepara e copia il brief per GPT” prepara testo da incollare
  in una chat. Salvare impostazioni nel browser non equivale a salvarle nel sito o
  in un repository; usare la copia del brief per trasferirle tra dispositivi.
- Queste istruzioni valgono nelle chat che leggono questo repository o il prompt
  dedicato. Una chat nuova e indipendente non può leggere il repository da sola:
  per applicare il comportamento ovunque, inserire il testo del file dedicato nelle
  istruzioni del progetto ChatGPT o nelle istruzioni personalizzate.

## Collegamento effettivo al codice

`video_director_v13.py brief` crea `PROJECT_V13.json` con:
- `editorial_contract`: formato richiesto, presenza della voce, lingua, versione e
  hash delle regole. Un cambio di format richiede un'istruzione dell'utente registrata
  in `format_change_authorization` con `from`, `to`, `approved_by: "user"`, `instruction`.
- `editorial_plan`: ricerca, promessa, conclusione, copertina, durata motivata,
  mix e lingue social. Ogni fonte richiede reference, finding, verification_notes
  e status `reviewed`, da compilare solo dopo controllo reale.

`check` esegue `src/editorial_rules.py` prima della produzione. V15 usa già questo
check; l'adapter V16 lo ripete anche se chiamato direttamente. V23 rispetta il mix
esplicito senza aggiungere altre tecniche. L'adapter Van Gogh accetta la durata
proposta arrotondata al secondo superiore, con limite tecnico minimo di 4 secondi;
la sua regia storica resta specifica di Van Gogh, non un motore universale.
V25 non impone più otto scene, tre tipi di inquadratura o 3–8 tecniche. Restano
obbligatori soggetti, ragioni, fonti, tempi, cue reali e controlli di consegna.

Le schede storiche senza contratto restano leggibili con un avviso: non sono
automaticamente migrate o certificate dalle nuove regole. Prima di riutilizzarle
per nuovi lotti, creare una nuova scheda e trasferire i materiali validi.
Gli script speciali che bypassano V13/V16 richiedono ancora l'applicazione esplicita
del playbook: questo intervento non dimostra che tutti i renderer siano integrati.

## Riferimenti tecnici da conservare

- Formati e capacità: `config/video_formats_v13.json`, `docs/GPT_VIDEO_PLAYBOOK.md`.
- Cinema: preset V6 e identità visiva approvati; Critico: guida serie V2.
- Tecniche: `config/cinematic_techniques_v23.json`; approvazioni in `editorial_rules.json`.
- Voce: WAV, profilo, cache e allineamento originali con hash coerenti.
- Musica e diritti: V20; controllo scene opache: no-ghosting V1.
- Testi social: V28; fascicolo: `docs/VIDEO_LIBRARY_DOSSIER_V1.md`.
- Produzione e ripresa: V15/V16; qualità: V17; apprendimento: V14/V18.

## Limiti dichiarati

La validazione controlla dati e coerenza delle dichiarazioni. Non vede la bellezza,
non prova che una fonte sia vera e non ascolta il parlato al posto della revisione.
Il menu nell'interfaccia richiede la distribuzione del repository per comparire sul
sito live; le istruzioni non attivano pianificazioni, servizi a pagamento o
pubblicazioni social.
Le nuove regole sono applicabili alle nuove chat solo se il progetto viene letto.
\n## V69 — scegliere prima la pellicola che si ricostruisce DAVVERO meglio (28/10/2026)\n\nFeedback dopo V68 Parigi: il livello wow dipende soprattutto dal **fotogramma antico di partenza**. Cercare scansioni 35mm con qualità reale superiore, anche di più di 100 anni, persone/volti abbastanza grandi e leggibili, movimento interessante e crop verticale che preserva i dettagli. La scena del cinema con insegna definita funzionava per architettura; per volti cercare primi piani più vicini. Confrontare almeno tre filmati, più frame ciascuno, e **provare realmente due foto AI generative** prima di scegliere il soggetto. Il risultato fotografico a colori, non il solo raster 4K, deve determinare la scelta. Il progetto V69 include `docs/LA_STORIA_RIVIVE_SCELTA_WOW_V69.md`, `config/storia_rivive_v69.json` e `src/storia_rivive_source_selector_v69.py` con blocchi se non sono verificati fonte PD/CC0 in Italia, provenienza scansione, fotografia generativa effettiva e QA volti/oggetti/scena. NON aumentare arbitrariamente FPS/risoluzione per chiamarlo 4K. No Vidu o GPU a pagamento, no autopubblicazione.\n

## ArtVision V61 — NO TESTE O VISITATORI TAGLIATI NEI VIDEO Museum (29/10/2026)
Regola permanente del proprietario: il visitatore seduto con la testa tagliata da un inquadratura 9:16 nel Cinema Museum Socrate deve scomparire da **TUTTO IL VIDEO**; correggere un'immagine singola NON soddisfa la richiesta. Default Museum: SALA VUOTA; una figura visibile solo se integra durante l'intera camera e motivata. QA obbligatorio in 9:16 su 0.1/1/3/5/7s, camera in/out, ultimo fotogramma e controllo visivo continuo. Se testa/busto/arti significativi troncati, `needs_visual_correction`, non V25. Socrate Cinema Museum V61 è revisione dello stesso slot V60, non altro video nel 4×1. Preservare titolo, dipinto originale e cornice. Riferimento `docs/ARTVISION_MUSEUM_NO_CROPPED_VISITORS_V61_20261029.md`.


## LA STORIA RIVIVE V83.1 — formato 4 classiche + 1 Vidu (29/10/2026)
Nuova variante SENZA eliminare V82: per un filmato social completo, 5 scene storiche realmente diverse; 4 originali d'archivio in movimento B/N → vero frame congelato → foto AI moderna fedele e nitida, più 1 clip Vidu circa 5s, con bianco e nero che prende colore entro circa 1s, poi almeno 3.5–4s di movimento AI reale e coerente. Inserire Vidu dove serve (hook/centro/finale), non sempre slot 3; continuità di cornice visiva, camera/crop, illuminazione, audio continuo e ritmo. Mantenere stacchi editoriali tra inquadrature distinte senza ghosting, non falsificare unico piano-sequenza storico. Identità, volti, oggetti e fonte PD/CC0 obbligatori. Vidu NON deve essere fermo/foto morph; controllo di saturazione e movimento dopo 1s; correzione cromatica V83.1 solo sul movimento Vidu realmente già generato, senza inventare movimento nuovo. MP4 H264/AAC, ZIP, cover, 4 post, QA, GitHub Release verificata e sito soltanto dopo revisione e permessi V55. Sempre consenso per ogni richiesta Vidu a pagamento, limite crediti, saldo prima/dopo, nessun secondo POST in caso di ambiguità. Pilota Paris 1900–1918 SOLO test tecnico tra epoche diverse e non master approvato. Manuale `docs/LA_STORIA_RIVIVE_HYBRID_4PLUS1_V83.md`; contratto `config/storia_rivive_hybrid_4plus1_v83.json`.


### V84/V85 — prove reali, correzioni vincolanti 29/10/2026
Cinque reali clip Q2 Pro Fast `img2video` 5s 720p sono state pagate e scaricate, 16 crediti cad. / 80 crediti totali. **Il loro budget di prova è esaurito: non rigenerare gli stessi test.** La prima seconda e quarta clip avevano associazioni ERRATE foto/prompt, benché i test di codec/movimento fossero passati: preflight semantico umano obbligatorio sul vero contenuto di ciascuna foto. Matrice corretta: V68 `01 NEWSSTAND`, `02 STATION`, `03 CINEMA`, `04 TRAM`; il codice usa una mappatura verificata e abortisce prima del pagamento se diverge. La colorizzazione del primo secondo si fa *sul video Vidu a colori già animato*, tramite una rampa B/N→colore per frame, non propagando crominanza con optical flow; i successivi 4s rimangono VIDEO vero in movimento. Mantieni comunque gli oggetti stabili e non etichettare automaticamente APPROVED un semplice test saturazione/movimento. V85 tecnica: 4 restauri V82 → Vidu 1900 finale, ordinati per ridurre i salti di esposizione, singola musica e link GitHub Release Android; serve ancora QA umano e periodo omogeneo per la produzione editoriale. Riferimento completo `docs/LA_STORIA_RIVIVE_V84_AUDIT_CINQUE_PROVE.md`.


## La Storia Rivive V101 — automazione archivistica sicura ogni 3 ore (30/10/2026)
Per produzione automatica storica leggere `docs/LA_STORIA_RIVIVE_V101_AUTOMAZIONE_3_ORE.md` e `docs/LA_STORIA_RIVIVE_V100_BANDIERA_E_PRODUZIONE.md`. È installato un workflow GitHub Actions isolato `.github/workflows/storia-rivive-v101-auto-3h.yml` (cron 17 ogni 3 ore UTC): sceglie una fonte dalla coda, esamina soltanto filmati autentici, conserva fotogrammi nativi, preordina cinque candidati e disegna un titolo discreto con bandiera storica supportata. **Questa fase produce un dossier di preparazione, NON quattro foto restaurate, NON Vidu, NON un MP4 completo e NON otto video al giorno.** Non chiamare un work order video finito. Richiesti sempre V91/V94/V96/V99 e confronto vero al V98, foto I2I fedeli, un Vidu source-locked reale, revisione artistica e diritti. Nessun acquisto/auto-ricarica/pubblicazione; ArtVision/WOW LAB invariati. Test offline e prova GitHub Actions V101 verificati sul ciclo Beirut 1919. I soggetti con bandiera non verificata mantengono titolo senza bandiera, senza anacronismi.
