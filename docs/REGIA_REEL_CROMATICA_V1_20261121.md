# REGIA REEL «ENFERMEDAD CROMÁTICA» — RICOSTRUZIONE TECNICA V1 (21 novembre 2026)

**Scopo:** ricostruire con precisione le tecniche di regia e packaging della pagina/reel
«Enfermedad cromática» (Escuela de Artes Plásticas — diffusione artistica educativa) per
avere una base tecnica riproducibile con cui generare reel più simili possibili.

**Stato:** ricostruzione da screenshot della pagina + fonti interne del progetto.
Non è un Gold Master, non è un'approvazione artistica, non autorizza pubblicazione
né spesa. Nessun materiale del riferimento (video, audio, foto, frame) viene riutilizzato.

Risorse collegate:
- `config/reel_cromatica_v1.json` — profilo macchina-readable del format (questo documento è la prosa).
- `templates/REEL_CROMATICA_V1_CANDIDATE.json` — piano di regia compilabile, già passabile al validatore V19.
- `src/reel_cromatica_v1_gate.py` — gate che verifica un brief contro il profilo (packaging, durata, diritti, sottotitoli, quattro post V28).
- `tests/test_reel_cromatica_v1_gate.py` — 22 test permanenti del gate (1 caso positivo + 21 negativi).
- `modules/artvision/REGIA_CINEMA_WOW_V2.md` — analisi del filmato campione 28,17 s (montaggio, non packaging).
- `docs/REGIA_REFERENZE_V326_20261112.md` — V326: rubare i principi, mai copiare il prodotto.
- `docs/ARTVISION_EDITORIAL_POST_STANDARD_V28.md` — V28: come si scrivono i quattro post.
- `config/editorial_rules.json` — regole sempre attive (precedenza: `explicit_user_request` → `editorial_rules` → `format_profile` → `episode_choices` → `historical_guides`).

**Stato di eseguibilità al 21/11/2026:** profilo, template e gate esistono e sono collaudati.
Il piano d'esempio passa V19 con **0 blocker** e il gate con **0 blocker**; restano solo
tre avvisi dichiarati (fatti da verificare, revisione artistica, registrazione musicale
da validare con ffprobe). I quattro post V28 sono scritti e controllati dal gate
(somiglianza massima fra due testi: 46%). Non è ancora un master, non è un'approvazione
estetica e non autorizza pubblicazione né spesa.

---

## 1. Perimetro della ricostruzione: cosa ho visto e cosa no

**Osservato direttamente dagli screenshot** (griglia Reels + profilo): la grammatica delle
scritte sovrimpresse, le formule di titolo, la gerarchia dei dati (nome artista → paese →
nazionalità), l'unità tipografica, la copertina, il mix di soggetti, i pattern di serie,
il volume di visualizzazioni per tipo di reel.

**Non verificabile dagli screenshot** (dichiarato come incognito, non riempito a supposizione):
la durata effettiva di ciascun reel, la presenza o meno di voce narrante, il brano e la
sua struttura, i movimenti di camera, il numero di tagli al secondo, la compressione e il
bitrate, la presenza di transizioni dissolve. Questi punti sono ricostruiti **solo** dove il
repo ha un dato reale (il campione 28,17 s / 9:16 / 30 fps analizzato in
`REGIA_CINEMA_WOW_V2.md`) e sono marcati come tali.

**Vincolo legale e di progetto che governa tutto il documento:** il campione è
un riferimento di **linguaggio**, non un materiale da ripubblicare. Nessuna immagine,
musica, voce o animazione del riferimento entra nei nostri video. Nessun timing o numero di
immagini viene copiato (`config/editorial_rules.json → always.do_not_copy_reference_video_timing_or_image_count`).

---

## 2. Anatomia del reel (specifiche tecniche)

