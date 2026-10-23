# Istruzioni operative per GPT e agenti di produzione video

Questo repository è lo studio video di Gianluca. Leggi questo file **prima di
proporre o produrre un filmato**. Non ricostruire il sistema da zero a ogni chat.
Le istruzioni esplicite dell'utente nella sessione hanno precedenza.

## CONTRATTI VINCOLANTI PER OGNI VIDEO NUOVO — V25 + POST V28

**PRIMA di realizzare qualunque filmato, in OGNI nuova chat che accede al repository, leggi in questo ordine:**
1. [Contratto permanente ArtVision V25](docs/ARTVISION_CONTRATTO_PERMANENTE_V25.md): identità visiva invariata, Gold Master Cinema V6, inglese solo per titoli opere / nome artista nella grafica, movimenti calibrati, primi 0/1/3/5/7s, musica e licenze, QA artistico, MP4 e pacchetto finale effettivo.
2. [Standard editoriale post V28](docs/ARTVISION_EDITORIAL_POST_STANDARD_V28.md): la descrizione social è una piccola storia vera, un fatto museale o una lettura umana interessante. **Mai** raccontare in post come è stato montato, riprodotto o generato il video. Vietati slogan artificiali e domande fuori luogo. Ricerca fonti verificabili, attribuzioni e 2–4 hashtag pertinenti. Diversifica tra opere e piattaforme.
3. Preset reale approvato del singolo format, ad esempio `modules/artvision/APPROVED_PRESET.json` e `modules/artvision/IDENTITA_VISIVA_FISSA_V6.json` per Cinema; poi manuali V17/V19/V20/V21/V23.

Il post pubblico NON è un foglio di lavorazione: i testi tecnici stanno solo in `TECNICHE_REGIA.md`, `VIDEO_RECIPE_V13.json` e `ISTRUZIONI_REPLICA.md`. Per ogni episodio salva `POST_EDITORIAL_RESEARCH.json`, `POST_FACEBOOK.txt`, `POST_INSTAGRAM.txt`, `POST_TIKTOK.txt`, `POST_YOUTUBE.txt`. Esegui `python src/artvision_editorial_post_v28.py --episode <chiave_editoriale> --out <cartella_episodio>` solamente dopo aver documentato e verificato la nuova voce di `config/artvision_editorial_v28.json`. Mai fabbricare un testo generico quando una voce manca. Il contratto V25 integra il gate V28 e BLOCCA i post irregolari, ma i test automatici non certificano scrittura umana o veridicità delle fonti; rileggi sempre.

**Non sovrascrivere** master, copertine e post personalizzati, né elementi nascosti/eliminati dall'utente. Anche un video tecnicamente valido richiede valutazione artistica prima di diventare nuovo Gold Master. Nessun servizio a pagamento o pubblicazione social non autorizzata.


## Biblioteca cinematografica permanente V23 — per OGNI NUOVO video

**Prima di decidere movimenti o montaggio**, consultare
`docs/REGIA_CINEMATOGRAFICA_V23.md` e `config/cinematic_techniques_v23.json`.
La libreria propone 117 tecniche, ma ogni episodio sceglie **poche tecniche motivate**
(3–8), non le applica tutte. `src/cinematic_director_v23.py` genera
`CINEMATOGRAPHY_PLAN_V23.json` e `CINEMATOGRAPHY_NOTE_V23.md` insieme al
pacchetto V21: la selezione è integrata automaticamente in
`src/creative_director_v21.py`, non richiede servizi nuovi né nuove API.
Non è un motore di rendering e non certifica l'estetica: il regista deve
vedere il master, ascoltare la voce e motivare dettagli, tagli, musica.
Per Critico privilegiare camera FERMA con pochi gesti lentissimi, per Cinema
rispettare Gold Master e struttura del brano, per libri seguire l'azione
narrata, per Visual Music la sincronizzazione su note reali.
Vietate le oscillazioni a pendolo (feedback Bosch V21): anche un movimento
tecnicamente regolare può provocare nausea. Togliere i moti gratuiti,
non sostituirli con tagli frenetici. Finale contestuale, mai domanda a caso.
Nessuna modifica ai vecchi master e nessuna pubblicazione automatica.

