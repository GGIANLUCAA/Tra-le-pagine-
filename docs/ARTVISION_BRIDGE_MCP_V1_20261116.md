# ArtVision Bridge MCP V1 — consultazione pubblica, isolata, senza costi aggiuntivi

Data: 16 novembre 2026. Responsabile: proprietario ArtVision.

## Obiettivo e confini

Un server MCP su Cloudflare Worker consultabile da TRAE (solo se la modalità Work/Code offre un client MCP remoto) e ChatGPT (solo dopo il collegamento di un plugin compatibile). Entrambi consultano lo stesso stato **pubblico e verificabile** del repository GitHub, invece di doversi rispiegare sempre tutto.

Questa V1 NON sincronizza direttamente chat private e NON legge memoria personale di ChatGPT o sessioni private TRAE. Non modifica codice, master MP4, ZIP, code, workflow o siti. Nessun modello a pagamento, database o automazione aggiuntiva.

## Architettura

- Cloudflare Worker separato: artvision-bridge-mcp-v1.
- Endpoint previsto: https://artvision-bridge-mcp-v1.600led.workers.dev/mcp dopo deploy e attivazione del sottodominio.
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