| Elemento | Valore | Fonte |
|---|---|---|
| Formato | 9:16 verticale | screenshot |
| Risoluzione clone | 720×1280 | istruzione esplicita dell'utente (chat precedente) |
| Frame rate | 30 fps | campione 28,17 s + istruzione esplicita |
| Codec | H.264 / AAC (MP4) | `config/editorial_rules.json → delivery_v55` |
| Loudness | −14/−15 LUFS integrato | istruzione esplicita dell'utente; il gate di misura `src/controllo_master_v5.py` usa −16 ±3 LU e −1 dBTP |
| Durata | 22–30 s, **decisa dal contenuto** | non copiare i 28,17 s del campione (regola `do_not_copy_reference_video_timing…`) |
| Sottotitoli | **mai**: nessun burn-in, nessun ASS/SRT, nessuna traccia | `REGOLE_VIDEO_V12.md §1` |
| Voce | opzionale per formato; mai sostituire la musica con la voce | `config/editorial_rules.json → always` |
| Musica | registrazione reale con licenza verificata per la registrazione specifica | `config/music_policy_v20.json` |

---

## 3. La grammatica delle scritte sovrimpresse — cuore del format

Troviamo **tre sistemi tipografici distinti**, non uno. Confonderli è l'errore più
costoso: il feed diventa incoerente e la pagina perde la firma.

### Sistema A — "chip" (formato dominante, ~60% dei reel osservati)

Stack verticale di **tre etichette**, ognuna con il proprio sfondo:

| Riga | Contenuto | Sfondo | Testo |
|---|---|---|---|
| 1 | **TITOLO/HOOK** | chip nero, angoli arrotondati | bianco, bold |
| 2 | **NOME ARTISTA** | chip bianco | nero, regular |
| 3 | **PAESE + BANDIERA** | chip bianco | nero, regular |

Posizione: allineato centralmente o appena sopra il centro, in orizzontale, con
separazione 6–10 px fra le righe. La riga 1 è **sempre** presente: è l'ancora visiva
del reel nel flusso.

Riga 1 secondo la formula:
- **"El/La [professione] de [specialità]"** → etichetta funzionale dell'artista
  (storico, con specialità riconoscibile).
- **"El Artista:" / "El artista:"** → prefisso esplicito per artista con statuto da
  scoperta (contemporanei, meno noti).
- **"Artistas que tienes que conocer"** → serie evergreen di scoperta.
- **"Maestros de la viñeta"**, **"Las brujas en el arte"**, **"Pintores del terror"** → serie tematiche/collettive.

### Sistema B — "cartello serif" (maestri canonici)

Nessun chip: testo **serif ad alto contrasto** (stile Didone), bianco, direttamente sul
dipinto, in basso o al centro, con tre righe:

```
William-Adolphe Bouguereau
1825–1905
Francia
```

Stessa struttura per Goya (1746–1828, España), Monet (1840–1926, Francia),
Beksinski (1929–2005, Polonia). Serve quando il nome **è già un'istituzione**: il
cartello non aggiunge curiosità, la mette in cornice.

### Sistema C — "domanda/affermazione" (serie tematiche-filosofiche)

Frase iniziale serif bianca, spesso iniziale con `¿`, in alto:

```
¿La luz no se puede pintar?
```
con sotto-riga descrittiva in sans più piccola su barra nera:
```
Mira el comportamiento de la luz en esta pintura
```

Variante con virgolette per l'affermazione impossibile:
```
"Es imposible pintar la luz"
```

Questo sistema **non nomina l'artista nei primi secondi**: la domanda è l'hook, il nome
arriva dopo. È la serie con la ripetizione più alta (74.011 / 122.048 / 31.873 visualizzazioni
sulle tre occorrenze osservate).

### Regole tipografiche valide per tutti e tre i sistemi

- Testo **sempre bianco** su fondale scuro o su chip: contrasto garantito dal chip.
- Mai testo bianco su dipinto chiaro senza chip → leggibilità a 3 cm dal telefono.
- **Nessun testo oltre i 3 secondi finali**: la chiusura è l'opera, non il cartello.
- Nessun logo, nessun watermark, nessun handle @ nel video.
- Le bandierine sono **emoji** (🇩🇪 🇦🇷 🇺🇸 🇮🇪 🇲🇽 🇨🇴 🇵🇪 🇮🇹 🇫🇷 🇻🇪 🇨🇭 🇵🇪🇺🇸) e rendono il paese immediatamente leggibile, anche per chi non conosce l'artista.
- Normalizzare l'ortografia dei nomi propri: la pagina originale scrive con
  inconsistenze (`Estados unidos`, `Peruano - Estadounidense`). Nelle nostre didascalie
  e nei nostri chip usiamo la forma **corretta e verificata** del nome.

