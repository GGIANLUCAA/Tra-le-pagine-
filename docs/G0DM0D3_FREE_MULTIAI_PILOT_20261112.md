# G0DM0D3 FREE · Stato del test reale (12 novembre 2026)

Questo è un adattamento **editoriale** ispirato al confronto fra più AI; **non** copia il frontend o il codice G0DM0D3. Non produce, modifica o pubblica MP4. Restano prevalenti AGENTS.md, docs/REGOLE_ATTIVE.md, V320/V322/V326, fonti/diritti, V80/V118 e revisione umana.

## Chiavi GIÀ esistenti — nessuna nuova credenziale necessaria

La schermata GitHub dell'utente mostrava due secrets, **`OPENRUTER3` e `OPENRUTER2`** (ortografia esatta senza la O dopo ROUT). Il controllo precedente cercava erroneamente `OPENROUTER_API_KEY` e le riteneva assenti.

- `OPENRUTER3` è stata autenticata con GET `https://openrouter.ai/api/v1/key`, HTTP **200**, run **43264184802**.
- GET comparativa di `OPENRUTER3` e `OPENRUTER2`: entrambe risultano associate allo **stesso account**, quota modelli gratuiti **50 disponibili su 50** alla run **43264951849**. Cambiare chiave non aumenterebbe la quota account, e non è opportuno usarlo per aggirare il 429.
- Il workflow principale `.github/workflows/g0dm0d3-free-four-roles-v1.yml` e il laboratorio una tantum usano ora soltanto il secret **OPENRUTER3**, recuperato protetto da GitHub Actions; mai scritto nei log, in chat, nelle bozze o nel codice.
- Non leggere o usare le altre chiavi (Google, Vidu, Groq...) per questo esperimento: non servono e potrebbero comportare costi.

## Risultati REALI (non simulati)

1. **Run 43264545886** — 1 POST effettiva verso `google/gemma-4-26b-a4b-it:free`, risposta HTTP **429**. Nessuna bozza generata, nessun retry. Il catalogo confermava prezzi input/output zero. La quota account ancora intatta suggerisce un limite a monte, non raggiungimento della quota giornaliera (non è certificata la causa esatta del 429).
2. **Run 43265334268** — selezionati `nvidia/nemotron-3.5-lightning:free` e `baidu/ernie-5.5-flash-preview:free`, prezzi live zero. Il modello NVIDIA ha restituito HTTP 200 con **contenuto finale non utilizzabile**; il secondo modello non è stato interrogato. Il limite output è stato elevato a 1200 token e il reasoning NVIDIA disattivato, perché può assorbire il budget.
3. **Run 43265754435** — due POST effettive; **NVIDIA Nemotron ha restituito una vera proposta editoriale**, `reported_cost_usd=0`, ruolo `sceneggiatore`. **Baidu ERNIE ha risposto HTTP 400**, quindi ruoli storico, regista e critico non sono stati prodotti. Nessun retry automatico.
4. Dopo la terza prova, è stato corretto **soltanto** il codice per applicare `reasoning.enabled=false` esclusivamente a NVIDIA e non a Baidu. Questo **non è ancora verificato con una nuova chiamata reale**. I test offline verificano l'instradamento dei parametri.

**Stato finale:** connessione credenziali reale PASS; modelli e prezzi live PASS; sceneggiatore live PASS (una risposta); quattro risposte reali FAIL/INCOMPLETO. È scorretto dichiarare il sistema creativo multi-AI completamente funzionante.

## Prime lezioni di autocritica dal testo NVIDIA

Il modello propone di far partire l'animazione dell'ingranaggio quando il narratore lo descrive, di evitare flash fotografici e di distinguere il reperto dalla ricostruzione grafica: idee potenzialmente utili. Ma afferma senza fonti che nel **1901** i pescatori di spugne fecero una specifica scoperta e cita come fonti **"Ciclicamente" e "XTEP"**, non presenti nel dossier. Propone formule deboli come *"un orologio che non dovrebbe esistere"* e *"non è solo un orologio"*, contrarie al naturale V320. Il testo non è approvato e NON si deve usare come narrazione o storyboard di produzione senza ricerca documentata e critica umana.

## Protezioni su costi e pubblicazione

- Modelli pinnati con suffisso `:free`, verifica live prezzi di prompt/completion e request: devono essere **0**. Il fatto di vedere "$0" non garantisce da solo la quota/routing di ogni account.
- Provider routing `allow_fallbacks:false` e `max_price:{prompt:0,completion:0}`; `max_tokens:1200`; massimo quattro chiamate sequenziali per test manuale, nessun retry automatico.
- Nessun `openrouter/free` router né passaggio a un modello a pagamento; nessun cron, video, TTS o Vidu; nessuna pubblicazione. La config del resto del sistema `config/free_llm_zero_cost_v1.json` mantiene `default_deny=true,routes=[]`.
- I prompt del test riguardano solo il tema storico pubblico: i provider di modelli gratuiti possono registrare i prompt, quindi niente dati privati.
- I dati di fatturazione delle singole richieste vengono letti dalla risposta `usage.cost` quando disponibile; il costo conto complessivo non è una garanzia data dal solo codice.

## Uso da Android, senza creare nuove chiavi

Aprire [Workflow G0DM0D3 FREE](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/g0dm0d3-free-four-roles-v1.yml). **Run workflow**, formato `giuliano`, soggetto pubblico. Con `execute_free_trial=false`: prova offline gratuita che non chiama modelli. Con `true`: usa il secret GitHub esistente `OPENRUTER3` e tenta al massimo quattro POST a prezzi zero, senza retry; può fallire se un provider è saturo/incompatibile.

Scaricare da Artifacts il rapporto `G0DM0D3_FREE_FOUR_ROLES_...` e leggere `ANDROID_REPORT.html` da Android. Non confondere singoli ruoli generati con un master approvato. Non ripetere automaticamente per aggirare limiti o fornitori non disponibili.

## Prossimo passo

Correggere la compatibilità delle risposte effettive Baidu dopo verifica dei dettagli dell'HTTP 400; provare di nuovo **soltanto con consenso per una nuova prova**, non in un loop. Confrontare il documento prodotto con il copione autentico di Anticitera e le fonti reali prima di inserire modifiche nel renderer.