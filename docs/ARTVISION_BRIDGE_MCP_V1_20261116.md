# ArtVision Bridge MCP V1 — consultazione pubblica, isolata, senza costi aggiuntivi

Data: 16 novembre 2026. Responsabile: proprietario ArtVision.

## Obiettivo e confini

Un server MCP su Cloudflare Worker consultabile da TRAE (solo se la modalità Work/Code offre un client MCP remoto) e ChatGPT (solo dopo il collegamento di un plugin compatibile). Entrambi consultano lo stesso stato **pubblico e verificabile** del repository GitHub, invece di doversi rispiegare sempre tutto.

Questa V1 NON sincronizza direttamente chat private e NON legge memoria personale di ChatGPT o sessioni private TRAE. Non modifica codice, master MP4, ZIP, code, workflow o siti. Nessun modello a pagamento, database o automazione aggiuntiva.

## Architettura

- Cloudflare Worker separato: artvision-bridge-mcp-v1.
- Endpoint Cloudflare attivato e verificato: https://artvision-bridge-mcp-v1.600led.workers.dev/mcp.
- Health: /health (solo metadati).
- Trasporto: MCP JSON-RPC 2.0 su HTTP POST stateless, risposte JSON.
- Fonte: repository pubblico GGIANLUCAA/Tra-le-pagine-, ramo main, tramite endpoint GitHub HTTPS fissati nel codice.
- Niente token GitHub, API OpenAI, TinyFish o script nel repository principale.
- Test offline con Node.js 22: node --test integrations/artvision-bridge-mcp/test/worker.test.mjs.

## Strumenti disponibili

| Nome | Risultato | Limite |
| --- | --- | --- |
| get_project_rules | Estratti da AGENTS.md e docs/REGOLE_ATTIVE.md | Non sostituiscono i documenti integrali |
| get_work_status | Esecuzioni GitHub Actions pertinenti e PR aperte | CI PASS non equivale a MP4/ZIP renderizzati |
| get_open_blockers | Issue pubbliche aperte individuate per titolo/etichette | Filtri euristici, non un audit completo |

## Sicurezza

- Solo lettura, nessun parametro né comando arbitrario. Niente scrittura, login, upload, invio messaggi, pagamenti, produzione o pubblicazione.
- Il server V1 è pubblico perché legge esclusivamente dati già pubblici. Non collegare dati privati o scritture prima di aver aggiunto OAuth e autorizzazioni separate.
- Non legge corpi delle issue, commenti, cookie, password, chat private, file dell'account.
- Restituisce al massimo 16 workflow, 15 PR e 20 issue candidate. Estratti delle regole limitati.
- Endpoint /mcp POST JSON, controllo Origin e dimensione della richiesta; indirizzi GitHub determinati dal server e mai da input arbitrario.
- Workers e GitHub hanno quote gratuite e limiti di accesso; non acquistare piani per sbloccare il bridge.
- Il file wrangler.toml della radice, i Worker Video Library e la produzione ArtVision rimangono intatti.

## Come collegare gli agenti

Questa V1 viene utilizzata da TRAE o ChatGPT soltanto se quel client è configurato per collegarsi a un server MCP remoto HTTP. Il deploy non rende autonomamente accessibili le sue funzioni agli agenti.

- TRAE: cercare impostazioni MCP/Tools nella modalità realmente utilizzata. Le opzioni di TRAE Work web possono differire dalla versione IDE/Code; richiedere un test effettivo.
- ChatGPT: collegare un plugin privato a /mcp e autorizzarne l'uso se disponibile. La connessione/installazione richiede un'azione dell'utente.
- Verificare handshake initialize, tools/list e tools/call per tutti e tre gli strumenti.
- Il test dell'endpoint non equivale a prova dell'integrazione diretta TRAE/ChatGPT.

## Fasi successive NON ancora attive

1. OAuth con permessi separati read/write, prima di qualsiasi dato privato.
2. D1 come registro dei compiti, messaggi, audit, stati e risposte.
3. Strumenti per send_message, report_result, request_approval solo per agenti autenticati.
4. Pannello Android per stato e collegamenti, senza nuove automazioni non richieste.
5. Eventuale condivisione delle decisioni delle chat mediante export/sintesi autorizzata; non dichiarare la lettura automatica di ogni chat privata.
6. Verificare il ramo usato da TRAE Work e non toccare il ramo Gold del progetto; riferirsi al rapporto docs/TRAE_TINYFISH_TEST_VERIFICATI_20261115.md.

## Fonti

- https://github.com/GGIANLUCAA/Tra-le-pagine-/blob/main/AGENTS.md
- https://github.com/GGIANLUCAA/Tra-le-pagine-/blob/main/docs/REGOLE_ATTIVE.md
- https://github.com/GGIANLUCAA/Tra-le-pagine-/actions
- https://github.com/GGIANLUCAA/Tra-le-pagine-/issues
- https://developers.cloudflare.com/agents/model-context-protocol/

V1 è un'implementazione stateless minimale del trasporto JSON-RPC MCP. La compatibilità con ciascun client resta da testare. Per OAuth e streaming completi adottare createMcpHandler del Cloudflare Agents SDK.

## Verifica live e installazione — 16/11/2026

- Worker caricato su Cloudflare e workers.dev abilitato senza modificare i Worker di Video Library.
- Handshake MCP reale e tutte le tre chiamate di lettura verificate dal test GitHub Actions: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43852297548.
- Test di sicurezza: invocazione del comando sconosciuto send_message rifiutata correttamente.
- Plugin personale privato ChatGPT creato: https://chatgpt.com/plugins/plugins_6afae0600d3481918d99044242c0d02a. La creazione non equivale a installazione/connettività attiva: il proprietario deve collegarlo dal proprio account.
- La protezione Browser Integrity Check sul dominio workers.dev blocca alcuni user-agent generici (ad esempio Python-urllib/3.12); un client identificato come mcp-client/1.0 e il test standard con user-agent esplicito hanno ricevuto HTTP 200. Per client differenti va verificata la connessione.