---

## 4. Sistema di titolazione — le 5 formule ricorrenti

| # | Formula | Funzione | Esempi reali osservati |
|---|---|---|---|
| 1 | `El/La [professione] de [specialità]` | etichetta funzionale → curiosità | El pintor de los monjes y el vino · El pintor de las llanuras argentinas · El pintor de la elegancia · El maestro del vitral · El pintor de la pincelada fluida · La pintora de la anatomía fantástica · La retratista del Perú del siglo XIX · El pintor de la memoria venezolana · El artista de los paisajes nevados · La pintora de los instantes fugaces · El pintor de la pincelada libre |
| 2 | `El Artista:` + nome + paese | statuto da scoperta | Armando Requena (Perú) · Frederic Edwin Church (EE.UU.) · Todd McFarlane (Canadá) · Saturnino Herrán (México) · Frank Frazetta (EE.UU.) · Johann Heinrich Füssli (Suiza) |
| 3 | `Artistas que tienes que conocer` | serie evergreen, discovery | (ripetuta su più reel) |
| 4 | Serie tematica | collettivo per tema | Las brujas en el arte · Pintores del terror · Maestros de la viñeta · Cuando los artistas pintan la luz |
| 5 | Domanda / paradosso | hook filosofico, nome in ritardo | ¿La luz no se puede pintar? · Es imposible pintar la luz |

**Regole di scelta:**
- La **specialità** (riga 1, formula 1) deve essere **un attributo specifico e verificabile**,
  non un aggettivo generico. "El pintor de los monjes y il vino" funziona perché è
  letterale; "El pintor famoso" no.
- Un artista non entra con la formula 1 e la 2 nella stessa serie: la 1 è per chi ha un
  mestiere riconoscibile, la 2 per chi è da scoprire.
- La formula 3–5 non si combinano con l'etichetta-chip a 3 righe nello stesso momento:
  o la domanda apre e il nome arriva dopo, o il chip apre con il titolo.

---

## 5. Il pacchetto di copertina e feed

- Griglia a **3 colonne**, thumbnail leggibili da soli, senza scroll.
- Il **titolo è dentro il thumbnail**: la riga 1 del chip o il cartello serif compare già
  nel fotogramma di copertina. Il reel deve essere riconoscibile dalla griglia, non
  dal testo del post.
- Fondali prevalentemente **scuri/neutri** per far leggere il dipinto: le copertine della
  pagina sono in prevalenza scure (chiaroscuro, fondi neri, interni).
- La copertina **non** è un'immagine dedicata: è un fotogramma del video.
- Nessun bordo, nessuna cornice, nessun collage: un'immagine per frame, niente ghosting
  (`config/cinematic_techniques_v23.json → safety.images_per_frame = 1`).

---

## 6. Grammatica dei shot (5 tipi ricorrenti)

| Tipo | Descrizione | Attenzione |
|---|---|---|
| **A. Dettaglio d'opera** | crop ravvicinato su luce, mani, tessuto, volto | è il cavallo di battaglia; reggere 1,5–3 s senza muoversi |
| **B. Opera intera** | quadro completo nell'inquadratura | almeno una volta per opera, per non mutilare |
| **C. Artista in studio** | l'artista al tavolo, con la sua opera o il suo processo | rompe il ritmo "quadro+quadro"; alto engagement |
| **D. Museo/cornice** | l'opera dentro una cornice reale, con scala | serve alla serie "Cuando los artistas pintan la luz" |
| **E. Serie / collettivo** | più opere sullo stesso tema, montate per affinità | copertine tematiche: Las brujas, Pintores del terror |

