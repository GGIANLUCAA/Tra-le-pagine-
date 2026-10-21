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

## Obiettivo economico e apprendimento

Leggere `docs/STRATEGIA_CREATOR_V13.md` prima di pianificare nuovi contenuti.
Compilare il contesto `business` della scheda: pubblico, promessa, valore originale,
obiettivo, una prova, budget e invito finale. Nessuna crescita o entrata garantita.
Usare `src/creator_metrics_v13.py` sui dati reali disponibili; dati mancanti restano
sconosciuti. Non copiare KPI arbitrari dai repository di marketing.