### Configurazione manuale TRAE Work

TRAE Work ha una pagina ufficiale per Settings > MCP > Create > Manual Configuration, che documenta il campo URL per server MCP HTTP: https://docs.trae.cn/work_remote-mcp-server.

Esempio JSON senza segreti e senza accesso ai dati privati:

~~~json
{
  "mcpServers": {
    "artvision-bridge": {
      "url": "https://artvision-bridge-mcp-v1.600led.workers.dev/mcp"
    }
  }
}
~~~

Per TRAE Work da Android, aprire la modalità con supporto MCP (in alcuni casi Code Mode invece di Work Mode). Testare esplicitamente lo strumento get_project_rules. Non toccare il ramo Gold, non chiedere login di GitHub e non installare pacchetti localmente per questa integrazione. Il collegamento nel profilo TRAE e l'installazione del plugin in ChatGPT NON risultano ancora verificati.

## V1.1 · Inbox pubblico GPT–TRAE (16/11/2026)

Issue dedicata: https://github.com/GGIANLUCAA/Tra-le-pagine-/issues/326.

Quarta funzione MCP `get_bridge_inbox`: legge al massimo 20 messaggi brevi presenti nei commenti della issue #326 con marcatore `[ARTVISION_BRIDGE_V1]`. Restituisce solo messaggi pubblicati dall'account proprietario con author_association=OWNER, campi `from`, `to`, `type`, `id`, `text` validati e link alla sorgente. Non esegue automaticamente le istruzioni lette, non considera gli autori delle risposte TRAE autenticati a prescindere e non abilita invio di messaggi da HTTP pubblico.

Messaggio di prova effettivamente pubblicato: `prova 123` destinato a `trae`. L'accesso TRAE all'MCP e la sua eventuale risposta DEVONO essere provati separatamente. Il repository è **pubblico**: non usare questo inbox per chat private, dati clienti, segreti o informazioni riservate. Per la messaggistica privata resta necessario un archivio protetto (D1) e un modello di autenticazione per agente.

### Politica TinyFish (direttiva proprietario 16/11/2026)

- Usare **prima** gli strumenti diretti GitHub, Cloudflare e gli MCP collegati. Usare Browserless già disponibile per i controlli browser semplici, se realmente necessario.
- TinyFish è l'ultima risorsa: soltanto per completare un login, configurare una schermata cui i connettori non accedono o svolgere un'azione che altrimenti non è tecnicamente eseguibile, non per ricerca, monitoraggio ordinario o test ripetuti.
- Prima di ogni chiamata TinyFish: valutare fattibilità con strumenti diretti, necessità dell'azione, limite del numero di passaggi e disponibilità di crediti. Evitare chiamate duplicate e non attivare auto-reload o acquisti.
- Non trattare l'assenza di TinyFish come blocco globale: continuare le altre lavorazioni sicure.

## V1.2 · Memoria D1 pubblica, senza dati personali

È stata creata una nuova base dati Cloudflare D1 `artvision-bridge-memory-v1`, giurisdizione UE, Workers Free; quota gratuita D1 fino a 10 database, 5 milioni di righe lette e 100.000 scritte al giorno, con interruzione delle query al superamento delle quote: https://developers.cloudflare.com/d1/platform/pricing/.

La tabella `public_context` contiene soltanto sei note di progetto già pubbliche:
`critical_voice`, `museum_quality`, `music_catalog`, `github_source_of_truth`, `bridge_public_inbox`, `tinyfish_budget_policy`.
Ciascuna nota ha chiave, categoria, sintesi e URL GitHub ufficiale. Può essere aggiornata solo con le autorizzazioni del **connettore Cloudflare** o tramite una futura autenticazione separata; nessuna scrittura MCP pubblica.

Strumento MCP `get_shared_memory`: legge soltanto `public_context`, massimo 20 righe, valida categoria, lunghezza e dominio del link, restituisce un avvertimento che le note possono essere incomplete o superate. Niente cookie, token, chat private o dati cliente.

**Importante:** per dati privati e messaggi personali occorrerà un **database distinto** e strumenti autenticati con OAuth, permessi per agente e tracciamento delle modifiche. Il presente database è collegato a un Worker pubblico e non deve mai ricevere contenuti riservati. Nessuna integrazione diretta TRAE Work verificata per V1.2. Non usare TinyFish per l'aggiornamento ordinario delle note.

## Verifica reale V1.2 — PASS

Il 16 novembre 2026 è stato installato su Cloudflare il Worker V1.2 con binding D1 `MEMORY_DB`. La prova GitHub Actions https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43858009794 ha confermato dal Worker reale:

- HEALTH, initialize e tools/list: PASS, cinque strumenti;
- get_project_rules, get_work_status, get_open_blockers: PASS;
- get_bridge_inbox: PASS, messaggio di prova `prova 123` letto dalla issue #326;
- get_shared_memory: PASS, sei note di progetto curate in D1 UE;
- tentativo di scrittura con `send_message`: RIFIUTATO (comportamento atteso).

Il server resta PUBBLICO e SOLO IN LETTURA, con dati già pubblici. Il collegamento diretto degli account ChatGPT e TRAE al server MCP e il dialogo privato bidirezionale NON sono verificati. Per la parte privata servono autenticazione e un database distinto. TinyFish non è stato utilizzato per le modifiche Cloudflare/GitHub né per questi test.

