# ART VISION CRITICO — PATTO VISIVO DELLA SERIE (21 ottobre 2026)

La base approvata da chi realizza il progetto è **Dalí Critico V1.1**, con miglioramenti non distruttivi introdotti per **Picasso Guernica V1**.

## Regole editoriali da preservare per ogni futuro quadro

1. L'episodio è un vero commento **da critico d'arte esperto**: informazioni museali controllate, descrizioni precise dei particolari effettivamente visibili, interpretazioni controverse distinte dai fatti. Mai inventare simboli, date, citazioni o caratteristiche.
2. Narrazione accessibile ma non banale: curiosità forte nei primi secondi, domande intelligenti, ritmo naturale con piccole pause e alternanza tra rivelazione, descrizione e riflessione. Non appesantire con liste e termini accademici non spiegati.
3. Voce italiana **Google Gemini Gacrux** quando disponibile, narratore coerente per l'intera storia; evitare cambi improvvisi di voce, volume o prosodia. Se non disponibile, registrare chiaramente la voce alternativa nei metadati. Mai fingere voce umana. **Standard di resa (obbligatorio):** recitazione unica e continua (una sola sessione, un solo timbro) con prompt di stile caldo, umano e vario, mai meccanico né pubblicitario; la voce viene poi **rifinita** (de-rimbombo, presenza, compressione morbida, loudness −16 LUFS, micro fade) per risultare **il più naturale e bella possibile**.
4. Il **quadro autentico** rimane il protagonista: allineare le immagini ai punti del copione. Zoom sui dettagli menzionati, ma periodicamente tornare alla visione integrale. **UNA SOLA inquadratura per battuta: mai due riquadri affiancati/impilati.** Per ogni dipinto (anche orizzontale) il riquadro ha le proporzioni dell'opera — a zoom 1 si vede l'opera intera, lo zoom rivela il dettaglio — e resta UNO solo, centrato. Nessun secondo pannello "insieme + dettaglio".
5. Copertina riconoscibile e di alta qualità con **identita_visiva_v6.py**: stessa fascia scura inferiore, nome artista, filetto oro, dicitura musicale, caratteri e composizione; variano opera, artista e titolo-esca elegante e veritiero. Nessun numero progressivo sulle copertine.
6. Musica autorizzata, discreta sotto la voce, senza cambi bruschi. Sfumare audio in apertura/chiusura e dissolvere tra inquadrature. Ritmi visivi mai da stampino.
7. Negli ultimi secondi solo **piccolo simbolo grafico** discreto per like/iscrizione (cuore e play/+), senza pronunciare richieste o interrompere il commento; chiusura armoniosa, non tagliata.
8. Preservare SEMPRE tutti i vecchi moduli, script, workflow e video; introdurre nuove versioni con nomi dedicati, senza sovrascrivere Cinema V6, libri o Dalí.
9. Prodotti finali: MP4 verticale Full HD 1080×1920 con audio e musica, JPG copertina, testo della voce, secondi/coordinate zoom, fonti e diritti. Prima dell'uso social, verificare copyright originale dei dipinti: disponibilità di foto online e fotografia CC0 non rendono di per sé un dipinto protetto di pubblico dominio.

## Regia e inquadrature — coordinate MISURATE (obbligatorio · aggiornamento 19 novembre 2026, dal caso Raffaello «Scuola di Atene»)

Nel primo master della «Scuola di Atene» i `focus` dei dettagli erano stimati a occhio: le statue di **Apollo** e **Atena** finivano **al bordo** dell'inquadratura e servirono più versioni per correggerle. Da oggi vale una regola sola: **nessun `focus` si scrive senza averlo misurato.** Così ogni episodio nasce giusto al primo colpo, senza rifacimenti.

### Come si misura un `focus` (prima di scrivere il JSON)
`focus = [fx, fy]` è in coordinate normalizzate (0–1) **sull'opera intera**: `crop_into` porta quel punto al **centro** dell'inquadratura. Va quindi misurato il **centro del soggetto**, non il bordo della nicchia o della struttura che lo contiene.

