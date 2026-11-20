# REPORT OPERATIVO — HANDOFF A GPT
## Regia completa per girare un reel `reel_cromatica_v1`

**Data:** 21 novembre 2026
**Formato:** `reel_cromatica_v1` — clone di linguaggio visivo del reel «Enfermedad cromática»
**Stato del formato:** `candidate_not_registered` — **non** è un formato approvato
**Destinatario:** un agente/GPT che deve produrre un episode dal nulla o riprendere un lavoro interrotto

---

## 0. Come leggere questo documento

Questo report è un **handoff operativo**: contiene tutto ciò che serve per passare dal
soggetto al master, con i comandi, i campi, le soglie e i divieti.

Non è un piano di regia già scritto. Non è un master. Non è un'approvazione artistica.

### 0.1 I tre stati da non confondere

| Stato | Che cos'è | Come si riconosce | Chi lo produce |
|---|---|---|---|
| **PIANO** | scheda JSON di regia: scena per scena, con durate, movimenti, motivazioni, fonti, packaging, 4 post | `templates/REEL_CROMATICA_V1_CANDIDATE.json` compilato; `output/<progetto>/EDITOR_REPORT_V19.json` | GPT, senza spesa |
| **CLIP** | brevi clip video 720×1280 generate a partire dalle opere originali | file `.mp4` per scena in `output/<progetto>/clips/` | GPT, **solo** con autorizzazione di spesa |
| **MASTER** | video verticale montato, con musica, overlay tipografici, copertina | `output/<progetto>/REEL_<ID>.mp4` + `COVER_<ID>.jpg` | montaggio + **revisione artistica umana** |

> **Regola assoluta:** nessun piano viene dichiarato "video pronto" e nessuna clip generata
> viene dichiarata "master". I validatori del repository controllano la **struttura** di un
> piano, non la qualità estetica di un master.

### 0.2 Cosa questo report NON autorizza

- **Non** autorizza spesa su API a pagamento (Vidu, Gemini, ecc.).
- **Non** autorizza pubblicazione automatica: senza revisione artistica lo stato resta `rendered_needs_review`.
- **Non** autorizza la registrazione del formato nelle fonti approvate del progetto.
- **Non** modifica il Gold Master V6, `config/editorial_rules.json` o `config/video_formats_v13.json`.
- **Non** sostituisce il master reale: un piano, per quanto perfetto, non è un filmato.

---

## 1. Scopo e output attesi

### 1.1 Scopo

Produrre un reel verticale breve (22–30 s) nel **linguaggio visivo** del reel di riferimento
«Enfermedad cromática», usando **opere nuove**, **musica nuova**, **montaggio nuovo**.

Principio architetturale non negoziabile:

> **Studiare il campione come linguaggio visivo, ma non copiarne filmato, audio, frame,
> fotografie, timing, ordine delle scene o numero di immagini.**

Il campione è un riferimento di **grammatica**, non un archivio di asset.

### 1.2 Output attesi (in quest'ordine)

1. `templates/REEL_CROMATICA_V1_CANDIDATE.json` compilato (o una copia per il nuovo episode).
2. `output/reel-cromatica-v1/EDITOR_REPORT_V19.json` — esito validatore V19.
3. `output/reel-cromatica-v1/REEL_CROMATICA_V1_GATE.json` — esito gate del profilo.
4. `output/reel-cromatica-v1/POST_FACEBOOK.txt` · `POST_INSTAGRAM.txt` · `POST_TIKTOK.txt` · `POST_YOUTUBE.txt`.
5. `output/<progetto>/MUSIC_RELEASE_V20.json` + `MUSIC_REPORT_V20.json` — diritto musicale.
6. Solo se autorizzati: clip generate, master MP4, copertina JPEG, `SOURCES_AND_RIGHTS.md`, ZIP di consegna.

### 1.3 Limiti dichiarati

- Il validatore tecnico **non certifica** qualità estetica, retention, accuratezza storica o liceità definitiva.
- Il passaggio tecnico **non equivale** ad approvazione artistica.
- I punteggi V32 sono **giudizi editoriali interni**, non misure di mercato.
- I numeri di visualizzazioni osservati negli screenshot del riferimento **non** sono misure di performance.

---

## 2. Precedenza e ordine di lettura

### 2.1 Precedenza delle regole (immutabile)

```
explicit_user_request
  → editorial_rules            (config/editorial_rules.json)
    → format_profile           (config/reel_cromatica_v1.json)
      → episode_choices        (scelte del singolo video)
        → historical_guides    (documenti storici)
```

In pratica: se il profilo del formato e le regole approvate si contraddicono, **vince
`editorial_rules`**. Se l'utente chiede qualcosa di esplicito, vince l'utente — ma mai in
contraddizione con i divieti di diritti e sicurezza.

### 2.2 Ordine di lettura per l'agente

| # | Da leggere | Perché | Quando |
|---|---|---|---|
| 0 | `docs/REGOLE_ATTIVE.md` | regole sempre attive, incluse le revisioni che superano le guide storiche | sempre, per prima cosa |
| 1 | `docs/GPT_VIDEO_PLAYBOOK.md` | procedura generale: recupera prima di generare, non dichiarare pronto ciò che è solo scheda | sempre |
| 2 | `config/reel_cromatica_v1.json` | il profilo machine-readable: è **la** fonte dei parametri | sempre |
| 3 | `docs/REGIA_REEL_CROMATICA_V1_20261121.md` | la prosa della grammatica: packaging, shot, ritmo, divieti | sempre |
| 4 | `docs/ARTVISION_EDITORIAL_POST_STANDARD_V28.md` | standard dei quattro post pubblici | prima di scrivere i post |
| 5 | `docs/ARTVISION_AUDIENCE_RESEARCH_V32.md` | regola del confronto a 3 candidate | prima di scegliere il soggetto |
| 6 | `config/music_policy_v20.json` + `docs/MUSIC_POLICY_V20.md` | diritto musicale | prima di scegliere il brano |
| 7 | `docs/ARTVISION_LINEE_GUIDA_SOCIAL.md` | cosa non spingere in primo piano | prima dei crop |
| 8 | `templates/REEL_CROMATICA_V1_CANDIDATE.json` | **l'episodio di esempio già compilato**: copia di riferimento | prima di compilare |
| 9 | `modules/artvision/REGIA_CINEMA_WOW_V2.md` | analisi del campione 28,17 s (montaggio, non packaging) | solo per capire i principi |
| 10 | `docs/REGIA_REFERENZE_V326_20261112.md` | V326: rubare i principi, mai copiare il prodotto | quando serve un riferimento |

> I documenti storici (V6, V5, V23, V55…) si consultano **per ricerca puntuale**, non come
> istruzioni percorse. Non generalizzare le preferenze di un formato a un altro: la serie
> Critico V2 ha una copertina diversa da Cinema V6, e questo profilo è un terzo formato.

---

## 3. FASE 0 — Preflight

