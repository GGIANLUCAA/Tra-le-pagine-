# Illustration Reveals Lab V2 — esperimento, 26 ottobre 2026

**Non è una nuova regola permanente.** Aggiunta isolata alla PR sperimentale Creative Reveals. Nessun cambiamento ai master, renderer di libri/Critico/Cinema, menu live, Video Library, preset e pubblicazione. Solo anteprime mute di una singola illustrazione. Eseguire la revisione artistica prima di usare su un video reale.

## Origine dell'idea
Filmato personale 42205.mp4 (circa 66 s): illustrazioni su bianco, contorni e colori che appaiono per soggetti. Solo ispirazione tecnica: il file e le sue immagini **non** sono copiati su GitHub. Test privato su un frame dell'esempio: riconosciuti 2 gruppi visivi, limite di segmentazione; su immagine originale della prova: 8 gruppi.

## Repository open source confrontati
- [OpenCV](https://github.com/opencv/opencv), Apache-2.0: Canny, contorni e segmentazione; **scelto** perché già compatibile con l'ambiente.
- [VTracer](https://github.com/visioncortex/vtracer), MIT/Apache-2.0: vettorializzazione colorata e percorsi SVG, utile da misurare, **non installato** in V2. Native Rust, gestione dipendenze extra.
- [svgpathtools](https://github.com/mathandy/svgpathtools), MIT: animazione/analisi di path SVG, interessante solo con sorgenti vettoriali; **non installato**.
- [scikit-image](https://github.com/scikit-image/scikit-image), BSD-3-Clause: skeleton e analisi regioni, non necessario nel prototipo.
- [Manim Community](https://github.com/ManimCommunity/manim), MIT: grafica animata avanzata, ma toolchain troppo pesante per default ad alto volume.

L'implementazione originale usa solo OpenCV, NumPy, Pillow e FFmpeg; non incorpora codice di terzi e non richiede servizi a pagamento. Le dipendenze e licenze restano quelle delle rispettive librerie.

## Effetti e comportamento
- `stroke_draw`: contorni via Canny/contour paths, poi colore da **identica sorgente**.
- `object_stagger`: gruppi/forme estratte da una sola immagine su carta chiara, rivelati uno dopo l'altro.
- `pigment_bloom`: pigmento con fronte irregolare e leggermente sfumato.
- `director_mix`: tratto iniziale, poi colore in gruppi in ordine visivo.
- `auto`: per libri/storybook suggerisce `director_mix`, mystery `stroke_draw`, soft `pigment_bloom`; neutro o `artvision_*` → `none`. Non è analisi semantica del copione.

Fondi scuri, immagini senza bordo carta uniforme e opere autentiche non si forzano: fallback `none`. Vietate dissolvenze tra dipinti o blending di scene differenti. La sorgente è sola e nessun viso è tagliato per obbligo di `fill`.

## Test effettuati
Laboratorio locale: quattro prove H.264 silenziose, ognuna 3 s, 72 frame, 360x640, 24 fps; ~2–4 s ciascuna sul container di prova, tempo non garantito su runners. Test unitari: 5/5 passati (raccomandazione sicura, gruppi, 4 render, SHA e prevenzione sovrascrittura, fallback, rifiuto MP4 come input). Il comportamento estetico richiede controllo umano e prova con voice-over reale.

## Da Android
Eseguire i test del workflow della PR. Su branch sperimentale la voce *Run workflow* potrebbe non apparire finché il workflow non è sul branch predefinito. Il check PR genera artifact scaricabili sul telefono; non avvia la pipeline master.

Comando equivalente (immagine illustrativa verificata, non video finito):

```sh
python src/illustration_reveals_lab_v2.py --image ILLUSTRAZIONE.png --out output/creative-reveals/SCENA_V2.mp4 --effect auto --mood storybook --duration 3 --fps 24
python -m unittest discover -s tests -p 'test_illustration_reveals_lab_v2.py' -v
```

## Priorità consigliate prima della produzione
1. Scegliere **una sola scena** dal dossier di un libro e riusare illustrazione originale, cue e voce; non cercare di ricostruire il percorso dei tratti da MP4 finale.
2. Per vera qualità superiore al riferimento, quando possibile creare illustrazioni con livelli separati per personaggi/oggetti. Componenti connesse automatiche possono fondere due soggetti che si toccano.
3. Considerare VTracer/svgpathtools solo se una prova A/B su asset approvati dimostra un miglioramento netto rispetto a OpenCV; non aggiungere altre dipendenze senza valore misurato.
4. Il video completo e l'audio devono restare invariati in fase di prova. Non pubblicare automaticamente. Registro finale: `technical_preview_needs_artist_review`.