## Standard creativo permanente V21 — per OGNI video NUOVO

**PRIMA di scrivere scene o lanciare un render** leggere
[`docs/CREATIVE_DIRECTOR_V21_STANDARD.md`](docs/CREATIVE_DIRECTOR_V21_STANDARD.md) e
`config/creative_director_v21.json`. Non modificare Cinema V6 Gold Master,
Critico V2, V12 o i vecchi MP4. La richiesta esplicita dell'utente e i preset
già approvati prevalgono sulle proposte del nuovo direttore.

Ogni episodio deve avere una strategia distinta per **primo fotogramma, 0/1/3/5/7
secondi, copertina, durata guidata dal contenuto, musica, copy per piattaforma,
hashtag pertinenti e diritti**. Le immagini si scelgono per pertinenza reale:
ritratti, sculture, figure, opere inquietanti, paesaggi o natura non si alternano
casualmente per attirare clic. Evitare riempitivi, intro decorative e clickbait.
**Preferenza durata aggiornata 23 ottobre 2026 (feedback dopo Thomas Cole):**
per i NUOVI ArtVision Cinema senza voce dare priorità a filmati più concisi, di
norma **45–75 secondi**, spesso vicino a **un minuto**, salvo motivo artistico
specifico per allungare. Non trasformare l'intervallo in un timer identico per
tutti: decidere durata reale da progressione visiva, tensione e struttura del
brano. Togliere dettagli ripetitivi, zoom superflui, pause riempitive e opere
ridondanti anziché accelerare tagli e movimenti. Conservare apertura forte,
camera stabile e finale motivato. Per i format narrati privilegiare comunque
la concisione, senza troncare fatti, spiegazioni o voce. **I master storici e
Cinema V6 Gold Master non vengono accorciati né sovrascritti.**
Non assegnare durata standard a tutti; se il video è già pronto usare ffprobe,
altrimenti stimare in base a scene/voce e dichiarare l'incertezza.
La musica selezionata su Facebook può essere ripetuta se coerente, ma va aggiunta
nell'app dove consentito; NON assumere diritti cross-platform né scaricare tracce
Meta per incorporarle nel master universale.

Eseguire `src/creative_director_v21.py` prima del render come pianificazione,
e dopo il render con `--video` per estrarre prime immagini reali e pacchetto social.
La V16 e Enigma sono collegate direttamente; per gli altri renderer storici
attivare esplicitamente il workflow V21 o lo script prima di qualificare il lavoro.
I file di packaging sono **bozze da revisionare** e non autorizzano pubblicazione.

## Punto di ingresso

1. Leggi `config/video_formats_v13.json` e `docs/GPT_VIDEO_PLAYBOOK.md`.
2. Identifica il formato dall'intento, non dalla sola parola "arte":
   - libro, racconto, fiaba → `libri`;
   - pittore + musica, senza voce → `artvision_cinema`;
   - spiegazione/commento di un'opera → `artvision_critico`;
   - cronaca e attualità → `controluce`;
   - musica e geometrie → `visual_music`; variante luminosa → `hyperlumen`.
3. Usa `python src/video_director_v13.py formats` per verificare le capacità reali.
4. Recupera la ricetta `VIDEO_RECIPE_V13.json` del video di riferimento, se esiste.
   In assenza, cerca copione, WAV, storyboard, configurazioni e sorgenti originali.
   Non dedurre con certezza motore vocale o font dal solo MP4.
5. Prepara il lavoro con `brief --format ... --topic ... --out ...`. Completa i
   file della scheda, poi esegui `check --project .../PROJECT_V13.json`.

## Preferenze già stabilite

- Narrazione italiana Google Gemini, profilo **Gacrux**, salvo richiesta diversa.
  Riutilizza un WAV verificato quando copione e profilo non cambiano. Il cache
  locale di `gemini_voice.py` richiede WAV e manifest coerenti nella stessa cartella.
