# V34 — Selettore automatico delle fonti per scene

**Stato:** motore di instradamento/riuso operativo e verificabile da Android. Le immagini NON sono selezionate e approvate artisticamente da un modello. Niente pagamento, download, generazione, montaggio o pubblicazione in automatico.

## Perche esiste
Ogni volta che creiamo un video, la prima domanda non e "quale servizio ha foto disponibili?" ma "**qual e il contenuto esatto della scena?**". Il V34 legge le regole V33, le scene e (se disponibile) un catalogo di immagini gia controllate. Propone una strada adatta al format; tenta il riuso **solo se la risorsa e associata alla stessa scena e i controlli sono indicati come svolti**.

### Percorso di decisione

- `fictional_action`: scene letterarie precise → asset originali coerenti, altrimenti prova AI Horde **esplicita** (limite tre per il prototipo). Niente stock generico spacciato per sequenza narrativa.
- `establishing`: ambiente generico (solo se pertinente) → libreria, Openverse V7, Pixabay; eventuale illustrazione originale.
- `authentic_artwork`: quadro autentico → museo/Open Access, Commons e fonte primaria, **mai sostituito da AI**.
- `documentary_evidence`: prove reali → documento autentico e verificato. Se non c'e, interrompere e distinguere eventuale ricostruzione.
- `documentary_broll`: filmato o fotografia di atmosfera → archive, Openverse, Pixabay selezionato; nessuna falsa attribuzione al fatto storico.
- `music_visual`: visualizzazioni a tempo → fonti e grafica sincronizzate; nessuno stock per riempire.

Il V34 **non inventa la verifica** dei media. Il nome Pixabay e corretto e il bridge usa il secret GitHub `PIXABAY`, con `PIXABAY_API_KEY` come alias se presente. Altre 45 fonti sono catalogate ma non tutte chiamabili automaticamente.

## Da Android (senza ulteriori account)

1. Aprire [Actions → Selettore fonti V34](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/selettore-fonti-v34.yml).
2. `Run workflow`: selezionare `example=libri`, `mode=plan` e avviare. **Zero API e zero immagini generate**.
3. Dalla run aprire **Artifacts** e scaricare `SELETTORE_FONTI_V34_...`. Estrarre lo ZIP e aprire `SCHEDA_FONTI_ANDROID_V34.html`; trovi decisione e fallback per scena, anche offline.
4. Se vuoi provare la ricerca di immagini stock: `example=controluce`, `mode=discover`, `scene_id=broll_citta`, `provider=openverse` oppure `pixabay`, `query=city skyline night`, `limit=3`. Risultano **candidati da revisionare**, non file scaricati.
5. Dopo aver controllato licenze, accuratezza e qualità, conservare i media approvati in archivio. Per nuove illustrazioni dei libri si usa **separatamente** [Immagini gratuite V1 / AI Horde](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/immagini-gratuite-v1.yml).

## Comandi dal repository

```bash
python src/source_selector_v34.py --mode plan --brief config/image_pipeline_v1_demo.json --out output/selettore_v34
python src/source_selector_v34.py --mode plan --brief config/source_selector_v34_demo.json --out output/selettore_v34_controluce

# Solo una ricerca per una scena di B-roll, con API key Pixabay in GitHub secret:
python src/source_selector_v34.py --mode discover \
  --brief config/source_selector_v34_demo.json --scene broll_citta \
  --provider pixabay --query 'city skyline night' --limit 3 \
  --out output/selettore_v34_discovery
```

Per usare un catalogo di materiali precedenti fornire `--catalog /percorso/catalogo.json` con `assets` e per ciascuna immagine: `scene_id` esatto, `source_kind`, `provider`, `source_reference`, `rights_review=reviewed`, `visual_review=passed`, `scene_relevance=reviewed`, piu `authenticity_review=reviewed` per opere/prove autentiche e `sync_review=passed` per materiali musicali. Queste sono **dichiarazioni registrate**, da accompagnare alla prova reale (file, hash, crediti), non approvazioni automatiche dell'agente. L'output segnala candidati associati, non certifica la presenza fisica del file.

## Collegamento reale

- `src/source_selector_v34.py`: per-scene routing e confronto con asset gia rivisti; `SCHEDA_FONTI_ANDROID_V34.html` e `PIANO_FONTI_V34.json`.
- `src/studio_ibrido_v6.py` aggiunge ai cue `source_need_v34` e `priority_sources_v34` (nessuna API). Un cue puo specificare `source_need: establishing` per libri o `documentary_broll` per cronaca; in assenza la scelta e prudente.
- `src/free_sources_bridge_v1.py`: solo per `mode=discover`, una sola ricerca Pixabay o Openverse; nessun download.
- `src/media_source_priority_v33.py`: il preflight V13 continua a richiedere revisione dei diritti/provenienza per i **nuovi** progetti.
- V34 non modifica il renderer V5, Gemini Gacrux, la videoteca o i master precedenti.

## Limiti e prossimi passi

Questo e un primo **selettore per metadati**, non un motore di riconoscimento delle immagini o un'automazione massiva di importazione. Non identifica da solo la correttezza di volti, prospettive o testi in un'immagine. Non chiama tutti gli archivi catalogati e non genera piu immagini AI: integra suggerimenti e riuso verificabile.

**Pixabay** ha regole contro richieste automatiche massive, richiede cache di 24h e revisione dei contenuti; nel workflow Github la cache tra run non e ancora implementata: **evitare di ripetere la stessa ricerca**. Il materiale di ogni archivio richiede la propria licenza, anche quando l'endpoint e pubblico.

Solo dopo prove vere e misurazione di tasso di immagini approvate, tempi e limiti passare ad altri adapter o grandi batch. Nessun account aggiuntivo o nuova spesa e necessaria per questa versione.
