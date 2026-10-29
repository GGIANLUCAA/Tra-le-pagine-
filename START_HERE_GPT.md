# Inizia da qui — studio video di Gianluca

Leggere `AGENTS.md`, [regole attive](docs/REGOLE_ATTIVE.md) e
[registro dei format](config/video_formats_v13.json). Questa revisione del 25/10/2026
prevale sui vincoli storici incompatibili. Le istruzioni della sessione restano prioritarie.

## V64 — FOTOGRAFIA REALISTICA E FEDELE, NON FALSO RESTAURO (28/10/2026)

**Feedback esplicito dopo V63:** i ~2s FOTO FERMA devono apparire davvero come fotografie moderne nitide: volti, occhi, pelle, capelli, mani, abiti e ambienti convincenti e corrispondenti al film originale. **V63 NON approvato come master definitivo**: crop originale da film Beirut 720×576→~324×576, DDColor+Real-ESRGAN non ricreano dettagli umani sufficienti. Test con AI generativa ha prodotto volti fotorealistici ma **persone/abiti differenti**, quindi scartare come falso restauro. Priorità: nuova fonte PD/CC0 con **vera scansione HD/2K**, volti già abbastanza grandi nel frame; confronto più fotogrammi reali per estrarre dettaglio verificabile; restauro conservativo, ricostruzione image-to-image con vincoli di identità/struttura e controllo umano. **Il file bello ma infedele è REJECT**, così pure il filtro sfocato 1080p. Nessun nuovo master se non supera `src/storia_rivive_quality_policy_v64.py`: `docs/LA_STORIA_RIVIVE_FOTO_FEDELE_V64.md`; `config/storia_rivive_v64.json`. Preferire scartare scena o cambiare fonte piuttosto che inventare lineamenti. V59,V55 e nessuna spesa GPU/HF/Vidu senza autorizzazione.

## V63 — REGIA PRIMA DEL RESTAURO (28/10/2026)

Dopo V62 (18,2s): meglio 20–28 s quando serve; studiare l'intero filmato e confrontare i ritagli 9:16, fermandosi sui volti, gesti e momenti davvero importanti. Priorità al contenuto, NON a scene panoramiche riempitive. Fotografia dal ritaglio originale prima di Real-ESRGAN, NO downscale distruttivo V62, denoise leggero, DDColor, render 1080×1920, hold 1.8–2.8s secondo importanza. Il 1080p NON è 4K. Un image-to-image generativo davvero fotografico può superare il semplice ESRGAN, ma serve compute, licenze e valutazione fedeltà, non è integrato. `docs/LA_STORIA_RIVIVE_DIREZIONE_FOTOGRAFICA_V63.md`, `config/storia_rivive_v63.json`, `src/storia_rivive_director_cut_v63.py`. Provino a verifica artistica; V59, V55 e 0 crediti Vidu invariati.

## V61 — EFFETTO ESATTO: VIDEO B/N → FOTOGRAFIA AI STATICA COLORATA

La scelta di regia è GIÀ stata chiarita dall'utente: analisi dei tre video `43054.mp4` (2s+2s), `43055.mp4` e `43056.mp4` (~0,9s+0,9s). Per ogni ripresa autentica: muove il B/N, seleziona istante significativo, **blocca movimento**, cambia rapidamente in NUOVA fotografia AI ricostruita con colori/distinzione e nitidezza moderna; lascia ammirare la FOTO per 0,9–2 s, poi cut a NUOVA scena. Non serve Vidu. Non basta DDColor su video, non serve 4K nativo. Vedi `docs/LA_STORIA_RIVIVE_FOTOGRAMMA_FOTO_AI_V61.md` prima di nuove produzioni. Senza il file fotografia AI realmente generato e visto non affermare di avere un risultato conforme.

## V59 — Fonti storiche di pubblico dominio, no monetizzazione

Per `La Storia Rivive` non domandare ancora se vuole monetizzare: la risposta è **no**. Seleziona SOLO veri filmati originali PD o CC0 verificati; il software può essere open-source o limitato a usi non commerciali quando consente effettivamente la produzione e pubblicazione prevista. Non usare tool «solo ricerca» per pubblicare senza verifica specifica. Diritti musica indipendenti, nessuna autopubblicazione, mantenere V55. Guida `docs/LA_STORIA_RIVIVE_DOMINIO_PUBBLICO_V59.md`.

