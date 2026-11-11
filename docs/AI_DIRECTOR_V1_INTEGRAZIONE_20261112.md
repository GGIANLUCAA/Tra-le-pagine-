# AI Director V1 · integrazione sicura nello Studio video (12 novembre 2026)

**Stato: modulo isolato e revisionabile. Nessun nuovo cron, nessuna pubblicazione, nessuna modifica ai master.**

## Architettura

La copia GGIANLUCAA/G0DM0D3 contiene una interfaccia di confronto multi-modello, ma le modalità ULTRAPLINIAN/CLASSIC possono chiamare numerosi modelli a pagamento. Non abbiamo importato prompt di jailbreak, telemetria o codice di quel sito: abbiamo adattato il **principio editoriale del confronto fra idee** ai motori di Tra-le-pagine-. Gli eventuali obblighi di licenza e i termini dei provider devono essere verificati prima di qualsiasi integrazione ulteriore.

### Collegamenti effettivi

| Modulo già esistente | Nuovo adattatore | Limitazione |
| --- | --- | --- |
| src/video_director_v13.py | ai_director_bridge_v1.py legge PROJECT_V13.json | Nessuna riscrittura; non inventa tempi mancanti |
| src/artvision_four_variants_gate.py | Lettura dei dossier ArtVision 4x1 | Produce quattro report separati |
| src/artvision_learning_loop_v1.py | Recupera la prossima singola lezione da ledger | Non modifica master, preset e queue |
| src/free_llm_zero_cost_v1.py | Gate admit prima di ogni inferenza opzionale | Default deny; zero fallbacks costosi |
| V320/V321, regia umana e V80/V94/V96/V99 | Prompt regista, critico e controllo manifesto | Regole originali prevalenti |

### Funzioni consegnate

1. Piano editoriale offline con due punti di vista: regista e critico scettico. Il risultato e una bozza, non un film approvato.
2. Audit storyboard: tempi sotto 0,95 s, hold sotto 1,5 s, scene sovrapposte, gap, ripetizioni di asset, mancate prove museali e disallineamenti espliciti fra dettaglio citato e mostrato. Nessuna pretesa di avere visto filmato o ascoltato audio.
3. Probe MP4 con ffprobe e SHA-256 e, quando FFmpeg e disponibile, scansione dei frame reali: stacchi rilevati a distanza sotto 0,95 s e intervalli neri oltre 0,12 s. Sono indizi tecnici da verificare, non una revisione artistica. La scansione viene limitata ai primi 240 s e segnalata come parziale oltre tale durata.
4. Confronto opzionale con due modelli gratuiti esplicitamente approvati e terzo giudice opzionale, massimo 2–3 richieste per avvio, senza retry. Disabilitato per impostazione predefinita.
5. Memoria dei difetti tramite registro già esistente, con una proposta alla volta; nessuna autocorrezione distruttiva.
6. Report HTML e JSON consultabili su Android tramite artifact GitHub Actions.

## Uso da Android senza PC

Dopo il merge della PR: GitHub → Tra-le-pagine- → Actions → AI Director V1 · offline editorial quality & Android reports → Run workflow.

- Mode PLAN: scegliere formato e soggetto pubblico; l'azione prepara un dossier di lavoro e il report HTML.
- Mode BRIDGE: inserire un percorso relativo a un dossier JSON **pubblico già presente nel repository**, schema video-project-v13 oppure artvision-4x1-v1.
- A run finita, scaricare l'artifact AI_DIRECTOR_V1_ANDROID_REPORT e aprire INDEX.html o ANDROID_REPORT.html.

L'azione non chiama OpenRouter, non richiede credenziali, non avvia Vidu/TTS, non genera MP4 e non pubblica.

## Comandi di prova

    python src/ai_director_v1.py --mode plan --format documentario --subject "Vita nel 1900" --out-dir output/ai_director_v1

    python src/ai_director_v1.py --mode audit --brief output/manifest_reale.json --video output/video_reale.mp4 --out-dir output/audit_v1

    python src/ai_director_visual_qa_v1.py --video output/video_reale.mp4 --output output/real_mp4_diagnostics.json

    python src/ai_director_bridge_v1.py --source output/ARTVISION_4X1_PLAN.json --out-dir output/review_4x1

    python src/ai_director_bridge_v1.py --source output/PROJECT_V13.json --learning-ledger output/learning/reviews.jsonl --out-dir output/review_v13

### OpenRouter e costo zero

Per usare davvero il confronto, devono essere soddisfatti **tutti** i controlli: due ID modello distinti e esattamente terminanti in :free; pricing ufficiale input/output a zero; termini per uso commerciale verificati; fatturazione e ripiego a pagamento disabilitati; prove recenti nella policy già esistente; token soltanto tramite variabile OPENROUTER_API_KEY; esplicita autorizzazione AI_DIRECTOR_ALLOW_FREE_CALLS=1 e opzione --execute.

Comando esemplificativo, **NON attivabile senza modelli ammessi**:

    AI_DIRECTOR_ALLOW_FREE_CALLS=1 python src/ai_director_v1.py --mode compare --execute --brief output/manifest_reale.json --model 'provider/modello-uno:free' --model 'provider/modello-due:free' --out-dir output/confronto

I nomi di esempio non sono modelli autorizzati. La lista dei modelli ammessi nel progetto resta routes=[]: nessuna inferenza. Il router virtuale openrouter/free non e approvato da questo gate, perche il modello finale non e vincolato in modo sufficientemente preciso. Non si registrano API key nei file o nei log.

L'audit del 4/11 in docs/API_SECRETS_AUDIT_20261104.md non rilevava OPENROUTER2 o OPENROUTER_API_KEY in GitHub Actions. L'accesso salvato nel browser Android e separato e non prova l'attivazione su Actions.

Il limite 2–3 richieste riguarda **la singola esecuzione**, NON una quota giornaliera globale condivisa fra runner. Fino alla presenza di un ledger globale e controlli del provider, non abilitare chiamate programmate. Nel workflow ufficiale le inferenze sono del tutto disabilitate.

## Risultati e limiti

Il report e consultivo e non puo dichiarare Gold, pubblicato o artistically approved. Restano obbligatori prove sulle fonti e diritti, verifica scene/video/voce reale, controllo del benchmark V99 per La Storia Rivive, veridicita delle sale per Museum e autorizzazione alla pubblicazione. Non vengono cancellati file ne ripristinate nuove versioni di master.

Le verifiche di qualità A/B con MP4 reali, una connessione live al sito e l'attivazione del confronto OpenRouter gratuito sono **fasi successive non ancora collaudate**. Non dichiarare completata la produzione automatica grazie a questi soli test.

### Test offline

    python -m py_compile src/ai_director_v1.py src/ai_director_bridge_v1.py src/ai_director_visual_qa_v1.py
    python -m unittest discover -s tests -p 'test_ai_director_v1.py' -v
    python -m unittest discover -s tests -p 'test_ai_director_bridge_v1.py' -v

Il workflow controlla anche che config/free_llm_zero_cost_v1.json rimanga default_deny=true, routes=[].

    python -m unittest discover -s tests -p 'test_ai_director_visual_qa_v1.py' -v

La rilevazione automatica di stacchi rapidi puo produrre falsi positivi su movimenti o cambi di luce. La nuova diagnostica non rileva tutti i flash e non sostituisce l'esame dei veri frame a velocita normale, la sincronizzazione voce/scene ne il QA umano.
