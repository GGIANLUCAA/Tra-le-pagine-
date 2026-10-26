# Creative Reveals V3 — regia narrativa sperimentale (26/10/2026)

**Stato:** candidato da valutare, non regola permanente. Non modificare V6, V12, V13, V33, V38, voce Gacrux, master storici, Video Library o pubblicazione. **Nessuna API AI e nessuna produzione a pagamento.**

## Nuova capacità

La V2 genera tratti e colori senza comprendere la storia. La V3 separa:

1. **Regista editoriale** — `src/narrative_reveal_director_v3.py`: a partire da scene con frasi, intervalli, intenzioni, descrizione immagine e coordinate dell'oggetto, genera per scena un piano con effetto/opzione nessun effetto, inizio rispetto alla voce, durata e tempo per leggere l'immagine completa. I dati semantici/ROI sono forniti dall'editor: **non sono riconosciuti automaticamente** da un LLM o da OpenCV.
2. **Renderer non distruttivo** — `src/narrative_reveal_renderer_v3.py`: da una sola illustrazione approvata crea un nuovo MP4 muto della **singola scena**. Con ROI `[x,y,w,h]` normalizzata, tutto ciò che è esterno alla ROI rimane l'immagine originale. Non c'è trasparenza fra scene.
3. **Confronto pratico** — `examples/creative_reveals_storyboard_v3.json`: racconto originale dimostrativo di 152 secondi con 14 scene. Il planner ne anima solo quelle con ragioni narrative; apertura/climax/emozione/finale generalmente restano leggibili senza transizioni. Tempi **stimati**, non sincronizzati alla voce.

## Filosofia della regia

- Hook: mostrare subito il soggetto, mai fare attendere su pagina bianca.
- Indizio: riconoscere e dare peso solo all'oggetto realmente nominato. Se manca ROI verificata, effetto `none`.
- Scoperta/meraviglia: disegno progressivo o colore locale quando aggiunge significato, non ogni tot secondi.
- Emozione/dialogo/finale: conservare la pausa e un'immagine completa. Non imporre numero, tipo o durata fissa di effetti.
- Sincronia: i campi `start_s`, `end_s`, `anchor_offset_s` diventano affidabili **solo dopo ascolto della voce effettiva**. `--audio` misura durata e hash del file, ma non identifica magicamente le parole. Lo stato resta `preview_only_needs_artistic_review`.
- Custodia materiali: sorgenti autentiche e licenze V33 restano da verificare. In una demo `visual_review=editorial_mock` significa *solo simulazione*, mai certificazione dei diritti.
- Limitazioni: sfondi non carta, oggetti toccanti, volti complessi: fallback sicuro all'immagine originale. Nessuna segmentazione semantica certa, nessun auto-rimontaggio del film completo.

## Prova riproducibile

```bash
python src/narrative_reveal_director_v3.py --story examples/creative_reveals_storyboard_v3.json --out output/creative-reveals/REGIA_STORIA_V3.json

python src/narrative_reveal_renderer_v3.py --plan output/creative-reveals/REGIA_STORIA_V3.json --scene scena_04 --image /percorso/ILLUSTRAZIONE_APPROVATA.png --out output/creative-reveals/SCENA_04.mp4

python -m unittest discover -s tests -p 'test_narrative_reveal_v3.py' -v
```

La prova Actions della PR genera una sorgente procedurale specifica con una chiave in posizione corretta e renderizza `scena_04`, non una storia narrata completa. Scaricabile da Android dagli artifact. Nessuna chiave API, nessun nuovo PC.

## Prima di proporre produzione su un vero episodio

1. Recuperare dossier, illustrazioni approvate, `scene_cues.json`, audio Gacrux già creato, eventuale `ALLINEAMENTO_VOCE.json`. Mai inventare timestamp di voce.
2. Studiare la narrazione, distinguere oggetti e momenti di scoperta; selezionare `focus_roi` visiva e timelining in base al parlato reale, non a parole isolate.
3. Confrontare sul medesimo MP4 originale le scene senza e con effetto, ascoltando lo stesso audio; verificare che l'oggetto risulti riconoscibile quando viene nominato e che il fermo immagine resti leggibile.
4. Solo dopo il controllo artistico, decidere **se** collegare questo modulo al renderer di produzione, in modo esplicitamente opt-in e con rollback. Questa PR non esegue il rimontaggio di due o tre minuti.

**Costi:** crediti AI per regia/render effetti: zero; rimangono risorse di calcolo/Actions e possibili costi già previsti per la produzione originale di voci o asset.
