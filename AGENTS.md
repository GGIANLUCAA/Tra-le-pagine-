# Studio video di Gianluca — istruzioni attive

Leggere questo file prima di proporre o produrre video.

## ARTVISION V58 — CONTRATTO MADRE 4×1 E BLOCCO PILOTA (29/10/2026)

**Decisione utente vincolante:** leggere `docs/ARTVISION_CONTRATTO_MADRE_4X1_V58_20261029.md`, `docs/ARTVISION_PILOT_FREEZE_20261029.md` e `config/artvision_pilot_lock_v58.json` prima di QUALSIASI nuova produzione ArtVision. Per ogni opera QUATTRO filmati distinti: Critico Standard, Critico Museum, Cinema Standard, Cinema Museum. **Prima completare e approvare tutto Socrate; non avviare nuovi quadri né automatizzare la serie.** Il secondo pilota richiede decisione dell'utente. Il rendering V16 applica il guard V58 prima di generare l'output. No copie, spese non autorizzate, finte review, fake Museum o pubblicazione social.
 Il repository principale è
`GGIANLUCAA/Tra-le-pagine-`. Lavorare dal sistema esistente e preservare i master
approvati. Le istruzioni esplicite della sessione hanno precedenza.

## Punto di riferimento unico (revisione approvata 25/10/2026)

Leggere **docs/REGOLE_ATTIVE.md** e **config/editorial_rules.json**, poi il profilo
in `config/video_formats_v13.json`. Ordine: richiesta esplicita → regole attive →
profilo del format → scelte del video → guide storiche. Le vecchie istruzioni
integrali sono in `docs/history/AGENTS_before_2026-10-25.md` solo come storico.
Le guide V12–V31 restano istruzioni dei moduli: in caso di conflitto prevale la
revisione attiva. Non aggiungere in cima altri blocchi «regola più recente»:
aggiornare la fonte unica con versione, motivo e riferimento dell'approvazione.

## V64 — FOTOGRAFIA REALISTICA E FEDELE, NON FALSO RESTAURO (28/10/2026)

**Feedback esplicito dopo V63:** i ~2s FOTO FERMA devono apparire davvero come fotografie moderne nitide: volti, occhi, pelle, capelli, mani, abiti e ambienti convincenti e corrispondenti al film originale. **V63 NON approvato come master definitivo**: crop originale da film Beirut 720×576→~324×576, DDColor+Real-ESRGAN non ricreano dettagli umani sufficienti. Test con AI generativa ha prodotto volti fotorealistici ma **persone/abiti differenti**, quindi scartare come falso restauro. Priorità: nuova fonte PD/CC0 con **vera scansione HD/2K**, volti già abbastanza grandi nel frame; confronto più fotogrammi reali per estrarre dettaglio verificabile; restauro conservativo, ricostruzione image-to-image con vincoli di identità/struttura e controllo umano. **Il file bello ma infedele è REJECT**, così pure il filtro sfocato 1080p. Nessun nuovo master se non supera `src/storia_rivive_quality_policy_v64.py`: `docs/LA_STORIA_RIVIVE_FOTO_FEDELE_V64.md`; `config/storia_rivive_v64.json`. Preferire scartare scena o cambiare fonte piuttosto che inventare lineamenti. V59,V55 e nessuna spesa GPU/HF/Vidu senza autorizzazione.

## V63 — REGIA PRIMA DEL RESTAURO (28/10/2026)

Dopo V62 (18,2s): meglio 20–28 s quando serve; studiare l'intero filmato e confrontare i ritagli 9:16, fermandosi sui volti, gesti e momenti davvero importanti. Priorità al contenuto, NON a scene panoramiche riempitive. Fotografia dal ritaglio originale prima di Real-ESRGAN, NO downscale distruttivo V62, denoise leggero, DDColor, render 1080×1920, hold 1.8–2.8s secondo importanza. Il 1080p NON è 4K. Un image-to-image generativo davvero fotografico può superare il semplice ESRGAN, ma serve compute, licenze e valutazione fedeltà, non è integrato. `docs/LA_STORIA_RIVIVE_DIREZIONE_FOTOGRAFICA_V63.md`, `config/storia_rivive_v63.json`, `src/storia_rivive_director_cut_v63.py`. Provino a verifica artistica; V59, V55 e 0 crediti Vidu invariati.

