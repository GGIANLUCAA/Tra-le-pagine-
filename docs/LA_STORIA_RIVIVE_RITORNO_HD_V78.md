# LA STORIA RIVIVE — V78 · Recupero HD senza perdere la fedeltà
**29 ottobre 2026 — richiesta utente:** «Con l'ultima correzione siamo tornati al livello indietro di restauro; le immagini non sono più in HD, nelle facce non sono ricostruite bene. Andava meglio prima».

## Decisione vincolante
La V77 ha peggiorato la qualità fotografica: il compositing V77 usava 78% della LUMINANZA del frame B/N originale **su tutta la fotografia**, e fino al 93–98% in zone sospette. Risultato: la geometria era conservata ma i visi, i capelli, gli abiti e la texture sono tornati sgranati.

**V78 corregge questo errore.** Per default preservare al 100% il dettaglio generativo fotorealistico dei soggetti V76 riusciti. NON applicare una fusione globale della luminanza con il fotogramma originale. Limitare qualunque recupero di forme originali soltanto a REGIONI ESPLICITE dove l'AI ha inventato o trasformato un oggetto (scala→persona, pezzo d'auto→volto, uomo→oggetto, ruote e ringhiere deformate). Proteggere con maschere morbide e misure locali, lasciando visi/capelli/abiti in alta definizione. Se non esiste un'evidenza di errore, non degradare l'immagine.

## Produzione corretta
1. Film d'epoca autentico in movimento B/N. Fermare il fotogramma corrispondente esatto.
2. Fotografia realmente rigenerata dalla scena originale, visivamente HD, carnagione naturale e capelli/occhi/vestiti credibili. Le texture hallucinate non devono essere trattate come prova storica.
3. Confronto in parallelo tra frame originale, fotografia generativa candidata **ad alta qualità**, immagini adiacenti in movimento e modifiche locali.
4. Identificare manualmente oppure con un sistema di segmentazione da validare tutte le regioni in cui si sospetta una conversione di identità. Marcare bounding box e proteggerle localmente; misurare che la nitidezza dei soggetti principali sia preservata.
5. Se il rischio è un volto/oggetto in primo piano, NON tentare di «correggere» mascherando tutto il volto con il frame sgranato: rigenerare SOLO quel soggetto con controllo d'immagine, riferimento dei frame vicini o selezionare altra inquadratura. Nessuna spesa API senza consenso.
6. I controlli strutturali (correlazione, Canny, varianza Laplaciana) NON classificano persone/scale né certificano fedeltà semantica. I candidati richiedono revisione artistica e semantica.
7. Se una parte resta ambigua e non può essere corretta conservando la qualità, lasciare il video in stato **PREVIEW / FAILED_SEMANTIC_REVIEW**. Non autopubblicare.
8. Non sostituire il formato approvato: *vera pellicola in moto → freeze → foto AI nitida e ferma → nuova vera scena*, titolo luogo/anno elegante, 20–26s variabili, musica originale, MP4+ZIP scaricabili e GitHub diretto.

## Parametri prova V78 (Parigi 1896–1900)
- **Tre foto della V76 già generate**, non tre nuove foto AI. Per ogni immagine la cromia della V76 è preservata; si fonde solo il canale L di Lab nelle zone meccaniche scelte.
- Zone modificate sopra il 20% del peso fonte: **~6,6%, 10,5%, 3,7%** rispettivamente, non l'intera fotografia.
- Qualità dettagli chiave: variazione della texture Laplaciana entro il 10% dell'originale V76 sui soggetti principali. Il dettaglio percepito resta alto.
- 20,47s, H264 720×1280 e AAC, tre trasformazioni, banda sonora originale. Non presentare 720×1280 come vera risoluzione 4K o come autentica ricostruzione dei lineamenti ignoti.
- **File master V76 preservato**. V77 conservato come esempio di regressione da evitare. V78 PREVIEW in attesa di verifica semantica umana.
- Codice: `src/storia_v78_hd_selective_identity.py`, workflow `.github/workflows/storia-v78-hd-identity.yml`. Prove della forma/fedeltà non sono certificazione di classe, così come 99% di correlazione globale non provava che non fossero nate persone inesistenti.

## Impostazioni che NON devono restare in vigore dalla V77
- ABOLIRE `base_source_weight=0.78` come default generale per video nuovi; evitare anche `source_weight=0.93–0.98` applicato automaticamente a tutte le tiles segnalate senza visione.
- ABOLIRE il limite rigido di denoise 0.27 come regola universale: la forza di ricostruzione va adattata alla qualità e alle maschere di controllo, valutando sempre fedeltà e foto.
- **Non ripetere la risposta errata «meglio meno bello purché conservativo»**: l'utente vuole **entrambe** qualità HD + identità corretta. Se non si riescono ad avere entrambe, rendere visibile il limite e bloccare la consegna definitiva.

## Problema residuo
V78 riduce il rischio nei piccoli elementi selezionati senza indebolire le facce; NON è una verifica esaustiva di ogni persona o oggetto. Per la produzione seriale servirà inventario manuale/segmentazione e controllo frame adiacenti, poi eventuale patch mirata.
