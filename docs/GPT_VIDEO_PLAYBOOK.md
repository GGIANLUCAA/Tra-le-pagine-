# Playbook operativo V13 - dal messaggio al filmato

> **Norma editoriale V28:** per TUTTI i nuovi film, i post pubblici raccontano **una storia vera o una riflessione interessante sull'opera**, non le tecniche di editing. Consultare [lo standard editoriale](ARTVISION_EDITORIAL_POST_STANDARD_V28.md), documentare un fatto verificabile e controllare che ogni parola sembri scritta da un appassionato, non dall'AI. Niente "in questo video ho scelto...", hashtag seriali o domande inventate. Attribuzioni/diritti in fondo in modo sobrio; istruzioni nei file privati di produzione.

> **Norma permanente V25 (23/10/2026):** leggere [ARTVISION_CONTRATTO_PERMANENTE_V25.md](ARTVISION_CONTRATTO_PERMANENTE_V25.md) PRIMA dei passi qui sotto. Per ogni NUOVO Cinema senza voce il gate `src/artvision_contract_gate_v25.py` deve passare in preflight e in finale, con copertina serie/inglese, reale regia V6/V23, 0/1/3/5/7 verificati, post Facebook/IG/TikTok/YouTube, diritti, hash/ricetta e istruzioni replica. La scelta estetica resta individuale e va vista/ascoltata, non automatizzata a punteggi. Nessuna consegna di un semplice piano al posto del video.


## Obiettivo

Ogni richiesta di Gianluca parte dal lavoro approvato. Questo file è una procedura
per GPT, non un nuovo servizio di generazione. Il registro dei formati indica cosa
esiste, cosa va preparato e cosa va recuperato. Il planner non chiama API.

Ordine di precedenza: richiesta attuale → regole V12 e preset approvato del formato
→ questa guida → documenti storici. La serie Critico V2 ha una copertina diversa
da Cinema V6; non generalizzare le preferenze tra formati.

## Requisito permanente aggiunto V21: prima impressione e confezione social

Leggere [CREATIVE_DIRECTOR_V21_STANDARD.md](CREATIVE_DIRECTOR_V21_STANDARD.md) per
ogni produzione nuova. Pianificare **PRIMA** del render primo fotogramma,
primi 3/5/7s, copertina dedicata, durata non fissa, scelta musicale emozionale
e diritti Meta/external, descrizioni per Facebook/Instagram/TikTok/YouTube.
Dopo il master eseguire il controllo V21 con `--video`: miniatura candidata e
contact sheet primi sette secondi vengono estratti da veri fotogrammi.
Non alterare il Gold Master approvato e non spacciarli per controllo estetico
automaticamente superato. Il V21 non sostituisce l'Editor V19, i diritti V20 o QA V17.
Se manca il video o il brief è povero, lasciare i campi **da revisionare** senza
inventare contesto, fatti, licenze o metriche. Per musica di Facebook scelta in-app
non riutilizzare la registrazione su social esterni senza diritti specifici.

## 1. Decidi il formato e trova un riferimento

Leggi `config/video_formats_v13.json`. Se è chiaro dal messaggio, scegli senza
domande superflue. Se l'utente indica un video precedente, cerca prima la sua
ricetta e poi i sorgenti. Se manca una scelta non essenziale, usa le preferenze
già approvate e comunicale brevemente. Se due formati cambiano radicalmente il
risultato e l'intento è ambiguo, chiarisci solo quel punto.

```bash
python src/video_director_v13.py formats
python src/video_director_v13.py brief --format libri --topic "Il libro richiesto" --out output/progetto
# Facoltativo: collega una o più ricette esistenti, senza copiare impostazioni alla cieca
python src/video_director_v13.py brief --format artvision_critico --topic "L'opera richiesta" --reference /percorso/VIDEO_RECIPE_V13.json --out output/critico
```

`PROJECT_V13.json` contiene soggetto, preset, asset, scene e revisioni da completare.
`BRIEF_GPT.md` indica le guide e i moduli reali. Nessun filmato viene dichiarato
pronto quando è stata creata soltanto la scheda. Una cartella esistente non viene
sovrascritta. I video storici restano intatti.