## V58 — Storia senza stampini e senza 4K cosmetico

Quando viene chiesto «un nuovo video storico», fare autonomamente ricerca qualitative di almeno 3 filmati d'archivio, scegliere scene con azioni vere, progettare un gancio forte e un montaggio anche multi-shot quando serve. Percepito nitido a 720p/1080p meglio di falso 4K. Colorizzazione AI reale non seppia, continuità, fonte esatta; montare con FFmpeg e materiali colorizzati già verificati. Vidu solo opzionale e a pagamento previa approvazione per clip. Leggere `docs/LA_STORIA_RIVIVE_OPEN_SOURCE_E_MONTAGGIO_V58.md` e il registro `queue/storia_rivive_candidates_v58.json`; nessuna domanda ripetuta sui preset già decisi.

## La Storia Rivive: riferimento estetico V57

Non chiedere di nuovo che effetto desidera l'utente: **colore vero ben definito, volti realistici, dettaglio moderno**, come i tre MP4 di riferimento; non seppia né sola dissolvenza. Leggere `docs/LA_STORIA_RIVIVE_QUALITA_V57.md` prima di avviare la categoria. Il test gratuito accettabile è una clip 2–3s colorizzata DAVVERO con AI, non un'altra tinta cosmetica. Preservare separazione archivio autentico vs ricostruzione generativa e budget 0 senza autorizzazione.

## La Storia Rivive V56 — avvio senza questionari

Per richieste di video da filmati storici usare il format `storia_rivive` e il suo contratto in `docs/LA_STORIA_RIVIVE_CONTRATTO_V56.md`, con preferenze già impostate: film originale autentico, CC0/diritti controllati, primo frame memorabile, restauro fedele, 0 crediti di default e pacchetto V55 completo. Non chiedere nuovamente le regole o le scelte già note; distinguere sempre pilot progettato, MP4 realmente pronto e archivio realmente sincronizzato.

Quando Gianluca chiede un video o una serie, usa il [menu rapido](docs/ISTRUZIONI_MENU_VIDEO_NUOVE_CHAT.md):
precompila le scelte già presenti nella richiesta, mostra le opzioni consigliate e
lascia modificare le altre senza trasformarle in domande obbligatorie. “Usa le
impostazioni consigliate e procedi” consente di continuare senza un altro giro di
conferme. In una chat indipendente, non presupporre che il repository sia accessibile.

Gianluca può chiedere:

> Crea cinque video Critico d'arte su soggetti diversi. Segui START_HERE_GPT.md,
> studia ogni opera, mantieni la voce Gacrux e proponi un mix motivato per ciascuno.
> Riusa le tecniche approvate e conserva le impostazioni di ogni risultato.

Oppure:

> Migliora questo video mantenendo il format e la voce. Usa l'apertura del video X
> e il ritmo del video Y se sono compatibili. Recupera prima le loro schede.

## Priorità permanente sulle immagini (V33)
## ArtVision 4x1 — guida rapida V54 (28/10/2026)

Per ogni opera scelta per la produzione **seriale ArtVision**, ora sono quattro i video distinti: Critico Standard, Critico Museum, Cinema Standard e Cinema Museum. Il limite precedente di due video V53 è superato. Leggere `docs/REGOLE_ATTIVE.md` e `docs/ARTVISION_FOUR_VARIANTS_CONTRACT_20261028.md`. Un'unica ricerca visiva e storico-artistica deve individuare almeno tre particolari autentici, tensione centrale, progressione emotiva e un momento forte *motivato*, non effetti casuali. Non usare lo stesso stampino di montaggio su opere diverse.

