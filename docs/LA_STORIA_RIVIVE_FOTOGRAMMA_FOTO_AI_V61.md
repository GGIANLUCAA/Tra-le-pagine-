# LA STORIA RIVIVE V61 — FOTOGRAMMA CHE DIVENTA UNA FOTOGRAFIA AI, POI RESTA FERMO
**28 ottobre 2026 — correzione esplicita dopo V60 e analisi dei TRE MP4 di riferimento nuovi.**
**Questa regia sostituisce il preset V56/V57/V58/V60 "tutta la pellicola a colori in movimento" come STANDARD quando si vuole l'effetto degli esempi.** Conserva autenticità della fonte, pubblico dominio/CC0 V59, V55/V28, formato verticale, consenso spese e trasparenza sulle immagini create.

## FATTI REALI MISURATI, non interpretazioni
File utente `43054.mp4`, `43055.mp4`, `43056.mp4`: tutti MP4 H264 **720×1280, 30 fps**. Il loro aspetto nitido non dimostra 4K né la tecnica AI specifica che li ha generati.
- **43054** (23,73 s): sei cicli di riprese d'epoca in B/N in movimento e **immagini a colori statiche**. Finestre colorizzate osservate: circa **2,10–4,13**, **6,07–8,07**, **10,03–12,17**, **14,07–16,13**, **18,00–20,10**, **22,00–23,73** secondi. Fotogrammi nel colore finale sono virtualmente identici per circa 2 s. Il video B/N di ciascuna scena dura circa 2 s prima del reveal. Questa è una **regia LENTA**.
- **43055** (20,23 s): per gran parte dei primi 16,4 s un **ciclo di circa 1,87 s**: ~0,9 s B/N in movimento, ~0,9 s fotografia fotografica a colori. Le finestre colorate partono circa a **0,93, 2,80, 4,67, 6,53, 8,40, 10,27, 12,13, 14,00, 15,83 s**. Le porzioni colorate possono avere microzoom/movimento digitale, ma NON il moto naturale della pellicola. Testo promo finale del video esempio NON trasferire al progetto.
- **43056** (20,97 s): **stessa cadenza rapida** ~0,9+0,9 s con immagini AI a colori dall'estetica Belle Époque; molte scene e finale promozionale dell'esempio, NON da replicare come copy.
- La transizione **è un taglio/morph visivo verso il fotogramma colorizzato e ricostruito**; non è una semplice LUT o una colorizzazione DDColor su TUTTI i frame come V60. L'immagine COLORATA diventa una **FOTOGRAFIA** e rimane visibile. Questa è l'informazione decisiva.

## Regola vincolante V61: motore "VIDEO VERO → FREEZE → FOTO AI"
Per ogni inquadratura:
1. Scegliere **una breve ripresa video storica autentica in B/N**, con movimento reale, emozione, gesto, occhio, dettaglio e soggetto riconoscibile. **Fonte del SINGOLO filmato CC0 o PD verificata**. Migliorare esposizione/stabilizzazione soltanto se aiuta.
2. **Scegliere il fotogramma di congelamento** con regia e non per intervalli automatici: quando l'espressione è leggibile o quando l'azione si ferma in un momento significativo. Estrarre QUEL vero frame come `frame_seed`, con timecode/hashes.
3. Generare una **NUOVA FOTOGRAFIA** dal `frame_seed` con uno strumento **image-to-image restauro ricostruttivo** (es. SUPIR/DiffBIR; eventualmente CodeFormer per volti e DDColor per colore semantico, dopo verifica tool/pesi/GPU). L'immagine deve apparire **moderna, fotografica, nitida, cromaticamente distinta e non plastica**, senza fingere che i dettagli inventati siano storicamente autentici.
4. **Preservare identità e struttura**: numero di persone, postura, posizione, gesti, oggetti principali, ambiente e costumi devono corrispondere alla fonte. Vietati mani extra, facce completamente diverse, auto moderne, luci artificiali. Qualunque contenuto ricostruito viene dichiarato `Fotogrammi storici autentici, fotografie a colori ricostruite con IA`. L'output AI NON è prova dei colori, materiali o lineamenti esatti del 1900.
5. Congelare l'ULTIMO frame del clip B/N. Nel giro di **0,15–0,9 s** trasformarlo nel file `restored_still` tramite dissolvenza/morph guidato dalle corrispondenze visive, non una ripresa nuova arbitraria. **Dopo la trasformazione l'immagine NON deve continuare a muoversi come la vecchia pellicola**: vero fermo immagine; al massimo un microzoom di 0–1% solo quando aggiunge profondità e non falsifica moto.
6. **Tenere la foto a colori abbastanza a lungo da apprezzare i dettagli**: 
    - `fast_reveal` ispirato a 43055/43056: circa **0,8–1,1 s** di film B/N, **0,6–1,1 s** di foto colorata inclusa trasformazione (reveal breve ~0,18–0,30s).
    - `slow_reveal` ispirato a 43054: circa **1,8–2,3 s** film B/N, **1,8–2,2 s** fotografia colorata inclusa trasformazione (reveal ~0,20–0,40s).
    - `editorial_custom`: tempi motivati dalla storia. Non imporre modello fisso: un taglio lento deve avere un motivo, più scene solo se diverse e coerenti.