## V61 — Regia storica CONGELA IL MOVIMENTO, FOTOGRAFIA AI, POI CUT

Richiesta definitiva confermata dopo 3 esempi reali del 28/10/2026 `43054.mp4`, `43055.mp4`, `43056.mp4`: NON basta la colorizzazione di pellicola in movimento come Beirut V60. La scena mostra **0,9–2 s B/N storico in movimento**, poi resta FERMA in una NUOVA fotografia AI nitida a colori per **0,9–2 s**, ritmata dalla musica; quindi un'altra scena B/N. La fotografia deve essere **rigenerata con image-to-image restoration** dal preciso frame originale; DDColor solo è insufficiente. Preservare persone/pose/oggetti, segnalare ricostruzione dei colori/dettagli. Guide `docs/LA_STORIA_RIVIVE_FOTOGRAMMA_FOTO_AI_V61.md`, config `config/storia_rivive_v61.json`; montatore `src/storia_rivive_photo_freeze_v61.py` richiede FOTO AI già creata e verificata. Nessun MP4 V61 finale senza la FOTO AI reale. Sorgenti solo PD/CC0 (V59), no spese Vidu, no autopubblicazione, pacchetto V55.

## V59 — Originali soltanto PD o CC0; pubblicazione prevista non monetizzata

Nuova decisione del 28/10/2026: per `storia_rivive` usare **solo pellicole realmente di pubblico dominio o CC0**, documentando la pagina del singolo filmato, fonte, paese, data e diritti residuali. Non richiedere commercializzazione del film: l'utente pubblicherà senza monetizzare. Modelli e pesi non commerciali sono candidati se i loro termini consentono la pubblicazione non commerciale; vincoli `research only` restano da verificare e non si considerano automaticamente autorizzati. Vedi `docs/LA_STORIA_RIVIVE_DOMINIO_PUBBLICO_V59.md` e `config/storia_rivive_v59.json`; non cambiare gli altri format, né spendere o autopubblicare.

## V58 — Ricerche open source e montaggi autentici in più scene

Leggere `docs/LA_STORIA_RIVIVE_OPEN_SOURCE_E_MONTAGGIO_V58.md` e `config/storia_rivive_v58.json` per OGNI nuovo reel storico. 4K non obbligatorio: priorità alla qualità percepita. Confrontare 3 fonti, selezionare azioni reali e montare scene pertinenti e diverse senza durata/numero fisso. Usare `src/storia_rivive_montage_v58.py` solo con clip **veramente AI-colorizzate** già presenti e gate V57; non colorizza, non scarica e non chiama Vidu. HAVC wrapper MIT non autorizza i componenti ColorMNet/CMNET2 non-commercial: non dare per scontata la monetizzazione. Eventuale segmento Vidu è ricostruzione AI separatamente etichettata con consenso per clip. Tutto resta sottoposto a V55/V28/V33/V25.

## V57 — Il target storico è colore AI fotorealistico, NON seppia

Correzione dell'utente del 28/10/2026: i tre file `facebook_20261028_142708.mp4`, `142737.mp4`, `142900.mp4` sono i riferimenti estetici; tutti risultano 720×1280, non vero 4K. Un banale viraggio caldo è stato esplicitamente bocciato. Leggere `docs/LA_STORIA_RIVIVE_QUALITA_V57.md` e `config/storia_rivive_quality_v57.json`. Per nuovi video storico-reference-grade applicare colorizzazione AI semantica e temporalmente coerente e reale recupero del dettaglio; non inviare un altro falso "restauro AI". Non confondere ricostruzione generativa con filmato storico autentico. Zero crediti Vidu senza consenso per clip; revisione e pacchetto V55 obbligatori.

## V56 — Nuova categoria La Storia Rivive (28/10/2026)

Per nuovi filmati storici leggere `docs/LA_STORIA_RIVIVE_CONTRATTO_V56.md`, `config/storia_rivive_v56.json` e il profilo `storia_rivive` di `config/video_formats_v13.json`. Usare V55, V28, V33 e V25 senza trasferire automaticamente Museum/V54 4x1 ai filmati d'archivio. Niente falsi documenti, fake colorization, crop facce o spese Vidu non approvate. Nuovo format separato, non modificare i master. Il pilot non è un MP4 pronto solo perché esistono regole.

