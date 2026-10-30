# La Storia Rivive — V108 · Mandato operativo, crediti già disponibili e produzione autonoma
Data: 30 ottobre 2026. Fonte: istruzioni esplicite dell'utente nella conversazione del progetto.
Ambito SOLO `La Storia Rivive` (restauro storico). Non alterare ArtVision/Museum 4×1 e WOW LAB.

## Non ripartire da zero
L'utente conferma che Vidu è GIÀ stato usato con successo per generare clip video utilizzando i propri crediti. Nelle prove del 29/10 risultavano cinque clip Vidu da 16 crediti ciascuna (80 crediti complessivi); fra gli esempi una clip «Paris 1900», con saldo letto 4.976 -> 4.960 nella prova. La generazione Vidu non è una funzionalità ipotetica da reinstallare. Distinguere rigorosamente il canale consumer dell'abbonamento dall'API: le prove pregresse non dimostrano che i due saldi siano intercambiabili. Controllare il canale operativo effettivamente riuscito e riusarlo, senza richiedere all'utente le stesse istruzioni e senza domandare di incollare segreti.

## Autorizzazione e limite economico
L'utente vuole SFRUTTARE i crediti già inclusi/disponibili nel suo account e, il 30/10, ha esplicitamente allentato il precedente orientamento a bloccare ogni consumo: evitare sprechi, non vietare per principio le generazioni coperte dal saldo. Questo è un mandato editoriale di uso dei crediti disponibili, NON un mandato ad acquistare nuovi pacchetti, abbonamenti o ad attivare addebiti fuori dal credito esistente.
- Prima di consumare: saldo e quota utilizzabile del CANALE realmente scelto, tariffa specifica, costo massimo, fingerprint immagine/prompt/modello e ledger idempotente.
- Non spendere con saldo/quota non verificati, non fare POST duplicati, non ricaricare o avviare rinnovi/acquisti.
- Il gateway corrente `src/vidu_project_gateway_v1.py` richiede preventivo e consenso specifico per scena. NON inventare l'attestazione `user_approved_this_exact_scene`, né un codice di approvazione. Implementare, testare e sottoporre a revisione una modalità di budget PREPAGATO limitata e verificabile per il mandato di serie, se compatibile con API/abbonamento e sicurezza; fino all'integrazione, rispettare i gate esistenti. La nuova policy non aggira i controlli dei servizi.
- Non confondere con `VIDU_TOKEN` consumer e `VIDUOK` API. Le prove della chat precedenti e i log GitHub vanno consultati prima di presentare blocchi già risolti.

## Obiettivo produttivo
Obiettivo iniziale: una possibilità di ciclo ogni 3 ore (fino a 8 al giorno), **non promessa di 8 finali**. Prima far riuscire 3 video CONSECUTIVI su soggetti diversi al livello almeno del vero San Francisco 1906 V98 accettato. Un ciclo può essere scartato se non ci sono fonti o qualità adeguate.

Ogni episodio: 5 inquadrature archivistiche realmente diverse; 4 sequenze pellicola B/N in movimento -> freeze ESATTAMENTE sul frame dell'originale -> foto I2I davvero moderna, naturale e fedele; 1 sequenza pellicola B/N -> clip Vidu reale e animata ricavata DALLO STESSO fotogramma/fonte. Temporizzazione specifica della scena, 14–35s senza riempitivi; musica continua, titolo discreto, apertura molto coinvolgente, cover, 4 post social, MP4 H264/AAC riproducibile e ZIP Android scaricabile.

## Regia, qualità, storia
- Non generare video random o soggetti scelti a caso: coda editoriale motivata (potenziale emotivo, originalità non inflazionata, disponibilità di film autentico, scene leggibili/HD, licenza e diritti in Italia). Non confondere frame diversi con riprese diverse.
- Escludere prima del costo fonti 480p/crop con volti illeggibili, watermark/timecode invadenti, immagini troppo morbide. Vietati DDColor-only spacciati per I2I fotografico, occhi/mani/oggetti inventati, Vidu da inquadratura diversa, titoli coprenti, colore arancione e sequenze monotone.
- Conservare V98 come golden minimum; obbligatori controlli V91/V94/V96/V99 sui BYTE reali e il QA artistico visivo/audio reale, senza spuntare falsamente approvazioni umane.
- Un workflow verde, un MP4 generato o un contatto-sheet non sono prova di master approvato. Se FAIL: isolare causa, correggere senza consumare crediti inutilmente, ripetere; se irrisolvibile, saltare ciclo.
- Status trasparenti: `source_rejected`, `assets_pending`, `vidu_pending`, `rendered_needs_review`, `technical_pass_review_pending`, `final_approved` (solo con vera revisione), `published` (solo con permesso distinto).
- Pubblicazione social/sito non autorizzata automaticamente. Diritti territoriali da verificare. Non pubblicare dati del saldo/account nei log di repository pubblico.

## Attività tecniche da eseguire, non un nuovo elenco di idee
1. Riconnettere `storia_rivive_autopilot_v101.py` (scouting/scelta) e V102 (frame SHA) alla produzione I2I effettiva, senza auto-persistenza di fonti scadenti.
2. Integrare il gateway Vidu già FUNZIONANTE (controllo saldo, piano, un solo submit legittimo, collect GET) con un budget/prepaid ledger verificato e revisione del fotogramma.
3. Comporre il vero 4+1 dal renderer V98/V86, fare gate V99 in modo non aggirabile, verificare MP4/ZIP/covers/posts/URL.
4. Eseguire tre piloti su soggetti distinti, comparare criticamente con V98, correggere regression e documentare difetti; solo poi collegare la produzione al cron V101.
5. Conservare la cronologia di candidati/clip usate per prevenire duplicati e rotazioni cicliche che si spacciano per episodi nuovi.
6. Documentare per ogni ciclo fonte, importi consumati DA saldo già disponibile, errori, gate, asset effettivi e stato finale. Eseguire test gratuiti prima di qualunque task Vidu.

## Punto di partenza verificato
- `docs/LA_STORIA_RIVIVE_V98_BENCHMARK_ACCETTABILE.md`
- `docs/LA_STORIA_RIVIVE_V99_ANTI_REGRESSIONE.md`
- `docs/LA_STORIA_RIVIVE_V101_AUTOMAZIONE_3_ORE.md`
- `docs/VIDU_CHATGPT_GATEWAY_TUTTE_LE_CHAT_V1.md`
- `docs/LA_STORIA_RIVIVE_CHINA_1928_V107_ESITO_E_GUARDRAIL.md`
- `AGENTS.md`, `docs/REGOLE_ATTIVE.md`.