7. Cut alla nuova clip B/N (o diversa scelta registica se motivata). Ogni scena deve essere **una vera ripresa distinta**, non semplicemente gli zoom e tagli della stessa foto. Apertura 0–3 s forte, ritmo musicale sincronizzato ai cambi **B/N→foto AI**.
8. Master social **720×1280 ottimo o 1080×1920**; NON 4K finto obbligatorio. **La fotografia AI deve avere risoluzione fonte alta** (ideale >= 720×1280 dopo taglio corretto e dettagli chiaramente leggibili). Real-ESRGAN può ingrandire ma non sostituisce la ricostruzione fotografica; DDColor colorizza ma **non ricostruisce dettaglio**.
9. Serie breve e modulare: se ci sono due scene belle sono meglio di sei ripetitive; 10–25 s consigliati dai riferimenti come ipotesi, non vincolo. Film+foto nello STESSO ciclo, non film interamente B/N e poi compilation di immagini.
10. **Nessun inserto Vidu necessario**: la magia nasce dalla foto AI. Vidu resta scelta futura, marcata `RICOSTRUZIONE AI`, solo con consenso per crediti, evitando di presentarla come materiale originale.

## Motori esterni: scopo corretto
- `SUPIR` https://github.com/Fanghua-Yu/SUPIR : image restoration generativa fotorealistica, **non commerciale** come dichiarato dal repository; potenziale alto per foto fissa, richiede GPU e pesi. Non installato/testato in questo flusso.
- `DiffBIR` https://github.com/XPixelGroup/DiffBIR : image restoration con diffusion, codice Apache 2.0, pesi/licenze dipendenti da modelli usati; GPU richiesta. Non installato/testato.
- `CodeFormer` https://github.com/sczhou/CodeFormer : restauro volti NTU S-Lab License 1.0, uso non commerciale; attenzione alla fedeltà volto; solo opzionale. Non installato/testato.
- `DDColor` https://github.com/piddnad/DDColor: può aggiungere i veri colori, ma il V60 ha mostrato che **non basta**. Può essere una fase preliminare alle fotografie AI, NON il risultato finale.
- I progetti open source/non commerciali sono candidati se il loro caso d'uso consente una **pubblicazione social non monetizzata**; condizioni di singoli pesi/policy da verificare. Se risorse GPU assenti: `PHOTO_AI_NOT_RENDERED`, non `APPROVED`.

## Test riproducibile V61
`src/storia_rivive_photo_freeze_v61.py` costruisce **solo il montaggio** da MP4 d'epoca e fotografie AI GIÀ generate. Mostra realmente: B/N in movimento → stop sul frame → transizione → foto a colori FERMA → nuovo clip. **NON genera l'immagine con AI** e rifiuta lavori reali senza `still_ai_verified`, provenienza, timecode, diritti e review fedeltà. Gli esempi `43054/55/56` NON vengono copiati nel repo né pubblicati (video forniti per studio, non attestati PD). In test offline, le foto sintetiche di verifica NON devono essere consegnate come risultato storico AI.
- Test CI: input B/N in movimento generato da FFmpeg + still finta, output MP4 H264/AAC, colore presente solo dopo il freeze e nessun movimento naturale nella foto. Questo è un **test tecnico**, NON una dimostrazione artistica.
- La prima vera prova finale deve invece usare una **vera fotografia ricostruita con modello image-to-image**, paragonata visivamente a quelli forniti: colore, capelli, occhi, vestiti, luce, materiali, composizione, dettagli, assenza di artefatti, qualità percepita e timecode.
- Consegna V55 resta obbligatoria (MP4, ZIP, cover, 4 post, link Android realmente scaricabile, verifica archivio) e su GitHub Release MP4 diretto se la Libreria fallisce; non inventare sincronizzazione sito.

**V60 Beirut 1919:** filmato autentico e colorizzato, ma **NON conforme esteticamente a V61**; NON riproporlo come esempio dell'effetto chiesto. Le regole V56–V60 valgono come sottoinsiemi tecnici e della documentazione storico-artistica, non come alternative equivalenti al reveal foto AI.