### 3.1 Comandi di preflight (nessuna spesa, nessun render)

```bash
cd /workspace

# 1. Validatore di schema/fonti (V19)
python src/artvision_editor_v19.py \
  --brief templates/REEL_CROMATICA_V1_CANDIDATE.json \
  --out output/reel-cromatica-v1

# 2. Gate strutturale del profilo (V19 + packaging + diritti + V28 + V32)
python src/reel_cromatica_v1_gate.py \
  --brief templates/REEL_CROMATICA_V1_CANDIDATE.json \
  --out output/reel-cromatica-v1

# 3. Suite di test del gate (22 test permanenti)
python -m unittest tests.test_reel_cromatica_v1_gate
```

`--profile` è opzionale nel gate e di default punta a `config/reel_cromatica_v1.json`.

### 3.2 Checklist bloccante di preflight

Il lavoro **non parte** se uno di questi è vero:

- [ ] Il gate restituisce `blocking_issues: []` — **0 blocker**.
- [ ] Il report V19 non elenca blocker.
- [ ] `scenes[0].visual_hook == true` e `scenes[0].on_screen_text` presente (il titolo deve stare nella copertina).
- [ ] La durata totale è in 22–30 s **e** differisce di almeno 1 s dai 28,17 s del campione.
- [ ] `audience_research.candidates` ha almeno 3 candidate complete e non duplicate.
- [ ] `audience_research.selected_work` è una delle opere confrontate.
- [ ] Ogni opera usata nelle scene è registrata in `sources` con `reuse_terms` ammesso.
- [ ] `music` ha titolo, autore, `source_url`, `license_url`.
- [ ] Non esiste nel brief nessuna chiave di sottotitolo (`subtitles`, `subtitle_track`, `srt`, `ass`, `burn_in_subtitles`…): la loro presenza è un blocker.

### 3.3 Cosa non fare in preflight

- Non modificare `config/editorial_rules.json`, `config/video_formats_v13.json`, `modules/artvision/V6_APPROVATA_GOLD_MASTER.md`.
- Non registrare `reel_cromatica_v1` nelle fonti approvate: serve approvazione esplicita dell'utente.
- Non lanciare renderer, API o upload.
- Non sovrascrivere una cartella di output esistente: crea `output/<nome-progetto>/` nuovo.

---

## 4. FASE 1 — Scelta del soggetto (V32)

Il confronto a 3 candidate **precede** lo storyboard. Non è un adempimento burocratico:
è il momento in cui si decide se l'opera regge il formato.

### 4.1 Struttura obbligatoria di `audience_research`

```json
{
  "policy": "docs/ARTVISION_AUDIENCE_RESEARCH_V32.md",
  "selection_mode": "research_selected",
  "explicit_user_instruction": "",
  "selected_work": "<deve essere una delle opere confrontate>",
  "selection_reason": "<perché questa e non le altre>",
  "viewer_interest": "<che cosa incuriosisce davvero>",
  "creative_direction": "<la struttura drammatica che intendi>",
  "signal_limitations": "<cosa NON è stato possibile verificare>",
  "analytics_feedback": "not_yet_published",
  "candidates": [ { ... }, { ... }, { ... } ]
}
```

Ogni candidato richiede **sette campi non vuoti**:

| Campo | Contenuto |
|---|---|
| `artist` | nome dell'artista |
| `work` | opera specifica (non "quadri di mare") |
| `visual_hook` | che cosa si legge nel **primo fotogramma**, anche in miniatura |
| `human_interest` | la persona: cosa rende la storia vera, non generica |
| `historical_anchor` | data, luogo, collezione, fonte primaria |
| `asset_rights_notes` | stato dei diritti e disponibilità reale dei file |
| `comparison_reason` | **perché** è in gara: il suo limite, non solo il suo pregio |

### 4.2 Il segnale di pubblico: due soli esiti ammessi

```json
"audience_signal": {
  "status": "unavailable",
  "reason": "Nessun dato verificato di reach, retention o tendenza su questa opera."
}
```

oppure

```json
"audience_signal": {
  "status": "verified",
  "reference": "<URL o documento>",
  "observation": "<cosa è stato osservato>",
  "checked_on": "YYYY-MM-DD"
}
```

> Se non hai un dato verificato, `unavailable` con il motivo. **Mai** inventare retention,
> reach, visualizzazioni o trend. Il gate blocca un candidato senza dichiarazione di segnale,
> e blocca un `verified` privo di fonte o data.

### 4.3 Il bilanciamento del soggetto (la parte che decide)

Il soggetto deve soddisfare **tutti** questi requisiti insieme, o un episode fallisce:

1. **Alternanza dettaglio → opera intera**: servono almeno 5–8 opere dello stesso artista
   (o dello stesso tema) per non ripetere crop. Una sola tavola non regge 10 inquadrature.
2. **Formula di titolo verificabile**: la specialità dichiarata ("El pintor de las tormentas")
   deve essere un attributo documentato dell'artista.
3. **Larghezza utile ≥ 500 px** dopo il crop verticale 9:16 (vedi §6.4).
4. **Diritti separati**: opera in pubblico dominio ≠ file fotografico libero. Entrambi vanno verificati.
5. **Motivo ricorrente**: deve esserci un leitmotiv (mani, luce, mare, tessuto) che tenga insieme i lavori.

### 4.4 Esempio già valutato (Aivazovsky)

| Candidato | Forza | Limite | Totale stima |
|---|---|---|---:|
| Ivan Aivazovsky — *The Ninth Wave* | corpus ampio, formula 1 naturale, arco tempesta → dopo la tempesta | — | **69** |
| Katsushika Hokusai — *La Grande Onda* | gancio e dettaglio migliori in assoluto | un solo foglio non regge 10 inquadrature senza ricomporre l'opera | 62 |
| J. M. W. Turner — *The Fighting Temeraire* | appoggio museale forte | tema della luce già saturo nel catalogo | 56 |

La stima somma **solo** le dimensioni valutabili; l'interesse osservato del pubblico resta
«non valutabile». Nel piano di esempio tutti e tre i candidati dichiarano
`audience_signal: unavailable` con il motivo esplicito.

---

## 5. FASE 2 — Verifica dei fatti

Il chip «El pintor de las tormentas» è un'**affermazione**, non un'etichetta neutra.
Ogni riga 1 e ogni frase dei post pubblici deve essere verificata su fonte primaria.

### 5.1 Elenco minimo di controlli

- [ ] Data e luogo di nascita e di morte dell'artista.
- [ ] Titolo originale e titolo corrente in lingua di pubblicazione, con anno.
- [ ] Collezione/museo di conservazione e titolo dell'opera.
- [ ] L'affermazione di **specialità** della riga 1 (è letterale e documentata?).
- [ ] Etichetta di paese e bandiera della riga 3 (verificata su fonte primaria).
- [ ] Descrizioni di scene citate nei post (chi, che cosa, dove).

### 5.2 Come si registra

Nel blocco `editorial`:

