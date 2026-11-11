# V4 — Regia WOW: traccia, colore, luce (esperimento non distruttivo)

Revisione: 26 ottobre 2026. Ambito: idea tecnica e prove isolate della PR #51. **Non** è una nuova regola permanente e **non** sostituisce V3, V12, Cinema V6, voce Gacrux, master o Video Library.

## Cosa abbiamo dimostrato in laboratorio

Demo locale di 27 secondi, 3 inquadrature originali collegate in forma narrativa: (0–7 s) città notturna, la protagonista già visibile, traccia dell'orologio e ultima stella; (7–16 s) mappa, serratura e chiave che prende forma; (16–27 s) linee delle costellazioni, stelle che si colorano e luce conclusiva. Video verticale H.264 540×960 / 24 fps, AAC con musica originale sintetizzata localmente; nessuna voce Gacrux. Durata e punti di ingresso sono decisioni editoriali di prova, **non** timing di parola misurato. Stato: technical_demo_needs_artistic_review.

## Cosa abbiamo riusato dagli open source

- CairoSVG ([Kozea/CairoSVG](https://github.com/Kozea/CairoSVG), LGPLv3) rasterizza gruppi SVG separati; evita confusione tra oggetti in contatto.
- OpenCV (Apache 2.0), NumPy, Pillow e FFmpeg compongono gratuitamente contorni, maschere locali, bagliori e MP4.
- [VTracer 1](https://github.com/visioncortex/vtracer) MIT è un'opzione FUTURA per convertire JPG/PNG in SVG; non è indispensabile né installato. VTracer 2 ha condizioni diverse.
- [svgpathtools](https://github.com/mathandy/svgpathtools) MIT è opzionale per tracciati Bezier; nessuna dipendenza obbligatoria aggiunta.

## Criteri di regia per il formato Libri

1. La scena deve essere leggibile al primo istante quando la frase richiede comprensione immediata.
2. Disegnare solo un oggetto narrativamente essenziale: soggetto e posizione devono essere identificati in anticipo, non indovinati dai colori.
3. Allineare inizio e durata del disegno alla frase pronunciata tramite AUDIO REALE e cue rivisti; senza WAV non dichiarare sincronizzazione.
4. Prima contorno, poi colore solo quando aiuta la rivelazione; lasciare il contenuto completo visibile per un tempo congruo; non forzare 3 secondi per tutto.
5. Raccordi tra scene con tagli puliti; vietato sovrapporre quadri. Niente movimenti ripetitivi, volti tagliati o strappi di velocità.
6. Se la segmentazione non è affidabile, usare V3 o un'inquadratura pulita, mai un effetto rotto; salvare sempre immagine, mastering e fonte intatti.
7. La scelta dei passaggi è una decisione registica per quel racconto, non un preset globale. Nessuna modifica al ramo main in questa PR.

## Convalide e limiti

Laboratorio locale: cinque nuovi test V4 riusciti; compatibilità con 16 test V1–V3 (totale 21). V4 richiede illustrazioni con livelli SVG preparati o maschere manuali: non promette effetto identico con ogni fotografia o MP4. AI API = 0, costi di CPU e minuti workflow non necessariamente nulli. Il codice sorgente e le immagini di prova sono stati consegnati separatamente come pacchetto ZIP; questo documento DA SOLO non installa un motore di produzione nel sito o sul ramo principale.

**Passaggio successivo:** riprodurre una singola scena reale usando asset approvati, cue del narratore Gacrux e hash; confrontare con lo stesso video privo di effetto. Non promuovere a gold master senza revisione artistica.
