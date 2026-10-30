# ArtVision V82 — Critico breve, ritmo cinematografico e immagine-parola (30/10/2026)

**Regola editoriale globale per i nuovi Critico Standard e Critico Museum.** Nasce dal giudizio dell'utente sui due Critico John Martin V81: **troppo lunghi (144,8 secondi), riprese generiche/mal pensate e narrazione visivamente noiosa**. Non modificare i Cinema già esistenti; non attribuire approvazione automatica ai nuovi output.

## La durata si guadagna, non è automatica
- Per un Critico social ricercare **circa 75–105 secondi** e in via orientativa **160–220 parole**, senza imporre a tutti un cronometro fisso. Se l'opera richiede davvero più respiro, motivare ogni ulteriore scena nella scheda e ottenere una revisione artistica prima della pubblicazione.
- Apertura con dettaglio/azione visiva significativa nei primi **1–3 secondi**. Contesto biografico, data, titolo e museo vanno inseriti solo quando servono, non come una lunga introduzione libresca.
- Copione competente e concreto: una frase, una scoperta; evitare frasi enfatiche ripetute, spiegazioni teoriche non visibili, commenti personali e descrizioni di dettagli che non appaiono.

## Storyboard e montaggio SEMANTICO
- Scrivere il copione in **8–12 paragrafi/beat**; per ogni beat assegnare **coordinate/poligono realmente verificato sul dipinto**, inizio/fine, distanza/zoom e cosa lo spettatore deve riuscire a vedere. Un beat può comprendere più inquadrature se emergono *dettagli veramente diversi*.
- Preparare tipicamente **10–16 inquadrature reali** per un critico breve, non lo stesso ritaglio spostato come se fosse una scena nuova. Non cercare 20 finti dettagli quando l'opera ne offre solo 7; preferire qualità e differenza percepibile.
- Tempo d'osservazione indicativo: 3–5 s per volti o azioni semplici, 5–8 s per composizioni complesse, con variazioni motivate. Sostituire un'inquadratura soltanto quando l'occhio ha letto l'informazione oppure la narrazione cambia soggetto.
- Per ogni frase parlata su un personaggio/oggetto, **quel soggetto deve essere visibile e comprensibile esattamente in quel momento**. Non puntare il cielo quando la voce descrive persone e non tenere un panorama fermo durante la descrizione di un dettaglio.
- Montaggio Cinema Standard può usare tagli e leggere dissolvenze 0,2–0,45 s dove utili; **Critico Museum** deve invece mantenere la continuità della camera nel quadro; anche la sua traiettoria deve seguire gli stessi beat informativi.
- Limitare zoom inutili, oscillazioni, ingrandimenti eccessivi di fonti low-res, facce/oggetti tagliati, cornici decorative e transizioni meccaniche.

## V80 cornice e V46 scala
- Nei due Museum mostrare cornice originale/documentata e sala **solo nella breve apertura e nel ritorno finale**. Durante TUTTA la narrazione centrale soltanto superficie pittorica, niente cornice in campo. La cornice si allontana e riappare per il movimento reale della camera, **mai dissolvenza**, stessa cornice in ingresso/uscita.
- La scala reale dell'opera e l'origine documentata del frame restano obbligatorie. Se la cornice non è verificata, video in review non Gold Master.

## Voce, musica e prova reale
- Generare **una sola voce Google Gemini Gacrux** per entrambi i Critico, WAV identico e controllato tramite SHA256, musica sotto voce.
- Utilizzare timecode da ASR o da allineamento verificato ascoltando i paragrafi; i timecode stimati dalla lunghezza del testo o dai silenzi sono solo **pre-montaggio**, e richiedono controllo umano prima di dichiarare la sincronizzazione perfetta.
- QA obbligatorio a velocità normale: ascoltare l'intero video, misurare durata, apprezzabilità di ogni inquadratura, relazione immagine-parola, quadro autentico, audio comprensibile, inizio accattivante, finale e cornice. Se fallisce uno di questi punti, rifare solo il pezzo necessario e **non pubblicare/non approvare**.
- Consegna MP4 reali, cover, 4 testi social distinti per variante, ZIP integri, provenienza/licenze e stato review veritiero; sito privato verificato separatamente.

**Caso di prova:** `pilot/artvision-martin-critico-v82` contiene il copione corretto 211 parole e 9 beat con inquadrature motivate per *The Great Day of His Wrath*, isolato dai due Cinema V81. La sola esistenza di un MP4 e il passaggio dei test non significano apprezzamento artistico.


## V83 — correzione CAMERA MUSEUM dopo QA del video John Martin (30/10/2026)

La prima versione Critico Museum V82 aveva ancora una ripresa **troppo ingrandita e sfocata**, benché il test cornice fosse passato. Regola tecnica ulteriore: **passare la verifica delle cornici NON basta: l'interno del quadro deve restare leggibile e vario**.

- Inizio: mantenere la vera foto della cornice visibile e leggibile per circa 1–2 s; poi avanzare nel quadro (esempio pilota z=1→5,4 in 3,2 s).
- Una volta che il bordo è davvero fuori dall'inquadratura, usare i pixel del dipinto direttamente (non una fotografia di sala enormemente ingrandita). **Zoom moderati ~1,1–1,5× rispetto alla sezione pittorica verticale** a seconda di risoluzione e oggetto; niente proiezioni estreme z=19–23 della piccola immagine museale come contenuto di tutta la spiegazione.
- All'interno: percorsi continui ma con soggetti effettivamente distinguibili (persone, lampi, rocce, città, fuoco); predisporre prima la mappa immagine→frase, e mantenere una pausa breve per l'occhio.
- Finale: portare la camera al centro dell'opera e tornare alla vera fotografia incorniciata soltanto nell'ultima uscita prospettica, mai durante la spiegazione.
- **Gate visivo aggiuntivo:** contatto storyboard estratto dal MP4 reale ai secondi 0/2/4/8/18/35/41/52/61/72/83/90/91.5 e controllo a schermo Android. Se almeno 2 passaggi interni appaiono sostanzialmente uguali o irriconoscibili, NON approvare: rivedere focale/fonte prima di pubblicare.
- Per la versione John Martin V83 il codice locale ha riutilizzato *senza alcuna nuova chiamata vocale* la traccia AAC ESATTAMENTE identica del Critico Standard V82 (SHA256 verificato); il rendering dei due Cinema e dei due Critico precedenti rimane immutato. Video V83 ha sorgente arte 1000×640, dunque non è fedeltà 4K nativa e resta in review artistica.

Il rendering V83 locale costituisce una revisione controllata a posteriori del Museum; non sovrascrivere il codice/il video V82 senza conservare la versione precedente. **Questa correzione non autorizza a inventare la cornice né a ignorare V80.**
