# AI Director V2 · Collegamento reale alle consegne video (12 novembre 2026)

**Stato prima dell'attivazione:** proposta isolata su ramo, test CI e prova su artifact da completare. Non confondere un modulo presente su GitHub con una produzione verificata.

## Scopo
Collegare l'idea G0DM0D3 (regista + critico indipendente) ai VERI file consegnati da GitHub Actions, con uno strato gratuito di diagnostica **read-only**. Non importiamo i prompt di jailbreak o il sistema multi-modello originale. I modelli remoti sono **disabilitati** di default; nessun nuovo cron, acquisto, Vidu, sintesi vocale, render o pubblicazione social.

## Moduli
- `src/ai_director_v1.py`: due punti di vista editoriali sul dossier, regia e critica. Non osserva il mondo e non approva contenuti.
- `src/ai_director_bridge_v1.py`: import di piani V13 e ArtVision 4x1; quattro rapporti separati per le varianti.
- `src/ai_director_delivery_v2.py` **nuovo**: legge la consegna vera (MP4, storyboard JSON se presente), applica diagnosi reali con `ai_director_visual_qa_v1.py` e `director_reference_v326.py`, produce `INDEX.html` e rapporti Android. Distingue secondi `estimated_seconds` Giuliano dai tempi ascoltati davvero; non dichiara la sincronizzazione voce senza ASR.
- `src/ai_director_artifact_fetch_v2.py` **nuovo**: legge una run completata e riuscita del medesimo repository, scarica **un solo** artifact non scaduto sotto il limite di 450 MB, estrae solo MP4/JSON con protezione zip traversal/symlink/bombe, registra SHA e provenienza. Max estrazione 750 MB. Nessun file scaricato viene eseguito.
- `.github/workflows/ai-director-delivery-v2.yml` **nuovo**: test PR offline, avvio manuale Android oppure avvio `workflow_run` sulle produzioni esplicitamente elencate. Nessun nuovo cron; per `workflow_run` solo push/dispatch realmente riusciti e originati nello stesso repository.

## Copertura iniziale
- Giuliano: EP2 Moai, Terracotta V2, EP3 Antikythera (solo **dopo** la riuscita del vero render). Uno `static-check` verde di EP3 non supera il requisito: non produce MP4.
- ArtVision: Rheam Sleeping Beauty Cinema. La revisione non altera le quattro varianti né le regole Museum; gli altri owner possono essere esaminati tramite run ID.
- La Storia Rivive: Venezia V310 (solo MP4 esistente). Per V101 esistono **soltanto ricerca e prove**, non eseguire diagnosi MP4 inventando un master.
- WOW LAB e altri episodi: revisione **manuale** tramite run ID, senza aggiungere pianificazioni. L'elenco degli eventi automatici va ampliato solo dopo prove reali sui singoli workflow.

Questa copertura è **parziale rispetto a tutte le centinaia di workflow del repository**. Non dichiarare integrazione automatica universale.

## Uso da Android
1. In GitHub apri **Actions → AI Director V2 | real video delivery QA and Android review**.
2. **Run workflow** → inserisci il numero della run terminata con successo (il numero dell'URL, es. la run di un master precedente), scegli il format, opzionalmente il nome esatto dell'artifact.
3. A job completato apri Artifacts → `AI_DIRECTOR_V2_ANDROID_QA_<run-id>`; estrai ZIP sul telefono e apri `INDEX.html`. `ARTIFACT_INPUT.json` contiene nome, dimensione e hash dei file letti; gli originali non sono modificati.

Un MP4 enorme, zip annidato, artifact scaduto, mancante o non selezionabile viene segnalato come non verificabile. Nessun test si può spacciare per visione completa del film.

## Cosa verifica realmente
- `ffprobe`: video presente, durata, codec; SHA256 del vero file in ingresso attraverso il modulo V1.
- `ffmpeg`: possibili stacchi sotto ~0,95 secondi, intervalli neri, coda nera. Il risultato può avere falsi positivi e non è analisi estetica umana.
- JSON storyboard: tempi incoerenti, ripetizioni note, dettagli narrati e mostrati **soltanto se i campi sono presenti**, rigetto delle false prove di scala Museum.
- Per ArtVision 4×1: se non è attribuibile con certezza un MP4 a una variante, il rapporto dice **video non disponibile**, non ricicla lo stesso MP4.
- Dossier editoriali e questioni emerse dalle precedenti regole V320/V321/V322/V323/V326.

## Cosa NON fa ancora
- Non invoca più LLM insieme: confronto OpenRouter resta `default_deny=true`, `routes=[]`, senza fatturazione o fallback a pagamento.
- Non corregge autonomamente scene o audio e non rimonta automaticamente il video.
- Non valida la fedeltà storica delle immagini, licenze commerciali, volti, vera scala museum, sincronizzazione voce al fonema o naturalezza del racconto. Queste richiedono gli specifici gate V80/V91/V94/V96/V99/V118/V119 e revisione artistica.
- Non sblocca la sintesi vocale Google di Antikythera né crea il master mancante.
- Non collega ancora il rapporto alla pagina pubblica del sito Video Library Studio.

## Test e controlli
```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_ai_director_delivery_v2.py' -v
python src/ai_director_delivery_v2.py --input-dir /tmp/preview --out /tmp/report --format giuliano --subject Antikythera
```
Non compromettere gli archivi di produzione, non fare merge senza CI verde, usare un run reale per la prova finale. L'integrazione utile si misura con MP4 esaminati e correzioni registiche successive, non con il numero di script.
