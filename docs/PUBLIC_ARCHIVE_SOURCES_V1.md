# Fonti ufficiali collegate V1 — 03/11/2026

Integrazione software effettiva nel selettore V34 (src/source_selector_v34.py),
senza cambiare il rendering, la produzione 4x1, V101 o i master precedenti.

## Sei adapter di ricerca senza chiavi
- met: Met Museum, API di ricerca paginata v1.1 (la v1 e stata ritirata).
  Un massimo di 1 ricerca + 5 richieste di dettaglio. Solo record PD con immagine.
- artic: Art Institute of Chicago, opere is_public_domain e ID immagini IIIF.
- cleveland: Cleveland Museum of Art, filtro CC0 e immagini presenti.
- loc: Library of Congress, ricerca metadata foto e filmati (fo=json).
- archive: Internet Archive, ricerche mediatype movies via advancedsearch.
- commons: Wikimedia Commons, ricerche namespace File con extmetadata licenza.

Pixabay e Openverse erano gia collegati prima di questa modifica; Pexels
e presente nel modulo Archivio Media V7 se e disponibile una credenziale.

## Come eseguire una ricerca reale

GitHub Actions -> Ricerca fonti ufficiali V1 -> Run workflow.
Scegliere:
- artvision: met, artic, cleveland o commons.
- storia: loc, archive o commons.
Inserire una query specifica e 1-5 candidati.
Scaricare l'artefatto CANDIDATI_FONTI_UFFICIALI_V1 con scheda HTML Android e JSON.

CLI equivalente:

python src/source_selector_v34.py --mode discover --brief config/public_api_artvision_v1.json --scene opera --provider artic --query "Seurat" --limit 3 --out output/artvision

python src/source_selector_v34.py --mode discover --brief config/public_api_storia_v1.json --scene archivio --provider loc --query "Market Street 1906" --limit 3 --out output/storia

## Cosa non fa (per sicurezza e diritti)

Ogni risultato resta rights_review=pending, visual_review=pending,
authenticity_review=pending, scene_relevance=pending. Una dicitura
Public Domain o CC0 nel catalogo NON basta a garantire la pubblicazione in
Italia, la correttezza del singolo file o la fedelta dei volti.
Il modulo non scarica media, non produce MP4, non consuma crediti,
non crea approvazioni e non pubblica su sito/social.
Non forza la pipeline storica e non bypassa V58/V80/V96/V99/V134.

Test unitari offline; la disponibilita degli endpoint dal runner va verificata
con un'avvio reale del workflow. Nessun retry su 429 e nessuna ricerca bulk.

## Rinvii a servizi non ancora attivati

Europeana, Smithsonian, Freesound, TTS, Groq, Gemini, Jamendo,
JSON2Video, Shotstack, CloudConvert e UpRes possono richiedere
account, chiavi, costi o verifiche di condizioni. Non sono stati
attivati automaticamente e non vanno etichettati come integrati.

Documentazione:
https://metmuseum.github.io/
https://api.artic.edu/docs/
https://openaccess-api.clevelandart.org/
https://www.loc.gov/apis/
https://archive.org/developers/
https://www.mediawiki.org/wiki/API:Main_page
