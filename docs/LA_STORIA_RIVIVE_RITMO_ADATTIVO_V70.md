# LA STORIA RIVIVE — REGIA PSICOVISIVA ADATTIVA V70
**Decisione dell'utente, 29/10/2026, dopo analisi del file storico 44274.mp4.**

## Scopo e precedenza
Queste sono **regole di processo severissime**, non uno stampino di montaggio. Si applicano ai **NUOVI video storici** del format `storia_rivive` e NON alterano i master già esistenti, il progetto libri o il protocollo ArtVision per le quattro varianti dei quadri. Restano prioritari V59 (fonti PD/CC0), V61 (film autentico B/N in movimento → congelamento su frame originale → NUOVA foto AI ferma a colori), V64/V66 (fotorealismo ma fedeltà dell'identità e geometria), V55 (MP4 + cover + social + ZIP + consegna/archivio verificati), divieto spese e autopubblicazione.

Il colore deve **sorprendere e appagare**, non saturare con tagli identici. Durata finale **14–35 secondi**, media desiderata **25 secondi** su molti episodi, non un obiettivo forzato per il singolo video. Non aggiungere scene deboli o code vuote per arrivare a 25 s.

## Prima del rendering, obbligatorio per ogni singolo video
1. Visionare realmente fonte archivistica e scene candidate; documentare URL, stato PD/CC0 del singolo file e giurisdizione, qualità della scansione, inquadratura 9:16, volti/gesti/mezzi reali e momenti in cui l'immagine attira lo sguardo. Se non è stata visionata, segnare **NON VERIFICATO**, non inventare.
2. Per ogni scena candidata individuare l'**esatto frame autentico** da congelare, con timecode reale; foto ricostruita AI deve corrispondere proprio a quel frame. Registrare nel JSON `source_frame_timecode_s`; il planner calcola `start_s` in base all'ultimo frame effettivamente emesso a 30 fps: `start_s = source_frame_timecode_s - (round(motion_s*30)-1)/30`. Non spostare la posa o il volto per esigenze di ritmo.
3. Compilare **evidenza del frame** (`visual_evidence`, descrizione concreta con timecode), categoria (`scene_type` = face/action/wide/detail/climax), gruppo di composizione, evento unico e ruolo narrativo. Motivare su scala 1–5 *emotional_value, visual_complexity, motion_value, image_quality*. Non spacciare punteggi algoritmici per osservazioni reali.
4. Conservare **l'ordine storico o editoriale già deliberato**: la pianificazione può tagliare scene ridondanti ma non riordinare fatti cronologici per creare un evento mai avvenuto.
5. Avviare il **planner** prima di generare foto o video e conservare il JSON di progetto completo con piano e le scene scartate; senza dati verificati il progetto è BLOCCATO, non può risultare «video finito».
6. Solo dopo pianificazione: vero restauro image-to-image vincolato alla fonte, scelta audio e accenti sulla trasformazione, render finale e QA V64/V66/V55. Il planner non esegue analisi CV del video o restauro: richiede un precedente passaggio effettivo di visione/selezione.

## Tempi per fase — soglie di controllo, NON slot costanti
| Fase | Finestra normale | Motivo |
|---|---:|---|
| Filmato B/N **in movimento** | 0,55–1,80 s | Il soggetto va riconosciuto senza annoiare |
| Trasformazione frame→foto | 0,18–0,80 s | Sorpresa visiva, conservando lo stesso fotogramma |
| Fotografia AI **ferma e colorata** | 1,05–3,05 s | Il pubblico deve poter osservare nuovi dettagli |
| Primo reveal completato | entro 1,50 s | Partenza incisiva, nessun logo/nero iniziale |
| Durata video finito | 14–35 s | Media su più video ~25 s, *non* durata prestabilita |

Il planner genera un punto di partenza **diverso per tipo di scena**, poi pondera movimento, complessità, emozione e varietà dei tagli: un volto espressivo, un'azione, una panoramica complessa o un climax non hanno lo stesso tempo. Queste soglie **sono ipotesi registiche sperimentali, non numeri psicologici universali**; eventuali variazioni di policy richiedono confronti reali, non ogni nuovo capriccio del montatore.

## Stop obbligatori — non "avvisi decorativi"
- Durata fuori 14–35 s, primo reveal oltre 1,5 s, colore troppo breve, 3 cicli quasi identici o 3 composizioni uguali consecutivamente: **REJECT_PACING**.
- Ritagli della stessa ripresa trattati come scene nuove, debolezza della fonte, volti tagliati, eventi non distinguibili, frame congelato diverso dalla foto IA: **REJECT_SOURCE_OR_VISUAL**.
- Fonte senza licenza PD/CC0 verificata, inventare persone/oggetti, geometria diversa, identità artefatta, musica non licenziata, uso di Vidu o GPU a pagamento non autorizzati: **REJECT_RESTORATION_OR_RIGHTS**.
- I video tecnicamente renderizzati **non sono Gold Master né pubblicabili** fino alla revisione del filmato intero (anche su Android): ritmo, chiara riconoscibilità, fedeltà, emozione, qualità dell'audio, copertina, MP4/ZIP e archivio V55.

## Variabilità voluta, non casualità
- **14–19 s**: breve e intenso, quando poche scene possiedono forte significato; nessun riempimento.
- **20–29 s**: naturale per la maggior parte dei reel; circa 25 s come media editoriale ma il numero di scene può variare.
- **30–35 s**: mini-storia con reale progressione o momenti molto ricchi; non solo ripetizione del colore.
- Le transizioni possono cadere sugli accenti musicali, ma l'audio va realmente ascoltato e sincronizzato: il planner non inventa beat rilevati.
- Cambiare scala visiva quando racconta qualcosa: persone → lavoro → movimento → panoramica → dettaglio → payoff. **Non rendere obbligatoria questa sequenza**. Non inventare nuovi personaggi o movimenti.
- Variare le durate nel singolo video; conservare per confronto tre ritmi **rapido/equilibrato/contemplativo**, scelti per contesto, non ruotati casualmente.

## Comandi tecnici (gratuiti, utilizzabili nel repository/GitHub Actions)
```bash
python src/storia_rivive_pacing_v70.py plan --input drafts/storia.json --output output/storia_paced.json
python src/storia_rivive_pacing_v70.py check --input output/storia_paced.json
# In seguito il renderer V61 legge il piano output, non il draft iniziale.
python src/storia_rivive_photo_freeze_v61.py --plan output/storia_paced.json --check
```
**Nota:** i comandi non trovano fonti da soli e non generano foto AI; la revisione visiva prima e dopo resta obbligatoria. `TIMING_PLANNED_NOT_VIDEO_QA` è uno stato pianificato, **mai** «approvato» né «MP4 consegnato». I vecchi esperimenti V61 con `test_only=true` restano eseguibili, ma non sono finali consegnabili.

## Come valutare se il mix funziona sul pubblico
Non ottimizzare a intuito usando una sola pubblicazione. Confrontare stesse fonti/scene con montaggi rapidi, equilibrati e più contemplativi; mantenere per quanto possibile stesso titolo, ora e audience. Monitorare retention iniziale, secondi medi di visione, completamento, rewatch, condivisioni per reach e giudizio qualitativo sul «WOW». Nessuna metrica singola dimostra causalità, e i video più brevi partono avvantaggiati sul completamento. Correggere il preset globale solo con risultati ripetuti e verificati.

**Precedenza:** richiesta esplicita dell'utente → regole attive / format → V70 adattivo → scelte motivate per l'episodio. Il rispetto della fonte e delle persone reali ha precedenza assoluta sulla viralità.