- **Nessun sottotitolo** nei nuovi filmati: V12 prevale sui vecchi README.
- Libri: prima protagonista, situazione, fatti, scelte e conseguenze; una breve
  riflessione finale. Immagini belle e pertinenti alla frase, personaggi coerenti.
- ArtVision senza parlato: **Cinema V6 Gold Master**, mai V5 per sbaglio.
  Per un nuovo artista prepara focali e storyboard specifici; il workflow Van Gogh
  non diventa universale cambiando il nome. Non modificare la baseline approvata.
- Critico: leggere la guida della **serie V2**, successiva al primo patto visivo.
  Copertina con titolo opera grande + artista; niente frasi decorative italiane.
  Non applicare questa copertina a Cinema V6, che ha una diversa identità approvata.
- Effetti motivati, movimenti armoniosi, niente confusione o ripetizione meccanica.
  Il parallax esistente è una camera su immagini, non animazione AI dei personaggi.
- **Correzione Critico Bosch 23 ottobre 2026 — obbligo prima della consegna:**
  nessun movimento sinusoidale, avanti-indietro o oscillazione della camera;
  alternare inquadrature FERME a pochi push/pull motivati e molto lenti (come
  riferimento prudente 0–1% di zoom nell'intera inquadratura, non al secondo),
  tagli solo quando cambia il dettaglio di cui si parla, dissolvenze sobrie.
  Nel controllo visivo guardare a velocità reale 0/1/3/5/7s e 3 transizioni
  centrali: riconoscibilità del soggetto, stabilità, assenza effetto mal di mare.
  La fine deve CHIUDERE il ragionamento senza inserire domande retoriche fuori
  contesto o richiami artificiali all'engagement. I commenti interpretativi
  personali del critico sono facoltativi, al massimo 1–2 se davvero utili;
  nessuna scritta/commento sovrimpresso, salvo richiesta esplicita. Proteggere
  parlato Google approvato, livello musica, copertina serie e master storico.
  Vedere `modules/artvision_critico/production_series/bosch_director_cut_v22.json`
  per la correzione concreta, non assumere che un test FFprobe dimostri armonia.
- Un solo filmato finale per richiesta; niente due varianti non richieste.
- Pubblicazione e caricamento su un sito pubblico seguono l'autorizzazione della
  sessione. Una richiesta di produzione non implica distribuzione pubblica.
- Lavora autonomamente entro le autorizzazioni già date. I controlli editoriali
  sotto sono lavoro dell'agente, non richieste ripetute di conferma all'utente.

## Produzione e controlli obbligatori dell'agente

1. Ricerca fatti/fonti e materiali. Riusa asset approvati, poi cerca originali
   autorizzati, genera soltanto quelli mancanti. I riferimenti altrui sono esempi
   di regia: non copiare audio, immagini o loghi senza autorizzazione.
2. Scrivi un copione originale e uno storyboard con soggetto/azione per scena.
   Confronta visivamente le immagini con il parlato; registra ciò che hai controllato.
3. Controlla asset e provenienza **prima** di consumare TTS. Non sostituire immagini
   mancanti con disegni di debug in un filmato presentato come finito.
4. Usa i renderer e workflow indicati nel registro. Per moduli branch-only o
   sorgenti mancanti, recupera e verifica il codice; non inventare capacità installate.
5. Leggi `ALLINEAMENTO_VOCE.json`: i tempi `estimated` richiedono revisione della
   sincronizzazione. Anche ASR non dimostra da solo accuratezza perfetta.
6. Controlla con ffprobe video+audio, durata, risoluzione, codec e assenza di
   sottotitoli. Guarda inizio/fine e fotogrammi di ogni scena, ascolta voce/musica,
   correggi tagli, errori di lettura, soggetti fuori quadro e chiusure brusche.
7. Salva `VIDEO_RECIPE_V13.json`: hash di MP4 e materiali, commit, preset, motore
   reale, tempi, controlli e riferimenti. La ricetta non contiene chiavi o URL firmati.
8. Consegna MP4 e copertina reali. Se autorizzata la sincronizzazione, importa nel
   sito e verifica scheda/anteprima/player; non confondere upload, catalogo e playback.

## Stati e onestà sul risultato

- `planned`: scheda pronta; `ready_for_production`: asset/editoria controllati;
  `rendered_needs_review`: file verificato tecnicamente, revisione artistica pendente.
- Non dichiarare "completo" una voce sola, uno storyboard o una run in coda.
- Non dichiarare 4K un 720p/1080p e non garantire approvazione estetica o assenza di ban.
- Se manca qualcosa, recuperalo autonomamente quando possibile; altrimenti indica
  il blocco preciso e il materiale ancora necessario, preservando il lavoro svolto.

## Modifiche al codice

- Conserva Gold Master, vecchi video e motori. Estensioni e versioni nuove sono additive.
- Non attivare modelli candidati, nuovi costi o pubblicazione per risolvere un errore
  senza base nella richiesta. Non esporre credenziali, token o link temporanei.
- Esegui i test pertinenti di `.github/workflows/video-director-v13-check.yml`.
- L'archivio `integrations/video_library_laboratorio/` è una copia dei sorgenti
  consegnati: non dimostra quale versione sia installata sul servizio live.

## Pre-lancio e selezione creativa V18

Prima della prima pubblicazione o per preparare una scorta usare [docs/PRELAUNCH_V18_GUIDA.md](docs/PRELAUNCH_V18_GUIDA.md), `src/prelaunch_editor_v18.py` e `src/creative_memory_v18.py`. Le nuove proposte sono bozze, non video pronti né stime di successo; le preferenze del pannello Android sono locali/esportabili e non alterano la coda. Controllare se esiste già una ricetta V13 completa prima di ricreare scene/voce. Non interpretare gli hash come approvazione artistica e non pubblicare automaticamente. Mantieni le regie approvate e gli altri motori invariati.

## Obiettivo economico e apprendimento

Leggere `docs/STRATEGIA_CREATOR_V13.md` prima di pianificare nuovi contenuti.
Compilare il contesto `business` della scheda: pubblico, promessa, valore originale,
obiettivo, una prova, budget e invito finale. Nessuna crescita o entrata garantita.
Usare `src/creator_metrics_v13.py` sui dati reali disponibili; dati mancanti restano
sconosciuti. Non copiare KPI arbitrari dai repository di marketing.

## Priorità corrente: crescita V14

Leggere `docs/PIANO_CRESCITA_V14.md` e `config/creator_growth_v14.json`.
La crescita dei canali propri precede per ora commissioni, sponsor e proposte
a editori/aziende: non suggerire outreach o servizi come prossima azione.
Preservare i format approvati. Pianificare secondo capacità con
`src/creator_growth_v14.py`; cercare prima nel catalogo e nei riferimenti.
Recuperare le lezioni pertinenti quando disponibili (schema in
`templates/CREATOR_LEARNING_V14.json`); se assenti, dichiarare che mancano.
Una sola variabile per prova; nessuna crescita garantita o pubblicazione implicita.
Il piano V14 prevale sulle priorità commerciali delle guide V1/V13.

## Produzione intensiva V15 — istruzione più recente

Leggere `docs/PRODUZIONE_INTENSIVA_V15.md` e `config/production_v15.json`.
Target: almeno 10 video finiti e controllati al giorno, con lavoro autonomo
dell’agente. Il precedente limite di due video/settimana è superato.
Preparare scorta, lotti paralleli, recupero dei materiali e revisioni dell’agente;
non richiedere conferme per ogni operazione già autorizzata.
Usare `src/production_batch_v15.py` per preflight e registro giornaliero.
Il modulo di coda non è ancora un servizio completo di render continuo: non
dichiarare attivo ciò che resta da integrare. Contare soltanto consegne distinte
verificate, non tentativi, bozze o file duplicati. Distinguere produzione e distribuzione.

## Esecuzione V16

Leggere `docs/PRODUZIONE_AUTONOMA_V16.md`. I pacchetti preparati della coda V15
si eseguono con `src/production_runner_v16.py run`: tre adapter ammessi, processi
isolati, checkpoint e ripresa. Non basta una bozza del copione: recuperare gli asset
e la voce verificata. Rivedere master e kit, poi registrare una revisione con hash
esatti in `queue/reviews_v16/`. Nessuna approvazione ripetuta all’utente per lavoro
già autorizzato. Se mancano asset o capacità, indicare il blocco, non inventare
dieci consegne. I master non revisionati restano nel pacchetto di lavoro.

## Regia qualità aggiuntiva V17 (senza API, non distruttiva)

Leggere [docs/QUALITY_DIRECTOR_V17.md](docs/QUALITY_DIRECTOR_V17.md) e `config/quality_director_v17.json`. Prima della produzione, dove esiste una scheda V13, eseguire `python src/quality_director_v17.py --project PATH/PROJECT_V13.json --out PATH/quality-preflight`: correggere le segnalazioni realmente rilevanti senza snaturare il preset. Per i lavori V16 il report finale V17 viene salvato accanto al master e al kit di revisione. V17 non certifica la bellezza, non verifica automaticamente le opere e non sostituisce la visione/ascolto integrali. Nessuna nuova API né costi obbligatori. Per nuove categorie creare una nuova policy, non modificare Cinema V6 Gold Master, Critico V2 o la voce Google già riuscita.

## Regia editoriale V19 — descrizioni e scelta delle scene (solo ADDITIVA)

Quando un nuovo video è `artvision_cinema` (senza voce) oppure un Reel d'arte breve, leggere [docs/ARTVISION_EDITOR_V19.md](docs/ARTVISION_EDITOR_V19.md), preparare un brief curato e lanciare `python src/artvision_editor_v19.py --brief templates/ARTVISION_JOHN_MARTIN_V19.json --out output/artist/editorial` (sostituendo il brief con quello del nuovo artista). Il modulo genera piano di regia, didascalia Facebook, fonti e avvisi sulle ripetizioni; i testi narrativi si collocano **nella didascalia, non dentro il Cinema V6**. La descrizione è obbligatoria nel kit social, con storia originale e crediti accurati; l'eventuale pubblicazione resta separata. Non dichiarare verificati fatti/diritti o revisione artistica quando il JSON li segnala ancora da controllare. Il modulo non sostituisce Cinema V6 Gold Master, Critico V2, il renderer, V17 o la review.


## Regole musica, diritti e pubblicazione V20 — OBBLIGATORIE per ogni nuovo video
Prima di scegliere la musica leggere [Music Director V20](docs/MUSIC_POLICY_V20.md) e [policy](config/music_policy_v20.json). Vale per Cinema V6, Critico V2, libri, Controluce, Visual Music e HyperLumen: scegliere la musica per il soggetto, la voce e la curva emotiva, NON per rotazione casuale. Il 75/25 tra tracce esterne e audio nativo Meta e' SOLO un esperimento, mai una promessa di vantaggio algoritmico o il permesso di usare tracce non licenziate.

Per ciascun nuovo film creare `MUSIC_RELEASE_V20.json` dal [template](templates/MUSIC_RELEASE_V20.json), con identità traccia, fonte/licenza della **registrazione**, piattaforme consentite, uso commerciale/monetizzazione/ads, attribuzioni e registrazione delle prove dei visual. Dopo render e controllo completo, eseguire `python src/music_rights_v20.py --manifest PATH/MUSIC_RELEASE_V20.json --out PATH/MUSIC_REPORT_V20.json`; dal solo Android si può lanciare [Music Rights V20](.github/workflows/music-rights-v20.yml) in GitHub Actions. `BLOCKED` o `REVIEW_REQUIRED` = nessuna pubblicazione. `READY_FOR_MANUAL_PUBLICATION` indica soltanto checklist compilata, non un accertamento legale o consenso implicito. Il controllo non pubblica né modifica un video. Se si prevede uso commerciale, trattarlo come tale anche prima di monetizzare; musica Meta non significa assenza di controllo video. Conservare le prove e gestire le contestazioni secondo la guida. Regole V6, voce, copertine e divieti sottotitoli rimangono invariati.
