# NVIDIA NIM — verifica chiave senza spese (04/11/2026)

## Risultato verificato

Il progetto ora cerca in GitHub Actions i seguenti nomi di Repository secrets:
`NVIDIA_API_KEY` (raccomandato), `NVIDIA`, `NVIDIA_NIM_API_KEY`,
`NVIDIA_NIM`, `NGC_API_KEY`, `INVIDIA`, `INVIDIA_API_KEY`.

Test senza rete verso i provider: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41806129627

Esito: **NVIDIA NIM NON RILEVATA** con questi nomi in quel run.
Questo non dimostra che il proprietario non abbia creato una chiave
nell'account NVIDIA; indica soltanto che il workflow GitHub non riceve
un secret non vuoto con i nomi sopra elencati.

## Singolo passaggio dell'utente, se serve

Aprire:
https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions

Controllare che il secret sia nello stesso repository, sezione
Repository secrets. Nome consigliato **NVIDIA_API_KEY**.
Copiare la *chiave originale* da https://build.nvidia.com/settings
solo nel campo valore del secret GitHub e salvare. Non mettere mai
la chiave nel codice o in chat. Se è già presente con un nome diverso,
comunicare soltanto il nome.

Eseguire il workflow manuale:
https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/secret-presence-audit-v1.yml

Questo verifica ESCLUSIVAMENTE la presenza, senza stampare il token o
effettuare richieste API NVIDIA.

## A che cosa servirebbe nel progetto

NVIDIA NIM / NVIDIA API Catalog fornisce inferenza remota per modelli
di linguaggio e alcuni modelli multimodali. L'endpoint è
https://integrate.api.nvidia.com/v1.
Potrebbe essere utile **solo a titolo sperimentale** per confrontare
bozze di sceneggiature, narrazioni, descrizioni social e note sulle fonti.
Non è HyperFrames e non sostituisce Vidu, FFmpeg, restauratori
video o l'analisi visiva di un MP4.

NVIDIA indica accesso gratuito per **prototipazione e test**, non una
fornitura illimitata e gratuita per produzione commerciale.
Non abilitare inferenza automatica per i filmati commerciali o pubblici
senza licenza, termini e condizioni di costo verificati.

Riferimenti:
- https://docs.api.nvidia.com/nim/docs/product
- https://docs.api.nvidia.com/nim/docs/api-quickstart
- https://build.nvidia.com/
- https://build.nvidia.com/api-catalog-terms

La nostra policy costo-zero rimane **deny all** per i provider
non esplicitamente approvati e verificati. Nessun modello NVIDIA
è stato attivato, nessun credito NVIDIA consumato.