1. Scaricare il quadro reale alla risoluzione usata dal motore (per gli episodi con `source_prefer_original` è l'originale Commons, es. 3697×2414).
2. **Volti** → face detection con `cv2.FaceDetectorYN` (YuNet). Modello: `face_detection_yunet_2023mar.onnx` da `https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx` (232589 B, sha256 `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`). ⚠️ Nella risposta la **colonna `score` è l'ULTIMA** (`r[-1]`), **non** `r[4]`. Tenere i volti con `score >= 0.6`.
3. **Figure non-volto (statue, oggetti)** → profilo orizzontale di luminanza con high-pass: il picco più forte nella fascia della figura è il suo asse; confermare con i connected-components del "marmo" (LAB, canale L).
4. **Cross-check** con l'asse di simmetria dell'architettura e, quando disponibile, con gli SVG etichettati di Commons (mappano i numeri alle figure; **non** etichettano le statue).
5. Scegliere il `focus` sul **centro di testa/torso** del soggetto (es. Apollo → `[0.225, 0.305]`, Atena → `[0.798, 0.320]`).

### Verifica OBBLIGATORIA prima del push (simula il crop del motore)
Ri-eseguire esattamente `crop_into` di `render_series_v2.py` per ogni beat di dettaglio e misurare dove cade il soggetto:
- il volto/centroide deve risultare **centrato** (offset da 0.5 ≈ 0.02–0.05);
- se cade al bordo (|offset| > 0.2) il `focus` è **sbagliato** → correggere e ripetere.

### Costanti di regia già fissate dal motore (`render_series_v2.py`)
- **Un solo riquadro per battuta (obbligatorio).** Ogni inquadratura mostra UN pannello, con le proporzioni dell'opera, centrato. Mai il vecchio "due livelli" (opera intera sopra + dettaglio sotto). Vale anche per i quadri orizzontali/larghi.
- Beat **"wide"**: inquadratura d'insieme con leggera deriva; **aprire e chiudere** con un wide.
- Beat **"dettaglio"**: `zoom_to_end: true` così lo **zoom arriva a fondo entro la battuta** restando agganciato al volto; `zoom_end` tipico **2.5–3.0**.
- Ritorno periodico alla **visione integrale** (una volta a metà racconto) per non perdere l'insieme → regola editoriale 4.
- Dissolvenze tra inquadrature **0.28 s**; `pad` breve e `tail` con cartellino d'opera per gli episodi con `immediate_visual_hook`.

### Vincolo di produzione
Qualsiasi episodio lanciato con `--config` richiede `GEMINI_API_KEY`: il master si produce **via CI GitHub Actions** (workflow dedicato per episodio), non in locale.

## Reel social — formato breve (obbligatorio · aggiornamento 20 novembre 2026)

Oltre all'episodio critico lungo, la serie produce **reel social verticali** di 30–45 s per la promozione. Regole fisse (riferimento: `src/render_social_reel_v3.py` — "gallery cut", primo master: Van Gogh, 36 s). La **v3** sostituisce la v2: stile "galleria d'arte", fluido, **quadri interi**):

1. **Un solo artista, molte opere.** Mai un solo quadro: 10–14 opere dello stesso pittore in sequenza. Il reel è un "assaggio" del pittore, non di un singolo dipinto.
2. **Quadri INTERI, mai croppati (regola v3).** Niente full-bleed cover-crop: ogni opera va **adattata intera (contain)** dentro una "placca" da galleria (max ~880×1055 px) su uno sfondo-ambiente scuro (lo stesso quadro sfocato e scurito come parete di museo) con passe-partout chiaro e ombra morbida. Il movimento non deve **mai** tagliare l'opera.
3. **Arco emotivo, non elenco.** L'ordine delle opere costruisce un'emozione: stupore → calore → delicatezza → speranza → lavoro → colore notturno → intimità → fatica → l'uomo → tragedia (climax). Il primo fotogramma deve essere il capolavoro più iconico (hook), l'ultimo il quadro più intenso.
4. **Niente "palpiti" / stroboscopia (regola v3).** Vietati i flash di luminosità e i micro-zoom pulsati a ogni beat: l'occhio li legge come sfarfallio ("palpiti"). Il movimento è un **"respiro" lento** (zoom ~3 % e deriva verticale che tornano al punto di partenza) che resta dentro i margini, quindi non croppa. Verifica: la variazione di luminanza per-frame deve restare bassa (media < 1, max ≪ 15 su 30 fps).
5. **Transizioni fluide a dissolvenza.** Tra un'opera e l'altra usare una **cross-dissolve** morbida (~0,7 s) invece di tagli netti; gli inizi-fine segmento restano comunque allineati al beat (via `scipy.signal.stft` + spectral flux).
6. **Testo in inglese, minimale ed elegante.** Hook (piccolo sopratitolo dorato + nome artista serif spaziato + date) in apertura; **didascalia discreta** sotto ogni opera (titolo serif + anno in oro); end-card con call-to-action ("Follow for one masterpiece a day"). Niente testi lunghi. Font P052 (Palatino) + Nimbus Sans.
7. **Grade cinema gentile.** Contrasto a S leggero, saturazione lieve, luci calde / ombre fredde (split-tone), vignettatura discreta (~18 %) e grana fine. Deve restare *elegante*, non aggressivo.
8. **Apertura, chiusura e loop.** Verticale **1080×1920 a 30 FPS**. Fade-in da nero e dissolvenza finale to-black con audio in fade: così il reel **si ripete in modo continuo** (il loop aumenta i replay, che l'algoritmo premia).
9. **Zona sicura.** Tenere testi e CTA lontani dal bordo inferiore (UI di TikTok/Reels): didascalie/CTA entro ~y ≤ 1560 su 1920.
10. **Difetti da evitare.** Frame bianchi da overflow `uint8` → clampare e `np.clip(frame, 0, 255)`. Sfasamento video/audio → base temporale unica (`t0`). Musica con copertina video incorporata → estrarre con `-map 0:a:0 -vn`. **Non riusare il nome file di un master precedente** (cache browser 7 gg): alzare la versione (`…_V3.mp4`).

**Musica per i social.** Sui social (Instagram/TikTok/Facebook) conviene usare le **librerie musicali in-app** (audio con licenza già inclusa nella piattaforma), scelte nella categoria *cinematic / emotional / classical*: brani ~90–115 BPM, pianoforte/archi con un *build* e un *drop*, perfetti per contenuti d'arte. Per il file *scaricabile* (fuori piattaforma) usare musica **CC** (es. Kevin MacLeod / incompetech, CC BY 4.0) e citarla nei crediti.

## Moduli di riferimento
- Reel social (v3, gallery cut — quadri interi, fluido): `src/render_social_reel_v3.py`
- Reel social (v2, cinema/beat-locked — superato): `src/render_social_reel_v2.py`
- Reel social (v1): `src/render_social_reel.py`
- Baseline copertina: `modules/artvision/identita_visiva_v6.py`
- Dalí, base approvata: `modules/artvision_critico/render_dali.py`, `dali_sogno_ape.json`; il V1.1 con musica rimane un Artifact GitHub separato.
- Picasso Guernica, nuovo episodio: `render_guernica.py`, `guernica_picasso_v1.json`, workflow dedicato.

**Questa guida non autorizza a sostituire file già approvati.** Le novità si aggiungono come moduli/versioni indipendenti.