## V55 — Video sempre recuperabili e primi 7 secondi curati (28/10/2026)

Per ogni nuovo film ArtVision, prima della consegna applicare **docs/REGOLE_ATTIVE.md > ArtVision V55**, `config/artvision_delivery_v55.json` e `docs/VIDEO_LIBRARY_DOSSIER_V1.md`. Nessun video è consegnato completamente se mancano MP4 verificato, JPEG cover nel branding approvato, 4 post social originali V28, dati fonti/diritti/ricetta/QA e ZIP completo verificato. Preparare i veri campioni 0.1/1/3/5/7 secondi del video con `src/artvision_delivery_v55.py pack` e revisionare apertura, primo frame, titolo/artista, emozione e sincronizzazione prima dell'etichetta finale. Non confondere un frame estratto con una revisione artistica.

Sempre tentare il trasferimento nell'archivio privato Video Library Studio immediatamente dopo il filmato pronto secondo i percorsi già autorizzati, poi **verificare separatamente** catalogo, playback, copertina, 4 post e ZIP su sito; il solo import MP4 non prova gli altri elementi. Conservare una consegna ChatGPT/Android con MP4 diretto e ZIP, verificare i percorsi reali e non promettere la durata dei link sandbox. Se qualcosa manca, dichiarare precisamente `delivery_incomplete` / `archive_sync_pending` e non inventare link. **Non pubblicare sui social automaticamente** e non aggirare V25/V44 per rendere il video visibile. Rispettare i master e i post già salvati.

## ArtVision 4x1 e direzione emotiva — 28/10/2026

Per ogni nuova opera ArtVision applicare `docs/ARTVISION_FOUR_VARIANTS_CONTRACT_20261028.md`: dossier unico, quattro varianti (Critico Standard/Museum e Cinema Standard/Museum), direzione emotiva fondata sui dettagli reali, gate artistici e stati separati. Non confondere l'obiettivo di quattro varianti con quattro video effettivamente renderizzati o approvati. Questo integra le regole attive e non autorizza spese o pubblicazioni.


**Esecuzione obbligatoria sui nuovi lotti 4x1:** `python src/video_director_v13.py four-brief --topic "Opera" --artist "Autore" --out output/ARTVISION_4X1_PLAN.json` crea un dossier *vuoto* e quattro schede V13 collegate (NON una ricerca svolta). Dopo averla compilata con dettaglio, fonti, progressione emotiva e quattro storyboard, `python src/video_director_v13.py four-check --plan output/ARTVISION_4X1_PLAN.json` deve passare prima di avviare i renderer. In progetti V13 marcati `serial_mode=artvision_4x1` impostare `artvision_4x1_plan` al dossier unico nella cartella del gruppo madre (`../ARTVISION_4X1_PLAN.json`): anche `check` blocca dossier deboli. Senza scheda compilata non dichiarare il lotto pronto.

**Dopo il render:** per ogni MP4 realmente recuperato e visionato/ascoltato, registrare 2-3 difetti con timecode e azione di correzione nel registro tramite `python src/artvision_learning_loop_v1.py record --review REVIEW.json --video VIDEO.mp4 --ledger output/artvision_learning.jsonl`; consultare `... next --ledger ...` per scegliere una sola modifica per il prossimo ciclo. Il registro verifica file, hash, formato H264/AAC verticale e struttura delle osservazioni; NON vede il video da solo, NON prova emozione e non autorizza pubblicazione o Gold Master. Nessuna recensione inventata se MP4 non visionabile. La modifica alla policy V54 cambia l'hash dei contratti V13: i vecchi progetti devono essere migrati esplicitamente, non aggiornati in silenzio.


## V55 — apertura forte + doppia consegna verificata (28/10/2026)

