# VIDU · Collegamento comune a tutte le chat ChatGPT del progetto

**Attivo dal 30 ottobre 2026 · API Vidu esistente in GitHub Secrets · Nessuna reinstallazione necessaria**

## Risposta rapida
**Qualsiasi conversazione di «Restauro storico» che disponga del plugin GitHub collegato può inviare una richiesta Vidu tramite lo stesso repository** `GGIANLUCAA/Tra-le-pagine-`, senza dipendere dalla sessione in cui è stato generato San Francisco 1906. **Non significa** che un'altra chat abbia automaticamente gli stessi strumenti, permessi, file temporanei o collegamenti: il plugin GitHub deve essere disponibile in quella conversazione. Se non lo è, va collegato; la chiave Vidu NON va copiata in chat.

**Workflow unico:** `.github/workflows/vidu-chatgpt-project-gateway.yml`  
**Motore:** `src/vidu_project_gateway_v1.py`  
**Comando da ChatGPT:** creare tramite il plugin GitHub un nuovo file UTF-8 `requests/vidu/<id-univoco>.json`. Un push su `main` lo avvia; **non serve** un'azione GitHub `workflow_dispatch`, che il connettore GitHub ChatGPT potrebbe non offrire. Il workflow processa esclusivamente file **aggiunti** sul commit, non file vecchi modificati. Una richiesta per commit, una coda unica.

## Le quattro operazioni
- `balance`: controlla gratis la presenza della chiave API e il saldo, senza generazioni. Il valore numerico rimane nell'artifact privato dell'Action, non nel log o nel repository.
- `plan`: controlla gratis fonte immagine, hash SHA-256, dimensioni, modello, prompt, secondo e credito atteso; produce `FREE_PLAN.json` con codice di approvazione associato a quella precisa sorgente, prompt e spesa. **Nessun POST Vidu.**
- `generate`: possibile soltanto DOPO preventivo e autorizzazione esplicita dell'utente **per quella singola clip**. Richiede codice del piano, frase `AUTORIZZO_<credito>_CREDITI_VIDU`, importo identico al preventivo, conferma esplicita, fonte verificata e ID nuovo. Riserva un ledger GitHub **PRIMA** del suo unico POST a pagamento; se la risposta è ambigua, MAI ritentare. Recupera l'MP4 Vidu originale e la copia con primo secondo B/N→colore sullo **stesso video che già si muove**; nessun optical flow cromatico retroattivo. Video e QA richiedono revisione artistica.
- `collect`: recupera GRATIS tramite GET un task già inviato, utilizzando il `collect_request_id` del ledger. Non genera né addebita nuovi clip. Da usare se la generazione ha impiegato troppo o la collezione è mancata.

## Formato richieste

Per **saldo** (nessuna foto necessaria):

```json
{
  "schema": "vidu_project_gateway_v1",
  "request_id": "vidu-controllo-saldo-20261030",
  "mode": "balance",
  "distribution": { "github_public_preview": false }
}
```

Per **preventivo**:

```json
{
  "schema": "vidu_project_gateway_v1",
  "request_id": "vidu-esempio-piano-20261030",
  "mode": "plan",
  "format": "storia_rivive",
  "source": {
    "release_tag": "TAG_REALE_GITHUB_RELEASE",
    "asset_name": "FOTO_RESTAURATA_REALE.jpg",
    "sha256": "SHA256_REALE_DI_64_CARATTERI",
    "subject_reviewed_by_user": true,
    "provenance_url": "https://pagina-autentica-della-fonte-storica"
  },
  "clip": {
    "model": "viduq2-pro-fast",
    "resolution": "720p",
    "seconds": 5,
    "off_peak": false,
    "audio": false,
    "color_reveal_first_second": true,
    "prompt": "The EXACT people and objects already visible in this image continue moving naturally for the full five seconds. Preserve identities, architecture, garments, perspective, wheels, hands and physical continuity. No camera cut, no still-photo zoom or image morph."
  },
  "distribution": { "github_public_preview": false }
}
```

**ATTENZIONE:** l'esempio qui sopra contiene segnaposto, NON va copiato come una richiesta vera! L'immagine reale deve essere un asset .jpg/.png/.webp di una GitHub Release **dello stesso repository**, la cui impronta SHA-256 sia stata verificata; il contenuto della foto va **guardato e identificato davvero** prima di attribuire un prompt. L'errore della mappatura immagini/prompt V84 aveva sprecato tre generazioni artisticamente inutilizzabili. I valori di `subject_reviewed_by_user` non sostituiscono un controllo semantico reale.

Per **generare**, creare un SECONDO file con `request_id` nuovo e `mode: "generate"`, copiando ESATTAMENTE `source` e `clip` del piano e aggiungendo:

