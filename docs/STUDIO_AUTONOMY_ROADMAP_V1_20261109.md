# Studio · autonomia controllata V1 — 9 novembre 2026

## Scopo
Realizzare le sei migliorie accettate dall'utente senza alterare i workflow di produzione attivi, i master approvati, le code owner o il controllo umano artistico. PR preparatoria: **nessun nuovo scheduler, nessun render, nessuna chiamata a pagamento, nessuna pubblicazione**.

## Stato reale
- Le cinque automazioni ChatGPT abilitate proseguono ai rispettivi orari, ma un turno completato **non dimostra** un nuovo MP4.
- PR #234 contiene un selettore ArtVision di **preflight**, non un renderer non-stop. Non replicare il proprietario della coda.
- Esistono già \`src/quality_director_v17.py\` per QA tecnica e \`src/artvision_learning_loop_v1.py\` per lezioni basate su recensioni reali: riusarli, senza simulare visione/ascolto.
- Il pannello V7 raccoglie informazioni e prepara il percorso «Ripara con GPT», ma non modifica autonomamente i workflow né apre da sé nuove chat.

## Primo componente in questa PR
\`src/studio_autonomy_gate_v1.py\` riceve **evidenze da verificare** (checkpoint JSON) e restituisce un'unica azione successiva non distruttiva:
- deduplica un input già completato;
- impedisce spese e pubblicazioni implicite;
- consente di suggerire solo retry **di controlli di sola lettura** per errori transienti noti, massimo due tentativi e soltanto con addebito certamente assente;
- rimanda errori sconosciuti/di render a diagnosi GPT, con testo senza log grezzi o segreti;
- blocca input senza fonte, diritti o hash;
- rifiuta contenuti narrati senza narrazione verificata e pacchetti senza MP4/ZIP/cover/post;
- mantiene separati QA tecnica, revisione artistica legata all'hash MP4 e autorizzazione a pubblicare.

**Non collega ancora la UI al motore, non avvia retry, e non certifica una verifica reale dei file**: il gate valuta gli attestati del checkpoint; esistono già QA reali separati da richiamare tramite il futuro orchestratore.

## Sequenza di integrazione (6 capacità + diario)
1. **Pilota**: integrare il checkpoint nel solo owner della coda (ArtVision PR #234 dopo verifica) e nella coda storia senza duplicazioni. Lock e idempotenza, salto di candidati bloccati, prova su un caso reale prima del live.
2. **Autoriparazione**: classificare errori GitHub e allegare job/step verificati; ripetere automaticamente solo verifiche gratuite di sola lettura. Correzioni di codice mediante PR con CI, senza merge/riavvio automatici su produzione finché non provati.
3. **QA audiovisiva**: riusare Quality Director V17 e i gate dedicati V25, V80/V118, V91/V94/V96/V99; registrare codice errore e timestamp realmente verificati. FFmpeg passato non equivale ad approvazione artistica.
4. **Archivio**: verifica indipendente dei byte MP4, SHA-256 e accessibilità del vero ZIP, cover, diritti e post; sincronizzazione privata solo dopo il completamento. Nessun file fantasma.
5. **Sala regia Android**: stati alimentati dai checkpoint, non presunti dal numero di run. Approva/scarta/revisiona con identità del file e consenso esplicito. Links ChatGPT esistenti conservati solo localmente; fallback diagnosi copiabile.
6. **Social**: prepara bozze separate per piattaforma. Nessuna pubblicazione automatica senza nuova approvazione e verifica diritti.
7. **Diario delle decisioni**: usare \`src/artvision_learning_loop_v1.py\` per autocritica legata al file, più registro versionato di decisioni dell'owner (fonte, motivazione, effetto, formato, video_sha). Non inferire approvazioni o cambiare preset master a posteriori.

## Regole da preservare obbligatoriamente
Leggere \`AGENTS.md\`, \`START_HERE_GPT.md\`, \`docs/REGOLE_ATTIVE.md\`, \`config/editorial_rules.json\` **prima** dei componenti di produzione. Tra le precedenze: V145 (prove non pubbliche), V134 (titoli pubblici puliti), V58/V80/V118/V119 (4×1, scale e cornici autentiche), V82 (sincronia Critico), V91/V94/V96/V99 (Storia fedele), V55 (consegna vera). Non confondere esperimento, master tecnico, Gold, approvazione dell'owner o rilascio.