**Per OGNI nuovo video, qualunque format** applicare `docs/REGOLE_ATTIVE.md > V55` e `docs/VIDEO_LIBRARY_DOSSIER_V1.md`: MP4 originale H264/AAC, copertina JPEG coerente e titolo/artista nei video d'arte, quattro post originali Facebook/Instagram/TikTok/YouTube, fonti/diritti/ricetta, ZIP completo e ZIP MP4-only quando serve ad Android. Testare hash, CRC, ffprobe e decodifica. Non considerare concluso il lavoro soltanto perché il renderer genera un MP4.

**Prima scena cruciale:** pianificare primi 0–3–7 secondi su un dettaglio reale/emozionante, con titolo/artista leggibile sul primo frame, ritmo, voce e musica appropriati. Verificare MP4 reale ai secondi 0/1/3/5/7 e ascoltare l'apertura; il codice non può certificare emozione, leggibilità o buona regia senza vera revisione del file. Per ArtVision utilizzare `src/artvision_delivery_v55.py pack`; `--opening-review` richiede osservazioni riferite all'hash esatto, e i blocchi restano visibili.

**Doppio percorso di consegna:** ChatGPT = allegati che esistono DAVVERO nella sessione (/mnt/data) e link MP4 + ZIP effettivamente verificati localmente; il solo sandbox non prova la disponibilità sul telefono. Studio = importare l'originale nel Video Library Studio privato, verificarne catalogo, riproduzione, vera cover, testi social persistiti e ZIP dinamico del dossier. Non confondere una scheda automatica vuota con i testi autentici salvati. Segnare `delivery_pending`/`archive_sync_pending` finché manca un controllo; niente link inventati. Non pubblicare sui social e non spendere crediti senza approvazione. Import da GitHub e import dalla Libreria ChatGPT sono distinti; la regola non implica disponibilità immediata garantita dai servizi.

## Prima di produrre

1. Identificare l'intento: `libri`, `artvision_cinema`, `artvision_critico`,
   `controluce`, `visual_music`, `hyperlumen`. Per un format nuovo verificare prima
   sorgenti/capacità e creare il profilo; non riciclarne uno cambiando l'etichetta.
2. Un Critico resta narrato. Non togliere voce per compensare crediti o problemi
   tecnici; non considerare una traccia AAC prova che contenga il parlato.
3. Recuperare ricetta, materiali e correzioni dei riferimenti. Non inferire con
   certezza voce, font o motore dal solo MP4. Riutilizzare il lavoro valido.
4. Preparare `brief` con `src/video_director_v13.py`: nuove schede contengono
   `editorial_contract` (richiesta e versione regole) ed `editorial_plan` (ricerca,
   promessa, apertura, conclusione, copertina, durata motivata, mix, lingue social).
5. Compilare fonti e note di verifica reali; esempi dell'utente non sono regole.
   Catalogo tecniche esistente: `config/cinematic_techniques_v23.json`. Una voce
   nel catalogo è disponibile, non necessariamente approvata dall'utente.
6. Eseguire `check` prima del render. Le vecchie schede senza contratto sono
   segnalate come storiche: migrare esplicitamente per nuovi lotti. Non inventare
   approvazioni o riscrivere la richiesta originaria per far passare un controllo.

## Ricerca del pubblico prima del video (regola approvata 25/10/2026)

Per ogni **nuovo** ArtVision Cinema, Critico o Collection leggere e applicare
`docs/ARTVISION_AUDIENCE_RESEARCH_V32.md` e la regola in `docs/REGOLE_ATTIVE.md`.
Se il soggetto è libero, confrontare >=3 candidati con interesse umano,
possibili segnali pubblici documentati (o indisponibilità dichiarata), storia
museale, qualità/diritti, originalità e regia prevista. Conservare il confronto
in `editorial_plan.audience_research` e nei materiali dell'episodio; eseguire
il gate preflight V13/V16 quando presente. **Non fabbricare statistiche**.
Se l'utente ha già scelto l'opera, analizzarne comunque il pubblico senza imporre altre opere.
La regia dev'essere specifica del soggetto, non uno stampino.
Questo non cambia i formati approvati né i master storici.

## Fonti e API per ogni nuovo contenuto — regola permanente V33