**Regole:**
- Non tagliare mai teste, firme o elementi semantici: crop selettivo, non mutilazione.
- Alternare A e B; C ogni 2–3 reel; D solo se la serie lo chiede.
- Il campione del repo (analisi V2) insegna tre cose verificabili: **chiaroscuro
  marcato**, **attenzione a mani / abiti / volti**, **ricorrenza di soggetti come
  leitmotiv** invece di una sequenza di quadri diversi senza legame.
- Zero deformazioni di volti e gesti: le opere sono autentiche, non ricostruite.

---

## 7. Ritmo e montaggio

Regola madre del progetto: **mai una regola "ogni N secondi"** (V326). Il ritmo si
motiva sull'opera. Però il campione reale e le soglie V326 danno un campo di gioco:

- Soglie di segnalazione (advisory, non divieti): flash < 1,1 s · dettaglio complesso < 2 s ·
  pausa statica lunga in uno short · tre inquadrature consecutive identiche per
  opera/focale/movimento · durate meccaniche (deviazione standard < 0,18 s) ·
  troppi flash (≥ 40% dei tagli sotto 1,1 s) · cartello finale > 2,5 s.
- Target pratico del clone: **5–13 inquadrature in 22–30 s**, durate **variate**,
  almeno un **respiro** (2,5–4,5 s), almeno un **taglio in battuta** su un cambio
  significativo (mano → mano, luce → luce).
- Chiusura: **l'opera**, non il testo. Se serve un cartello finale, ≤ 2,5 s.
- Transizioni: stacchi netti, poche dissolvenze motivate, mai flash a raffica.

---

## 8. Direzione musicale e audio

- Brano **solo strumentale**, struttura con evoluzione (non loop di 4 onde).
- Scelta musicale **prima** dello storyboard: si decide la forma del brano (quanti
  piccoli, dove i fraseggi) e poi si taglia.
- Licenza: registrazione specifica con fonte, autore, URL, prova di registrazione e
  crediti (`config/music_policy_v20.json`, `templates/MUSIC_RELEASE_V20.json`).
  **Non** riusare l'audio del campione.
- Se c'è voce narrante: frasi corte, in italiano o spagnolo a seconda del format, e
  **mai** sottotitoli impressi. La voce non sostituisce la musica: si somma.
- Mix: musica a −14/−15 LUFS integrato, senza clipping.

---

## 9. Selezione del soggetto e regole di verifica

La pagina mescola tre bacini — è il segreto della sua varietà:

1. **Maestri canonici** (Bouguereau, Goya, Monet, Manet, Sargent, Morisot, Courtois,
   Previati, Herrera Toro, Holguín, Alciati, della Valle, Church, Grützner) → formula 1 o 2.
2. **Contemporanei e illustratori** (Requena, Vallejo, McFarlane, Frazetta, Bell, Füssli,
   Sanjuán, Herrán) → formula 2, con clip in studio (shot tipo C).
3. **Temi** (streghe, terrore, luce, vetro, miniatura) → serie tematiche, formula 4.

Regole di ingaggio:
- Verificare i fatti (date, paese, tecnica, specialità) su fonte primaria: il chip
  "El pintor de X" è un'**affermazione** e va verificata, non inventata.
- Diritto: opere in pubblico dominio o CC0 con provenienza registrata; foto di
  artista e quadri contemporanei con diritti documentati per l'uso sociale.
- Confronto di almeno 3 candidate prima di scegliere il soggetto
  (`docs/ARTVISION_AUDIENCE_RESEARCH_V32.md`).
- Nessuna tendenza o metrica inventata: se non abbiamo il dato, lo dichiariamo
  non disponibile.

---

## 10. Post e didascalie (V28)

Quattro testi **davvero distinti** (Facebook / Instagram / TikTok / YouTube), non la stessa
stringa quattro volte.

- Il testo racconta **l'opera e il suo significato**, non la lavorazione.
- Vietato in pubblico: `regia`, `zoom`, `inquadrature`, `montaggio`, `script`, `AI`,
  `cameraman`, `algoritmo`, `metodologia`, `effetti`, `render`, `velocità`.
- Cliché da non usare: "Un'opera che parla senza parole", "Un viaggio dentro",
  "Lasciati trasportare", "L'arte prende vita".
