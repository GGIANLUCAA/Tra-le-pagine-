# V64 — FOTO AI DAVVERO FOTOGRAFICHE: riferimento 43054 / 43055, non solo super-risoluzione
Data: 28 ottobre 2026. Decisione dopo confronto reale di nuovi 43054.mp4 e 43055.mp4 con V63.

## Conclusione osservata e corretta
Entrambi i video esempio sono 720×1280 a 30fps: la qualità apparente non equivale alla risoluzione digitale 4K. Nei fermi a colori cambiano dettagli ad alta frequenza, materiali, pelle, volti, edifici; possono cambiare anche particolari dei soggetti. La trasformazione è **compatibile con** una ricostruzione generativa image-to-image, ma non è possibile dedurre lo specifico modello da questi MP4. La maggiore nitidezza NON è la prova che siano stati recuperati dettagli reali mancanti nella pellicola.

Il V63 NON supera il target: DDColor colorizza semanticamente e Real-ESRGAN aumenta il dettaglio tramite rete neurale, ma la foto finale resta troppo morbida/polverosa rispetto ai riferimenti. NON promuovere futuri video al livello riferimento senza un vero candidato **image-to-image generativo** correttamente valutato.

## Motori da confrontare sullo STESSO fotogramma
1. **HYPIR** https://github.com/XPixelGroup/HYPIR — primo candidato operativo, modello di restauro ad alta fedeltà percettiva derivato da priors diffusivi con singola passata; autore documenta **Google Colab T4 gratuito** disponibile quando quota e account lo consentono. Fonte ufficiale indica **solo uso non commerciale**, corrispondente al progetto soltanto se non vi sono attività promozionali o altri termini in conflitto. Non installato, non eseguito con GPU in questa revisione.
2. **DiffBIR v2.1** https://github.com/XPixelGroup/DiffBIR — generazione di dettaglio controllata con diffusione, opzioni viso/background e controllo fedeltà. Più lento e più pesante.
3. **SUPIR** https://github.com/Fanghua-Yu/SUPIR — restauro generativo molto spinto con controllo fedeltà; può inventare tratti e usa GPU e modelli pesanti. È NON commerciale. Non considerarlo automaticamente migliore sul volto: pubblicazioni di restauro segnalano possibili allucinazioni.
4. **CodeFormer** https://github.com/sczhou/CodeFormer — solo volto dove effettivamente leggibile e utile, confronto con parametro di fedeltà. Non cambiare identità e non sostituire un volto con uno inventato senza disclosure.
5. DDColor e Real-ESRGAN rimangono **base di confronto V63**, non motore finale automatico.

## Regia/recupero per ogni scena
- Selezionare **un vero keyframe congelato** con gesto emotivo leggibile, persona in dimensioni adeguate e crop che non taglia mani/volti. Selezione da tutto il video, non timecode casuali.
- Da quel solo frame derivare 3 candidati di foto fissa: `A conservative` (DDColor/ESRGAN), `B photographic-generative` (HYPIR o DiffBIR con fedeltà alta), `C photographic-stronger` (variazione moderata), stesso soggetto, stessa geometria, stessa luce prospettica.
- **Vietato fotogramma di fantasia fuori scena**: nessun volto aggiunto, figura cambiata, animale extra, edificio o carro non presente. Non trasformare una famiglia in un'altra famiglia; se la sorgente è troppo sfocata, cercare un altro frame più riconoscibile.
- Scegliere il migliore su qualità della pelle, occhi e capelli, vestiti, nitidezza reale, tessiture di muri/suolo, fedeltà alla posa, bordi senza halo. Quando esistono più persone in primo piano, controllare ciascuno.
- **Fotografia ricostruita ≠ dato storico autentico**: volti plausibili ma dettagli non recuperabili non saranno descritti come certi. Testo di disclosure nella descrizione/dossier.
- Mantieni il montaggio V61/V63 già migliorato: reale B/N in moto, stop esattamente sulla stessa geometria, morph breve e **2–3 secondi foto ferma** se importante, film 20–30 secondi a regia motivata.
- L'ultimo gesto compositivo è il controllo qualità SUL FILE esportato a 720p/1080p: nitidezza percettiva, niente fake 4K come metadato.

## Gate BLOCCANTE prima del prossimo video
`image_to_image_generatively_restored=true`, `actual_source_frame_sha256`, `candidate_model`, `candidate_image_sha256`, `human_visual_comparison_source_vs_photo_pass=true`, `fidelity_people_pose_objects_pass=true`, `reference_level_detail_qa_pass=true`; ogni volta con prove effettive, MAI prepopolare true. Richiedere almeno due varianti e annotare quale è stata scartata e perché. **Non basarsi solo su misure numeriche di nitidezza**: l'aumento di alte frequenze può derivare da rumore o contenuti inventati.
La GPU gratuita non è garantita: non avviare servizi che possano fatturare e non consumare Vidu. Se il modello desiderato non può essere eseguito, segnalare il blocco e non consegnare un MP4 inferiore spacciandolo per uguale agli esempi.

## Riscontri dei filmati forniti
- `43055.mp4`: 20,23s, 720×1280, 30fps; donna con cappello rosa 0,38s B/N e 1,38s fermo a colori: espressione, occhi, trucco e trama tessuti acquistano nettezza molto superiore. Altri casi 2,20→3,20s, 4,10→5,12s mostrano lo stesso salto; le immagini a colori **possono ridisegnare** dettagli, quindi non presumere fedeltà di identità non controllabile.
- `43054.mp4`: 23,73s, 720×1280, 30fps; 13,05→15,05s strada e carri e 17,10→19,10s cavalli e facciate mostrano texture di pietre, persone, carrozze molto più distinte. La composizione resta plausibile ma particolari potrebbero essere ricostruzioni artistiche.
- V63: la foto a colori ancora mantiene la morbidezza della fonte; usare come **negativo di qualità**, non reference.
- Non assumere che i video social di esempio siano PD: sono materiale di studio dell'utente, NON da pubblicare a nostra volta.

Riferimenti ricerca:
HYPIR https://github.com/XPixelGroup/HYPIR — 2025/07 Colab T4 e licenza non commerciale;
DiffBIR https://github.com/XPixelGroup/DiffBIR — pipeline generativa a due stadi;
SUPIR https://github.com/Fanghua-Yu/SUPIR — restauro generativo e tradeoff fedeltà.
