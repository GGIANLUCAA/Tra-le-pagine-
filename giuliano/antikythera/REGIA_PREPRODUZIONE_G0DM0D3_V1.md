# GIULIANO 03 — THE ANCIENT COMPUTER
## Dossier di pre-regia V1 — 12 novembre 2026

**Stato:** PREPRODUZIONE. NON un MP4 finito. Nessuna chiamata a pagamento, nessuna pubblicazione.

### Durata e impostazione
- Target 135–145 s, ~2:20, narrato in italiano naturale, titolo internazionale THE ANCIENT COMPUTER.
- Prima acquisire fonti visive autentiche con diritti/attribuzioni verificati; solo dopo chiudere testo, montaggio e tempi.
- Estetica: documentario televisivo sobrio; una ripresa vera di ingranaggi in moto vale più di cinque fotografie animate. No zoom automatici ripetuti, no effetto slideshow, no domande/chiuse stereotipate AI.
- Voce = immagini: ogni frase e sottoproposizione deve avere corrispondenza concreta; eventuale ricostruzione chiaramente etichettata. Non spacciare riprese moderne subacquee per quelle della scoperta del 1901.
- Zero microflash: rilevamento fotogramma per fotogramma sul MP4 finale, doppi tagli sotto 0,5 s bloccanti, preferire foto almeno 2,5–3 s quando statiche. Attenzione speciale ai bordi degli overlay.
- QA: ascolto completo e visione completa, verifica delle fonti, diritti, qualità audio, MP4 integrale Android e Full HD, ZIP e copertina. Il QA automatico non sostituisce revisione artistica.

### Scaletta indicativa (soggetta a fonti e registrazione)
| Sec | Cosa racconta la voce | Cosa si deve VEDERE | Divieto |
| --- | --- | --- | --- |
| 0–13 | Un relitto greco e il recupero del 1901 | Reperti autentici / mare e relitto documentati | Finta ricostruzione della scoperta presentata come vera |
| 13–33 | Il bronzo corroso sembra un oggetto qualsiasi | Frammenti originali del meccanismo, museo di Atene | Replica moderna senza etichetta |
| 33–55 | Dentro si trovano ruote dentate e iscrizioni | Macro, radiografie/CT pubblicabili, disegni accademici | Ingranaggi generici di orologio |
| 55–83 | Un sistema per rappresentare i cicli del cielo | Vera replica funzionante, rotazione documentata, spiegazione del quadrante | Animazione senza legame con la frase |
| 83–108 | Eclissi e calendario: a cosa serviva | Replica del quadrante e ciclo astronomico coerente | Riprese spaziali di riempimento |
| 108–132 | Come lo studiamo oggi e che cosa ancora non sappiamo | Analisi dei ricercatori, ricostruzioni identificate | Affermazioni certe su autore/finalità non dimostrate |
| 132–140 | Chiudere su un particolare osservabile dell'oggetto | Dettaglio finale del meccanismo, tenuta naturale | Domanda filosofica generica |

### Fonti da cercare e verificare PRIMA del render
1. National Archaeological Museum Athens / Hellenic Ministry of Culture: foto e schede ufficiali dei frammenti.
2. Antikythera Mechanism Research Project: scansioni, radiografie, documenti e crediti.
3. University College London e studi peer-reviewed: ricostruzioni scientifiche; distinguere ipotesi da elementi attestati.
4. Riprese di una replica realmente funzionante da università/musei/ricercatori con permesso di riutilizzo verificato.
5. Filmati subacquei di spedizioni moderne sul relitto, esplicitamente etichettati come contemporanei.

### Uso concreto dell'integrazione G0DM0D3
Nel repo esiste già `src/ai_director_v1.py` e `src/ai_director_bridge_v1.py`, documentati in `docs/AI_DIRECTOR_V1_INTEGRAZIONE_20261112.md`.
Non usare la modalità multi-API originale G0DM0D3 né chiamare modelli a pagamento. Usare AI Director **offline** come regista + critico scettico per:
1. Proporre due scalette diverse a partire da fonti verificate.
2. Contestare ogni scelta generica, taglio inutile, ripetizione di immagini e scena non supportata.
3. Auditare il manifest con `--mode audit` e poi il **vero** MP4 con `src/ai_director_visual_qa_v1.py`.
4. Tenere separate le decisioni creative dalle prove oggettive. Se un rapporto non ha letto il video, non dichiarare che lo ha verificato.
5. Solo dopo una vera prova A/B misurabile valutare se aggiungere confronti fra modelli `:free` verificati e autorizzati, mantenendo il gate default-deny e nessun costo.

### Decisioni ancora aperte
- Disponibilità/licenza di clip reali e scansioni.
- Durata effettiva dopo prova voce.
- Approvazione artistica del master.