- 2–4 hashtag pertinenti, mai 20 tag generici.
- Titolo dell'opera in inglese dove esiste il titolo inglese canonico; crediti e licenze
  nel piè di testo sobrio.
- Niente forza di like/commento/share.

Per il **clone in spagnolo** (destinazione della pagina originale), i post vanno scritti
in spagnolo naturico; per i canali italiani restano in italiano naturico (V28).
La lingua dei testi è **per canale**, non un blocco unico.

### 10.1 Come il gate verifica i quattro post

V19 non legge `social_posts`: è il gate dedicato a controllarli, perché il requisito
V28 è di fatto non negoziabile e non può dipendere da una revisione a occhio.

| Controllo | Esito |
|---|---|
| Presenza e non-vuoto dei quattro testi | blocker |
| Somiglianza fra due testi (Jaccard sul **corpo editoriale**, senza hashtag e righe di credito) | blocker ≥ 75%, avviso ≥ 60% |
| Parole vietate di lavorazione (`regia`, `zoom`, `montaggio`, `AI`, `render`, …) | blocker |
| Cliché vietati | blocker |
| Richieste di interazione («dale like», «comenta», «suscríbete») | blocker |
| Termini interni di lavorazione (`brief`, `storyboard`, `shot list`, `montaje`) | blocker |
| Citazione dell'artista o di un'opera del reel | blocker |
| Numero di hashtag (2–4) | avviso |
| Crediti musicali e licenze nel testo pubblico | avviso |
| Possibile italiano residuo / assenza di segnali spagnoli | avviso |
| Refusi, punteggiatura, troppe domande o punti esclamativi | avviso |

La misura di somiglianza usa il corpo editoriale perché hashtag e crediti sono
**obbligatori e identici per canale**: conteggiarli gonfierebbe il punteggio e
nasconderebbe i tagli realmente uguali. Nel piano d'esempio la somiglianza massima
fra due post è **46%** (Instagram/TikTok), sotto la soglia di avviso.

Quando il gate passa, scrive i quattro file pubblicabili nella cartella di output:
`POST_FACEBOOK.txt`, `POST_INSTAGRAM.txt`, `POST_TIKTOK.txt`, `POST_YOUTUBE.txt`.

### 10.2 Il confronto a 3 candidate (V32)

Prima di scegliere il soggetto, `docs/ARTVISION_AUDIENCE_RESEARCH_V32.md` impone di
confrontare **almeno 3 opere o temi distinti** e di dichiarare i limiti dei segnali.
Il gate replica quegli stessi controlli sul blocco `audience_research` del brief
(misma struttura di `src/editorial_rules.py`).

Nel piano d'esempio i tre confrontati sono:

| Candidato | Forza | Limite | Totale stima |
|---|---|---|---:|
| **Ivan Aivazovsky — The Ninth Wave** | corpus ampio e coerente, formula di titolo 1 naturale, arco tempesta → dopo la tempesta | — | **69** |
| Katsushika Hokusai — La Grande Onda | gancio e dettaglio migliori in assoluto | un solo foglio non regge 10 inquadrature senza ricomporre l'opera | 62 |
| J. M. W. Turner — The Fighting Temeraire | appoggio documentale e museale forte | tema della luce già saturo nel catalogo | 56 |

La stima è un **giudizio editoriale interno**, non una misura di mercato: la
dimensione "interesse osservato del pubblico" resta **`non valutabile`** e i totali
sommano solo le dimensioni valutabili. Tutti e tre i candidati dichiarano
`audience_signal: unavailable` con il motivo: **non esistono dati verificati** di
retention, reach o tendenza per queste opere. Nessun numero è inventato.

