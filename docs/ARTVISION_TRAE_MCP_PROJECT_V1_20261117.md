# ArtVision — TRAE MCP a livello di progetto (17/11/2026)

## Scopo

Offrire a TRAE un punto di ingresso **gratuito, pubblico e solo lettura** verso le regole ArtVision, lo stato GitHub, i blocchi, l'inbox di prova e la memoria condivisa D1 UE. Questo evita il ricorso a TinyFish per attività che TRAE può fare mediante un client MCP standard.

### File aggiunti

- `.trae/mcp.json`: configurazione MCP a livello del repository, con un solo URL HTTPS verso Cloudflare ArtVision Bridge. Nessun segreto, token o codice eseguibile.
- `integrations/artvision-bridge-mcp/trae-work-mcp.json`: identica configurazione, pronta per l'inserimento manuale in TRAE Work web se il prodotto lo richiede.
- `.github/workflows/trae-project-mcp-config-check.yml`: test che i due file restino identici e privi di credenziali.

### Cosa è confermato e cosa no

1. **Confermato:** la documentazione ufficiale TRAE IDE descrive l'import automatico dei server MCP da `.trae/mcp.json`, **dopo aver abilitato la funzione di progetto nelle impostazioni**. Fonte: https://docs.trae.cn/ide_add-mcp-servers
2. **Confermato:** TRAE Work web supporta MCP HTTP con configurazione manuale dalla sezione Impostazioni > MCP. Fonte: https://docs.trae.cn/work_remote-mcp-server
3. **Confermato:** il server ArtVision Bridge passa il test ufficiale MCP Python, compresi `get_bridge_inbox` e `get_shared_memory`: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43859189334
4. **Da verificare:** TRAE Work **web** non è stato configurato nel tuo account e non ha ancora attestato di aver letto `prova 123`. Non dichiarare la connessione attiva in TRAE Work prima di una chiamata reale.
5. **Importante:** TRAE Work aveva selezionato un vecchio ramo Gold. La configurazione si trova sul ramo **main**; evitare ogni scrittura su `ARTVISION_V6_GOLD_MASTER_APPROVATA_2026-10-20`.

### Test di accettazione in TRAE, senza modifiche

Solo in un workspace autorizzato, sul ramo giusto, richiedere:

> Usa il server MCP artvision-bridge. Chiama get_bridge_inbox e riporta l'ID del messaggio di prova indirizzato a trae. Poi chiama get_shared_memory e indica le regole di voce Critico. Non modificare file, non creare video, non effettuare merge o pubblicazioni.

Risultati attesi: ID `artvision-bridge-smoke-20261116-001`, testo `prova 123`, nota `critical_voice` con Gacrux.

Se il client non mostra gli strumenti, controllare l'abilitazione MCP e il contesto (web/cloud vs IDE), non avviare cicli TinyFish ripetuti. Il server è pubblico e non accetta comandi di scrittura. GitHub Issue #326 è solo un inbox pubblico di test: non pubblicarvi password, cookie o conversazioni private.

### Risparmio crediti TinyFish

La politica è: verificare prima tramite connettori GitHub/Cloudflare e il protocollo MCP; usare TinyFish **solo per passaggi nella UI non raggiungibili direttamente**, preferibilmente una singola esecuzione limitata. Non avviare un'automazione TinyFish autenticata se il profilo non è confermato acceso a TRAE. Non abilitare acquisti o ricariche.
