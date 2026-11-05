# La Storia Rivive — V293 · Remaster dai lavori esistenti + riferimenti visivi (05/11/2026)

## Nuova decisione editoriale del proprietario
Priorità a **4–5 MP4 completi al giorno come obiettivo produttivo**, recuperando innanzitutto i filmati e gli asset migliori già prodotti, NON ripartendo da zero ogni volta. Nessuna produzione in massa a costo della qualità, nessun riciclo spacciato per video nuovo, nessuna pubblicazione senza permesso. Preservare isolamento dai formati ArtVision/Cinema Reale.

## Riferimenti del proprietario da consultare ad ogni produzione
- Esempi forniti dall'utente **43054.mp4, 43055.mp4, 43056.mp4**, analizzati in `docs/LA_STORIA_RIVIVE_GOLD_REFERENCE_43054_43055_43056_V82.md` e `docs/LA_STORIA_RIVIVE_V108_BENCHMARK_43055_43056_E_DOWNLOAD.md`: vero movimento archivistico B/N, stesso frame → ricostruzione fotografica I2I nitida e naturale, volti/tessuti/ambienti leggibili; la regia e le durate sono **ispirazione, non copia meccanica**; ignorare i loro outro pubblicitari e non riutilizzare i video altrui come sorgenti.
- **San Francisco 1906 V98**, unico nostro riferimento esplicitamente definito "accettabile", quindi **minimo artistico**, non master perfetto né automaticamente pubblicabile: https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/tag/storia-rivive-san-francisco-1906-v98-4-real-i2i-1-real-vidu
- Controlli necessari: `docs/LA_STORIA_RIVIVE_V99_ANTI_REGRESSIONE.md` e V91/V94/V96/V99, QA artistico effettivo separato.
- **Da evitare**: `44518.mp4` già bocciato, New York V95.1 (`44486.mp4`: Vidu staccato dal frame), Bombay `44371.jpg` (fascia titolo invadente); niente DDColor-only spacciato per vera fotografia restaurata, niente soggetti inventati, look arancione, freeze eccessivi o immagini simulate statiche chiamate movimento.

## Inventario reale del 05/11: 41 GitHub Releases consultate, non 41 video approvati
La seguente è una **graduatoria di lavoro**, non l'esito di nuova ispezione frame-by-frame. Conservare identità e SHA di ogni asset originale, verificare i diritti applicabili in Italia.
| Priorità | Materiale esistente / release | Utilizzo | Blocco / controllo prima di parlare di master |
| --- | --- | --- | --- |
| **0 GOLD MINIMO** | SF1906 V98: `storia-rivive-san-francisco-1906-v98-4-real-i2i-1-real-vidu` | Baseline A/B, recupero tecnica e regia approvata come minimo | Già consegnato, **non contarne una copia identica come nuovo video**; diritti/QA per nuovo uso |
| **1 REMASTER** | Bombay 1929 V98.1: `storia-rivive-bombay-1929-v981-natural-color-real-vidu` | Master esistente I2I + clip Vidu autentica + correzione palette; candidato alla rifinitura mirata | QA artistico completo, microvolti, diritti italiani; non spendere nuovi crediti per correggere montaggio |
| **2 REMASTER/SEPARAZIONE** | Paris 1900–1918 V85: `storia-rivive-paris-1900-1918-v85-4plus1-vidu-moving-finale` | Riordinamento con clip Vidu esistente e colori regolati | Filmati originali 1918 e 1900: **non rappresentarli come unico momento storico**; clip Walkway non automaticamente Gold |
| **3 RIPROGETTAZIONE SULLA SORGENTE** | Coney Island 1903 V73: `storia-rivive-coney-island-1903-v73` | Recuperare sorgente B/N autentica, scene e montaggio se fedeli; nuovi restauri I2I | Vecchio formato non soddisfa automaticamente benchmark V98; serve una nuova clip Vidu source-locked solo dopo bilancio |
| **4 RIPROGETTAZIONE SULLA SORGENTE** | Venice 1896 V81: `storia-rivive-venice-1896-original-color-film-v81` | Valutare più scene reali del film e nuovi restauri mirati | Rispettare qualità delle scansioni, licenza e assenza di volti inventati |
| **5 CLIP RIUTILIZZABILI SOLO SE MATCH** | V84: `storia-rivive-v84-vidu-five-full-motion-previews-20261029` | Prima ispezione: STATION `03` e MOVING_WALKWAY `05`, promettenti ma non approvate | Clips `01`, `02` scartate per prompt sbagliato; `04` non approvata. Stessa scena/fotogramma originali obbligatori |

## Processo senza stalli
1. Coda **REMASTER_EXISTING** prima di **NEW_SOURCE**: per ciascun candidato recuperare MP4/ZIP REALI da release, sorgente, diritti, file I2I, audio e Vidu collegati; fare manifest con SHA. Un vecchio video non è "nuovo" per il solo cambio nome/copertina.
2. Fare lavoro in **lotti da massimo 5 episodi**: se una fonte/copia non è adatta, declassarla con motivo verificato e passare subito al successivo. Non fermare gli altri per 429, diritto incerto o saldo Vidu sconosciuto.
3. Preset regia da scegliere **per soggetto**: alternanza autentico B/N → freeze dello stesso frame → fotografia moderna source-locked, colore coerente, ritmo misto e hook iniziale rapido; eventuale Vidu SOLO se **nuovo o già esistente e corrispondente esattamente al frame**. Non imporre 5 scene fisse per generi diversi solo per imitare gli esempi.
4. Vidu: controllare API/ledger e costi prima di un nuovo POST, **mai doppio POST su esito ambiguo**. Se bloccato, completare fino a stadio PREPARED gli episodi indipendenti e passare a rimontaggi coerenti con **clip già pagata per la stessa inquadratura**; non definire finali video senza il componente obbligatorio.
5. QA quantitativo V91/V94/V96/V99 **su file reali**, più visione intera e confronto dei frame; se solo codec/ZIP PASS è **review pending**, non pronto/pubblicabile.
6. Deliverable per ciascun *nuovo master verificato*: MP4 effettivamente diverso e migliorato, copertina, 4 copy social, fonti/diritti/disclosure, ZIP, link testati. Nessun upload social automatico.
7. **Obiettivo 4–5 al giorno ≠ capacità attualmente provata.** Misurare `finished_and_verified`, non numero di job, candidati o release. Nessuna promessa di esecuzione tra chat senza workflow realmente attivo, testato e autorizzato.

## Stato operativo distinto dall'editoriale
La GitHub Action `storia-rivive-v101-auto-3h.yml` esistente contiene cron ogni tre ore, ma il suo stesso codice salva `status=RESEARCH_PREPARATION_ONLY`, `finished_mp4=false` e `real_vidu_clips_approved=0`: **non è una fabbrica di 4–5 MP4 al giorno**. Implementare il passaggio reale da coda di remaster → recupero asset → render differenziale → QA → release, con job isolati e artifact persistenti; **non dichiarare che sia già implementato o riattivato** solo perché questo documento è stato scritto. Prima di produrre, controllare eventuale disattivazione/duplicati delle automazioni e autorizzazioni richieste.

Questa regola aggiorna SOLO La Storia Rivive; le regole esistenti su costi, diritti, qualità e nessuna pubblicazione restano attive.
