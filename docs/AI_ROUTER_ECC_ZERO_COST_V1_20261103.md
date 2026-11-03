# Router AI a costo zero + ECC: selezione e governance V1 (03/11/2026)

## Scopo e stato

Preparazione **senza spese** nel repository per ArtVision e La Storia Rivive.
Non attiva provider né installa un router su un server. La vecchia pipeline
resta proprietaria di video, Vidu, audio, licenze, 4x1, archivio, social e sito.

## Selezione di componenti

| Progetto | Decisione | Motivo |
| --- | --- | --- |
| FreeLLMAPI | **Adattatore editoriale opzionale**, OFF | Un endpoint compatibile OpenAI per bozze |
| ECC (Everything Claude Code) | **Adottare principi**, non installare tutto | Verification Loop, regression test, regole permanenti |
| ZeroSpend | **Adottare politica** UNKNOWN COST = NOT FREE | No secondo router duplicato |
| Free LLM API Hub | **Fonte di ricerca** | Catalogo non sostituisce la documentazione ufficiale |
| Groq | **Candidato**, NON abilitato | Livello gratis con quote variabili; termini da controllare |
| OpenRouter | **Candidato**, NON abilitato | Solo modelli identificati :free e costi zero verificati |
| Cloudflare Workers AI | **Candidato**, NON abilitato | Piano Free con dotazione giornaliera; alcune famiglie sono paid-only |
| Ollama / llama.cpp / LocalAI | **Opzioni locali**, NON installate | Nessuna tariffa token locale, ma consumano hardware |

Non installare contemporaneamente FreeLLMAPI, LiteLLM, Portkey e ZeroSpend:
sono router sovrapposti e moltiplicherebbero la manutenzione. Per l'uso
previsto bastano UN router e controlli indipendenti nel client.

## Regole fail-closed

Configurazione in config/free_llm_zero_cost_v1.json; inizialmente routes=[].
Codice: src/free_llm_zero_cost_v1.py.

Una richiesta editoriale è ammessa solo con:
- FREE LLM attivato manualmente tramite FREELLMAPI_ENABLED=1 e --execute;
- modello ESPLICITO: auto, auto:* e fusion sono vietati;
- route dichiarata esplicitamente, enabled=true e prezzi di input/output 0;
- prova HTTPS UFFICIALE verificata entro 7 giorni; no trial credits;
- Terms of Service verificati per l'utilizzo richiesto; niente resale;
- stato di fatturazione verificato come disabilitato per l'account;
- fallback del router esaminati: **solo** modelli gratis, mai fallback paid;
- header di risposta coerente e assenza di tentativi fallback.

Queste condizioni sono *evidenze operative*, non assicurazione matematica di
costo zero. Il client non può interrogare prima della richiesta tutti gli
stati di fatturazione esterni, né bloccare una eventuale spesa già partita
nel provider remoto. Per questo il controllo più importante è **a monte**:
non aggiungere carte/metodi di pagamento e NON abilitare modelli a pagamento
nelle dashboard provider o nella fallback chain del router. Non usare
endpoint custom a costo ignoto. Impostare limitazioni sui servizi, se offerte.

Fintanto che non esiste tale configurazione verificata, nessuna chiamata
può partire e nessuna bozza AI viene presentata come completata.

## Regole del progetto NON negoziabili

1. Leggere AGENTS.md e docs/REGOLE_ATTIVE.md (non generare nuove regole in concorrenza).
2. ArtVision: esattamente 4 varianti, titoli pubblici in inglese senza
   etichette tecniche o nomi del progetto, copertine coerenti; QA Museum
   di V118/V119 indipendente dai test strutturali.
3. La Storia Rivive: sorgenti reali, V98 benchmark, V94/V96/V99, veri movimenti,
   controllo durata/ritmo; un TEST riuscito non equivale a video approvato.
4. Social: usare il contratto editoriale V28, prove sulle fonti e diritti,
   nessun contenuto generico di comodo; bozze AI sono non approvate.
5. Video reale, cartella ZIP, link scaricabile e disponibilità Video Library
   Studio vanno verificati separatamente prima di dichiarare consegna.
6. Owner unici delle code e dei workflow già approvati; non duplicare orari
   di produzione né creare nuovi job video da questa integrazione.
7. Nessuna pubblicazione pubblica nuova né spesa API senza autorizzazione.

## Applicazione dei migliori principi ECC

- Rule distillation: leggere regole attive e riciclare i gate esistenti,
  non copiarli in altre decine di documenti concorrenti.
- Regression testing: test offline che riproducono i casi di modelli paid,
  evidenza scaduta, fallback inatteso e falsa approvazione.
- Verification Loop: Python compile e unittest prima della fusione in main;
  gli errori del CI bloccano il rilascio.
- Changelog ed evidence: ogni provider richiede fonte ufficiale e data,
  non basta una lista di GitHub o il nome “free”.
- Independent review: una risposta LLM può assistere l'editorial review,
  ma non firmare QA artistico o licenze.

Non è stato installato tutto il pacchetto ECC, che contiene strumenti
pensati per altri ambienti. Abbiamo riutilizzato i principi in forma
leggera e compatibile con le nostre GitHub Actions esistenti.

## Attività che non richiedono ulteriori credenziali

Test offline, validazione di policy vuota, disattivazione predefinita,
documentazione, revisione e rilascio dei soli moduli di sicurezza.

## Attività che richiedono un account/configurazione esterna

Installare FreeLLMAPI su host affidabile (PC o self-hosted runner),
fornire chiavi API dei servizi scelti via gestore segreti e verificare
quote, fatturazione, termini e privacy. Il router locale sul PC non è
raggiungibile da GitHub Actions hosted senza un percorso di rete sicuro.
Non chiedere chiavi in chat, né promettere autonomia 24/7 senza un host.

## Riferimenti ufficiali (da riconfermare alla configurazione)

- FreeLLMAPI: https://github.com/tashfeenahmed/freellmapi
- ECC: https://github.com/affaan-m/ECC
- ZeroSpend: https://github.com/sjfakharian/zerospend
- Free API directory: https://github.com/pacocartones/free-llm-api-hub
- OpenRouter free: https://openrouter.ai/collections/free-models
- Cloudflare Workers AI: https://developers.cloudflare.com/workers-ai/platform/pricing/
