# ArtVision V331 — QUADRO FRONTALE · DIVIETO DI PROSPETTIVE STORTE
**Direttiva proprietario 12 novembre 2026 · regola globale vincolante per ogni nuovo Museum, Critico e Cinema.**

## Cosa non va più consegnato come bello/approvato
La tela inclinata rispetto al muro, il rettangolo che appare un trapezio per una ripresa laterale non motivata, cornici pendenti, quadro fuori centro, composizione sbilanciata, prospettiva di parete che deforma l'opera, asse camera sbagliato e geometria incoerente fra ingresso e ritorno sono **difetti regia**, anche quando la fotografia è autentica. I video già in review con tali difetti restano **REVIEW / da correggere**, non Gold, anche se FFmpeg e hash passano. La disponibilità di una fotografia reale della sala non giustifica utilizzare qualsiasi angolo.

## Nuovo piano di regia obbligatorio
1. **Vista iniziale da davanti:** telecamera circa perpendicolare al piano della tela, asse ottico puntato sul centro effettivo del quadro, verticale e orizzontale della cornice ragionevolmente allineate ai bordi dello schermo. Il quadro **deve apparire come un rettangolo**, non un trapezio.
2. **Stessa impostazione nel ritorno:** la camera può esplorare i dettagli pittorici SOLO dopo un'inquadratura frontale corretta, e deve rientrare davanti al medesimo quadro dalla stessa direzione. Quando il dipinto è completamente visibile, il suo asse deve tornare centrato e dritto. Durante l'interno nessuna cornice.
3. **Cornice vera e proporzioni reali:** V80/V118/V119 prevalgono sempre. Le dimensioni del dipinto (cm) devono coincidere con il rapporto nella ripresa, evitando schiacciamenti, stiramenti o finte pareti 2D.
4. **Foto d'archivio laterale:** preferire fonte ufficiale o CC realmente frontale. Una foto di sala ripresa di sbieco può essere usata solo come documentazione/texture ausiliaria, non come inquadratura Museum principale. Una omografia di raddrizzamento della **sola superficie planare del dipinto** può recuperare il rettangolo e soltanto con QA di nitidezza/proporzioni, ma **non** trasforma la fotografia obliqua di una stanza in una vera fotografia frontale della stanza. Non allungare pareti, deformare cornici o fingere che una foto laterale sia stata ripresa frontalmente.
5. **Eccezioni rare e motivate dal quadro:** solo per una scelta di regia realmente collegata a un soggetto, allestimento o effetto ottico specifico (es. anamorfosi, voler mostrare consapevolmente profondità della cornice), non per aggiungere movimento fine a sé stesso. Registrare `artwork_specific_rationale`, provino MP4 visto a velocità normale e consenso artistico esplicito del proprietario. La prospettiva angolata non è mai il fallback per una fonte sbagliata.
6. **Se non c'è vista frontale credibile, fermare SOLO la variante Museum**, conservarne sorgenti e Standard, segnare `museum_status=needs_frontal_reference`, passare all'opera successiva. Non inventare una sala inesistente e non pubblicare.

## QA obbligatoria: due livelli, non basta il test geometrico
**A. Verifica strumentale:** nel MP4 reale estrarre almeno due PNG ad alta risoluzione quando l'intero dipinto è visibile: `entry_frontal` e `exit_frontal`. Segnare manualmente i quattro angoli **interni della superficie dipinta** (TL,TR,BR,BL) e verificare i file SHA. Eseguire `python src/artvision_museum_frontal_gate_v331.py dossier.json --output result.json`. I limiti conservativi iniziali (modificabili solo con motivazione):
- inclinazione bordo superiore/inferiore rispetto all'orizzontale <= 1,75°;
- spostamento laterale dei bordi verticali rispetto alla verticale <= 2,75°;
- differenza fra lati contrapposti <= 4,5%;
- errore relativo rapporto dipinto immagine rispetto ai cm <= 4,5%;
- centro orizzontale entro 6,5% della larghezza totale.

L'assenza dei quattro angoli o di due PNG autentici è un **FAIL**, non una promozione. Per una variante in formato verticale, le parti fuori campo durante il viaggio della camera non si prestano a questo test: gli scatti devono essere scelti quando il dipinto è interamente riconoscibile. L'identità della foto/video deve essere verificata con hash, senza inventare corner automatici.

**B. Revisione artistica reale:** guardare ingresso, centrare l'intera opera, transizione, dettagli, ritorno e uscita **a velocità normale** su telefono. Valutare se la prospettiva della parete sia credibile; bordi del quadro rettilinei e paralleli, quadro centrato, luce e ombre, scala reale, assenza salti. Se l'immagine appare ancora storta **bocciare anche con QA numerica PASS**. Non dichiarare Gold senza approvazione umana.

## Impatto su lavori esistenti e automazioni
La regola si applica a tutte le automazioni e renderer che producono Museum. Non modificare e non sovrascrivere i master Standard già apprezzati, né creare revisioni inutili di video completi. I precedenti Museum generati da una fotografia obliqua devono essere riesaminati come `needs_perspective_review`; se non c'è soluzione autentica, non produrre la versione Museo. Nessun costo API, TTS, Vidu o pubblicazione richiesti per attivare questa regola. L'uso di una camera angolata come scelta espressiva NON si considera scorciatoia approvata automaticamente.

**Nota tecnica onesta:** il gate V331 verifica angoli forniti da un operatore, su pochi fotogrammi; non rileva autonomamente il soggetto nel video, non prova la continuità degli altri frame, non misura la vera profondità fisica del locale e NON sostituisce il controllo visivo.
