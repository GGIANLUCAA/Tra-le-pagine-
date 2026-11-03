# FreeLLMAPI V1 — integrazione editoriale opzionale (03/11/2026)

## Stato

**Prototipo in ramo di sviluppo, disattivato per impostazione predefinita.**
Non è un server già installato, non genera MP4, non usa crediti Vidu,
non pubblica e non sostituisce i controlli esistenti.

Repository originale: https://github.com/tashfeenahmed/freellmapi
(software MIT; per ciascun provider restano validi termini d'uso e quote).
L'upstream lo presenta come strumento per sperimentazione personale:
prima di usarlo nei nostri contenuti pubblici o commerciali bisogna
verificare i termini di ogni fornitore. Le grandi quote pubblicizzate
non sono automaticamente disponibili a questo progetto.

## Divisione dei ruoli

- ECC: possibile livello futuro per agenti, regole, verifica e memoria.
- FreeLLMAPI: router locale OpenAI-compatible, verso fornitori configurati.
- ArtVision / La Storia Rivive: proprietari di fonti, diritti, QA, montaggio,
  voce, Video Library Studio, ZIP e pubblicazione.

Il modulo Python opzionale è src/freellmapi_editorial_v1.py.
Accetta cinque compiti, **solo per bozze**:
1. storyboard — ideazione di sequenze da verificare con materiali autentici.
2. narration — prima bozza della voce italiana.
3. social — bozza dei post, con titoli pubblici in inglese.
4. source_notes — sintesi di fonti realmente fornite, non ricerca automatica.
5. qa_second_opinion — controllo testuale dei manifest, mai analisi visiva
   presunta del MP4.

Le risposte restano in stato draft_unreviewed, con diritti, fonti, approvazione
artistica e pubblicazione **false**. Nessuna risposta AI può cancellare i
vincoli in AGENTS.md, docs/REGOLE_ATTIVE.md, V91/V94/V96/V99, V118/V119 o V134.

## Installazione opzionale SOLO locale

1. Esaminare e installare l'upstream su una macchina propria:
   https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/install/01-install.md
   Non eseguire script remoti non ispezionati.
2. Lasciare il router sulla porta locale 3001: NON esporre la dashboard
   direttamente a Internet. Configurare account, modelli e chiavi upstream
   nella dashboard locale.
3. Abilitare solo modelli di cui sono stati controllati costo, privacy e
   eventuali diritti d'uso commerciale. FreeLLMAPI instrada anche su provider
   a pagamento, se vengono aggiunti: NON garantisce costo zero.
4. Recuperare la chiave unificata FreeLLMAPI dalla dashboard. NON usare token
   Vidu o GitHub, né incollare credenziali nella chat, nel codice o nei log.

Verifica offline senza chiavi, senza rete e senza scrivere file:

    python src/freellmapi_editorial_v1.py --task social --prompt-file /tmp/nota_pubblica.txt --output /tmp/social_draft.json

Solo dopo configurazione autorizzata, esportare da un gestore di segreti
locale FREELLMAPI_API_KEY e attivare manualmente una singola chiamata:

    FREELLMAPI_ENABLED=1 python src/freellmapi_editorial_v1.py --task social --prompt-file /tmp/nota_pubblica.txt --output /tmp/social_draft.json --execute

Variabili:
- FREELLMAPI_ENABLED: solo il valore 1 permette una richiesta.
- FREELLMAPI_API_KEY: chiave unificata del router; mai in Git.
- FREELLMAPI_BASE_URL: default http://127.0.0.1:3001/v1 (solo loopback).
- FREELLMAPI_MODEL: default auto, configurato nel router.

Anche con router locale, i prompt viaggiano ai provider upstream configurati.
Inviare solo materiali pubblici/autorizzati, senza dati personali o segreti.
Non sono ammesse destinazioni remote in questa V1.

GitHub Actions hosted non può raggiungere il router installato sul PC
dell'utente attraverso localhost. Un collegamento automatico futuro
richiederebbe un runner self-hosted o una soluzione privata sicura e
specificamente autorizzata; NON è già attivo.

## Test di non regressione

    python -m unittest discover -s tests -p 'test_freellmapi_editorial_v1.py' -v

I test sono offline: blocchi per disattivazione predefinita, segreti mancanti,
indirizzi remoti, path inaspettati, task non editoriali, risposte vuote o
eccessive e falsi stati di approvazione.

## Condizioni prima dell'eventuale uso operativo

- Licenze e ToS verificati per ogni provider.
- Host sicuro e persistente, con accessi e segreti protetti.
- Tre prove comparative con bozze precedenti, senza modificare i master.
- Nessun nuovo owner delle code e nessuna spesa senza permesso.
- Qualunque revisione visuale, approvazione artistica e sincronizzazione
  restano gestite dai sistemi esistenti.

Questa modifica non installa ECC, non installa il router upstream e
non cambia nessuna automazione o pubblicazione esistente.
