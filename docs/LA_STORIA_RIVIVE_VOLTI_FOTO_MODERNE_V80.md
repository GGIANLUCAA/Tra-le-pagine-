# LA STORIA RIVIVE — V80/V81 · VOLTI COME FOTOGRAFIE MODERNE

**29 ottobre 2026 — correzione esplicita dell'utente:** «La qualità ricostruttiva deve essere ancora migliore; i volti devono essere fatti molto meglio, ricostruirli come se la foto fosse stata scattata oggi».

## Obiettivo artistico VINCOLANTE
Nel fermo-immagine AI a colori, il volto deve apparire davvero come un ritratto fotografico contemporaneo: viso chiaro, occhi distinti, palpebre e sopracciglia naturali, lineamenti armonici, pelle con pori e pieghe credibili, capelli a singoli ciuffi, abiti ricchi di materiale reale e colori diurno naturali. Non basta una colorizzazione o un filtro di contrasto. Nessuna patina di seppia o dominante verde/arancione, nessun viso plasticoso, troppo levigato, sfocato o pittorico. La priorità è l'effetto *wow* visivo accompagnato dalla fedeltà.

## Conservazione della verità storica
La fotografia a colori è una ricostruzione moderna ipotetica, NON una vera fotografia a colori d'epoca. Le caratteristiche intrinsecamente indecidibili dal fotogramma (colore esatto degli occhi, singoli pori, linee del viso cancellate dalla grana) non possono essere certificate. Vincolo irrinunciabile: stessa quantità di persone, stesse sagome, stessa fascia di età, posa, abiti, acconciatura, capelli, espressioni e posizione degli oggetti. Vietate le conversioni «ruota/scala→uomo», «uomo→oggetto» e volti scambiati. Nessun ringiovanimento glamour artificiale.

## Processo corretto per ciascuna scena
1. Preselezionare vera pellicola storica con volto **sufficientemente grande**, piuttosto che cercare di ricostruire a distanza passanti di pochi pixel. Scegliere 3–5 fotogrammi vicini e verificare il vero viso.
2. Restauro B/N, recupero stabile di danni/graffi, source-bound image-to-image AI fotografica — non re-rendering di tutto il filmato né zoom di uno still.
3. Facce: usare strumenti di recupero facciale GRATIS quando disponibili (es. CodeFormer) come passaggio su sola ROI viso; confrontare con l'originale ed escludere output che ricrea un'altra persona. Scegliere forza di ricostruzione per singolo soggetto, non un unico 0.22/0.27 per tutto.
4. Color grading moderno bilanciato, profondità luminosa naturale, pelle non cerosa, contrasto localizzato; inpainting di graffi sottili senza distruggere naso/occhi/capelli. Conservare oggetti e background.
5. Confronto visivo: sorgente autentica, foto AI base, eventuale volto recuperato e finale. Non approvare solo da correlazione globale: analisi locale/manuale di occhi, naso, bocca e mani, oggetti protetti, coerenza età/espressione.
6. Se il volto resta poco leggibile oppure il generatore lo cambia troppo, rigenerare LOCALMENTE con limiti e costo approvati oppure selezionare un'altra vera scena; non dichiarare master definitivo.
7. Regia approvata inviolabile: **vero movimento B/N → stop sul frame realmente filmato → fotografica AI a colori ferma e dettagliata → nuova vera clip**. Titolo elegante con LUOGO e ANNO, 20–26 sec se materiale adeguato, no voce, musica originale.
8. MP4 H264/AAC e ZIP scaricabili realmente (GitHub Release Android + sandbox se verificato), copertina, post social, fonte/diritti e QA; niente spese Vidu/API senza permesso; non confondere riuscita tecnica con approvazione artistica.

## Test V80 «I primi baci del cinema 1896–1900»
Due pellicole originali distinte: https://commons.wikimedia.org/wiki/File:The_Kiss_(1896).webm e https://commons.wikimedia.org/wiki/File:The_Kiss_(1900).webm.
Tre fotogrammi reali distinti e relativi volti restaurati con DDColor+Finegrain+CodeFormer+correzione colore locale gratuita. Montaggio: 20,83 s, 720×1280, audio originale, tre trasformazioni statiche, MP4 e ZIP verificati. Fred Ott 1894 è stato escluso per qualità insufficiente. Si tratta di un **provino artistico**: la fiducia nella corrispondenza identitaria resta da verificare e la resa da foto moderna può ancora migliorare con fonti migliori/generazione più affidabile. Non chiamare 720×1280 video «4K nativo».
- Video script: src/storia_v80_primi_baci_faces_video.py
- Image script: src/storia_v80_modern_face_detail.py
- Video workflow: .github/workflows/storia-v80-primi-baci-final.yml
- Immagini di review: i 3 JPG/PNG e report QA del workflow fotografie V80.
**Questa regola prevale sul vecchio errore V77 di ridurre ovunque la nitidezza e sul genere standard «basta colorizzare».**