Leggere **docs/FILOSOFIA_FONTI_MEDIA_V33.md** e seguire
`config/editorial_rules.json > media_source_priority` **prima di scegliere immagini,
clip, suoni o generare nuovi asset**. Fonte autentica per ArtVision, ricostruzione
esplicitamente distinta in cronaca, immagini originali coerenti per scene di libri,
riuso preferito solo quando davvero pertinente. Pixabay è il nome corretto:
secret primario `PIXABAY`; alias `PIXABAY_API_KEY`.
AI Horde è un prototipo manuale, Gemini Gacrux resta la voce; `OPENROUTER2`
non è un permesso per modelli a pagamento. Nessuna quota aggirata o servizio Premium.
Per i nuovi progetti V13 completare `editorial_plan.media_sourcing` per ogni
asset visuale; il preflight blocca provenienza/diritti/pertinenza non revisionati.
Questa regola non modifica automaticamente motori specializzati che bypassano V13;
i rispettivi agenti devono seguirla esplicitamente.

## Selettore fonti V34 — usare dopo il piano delle scene

Per ogni nuovo contenuto, dopo storyboard/cue e prima di cercare o generare asset, leggere
`docs/SELETTORE_FONTI_V34_GUIDA.md`. Il motore `src/source_selector_v34.py`
applica le priorita V33 per formato, controlla candidati di riuso documentati e
restituisce il percorso scena-per-scena. Lo Studio Ibrido V6 lo include gia nel
piano delle scene. `plan` e offline; `discover` e solo una ricerca manuale
per una scena di ambientazione/B-roll su Openverse/Pixabay, non un crawler.
Un candidato non e un file acquisito, una licenza approvata o un video montato.

## Firma e regia

- Cinema: baseline V6, opere autentiche, senza voce; identità di serie, nome artista
  e credito MUSIC BY; testi previsti in inglese. Copertina dedicata al soggetto.
- Critico: copertina serie V2, voce Google Gacrux, dettagli coordinati alle parole,
  camera ferma alternata a movimenti motivati e molto lenti. Niente oscillazioni,
  pendoli, avanti-indietro o domande finali fuori contesto. Concludere il pensiero.
- Libri: protagonista, situazione, fatti, scelte e conseguenze; immagini coerenti
  con personaggi e frasi, riflessione finale pertinente. Voce naturale Gacrux.
- Controluce: una storia, fonti e attribuzioni verificabili; ricostruzioni
  riconoscibili come tali. Non presentare immagini illustrative come documenti.
- Visual Music/HyperLumen: note/eventi reali e sincronia documentata, forme leggibili,
  niente numerazioni decorative o sovrapposizioni confuse. Recuperare i generatori
  se il registro li indica ancora mancanti; non dichiararli installati.
- Sottotitoli disattivati nei profili correnti. Una variante va autorizzata e
  supportata dal motore; non applicare la preferenza indistintamente ai format futuri.
- Firma di serie coerente, composizione adattabile. Preservare i file storici.
- Durata, scene, effetti, ordine dettaglio/totale e numero di tecniche si motivano
  sul soggetto. Nessuna quota globale, apertura unica o domanda finale obbligatoria.
- Le scelte esplicite del mix in `editorial_plan.techniques` prevalgono sui
  suggerimenti automatici V23. Il planner non esegue automaticamente gli effetti.

## Feedback video libri e regia senza stampino — approvazione 26/10/2026 (V38)

Per **ogni nuovo video** leggere `docs/FEEDBACK_REGIA_NARRATIVA_V38.md` e la policy `config/editorial_rules.json > creative_variation`; se il format e narrativo recuperare anche il riferimento `creative_references.time_machine_20261026`.

L'utente ha giudicato positivamente **La macchina del tempo (H. G. Wells)** per la maggiore ricchezza e varietà delle immagini, pur rilevando possibili miglioramenti. Registrato come **riferimento buono, non GOLD MASTER** e non prova di pubblicazione o diritti verificati. **Non replicare** la durata, il numero di illustrazioni (16 in quell'episodio), la durata delle scene o lo schema di regia. Progettare per storia i beat, il numero di immagini davvero pertinenti, i passaggi visivi e i ritmi, senza quota estetica. Nessun effetto/immagine per riempimento. Preservare la riconoscibilita del brand e la coerenza dei personaggi; il mix di ogni storia e unico.