```json
"fact_sources_checked": true,
"facts_pending": []
```

Se un fatto non è ancora verificato, **non scriverlo come se fosse certo**: si lascia in
`facts_pending` e il flag resta `false`. Il gate emette in quel caso l'avviso
«Fatti del post ancora da verificare» — che è il comportamento corretto, non un difetto.

### 5.3 Attenzione alla lingua

La pagina di riferimento scrive con incoerenze (`Estados unidos`, `Peruano - Estadounidense`).
Nelle didascalie e nei chip si usa la forma **corretta e verificata** del nome.

---

## 6. FASE 3 — Fonti, asset e diritti

### 6.1 Termini di riuso ammessi

```json
"allowed_reuse_terms": ["Public domain", "CC0", "CC BY 4.0", "CC BY-SA 4.0"]
```

Ogni fonte nel registro deve avere `artwork`, `url` (https) e `reuse_terms` **esattamente**
uno di questi valori — il confronto è per stringa, minuscola, senza wildcard.

### 6.2 Separazione dei diritti (il punto che si sbaglia più spesso)

| Livello | Cosa copre | Come lo verifichi |
|---|---|---|
| **Opera** | il diritto d'autore sull'opera (scade) | data dell'opera + status dell'archivio/museo |
| **File fotografico** | il diritto sulla riproduzione fotografica | licenza dichiarata dalla pagina del file |
| **Foto d'artista** | il diritto sul ritratto | va documentato a parte (`artist_photo_rights_required`) |
| **Cultura / proprietà** | restrizioni su beni culturali | controllo `cultural_property_restrictions_check` |

> Un file su Wikimedia in pubblico dominio non autorizza automaticamente l'uso sociale
> in ogni paese. Il registro fonti **non è un clearance legale**: la responsabilità resta
> a chi pubblica.

### 6.3 Il campione non è un asset

Le fonti non devono contenere URL di piattaforme social (`youtube.com`, `instagram.com`,
`tiktok.com`, `facebook.com`, `drive.google.com`): il gate emette avviso, e per i diritti
vale il divieto assoluto di riusare il materiale del riferimento.

### 6.4 Scaricare e verificare una fonte

L'API Wikimedia **richiede un User-Agent**: senza, risponde 403.

```bash
curl -sS -A "ArtVisionResearch/1.0 (editorial planning)" \
  "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|size|extmetadata&titles=File:Hovhannes_Aivazovsky_-_The_Ninth_Wave_-_Google_Art_Project.jpg"
```

Dal risultato si ricavano: URL diretto del file, dimensioni in pixel, autore, data,
e stringa di licenza. Il formato canonico registrato nel brief è:

```json
{
  "artwork": "The Ninth Wave",
  "url": "https://commons.wikimedia.org/wiki/File:....jpg",
  "reuse_terms": "Public domain",
  "attribution": "Aivazovsky, The Ninth Wave (1850), public domain, via Wikimedia Commons",
  "year": "1850",
  "pixel_size": [5090, 3420],
  "usable_width_px_9_16": 1923,
  "used_in_episode": true
}
```

**Calcolo della larghezza utile dopo il crop 9:16:**

```
larghezza utile = larghezza originale × (9 / 16) ÷ altezza originale
```

es. 5090 × (9/16) ÷ 3420 = 1923 px utili. Sotto **500 px** il gate avvisa: il crop
verticale risulterebbe sfocato in uscita 720×1280.

### 6.5 Preparazione fisica degli asset

Dal playbook, per ogni scena cerca nell'ordine: **asset approvato → fonte originale
pertinente → nuova immagine**. Poi:

- raccogli i file in `output/<progetto>/assets/` con **percorsi relativi** nella scheda;
- conserva per ciascun asset: `id`, `file`, `role`, `source`, `rights`, `credit`;
- ruoli ammessi: `visual`, `voice`, `music`, `other`;
- **non** inserire link firmati o segreti nella scheda.

```json
{
  "id": "scene01",
  "file": "assets/the_ninth_wave.jpg",
  "role": "visual",
  "source": "https://commons.wikimedia.org/wiki/File:....jpg",
  "rights": "Public domain, file verificato il 21/11/2026 via Wikimedia Commons API",
  "credit": "Aivazovsky, The Ninth Wave (1850), public domain, via Wikimedia Commons"
}
```

---

## 7. FASE 4 — Musica (prima dello storyboard)

**Il brano si sceglie prima dello storyboard**, non dopo: dalla struttura del brano
(tempi, fraseggi, arrivi) deriva il ritmo dei tagli.

### 7.1 Regole

- **Solo strumentale**, un solo brano, struttura con **evoluzione reale** (non un loop di quattro onde).
- **Mai** riusare l'audio del campione.
- Evitare i brani usati negli ultimi 3 episodi (`modules/artvision/music_library.json`).
- Licenza: CC BY 4.0 o superiore, **con prova della registrazione specifica**:
  la licenza del brano non certifica la registrazione che stai usando.
- Crediti musicali **nel testo pubblico** (riga di crediti in ciascun post).
- Se c'è voce narrante: frasi corte, **mai** sottotitolata, e **non** sostituisce la musica.

### 7.2 Scheda musica V20

```bash
cp templates/MUSIC_RELEASE_V20.json output/<progetto>/MUSIC_RELEASE_V20.json
# compilare
python src/music_rights_v20.py \
  --manifest output/<progetto>/MUSIC_RELEASE_V20.json \
  --out output/<progetto>/MUSIC_REPORT_V20.json
```

Campi da compilare realmente (dal template):

```json
"video": {
  "id": "<ID reale, non REPLACE_ID>",
  "format": "other",
  "title": "<titolo>",
  "originality_statement": "<descrizione del contributo editoriale originale>",
  "visual_rights_evidence": [
    {"name": "<opera>", "proof_url": "<url del file con licenza>"}
  ]
},
"music": {
  "title": "", "artist": "", "origin": "external_licensed",
  "source_url": "", "recording_proof_url": "",
  "license_name": "", "license_url": "", "license_checked_on": "YYYY-MM-DD",
  "allow_commercial": true, "permitted_platforms": ["facebook","instagram","tiktok","youtube"],
  "monetization_allowed": true, "ads_allowed": false,
  "credit_required": true, "credit_text": "🎵 <brano> - <strumento> — <autore> (CC BY 4.0)",
  "music_embedded": true, "rights_holder_claim_status": "cleared",
  "emotional_direction": "", "cue_notes": ""
},
"qa": {
  "music_fit_reviewed": true, "full_watch_listen": true, "audio_mix_reviewed": true,
  "visual_rights_reviewed": true, "caption_ready": true, "originality_reviewed": true
},
"publish_status": "draft_only"
```

> **Due precisazioni sul controllo V20.**
> 1. `video.format` deve essere uno di `artvision_cinema, artvision_enigma, artvision_critico,
>    libri, controluce, visual_music, hyperlumen, other`. `artvision_meraviglia_breve` **non**
>    c'è: per un formato candidato usare `"other"`. Il controllo in quel caso produce una
>    richiesta di revisione, non un blocco.
> 2. `rights_holder_claim_status` deve essere `"cleared"`: se resta `"unchecked"` il report
>    chiede la risoluzione dei claim.

