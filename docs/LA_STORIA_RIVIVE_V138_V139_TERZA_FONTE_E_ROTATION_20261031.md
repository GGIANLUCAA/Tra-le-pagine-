# La Storia Rivive — V138/V139, terza pellicola HD e rotazione non ripetitiva

**31 ottobre 2026 | Studio Restauro storico | sola ricerca**  
Collegamento: issue #144, mandato V108, PR draft #155 stacked sulla PR #153. Nessun intervento a ArtVision, WOW LAB o benchmark SF1906 V98.

## V138 — collaudo davvero eseguito su Versailles 1919

- Fonte: [*The signing of the peace treaty of Versailles (16 fps)*, Wikimedia Commons](https://commons.wikimedia.org/wiki/File:The_signing_of_the_peace_treaty_of_Versailles_(16_fps).webm), filmato del 1919 attribuito alla produzione del Department of Defense, catalogo NARA 24746.
- Il file **originale caricato** su Commons è WebM 1920×1080, durata **497,467 secondi**, 46.244.117 byte circa; il raster del file non prova che i dettagli siano scansione originale HD. La licenza dichiarata è pubblico dominio **negli Stati Uniti** con avvertenza sul possibile status diverso in altri Paesi: **diritti italiani non verificati**.
- [Actions run #41198999054](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41198999054) **SUCCESS come audit**, artifact `STORIA_V138_VERSAILLES_SOURCE_AUDIT_41198999054` ([scarica evidenza](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41198999054/artifacts/13041388609)). Ho scaricato e letto dal contenuto ZIP report V138, scout V101 e movimento V125.
- SHA-256 del film realmente acquisito: `a29801c567fa7f237fed71a686b853a5c37e1323aed7a53c5a73265b975dadf8`.
- FFprobe conferma il raster originale 1920×1080; cache V134 conferma byte di film e dei PNG e provenienza della pagina Commons.
- Lo scout ha individuato **9** possibili tagli/intervalli lunghi, il V124 ha campionato **9 PNG fotografici autentici** con PTS SHA-bound; **solo 1/9 finestre** ha superato il gate V125 di movimento spaziale originale. Il V126 ha restituito `V126_INSUFFICIENT_MOTION_SCENE_VARIETY` con **zero** candidati per una cinquina 4+1. V128/V129 non hanno certificato una cinquina.
- Status finale `SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY`. Il successo Actions dimostra che **il controllo ha funzionato e ha rifiutato la fonte**; non equivale a video riuscito o a diritti certificati.

**Limite interpretativo:** la bocciatura riguarda la digitalizzazione e il campionamento attuali con le soglie di movimento vigenti, non dimostra che ogni fotogramma del girato del 1919 sia statico o che una scansione alternativa più nitida non sia mai utilizzabile. Le fonti originali si rivalutano solo attraverso un nuovo materiale con provenienza verificabile.

## V139 — evitare cicli inutili sulle tre pellicole respinte

Il registro di ricerca `config/storia_rivive_v133_rejected_films.json` è esteso da una a **tre** voci:
1. `france_cotton_mill_1920`, SHA `e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9`, rifiuto storico V132 dopo veti visivi.
2. `white_house_1917_1921`, SHA `db829527e66425bafdcfa9f3e6fc2d0bd17ffc13a43f62d56175e9bef1ac94a9`, [audit vero V136](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41192692081): 1 sola finestra con movimento.
3. `versailles_treaty_1919`, SHA `a29801c567fa7f237fed71a686b853a5c37e1323aed7a53c5a73265b975dadf8`, [audit V138](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41198999054): 1 sola finestra con movimento.

Il selettore `src/storia_rivive_autopilot_v101.py` accetta come motivazioni soltanto gli status **documentati** `SOURCE_REJECTED_V132_INSUFFICIENT_DIVERSITY_AFTER_VETO` e `SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY`. Ogni voce richiede identificativo candidato, pagina originale identica a quella nella coda, SHA ben formato e URL di prova GitHub Actions. La rotazione ogni tre ore non sceglie più questi tre vecchi file; **non** riattiva I2I/Vidu e non altera cron o altre automazioni.

I vecchi filmati a 480p/576p rimangono nella coda per studio, ma vengono fermati dal controllo della risoluzione nativa V121 prima di ogni download pesante. Il confronto della pagina non rileva automaticamente un eventuale nuovo caricamento alla stessa URL: serve sempre revisione del catalogo quando si scopre una digitalizzazione differente.

Test:
- `tests/test_storia_rivive_v138_workflow.py`: source binding, no diritti fittizi, strumenti gratuiti e solo artifact JSON/contatti.
- `tests/test_storia_rivive_v139_rejection_rotation.py`: 24 finestre da 3 ore senza ripescare le tre fonti, registro falso o stale, nessuna sorgente rimasta, no pagamento.
- V101 vecchi test V133 su una sola sorgente mantengono la loro fixture scoped; il test V139 esegue invece il registro **completo** con la coda reale.
- Workflow V109 include entrambe le nuove suite. Il risultato PASS è da confermare con la GitHub CI sul commit attuale; non attribuirlo a un run precedente.

## Cosa manca per produrre un vero primo pilota

Una **quarta fonte di qualità documentata** che passi 5 riprese genuinamente differenti, 5 finestre di movimento, dettagli fotografici confrontabili con SF1906 V98 e verifica di riuso per l'Italia. Poi **quattro vere I2I** e **una vera clip Vidu** dallo stesso frame originale (rispettando budget, autorizzazione per scena e consumo prepagato verificato), montaggio 14–35 s, voce/musica/titoli appropriati, MP4/ZIP Android realmente scaricabili e QA V91/V94/V96/V99 con revisione artistica. Rimangono **zero nuovi pilot 4+1 completi, zero crediti e zero pubblicazioni** per queste modifiche.

La PR #155 resta **draft** e non è unita a main; richiede revisione prima dell'integrazione.