## 2. Recupera prima di generare

Per ogni scena cerca: asset approvato → fonte originale pertinente → nuova immagine.
Riunisci i file nella cartella di lavoro, anche tramite copie locali, con percorsi
relativi nella scheda. Per ciascun asset conserva `id`, `file`, `role`, `source`,
`rights` e `credit`. Ruoli: `visual`, `voice`, `music`, `other`.
Non inserire link firmati o segreti. La scheda si può salvare in un archivio
privato; non pubblicare automaticamente materiali nel repository pubblico.

Esempio di voce in `assets`:

```json
{"id":"scene01","file":"assets/scene01.jpg","role":"visual","source":"URL pubblico originale oppure identificativo archivio","rights":"Licenza verificata e riferimento","credit":"Attribuzione richiesta"}
```

Per ogni scena in `scenes` usa `asset_id`, `description`, `reason`. Per i narrati
aggiungi `narration_anchor`, una frase esatta del copione; per la musica senza voce
descrivi il punto musicale. I tempi reali arrivano dopo la sintesi o l'analisi audio.
L'ordine degli anchor deve seguire il copione. La scheda non sostituisce il JSON
specifico richiesto dal renderer: l'agente prepara l'adattamento indicato nel brief.

## 3. Progetta la regia, non una successione casuale

- **Racconti:** definisci personaggi/epoca; ogni scena mostra l'azione narrata.
  Inizio concreto, nessi causa-effetto, finale comprensibile. Niente riflessioni
  generiche al posto della storia. Non obbligare tutti i libri allo stesso effetto.
- **Cinema V6:** scegli opere autentiche e dettagli significativi. Alterna tagli,
  movimenti lievi e pause; preserva colore e nitidezza. Coordinate dedicate per artista.
- **Critico V2:** fatti verificati e interpretazioni distinte; il dettaglio citato
  entra quando viene descritto. Torna all'opera completa. Titolo opera + artista
  in copertina; simboli discreti in chiusura, niente frasi italiane aggiuntive.
- **Controluce:** verifica ciò che potrebbe smentire la lettura iniziale; una
  vicenda centrale; ricostruzioni non spacciate per documenti o riprese autentiche.
- **Musica:** geometrie leggibili, spazio libero, proporzioni corrette; annota
  se la sincronizzazione è su note MIDI, battiti, ampiezza o altra analisi reale.

Controlli editoriali dell'agente: `story`, `visuals`, `rights`. Compila ogni revisione
solo dopo averla svolta, con `status: "passed"` e `notes` concrete. Per film senza
narrazione `story` significa revisione della struttura visiva/musicale. Non sono
tre nuove approvazioni da chiedere a Gianluca.

```bash
python src/video_director_v13.py check --project output/progetto/PROJECT_V13.json
```

Il controllo verifica file, identità asset, anchor e revisioni dichiarate, non la
verità semantica delle immagini. Se il formato è da recuperare, segnala il blocco.
Solo dopo verifica del codice recuperato aggiorna il registro con test e guida.

## 4. Produci con il motore esistente

**Libri** (dalla radice del repository; sostituire EPISODIO):

```bash
python src/episode_v3.py --episode EPISODIO
python src/regia_narrativa_v12.py --episode episodes/EPISODIO
python src/render.py --episode episodes/EPISODIO --engine gemini --effects v4 --out output/EPISODIO
python src/episode_v3.py --episode EPISODIO --out output/EPISODIO --post
```

**Cinema V6:** usa le guide e i director registrati. Il director Van Gogh contiene
uno storyboard specifico: non lanciarlo come generatore universale. Non modificare
il Gold Master per produrre un nuovo artista.

**Critico V2:** `render_series_v2.py --episode ID` accetta le quattro configurazioni
registrate. Per un'opera nuova crea una configurazione e un adattamento testato,
preservando i renderer precedenti. Non inventare un parametro CLI inesistente.

