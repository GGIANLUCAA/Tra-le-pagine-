# Crea il prossimo video partendo dal lavoro già riuscito

**GPT: leggi [AGENTS.md](AGENTS.md), poi il
[Playbook](docs/GPT_VIDEO_PLAYBOOK.md) e il
[registro dei formati](config/video_formats_v13.json).**

Gianluca può chiedere normalmente:

> Crea un video su [argomento] usando il progetto Tra-le-pagine-.
> Segui START_HERE_GPT.md. Mantieni le tecniche approvate e consegna il filmato finito.

Oppure:

> Usa la voce del video X e la regia del video Y. Recupera le loro ricette,
> riutilizza i materiali adatti e genera soltanto ciò che manca.

La guida funziona quando GPT ha accesso al repository e la legge; non modifica
automaticamente tutte le chat o installazioni di ChatGPT. Per iniziare da un'altra
chat condividi questo file o il link del repository.

## Comandi, senza consumo di API

```bash
python src/video_director_v13.py formats
python src/video_director_v13.py brief --format libri --topic "Titolo del libro" --out output/nuovo_video
python src/video_director_v13.py check --project output/nuovo_video/PROJECT_V13.json
```

`brief` crea la scheda e istruzioni specifiche. `check` identifica materiali e
revisioni mancanti. Sono strumenti per l'agente: non generano da soli immagini,
voce o MP4. L'agente prosegue con i motori esistenti indicati nel piano.

Il percorso dei libri con `episode_v3.py --post` registra automaticamente la ricetta
del video finale. Per gli altri formati usare `capture` dopo il render, come nella guida.

## Obiettivo economico e apprendimento

Leggere `docs/STRATEGIA_CREATOR_V13.md` prima di pianificare nuovi contenuti.
Compilare il contesto `business` della scheda: pubblico, promessa, valore originale,
obiettivo, una prova, budget e invito finale. Nessuna crescita o entrata garantita.
Usare `src/creator_metrics_v13.py` sui dati reali disponibili; dati mancanti restano
sconosciuti. Non copiare KPI arbitrari dai repository di marketing.
