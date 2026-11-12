# G0DM0D3 FREE · primo vero esperimento multi-AI per video (12/11/2026)

**Scopo:** adattamento editoriale ispirato al confronto di idee G0DM0D3; **non** è un'installazione del suo frontend e non ne importa jailbreak/telemetria. Sicurezza e regole V320/V321/V322/V326, fonti, licenze, allineamento voce–scene, Museum 4x1 e no pubblicazione restano prioritarie.

## Risultati read-only della connessione
Run GitHub `43254929517` (GET soltanto; zero POST): `google/gemma-4-26b-a4b-it:free` presente con input/output a costo 0; il precedente Nemotron Super 3 non era più nell'elenco corrente e pertanto è stato scartato. Nuovo modello selezionato `google/gemma-4-31b-it:free` da elenco live OpenRouter e pagina ufficiale.
**OPENROUTER_API_KEY e OPENROUTER_KEY ASSENTI dalle secrets Actions durante la prova.** Un login o una chiave nel browser Android non costituisce connessione al runner.
- Costo del modello: $0 input e $0 output verificati nel catalogo OpenRouter, e riconfermati automaticamente prima di ogni prova live.
- Limiti Free indicativi: 50 richieste al giorno e 20 al minuto senza acquisti di crediti; i tentativi falliti contano.
- La prova è unicamente editoriale: no MP4, voce, Vidu, file privati, sito/social, nuova API a pagamento, saldo/ricariche.
- **La fatturazione reale a livello di account e i termini dei singoli provider NON sono ancora stati verificati nella chiave del proprietario.** Non dichiarare costo totale certo di ogni account o uso commerciale definitivo senza controllo ulteriore.

## Quattro ruoli, due modelli gratuiti, quattro tentativi al massimo
- Sceneggiatore → `google/gemma-4-26b-a4b-it:free`: sei beat, specificità e gancio.
- Storico → `google/gemma-4-31b-it:free`: dubbi, errori, fonti da verificare; non sostituisce verifica storica indipendente.
- Regista → `google/gemma-4-26b-a4b-it:free`: tempi e scelte visive motivate; risponde a storico/sceneggiatore.
- Critico indipendente → `google/gemma-4-31b-it:free`: obiezioni specifiche e priorità unica di correzione.

**Non sono quattro diversi modelli:** sono quattro ruoli di due modelli. Nessun dibattito o revisione iterative oltre il primo giro, limite quattro chiamate. Ogni risultato è NON approvato, non dimostra visione/ASR/fedeltà delle immagini. I risultati precedenti vengono passati al turno successivo, quindi la critica può proporre una correzione contestuale.

Codice `src/g0dm0d3_free_four_roles_v1.py`; report `REPORT.json`, `ANDROID_REPORT.html`; test `tests/test_g0dm0d3_free_four_roles_v1.py`; workflow `.github/workflows/g0dm0d3-free-four-roles-v1.yml`.

**Protezione costi**: nessun modello `auto`, `openrouter/free` o senza `:free`; verifica prezzi live ufficiali; `provider.allow_fallbacks=false`, `provider.max_price.prompt/completion=0`; `max_tokens=720`; niente retry, nessun cron, nessuna lettura di altri segreti. Se OpenRouter rifiuta, viene registrato stato `incomplete_no_retry`, non vengono tentate altre AI. Eventuale costo nonzero segnalato dal provider → blocco.

## Procedura Android (chiave mai in chat)
1. Aprire **OpenRouter → API Keys**: https://openrouter.ai/settings/keys. Generare una chiave *per il solo laboratorio*, preferibilmente con limite di spesa zero e senza abilitare modelli a pagamento, se le impostazioni dell'account lo consentono.
2. In Chrome Android, su GitHub repository `GGIANLUCAA/Tra-le-pagine-` → **Settings → Secrets and variables → Actions → New repository secret**, nome ESATTO `OPENROUTER_API_KEY`. Inserire il token nella schermata protetta GitHub, **non** nel repository, nei messaggi ChatGPT o nei rapporti.
3. Aprire GitHub → Actions → **G0DM0D3 FREE | Four-role cinematic board (isolated trial)** → **Run workflow**. Il solo primo avvio di verifica può mantenere `execute_free_trial=false` (zero chiamate). Per il tentativo vero usare `true`, scegliere formato e un soggetto PUBBLICO.
4. Scaricare dall'esecuzione il pacchetto `G0DM0D3_FREE_FOUR_ROLES_...`, aprire `ANDROID_REPORT.html` dal telefono. `REPORT.json` contiene modelli, numero di richieste e quattro risposte solo se davvero ricevute.

Una chiave assente produce `blocked_missing_openrouter_key` e il workflow live fallisce chiaramente, ma conserva il report. Non copiare nella richiesta dati privati, account o fotografie di persone. La documentazione sulle policy OpenRouter: https://openrouter.ai/pricing e https://openrouter.ai/collections/free-models .

## Stato del primo esperimento
- Diagnostica pubblica OpenRouter e segreto Actions: completata (GET; nessun modello invocato).
- Codice e test del laboratorio: da attestare con esecuzione CI verde.
- Quattro risposte reali di AI diverse: **non ancora prodotte** finché il proprietario non collega una chiave al secret GitHub e lancia esplicitamente il test.
- Integrazione permanente in rendering ArtVision/La Storia Rivive/Giuliano: **non attiva**, richiede confronto reale di qualità, quote, diritti e fatturazione.

Non considerare l'assenza di chiave come "modelli non funzionano"; né la sola presenza del codice come "quattro AI già collegate".
