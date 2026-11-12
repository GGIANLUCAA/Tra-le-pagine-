# G0DM0D3 FREE · 4 ruoli REALI su Giuliano Anticitera — Audit critico (12/11/2026)

**RISULTATO CONFERMATO:** quattro risposte REALI di due modelli diversi, non quattro modelli autonomi. Run conclusiva [43277255436](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43277255436) **SUCCESS** con artifact `G0DM0D3_ALL_FOUR_REAL_ROLES_ANDROID_43277255436` (HTML/JSON). PR #292/#293/#294 integrate su `main`. Non è una installazione originaria G0DM0D3: è un laboratorio editoriale con quattro ruoli applicato alla nostra regia.

## Provenienza reale, costi e limiti
- Run [43275046749](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43275046749): 4 tentativi; tre vere risposte da NVIDIA (sceneggiatore), Liquid (storico), NVIDIA (regista), quarta Liquid senza testo perché `finish_reason=length`, 1102 token di ragionamento su 1200.
- Run [43276334272](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43276334272): **sola** quarta risposta Liquid, 2500 token, ancora senza testo (2351 token di ragionamento); tre risultati veri recuperati e verificati SHA256, nessuna delle tre richieste ripetuta.
- Run [43277255436](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43277255436): **sola** risposta critica NVIDIA, positiva. Recuperate le tre precedenti con controllo SHA, una chiamata nuova. Totale storico **6 tentativi** per ottenere 4 risposte, non solo 4 chiamate complessive. I quattro risultati riportano `usage.cost=0`. I costi effettivi dell'intero account non sono certificati da questa sola prova; le richieste erano su modelli `:free` verificati con `provider.max_price=0` e `allow_fallbacks=false`.
- Le quattro voci sono **ruoli editoriali**, non persone: sceneggiatore NVIDIA, storico Liquid, regista NVIDIA, critico NVIDIA. Lo stesso NVIDIA ricopre tre ruoli: il critico NON è indipendente per modello.
- Le AI hanno ricevuto lo **shotmap reale** dei 20 segmenti e il rapporto di allineamento vocale, non hanno visto l'intero film né ascoltato la voce. Alcune risposte riscrivono male le frasi originali o inventano minutaggi. Le loro opinioni NON sono prova di un difetto visivo osservato direttamente.
- Master GIULIANO EP03, voce Gacrux, sorgenti e distribuzione rimangono intatti. Nessun nuovo video/TTS/Vidu, nessuna pubblicazione.

## Verità del master da preservare

Fonte interna indipendente dai modelli: `GIULIANO_03_COMPLETO.zip / TIMING_REAL_VOICE.json` della [run originale 43247270123](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43247270123). Voce originale **126,12 s**, 20 scene; match ASR **261/283 parole** (~92,2%), quindi tempi in parte interpolati: revisione scena/voce a velocità normale ancora necessaria.

1. **00:00–00:07,61**: la voce dice `Nel 1900, alcuni pescatori di spugne scoprono un relitto...`, **non 1901**. L'anno successivo il bronzo emerge nella scena 2 (7,61–14,16). Non modificare il copione/voce per adeguarlo a una proposta AI sbagliata.
2. **07,61–19,26**: due scene consecutive con `asset_id=front` (frammento A), ma frasi diverse. La ripetizione è un candidato **per revisione registica**, non una prova di monotonia misurata psicologicamente.
3. **25,28–32,64**: frase sui denti nel metallo, `asset_id=front`. **50,26–63,32**: narrazione su iscrizioni/raggi X e analisi interne, con fotografie D/C; le fotografie NON sono scansioni radiografiche. I ruoli AI hanno talvolta confuso questi intervalli.
4. **63,32–75,21**: due segmenti da ricostruzione CGI ingranaggi; **75,21–96,00** tre segmenti CGI quadranti, con voci diverse: quadranti/calendario (75,21–82,20), ciclo di 19 anni (82,20–89,37), eclissi/223 mesi (89,37–96,00). È corretto differenziare le inquadrature senza fingere immagini d'archivio nuove.
5. **96–101,4** la voce dice che il sistema dei pianeti è una possibilità proposta dalle ricerche; **101,4–108,97** sottolinea l'incertezza della ricostruzione: NON renderla una certezza visiva.

## Tre miglioramenti pratici da tenere, senza compromettere il master

| Intervallo | Modifica candidata | Gate qualità obbligatorio |
|---|---|---|
| **7,61–19,26 s** | Evitare due riprese fotografiche identiche; far seguire alla vista d'insieme del frammento A un dettaglio motivato, usando solo immagini realmente già verificate e senza stacchi brevissimi. | Ascoltare entrambe le frasi esatte: il secondo dettaglio non deve anticipare artificiosamente la rivelazione dei denti spiegata a 25,28 s. |
| **50,26–63,32 s** | Mantenere foto autentiche correttamente etichettate come frammenti, oppure cercare in futuro una vera tomografia/radiografia con provenienza e licenza verificabili. | Non applicare effetti che facciano passare la fotografia come una scansione X reale. Non inventare una sorgente o una licenza. |
| **63,32–96 s** | Preservare il movimento degli ingranaggi, valorizzato dal proprietario; differenziare gradualmente prospettiva/crop e punti di attenzione nei segmenti calendario, ciclo 19 anni ed eclissi 223 mesi. | Immagine/voce esattamente congruenti, CGI dichiarata scientifica, niente flash <1 s, niente loop riconoscibili, no aumento della quantità di stacchi fine a sé stessa. |

Queste sono **proposte da provare**, non correzioni già realizzate. Un nuovo MP4 richiederebbe QA reale e approvazione artistica separata.

## Proposte AI da SCARTARE

- Lo sceneggiatore propone **1901 nella prima scena**, in contrasto con il vero WAV (1900).
- Lo storico propone una sequenza di **3 frame** o montaggio 'frame per frame': potenziale ritorno agli odiati flash brevissimi.
- Un ruolo assegna i raggi X a **25,28–32,64 s** mentre la voce sui raggi X arriva più tardi; usare i tempi reali.
- Il critico suggerisce un **flash al secondo 82** e un dato sui 'pesi specifici' non pronunciato: violerebbe V320, precisione semantica e preferenze di regia.
- 'Differenziale antico', 'foto scelte già come le più nitide' e frasi inventate per la voce: non accettare senza prova/fonti o senza mantenere la registrazione vera.
- Non usare `human_approved` o `artistic_gold` dai rapporti: i modelli **non hanno visionato** il video in tempo reale.

## Decisione di integrazione

**APPROVATO SOLO COME LABORATORIO PER PROPOSTE.** I risultati generativi passano prima da un **filtro di verità del master** (tempo, parola esatta, asset, provenienza, licenza, no-flash) e poi dai gate di qualità editoriale V320/V322/V326 e QA umano. Nessuna autonoma modifica ai video approvati e nessuna produzione automatica su questo esperimento.

**Prossima prova utile:** applicare UNA delle tre modifiche in un provino A/B solo quando esiste un progetto di montaggio e sono disponibili gli stessi asset/licenze; preservare la voce Gacrux e master attuale come controllo, confrontando il vero MP4 a velocità normale. Prima di usare nuovi modelli controllare il prezzo live e i limiti dell'account; non introdurre cron, prompt segreti o spese non verificate.
