# LA STORIA RIVIVE — V77: BLOCCO DELLE SOSTITUZIONI DI IDENTITÀ

**Data:** 29 ottobre 2026. **Priorità assoluta di qualità:** l'utente ha individuato trasformazioni inaccettabili: pezzi d'auto, scale, carrozze o altri oggetti diventano persone, e talvolta persone diventano oggetti. Questo difetto prevale su risoluzione, colorizzazione, effetto WOW e velocità di produzione.

## Regola inviolabile: STESSA SCENA, STESSI OGGETTI, STESSE PERSONE
Il video storico in movimento, il suo fermo fotogramma e la fotografia AI devono rappresentare **esattamente gli stessi soggetti, nelle stesse posizioni e con lo stesso numero di persone/animali/veicoli**. Un oggetto può essere ripulito o reso nitido, mai trasformato in un altro. È vietato aggiungere visi, braccia, gambe, figure, animali, ruote, scale, balaustre, auto o qualsiasi altro oggetto assente dalla fonte verificabile. Mai «completare» automaticamente figure umane nascoste da un palo o una ruota.

### Flusso di lavoro V77 obbligatorio
1. Prima di qualsiasi chiamata generativa, esaminare il frame autentico e 3–5 frame vicini della pellicola. Compilare **inventario verificato** di persone/animali/veicoli, oggetti rigidi (scale, pali, ringhiere, ruote, carrozze, architetture), posizioni e zone non interpretabili; nessuna categoria dedotta arbitrariamente da un singolo punto sfocato.
2. Definire eventuali **maschere di protezione** per elementi riconosciuti o ambigui. I volti piccoli, i raggi delle ruote, le scale, i pali e le ringhiere sono ad alto rischio. Le parti non verificabili non vanno trasformate in persone. Se davvero incerto, conservare una zona più vicina alla fonte e segnalarla.
3. **Rendere la generazione conservativa:** il vecchio prototipo V71 usava `denoise_strength=0.53`, troppo permissivo per forme ambigue. Nuovo punto di partenza `0.22` e limite `0.27`; `controlnet_scale` circa `1.30` e `condition_scale` circa `5`, con attenzione ai limiti della Space. Il prompt deve nominare gli oggetti realmente verificati e vietare conversioni persone↔oggetti. Nessun retry automatico su risorse gratuite o a crediti: una chiamata per candidato, QA, poi eventuale decisione esplicita.
4. Salvare candidato grezzo + frame originale + immagine sorgente-conservativa. Applicare **source-luminance lock**: il chiaroscuro originale guida sagome e geometria; il colore AI non deve riscrivere la forma di volti e veicoli. Per zone sospette/protette rafforzare il peso dell'originale fino a circa 93–98% della luminanza. La soluzione può risultare meno dettagliata, ma non deve introdurre nuovi personaggi.
5. **Controllo per zone, non media globale:** il precedente controllo V71 di correlazione globale consentiva false approvazioni. La V77 suddivide la scena in una griglia (es. 6×10), confronta bordi e struttura e segnala anomalie; produce tavola prima/candidato/foto conservativa e report. Una somiglianza globale anche del 99% NON prova che una scala o ruota sia rimasta tale.
6. **Verifica visiva obbligatoria degli oggetti:** contare persone, animali e veicoli; guardare mani, volti, vestiti, ruote, scale, ringhiere, spigoli e prospettive. Confrontare il frame fotografico anche con i fotogrammi vicini del film. I filtri automatici non sanno garantire la categoria semantica «uomo» vs «scala». Senza tale controllo, stato `PENDING_HUMAN_SEMANTIC_REVIEW` e **nessuna pubblicazione, né dichiarazione di video definitivo**.
7. Se un candidato sbaglia un oggetto: **scartare o correggere localmente** ripristinando la fonte/una colorizzazione non generativa; non nascondere l'errore con musica, tagli o flash. Se la scena non è restaurabile in modo fedele, sostituirla con una scena diversa. Nessun aumento gratuito di FPS o 4K come rimedio.

### Cosa rimane invariato
Gold format V74–V76: pellicola **vera** in B/N in movimento → fermo sul medesimo fotogramma → fotografia AI fotorealistica a colori, **ferma** → altra vera scena. Titolo iniziale luogo/annata, ~20–26 s quando giustificati; audio originale, ZIP e MP4 scaricabili, preferenza backup GitHub Release. È approvata la regia, non qualsiasi ricostruzione generativa.

### Prova effettiva su Parigi V76
Abbiamo confrontato `ORIGINAL_02.png` e `FOTO_AI_02.png` del marciapiede mobile: correlazione globale circa **0,996**, eppure il nuovo controllo V77 marca **17 regioni su 60** per ispezione. Queste regioni sono soltanto segnali di possibile modifica strutturale, NON una diagnosi certa di persone inventate. Abbiamo creato tre foto alternative con luminosità/forme maggiormente vincolate all'originale e una prova MP4 di 20,47 s. Il materiale è *un confronto tecnico non approvato*, non nuova produzione storica né prova definitiva di correttezza. Non sovrascrivere V76 né pubblicare la prova automaticamente.

### Requisiti operativi
* Codice: `src/storia_rivive_v77_identity_guard.py`, `src/storia_rivive_v77_safe_photo_generator.py`
* Parametri: `config/storia_rivive_identity_lock_v77.json`
* Output: sorgente, inventario oggetti, candidato AI, maschere, foto conservativa, report QA, checklist verificata; file hash SHA256.
* Diritti e fonti sempre verificati; nessuna spesa API/Vidu senza consenso; niente claim «soggetto identico verificato» da un algoritmo basato su pixel.

**Regola decisionale:** è preferibile una fotografia leggermente meno spettacolare ma fedele, rispetto a una fotografia apparentemente perfetta che inventa persone o cambia la storia.