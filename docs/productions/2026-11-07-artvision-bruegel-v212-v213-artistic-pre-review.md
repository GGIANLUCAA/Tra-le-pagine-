# ArtVision · Revisione artistica autonoma preliminare — Bruegel V212/V213

Data: 2026-11-07. Fonte: veri file MP4 prodotti e recuperati nella sessione, non report teorici. Metodologia: lettura metadata e controllo visivo di una griglia di fotogrammi a 0–47 s per Cinema V212 e 0–115 s per Critico V213; verifica addizionale di 34 istanti di V213 (16–115 s). **Non è una proiezione integrale a velocità naturale**, né l'approvazione artistica umana/owner, né una verifica Android dei link. Non sostituisce i gate finali V80/V118/V119 e territorial rights.

## Cinema Museum V212 — ESITO PRELIMINARE: PASS VISIVO CAMPIONATO, NON GOLD
- Opera autentica e vera fotografia della stanza con quadro incorniciato; parete, pavimento, scala dell'opera e cornice visivamente credibili all'inizio/fine.
- Campioni esaminati: 0,2,5,8,11,17,23,30,36,40,44,47 secondi.
- La camera procede dall'ambiente reale al piano pittorico; durante i dettagli la cornice non resta visibile. Ritorna nella medesima sala.
- I dettagli appaiono nitidi e senza tagli palesi nei campioni. La verifica software V212 di continuità è PASS (max mean-adjacent jump 23.194; 253 inlier per registrazione geometrica), ma da sola non dimostra fluidità artistica a tempo reale.
- Miglioria lieve: titolo iniziale poco leggibile a dimensione smartphone; controllare resa a pieno schermo e possibili riflessi/artefatti lungo il bordo durante la transizione.
- **Esito**: promosso alla *revisione integrale full-speed*; non ancora artisticamente approvato per la coda e non pubblicabile automaticamente.

## Critico Museum V213 — ESITO PRELIMINARE: REJECT / CORREZIONE REGIA PRIMA DELL'APPROVAZIONE
- Audio originale Gacrux conservato bit-identico, durata 115.8 s, 9 capitoli e 18 frasi V144; fonti e cornice autentiche.
- **Difetto verificato A (significativo)**: capitolo `La vera opera`, voce ~16.26–29.06 s, richiede la visione **dell'intero dipinto**. Campioni a 16,18,22,26,28 s mostrano una porzione centrale, senza quadro completo. Non rispetta la nuova regola shot–narration.
- **Difetto verificato B (significativo)**: capitolo finale ~98.04–109.4 s richiede l'intero dipinto; campioni a 99,103,107,109 s restano su un campo centrale parziale. Il rientro alla cornice avviene più tardi, attorno a 112–115 s, a voce ormai terminata.
- Gli altri passaggi campionati mostrano allineamento più plausibile: 34–38 s Michele, 40–46 s area superiore, 52–60 s creature ibride, 65–74 s fauci, 79–85 s creatura alata. Controllare comunque ogni frase e soggetto in playback normale, senza attribuire automaticamente PASS.
- **Correzione minima V214**: mantenere esattamente l'AAC/WAV Standard, l'immagine autentica, la fotografia Room68, la scala fisica e i movimenti dei capitoli riusciti; ricalibrare solo traiettoria dei capitoli 1 e 8 per ottenere un'inquadratura leggibile dell'intero quadro nei periodi indicati. Evitare scatti di camera nelle transizioni con easing aggiustato. Correre QA continuo e ricontrollare il video completo. Non contare la revisione come slot nuovo prima dell'approvazione finale.

## Stato e politica di autonomia
- Il sistema può **eseguire autonomamente controllo artistico preliminare, respingere clip con difetti, correggere e ripresentare i provini** senza richiedere OK per ogni iterazione, nel perimetro degli asset/licenze/spese consentiti.
- Una valutazione AI di fotogrammi **non equivale a certificare una visione umana integrale**. Per Gold o pubblicazione occorre la separata approvazione owner prevista dal progetto. Non cambiare `museum_approved`, `slots_delivered_this_selection` o `Gold_V25` sulla sola base di questa analisi.
- MP4 nuovi già verificati e archiviati: V212 SHA256 `14a75721e28183745b5d4bd93d048d89d3dbd7bbb9d5c55a7ef2d1e98045795d`; V213 SHA256 `05c1e0a15f7207a881b625230047e934e4e4261693189fc6b96c3aa240e6e23c`. Coda resta 26/40, entrambi test tecnici PASS ma nessun nuovo slot finale approvato.
