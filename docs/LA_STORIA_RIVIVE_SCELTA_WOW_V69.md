# LA STORIA RIVIVE V69 — PRIMA LA RESTAURABILITÀ, POI LA REGIA WOW
28 ottobre 2026. Decisione utente dopo V68 Parigi 1918: usare filmati antichissimi originali con **migliore qualità utile alla fotografia AI**. L'esempio della scena del cinema funzionava bene perché si vedevano l'insegna e la facciata; un ritratto di volto richiede però più pixel sul volto.

## Regola non negoziabile
**Mai scegliere la pellicola solo perché è famosa, vecchia o esportata in 4K.**
Cercare e confrontare pellicole autentiche d'epoca da scansioni migliori: 35mm ad alta risoluzione, sequenze meno mosse, soggetti più vicini, esposizione corretta, persone con occhi/viso leggibili, ambiente con texture e oggetti concreti. Per un formato 9:16 conta la risoluzione **dell'effettivo ritaglio del soggetto**, non il valore della larghezza totale del video. Distinguere scansione fisica 35 mm da video digitalmente ingrandito, restauri moderni e titoli con falso "4K". I sottocampionamenti realizzati in passato prima dell'AI sono proibiti.

## Tre livelli di selezione
**Livello A — potenziale sorgente:** per ogni filmato scaricare/analizzare il miglior trasferimento originale, non un video social ricolorato. Esaminare *più secondi* e scegliere almeno tre frame non consecutivi, non semplici duplicati. Valutare: pixel nativi dopo crop 9:16, leggibilità di visi ed espressioni, contrasto, sfocatura, graffi, persone non tagliate, oggetti storici, soggetto vicino alla camera e riconoscibilità. Sorgenti di dimensioni effettivamente maggiori hanno priorità solo se contengono più **dettagli originali utili**, non solo un raster maggiore.

**Livello B — mini-restauro AI obbligatorio:** ogni candidato selezionato deve passare una prova su **uno stesso fotogramma preciso** per foto originale → 2 varianti generative con diverso denoise/fedeltà. Solo DOPO le prove si sa quali filmati *riescono veramente a ricostruirsi meglio*. Usare, se disponibili entro le quote gratuite, Finegrain come effettivamente eseguito in V68, HYPIR/DiffBIR se tecnicamente accessibili. Non consumare crediti Vidu o GPU a pagamento senza consenso. Controllare cinque categorie particolari: naturalezza del volto, pelle/capelli, vestiti e gesti, architettura/muratura/scritte, continuità con il medesimo filmato B/N. Per gruppi di persone, **tutte le persone principali** devono essere coerenti. Visi e scritte inventati sono sempre interpretazione, non prova.

**Livello C — regia wow:** tra i soggetti che superano B, scegliere apertura emotiva forte (0–3s), un soggetto riconoscibile, freeze sull'istante più leggibile, morph in circa 0.2–0.5s, fotografia generativa nitida e ferma **~1.8–3.0s** (variazioni motivate), poi altra scena qualitativamente diversa. Il fermo può essere più lungo quando il dettaglio merita attenzione; meno scene ma ottime battono tante mediocri. Video normalmente ~20–30s secondo storia, non durata fissa. Musica e montaggio sulle transizioni; correzione colore coerente fra le foto; no titoli invasivi sulle persone.

## Criterio del selettore V69 — eseguibile
`src/storia_rivive_source_selector_v69.py` valuta l'immagine **originale** e separa due punteggi:
- `pre_restoration_scout_score_100`: misura solo priorità di esplorazione, con nitidezza standardizzata, pixel del crop effettivo, dimensione del soggetto, contrasto e valutazione *editoriale*.
- `after_real_ai_and_human_review_100`: solo dopo una FOTO AI REALMENTE GENERATA e una revisione per visi, tessuti, ambiente, fedeltà geometrica, emozione. **È questo punteggio che deve decidere la selezione finale**, non quello iniziale.
I controlli su sopracciglia/pelle e identità sono manuali; Haar frontalface advisory può mancare volti storici; correlazione a bassa frequenza non certifica stessa identità. Gate chiusi se mancano diritti in Italia/luogo di origine, provenienza della scansione, origini reali, foto già generata e approvazione visuale.
Test: `python -m unittest discover -s tests -p "test_storia_rivive_source_selector_v69.py" -v`.
Esempi formati in `templates/STORIA_RIVIVE_V69_SOURCE_RANK.json`.

