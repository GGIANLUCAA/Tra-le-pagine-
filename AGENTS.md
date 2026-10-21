# Istruzioni operative per GPT e agenti di produzione video

Questo repository è lo studio video di Gianluca. Leggi questo file **prima di
proporre o produrre un filmato**. Non ricostruire il sistema da zero a ogni chat.
Le istruzioni esplicite dell'utente nella sessione hanno precedenza.

## Punto di ingresso

1. Leggi `config/video_formats_v13.json` e `docs/GPT_VIDEO_PLAYBOOK.md`.
2. Identifica il formato dall'intento, non dalla sola parola "arte":
   - libro, racconto, fiaba → `libri`;
   - pittore + musica, senza voce → `artvision_cinema`;
   - spiegazione/commento di un'opera → `artvision_critico`;
   - cronaca e attualità → `controluce`;
   - musica e geometrie → `visual_music`; variante luminosa → `hyperlumen`.
3. Usa `python src/video_director_v13.py formats` per verificare le capacità reali.
4. Recupera la ricetta `VIDEO_RECIPE_V13.json` del video di riferimento, se esiste.
   In assenza, cerca copione, WAV, storyboard, configurazioni e sorgenti originali.
   Non dedurre con certezza motore vocale o font dal solo MP4.
5. Prepara il lavoro con `brief --format ... --topic ... --out ...`. Completa i
   file della scheda, poi esegui `check --project .../PROJECT_V13.json`.

## Preferenze già stabilite

- Narrazione italiana Google Gemini, profilo **Gacrux**, salvo richiesta diversa.
  Riutilizza un WAV verificato quando copione e profilo non cambiano. Il cache
  locale di `gemini_voice.py` richiede WAV e manifest coerenti nella stessa cartella.
- **Nessun sottotitolo** nei nuovi filmati: V12 prevale sui vecchi README.
- Libri: prima protagonista, situazione, fatti, scelte e conseguenze; una breve
  riflessione finale. Immagini belle e pertinenti alla frase, personaggi coerenti.
- ArtVision senza parlato: **Cinema V6 Gold Master**, mai V5 per sbaglio.
  Per un nuovo artista prepara focali e storyboard specifici; il workflow Van Gogh
  non diventa universale cambiando il nome. Non modificare la baseline approvata.
- Critico: leggere la guida della **serie V2**, successiva al primo patto visivo.
  Copertina con titolo opera grande + artista; niente frasi decorative italiane.
  Non applicare questa copertina a Cinema V6, che ha una diversa identità approvata.
- Effetti motivati, movimenti armoniosi, niente confusione o ripetizione meccanica.
  Il parallax esistente è una camera su immagini, non animazione AI dei personaggi.
- Un solo filmato finale per richiesta; niente due varianti non richieste.
- Pubblicazione e caricamento su un sito pubblico seguono l'autorizzazione della
  sessione. Una richiesta di produzione non implica distribuzione pubblica.
- Lavora autonomamente entro le autorizzazioni già date. I controlli editoriali
  sotto sono lavoro dell'agente, non richieste ripetute di conferma all'utente.

## Produzione e controlli obbligatori dell'agente

1. Ricerca fatti/fonti e materiali. Riusa asset approvati, poi cerca originali
   autorizzati, genera soltanto quelli mancanti. I riferimenti altrui sono esempi
   di regia: non copiare audio, immagini o loghi senza autorizzazione.
2. Scrivi un copione originale e uno storyboard con soggetto/azione per scena.
   Confronta visivamente le immagini con il parlato; registra ciò che hai controllato.
3. Controlla asset e provenienza **prima** di consumare TTS. Non sostituire immagini
   mancanti con disegni di debug in un filmato presentato come finito.
4. Usa i renderer e workflow indicati nel registro. Per moduli branch-only o
   sorgenti mancanti, recupera e verifica il codice; non inventare capacità installate.
5. Leggi `ALLINEAMENTO_VOCE.json`: i tempi `estimated` richiedono revisione della
   sincronizzazione. Anche ASR non dimostra da solo accuratezza perfetta.
6. Controlla con ffprobe video+audio, durata, risoluzione, codec e assenza di
   sottotitoli. Guarda inizio/fine e fotogrammi di ogni scena, ascolta voce/musica,
   correggi tagli, errori di lettura, soggetti fuori quadro e chiusure brusche.
7. Salva `VIDEO_RECIPE_V13.json`: hash di MP4 e materiali, commit, preset, motore
   reale, tempi, controlli e riferimenti. La ricetta non contiene chiavi o URL firmati.
8. Consegna MP4 e copertina reali. Se autorizzata la sincronizzazione, importa nel
   sito e verifica scheda/anteprima/player; non confondere upload, catalogo e playback.

## Stati e onestà sul risultato

- `planned`: scheda pronta; `ready_for_production`: asset/editoria controllati;
  `rendered_needs_review`: file verificato tecnicamente, revisione artistica pendente.