Il gate blocca se manca il confronto, se i candidati sono meno di 3, se uno è
incompleto o duplicato, se un candidato non dichiara il segnale (o non ne motiva
l'indisponibilità), se `selected_work` non è una delle opere confrontate, o se
mancano `selection_reason`, `viewer_interest`, `creative_direction`,
`signal_limitations`.

---

## 11. Divieti (checklist negativa)

1. Non copiare il video campione, il suo audio, i suoi frame o le sue fotografie.
2. Non copiare il timing o il numero di immagini del riferimento.
3. Non produrre sottotitoli (burn-in, ASS, SRT, tracce) — **mai**, in nessun formato.
4. Non usare la voce al posto della musica, o la musica al posto della voce se il
   format la richiede.
5. Non deformare volti, mani o gesti; non generare ricostruzioni di opere storiche.
6. Non scrivere in pubblico parole di lavorazione; non usare cliché ricorrenti.
7. Non fare ghosting, non più di un'immagine per frame, nessuna sovrapposizione
   alpha tra immagini.
8. Non spingere dettagli intimi, sangue o nudità pittorica in primo piano
   (`docs/ARTVISION_LINEE_GUIDA_SOCIAL.md`).
9. Non pubblicare in automatico: senza revisione artistica lo stato resta
   `rendered_needs_review`.
10. Non usare parole "Standard", "ArtVision", "Tra le Pagine" nelle scritte visibili,
    nelle copertine, nei titoli pubblici o nelle descrizioni.

---

## 12. Come si usa questa base (percorso operativo)

1. **Scegliere il soggetto**: compilare `audience_research` con il confronto a 3
   candidate (V32, cap. 10.2) + verifica dei fatti su fonte primaria.
2. **Scegliere la formula di titolo** (cap. 4) in base allo statuto dell'artista e alla serie.
3. **Compilare `templates/REEL_CROMATICA_V1_CANDIDATE.json`**: scena per scena, con
   `visual_anchor`, `camera_reason`, `on_screen_text` (chip o cartello), durate motivate;
   poi `audience_research` e i quattro `social_posts`.
4. **Validare in due passaggi** (nessuna spesa, nessun render):
   ```bash
   python src/artvision_editor_v19.py \
     --brief templates/REEL_CROMATICA_V1_CANDIDATE.json \
     --out output/reel-cromatica-v1
   python src/reel_cromatica_v1_gate.py \
     --brief templates/REEL_CROMATICA_V1_CANDIDATE.json \
     --out output/reel-cromatica-v1
   ```
   Blocchi e avvisi sono in `output/reel-cromatica-v1/EDITOR_REPORT_V19.json` e
   `output/reel-cromatica-v1/REEL_CROMATICA_V1_GATE.json`.
   V19 controlla schema e fonti; il gate controlla che il piano rispetti **questo**
   profilo: durata 22–30 s, durata diversa dal campione, inquadrature e movimenti
   ammessi, chip/cartello conformi, nessun testo negli ultimi 3 s, nessun sottotitolo,
   parole vietate nel testo pubblico, ogni opera registrata con diritti ammessi.
   I blocker fermano; gli avvisi chiedono una revisione umana.
5. **Montare** 720×1280 / 30 fps / H.264+AAC, musica con licenza, overlay secondo cap. 3.
6. **Controllare il master vero**: con audio, muto, e solo audio; primi 3 s e ultimi 3 s
   su schermo Android; coda nera reale (`src/director_reference_v326.py → inspect_black_tail`).
7. **Produrre i post** (4 testi distinti in `social_posts`; il gate li scrive in
   `output/…/POST_*.txt`) + `SOURCES_AND_RIGHTS.md` + crediti musicali.
8. **Consegna**: MP4, copertina JPEG, ricetta riproducibile, ZIP CRC-checked
   (`config/editorial_rules.json → delivery_v55`).
9. **Chiedere il parere estetico**: il passaggio tecnico non è approvazione.

---

## 12bis. Esempio di riferimento già montato: «El pintor de las tormentas»

`templates/REEL_CROMATICA_V1_CANDIDATE.json` non è uno scheletro vuoto: è un episodio
completo che mostra come si compila ogni campo. Serve da modello di copia per i prossimi.

- **Soggetto**: Ivan Aivazovsky (1817–1900), formula 1 «El pintor de las tormentas».
- **Packaging**: chip a tre righe — `El pintor de las tormentas` (nero, bianco bold) /
  `Ivan Aivazovsky` (bianco, nero) / `🇷🇺 Rusia` (bianco, nero) — presente nella
  copertina e per i primi 4,7 s, poi più nessun testo.
- **10 inquadrature, 23,60 s** (non i 28,17 s del campione), 8 opere, tutte file
  Wikimedia Commons in pubblico dominio verificati il 21/11/2026 (URL, dimensioni,
  licenza letti via API; larghezza utile dopo il crop 9:16 compresa tra 675 e 1923 px).
- **Struttura drammatica**: mani che sventolano → opera intera → cielo in tensione →
  cresta d'acqua → contrasto cromatico (l'iride) → nave in colonna verticale →
  **respiro** (mare vuoto, 3,2 s) → ultima luce → tramonto → ritorno circolare al
  motivo di apertura. Chiusura **sull'opera**, non su un cartello.