`publish_status` resta `"draft_only"` finché non c'è autorizzazione umana alla pubblicazione.

---

## 8. FASE 5 — Packaging: sistema tipografico e formula di titolo

Confondere i tre sistemi è l'errore più costoso: è ciò che rende un feed incoerente.

### 8.1 Sistema A — chip a tre righe (dominante, ~60% dei reel osservati)

Stack verticale centrato in orizzontale, **appena sopra il centro**.

| Riga | Ruolo | Sfondo | Testo | Corpo | Grassetto |
|---|---|---|---|---|---|
| 1 | titolo / hook | `#000000` | `#FFFFFF` | 34 px | bold |
| 2 | nome artista | `#FFFFFF` | `#000000` | 26 px | regular |
| 3 | paese + bandiera | `#FFFFFF` | `#000000` | 22 px | regular |

Parametri geometrici (dal profilo):

```json
"block_top_percent_of_height": 44,
"row_gap_px": 8,
"padding_px": {"horizontal": 18, "vertical": 8},
"corner_radius_px": 8,
"max_block_width_percent": 82
```

La **riga 1 è sempre presente**: è ciò che rende il reel riconoscibile dalla griglia a
tre colonne senza aprire il post. La riga 3 **richiede l'emoji della bandiera** (il gate
blocca se manca). Font stack riga 1: sans condensata bold.

### 8.2 Sistema B — cartello serif (maestri canonici)

Nessun chip. Testo serif Didone ad alto contrasto (Playfair Display, Bodoni Moda), bianco,
direttamente sul dipinto, mai sul bordo inferiore di testo.

```
William-Adolphe Bouguereau
1825–1905
Francia
```

Corpi: 40 px (nome), 24 px (anni), 24 px (paese). Interlinea 1.3.
Ombra opzionale `0 2px 6px rgba(0,0,0,0.45)`.

Serve quando il nome **è già un'istituzione**: il cartello non aggiunge curiosità, mette in cornice.

### 8.3 Sistema C — domanda / affermazione (serie tematico-filosofiche)