```json
"spend": {
  "approved_max_credits": 16,
  "approved_plan_code": "CODICE_12_CARATTERI_DAL_FREE_PLAN",
  "authorization_phrase": "AUTORIZZO_16_CREDITI_VIDU",
  "user_approved_this_exact_scene": true
},
"distribution": {
  "github_public_preview": true
}
```

L'autorizzazione si richiede all'utente **prima** di creare il file di generazione a pagamento. Per 5 secondi 720p normale il costo riscontrato è 16 crediti; per 2–8 secondi il gateway usa il preventivo Vidu Q2 Pro Fast (`8 + 2 × (secondi − 1)`), da verificare contro il listino e la risposta del fornitore. `github_public_preview: true` pubblica una **prerelease pubblicamente raggiungibile** con i soli MP4 e report QA pubblico; richiede che l'utente accetti questa modalità di consegna. Se non vuole una release pubblica, usare `false`: video conservato nel solo artifact GitHub Actions per 14 giorni.

Per **recuperare** un task inviato senza ritentare il pagamento:

```json
{
  "schema": "vidu_project_gateway_v1",
  "request_id": "vidu-recupero-20261030-01",
  "mode": "collect",
  "collect_request_id": "ID_DELLA_PRECEDENTE_RICHIESTA_GENERATE",
  "distribution": { "github_public_preview": false }
}
```

## Procedura operativa da QUALUNQUE chat del progetto
1. Leggi `AGENTS.md`, `docs/REGOLE_ATTIVE.md` e questa guida. **Non confondere ArtVision 4×1 (quadri), Restauro storico V82 e gateway clip Vidu.** Il gateway genera **una clip**, non inventa automaticamente un master 4+1.
2. Usa il connettore GitHub per verificare la reale immagine storica restaurata e i suoi asset presenti nella release; confronta foto, soggetto, fonte/licenza, scena e prompt. Non inventare SHA o URL né passare collegamenti temporanei ChatGPT come sorgenti al provider.
3. Crea una richiesta `plan` con ID nuovo in `requests/vidu/`, controlla il workflow che il push ha avviato e apri l'artifact `FREE_PLAN.json`. Il saldo può essere verificato separatamente via `balance`.
4. Dopo il permesso esplicito di spesa per la clip specifica, crea una richiesta `generate` diversa, con importo e codice approvato. **Una sola POST Vidu**, serializzata e registrata su GitHub prima dell'invio.
5. Segui lo stato GitHub Actions e scarica l'MP4 vero. Se non è pronto, crea una nuova richiesta `collect` **GET-only**. Non reinviare `generate` con un nuovo ID per la stessa scena in errore.
6. Effettua QA video semantico e tecnico reale (stabilità dei volti/oggetti, movimento effettivo nei secondi 1–5, colori, cartelloni, camera, audio finale). La metrica automatica non equivale ad approvazione artistica.
7. Se autorizzata la release pubblica, fornisci il **link diretto esterno GitHub Release MP4**, con tag `vidu-chat-<id-richiesta>`; verifica la presenza effettiva dell'asset. Evita download `sandbox` non verificati o `Library file not found`.

### Per La Storia Rivive: combinazione 4+1
Usa il gateway per ottenere **una sola clip Vidu** con movimento colore in 4 secondi dopo la transizione B/N del primo secondo. Integra la clip nel renderer V83/V85/V86 con **quattro differenti scene storiche** originali realmente in movimento B/N → congelamento sul fotogramma esatto → **quattro** restauri fotografici AI di qualità comparabile. Stessa fonte/periodo per tutte le scene; colonna sonora continua; raccordi registicamente motivati, senza aloni/ghosting. Non presentare la parte Vidu come film d'epoca originale a colori.

### Sicurezza e risoluzione problemi
- La API key `VIDUOK` oppure `VIDU_API_KEY` è letta soltanto da **GitHub Secrets nel runner**; non va salvata nelle richieste, nei log o in chat.
- Richieste di pagamento senza `spend` completo, SHA corretto, preventivo e permesso esplicito **falliscono prima del POST**.
- Un ledger GitHub in `queue/vidu_api_attempts/CHAT_GATEWAY_V1_*.json` evita doppioni; `cancel-in-progress: false`, coda seriale, `github.run_attempt == 1`. Se un task è ambiguo, usare **collect**, mai ritentare il POST.
- Il connettore GitHub può creare/aggiornare file ma potrebbe **non esporre workflow_dispatch**: il trigger è il **push di nuovo file**.
- L'Action espone crediti e saldi solo nell'artifact con accesso GitHub, non nelle GitHub Releases pubbliche. Nessun automatismo pubblica su Instagram/Facebook o nel sito: rispettare V55.
- Se GitHub non è collegato in una specifica chat, questa chat **non può materialmente avviare il workflow** anche se il codice condiviso esiste; usare lo stesso plugin GitHub collegato all'account/progetto.
- Questo sistema non richiede API Vidu inserite nuovamente, abbonamenti aggiuntivi, token personali condivisi in chat o un computer locale.