- **Lezioni di regia applicate**: dettaglio → opera intera (mai il contrario di
  default), un solo movimento per volta e mai tre uguali, durate disuguali
  (deviazione standard 0,69 s), respiro centrale, motivo ricorrente (mani, luce),
  taglio in battuta solo dove cambia qualcosa.
- **Verifiche eseguite**: V19 → 0 blocker, 2 avvisi (fatti, revisione artistica);
  gate del profilo → 0 blocker, 3 avvisi (gli stessi due più la registrazione
  musicale da validare con ffprobe). Il gate è collaudato da **22 test permanenti**
  (`tests/test_reel_cromatica_v1_gate.py`): 1 caso positivo + 21 negativi, fra cui
  timing uguale al campione, testo negli ultimi 3 s, chip a due righe, ancora visiva
  mancante, sottotitolo nel brief, parola vietata, cliché, CTA, termine interno di
  lavorazione, opera fuori registro fonti, diritto non ammesso, movimento sconosciuto,
  post mancante/vuoto/duplicato, hashtag fuori range, testo senza artista, confronto
  V32 mancente, con meno di 3 candidate, con candidate duplicate, senza segnale
  dichiarato e con opera scelta non confrontata.
- **Confronto V32 documentato**: Aivazovsky (69) vs Hokusai (62) vs Turner (56),
  con l'interesse osservato dichiarato `non valutabile` e i segnali di pubblico
  dichiarati `unavailable` con motivo — nessuna metrica inventata.
- **I quattro post V28 sono scritti** (Facebook 118 parole, Instagram 107, TikTok 84,
  YouTube 142; 3 hashtag ciascuno; somiglianza massima fra due testi 46%) e il gate
  ne produce i file pubblicabili in `output/reel-cromatica-v1/POST_*.txt`.
- **Cosa resta da fare a mano**: guardare i file originali e scegliere i crop
  verticali (le coordinate non sono nel brief), rivedere i fatti elencati in
  `editorial.facts_pending`, provare la registrazione musicale.

---

## 13. Cosa resta fuori da questo documento (chiamarlo, non fingerlo)

- Registrazione del nuovo format nelle fonti uniche del progetto
  (`config/video_formats_v13.json`, `config/editorial_rules.json → formats`): serve
  approvazione esplicita, perché quelle fonti sono la versione approvata e non si
  modificano in autonomia. Fino ad allora il profilo vive in
  `config/reel_cromatica_v1.json` come **candidato**.
- Renderer dedicato per i chip e i cartelli serif: non esiste ancora. Il piano si
  valida con V19 e con il gate, ma la resa tipografica va costruita e poi verificata
  a occhio; i parametri (corpi, spaziature, allineamenti) sono specificati nel
  profilo, non ancora eseguiti da un motore.
- Verifica dei diritti di ogni opera/immagine/foto usata in un episodio concreto:
  le fonti del template sono in pubblico dominio e documentate, ma la
  **responsabilità** resta a chi pubblica.
- Qualunque metrica di performance: i numeri di visualizzazioni osservati provengono
  dagli screenshot e **non** sono misure di retention, durata media o completamento.
- Il renderer di un nuovo episode non è scritto: il profilo dice *cosa* montare,
  non *come* lo codifica.