Creare il dossier vuoto con `python src/video_director_v13.py four-brief --topic "Opera" --artist "Autore" --out output/ARTVISION_4X1_PLAN.json`, compilarlo senza inventare verifiche, poi `python src/video_director_v13.py four-check --plan output/ARTVISION_4X1_PLAN.json`. È un controllo strutturale a costo zero, non una verifica estetica. Se il dossier 4x1 è legato al progetto V13 con `serial_mode` e `artvision_4x1_plan`, anche il preflight ordinario lo blocca quando incompleto.

Dopo ogni MP4 realmente visto e ascoltato usare `src/artvision_learning_loop_v1.py` per registrare difetti specifici contro il SHA256 esatto, conservare lezioni e scegliere **una sola sperimentazione misurabile** per la produzione seguente. Niente falsi Gold Master, spese automatiche o autocritiche inventate.



Per **qualsiasi nuovo video/serie** applicare `docs/FILOSOFIA_FONTI_MEDIA_V33.md`
e `config/editorial_rules.json > media_source_priority`:
riusa prima asset approvati **pertinenti**, per arte/cronaca privilegia fonti
autentiche e licenziate; usa Pixabay (`PIXABAY`) o Openverse per stock coerente;
per scene narrative specifiche privilegia illustrazioni originali con personaggi
consistenti (AI Horde sperimentale); non usare Canva Premium per default.
Compila `media_sourcing` per ogni asset prima del check V13. Nessuna spesa
o pubblicazione automatica e niente nuovi secret da richiedere se già disponibili.
Una fonte catalogata non è necessariamente un connettore attivo.

## Selettore scene/fonti V34

Applicare i criteri permanenti V33 tramite `docs/SELETTORE_FONTI_V34_GUIDA.md`.
Dopo lo storyboard e prima dell'acquisizione utilizzare `src/source_selector_v34.py`
per proporre un percorso scena per scena. `plan` offline, ricerca singola
`discover` su Pixabay/Openverse per sole scene pertinenti; non considerare
le 45 API integrate. Il controllo artistico e il render restano separati.

## Riferimento creativo V38 (26/10/2026)

Consultare `docs/FEEDBACK_REGIA_NARRATIVA_V38.md` e `config/editorial_rules.json > creative_variation`. Il filmato **La macchina del tempo** e un riferimento **positivo per ricchezza visuale e varieta** ma non un modello da replicare ne un Gold Master. Ogni storia sceglie durata, immagini, ritmo e regia a partire da beat e necessità della narrazione; non copiare le 16 immagini o circa tre minuti del riferimento. L'identita di serie resta coerente, il montaggio cambia per ogni soggetto.

## Procedura dell'agente

1. Recuperare riferimenti e regole; identificare il format richiesto.
2. Creare una nuova scheda con `brief`; compilarla con ricerca e scelte motivate.
3. Eseguire `check`, risolvere i blocchi, usare i renderer realmente disponibili.
4. Controllare file, parlato e immagini; consegnare MP4, cover, post e dati di replica.
5. Salvare le correzioni con ambito e versione; pubblicare solo se autorizzato.

```bash
python src/video_director_v13.py formats
python src/video_director_v13.py brief --format artvision_critico --topic "Opera scelta" --out output/nuovo_video
python src/video_director_v13.py check --project output/nuovo_video/PROJECT_V13.json
```

Il brief contiene `editorial_contract` e `editorial_plan`. Una scheda vuota è
una bozza: check blocca la produzione finché dati e revisioni sono incompleti.
Il cambio Critico → Cinema non può avvenire silenziosamente. I numeri di scene,
le durate e le tecniche si scelgono per il contenuto, senza quote estetiche fisse.

Per lotti e ripresa consultare V15/V16 nel [playbook](docs/GPT_VIDEO_PLAYBOOK.md).
Android è il mezzo operativo. Nessun nuovo servizio a pagamento viene attivato.
Questo file non è un generatore di video né una funzione installata sul sito live:
serve all'agente con accesso al repository per eseguire il lavoro con i motori esistenti.


## Consegna obbligatoria V55: ChatGPT e Video Library Studio

Per ogni nuovo video (non solo ArtVision) applicare `docs/REGOLE_ATTIVE.md > V55`: MP4 scaricabile in ChatGPT, ZIP alternativo reale, copertina approvata, 4 post social curati e file di fonti/ricetta; importare e verificare lo stesso master e dossier sul sito privato prima di dichiarare la consegna completa. Il sito genera il ZIP completo on demand con link temporaneo; non considerare automaticamente presente il post originale se il sito ha soltanto una scheda generica.

