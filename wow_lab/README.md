# ArtVision — WOW LAB V1 · zona completamente separata

**Autorizzazione:** 29 ottobre 2026: generatore creativo autonomo dentro `GGIANLUCAA/Tra-le-pagine-` SENZA alterare alcuna logica, memoria, regola o automazione precedente.

## Confine tecnico

- **Unica cartella del modulo:** `wow_lab/`. Unico workflow nuovo: `.github/workflows/wow-lab-isolated-v1.yml`.
- **Nessun import né modifica** di `src/`, `config/`, `docs/`, `site/`, `worker/`, `AGENTS.md`, `START_HERE_GPT.md`, delle code, dei preset o dei 4×1.
- L'automazione madre ArtVision V58/V68 e la produzione storica V74/V82 restano intatte e NON vengono chiamate o sbloccate.
- Proprio scheduler ogni due ore in **UTC** e proprio gruppo di concorrenza. Trigger GitHub su `main`, nessun nuovo ChatGPT task.
- Artefatti e release separati, con prefisso `WOW_LAB_` / `wow-lab-v1-`; non importare nel sito né pubblicare sui social senza revisione umana.
- Nessuna nuova API a pagamento, GPU, Vidu, connessione segreta o costo approvato; solo GitHub-hosted runner standard pubblico, Pillow/OpenCV/FFmpeg e Met Open Access. Minuti e disponibilità GitHub restano dipendenti dalla piattaforma.
- **Stop:** `wow_lab/config.json > enabled=false` o disattivare il workflow da Actions; non rimuovere né modificare altre automazioni.
- Sviluppo su ramo separato, verifiche prima dell'eventuale merge sul default branch.

## Contratto editoriale

- Opera originale autentica, identificazione oggetto sul sito del museo e verifica puntuale `isPublicDomain=true` prima di scaricare.
- Ricerca soggetti nuovi e variabilità motivata, evitando l'ultimo soggetto e l'ultima tecnica nei risultati precedenti se disponibili.
- Il test V1 può produrre **cinema 2.5D** con prospettiva, illuminazione e frame portal; **non** spaccia questi effetti per mesh 3D o pop-out di personaggio ricostruito. Per il vero 3D serviranno un modello verificato e un adattatore isolato aggiuntivo.
- Durate e montaggio non stampino: tre ricette indipendenti variabili per soggetto. Nessun semplice zoom descritto come rigenerazione 3D.
- Autocritica automatica limita bug, sorgenti, formati, novità e sincronizzazione. **Il software non può attestare da solo la bellezza, l'emozione o la viralità**; lo stato resta `needs_human_review` fino a revisione.
- Nessun risultato mediocre viene dichiarato master; se il controllo fallisce: **nessuna release finale**, resta il report di fallimento nel job.
- Nessun limite di tempo promesso: GitHub schedule può subire ritardi, run saltate o disattivazione dopo 60 giorni di inattività del repository pubblico.

## Come funziona

1. GitHub Actions `wow-lab-isolated-v1` si avvia ogni due ore (cron `23 */2 * * *`) quando è presente nel ramo `main`.
2. `wow_lab/engine.py` legge esclusivamente `wow_lab/config.json`, legge gli ultimi manifest WOW LAB pubblicati e seleziona una fonte di pubblico dominio.
3. Crea un MP4 verticale con musica originale, copertina, metadati di diritti, descrizioni social in bozza, manifesto con hash SHA256 e autodiagnosi.
4. Verifica l'MP4 tramite ffprobe, decodifica con ffmpeg, differenza fotogrammi. Se supera il QA tecnico, crea un **GitHub prerelease** namespaced e un Artifact (non social).
5. Dall'Android apri `https://github.com/GGIANLUCAA/Tra-le-pagine-/releases`, filtra i tag `wow-lab-v1-` e scarica il file MP4 o ZIP.

**Nota fondamentale:** generazione ogni due ore è un obiettivo operativo, **non una garanzia**. Se fonti, servizio o qualità non sono disponibili il sistema salta e segnala il motivo, senza produrre falso materiale.

## Esecuzione in autonomia (test)

```bash
python -m pip install pillow numpy opencv-python-headless
sudo apt-get install -y ffmpeg
python wow_lab/engine.py --out output/wow_lab --slot 2026-10-29T20 --test-source-id 437133
```

Il test utilizza sempre una vera fonte CC0 Met e non modifica i video precedenti. Cartella output ignorata dalle modifiche permanenti.

### Miglioramento progressivo

`wow_lab/engine.py` legge i manifest del proprio namespace pubblicati come release. La scelta soggetto/ricetta non ripete immediatamente gli ultimi. Registra i difetti tecnici e i dati di produzione; miglioramenti creativi profondi richiedono feedback reale o metrica analytics verificata, non voti inventati. Qualsiasi variazione del codice rimane confinata a `wow_lab/` e passa da test; il motore non può auto-riscrivere regole protette.

### Diritti

The Metropolitan Museum of Art, Open Access / CC0, API documentata su https://metmuseum.github.io/ .
**Si controlla il singolo record**: la presenza nel museo non basta per licenza commerciale.

### Non ancora incluso

- Nessuna mesh 3D vera o rigging, generazione gratuita illimitata, Vidu, critico Gacrux, ripristino storico V74, analytics social, upload in Video Library Studio, moderazione automatica dei contenuti, pubblicazione social. Sono adattatori futuri vincolati ai loro contratti, non caratteristiche da dichiarare già funzionanti.
