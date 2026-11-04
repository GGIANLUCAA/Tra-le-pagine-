# NVIDIA API — verifica reale del 4 novembre 2026

## Risultato verificato

Il secret NVIDIA in GitHub Actions esiste e viene reso disponibile al workflow:
il controllo `check-github-secret-on-main` è passato.

Una GET al catalogo NVIDIA `https://integrate.api.nvidia.com/v1/models`
ha restituito risposta valida nel report live API:
https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41883246691

Due richieste di **inferenza reali** hanno invece fallito:

1. **Video:** `POST https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano`,
   `model_mode=text2video`, 25 frame, 480 verticale, unica richiesta.
   **HTTP 404**. Non è stato generato alcun MP4.
   https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41914666677
2. **Testo:** `POST https://integrate.api.nvidia.com/v1/chat/completions`,
   modello `nvidia/nemotron-3-super-120b-a12b`, unica richiesta.
   **HTTP 404**. Non è stata prodotta una bozza testuale.
   https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41914849398

Nessun retry automatico, nessun fallback a servizio a pagamento e
nessun video pubblicato. Le chiamate GET non validano necessariamente i
permessi dei singoli modelli: **NON segnare NVIDIA come generatore attivo**.

## Azione successiva

Verificare dal proprio account https://build.nvidia.com/ quale endpoint
hosted è effettivamente disponibile e quale chiave/entitlement richiede.
Non incollare credenziali nella chat. Dopo aver verificato i permessi si
può effettuare una nuova prova manuale nel workflow
`.github/workflows/nvidia-nim-dev-v1.yml`; i job temporanei di inferenza
su push sono stati rimossi per evitare consumi involontari.

**Vidu è dichiarato funzionante dal proprietario**, ma non fa parte dei
due test NVIDIA qui documentati. Non modificare i flussi Vidu per risolvere
l'accesso NVIDIA. La generazione NVIDIA resta **bloccata** fino a evidenza
di almeno un file MP4 valido e leggibile o una risposta testuale riuscita.

## Diagnosi ampliata — verifica NVIDIA Cloud Functions

Verifica GitHub in sola lettura (nessuna generazione):
https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41919954103

- `GET https://integrate.api.nvidia.com/v1/models`: **HTTP 200**,
  85 voci, incluso `nvidia/nemotron-3-super-120b-a12b`.
- `GET https://api.nvcf.nvidia.com/v2/nvcf/functions`: **HTTP 200**,
  263 funzioni e nomi contenenti Cosmos e Nemotron.
- La presenza in un **catalogo di funzioni** (con visibilità anche pubblica)
  non prova il diritto di invocare quel modello. Non sono stati mostrati
  account ID, token o risultati grezzi.

**Fonti NVIDIA ufficiali:**
- https://docs.api.nvidia.com/cloud-functions/reference/getfunctions_1
- https://build.nvidia.com/nvidia/cosmos3-nano/modelcard
- https://docs.api.nvidia.com/nim/re/reference/nvidia-nemotron-3-super-120b-a12b-infer

**Segnalazioni pubbliche NVIDIA dei medesimi errori:**
- Nemotron: `GET /v1/models` riuscita e `POST /v1/chat/completions` HTTP 404,
  possibile mancata abilitazione `Public API Endpoints`:
  https://forums.developer.nvidia.com/t/request-to-enable-public-api-endpoints-404-function-not-found/387454
- Cosmos3 Nano: endpoint ufficiale `POST /v1/cosmos/nvidia/cosmos3-nano`
  HTTP 404 anche per altri account:
  https://forums.developer.nvidia.com/t/404-error-missing-api-endpoint-code-for-cosmos3-nano-on-build-nvidia-com/372044

**Prossimo passo non tecnico:** rivolgersi al supporto NVIDIA tramite
`help@build.nvidia.com`, chiedendo una verifica delle autorizzazioni
`Public API Endpoints` per il proprio account e della disponibilità reale
Cosmos3 Nano per invocazioni API. NVIDIA rimane bloccata per inferenza fino
alla loro conferma e a un futuro test riuscito. Non inviare mai la chiave API.
Il flusso Vidu continua separato senza alcuna modifica.

**Test one-shot disattivati dopo la verifica**, mantenuti soltanto
workflow manuali con policy zero-spend.