L'apertura (primo frame e primi 1/3/5/7 secondi) decide l'interesse: organizzare un dettaglio significativo, una scoperta e una progressione, con voce/musica adatta e titoli leggibili. Controllare fotogrammi reali e ascoltare tutto l'inizio; niente ingressi museali vuoti, niente stesso stampino. Strumento per ArtVision: `src/artvision_delivery_v55.py`. La verifica tecnica non certifica emozione, la presenza locale non prova la disponibilità del link su Android.

\n## V69 — scegliere prima la pellicola che si ricostruisce DAVVERO meglio (28/10/2026)\n\nFeedback dopo V68 Parigi: il livello wow dipende soprattutto dal **fotogramma antico di partenza**. Cercare scansioni 35mm con qualità reale superiore, anche di più di 100 anni, persone/volti abbastanza grandi e leggibili, movimento interessante e crop verticale che preserva i dettagli. La scena del cinema con insegna definita funzionava per architettura; per volti cercare primi piani più vicini. Confrontare almeno tre filmati, più frame ciascuno, e **provare realmente due foto AI generative** prima di scegliere il soggetto. Il risultato fotografico a colori, non il solo raster 4K, deve determinare la scelta. Il progetto V69 include `docs/LA_STORIA_RIVIVE_SCELTA_WOW_V69.md`, `config/storia_rivive_v69.json` e `src/storia_rivive_source_selector_v69.py` con blocchi se non sono verificati fonte PD/CC0 in Italia, provenienza scansione, fotografia generativa effettiva e QA volti/oggetti/scena. NON aumentare arbitrariamente FPS/risoluzione per chiamarlo 4K. No Vidu o GPU a pagamento, no autopubblicazione.\n
## REGOLA VINCOLANTE V74 — Effetto approvato La Storia Rivive, 29/10/2026
Feedback esplicito: il film Coney Island V73 (colore continuo sul moto) è **BOCCIATO rispetto all'effetto richiesto**, nonostante MP4 tecnicamente valido. Per OGNI nuovo video storico richiesto genericamente, standard obbligatorio = filmato d'epoca realmente in movimento in B/N → STOP sul frame esatto → **fotografia AI image-to-image nitida, colorata, fotorealistica e fedele** → pausa foto statica o micro-movimento fotografico → nuovo vero filmato B/N diverso. Il riferimento è l'esempio utente `43054.mp4` (6 trasformazioni lente da ~2s) e `43056.mp4` (9 trasformazioni rapide da ~0,9s). Non basta colorizzare il filmato in movimento, applicare LUT, seppia, DDColor, geometrical upscale o una dissolvenza. Se la sorgente è sfocata è ammessa ricostruzione più profonda ma plausibile; se è nitida serve fedeltà superiore a volti, abiti, occhi, mani, oggetti e prospettiva. V72 «cinema continuo» è solo opzione sperimentale se esplicitamente richiesta, **non** preset predefinito. V73 va marcato `REJECT_REFERENCE_MISMATCH`. Regole complete: `docs/LA_STORIA_RIVIVE_EFFETTO_REFERENCE_V74.md`. Verifica strutturale: `src/storia_rivive_v74_effect_gate.py`; la verifica artistica resta obbligatoria, non automatica. Nessun credito Vidu senza consenso, MP4+ZIP realmente scaricabili e sito privato verificato senza dichiarazioni false. Mai chiedere all'utente di ripetere le regole o rimontare i suoi video di esempio.

## V75 — Feedback positivo e perfezionamento del formato (29/10/2026)

**L'utente APPROVA l'effetto realizzato in Parigi V74**: ripresa storica autentica in bianco e nero con movimento → blocco dello stesso fotogramma → fotografia AI restaurata a colori, fotorealistica e FERMA → successiva ripresa autentica. Non cambiare questo effetto né reinterpretarlo come colorizzazione in movimento. V74 è ora riferimento positivo per la regia, pur restando migliorabile nella qualità fotografica.

