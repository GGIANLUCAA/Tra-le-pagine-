# Studio V11 · Memoria delle correzioni, cronologia per-video e sblocco selettivo
**10 novembre 2026 · Anteprima, senza merge o deploy**

## Obiettivo pratico
Trasformare il feedback del proprietario in una regola utile per i video futuri, senza scambiare una *segnalazione* per un miglioramento tecnico realmente verificato. Dal solo smartphone Android, senza account Cloudflare con token di scrittura e senza aggiungere nuove automazioni.

## Come funziona per il proprietario
1. Dal Centro di controllo apri **Ripara GPT → un quadro → la variante**.
2. Scrivi *cosa è sbagliato / cosa hai corretto*. Scegli una categoria; facoltativamente spunta **«Valuta come regola per i futuri video»**. Tocca **Salva questa correzione**.
3. La nota appare nella **Cronologia di questo video**, con data, categoria e riferimento univoco all'opera/variante. **Salvataggio immediato nel browser Android, non in GitHub**; se localStorage è disabilitato, appare avviso.
4. Premi **Copia e apri la chat**. La richiesta include soltanto le ultime note di quel video, ID lavoro, slot, MP4 se identificato e l'azione richiesta; mai link di chat privati, token o segreti. GPT deve leggere lo stato reale della PR e del repository, verificare duplicati e, se ha i permessi, registrare la nota come `reported` nell'array `history` di `quality/STUDIO_VIDEO_LESSONS_V1.json`, tramite una modifica minima o una nuova PR.
5. La correzione viene prima **proposta / provata**, poi verificata con MP4 prima/dopo, SHA, QA e approvazione owner. Solo una regola esplicitamente `owner_approved` oppure `verified_effective` è propagata ai video futuri. L'approvazione owner di una regola generale esistente NON è prova empirica che sia già migliorata su un nuovo MP4.
6. La cronologia locale è per dispositivo/browser; la memoria **condivisa tra produttori** è il file GitHub dopo l'intervento di GPT. Il semplice pulsante «Salva» non modifica il repository, e un link chat associato rimane solo sul browser.

## Anche La Storia Rivive, WOW LAB e gli altri format
Nella sezione «Ripara GPT» compare anche «Altri video recenti», alimentata **soltanto dai file identificabili nel campione del catalogo**. Il pulsante «Annota / migliora» genera un ID stabile dal file MP4, associa una chat dedicata e riutilizza la stessa cronologia e il processo di registrazione della correzione. I file che il catalogo segnala offline offrono invece «Recupera». Un episodio non elencato qui **non deve essere dichiarato mancante**: cercarlo nella coda/owner della serie. Anche questa funzione è sola lettura verso i server.

## Contratto del registro
- **Fonte:** `quality/STUDIO_VIDEO_LESSONS_V1.json`.
- **Lettore + validatore:** `src/studio_quality_memory_v1.py`.
- **Lezioni iniziali owner-approvate:** 6 vincoli già stabiliti: non stampino AI, sincronia voce/immagini, museo in scala, ritmo del restauro, Vidu dall'inquadratura originale, tagli/zoom non ripetitivi. Tutte hanno `effectiveness_proven_by_new_video=false`: non vengono spacciate come test di successo su filmati nuovi.
- **Segnalazioni:** `history` conserva ID, opera, slot, nota, categoria, provenienza, stato `reported`. Una richiesta non ottiene automaticamente stato `verified_effective` o una nuova lezione.
- **Promozione:** `promote_feedback` richiede feedback verificato, video SHA-256, confronto A/B, riferimento QA e conferma owner. Non modifica l'originale; genera i dati da affidare alla PR. Non può attestare l'efficacia visiva senza osservazione reale: le informazioni sono dichiarazioni validate a livello di schema.

## Collegamento ai processi attuali
- `src/video_director_v13.py` aggiunge a ogni **nuovo dossier** `STUDIO_QUALITY_CHECKLIST_V1.json`, aggiorna `PROJECT_V13.json` e include in `BRIEF_GPT.md` le regole approvate **pertinenti al formato**, con controlli spiegati. Non rende o riscrive video.
- `src/studio_cycle_handoff_v1.py` allega al **checkpoint già esistente** ArtVision/Storia l'elenco di ID delle lezioni trasferibili. Un handoff di ricerca rimane ricerca: MP4 prodotti = 0, Gold e pubblicazione = false.
- `AGENTS.md`, `START_HERE_GPT.md`, `docs/REGOLE_ATTIVE.md` obbligano le future chat/owner a consultare il registro e distinguere note da regole.

## Sblocca ciò che è possibile
Nella sezione Ripara GPT il pulsante prioritizza fino a dieci slot ArtVision **non visionabili**, con priorità `offline → registrato ma non accessibile → non individuato`. Dalí escluso. Non include slot con stato sconosciuto o fonti non disponibili. Trasmette un **piano per GPT**, non lancia workflow: GPT deve controllare run in corso/owner e provare recupero del master prima di un nuovo render. Nessun duplicato, nuova spesa o autopubblicazione.

## Cosa ancora non si può promettere
- **Non è una correzione automatica del filmato già pubblicato.** È una memoria applicata ai nuovi brief e una guida a riparazione tramite chat.
- Il pulsante «Salva» mantiene i dati sul telefono, mentre la persistenza cross-device richiede un commit GitHub autorizzato; è visibile nella PR.
- Nessun controllo automatico dentro il browser può dimostrare che un MP4 è stato migliorato artisticamente: servono visione, ascolto, hash del file e confronto.
- I workflow e le automazioni di produzione che **non** passano da V13 o da handoff possono leggere le istruzioni V321 nei documenti, ma non sono stati dichiarati automaticamente integrati a livello di renderer. L'integrazione di ogni renderer va confermata prima di parlare di apprendimento applicato in massa.
- Prima del deploy: verifica browser Android reale, clipboard, salvataggio locale, stato delle fonti, protezione anti-duplicato, gating delle regole e regressioni. Sito pubblico intatto.

## Test
`tests/test_studio_quality_memory_v1.py` verifica schema, scoping, nuova checklist V13, handoff senza render, blocco promozione senza prove, fallback su dati mancanti.
`tests/control-center-action-hub-dom.test.cjs` verifica tocchi, cronologia salvata, messaggio GPT, sblocco e assenza di richieste di scrittura.
CI in `.github/workflows/artvision-control-center-preview-ci.yml` compila la preview Worker ma **non la distribuisce**.