La voce Google ora conserva `VOICE_CACHE_V13.json`, `VOCE.wav`,
`VOICE_PROFILE_V13.json` e `ALLINEAMENTO_VOCE.json`. Il riuso richiede stesso testo
diretto, modello, voce, istruzioni e hash WAV corretto. È locale alla cartella:
tra runner diversi occorre recuperare questi file prima del render. Cambiare il
copione invalida il riuso; modificare solo immagini o tagli non richiede nuova voce.
Un vecchio WAV senza manifest non viene riutilizzato automaticamente.

I tempi stimati sono dichiarati nel report; non considerarli sincronizzazione
esatta. Controllare comunque scene/voce, anche quando l'allineamento ASR riesce.

## 5. Registra e verifica la consegna

Per i libri `--post` salva già `VIDEO_RECIPE_V13.json` e `RIUSO_VIDEO_V13.md`.
Per altri formati, dopo il render:

```bash
python src/video_director_v13.py capture --format artvision_cinema --topic "Artista" --video output/film/film.mp4 --cover output/film/cover.jpg --out output/film --source modules/artvision/APPROVED_PRESET.json --source output/film/STORYBOARD_V6.json
```

Aggiungi `--source` per copione, audio, immagini/ZIP, musica, fonti e rapporti
effettivi. Ogni file è registrato con hash: il riferimento deve essere archiviato
assieme al progetto, non soltanto nominato. Il comando non carica né pubblica.
La ricetta certifica caratteristiche tecniche del file, non il giudizio estetico.

Prima di consegnare: ascolta tutto il parlato, guarda campioni di ogni scena e i
tagli più importanti, verifica inizio/fine, copertina, volume, sorgenti e crediti.
Se la sessione autorizza l'archiviazione sul sito, completa importazione, poster,
metadati e verifica player. Il solo successo della voce o dell'upload non basta.

## Riprendere un lavoro interrotto

Recupera la cartella e la ricetta; verifica gli hash; riusa audio/asset validi;
riparti dalla prima fase incompleta. Non rigenerare ciò che è già approvato.
Leggi i messaggi di errore e distingui blocco tecnico, materiale mancante e revisione.
Non dichiarare attivi modelli che il catalogo identifica come candidati.

## Conservazione del Laboratorio

`integrations/video_library_laboratorio/` conserva il pacchetto del 21/10/2026
con stili, progetti, diario e selezione multipla. Salva riferimenti creativi;
non ricava automaticamente voce, font o regia da un MP4. Per rendere eseguibile
una sua scheda, GPT deve risolvere i riferimenti nelle ricette e preparare il
progetto del formato scelto. Questo aggiornamento non cambia il servizio live.

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


## 6. Music Director V20 e safety prima della pubblicazione (obbligatorio per video nuovi)
Non avviare il render con un brano casuale. Pianificare colonna sonora, struttura emotiva, sincronizzazione e registrare le prove della specifica registrazione, non soltanto della composizione. Leggere [MUSIC_POLICY_V20.md](MUSIC_POLICY_V20.md) e partire dal [manifest V20](../templates/MUSIC_RELEASE_V20.json). Per tutti i formati, oltre al kit V13/V17/V19, produrre una scheda musica e pubblicazione completa e relativo rapporto `src/music_rights_v20.py`. Se si usa audio aggiunto nell'editor Meta distinguere il master senza musica dalla versione finale e verificare la licenza per uso commerciale. Prestare attenzione anche alle opere d'arte, immagini museali e contributo originale del montaggio.

Comandi dall'ambiente del repo:
```bash
python src/music_rights_v20.py --manifest output/progetto/MUSIC_RELEASE_V20.json --out output/progetto/MUSIC_REPORT_V20.json
python -m unittest discover -s tests -p 'test_music_rights_v20.py' -v
```
Su Android usare **Actions → Music Rights V20**; fornisce report scaricabile quando la scheda e' committata. Nessun upload/pubblicazione social: `BLOCKED` o `REVIEW_REQUIRED` fermano la distribuzione; `READY_FOR_MANUAL_PUBLICATION` NON sostituisce verifica dei diritti, ascolto finale o consenso.