### Due modifiche richieste e approvate
1. **Durata leggermente maggiore rispetto a Parigi V74 (14,4 s).** Impostazione editoriale orientativa per i prossimi episodi: **22–28 secondi**, variabile secondo l'azione e la qualità delle scene, senza allungare artificialmente singoli fotogrammi o riciclare riprese. In genere 4–6 trasformazioni davvero diverse e significative; qualità prevale sul numero. Se esistono solo tre foto eccezionali, non riempire con materiale mediocre. Il video deve iniziare a incuriosire entro i primi 1–3 s.
2. **Un bel titolo iniziale con anno ben leggibile**, e località corretta. Titolo cinematografico/museale elegante, curato nella tipografia e nelle proporzioni, ad esempio `PARIGI · 1898` / `CONEY ISLAND · 1903`, eventuale credito archivio piccolo e discreto. Idealmente appare nei primi **0,8–1,5 s sopra una vera ripresa in movimento** (senza cartello nero fermo o attesa vuota), poi si ritira per lasciare spazio alle scene. Niente «prima/dopo», diciture tecniche o paragrafi; niente voce per questo format. Verificare il periodo esatto sulle fonti, non inventare l'anno.

### Indicazioni per montaggio e QA
- Eseguire il formato **V74 approvato**, il titolo non deve coprire i volti, l'azione o la trasformazione né appesantire la prima inquadratura.
- I blocchi fotografici devono essere abbastanza lunghi da far ammirare i dettagli (preferibilmente 1,5–2,5 s, con flessibilità artistica).
- Allungare l'episodio aggiungendo scene vere, soggetti WOW e fotografie AI approvate, **non** mediante zoom/fermi troppo lunghi o duplicati.
- Esportare e verificare MP4/ZIP scaricabili, titoli, musica originale e controllo artistico. Backup GitHub diretto e sito privato soltanto se effettivamente caricati/verificati.
- Queste sono preferenze permanenti per i **prossimi episodi**. Non dichiarare di aver già rifatto video precedenti senza averlo eseguito.

**Stato:** effetto V74 APPROVATO dall'utente; introduzione/ritmo V75 miglioramenti richiesti per nuove produzioni.


**AGGIORNAMENTO V75 · LA STORIA RIVIVE (29/10/2026):** L'utente ha approvato l'effetto V74 ma vuole video **leggermente più lunghi**, indicativamente 20–26 s quando esistono scene reali sufficienti, e **un titolo iniziale museale elegante con luogo + anno**, ad esempio `PARIGI / 1896 — 1900`, sovrapposto per circa 1,8–2,5 s alla vera pellicola B/N già in movimento. Nel video evitare altri slogan e didascalie: città/anno soltanto, credito archivio al massimo discreto se pertinente; brand e descrizioni in copertina/social. Mantenere sempre il formato approvato **video reale in movimento → freeze esatto → fotografia AI fotorealistica restaurata a colori → fotografia ferma visibile → nuova scena reale**; non allungare con ripetizioni/zoom e non passare alla colorizzazione continua del fallito V73. Le foto AI devono essere più fedeli quando l'originale è nitido e più ricostruttive ma credibili quando è sgranato. Scheda: `docs/LA_STORIA_RIVIVE_DURATA_TITOLO_V75.md`. Esempio V75 Parigi 21,9 s. Consegnare MP4, ZIP, copertina, post, provenance e URL esterno verificato per Android.


