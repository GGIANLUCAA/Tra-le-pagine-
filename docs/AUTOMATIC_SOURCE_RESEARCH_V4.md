# Ricerca automatica delle fonti V4 — ArtVision e La Storia Rivive

**4 novembre 2026** — Integrazione non distruttiva delle API pubbliche nei cicli di ricerca gia esistenti.

## Cosa e realmente automatico

- **La Storia Rivive**: il workflow gia attivo `.github/workflows/storia-rivive-v101-auto-3h.yml` continua a preparare una fonte originale ogni tre ore. Subito dopo la generazione del vero `WORK_ORDER.json`, una nuova fase chiede **una sola ricerca mirata a una sola API gratuita**. Il risultato compare in `SOURCE_RESEARCH_COMPANION_V4.json` nel medesimo artifact `STORIA_V101_RESEARCH_...`, e il relativo stato in `CYCLE_STATUS.json`. La nuova ricerca non sostituisce la fonte originale e, se il provider fallisce, il lavoro V101 prosegue.
- **ArtVision**: il nuovo workflow `.github/workflows/artvision-owner-source-research-v4.yml` viene eseguito ogni tre ore su GitHub Actions (UTC `41 */3 * * *`) e prepara una scheda per **una sola opera** della coda approvata di dieci, con selezione deterministica e senza duplicati nel singolo ciclo. Il processo non e un nuovo owner del rendering e non modifica i job della produzione ArtVision 4x1.
- Le due schedulazioni sono distinte **solo per la ricerca**. Un nuovo artifact non significa nuovo video.

## Selezione intelligente, non casuale

Le ricerche sono definite in `config/source_cycle_companion_v4.json` e partono da:
- I **dieci** lavori nella coda `queue/artvision_owner_selected_ten_20261102.json`, saltando Dalí perché bloccato dai diritti. Per *The Night Watch* usa Rijksmuseum; per *The Garden of Death* usa Finna; per altri dipinti cerca la specifica opera su Commons.
- Il **vero ordine V101** di `queue/storia_rivive_candidates_v58.json`, con identificativo, pagina sorgente e ciclo storico non modificati. Le ricerche aggiuntive nei cataloghi non possono rimpiazzare il film originale o essere presentate come riprese dello stesso evento senza verifica.

Il limite e **1 query, 1 risultato, massimo 2 richieste provider** per ciclo/progetto, zero credenziali, zero richieste API a pagamento. Timeout e nessun retry automatico su 429. Il ciclo e tracciato con ID UTC e SHA256 del piano. Il risultato resta candidato: nessun asset approvato automaticamente.

## Cosa NON cambia

Nessun download dai nuovi archivi, nessun filmato Vidu, GPU, restauro o voce addizionale, nessun MP4/ZIP generato dalla ricerca, nessuna modifica delle cornici, delle sale, dei titoli, delle copertine o dei post social. Tutti i controlli sui diritti italiani, le dimensioni fisiche, autenticita dell'opera, riferimenti fotografici e QA continuano a valere; nessuna falsa approvazione umana. Il video non viene pubblicato. I risultati sono salvati come artifact GitHub Actions, non caricati automaticamente sul sito o in Video Library Studio.

La ricerca aiuta i cicli di **preparazione** delle fonti. Il consumo automatico dei candidati nella creazione video e intenzionalmente bloccato fino alla verifica effettiva delle licenze e della pertinenza dell'immagine originale; quindi **non equivale** a una produzione video automatica end-to-end.

## File e test

- `src/production_source_research_v4.py`
- `config/source_cycle_companion_v4.json`
- `tests/test_production_source_research_v4.py`
- `.github/workflows/artvision-owner-source-research-v4.yml`
- `.github/workflows/storia-rivive-v101-auto-3h.yml` (integrazione additiva)

Test: selezione deterministica per fascia oraria, corrispondenza alla coda proprietario, esclusione Dalí, ciclo V101 coerente, un'unica ricerca, limiti API, errori 429 senza retry, candidate rights=`pending`, no download/render/pubblicazione, no costi. Gli errori del provider sono riportati nello stato e non vengono camuffati da risultati riusciti.

## Consultazione e fallback

Da Android aprire Actions:
- **ArtVision V4 - Ricerca fonti automatica per le dieci opere** — artifact `ARTVISION_OWNER_SOURCE_RESEARCH_V4_...`.
- **La Storia Rivive V101** — artifact `STORIA_V101_RESEARCH_...` con nuova scheda V4.

Le automazioni ChatGPT continuano a essere gli owner della produzione e possono consultare questi report. Questa modifica **non** autorizza nuove esecuzioni di rendering in parallelo.
