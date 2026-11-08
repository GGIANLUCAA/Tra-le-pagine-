# ArtVision Critico — QA regia collegata al MP4 reale (08/11/2026)

## Implementazione verificata

Il modulo `src/artvision_critico_review_capture_v1.py` viene chiamato automaticamente a fine **render** nei cinque generatori standard già esistenti:

- `artvision_rebel_critico_standard_v144.py`
- `artvision_simberg_garden_critico_v146.py`
- `artvision_bruegel_triumph_critico_v151.py`
- `artvision_waterhouse_magic_circle_critico_v159.py`
- `artvision_blake_ghost_flea_critico_v159.py`

Senza alterare il montaggio, registra le coordinate dei crop **realmente calcolate durante il render** ogni 10 frame, legge l'esatto WAV Gacrux e il `VOICE_CACHE_V13.json` allineato con ASR, e preleva dal vero MP4 tre JPG per frase (inizio/centro/fine). Confronta hash MP4 e WAV, salva il report `FOCUS_REVIEW_V1/ARTVISION_CRITICO_REAL_MP4_FOCUS_QA.json` e include report e immagini nello ZIP. La QA originale FFmpeg, SHA, ZIP e i divieti di pubblicazione rimangono invariati. Una fotografia generata o una stima dai soli testi non è un frame di prova.

## Prova indipendente con vero video precedente

- Video: Bruegel, *The Fall of the Rebel Angels*, Critico Standard V144.
- Source: Action run [41803668367](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41803668367), artifact id `13309290632`, fonte non scaduta all'audit.
- WAV SHA-256: `e50f97bf6bf272bdda3a1b8577acf492f974d5c88d2b336d35cf976c5a814ade`.
- MP4 SHA-256: `83aad1da82a091de42aa19ca6bd532a0e2a2b21c27f4c4c34eac5e53c8799f39`.
- Audit: [run 42471442030](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42471442030), 18 frasi ASR, **54 JPG da veri frame MP4**, full decode e SHA validati.
- Artifact di soli fotogrammi/report: `ARTVISION_V144_REAL_FOCUS_REVIEW_ONLY`, id `13613787062`; non è un nuovo master, non ha una verifica artistica e ha retention temporanea.
- Esito reale: `needs_camera_trace_and_semantic_review`, poiché il video V144 PRECEDENTE non conteneva ancora la telemetria del nuovo renderer. Questo non equivale a un errore nel video né a un PASS artistico.
- CI sintetica in `.github/workflows/artvision-narrative-focus-qa.yml`: 12 test gate frase-camera e 5 test capture compresi MP4 fisico; nessun test saltato quando FFmpeg è configurato.

## Uso futuro e funzionamento del loop

Per i nuovi renderer che ereditano questo codice, ogni produzione emette l'evidenza contestualmente al render. Per un altro Critico o per Museum già esistente si può fare la stessa estrazione senza ridoppiare la voce, usando la CLI:

```bash
python src/artvision_critico_review_capture_v1.py \
  --video /cartella/CRITICO_MUSEUM_REVIEW.mp4 \
  --wav /cartella/VOCE.wav \
  --voice-cache /cartella/VOICE_CACHE_V13.json \
  --variant critico_museum \
  --voice-offset-s 3.5 \
  --video-duration-s 110.0 \
  --expected-video-sha256 SHA256_VERIFICATO_64_CARATTERI \
  --output-dir /cartella/FOCUS_REVIEW
```

I numeri dell'esempio non vanno copiati: offset, durata e SHA devono provenire dalla revisione vera del singolo MP4. Se il renderer Museum non fornisce una traccia camera misurata, rimane `needs_camera_trace_and_semantic_review`. Una **nuova** versione Museum deve registrare le sue coordinate camera, non copiare quelle dello Standard.

Revisione artistica: per ogni frase valutare i tre JPG e il video a velocità normale; confrontare parole, oggetti e personaggi dell'opera autentica, individuare crop errati/anticipi/ritardi. Memorizzare il difetto nel registro `artvision_learning_loop_v1.py` **solo** dopo reale osservazione del filmato e prove specifiche, proporre una modifica locale, rigenerare soltanto la variante difettosa e ripetere il test A/B. Il gate dettagliato `src/artvision_narrative_focus_gate.py` si esegue quando entrambi i Critico e i rettangoli semantici **verificati sull'opera** sono disponibili: mai inventare `subject_bbox_xyxy` dal centro generico della camera.

**Limite dichiarato:** nessun sistema software di questo intervento identifica da solo il soggetto pittorico; l'automiglioramento semantico completo resta in sviluppo e richiede un revisore visivo. `needs_visual_and_semantic_review` non è Gold V25, non autorizza pubblicazioni, non è una quarta variante aggiunta né un video finito per la coda. Non creare un'altra automazione concorrente, non modificare vecchi master né i loro SHA.