## Candidati REALI documentati — per sopralluogo, NON qualità finale approvata
1. **San Francisco 1906, A Trip Down Market Street** — Wikimedia Commons `https://commons.wikimedia.org/wiki/File:A_Trip_Down_Market_Street_(1906).webm`. Originale WebM **3260×2420, 11:26, ~3.2 GB**, scansione del 2018 di 35mm d'epoca da Prelinger/Internet Archive. Ottima pista *di acquisizione* per tram, pedoni e carrozze, ma campo spesso ampio: i volti in lontananza possono essere piccoli. File dichiarato PD-US; per pubblicazione dall'Italia verificare specifica scansione e condizioni territoriali, nessuna approvazione automatica.
2. **New York 1903, Scenes in New York City** — `https://commons.wikimedia.org/wiki/File:Scenes_in_New_York_City,_1903.webm`, **1920×1080, 4:33, ~83 MB**; filmato di strada autentico con già stabilizzazione e riproduzione a velocità adattata. Il raster HD *non prova* risoluzione nativa della pellicola trasferita. Diritti indicati PD-US, verifica ulteriore necessaria.
3. **India 1906, A Native Street in India** — `https://commons.wikimedia.org/wiki/File:A_Native_Street_in_India_(1906).webm` **1920×1080, 2:52, ~49 MB**, una via affollata da camera fissa, BFI online/film caricato da YouTube. Il file compare PD India/UK/US ma i diritti della specifica registrazione, della digitalizzazione e la territorialità devono essere verificati. Nessun luogo cittadino da inventare: città identificata come sconosciuta.
4. **Parigi 1918, Gare de Lyon / cinema Parisiana** — V65/V68: B/N da vero archivio Musée Albert-Kahn, **raster 720×576**; V68 già generato con Finegrain quattro fotografie, confronto reale. La scena *cinema* ha architetture più leggibili; *stazione* e *venditrice* hanno soggetti più grandi per ritratti. Funziona come **benchmark esistente**, non come sorgente ideale definitiva.
5. **Scansioni cinematografiche 1905–1920** — ricerca di film muti con primi piani, attori, gesti; questi sono **film di finzione**: se usati, etichettare cinema d'epoca, MAI descriverli come riprese spontanee della realtà storica. Valutare diritti anche su musica aggiunta e restauro recente.

I numeri sono proprietà dichiarate dei file consultati, NON misurazioni dei frame completi né garanzie di legalità in Italia, né certificazioni di qualità 4K reale. Non usare mai materiale con licenza non verificata o fonti video AI già ricostruite presentandole come originale.

## Fattore WOW: cosa cercare in concreto
- Una persona guarda in camera e dopo il fermo immagine compaiono occhi/vestito/texture realistici, senza cambiare volto o postura.
- Un tram avanza fra la folla e si blocca quando una figura chiaramente riconoscibile entra in primo piano.
- Una facciata o una vetrina con dettagli originali leggibili torna con mattoni, scritte e tessuti fotografici, senza inventare marchi leggibili mai presenti.
- Una scena più vicina e nitida può vincere su una celebre panoramica 4K, perché ha **più informazioni per ogni soggetto**.
- Il wow deve iniziare con *il soggetto che si capisce*, non con una lunga introduzione.
- Mai rivendere come `4K originale` un file esportato 1080×1920 o restaurato generativamente; usare solo la definizione `alta qualità fotografica percepita`.

## Prossimo step operativo
Per un prossimo episodio, prima selezionare 3 fonti legalmente utilizzabili, esaminare 3–6 fotogrammi per ognuna, fare **un micro-test generativo** su 2 candidati e scegliere quello che ricostruisce più credibilmente la persona/oggetto. Soltanto dopo produrre MP4 con audio, ZIP, cover, 4 post, QA e download GitHub verificato e importare sul sito quando confermato. Se il generatore gratuito raggiunge quota, non spendere denaro senza permesso e non consegnare regressioni V65/V67 chiamate wow.