## No ghosting e apertura museo

Per i video d'arte: un quadro nitido e opaco alla volta. Vietate dissolvenze
incrociate, doppie esposizioni e blend tra scene (`xfade`, `Image.blend`,
`cv2.addWeighted` tra quadri). Tagli puliti, match geometrico senza sovrapposizione,
eventuale passaggio separato al nero. La grafica di identità non è un secondo quadro.

L'ingresso POV museo → quadro è un'opzione apprezzata (feedback 24/10), non
obbligatoria. Movimento unico, lento e progressivo; riproduzione autentica;
sala illustrativa dichiarata come tale oppure fotografia con fonte e diritti.
Non eliminare l'apertura per risolvere il ghosting: correggere il raccordo.
Eseguire `src/artvision_no_ghosting_gate_v1.py` su ricetta e sorgenti; vedere i
fotogrammi reali e i raccordi a velocità normale. Il test non certifica l'estetica.

## Audio, ricerca e consegna

- Verificare fatti, asset e provenienza prima di consumare TTS. La voce resta Google
  Gacrux salvo istruzione diversa. Nessun rimpiazzo robotico automatico.
- Riutilizzare WAV solo con testo, modello, istruzioni e hash coerenti. Leggere
  `ALLINEAMENTO_VOCE.json`; tempi stimati non equivalgono a sincronia verificata.
- Una traccia musicale è la preferenza, ripetibile se pertinente. Cambi motivati,
  volume che protegge il parlato, fine musicale curata. Nessuna promessa algoritmica.
- Consultare V20 e verificare la licenza della registrazione e delle immagini;
  audio Meta non trasferibile automaticamente ad altre piattaforme.
- Evitare primi piani insistiti su nudità artistica e dettagli cruenti, anche in
  copertina. Nessuna garanzia di assenza di claim, ban o successo social.
- V28: post con storia/fatto verificato, pertinenti alla piattaforma e lingua scelta;
  niente note di montaggio al pubblico. Crediti corretti, nessuna domanda artificiale.
- Controllare MP4 effettivo, durata/codec/risoluzione, fotogrammi di tutte le scene,
  primi secondi e raccordi, ascolto integrale di voce/musica. Mai chiamare 4K un Full HD.
- **Consegna Android affidabile:** applicare il protocollo permanente in
  `docs/REGOLE_ATTIVE.md > Consegna file verificabile su Android`: verificare
  l'esistenza del file e, per MP4/ZIP, integrità e decodifica; consegnare
  collegamento diretto a nome breve e ZIP di soli finali quando utile.
  Il controllo locale non certifica l'accessibilità del link sandbox
  nell'app ChatGPT. In caso di "File not found" offrire percorso
  alternativo realmente disponibile, senza inventare URL.
- Salvare ricetta V13 con materiali, hash, preset effettivo, commit e regole usate.
  Consegnare MP4 scaricabile, copertina e kit social. Un render riuscito resta
  `rendered_needs_review` fino alla revisione artistica sul file esatto.
- Prima di registrare/importare in Video Library Studio leggere
  `docs/VIDEO_LIBRARY_DOSSIER_V1.md`. Verificare salvataggio, scheda, anteprima e player.
  Una copia di sorgenti nel repository non dimostra cosa sia installato sul sito live.

## V44 — NIENTE FINTA ANIMAZIONE / MASTER NON REVISIONATI (27/10/2026)

**Incidente reale e feedback dell'utente:** \`docs/VIDEO_INCIDENT_2026-10-27_V44.md\`.
Il video "Macchina del tempo animata" con ruote ruotate e leva deformata in OpenCV
è stato RIFIUTATO. MP4 integro e audio presente NON equivalgono a film pronto.
**Mai ripetere l'errore** di consegnare un video come FINALE dopo una mera analisi
ffprobe/ZIP/decodifica, senza vera autocritica delle azioni e della regia.

Per ogni video creato mediante aggiunta o sostituzione di scene animate:
- Confrontare il medesimo intervallo PRIMA/DOPO e ascoltare le esatte parole.
- Se la richiesta è movimento IA reale, semplici zoom, crop, deformazioni e rotazioni
  locali NON soddisfano il lavoro; non etichettarli come scena IA.
