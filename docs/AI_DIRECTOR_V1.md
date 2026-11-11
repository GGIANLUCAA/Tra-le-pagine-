# AI Director V1 · Direzione editoriale e QA integrati, senza regressioni

**Data:** 12/11/2026 · **Stato:** prototipo su branch per validazione. Non è automaticamente attivo nei workflow owner, nel sito o nei renderer.

## Obiettivo

Riutilizzare idee di confronto multi-modello di G0DM0D3 senza copiare l'interfaccia o il suo meccanismo di richieste costose. Inserire un controllo aggiuntivo, non un secondo sistema produttivo.

**Regole prevalenti:** AGENTS.md, docs/REGOLE_ATTIVE.md; V320/321 naturalezza, V322 regia umana, V323 verifica cromatica su MP4, ArtVision V80/V118/V119, La Storia Rivive V94/V96/V99, diritti, Vidu gateway. Nessun video già approvato viene alterato. Quattro varianti ArtVision invariabili e WAV condiviso tra i due Critico.

## Cosa è concretamente implementato

1. **Regia preventiva offline:** analisi di scene con cronologia assoluta, sovrapposizioni, buchi, flash (<0,9 s), hold brevi (<1,3 s) e ripetizione eccessiva degli stessi asset. Le durate sono quelle del dossier: non si deduce il montaggio reale.
2. **Narrazione e contenuti:** richiama il gate V320 per naturalezza. Associa gli estratti pronunciati alla scena (verifica testuale, NON vero timecode ASR). Segnala le fonti ancora non verificate.
3. **Restauro e Museum:** non consente di presentare un flag di colorizzazione come prova di colore reale. Richiede a valle il gate V323; nei Museum richiede fonti di cornice/sala/dimensioni; nel 4×1 rispetta il controllo canonico esistente.
4. **Memoria dei difetti:** legge solo se richiesto il JSONL delle recensioni reali registrate con SHA esatto da artvision_learning_loop_v1.py. Mostra osservazioni documentate e le passa come contesto al revisore editoriale. Non dice di avere guardato un MP4.
5. **AI comparativa opzionale:** due chiamate editoriali distinte, sceneggiatore e revisore, con modelli esatti che terminano in :free, sottoposti all'esistente free_llm_zero_cost_v1.admit. Modello fissato, nessuna lista di fallback, provider.max_price input/output = 0, allow_fallbacks=false, max 850 token per risposta, stop al primo errore, nessun retry. Producono bozze, mai una certificazione di qualità o approvazione.
6. **Report Android:** JSON e HTML autonomi scaricabili come artifact GitHub Action. Sono snapshot statici della singola esecuzione, NON un progresso in tempo reale del sito.

## Componenti

- src/ai_director_v1.py — motore offline/opt-in.
- tests/test_ai_director_v1.py — test offline di regia, prova colore, prompt, limiti.
- examples/ai_director_v1_sample.json — esempio dichiaratamente sintetico.
- .github/workflows/ai-director-v1.yml — manuale e PR test; nessun cron.
- config/free_llm_zero_cost_v1.json non modificato (routes=[], politica default deny).

## Esecuzione locale, senza Internet

~~~bash
python src/ai_director_v1.py \
  --brief examples/ai_director_v1_sample.json \
  --out output/ai_director_v1/report.json \
  --dashboard output/ai_director_v1/report.html
python -m unittest discover -s tests -p 'test_ai_director_v1.py' -v
~~~

Il report dell'esempio segnala che nessuna fonte è stata verificata. Non è un vero filmato né una recensione artistica.

## Ingresso diretto dal dossier ArtVision 4×1 V68

Quando esiste un vero dossier compilato con schema artvision-4x1-v1:

~~~bash
python src/ai_director_v1.py \
  --four-plan output/ARTVISION_4X1_PLAN.json \
  --variant critico_standard \
  --out output/ai_director_v1/critico_standard.json \
  --dashboard output/ai_director_v1/critico_standard.html
~~~

Ripetere per le altre tre varianti, senza copiare parole o timecode inventati. Il bridge riusa artvision_four_variants_gate.validate, incluso il vincolo di sceneggiatura condivisa. Se il dossier non è compilato, fallisce chiuso o segnala la mancanza: non inventa fonti né immagini.

Con un file JSONL di recensioni effettive, si può aggiungere --ledger PERCORSO.jsonl per vedere fino a sei lezioni annotate in precedenza. Se l'utente non ha realmente guardato/ascoltato il video, non registrare una falsa recensione.

## Verifica tecnicamente il vero MP4, ma non finge di guardarlo

L'opzione --video /percorso/vero.mp4 usa ffprobe per codec/durata/dimensioni e legge integralmente i byte per SHA256. Il controllo del colore deve restare il gate V323 reale; l'autocritica artistica richiede ancora vedere il filmato integrale, senza audio e con audio, e ascoltare l'audio separatamente. I report devono sempre mantenere mp4_seen=false, human_approved=false, published=false fino a verifiche esterne genuine.

## OpenRouter: attivazione soltanto dopo controllo effettivo

Il sito G0DM0D3 e GitHub Actions sono ambienti distinti. L'accesso dal browser Android non installa automaticamente la chiave nel progetto. L'audit del 04/11/2026 non vedeva OPENROUTER_API_KEY nel runner: va ricontrollato, senza mostrare la chiave.

La policy repository config/free_llm_zero_cost_v1.json ha routes=[]: così ogni tentativo live è respinto. NON renderla permissiva a intuito. Solo un modello con prezzo 0 input/output, condizioni commerciali verificate, fatturazione e fallback disabilitati, evidenze ufficiali recenti, può essere ammesso con la funzione admit. Il provider OpenRouter pubblica 50 richieste/giorno (20/minuto) per le varianti free, anche gli errori contano; due chiamate per questa invocazione non rappresentano una quota giornaliera condivisa tra account, sito e tutte le Action.

Solo dopo audit si può usare workflow_dispatch con enable_live=true e due modelli :free già ammessi. Il workflow espone il secret solo nello step manuale di inferenza, non nei test PR. Non usare openrouter/free (scelta dinamica) né il profilo G0DM0D3 ULTRAPLINIAN 12–60 modelli: non rispettano il vincolo del modello esatto.

## Dal telefono Android

1. GitHub → repository Tra-le-pagine- → Actions → AI Director V1 | isolated director preflight.
2. Run workflow, con enable_live=false per la prima prova.
3. Aprire run → Artifacts → ai-director-v1-qa-...; aprire report.html e report.json.
4. Solo dopo prova di qualità, prendere in considerazione una chiamata AI gratuita su una vera bozza pubblicabile.

## Passaggio successivo prima della produzione seriale

Per integrare nel sistema automatico, occorre misurare un caso reale contro la regia attuale: lo stesso dossier e il vero MP4, verificare nessun blocco spurio, tempi di esecuzione e migliorie concrete. Dopo il PASS si può aggiungere al workflow owner esistente uno step pre-render non bloccante e senza API, poi il gate bloccante solo per difetti riconosciuti e confermati.

Nessuna modifica a master, owner, cron, G0DM0D3 fork, sito pubblico, Vidu, TTS, social o segreti. Nessun nuovo costo. Il modulo non è un motore video e non produce MP4 da solo.