Frase serif bianca in alto (block top 18% dell'altezza, 36 px, spesso con `¿` o virgolette),
sotto-riga sans 20 px su barra nera con padding 6 px.

```
¿La luz no se puede pintar?
Mira el comportamiento de la luz en esta pintura
```

Il **nome dell'artista non compare nei primi secondi**: la domanda è il gancio.

### 8.4 Le cinque formule di titolo

| # | Pattern | Quando | Requisito |
|---|---|---|---|
| 1 | `El/La [professione] de [specialità]` | artista con mestiere riconoscibile | la specialità deve essere **specifica e verificabile**, non un aggettivo generico |
| 2 | `El Artista: [nome] ([paese])` | artista da scoperta | riga 1 = prefisso, riga 2 = nome, riga 3 = paese e bandiera |
| 3 | `Artistas que tienes que conocer` | serie evergreen di scoperta | ripetuta su più reel della serie |
| 4 | `[Tema] en el arte` | collettivo per tema | il tema deve unire opere realmente affini |
| 5 | `¿[affermazione impossibile]?` | serie tematico-filosofica | il nome **non** compare nei primi secondi |

**Esclusività:** una sola formula per reel. Il chip **non** si combina con le formule 3–5
nello stesso momento: o la domanda apre e il nome arriva dopo, o il chip apre col titolo.
Nel reel è ammesso **un solo sistema tipografico** (il gate blocca la sovrapposizione).

### 8.5 Regole tipografiche valide per tutti e tre i sistemi

- Testo **sempre bianco** su fondale scuro o su chip. Mai bianco su dipinto chiaro senza chip.
- **Nessun testo oltre i 3 secondi finali**: la chiusura è l'opera, non il cartello.
- Nessun logo, nessun watermark, nessun handle `@` nel video.
- Bandierine **emoji** (🇩🇪 🇦🇷 🇺🇸 🇮🇪 🇲🇽 🇨🇴 🇵🇪 🇮🇹 🇫🇷 🇻🇪 🇨🇭 🇵🇪🇺🇸).
- Nelle scritte visibili, nelle copertine e nei titoli pubblici **non** usare le parole
  `Standard`, `ArtVision`, `Tra le Pagine`.

### 8.6 Il pacchetto di copertina

- Griglia a **3 colonne**, thumbnail leggibili da soli.
- Il **titolo è dentro il thumbnail**: la riga 1 del chip compare già nel fotogramma di copertina.
- Fondali prevalentemente **scuri/neutri**.
- La copertina **non** è un'immagine dedicata: è un fotogramma del video.
- Nessun bordo, nessuna cornice, nessun collage: **una sola immagine per frame**, niente ghosting.

---

## 9. FASE 6 — Storyboard

### 9.1 Vincoli quantitativi

| Vincolo | Valore | Controllo |
|---|---|---|
| Durata totale | 22–30 s | blocker se fuori range |
| Distanza dal campione (28,17 s) | ≥ 1,0 s | blocker |
| Inquadrature | 5–13 | avviso se fuori |
| Durata minima di uno shot | 1,2 s | soglia di progetto |
| Respiro | almeno uno da 2,5–4,5 s | soglia di progetto |
| Statico massimo in uno short | 6,0 s | avviso V326 `LONG_STATIC_SHORT` |
| Cartello finale | ≤ 2,5 s | avviso `LONG_END_CARD` |
| Shot «flash» | < 1,1 s | avviso `FLASH_SHOT` |
| Quota di flash | ≤ 40% dei tagli | avviso `TOO_MANY_FLASHES` |
| Dettaglio complesso | ≥ 2,0 s (o con `rhythm_justification`) | avviso `COMPLEX_DETAIL_TOO_FAST` |
| Deviazione standard delle durate | ≥ 0,18 s | avviso `MECHANICAL_CADENCE` |
| Tre inquadrature identiche (opera+focale+movimento) | mai | avviso `SAME_SHOT_PATTERN` |
| Tre movimenti consecutivi identici | mai | avviso |

> **Mai** una regola «ogni N secondi». Il ritmo nasce dall'opera e dall'audio reale.
> Le soglie sopra sono **prompt di revisione**, non una ricetta.

### 9.2 Campi obbligatori per ogni scena

```json
{
  "artwork": "<titolo esatto come in sources>",
  "framing": "detail | portrait | medium | full_artwork | architecture | landscape",
  "move": "static | push_in | pull_out | pan_left | pan_right | detail_reveal | match_cut",
  "visual_hook": true,
  "purpose": "<perché questa inquadratura esiste>",
  "start": 0.0,
  "end": 1.9,
  "visual_anchor": "<il dettaglio preciso e visibile>",
  "visual_purpose": "hook | reveal | tension | contrast | human_focus | breath | recovery | payoff",
  "camera_reason": "<ragione registica reale. MAI 'auto_zoom'>",
  "on_screen_text": { "system": "chip", "rows": [ ... ] },
  "source_verified": true,
  "visual_verified": false
}
```

Blocchi dal gate: `visual_anchor` mancante, `camera_reason` mancante o `auto_zoom`,
`framing`/`move` non previsti, opera non presente nel registro fonti, overlay di un sistema
diverso da quello dichiarato, chip senza 3 righe, riga 3 senza bandiera, testo negli ultimi 3 s.

Campi opzionali ma raccomandati: `complex_detail: true` (attiva il controllo dei 2 s),
`rhythm_justification` (serve a giustificare flash, statico lungo o dettaglio complesso breve).

### 9.3 I cinque tipi di shot

| Tipo | Contenuto | Durata | Frequenza | Attenzione |
|---|---|---|---|---|
| **A. Dettaglio d'opera** | crop ravvicinato su luce, mani, tessuto, volto | 1,5–3,0 s | cavallo di battaglia | deve reggere senza muoversi |
| **B. Opera intera** | quadro completo nell'inquadratura | 2,5–4,5 s | **almeno una volta per opera** | non mutilare il dipinto |
| **C. Artista in studio** | l'artista al tavolo con la sua opera o il suo processo | 2–3 s | ogni 2–3 reel | diritti della foto documentati |
| **D. Museo/cornice** | l'opera dentro una cornice reale, con scala | 2–4 s | solo se la serie lo chiede | `architecture` |
| **E. Serie/collettivo** | più opere sullo stesso tema montate per affinità | 3–4,5 s | copertine tematiche | il tema deve unire davvero |

Regola d'oro: **alternare A e B**. Dopo un dettaglio, l'opera intera: mai due dettagli
identici di fila, mai tre inquadrature con la stessa firma opera+focale+movimento.

### 9.4 Le sei inquadrature e i sette movimenti

| `framing` | Significato | Uso tipico |
|---|---|---|
| `detail` | crop ravvicinato su un punto semantico | mani, luce, pennellata |
| `portrait` | figura o soggetto umano in verticale | nave, figura, colonna |
| `medium` | soggetto a media distanza, metà scena | elemento centrale dell'opera |
| `full_artwork` | opera intera leggibile | rivelazione, chiusura |
| `architecture` | spazio, cornice, museo | serie "cornici" |
| `landscape` | mare, cielo, orizzonte, respiro ampio | pausa |

| `move` | Cosa deve fare la camera | Quando usarlo |
|---|---|---|
| `static` | camera ferma: pausa consapevole, opera intera, respiro | rivelazione, respiro, chiusura |
| `push_in` | avvicinamento lento verso un dettaglio o un'ancora semantica | isolare un gesto |
| `pull_out` | allontanamento che rivela l'opera intera o lo spazio | riapertura, chiusura |
| `pan_left` | scorrimento orizzontale verso sinistra su un motivo | seguire una diagonale |
| `pan_right` | scorrimento orizzontale verso destra su un motivo | accompagnare la luce |
| `detail_reveal` | dal dettaglio al senso della scena, con progressione interna | passaggio dettaglio → contesto |
| `match_cut` | passaggio per geometria, direzione, colore o motivo ricorrente | chiusura circolare |

Regole: mai tre movimenti consecutivi identici; `camera_reason` è una **ragione reale**;
nessun movimento meccanico ripetuto su ogni shot.

### 9.5 Regole di crop 9:16

- Usare **una fetta verticale centrata sull'ancora semantica** (albero, vela, onda, mani),
  non un crop cieco al centro.
- **Non tagliare mai**: teste, mani, firme, elementi semantici del soggetto.
- Larghezza utile ≥ 500 px dopo il crop.
- **Nessuna deformazione** di volti, mani o gesti; **nessuna ricostruzione** di opere storiche.
- Non spingere in primo piano dettagli intimi, sangue o nudità pittorica; preferire volti, mani,
  pennellate, simboli, paesaggio, composizione generale.

### 9.6 Il ritmo: costruzione pratica

1. **Primo fotogramma = gancio visivo.** `visual_hook: true` sulla scena 1, con la copertina.
2. **Chiusura sull'opera**, non su un cartello. Se serve un cartello finale, ≤ 2,5 s.
3. **Almeno un respiro** (2,5–4,5 s) nel terzo centrale.
4. **Almeno un taglio in battuta** motivato: su un cambio significativo (mano → mano, luce → luce),
   non a ogni battuta.
5. **Durate disuguali**: è la cosa che distingue un montaggio da una slideshow.
6. **Un solo movimento per volta**; il cambio di movimento è un taglio, non una dissolvenza.
7. **Transizioni**: stacchi netti; poche dissolvenze, solo motivate; mai flash a raffica.

### 9.7 Il piano di esempio, riga per riga

`templates/REEL_CROMATICA_V1_CANDIDATE.json` — «El pintor de las tormentas»:
23,60 s, 10 inquadrature, 8 opere, delta 4,57 s dal campione.

| # | Opera | Framing | Move | s | Dur. | Funzione |
|---|---|---|---|---|---|---|
| 1 | The Ninth Wave | detail | push_in | 0,0–1,9 | 1,9 | hook (mani e panno) |
| 2 | The Ninth Wave | full_artwork | static | 1,9–4,7 | 2,8 | reveal + chip |
| 3 | Gathering Storm | detail | pan_right | 4,7–6,3 | 1,6 | tension (albero e vela) |
| 4 | The Black Sea | detail | push_in | 6,3–8,4 | 2,1 | tension (cresta) |
| 5 | The Rainbow | medium | detail_reveal | 8,4–11,2 | 2,8 | contrast (iride) |
| 6 | Brig Mercury | portrait | pan_left | 11,2–12,8 | 1,6 | human_focus (nave) |
| 7 | Among the Waves | landscape | static | 12,8–16,0 | 3,2 | **respiro** |
| 8 | End of Storm | detail | pan_right | 16,0–17,8 | 1,8 | recovery |
| 9 | Sunset at Sea | full_artwork | pull_out | 17,8–21,5 | 3,7 | payoff (tramonto) |
| 10 | The Ninth Wave | detail | push_in | 21,5–23,6 | 2,1 | **ritorno circolare** sul motivo di apertura |

Da copiare come metodo, non come contenuto: **dettaglio → opera intera → tensione →
respiro → ritorno circolare**; un movimento per volta; durate disuguali; chiusura sull'opera.

---

## 10. FASE 7 — Istruzioni operative per GPT

### 10.1 Due strade tecniche, e il confine fra loro

| Strada | Cosa produce | Costo | Quando |
|---|---|---|---|
| **A. Motion locale** (`ffmpeg zoompan` su immagine fissa) | camera pseudo-3D lenta su un'immagine originale: push/pull/pan | nessuno | opera intera, respiro, chiusura, dettagli non animabili |
| **B. Generativo image-to-video** (Vidu) | clip con **movimento fisico reale** dell'opera (acqua, nuvole, luce) | **API a pagamento** | dettagli animabili: mare, cielo, fiamma, tessuto |

> Nel repository esistono renderer locali con lo stesso vocabolario di movimento
> (`zoompan` con `min(zoom+0.00009,1.035)` per il push, `x=(iw-iw/zoom)*(on/N)` per il pan).
> La **strada A** è sempre disponibile e non costa nulla: è la scelta predefinita.
> La **strada B** richiede autorizzazione di spesa **esplicita** e separata.

### 10.2 Vincoli reali del gateway generativo (`src/vidu_project_gateway_v1.py`)

Non sono suggerimenti: sono controlli del codice, e il gateway **rifiuta** la richiesta se non sono rispettati.

```json
{
  "mode": "generate",
  "request_id": "<id_univoco>",
  "format": "artvision",
  "source": {
    "release_tag": "<tag del rilascio GitHub del repository>",
    "asset_name": "<nome file immagine>",
    "sha256": "<sha256 esatto dell'immagine>",
    "provenance_url": "https://...",
    "subject_reviewed_by_user": true
  },
  "clip": {
    "prompt": "<prompt di movimento fisico, 45–2900 caratteri>",
    "model": "viduq2-pro-fast",
    "resolution": "720p",
    "seconds": 2,
    "off_peak": false,
    "audio": false,
    "color_reveal_first_second": false
  }
}
```

Requisiti non negoziabili:

- `model` = `viduq2-pro-fast`, `resolution` = `720p` — **solo** questo preset verificato.
- `seconds` intero, **2–8** (formato `personale`: 2–10). Uno shot sotto 2 s **non** può
  essere una clip generativa: va realizzato in motion locale o accorpato.
- `audio: false` e `off_peak: false` obbligatori.
- `source.subject_reviewed_by_user: true` obbligatorio: **prima di spendere**, l'immagine
  deve essere stata guardata e riconosciuta dall'utente.
- `source.sha256` deve essere lo SHA esatto dell'immagine.
- `format` deve essere uno di `storia_rivive, artvision, tra_le_pagine, effetti_wow, personale`.
  **`reel_cromatica_v1` non è ammesso**: il profilo non è registrato. Usare `artvision` è una
  decisione che va dichiarata all'utente, non una scorciatoia da prendere in silenzio.

> **Punto di decisione, non di esecuzione:** se serve generare clip, il formato del gateway e
> la spesa vanno autorizzati esplicitamente. Senza autorizzazione si resta sulla strada A e
> si dichiara il limite.

### 10.3 Anatomia del prompt (struttura obbligatoria)

Il prompt del gateway deve descrivere **movimento fisico**, non stile né mood generico.
Cinque blocchi, in quest'ordine:

```
[SOGGETTO IN MOVIMENTO] che [azione fisica osservabile] [direzione/velocità] .
[AMBIENTE] con [elementi secondari] che [movimento secondario] .
[LUCE] che [comportamento della luce] .
[INQUADRATURA] [dettaglio / campo medio / opera intera] , [inquadratura stabile] .
[VINCOLI] nessuna deformazione , nessun testo , nessun logo , colori fedeli all'originale .
```

Esempio reale, shot 7 (`Among the Waves`, respiro, statico):

```
L'onda lunga si alza lentamente e si abbassa senza spezzarsi, la schiuma si muove
lungo la cresta e scompare nei cavi. Il cielo resta immobile sopra il mare vuoto.
La luce radente resta costante sulla superficie dell'acqua. Campo medio del mare,
inquadratura stabile e verticale, nessuna deformazione, nessun testo, nessun logo,
colori fedeli all'originale.
```

Esempio reale, shot 4 (`The Black Sea`, dettaglio, push_in):

```
La cresta verde si solleva lentamente e l'acqua nerastra scende verso il basso,
le micro-onde scorrono verso la camera. La luce resta cupa e fredda sulla superficie.
Avvicinamento lentissimo sulla cresta, crop ravvicinato verticale, nessuna deformazione,
nessun testo, nessun logo, colori fedeli all'originale.
```

### 10.4 Prompt per ciascun movimento (banca di riferimento)

| `move` | Prompt |
|---|---|
| `static` | «L'inquadratura resta immobile. [elemento] respira appena: [micro-movimento]. [luce] costante. Nessun movimento di camera, nessuna deformazione, nessun testo.» |
| `push_in` | «Avvicinamento lentissimo su [ancora]. [elemento] si muove appena. La luce [comportamento]. Nessuna deformazione, colori fedeli.» |
| `pull_out` | «Allontanamento lento che rivela [opera intera / spazio]. [elemento] si muove appena. Nessuna deformazione, colori fedeli.» |
| `pan_left` | «Scorrimento orizzontale verso sinistra su [motivo]. [motivo] scorre nel quadro. Nessuna deformazione, colori fedeli.» |
| `pan_right` | «Scorrimento orizzontale verso destra su [motivo]. [motivo] scorre nel quadro. Nessuna deformazione, colori fedeli.» |
| `detail_reveal` | «Partendo da [dettaglio], la vista si apre lentamente fino a [contesto]. [elemento] rivela la sua forma. Nessuna deformazione, colori fedeli.» |
| `match_cut` | «[Forma/direzione/colore ricorrente] si sposta dal bordo sinistro al bordo destro, [altro elemento] occupa lo stesso punto dell'inquadratura. Nessuna deformazione, colori fedeli.» |

### 10.5 Prompt per ciascun tipo di shot

| Tipo | Istruzione aggiuntiva |
|---|---|
| **A. Dettaglio** | «Crop ravvicinato su [mano / luce / tessuto / pennellata]. La profondità del dettaglio deve restare nitida, nessuna ricostruzione, nessun dettaglio inventato.» |
| **B. Opera intera** | «L'opera è interamente visibile nel quadro verticale, bordo per bordo, senza ritagliare figure o firme.» |
| **C. Artista in studio** | «L'artista [gesto reale descritto dalla fonte]. Movimento minimo, naturale, senza gestualità amplificata.» |
| **D. Museo/cornice** | «La cornice reale e il muro restano fermi; solo l'illuminazione ambientale cambia appena. Scala e prospettiva non si alterano.» |
| **E. Collettivo** | «Le opere restano immobili, una dopo l'altra nello stesso punto del quadro, senza deformarsi.» |

### 10.6 Conservazione integrale dell'opera (blocchi negativi)

In ogni prompt, e in ogni revisione del risultato:

- **mai** deformare volti, mani, gesti o proporzioni;
- **mai** ricostruire, completare o "colorare" parti mancanti di un'opera storica;
- **mai** aggiungere elementi non presenti nell'originale (persone, imbarcazioni, animali, nuvole);
- **mai** alterare la palette: il cromatismo dell'opera è il contenuto;
- **mai** generare testo, loghi, watermark o firme all'interno del frame;
- **mai** sovrapporre due immagini: **una sola immagine per frame**, niente ghosting, niente alpha;
- **mai** tagliare teste, mani, firme o elementi semantici.

### 10.7 Assemblaggio della timeline

1. Un file per scena, 720×1280, 30 fps, senza audio.
2. Estrazione dei segmenti secondo `start`/`end` del brief: `ffmpeg -ss <start> -t <durata>`.
3. **Stacchi netti** di default; dissolvenze solo motivate e mai con sovrapposizione alpha.
4. **Nessun testo** negli ultimi 3 s; chiusura sull'opera.
5. Copertina: **un fotogramma reale** del video (non un'immagine dedicata) in JPEG.
6. Assemblamento finale: MP4 reale, H.264 + AAC, `-movflags +faststart`.

### 10.8 Mix audio

- Musica a **−14/−15 LUFS integrati**, true peak ≤ **−1 dBTP**.
- Nessun clipping; normalizzazione a due passate.
- Voce (se presente): frasi corte, mix sotto la musica, **mai** sottotitolata.
- Verifica finale:

```bash
python src/controllo_master_v5.py \
  --video output/<progetto>/REEL_<ID>.mp4 \
  --out output/<progetto>/CONTROLLO_AUDIO_VIDEO_V5.json
```

---

## 11. FASE 8 — QA

### 11.1 Controlli automatici

| Controllo | Comando | Soglia |
|---|---|---|
| Schema, fonti, movimenti | `python src/artvision_editor_v19.py --brief <brief> --out <out>` | 0 blocker |
| Profilo, packaging, diritti, V28, V32 | `python src/reel_cromatica_v1_gate.py --brief <brief> --out <out>` | 0 blocker |
| Ritmo e pattern | `src/director_reference_v326.py → analyze_scenes` (richiamato da entrambi) | 0 blocker |
| Coda nera reale | `src/director_reference_v326.py → inspect_black_tail` | nessuna coda nera non voluta |
| Loudness/peak/durata | `python src/controllo_master_v5.py --video <mp4> --out <json>` | −16±3 LU, ≤ −1 dBTP |
| Diritti musicali | `python src/music_rights_v20.py --manifest <m> --out <r>` | 0 blocker, 0 claim aperto |
| Test del gate | `python -m unittest tests.test_reel_cromatica_v1_gate` | 22 test verdi |

### 11.2 Codici di avviso V326 da sapere leggere

| Codice | Significato |
|---|---|
| `FLASH_SHOT` | inquadratura sotto 1,1 s: difficile da leggere |
| `LONG_STATIC_SHORT` | piano statico prolungato in uno short |
| `COMPLEX_DETAIL_TOO_FAST` | dettaglio complesso con tempo insufficiente |
| `LONG_END_CARD` | cartello conclusivo lungo: meglio chiudere sull'opera |
| `SAME_SHOT_PATTERN` | tre inquadrature con opera+focale+movimento uguali |
| `TOO_MANY_FLASHES` | troppi tagli sotto 1,1 s |
| `MECHANICAL_CADENCE` | durate quasi uguali: il ritmo non è motivato |
| `UNMOTIVATED_CAMERA` | `camera_reason: auto_zoom` |
| `VISUAL_ANCHOR_MISSING` | frase nominata senza dettaglio visibile corrispondente |
| `TIMELINE_OVERLAP` / `TIMELINE_GAP` | sovrapposizione o buca nella timeline |

Sono **prompt di revisione**, non certificazioni di qualità.

### 11.3 Controlli a occhio (obbligatori, non delegabili)

- [ ] Guardare **l'intero** video, con audio e muto.
- [ ] Controllare i primi 3 s e gli ultimi 3 s su schermo Android.
- [ ] Verificare che **nessun testo** resti negli ultimi 3 s.
- [ ] Verificare che il **titolo sia leggibile nella copertina**.
- [ ] Verificare la coda nera reale con `inspect_black_tail`.
- [ ] Verificare che i diritti di **ogni** opera, foto e traccia siano documentati.
- [ ] Verificare i **fatti** dei testi pubblici.
- [ ] Guardare campioni di ogni scena e i tagli più importanti.

### 11.4 Il passaggio tecnico non è approvazione artistica

> Un gate verde significa: il piano è strutturalmente conforme. **Non** significa che il
> video sia bello, che i fatti siano veri, che i diritti siano liberi o che valga la pena
> pubblicarlo. Quelle quattro risposte le dà una persona che guarda e ascolta.

---

## 12. FASE 9 — I quattro post pubblici (V28)

### 12.1 Regole

- Quattro testi **davvero distinti** (Facebook / Instagram / TikTok / YouTube).
- Il testo racconta **l'opera e il suo significato**, non la lavorazione.
- Lingua **per canale**: spagnolo naturico per i canali della pagina originale, italiano
  naturico per i canali italiani.
- **2–4 hashtag** pertinenti, mai 20 tag generici.
- Titolo dell'opera in inglese dove esiste il titolo inglese canonico.
- Crediti e licenze in fondo, sobri.
- Niente forzature di like/commento/share.

### 12.2 Parole e formule vietate in pubblico

`regia`, `zoom`, `inquadrature`, `montaggio`, `script`, `AI`, `cameraman`, `algoritmo`,
`metodologia`, `effetti`, `render`, `velocità`, `Standard`, `ArtVision`, `Tra le Pagine`.

Cliché vietati: «Un'opera che parla senza parole», «Un viaggio dentro», «Lasciati trasportare»,
«L'arte prende vita», «Cosa ne pensi? Scrivilo nei commenti», «Non è solo un quadro».

Sono vietati anche i **termini interni di lavorazione** (`brief`, `storyboard`, `template`,
`json`, `shot list`, `pipeline`, `workflow`, `montaje`) e le **richieste di interazione**
(«dale like», «suscríbete», «comenta», «comparte»).

### 12.3 Come il gate misura la somiglianza

Jaccard **sul corpo editoriale**: hashtag e righe di crediti/licenze sono esclusi dal calcolo
(sono obbligatori e identici per canale: conteggiarli gonfierebbe il punteggio e nasconderebbe
i tagli realmente uguali).

| Somiglianza | Esito |
|---|---|
| ≥ 75% | **blocker** — testi quasi identici |
| ≥ 60% | avviso — testi molto vicini |
| < 60% | ok (nel piano di esempio il massimo è **46%**) |

### 12.4 Come scrivere i quattro tagli (non la stessa stringa quattro volte)

| Canale | Taglio consigliato | Lunghezza indicativa |
|---|---|---|
| **Facebook** | il racconto biografico e l'opera: chi era, cosa guardava, cosa dipingeva | 110–130 parole |
| **Instagram** | l'affermazione che rende l'artista unico, con l'opera come prova | 100–120 parole |
| **TikTok** | una domanda che apre e una risposta breve; ritmo secco | 80–100 parole |
| **YouTube** | titolo esplicativo + contesto + elenco opere con licenze + crediti musicali | 130–160 parole |

Ogni post deve **citare l'artista o un'opera del reel** (il gate lo controlla) e deve
contenere la **riga di crediti musicali**.

---

## 13. Consegna

### 13.1 File richiesti

| File | Contenuto |
|---|---|
| `REEL_<ID>.mp4` | MP4 reale, H.264 + AAC, 720×1280, 30 fps, 22–30 s, −14/−15 LUFS, TP ≤ −1 dBTP |
| `COVER_<ID>.jpg` | copertina = fotogramma reale del video |
| `POST_FACEBOOK.txt` | testo pubblico del canale |
| `POST_INSTAGRAM.txt` | testo pubblico del canale |
| `POST_TIKTOK.txt` | testo pubblico del canale |
| `POST_YOUTUBE.txt` | testo pubblico del canale |
| `SOURCES_AND_RIGHTS.md` | provenienza opera per opera + diritti + crediti musicali |
| ricetta riproducibile | comandi, asset, hash, tempi: il video deve essere rifabbricabile |
| ZIP CRC-checked | pacchetto completo |
| ZIP solo MP4 | fallback Android |

### 13.2 Comandi di consegna

```bash
# Pacchetto di consegna (crea lo ZIP, NON carica e NON pubblica)
python src/artvision_delivery_v55.py pack \
  --video    output/<progetto>/REEL_<ID>.mp4 \
  --cover    output/<progetto>/COVER_<ID>.jpg \
  --facebook output/<progetto>/POST_FACEBOOK.txt \
  --instagram output/<progetto>/POST_INSTAGRAM.txt \
  --tiktok   output/<progetto>/POST_TIKTOK.txt \
  --youtube  output/<progetto>/POST_YOUTUBE.txt \
  --rights   output/<progetto>/SOURCES_AND_RIGHTS.md \
  --recipe   output/<progetto>/RECIPE.json \
  --out      output/<progetto>/dist
```

### 13.3 Stato finale

Il riepilogo di consegna dichiara esplicitamente:

```text
status: rendered_needs_review
artistic_review_complete: false
automatically_publishable: false
```

Finché la persona non ha visto e approvato il master, questo è lo stato. **La pubblicazione
non parte da sola.**

---

## 14. Divieti — checklist negativa per l'agente

1. Non copiare il video campione, il suo audio, i suoi frame o le sue fotografie.
2. Non copiare il timing o il numero di immagini del riferimento.
3. Non produrre sottotitoli: mai burn-in, mai ASS/SRT, mai traccia subtitle.
4. Non sostituire la musica con la voce, né la voce con la musica.
5. Non deformare volti, mani o gesti; non generare ricostruzioni di opere storiche.
6. Non scrivere in pubblico parole di lavorazione; non usare cliché ricorrenti.
7. Niente ghosting, una sola immagine per frame, nessuna sovrapposizione alpha.
8. Non spingere dettagli intimi, sangue o nudità pittorica in primo piano.
9. Non pubblicare in automatico: senza revisione artistica lo stato resta `rendered_needs_review`.
10. Non usare le parole `Standard`, `ArtVision`, `Tra le Pagine` nelle scritte visibili,
    nelle copertine o nei titoli pubblici.
11. Non modificare `config/editorial_rules.json`, `config/video_formats_v13.json`, il Gold Master V6.
12. Non registrare il formato candidato nelle fonti approvate senza approvazione esplicita.
13. Non dichiarare un piano come «video pronto» né una clip come «master».
14. Non inventare metriche, tendenze, licenze, fonti o verifiche.
15. Non spendere su API a pagamento senza autorizzazione esplicita e separata.

---

## 15. Cosa resta fuori da questo documento (chiamarlo, non fingerlo)

- **Renderer dedicato per chip e cartelli serif: non esiste.** I parametri di tipografia
  (corpi, spaziature, allineamenti, angoli) sono specificati nel profilo e devono essere
  **costruiti e verificati a occhio**. Un agente che afferma «il chip è stato renderizzato»
  senza aver prodotto e guardato il file sta mentendo.
- **Registrazione del formato** in `config/video_formats_v13.json` e
  `config/editorial_rules.json → formats`: serve approvazione esplicita.
- **`reel_cromatica_v1` non è un valore ammesso dal gateway generativo Vidu.** Se serve
  generazione i2v, la scelta del valore `format` e la spesa sono una decisione umana.
- **Verifica dei diritti di ogni opera, foto e traccia** di un episodio concreto: le fonti del
  template sono documentate, ma la responsabilità resta a chi pubblica.
- **Qualunque metrica di performance**: nessuna retention, reach o trend è disponibile.
- **Coordinate dei crop**: i crop verticali vanno scelti guardando i file originali e
  documentati a mano; il brief dichiara l'ancora, non le coordinate.

---

## 16. Appendice — comandi in sequenza (episodio nuovo)

```bash
cd /workspace

# F0 — Preflight sul piano di esempio, per capire il contratto
python src/artvision_editor_v19.py --brief templates/REEL_CROMATICA_V1_CANDIDATE.json --out output/reel-cromatica-v1
python src/reel_cromatica_v1_gate.py --brief templates/REEL_CROMATICA_V1_CANDIDATE.json --out output/reel-cromatica-v1
python -m unittest tests.test_reel_cromatica_v1_gate

# F1 — Copia il template per il nuovo episode
cp templates/REEL_CROMATICA_V1_CANDIDATE.json output/<progetto>/BRIEF_<ID>.json

# F2 — Compila: scenes, sources, music, audience_research, social_posts
#      poi rilancia F0 sul nuovo brief

# F3 — Musica (prima dello storyboard)
cp templates/MUSIC_RELEASE_V20.json output/<progetto>/MUSIC_RELEASE_V20.json
python src/music_rights_v20.py --manifest output/<progetto>/MUSIC_RELEASE_V20.json --out output/<progetto>/MUSIC_REPORT_V20.json

# F4 — Generazione clip: SOLO con autorizzazione di spesa
#      (vedi §10.2 per i vincoli del gateway)

# F5 — Montaggio 720×1280 / 30 fps / H.264+AAC, musica mixata a −14/−15 LUFS

# F6 — QA
python src/controllo_master_v5.py --video output/<progetto>/REEL_<ID>.mp4 --out output/<progetto>/CONTROLLO_AUDIO_VIDEO_V5.json
# + inspect_black_tail + controllo a occhio (i primi 3 s e gli ultimi 3 s su Android)

# F7 — Post e consegna
python src/artvision_delivery_v55.py pack --video ... --cover ... --facebook ... --instagram ... --tiktok ... --youtube ... --rights ... --recipe ... --out output/<progetto>/dist

# F8 — Chiedere il parere estetico. Il passaggio tecnico non è approvazione.
```

---

*Fine del report. Documento autonomo: non è stato generato da `video_director_v13.py` e non
modifica il profilo `config/reel_cromatica_v1.json`, che resta candidato non registrato.*