- Verificare se il soggetto FA davvero l'azione richiesta, e controllare testa, mani,
  elementi fisici e continuità a velocità normale. Se il risultato è brutto, SCARTARLO.
- Eseguire \`src/animated_video_release_gate_v44.py\`: preparare sempre manifest
  \`rendered_needs_review\`. Non dichiarare FINALE né pronto per pubblicazione
  senza validazione effettiva, stato \`approved_for_final_delivery\` e hash del video
  revisionato. In mancanza di revisione mostrare solo bozza chiaramente non approvata.
- Nessun retry pagato e nessuna simulazione della revisione con flag inventati.
- Le protezioni sono necessarie ma non certificano automaticamente l'estetica e
  non impediscono da sole che uno script esterno al repository le aggiri.
  Applicare la regola anche a lavori locali, chat e automazioni.

## Crediti video IA a pagamento — blocco preventivo inderogabile

Prima di ogni chiamata a modelli video che consumano crediti leggere e applicare
`docs/REGOLE_ATTIVE.md > Crediti IA video a pagamento`. **L'acquisto
dell'abbonamento e l'inserimento di VIDU_API_KEY non autorizzano generazioni.**
Mai approvare automaticamente una spesa, neanche da 1 centesimo. Preparare
gratuitamente la singola scena con anteprima immagine, frase del copione, azione,
prompt, modello, secondi, costo stimato e motivo narrativo. Chiedere approvazione
dell'esatta scena e preventivo PRIMA del singolo invio, usando il codice del piano.
Se c'e incertezza editoriale, chiedere chiarimenti invece di sprecare crediti.
Nessun retry, batch, job ricorrente o fallback pagato implicito, nemmeno dopo errore.
Un MP4 tecnicamente riuscito NON e automaticamente un video bello o pubblicabile.
L'obiettivo fino a 20 clip/giorno non autorizza alcuna spesa automatica.

## Autonomia e manutenzione

Android soltanto, nessun nuovo costo o servizio senza autorizzazione. Eseguire le
scelte operative già autorizzate senza chiedere conferme ripetitive. Pubblicazione
social, caricamento pubblico e programmazione seguono l'autorizzazione della sessione.
Il vecchio incarico V31 ogni tre ore è documentato nella sua guida: questo
aggiornamento non crea né duplica routine. Un format esplicitamente richiesto
prevale sempre sull'alternanza automatica.

Usare V15/V16 per lotti, checkpoint e ripresa. Contare consegne distinte controllate,
non bozze, copie, anteprime o soli WAV. Il target 10/giorno è un obiettivo, non una
capacità certificata. Budget, costi e quote si misurano; non promettere render continui.
Usare V14/V18 per esperimenti e risultati reali: modificare una variabile importante
alla volta quando si vuole confrontare, nessuna promozione automatica a Gold Master.

Per modifiche al codice eseguire i test pertinenti di
`.github/workflows/video-director-v13-check.yml` e dei moduli modificati.
Non inserire credenziali o link firmati in ricette, log o repository.
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


### ArtVision Museum V61 — visitatori visibili interi, default SALA VUOTA (29/10/2026)
L'utente ha bocciato nel VIDEO Cinema Museum di Socrate un visitatore seduto con TESTA TAGLIATA dal crop verticale. REGOLA PERMANENTE: default scene Museum senza spettatori in primo piano; se persone deliberate, testa e figura rilevante DEVONO essere visibili integralmente in 9:16 per TUTTO il movimento, ingresso/uscita compresi; niente mezze teste ai bordi o nei titoli. Se una figura risulta troncata, rimuoverla dall'intero VIDEO, sostituendo la regione con parete/parquet coerenti, o rifare foto/inquadratura: NON bastano una cover o una singola immagine corretta. Per SOCrate V61: nessun visitatore seduto, preservare titolo, musica, cornice, quadro e camera V57. Prove e regola: `docs/ARTVISION_MUSEUM_NO_CROPPED_VISITORS_V61_20261029.md`. Il Cinema Museum V61 corretto è revisione dello STESSO slot V60, non una quinta variante e non è V25 Gold Master senza revisione umana.
