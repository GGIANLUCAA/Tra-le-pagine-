# AI Director · Dal catalogo alla scena, V34 · 12/11/2026

## Stato del lavoro

Questo collegamento riutilizza la ricerca archivistica senza chiavi (Library of Congress, Wikimedia Commons, Met, Art Institute, Cleveland, Internet Archive, Wellcome), e prepara un pacchetto per il **selettore scene V34 già presente**. Non modifica renderer, owner, cron, G0DM0D3, master, Vidu, Gemini TTS o social.

Per ogni candidato di ricerca produce:

- `SOURCE_INTAKE.json`: scheda con URL verificabile, autore/titolo come **dichiarati dal catalogo**, istruzioni di revisione e vincoli.
- `V34_PENDING_CATALOG.json`: catalogo compatibile con `src/source_selector_v34.py`. Tutti i record conservano `rights_review=pending`, `visual_review=pending`, `authenticity_review=pending`, `scene_relevance=pending`.
- `SOURCE_REVIEW_ANDROID.html`: scheda da telefono con link originali e checklist.
- Con un **vero storyboard V34 e scene_id** si producono anche `PIANO_FONTI_V34.json` e `SCHEDA_FONTI_ANDROID_V34.html`. La fonte resta **source_needed**: non viene scelta come già revisionata.

La ricerca, inclusa la corretta ricostruzione di alias documentati, non basta per passare al render: V34 non seleziona alcun asset non verificato. La presenza di un URL nel catalogo non significa un JPEG disponibile, un video decodificabile o un permesso di pubblicazione.

## Utilizzo da Android

Aprire [AI Director — Fonti senza chiavi](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/ai-director-external-apis-v1.yml). Run workflow con categoria art / historical_video / historical_photo, soggetto e (per i dipinti) nome artista esatto. Dopo esecuzione aprire Artifacts `AI_DIRECTOR_KEYLESS_SOURCES_...`; dentro `source_handoff/SOURCE_REVIEW_ANDROID.html` e `source_handoff/V34_PENDING_CATALOG.json`.

Il report HTML è statico, non aggiornamento live del sito. Zero inferenze a pagamento, nessuna chiave API, nessun file multimediale scaricato o alterato. Europeana rimane esclusa.

## Caso verificato: The Goldfinch, Carel Fabritius

**Ricerca reale**: run GitHub [43193008930](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43193008930); trovato `Fabritius-vink.jpg` su Commons dopo una singola ricerca mirata con alias. E' un record di catalogo, non un originale già letto in byte.

Fonti pubbliche indipendenti consultate il 12/11/2026:

- [Mauritshuis · Il Cardellino, inv. 605](https://www.mauritshuis.nl/it/scopri-la-collezione/collezione/605-il-cardellino): Carel Fabritius, 1654; dimensioni dell'opera 33,5 × 22,8 cm.
- [Mauritshuis · Informazioni per riutilizzare immagini](https://www.mauritshuis.nl/en/contact/requesting-visual-material): download senza royalties con regole editoriali per le pubblicazioni; chiedono un credito che includa pittore, titolo, anno e `Mauritshuis, The Hague`.
- [Commons · Fabritius-vink.jpg](https://commons.wikimedia.org/wiki/File:Fabritius-vink.jpg): immagine candidata 1965 × 3000, dichiarazione PD-Art/Public Domain Mark e provenienza dichiarata.
- [Commons · Carel Fabritius - The Goldfinch - 605 - Mauritshuis.jpg](https://commons.wikimedia.org/wiki/File:Carel_Fabritius_-_The_Goldfinch_-_605_-_Mauritshuis.jpg): alternativa **3.930 × 6.000 pixel**; candidate a maggior dettaglio, **file non scaricato o esaminato integralmente**.

Per la produzione ArtVision mantenere credito proposto: **Carel Fabritius, The Goldfinch (1654). Mauritshuis, The Hague** (verificare formato e collocazione effettiva); ricordare che i titoli video pubblici seguono V134 e che il credito può comparire nel materiale social/descritto anziché sovrapporsi al quadro.

**Non confondere le dimensioni del dipinto (centimetri) con la risoluzione dell'immagine (pixel)**; non dedurre cornice museale o sala autentica da questa immagine. Per le varianti Museum valgono V80/V118/V119 e verifica visiva del MP4 reale.

## Sicurezza

- Accetta soltanto schemi risultati `ai-director-keyless-archives-v1`, sorgenti HTTPS da un elenco chiuso di archivi, con approvazioni e diritti dichiarati **non verificati**. Non esegue rete.
- Rifiuta risultati marcati `approved=true`, richieste con AI a pagamento, link esterni non consentiti, formati media incoerenti.
- Il gate V34 già esistente continua a richiedere revisione di diritti, autenticità, qualità visiva, pertinenza per la scena e per alcune categorie hash/file.
- Nessuna revisione può essere inferita dal nome del file, dal titolo tradotto o da un'etichetta "PD" del catalogo.
- Un file effettivamente scaricato va analizzato in una fase separata: SHA256 dei byte originali, integrità/risoluzione, fonte, diritti Italia, compatibilità di licenza e verifica visiva. Non inventare questi dati.

## Comandi riproducibili (offline)

```bash
python src/ai_director_source_handoff_v1.py \
  --research examples/ai_director_goldfinch_observed_catalogue_20261112.json \
  --scene-brief examples/ai_director_goldfinch_v34_source_scene.json \
  --scene-id work_opening \
  --out output/ai_director_goldfinch_intake

python -m unittest discover -s tests -p 'test_ai_director_source_handoff_v1.py' -v
```

I file in `examples/` sono una **riproduzione documentata del risultato del run reale** per test offline, non una nuova ricerca live. Il workflow di ricerca manuale crea il pacchetto automaticamente per ogni ricerca.

**Prossima fase, non ancora realizzata:** recupero e lettura integrale dell'asset scelto, calcolo SHA256 e identificazione file, QA visivo, collegamento semantico alle scene del vero storyboard, verifica di licenze e crediti, solo poi render di prova. Nessun video è stato prodotto o approvato da questa aggiunta.
