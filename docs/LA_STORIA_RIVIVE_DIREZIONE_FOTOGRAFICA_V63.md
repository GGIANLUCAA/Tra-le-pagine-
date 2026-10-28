# La Storia Rivive V63 — Regia delle scene e fotografie AI percepite nitide
28/10/2026. Feedback sul reale V62: 18,2 s troppo corto; ritmo regia troppo uniforme; fotografia AI ancora grana, sfocature e finte texture. Nessuna approvazione artistica per V62.

## Diagnosi verificata sul master e sul filmato reale
- Il filmato Beirut "Scènes de rue" è 720×576, circa 188 s, 30 fps. Per un video 9:16 che occupa tutto lo schermo, il ritaglio è ~324×576 pixel reali, quindi nessun modello può "ripescare" i tratti veri perduti. Elaborazione 1080×1920 o 4K NON equivale a fonte 4K.
- V62 colorizzava con DDColor, poi faceva un **downscale distruttivo** del ritaglio storico da ~324×576 a 240×427 **prima** di Real-ESRGAN, ingrandiva a 960×1708 e rendeva a 720×1280. Questo toglieva informazione iniziale e detailEnhance enfatizzava grana/contorni.
- Il vecchio piano selezionava alcuni totali/porti con persone molto lontane; una foto di persona minuscola non diventa magicamente un primo piano realistico.
- C'era un'etichetta nera sul video a ogni scena/foto: interrompeva la continuità e copriva soggetti.
- La sequenza uniforme 1,24 + 0,36 + 1,43 s per OGNI immagine trattava tutte come ugualmente importanti e spingeva troppo in fretta.

## Nuova strategia V63 per episodi migliori
1. **Studiare tutto il video originario**; preparare una timeline visuale da cui identificare almeno 8 scene candidate, confrontando più possibili ritagli 9:16. Selezionare in base a (a) viso o soggetto leggibile, (b) gesto/espressione, (c) storia narrabile, (d) geometria sicura per ritaglio verticale, (e) restauro realistico, (f) variazione di soggetti. Evitare di utilizzare 6 momenti dello stesso evento solo perché disponibili. Se qualità < soglia, scegliere un altro **filmato CC0/PD più nitido**.
2. **Congelare il momento più espressivo**. Da questo preciso frame l'AI produce una NUOVA FOTO colorata. Evitare cornici e black box che nascondono dettagli; titolo breve solo all'inizio, descrizioni autentiche nel dossier.
3. **Variabilità narrativa dei tempi**: circa 1,2–1,6 s film B/N in movimento; rapida transizione 0,3–0,4 s; fotografia AI **1,8–2,8 s** se significativo. Il video dovrebbe tipicamente arrivare a **20–28 s**, ma durata sempre giustificata.
4. **Non degradare pixel prima della super-risoluzione**. Partire sempre dal ritaglio storico originale (qui 324×576), leggera riduzione rumore, DDColor, SR x4 direttamente sul ritaglio, riduzione a 1080×1920, colore meno aggressivo, evitare detailEnhance che amplifica artefatti. Un export 1080p **non è 4K**.
5. **Quando serve il salto di qualità fotografica dei riferimenti:** aggiungere il percorso opzionale `real_photo_diffusion` su un keyframe usando un modello image-to-image (DiffBIR o SUPIR) con controllo di fedeltà, persone/vestiti/luoghi/geometria. Richiede GPU e verifiche termini e budget; **non è integrato/attivo**, zero API a pagamento predefinite. Real-ESRGAN migliora dettagli in modo più conservativo ma NON può restituire tutta la naturalezza di una fotografia generativa high-quality.
6. **Gate visivo obbligatorio prima della consegna**: confrontare IN PARALLELO ogni frame originale e la sua fotografia restaurata (volto, mani, corpo, vestiti, bordi, rumore, colori, oggetti e continuità); scartare ritratti plastici, arancione rosa uniforme, volti inventati, case ristrutturate, vignette e paesaggi fuori fonte. Differenziare fallimenti tecnici ed estetici. Copertina e 4 copy V55 originali.
7. **Prossimi output**: `src/storia_rivive_director_cut_v63.py`, `config/storia_rivive_v63.json`, `queue/storia_rivive_beirut_v63_selected_scenes.json`. Video V63 **preview a verifica artistica**, non master approvato né video pubblicato sui social. Link GitHub Release diretto dopo render riuscito + prova QA, per evitare "Library file not found". Site sync separato e verificato.

## Research e limiti attuali
- Real-ESRGAN ufficiale https://github.com/xinntao/Real-ESRGAN include modello generale con controlli di denoise; qualità dipende soprattutto dalla sorgente.
- SUPIR https://github.com/Fanghua-Yu/SUPIR è orientato alla ricostruzione fotografica via modello generativo; richiede GPU e RAM sostanziali, modello/code license da verificare rispetto al post non monetizzato.
- DiffBIR https://github.com/XPixelGroup/DiffBIR supporta super-risoluzione generativa e alcune modalità CPU/MPS, ma diffusion pesante e non disponibile sul runner CPU veloce di questa pipeline.
- Non indicare mai foto ricostruita come documento originale a colori: mostrare sempre fonte, licenza della pellicola e disclosure di colori/dettagli inventati.

## Scelta direttoriale iniziale Beirut V63
Dai 188 secondi ho selezionato 6 azioni differenti in ordine drammaturgico (non in ordine cronologico): carovana (hook), volti e bambini (emozione), merci mercato (vita quotidiana), uomini al caffè (socialità), lavoratori porto (respiro spaziale), folla in piazza (chiusura). Durata approssimativa **24,5 secondi**. Tempo maggiorato alle foto con persone leggibili; minore al porto. I file di elenco e i timecode sono documentati in `queue/storia_rivive_beirut_v63_selected_scenes.json`, da confermare con ispezione finale.

Questa revisione corregge REGIA e RESTAURO con gli strumenti CPU realmente disponibili. Non garantisce effetto indistinguibile da foto moderna; per quello testare image-to-image generativo con compute autorizzato e identità verificata. Mai consumare Vidu senza consenso.
