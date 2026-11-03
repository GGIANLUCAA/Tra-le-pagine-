# V2 · Integrazione ecosistema AI gratuito (4 novembre 2026)

## Risultato

Il repository integra ora un **catalogo aggiornabile** e un processo GitHub
Actions di **verifica settimanale SOLO in lettura**. FreeLLMAPI resta l'unico
router previsto; ECC fornisce principi di audit e regressione. Non vengono
creati account, acquistati crediti, effettuate chiamate di inferenza,
generati video, sovrascritti master, pubblicati contenuti o modificati
workflow video esistenti.

- Adapter editoriale V1: src/freellmapi_editorial_v1.py
- Guardia costo zero: src/free_llm_zero_cost_v1.py
- Regole pubbliche V134: src/ecc_public_editorial_guard_v1.py
- Nuova scoperta V2: src/ai_free_catalog_audit_v2.py
- Candidati e requisiti: config/ai_free_stack_candidates_v2.json
- Audit: .github/workflows/ai-free-stack-v2.yml
- Deployment locale FACOLTATIVO: deploy/freellmapi/compose.yaml

## Cosa significa "integrato"

| Progetto | Stato V2 | Attivazione |
| --- | --- | --- |
| Everything Claude Code (ECC) | Principi Verification Loop e regression testing applicati ai nostri test | Nessuna installazione del runtime Claude |
| FreeLLMAPI | Client editoriale e manifest Docker predisposti; gateway non in esecuzione | Occorre un host persistente e chiave unificata |
| ZeroSpend | Politica UNKNOWN COST = NOT FREE applicata in modo indipendente | Non installato come secondo router |
| Free LLM API Hub | Scanner e audit schedulato settimanale | GIÀ operativo dopo merge |
| Groq | Riconoscimento e verifica candidato | Account/chiave/ToS/quote da completare |
| OpenRouter | Riconoscimento e verifica di modelli :free | Account/chiave/ToS/quote da completare |
| Cloudflare Workers AI | Riconoscimento e verifica modello/piano | Piano e fatturazione da accertare, credenziale dedicata |
| Z.ai | Riconoscimento e verifica candidati GLM | Condizioni del proxy e disponibilità da accertare |
| Google Gemini | Riconoscimento come candidato CON cautela EEA | Verifica termini applicabili all'Italia |
| Ollama, llama.cpp, LocalAI | Registrati come opzioni per inferenza locale | Serve un host capace di eseguirli |
| LiteLLM e Portkey | Valutati, **non duplicati** | Ulteriori router non aumentano i crediti gratis |
| OVHcloud AI Endpoints | Opzione anonima da studiare, NON attivata | Verificare licenza e condizioni d'uso commerciale |

La connessione Cloudflare in ChatGPT consente alcune operazioni sul relativo
account, ma non concede automaticamente un token utilizzabile da GitHub Actions.
Lettura dello stato di fatturazione dell'account Cloudflare non è disponibile
con i permessi attuali; quindi NON dichiarare il piano gratuito verificato.

## Audit settimanale senza chiavi

Il workflow GitHub Actions viene eseguito ogni lunedì alle 05:43 UTC.
Scarica esclusivamente un JSON pubblico dal repository
pacocartones/free-llm-api-hub, verifica la freschezza, esclude offerte
trial/crediti promozionali e registra un file JSON temporaneo tra gli
artifact della run. Non attiva i provider e NON modifica main o config.

Anche quando il progetto upstream indica un modello gratis, serve sempre:
- documento ufficiale corrente e prova prezzi input/output a zero;
- controllo dei termini di utilizzo commerciali e di privacy;
- fatturazione disabilitata e nessun fallback a tariffazione incerta;
- credenziali in un secret manager, non nei file Git;
- provino e verifica qualità reale prima di usare i testi.

Il nostro registro operativo config/free_llm_zero_cost_v1.json conserva
routes=[] finché questi requisiti non sono soddisfatti. Un report "candidate"
NON autorizza a chiamare l'API. Mai inventare l'avvenuta configurazione.

## FreeLLMAPI pronto per installazione LOCALE, non automaticamente in cloud

Nel caso ci sia un PC/server disponibile con Docker:
1. Verificare la release, l'immagine e il codice upstream.
2. Copiare deploy/freellmapi/example.env in deploy/freellmapi/.env
   (il file .env deve restare fuori da Git).
3. Generare una chiave di cifratura casuale con openssl rand -hex 32,
   inserirla in .env. Non utilizzare stringhe d'esempio.
4. Avviare in modo esplicito con:
   docker compose -f deploy/freellmapi/compose.yaml up -d
5. Configurare i provider nella dashboard locale 127.0.0.1:3001.
6. SOLO dopo verifica dei termini e della policy, autorizzare i singoli
   modelli nel registro tramite evidenze aggiornate.

Non è possibile avviare questo container sui runner GitHub Actions e
considerarlo un servizio permanente: i runner sono effimeri. Un router sul
PC dell'utente non è raggiungibile da GitHub Actions tramite localhost.
Non esporre la dashboard su Internet, non installare updater con accesso
al socket Docker e non sincronizzare segreti nel repository.

L'immagine :latest è indicata SOLO come template. Per una installazione
effettiva a lungo termine pinning della release/digest, backup sicuri e
aggiornamenti verificati sono preferibili.

## Qualità: come useremo i nuovi modelli quando davvero disponibili

1. Ricerca di fonti: AI può riassumere soltanto fonti recuperate e verificabili.
2. Preparazione sceneggiatura/narrazione: bozze, mai sostituto di revisione.
3. Descrizioni social: mantenere V28 + V134, titoli pubblici in inglese
   ed etichette interne vietate.
4. ArtVision: quattro versioni obbligatorie, realismo Museum e V118/V119.
5. La Storia Rivive: confronto V98 e guard V94/V96/V99 su MP4 reali.
6. Video Library Studio: link scaricabile e verifica video reale.
7. Nessun candidato LLM può dichiarare approved, Gold o published.

**Regola: QA tecnico superato NON è QA artistico superato.**

## Test senza API

- python -m unittest discover -s tests -p 'test_ai_free_catalog_audit_v2.py' -v
- python -m unittest discover -s tests -p 'test_freellmapi_editorial_v1.py' -v
- Il workflow ai-free-stack-v2.yml esegue entrambi e verifica policy vuota.

## Fonti di riferimento

- FreeLLMAPI: https://github.com/tashfeenahmed/freellmapi
- ECC: https://github.com/affaan-m/ECC
- ZeroSpend: https://github.com/sjfakharian/zerospend
- Free LLM API Hub: https://github.com/pacocartones/free-llm-api-hub
- Groq: https://console.groq.com/docs/rate-limits
- OpenRouter: https://openrouter.ai/collections/free-models
- Cloudflare: https://developers.cloudflare.com/workers-ai/platform/pricing/
- OVHcloud: https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-troubleshooting

Una verifica pubblica del listino non equivale alla verifica dell'account
specifico o a una garanzia futura di costo zero.
