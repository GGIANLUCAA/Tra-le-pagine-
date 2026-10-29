# ArtVision Blake Brooklyn — V77: cornice non verificata, correzione del 29 ottobre 2026

## Motivo
Feedback dopo Cinema Museum V76: la cornice vista nel video è giudicata orribile, artificiale, non veritiera e non coerente con l'opera. Il renderer V74 disegnava un bordo dorato ornamentale mediante rettangoli RGB; non esiste nel dossier una fotografia che dimostri tale cornice. V76 è rifiutato per la cornice e resta storico, non Gold Master.

## Fatti e limiti
- Originale: William Blake, The Great Red Dragon and the Woman Clothed with the Sun (Brooklyn Museum, 15.368), ca. 1803–1805.
- Tecnica: inchiostro e acquerello su carta; immagine 43,7 × 34,8 cm; foglio circa 55,1 × 43,3 cm.
- Fonte esatta: https://www.brooklynmuseum.org/opencollection/objects/4368
- Cornice espositiva storica o attuale non documentata nelle fonti disponibili. Non dichiararla originale e non confondere con la versione della National Gallery of Art, Washington.
- Sala e montatura rimangono una ricostruzione cinematografica illustrativa, mai una foto dell'attuale Brooklyn Museum.

## Patch circoscritta
- src/artvision_blake_visual_v74.py: barre dorate sostituite con profilo sottile color grafite e montatura neutra in stile conservativo, rispettando il foglio completo e la scala; copertina coerente.
- src/artvision_blake_render_v74.py: aggiornata la descrizione nel manifest.
- Invariati audio, copione, ritmi, entrata e uscita continue, sequenze di dettaglio, quattro slot, fonte Brooklyn, blocchi di spesa o pubblicazione e V58.
- Durante l'avvicinamento la montatura esce naturalmente dal campo; nei dettagli resta soltanto la pittura autentica; all'uscita ricompare nella stessa stanza (V73).

## Gate per il futuro
Prima di scegliere una cornice: cercare una foto autorevole dell'allestimento reale e riscontri sullo stesso esemplare. Se documentata replicarla senza inventare decori; se mancano prove usare una montatura sobria e dichiaratamente ricostruita, appropriata al supporto (carta/tela). Non usare bordi dorati generici per simulare autenticità. Questo principio già presente nel contratto madre è qui applicato a Blake senza cambiare il preset globale.

## Stato
Correzione di codice, non un nuovo video: nessun nuovo MP4 V77 certificato, ascoltato e approvato artisticamente. Prima di chiamarlo finito, eseguire test V77, rendering Cinema Museum, controllo apertura/dettagli/uscita, codec/ZIP e archivio reale. V76 resta separato come storico da correggere. Nessuna API a pagamento necessaria per questa cornice.