- Non dichiarare "completo" una voce sola, uno storyboard o una run in coda.
- Non dichiarare 4K un 720p/1080p e non garantire approvazione estetica o assenza di ban.
- Se manca qualcosa, recuperalo autonomamente quando possibile; altrimenti indica
  il blocco preciso e il materiale ancora necessario, preservando il lavoro svolto.

## Modifiche al codice

- Conserva Gold Master, vecchi video e motori. Estensioni e versioni nuove sono additive.
- Non attivare modelli candidati, nuovi costi o pubblicazione per risolvere un errore
  senza base nella richiesta. Non esporre credenziali, token o link temporanei.
- Esegui i test pertinenti di `.github/workflows/video-director-v13-check.yml`.
- L'archivio `integrations/video_library_laboratorio/` è una copia dei sorgenti
  consegnati: non dimostra quale versione sia installata sul servizio live.

## Pre-lancio e selezione creativa V18

Prima della prima pubblicazione o per preparare una scorta usare [docs/PRELAUNCH_V18_GUIDA.md](docs/PRELAUNCH_V18_GUIDA.md), `src/prelaunch_editor_v18.py` e `src/creative_memory_v18.py`. Le nuove proposte sono bozze, non video pronti né stime di successo; le preferenze del pannello Android sono locali/esportabili e non alterano la coda. Controllare se esiste già una ricetta V13 completa prima di ricreare scene/voce. Non interpretare gli hash come approvazione artistica e non pubblicare automaticamente. Mantieni le regie approvate e gli altri motori invariati.

## Obiettivo economico e apprendimento

Leggere `docs/STRATEGIA_CREATOR_V13.md` prima di pianificare nuovi contenuti.
Compilare il contesto `business` della scheda: pubblico, promessa, valore originale,
obiettivo, una prova, budget e invito finale. Nessuna crescita o entrata garantita.
Usare `src/creator_metrics_v13.py` sui dati reali disponibili; dati mancanti restano
sconosciuti. Non copiare KPI arbitrari dai repository di marketing.

## Priorità corrente: crescita V14

Leggere `docs/PIANO_CRESCITA_V14.md` e `config/creator_growth_v14.json`.
La crescita dei canali propri precede per ora commissioni, sponsor e proposte
a editori/aziende: non suggerire outreach o servizi come prossima azione.
Preservare i format approvati. Pianificare secondo capacità con
`src/creator_growth_v14.py`; cercare prima nel catalogo e nei riferimenti.
Recuperare le lezioni pertinenti quando disponibili (schema in
`templates/CREATOR_LEARNING_V14.json`); se assenti, dichiarare che mancano.
Una sola variabile per prova; nessuna crescita garantita o pubblicazione implicita.
Il piano V14 prevale sulle priorità commerciali delle guide V1/V13.

## Produzione intensiva V15 — istruzione più recente

Leggere `docs/PRODUZIONE_INTENSIVA_V15.md` e `config/production_v15.json`.
Target: almeno 10 video finiti e controllati al giorno, con lavoro autonomo
dell’agente. Il precedente limite di due video/settimana è superato.
Preparare scorta, lotti paralleli, recupero dei materiali e revisioni dell’agente;
non richiedere conferme per ogni operazione già autorizzata.
Usare `src/production_batch_v15.py` per preflight e registro giornaliero.
Il modulo di coda non è ancora un servizio completo di render continuo: non
dichiarare attivo ciò che resta da integrare. Contare soltanto consegne distinte
verificate, non tentativi, bozze o file duplicati. Distinguere produzione e distribuzione.

## Esecuzione V16

Leggere `docs/PRODUZIONE_AUTONOMA_V16.md`. I pacchetti preparati della coda V15
si eseguono con `src/production_runner_v16.py run`: tre adapter ammessi, processi
isolati, checkpoint e ripresa. Non basta una bozza del copione: recuperare gli asset
e la voce verificata. Rivedere master e kit, poi registrare una revisione con hash
esatti in `queue/reviews_v16/`. Nessuna approvazione ripetuta all’utente per lavoro
già autorizzato. Se mancano asset o capacità, indicare il blocco, non inventare
dieci consegne. I master non revisionati restano nel pacchetto di lavoro.

## Regia qualità aggiuntiva V17 (senza API, non distruttiva)

Leggere [docs/QUALITY_DIRECTOR_V17.md](docs/QUALITY_DIRECTOR_V17.md) e `config/quality_director_v17.json`. Prima della produzione, dove esiste una scheda V13, eseguire `python src/quality_director_v17.py --project PATH/PROJECT_V13.json --out PATH/quality-preflight`: correggere le segnalazioni realmente rilevanti senza snaturare il preset. Per i lavori V16 il report finale V17 viene salvato accanto al master e al kit di revisione. V17 non certifica la bellezza, non verifica automaticamente le opere e non sostituisce la visione/ascolto integrali. Nessuna nuova API né costi obbligatori. Per nuove categorie creare una nuova policy, non modificare Cinema V6 Gold Master, Critico V2 o la voce Google già riuscita.
