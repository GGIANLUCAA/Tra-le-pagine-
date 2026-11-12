---
name: artvision-ci-triage
description: "Usa questa skill per indagare GitHub Actions, run fallite, PR bloccate, asset non scaricabili o workflow del repository Tra-le-pagine-. Diagnosi prima della correzione; vietati retry a pagamento e merge automatici."
---

# ArtVision: triage dei workflow senza regressioni

## 1. Verifica GitHub prima di intervenire
- Leggi `AGENTS.md`, `docs/REGOLE_ATTIVE.md`, il workflow specifico e la branch/ref effettiva.
- Ricava lo stato attuale della run, eventuali nuovi tentativi, job, step e *log reali*. Un alert storico nel pannello NON dimostra un guasto attivo.
- Controlla se il file atteso è nel repository, in GitHub Artifacts, in Release o in un archivio distinto. URL GitHub o metadata non bastano come prova del download integrale.
- Individua il primo errore causale, separandolo dalle conseguenze a cascata.

## 2. Classifica correttamente
- `ACTIVE_FAILURE`: errore riprodotto nell'ultima run pertinente.
- `HISTORICAL_RECOVERED`: run storica fallita, ma versione successiva riuscita; citare entrambe.
- `SOURCE_OR_RIGHTS_BLOCK`: mancano fonte/licenza/asset affidabili.
- `DOWNLOAD_UNVERIFIED`: metadati presenti, integrità/download non provati.
- `ARTISTIC_REVIEW_PENDING`: file forse tecnicamente buono ma senza visione/ascolto e validazione.
- `TRANSIENT_EXTERNAL`: rate limit, endpoint/provider instabile o connessione incerta; distinguere da errori deterministici.

## 3. Piano di correzione minimo e isolato
- Leggi i test esistenti; modifica soltanto il punto dimostrabilmente responsabile.
- Non interrompere la coda owner ArtVision, non duplicare job, non attivare cron, non riavviare batch Vidu, Gemini o provider con costo.
- Se occorre codice, crea un branch e PR **draft** separati; preserva main, master, Release, asset e impostazioni pubblicazione.
- Verifica sintassi, test interessati, regressioni e regole fail-closed; riporta i comandi realmente eseguiti e risultati. Non dichiarare test PASS se non eseguiti.
- Quando il problema dipende da servizi esterni, preferisci controlli read-only e un fallback consentito. Evita retry di POST se lo stato del provider è ambiguo.

## 4. Report obbligatorio
Fornisci: workflow + run ID + timestamp, branch/commit, step fallito, errore causale con estratto di log, stato **attuale**, impatto sull'MP4 reale, eventuale patch/PR, test eseguiti, rischio residuo. Distingui **CI**, **disponibilità byte**, **qualità artistica**, **diritti** e **autorizzazione a pubblicare**.

Non dichiarare video pronto o in produzione autonoma per il solo successo della CI. In assenza di prova usa `UNVERIFIED`; chiedi intervento solo per un blocco reale che non consente alternative sicure.