### LA STORIA RIVIVE — SOCIAL MUSEUM V76 (29/10/2026)
Applicare alle richieste future le migliorie V76 **senza cambiare** il gold format VIDEO storico in movimento B/N → FREEZE sul medesimo fotogramma → vera fotografia AI image-to-image realistica a colori e FERMA → diversa clip storica. V73 colorizzazione continua è stato scartato. Il titolo iniziale mostra solo CITTÀ/ANNO in elegante serif, sovrapposto alla pellicola in movimento per ~1,5–2s. Apertura con movimento forte e prima foto-reveal idealmente entro 2–3s; durata tipica 20–26s, fotografie 2–4s con tempi variabili, suono musicale originale sincronizzato al reveal, finale forte possibilmente su persone, niente inviti a seguire o fade lunghi, no voci o scritte tecniche in video. Foto AI molto fedeli quando la sorgente è nitida, ricostruzione più profonda ma plausibile se scadente; evitare volti/oggetti inventati. QA strutturale e visivo prima di consegnare, link MP4/ZIP sempre verificati e backup GitHub Release per evitare Library file not found su Android. Non assumere viralità senza dati analytics reali, confrontare soggetti e metriche dopo la pubblicazione. I preset e le regole complete sono `docs/LA_STORIA_RIVIVE_SOCIAL_MUSEUM_V76.md` e `config/storia_rivive_social_museum_v76.json`; prototipo fonte autentica Parigi 1896–1900 (tre foto AI preesistenti, non nuovo restauro) `src/storia_v76_paris_social_museum.py`, workflow `.github/workflows/storia-v76-social-museum.yml`. V75 rimane intatta, Vidu zero crediti, niente autopubblicazione.


### LA STORIA RIVIVE V77 — PERSONE NON DEVONO NASCERE DA OGGETTI (29/10/2026)
Feedback prioritario dell'utente: nelle fotografie AI V76, pezzi d'auto, scale, ringhiere e altri oggetti a volte diventano persone e viceversa. NON ACCETTABILE, anche quando il montaggio è bello.
Per ogni nuova scena storica bloccare conversioni di classe persone-oggetti, alterazioni di sagome/posizioni, persone aggiunte o cancellate e oggetti inventati. Controllare il frame B/N e alcuni frame vicini; compilare un inventario verificato di persone, veicoli, animali, scale, ringhiere e architetture; marcare ROI incerte e conservarle vicine alla fonte.
Sostituire il modello generativo troppo aggressivo (vecchio denoise 0.53) con impostazione conservativa circa 0.22 e massimo 0.27, controllo source-locked, maschere e valutazione della struttura per piccole zone. Non scambiare alta correlazione globale per fedeltà semantica: segnali automatici richiedono verifica visiva reale prima di approvare.
Se non si può ricostruire senza inventare, preservare il dettaglio originale più morbido oppure scartare la scena. REGOLA SUPERIORE ALL'EFFETTO WOW.
Codice: src/storia_rivive_v77_identity_guard.py e src/storia_rivive_v77_safe_photo_generator.py; test: tests/test_storia_rivive_v77_identity_guard.py; istruzioni: docs/LA_STORIA_RIVIVE_REGOLE_IDENTITA_V77.md; config: config/storia_rivive_social_museum_v76.json (identity_integrity).
Gold format video reale B/N -> freeze stesso frame -> foto AI ferma a colori invariato. Nessuna spesa Vidu o API; nessuna pubblicazione di video semanticamente non approvati.


