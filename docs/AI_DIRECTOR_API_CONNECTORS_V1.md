# AI Director · API esterne V1 (Europeana + Gemini + Groq)

12 novembre 2026 · Add-on isolato sul repository GGIANLUCAA/Tra-le-pagine-.

## Stato concreto

| Provider | Codice | Condizione d'uso |
| --- | --- | --- |
| Europeana Search | Adapter reale + report + bridge al dossier | Solo richiamando esplicitamente una ricerca da GitHub Actions, con chiave Europeana. Nessun media scaricato |
| Google Gemini | Adapter di revisione di UN fotogramma JPEG/PNG | Disabilitato (routes vuote); termini, regione Italia e costo zero da verificare |
| Groq Whisper | Adapter trascrizione con timecode a segmenti | Disabilitato (routes vuote); tariffazione pubblicata dal provider, non trattare il Free plan come automaticamente gratuito |
| OpenRouter | Gia presente in src/ai_director_v1.py | Il gate costo zero resta invariato, non abilitato |
| Cloudflare Workers AI | NON implementato in V1 | La quota dipende da piano/account; il modello Vision richiede accettazione licenza Meta |

## Qualita e dati

- Europeana e un catalogo di ricerca, non una verifica dei diritti. I risultati hanno rights_review=pending, approved=false. Anche il filtro 'open' non assicura il diritto di pubblicare il materiale in Italia.
- Solo i metadati del catalogo, non gli asset, possono confluire in ai_director_v1.py tramite src/ai_director_europeana_bridge_v1.py. Questo prepara un BRIEF e un report Android con sources_verified=false, senza creare scene o inventare citazioni.
- Gemini analizza al massimo un fotogramma sorgente, non l'intero MP4. La revisione umana, il V323 colore reale e i test video esistenti restano necessari.
- Groq riceverebbe l'audio originale e non deve essere attivato senza verificare privacy, condizioni e quote. Gli offset ASR non dimostrano coerenza tra immagini e voce.
- Nessuna modifica a editor, Vidu, Gemini TTS, social, master, produzione ricorrente, autopubblicazione o diritti.
- Nessuna chiave nel codice o in report pubblici.

## Uso Android · Europeana

1. Richiedere una chiave Europeana su https://www.europeana.eu/en/how-to-register-for-and-manage-an-api-key .
2. Aprire https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions e creare EUROPEANA_API_KEY. Inserire la chiave solo nel campo Secret, non in un messaggio.
3. GitHub > Actions > AI Director API V1 | Europeana search and connector safety > Run workflow.
4. Scegliere mode=europeana, una ricerca pubblica (es. Venice 1896), max 3–8 risultati e execute=true per una sola richiesta di lettura metadati. Di default execute=false, simulazione senza rete.
5. In Artifacts scaricare AI_DIRECTOR_API_RESEARCH. All'interno: REPORT.json per candidati Europeana, DIRECTOR_BRIEF.json, director/ANDROID_REPORT.html, director/REPORT.json, director/EDITORIAL_PROMPTS.json.

Senza chiave il workflow non simula la ricerca: fallisce dichiarando chiave assente. Anche con chiave il filtro open media potrebbe restituire zero risultati.

## CLI manuale (non necessaria su Android)

Offline senza rete:

    python src/ai_director_external_apis_v1.py --mode europeana --query "Venice 1896" --output output/ai_director_apis/REPORT.json

Ricerca autorizzata dopo secret disponibile nell'ambiente:

    python src/ai_director_external_apis_v1.py --mode europeana --query "Venice 1896" --execute --output output/ai_director_apis/REPORT.json

Bridge con ricerca vera:

    python src/ai_director_europeana_bridge_v1.py --input output/ai_director_apis/REPORT.json --subject "Venice 1896" --output output/ai_director_apis/DIRECTOR_BRIEF.json --report-dir output/ai_director_apis/director

## API AI ad alto rischio costo

Il file config/ai_director_external_api_v1.json imposta default_deny=true e routes=[]; Gemini Vision e Groq Whisper sono quindi client disabilitati. Per ogni modello occorrono prove ufficiali di prezzo effettivamente zero sul piano specifico, termini Italia/commerciale, limiti e no fallback, fatturazione disabilitata, evidenza recente (massimo 7 giorni) e flag AI_DIRECTOR_EXTERNAL_LIVE=1. Le sole credenziali non bastano.

Il workflow non espone GEMINI_API_KEY o GROQ_API_KEY a nessun job e non fornisce pulsanti di inferenza. Questi strumenti non saranno attivati senza gli attestati e un controllo anti-credito condiviso; la protezione per chiamata non equivale a limitazione globale di quota. Groq pubblica prezzi per i modelli Whisper (https://console.groq.com/docs/speech-to-text).

## Test e manutenzione

    python -m py_compile src/ai_director_external_apis_v1.py src/ai_director_europeana_bridge_v1.py
    python -m unittest discover -s tests -p 'test_ai_director_external_apis_v1.py' -v

La CI verifica anche che entrambe le policy config/ai_director_external_api_v1.json e config/free_llm_zero_cost_v1.json mantengano routes vuote. Nessuna richiesta web viene effettuata durante i test.

## Fonti ufficiali

- Europeana Search API: https://europeana.atlassian.net/wiki/spaces/EF/pages/2385739812/
- Europeana API key: https://europeana.atlassian.net/wiki/spaces/EF/pages/2462351393/
- Groq Whisper: https://console.groq.com/docs/speech-to-text
- Google Gemini generateContent: https://ai.google.dev/api/generate-content
- Cloudflare Workers AI Vision: https://developers.cloudflare.com/workers-ai/models/llama-3.2-11b-vision-instruct/

Il collegamento a un archivio non garantisce automaticamente un miglioramento del video. I risultati vanno confrontati con fonti e MP4 reali prima della produzione.
