# Groq API V1 — collegamento al progetto, senza server FreeLLMAPI

## A cosa serve

Un adattatore editoriale Python per ArtVision e La Storia Rivive:
src/groq_editorial_v1.py

Prepara soltanto bozze di storyboard, narrazioni, post social,
note su fonti e controllo testuale. Non produce MP4, non pubblica,
non certifica diritti e non approva musei/cornici o qualità artistica.

La chiamata diretta verso https://api.groq.com/openai/v1/chat/completions
non richiede un server FreeLLMAPI, utile se si usa GitHub Actions
e non c'è un computer Docker acceso 24 ore al giorno.

## Come memorizzare la chiave Groq (una sola operazione dell'utente)

1. Aprire:
   https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions
2. Selezionare **New repository secret**.
3. Nome preciso: **GROQ_API_KEY**.
4. Incollare la chiave Groq SOLO nel campo Secret di GitHub.
5. Selezionare **Add secret**.

Non incollare il token in chat, README, codice, workflow, file JSON
o messaggi GitHub. Il connettore corrente non dispone di permessi
per creare i segreti direttamente: soltanto il proprietario può
completare questo passaggio nel proprio account.

## Test sicuro dopo aver creato il segreto

Aprire Actions > "Groq API - optional secret presence and offline adapter tests"
> Run workflow, sul ramo main. Il controllo stampa soltanto
GROQ_API_KEY_PRESENT se esiste una variabile segreta non vuota.
Non stampa la chiave, non effettua richieste Groq e non usa token.

Questo test NON verifica che la chiave sia corretta, la quota residua
o il tipo di piano attivo.

## Modelli e prezzi: attenzione ai piani

Il modello openai/gpt-oss-120b è tra quelli inclusi nei limiti
del piano Free di Groq, ma Groq mostra anche prezzi per token
nei piani a pagamento. Una API key non prova da sola che
l'account sia gratuito o che la fatturazione sia disattivata.
Verificare personalmente:
https://console.groq.com/docs/rate-limits

Fino alla verifica del piano, delle condizioni commerciali e della
fatturazione, config/free_llm_zero_cost_v1.json conserva
routes=[] (default deny). Non inserire mai attestazioni fittizie.

## Come verrà attivato il collegamento reale

Dopo che l'utente ha verificato il piano Free e i termini applicabili:
1. Registrare nel file di policy l'ID del singolo modello
   effettivamente gratuito per l'account, con documentazione ufficiale
   e una data corrente (max 7 giorni).
2. Confermare che non ci siano addebiti o fallback paid;
   l'adattatore Groq usa un solo modello, non fa fallback.
3. Eseguire manualmente una bozza con GROQ_EDITORIAL_ENABLED=1,
   GROQ_MODEL=<ID-approvato> e GROQ_API_KEY fornita dal gestore segreti.
4. Valutare il contenuto contro le regole V28, V91/V94/V96/V99,
   V118/V119 e V134 prima di qualsiasi consegna.

Esempio CLI di verifica senza credenziali, senza chiamate o file scritti:

    python src/groq_editorial_v1.py --task social --prompt-file /tmp/source_notes.txt --output /tmp/draft.json

Solo in un ambiente sicuro con chiave, modello e policy approvati,
l'opzione --execute avvia la singola chiamata.

Il workflow GitHub incluso non ha un tasto di inferenza:
l'accesso a una API esterna non viene attivato automaticamente
dal solo inserimento della chiave. La futura automazione dovrà
mantenere i controlli e i limiti di spesa/costo zero.

## Fonti

- API Groq: https://console.groq.com/docs/api-reference
- Modelli e piani: https://console.groq.com/docs/rate-limits
- Segreti GitHub: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets

No second router, no paid activation, no changes to video owners.
