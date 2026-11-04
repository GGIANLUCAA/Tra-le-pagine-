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
