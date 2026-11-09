# Studio · passaggio di consegne tra cicli esistenti V1 (10/11/2026)

## Obiettivo
Le automazioni ChatGPT già attive e i workflow GitHub di ricerca esistenti devono poter distinguere **cosa è stato provato, cosa manca e quale passo è consentito**. Nessuna nuova automazione, cron, renderer, provider, recupero a pagamento o pubblicazione.

## Output per ogni ciclo
`OWNER_HANDOFF_V1.json` viene allegato agli artifact **già esistenti**:
- `ARTVISION_OWNER_SOURCE_RESEARCH_V4_<run_id>` dell'esistente `artvision-owner-source-research-v4.yml`;
- `STORIA_V101_RESEARCH_<run_id>` dell'esistente `storia-rivive-v101-auto-3h.yml`.

Il codice `src/studio_cycle_handoff_v1.py` legge rapporti realmente presenti, senza fetch, provider o effetti collaterali. La ricerca fonte V4 passa per stati `SOURCE_CANDIDATE_NEEDS_REVIEW`, `NO_SOURCE_MATCH`, `RESEARCH_NOT_READY` oppure `EVIDENCE_INCOMPLETE`. La V101 può mostrare `PREPARATION_ONLY_NO_VERIFIED_RESEARCH` quando il lavoro d'archivio risulta preparato ma la ricerca facoltativa fallisce. L'assenza dei file, cicli non coincidenti, identità errate, permessi incoerenti o promozioni non autorizzate producono **dati incompleti, mai successo**.

Gli output attestano **sempre**: `new_finished_mp4=0`, `auto_render_started=false`, `master_mp4_verified_by_handoff=false`, `owner_artistic_approved=false`, `auto_publish_authorized=false`, `paid_api_calls_authorized=false`. Il prossimo passo è una *raccomandazione*, non un task eseguito.

## Regole operative per le automazioni già create
1. Prima di procedere con un'opera/episodio, consultare la coda owner attuale, `AGENTS.md`, `START_HERE_GPT.md`, `docs/REGOLE_ATTIVE.md` e gli eventuali checkpoint render più recenti. Il rapporto fonte V4 è complemento, non proprietario della coda.
2. Se esiste un `OWNER_HANDOFF_V1.json` dell'ultimo ciclo corrispondente, leggere `project`, `item_id`, `cycle_id`, `state` ed `evidence`. Se un artifact non è disponibile o scaduto, segnalare 'prova non disponibile', non un blocco fittizio o un video finito.
3. Se `SOURCE_CANDIDATE_NEEDS_REVIEW`, verificare la **fonte primaria, l'esemplare esatto, la licenza, i diritti territoriali, la qualità dell'asset e i file veri**. Solo il workflow owner autorizzato decide il render, secondo V80/V118/V119 o V91/V94/V96/V99. Non convertire `RESEARCH_CANDIDATES_PENDING_REVIEW` in `ready` senza prove.
4. Se `NO_SOURCE_MATCH` o `RESEARCH_NOT_READY`, massimo due verifiche ragionevoli sicure; passare a un altro soggetto indipendente senza doppie chiamate a pagamento o duplicati. Nessun retry automatico qui.
5. I nuovi video contano soltanto quando i byte MP4 e pacchetto ZIP esistono, con decode, SHA, CRC e prove concrete di consegna. Nessun automatic Gold o pubblicazione. I file di approvazione artistica rimangono distinti dalla verifica tecnica.
6. **Per ArtVision**, la vecchia V4 di ricerca riguarda la coda delle dieci opere; non sostituisce la shortlist delle trenta né il produttore 4×1. Dalí *The Temptation of St. Anthony* resta escluso.
7. **Per La Storia Rivive**, il workflow V101 rimane ricerca/preparazione, non realizza 4–5 MP4 al giorno per il solo fatto di eseguire il proprio cron. Il progetto deve rispettare il benchmark V98 e la priorità visiva effettiva dell'owner.
8. Nessun aggiornamento all'utente a ogni esecuzione vuota: avvisare su nuovi MP4 reali, miglioramenti tecnici importanti e blocchi seri con causa/intervento.

## Limiti tecnici
- Gli artifact scadono secondo le policy GitHub (i workflow attuali usano 14 giorni): non sono uno storico permanente; non chiamarli ledger immutabile.
- Il file raccoglie un solo report/ciclo, **non** effettua una ripresa tecnica del render, non avvia GitHub Actions e non valuta visivamente i video. La ripresa vera richiede checkpoint producer e QA sui file.
- Lo step nei workflow usa `always()` e `continue-on-error` per non mascherare il risultato originale. Anche in caso di errore nella generazione del riepilogo l'artifact originale viene preservato, se esiste.
- Nessuna API a pagamento o modifica a Video Library Studio, R2, WOW LAB, master o workflow di produzione.