### LA STORIA RIVIVE V78 — RIPRISTINO HD DOPO REGRESSIONE V77 (29/10/2026)
L'utente segnala chiaramente: «Con l'ultima correzione siamo tornati al livello indietro di restauro: le immagini non sono più in HD, le facce non sono ricostruite bene, andava meglio prima». CAUSA ACCERTATA: V77 sovrapponeva ovunque 78% della luminanza sgranata B/N originale, distruggendo il dettaglio fotorealistico generato nella V76, con peggioramento dei volti. CORREZIONE INDISPENSABILE: mantenere V76 come gold baseline di nitidezza, eliminare miscelazione globale e non impostare universalmente denoise 0.22/0.27; applicare protezione della struttura originale SOLO IN ZONE MECCANICHE SOSPETTE delimitate e controllate a mano (scale, ruote, parti d'auto, ringhiere), mai ricoprire globalmente visi e vestiti di sfocatura. Per errori semantici del volto richiedere rigenerazione LOCALE vincolata o altra inquadratura, non degradare l'intera fotografia. Conservare alta risoluzione visiva e correttezza dei soggetti insieme; se impossibile, scartare o tenere in preview. Codice V78: src/storia_v78_hd_selective_identity.py; regole docs/LA_STORIA_RIVIVE_RITORNO_HD_V78.md, configurazione in config/storia_rivive_social_museum_v76.json. V78 Parigi è una PROVA con tre foto già generate V76, non una nuova generazione; rielaborazione solo 4–11% delle zone, 20.47s, H264/AAC, 0 crediti Vidu, non pubblicare senza revisione semantica.


### V79 — VOLTI FOTOGRAFICI MODERNI (29/10/2026)
Utente: «Volti più realistici e dettagliati come foto moderne, si deve vedere bene il volto». Nuova priorità: **scegliere veri film storici con primi piani leggibili, non solo renderizzare alla risoluzione più alta**. Mantieni le stesse persone, stessa espressione e stessa geometria; pelle/occhi/capelli naturali senza allucinare identità, e mai scala/carrozze/auto trasformate in persone. Se il volto archivistico è troppo piccolo, cambiare inquadratura o soggetto invece di inventare dettagli. V77 era troppo sgranata perché miscelava globalmente la luminanza vecchia; usare V78 come riferimento visivo, correzioni mirate e QA locale. Il primo provino V79 Parigi è **solo sharpening selettivo non-generativo su tre fotografie già prodotte**, 20,47s 1080x1920 tramite upscale (non 1080p nativo), non una nuova ricostruzione reale dei volti. Nuovi video puntano a materialmente migliori primi piani. Documento vincolante: docs/LA_STORIA_RIVIVE_VOLTI_FOTOGRAFICI_V79.md. Preset video storico reale B/N -> freeze -> foto AI realistica ferma -> nuova scena invariato. Nessuna spesa Vidu, no autopubblicazione.


### LA STORIA RIVIVE — V79/V80 · VOLTI COME FOTO MODERNE, OGGETTI FEDELI (29/10/2026)
L'utente vuole NUOVI episodi storici REALMENTE FILMATI, con ricostruzione a colori dall'aspetto di fotografia moderna, in particolare viso, pelle, occhi e capelli ben leggibili. Se il volto è troppo sfocato, scegliere frame vicini e inquadrature con viso più grande; non chiamare vera identità storica i dettagli ricostruiti plausibilmente. NON RIPETERE REGRESSIONE V77: nessun 78% di luminanza antica sovrapposta globalmente. Non lasciare che l'AI trasformi oggetti in volti: nel nuovo episodio Ellis Island 1903 (fonte LOC 00694367), il Finegrain aveva creato un viso inesistente su un bagaglio! La V80 lo ripristina dal frame source colorizzato, migliorando SOLO veri volti selezionati con GFPGAN 1.4 CPU gratuito e maschere locali. I controlli globali di somiglianza (0.999) NON garantiscono oggetti corretti. Il video conserva ripresa reale in movimento B/N -> freeze sullo stesso frame -> fotografia AI ferma e realistica -> nuova scena, titolo SOLO luogo + annata, musica, 20–26s quando disponibili. Nessun costo Vidu o auto-pubblicazione. V79 prima versione ha tre foto generate (quarta bloccata dalla quota ZeroGPU): non descriverla come 4 scene. V80 filmato reale ~21.37s, tre scene, GFPGAN e correzione bagaglio, GitHub release di provino. Stesso vincolo di QA artistico: dettagli dei visi ricostruiti non sono la vera identità certificata. Documentazione docs/LA_STORIA_RIVIVE_V80_VOLTI_MODERNI_OGGETTI_FEDELI.md, script src/storia_v80_ellis_face_gfpgan_video.py e .github/workflows/storia-v80-ellis-hd-face-fix.yml. Priorità alla qualità, non consegnare master mediocre.


### V82 · EQUILIBRIO RESTAURO — PRIORITÀ RECENTE (29/10/2026)
Correzione dell'utente: «No devono avere una giusta via di mezzo». La V77 troppo conservativa ha sfocato volti e dettagli; l'illustrazione generativa «Ellis Island 1903» ha inventato visi, intere persone e scene non presenti nella pellicola. ENTRAMBI GLI ESTREMI SONO RESPINTI. I prossimi filmati devono usare un restauro *credibile*, con una nitidezza fotografica moderna ma senza cambiare identità, numero, postura e posizione di persone/oggetti o trasformare scale/pezzi d'auto in persone. Rispettare età, espressione e fisionomia compatibili con i fotogrammi adiacenti; un volto piccolo e sfocato non permette ricostruzioni storicamente sicure. Colore naturale, senza plastic skin o look ritratto di studio. Correzioni MASCHERATE LOCALI dove realmente necessarie, MAI global blur, mai scene nuove inventate per mostrare maggior realismo. Presentare il fotogramma B/N esatto accanto alla foto restaurata per controllo visuale di ciascuna scena; se difettosa scartare o lasciare in preview. Il gold-format resta MOVIMENTO reale B/N → FREEZE dello stesso frame → FOTO a colori ferma → ripresa diversa. Titoli delle città/anni SEMPRE IN INGLESE, eleganti. Regola completa: docs/LA_STORIA_RIVIVE_EQUILIBRIO_RESTAURO_V82.md. Nessun credito Vidu senza consenso.


### LA STORIA RIVIVE — PRIORITÀ V80 VOLTI COME FOTO MODERNE (29/10/2026)
L'utente richiede che il risultato dei fermo-immagine del film storico sembri una FOTOGRAFIA SCATTATA OGGI, con occhi/pelle/capelli/lineamenti chiari, naturali, ricchi di texture e abiti realistici. Non basta colorizzare o aumentare nitidezza; evitare dominanti verde/arancione, graffi e plastica. Selezionare pellicole con volti abbastanza grandi e ben documentati; restauro facciale image-to-image localizzato e gratuito quando possibile, controllo di stessa età/posa/acconciatura/persone, preservazione degli oggetti e confronto con frame adiacenti; se troppo scarso, scartare la scena, MAI chiamare un volto inventato storicamente autentico. I microdettagli prodotti dall'AI sono interpretativi, da descrivere così nei metadati. Vietato regressione V77 che riporta grana sgranata su tutta la foto. Regia e durata V74/V75/V76 invariati. Regole complete docs/LA_STORIA_RIVIVE_VOLTI_FOTO_MODERNE_V80.md. Il pilota V80 su The Kiss 1896 / The Kiss 1900 usa 2 video veri e 3 foto AI, 20.83s, MP4+ZIP, nessun costo Vidu, pubblicazione social/sito NON verificata.


### LA STORIA RIVIVE V82 — RIFERIMENTI VERIFICATI SU MP4 ORIGINALI UTENTE (29/10/2026)
LE TRE clip utente `43054.mp4`, `43055.mp4`, `43056.mp4` sono GOLD REFERENCES DELLO STILE, analizzate frame per frame. Vedi `docs/LA_STORIA_RIVIVE_GOLD_REFERENCE_43054_43055_43056_V82.md`. Esattamente: (A) `43054` 23.73s, 6 cicli circa 2s PELLICOLA ANTICA B/N REALMENTE IN MOVIMENTO → 2s FOTO AI nuova, a colori, FOTOREALISTICA MODERNA FERMA; (B) `43055` 20.23s, `43056` 20.97s, ciascuno 9 cicli rapidi ~0.93s film B/N → ~0.93s FOTO COLORATA MODERNA (montaggio effettivo fino a 16.43s, resto è promo nero da NON riprodurre). TUTTI richiedono un salto ottico grande: volto, occhi, pelle, capelli, abiti, architetture devono sembrare ripresi oggi; non basta DDColor, LUT, semplice upscale o ripresa continua a colori (V73 errore). Preservare camera/posa/numero di persone/oggetti; vietato far diventare scale, veicoli e finestre persone; fonte povera implica microdettagli facciali interpretativi, non identità storicamente certe. Titolo inglese elegante città/anno (PARIS 1899, NEW YORK 1903, VENICE 1896), senza promo finale, musica originale. Ogni correzione deve consegnare MP4 VERO e scaricabile con controllo artistico oltre a tecnico; se non è disponibile dire che manca, non sostituire con rendering immagini. Riferimenti dell'utente usati solo per comprendere l'effetto, MAI riutilizzati come footage nuovo o caricati nel GitHub pubblico.
