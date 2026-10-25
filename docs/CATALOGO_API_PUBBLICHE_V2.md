# Catalogo API pubbliche V2 — Tra le Pagine

**Data di verifica documentale: 25 ottobre 2026.**

**45 endpoint/sorgenti** senza API key per consultazione di dati pubblici (8 catalogati prima e 37 aggiunti). Per Wikimedia e Open Library alcuni endpoint derivano dallo stesso provider: non sono servizi indipendenti.

> **Stato reale: catalogate, NON integrate.** Questa aggiunta NON cambia l'attuale pipeline V6/V7/V11, la voce Gemini, gli asset o le automazioni. Le risposte non sono state testate in produzione una per una. Nessuna nuova chiave, quota a pagamento o abbonamento è richiesto. Un endpoint senza autenticazione NON attribuisce automaticamente il diritto di riutilizzare immagini, video, registrazioni o testi; verificare licenza e autore di ogni asset.

## Arte e musei

- [The Met](https://metmuseum.github.io/)
- [Art Institute Chicago](https://api.artic.edu/docs/)
- [Cleveland Museum](https://www.clevelandart.org/open-access-api)
- [Victoria & Albert](https://developers.vam.ac.uk/)
- [SMK Denmark](https://www.smk.dk/en/article/smk-api/)
- [Rijksmuseum](https://data.rijksmuseum.nl/docs/search)
- [Getty](https://data.getty.edu/)
- [Wellcome](https://developers.wellcomecollection.org/docs/catalogue)

## Archivi e media

- [Wikimedia Commons](https://www.mediawiki.org/wiki/API:Action_API)
- [Library of Congress](https://www.loc.gov/apis/)
- [Internet Archive search](https://archive.org/developers/)
- [Gallica SRU](https://www.data.gouv.fr/dataservices/api-gallica-recherche)
- [Gallica IIIF](https://www.data.gouv.fr/dataservices/api-gallica-iiif)
- [IIIF Image API](https://iiif.io/api/)
- [Openverse Images](https://api.openverse.org/v1/)
- [NASA Images & Videos](https://api.nasa.gov/)
- [Internet Archive Metadata](https://archive.org/developers/)

## Libri

- [Open Library search](https://openlibrary.org/developers/api)
- [Gutendex](https://gutendex.com/)
- [Open Library covers](https://openlibrary.org/dev/docs/api/covers)
- [Google Books public volumes](https://developers.google.com/books/docs/v1/reference/volumes)
- [Wikisource italiano](https://www.mediawiki.org/wiki/API:Action_API)
- [Open Library Subjects](https://openlibrary.org/developers/api)
- [Open Library Works](https://openlibrary.org/developers/api)

## Audio e musica

- [Openverse Audio](https://api.openverse.org/v1/)
- [LibriVox](https://librivox.org/api/info)
- [Open Opus](https://github.com/openopus-org/openopus_api)
- [MusicBrainz (non commerciale per servizio gratuito)](https://musicbrainz.org/doc/MusicBrainz_API)
- [Cover Art Archive (immagini protette)](https://musicbrainz.org/doc/Cover_Art_Archive/API)

## Ricerca e verifica

- [Wikipedia IT](https://www.mediawiki.org/wiki/API:Action_API)
- [Wikidata SPARQL](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service)
- [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [OpenAlex public](https://help.openalex.org/api/authentication/)
- [Europe PMC](https://europepmc.org/RestfulWebService)
- [arXiv](https://info.arxiv.org/help/api/)

## Natura e scienza

- [GBIF](https://techdocs.gbif.org/en/openapi/v1/occurrence)
- [iNaturalist](https://api.inaturalist.org/v1/docs/)
- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/docs/program_interfaces.html)
- [USGS Earthquakes](https://earthquake.usgs.gov/earthquakes/feed/v1.0/index.php)
- [US National Weather Service](https://www.weather.gov/documentation/services-web-api)
- [SpaceX V4 (repository archiviato, solo storico)](https://github.com/r-spacex/SpaceX-API)

## Dati e geografia

- [World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)
- [Eurostat](https://ec.europa.eu/eurostat/en/web/user-guides/data-browser/api-data-access/api-introduction)
- [OSM Nominatim (1 req/s, no bulk)](https://operations.osmfoundation.org/policies/nominatim/)
- [Open-Meteo (Free solo non-commerciale)](https://open-meteo.com/en/terms)

## Priorità di integrazione

1. **ArtVision:** Met, Chicago, Cleveland, SMK, Rijksmuseum, Getty, Wikimedia Commons; scarica solo opere chiaramente autorizzate e conserva i credit.
2. **Libri e racconti:** Gutendex, Open Library per ricerca puntuale, Gallica, Wellcome e Wikimedia; per illustrazioni nuove resta necessario un motore AI separato.
3. **Cronaca/scienza:** NASA Media, Library of Congress, USGS e fonti primarie. Non presentare materiale d'archivio come fotografie dell'evento recente.
4. **Suoni e musica:** Openverse Audio e LibriVox con licenze specifiche; Open Opus fornisce solo metadata e non registrazioni.
5. **Verifica narrativa:** Wikidata, Google Books, Crossref, OpenAlex, Eurostat e World Bank con caching.

## Regole tecniche prima di collegare ogni provider

- Prova API con una richiesta minima e controllo status, formato e campi reali. Non dichiarare funzionante il provider prima della prova.
- Un modulo per provider: documentazione, ricerca, selezione, download opzionale e metadata licenza.
- Separare ricerca e import; evitare scraping, crawler e download di massa. Non fare retry a raffica su 404/429.
- User-Agent identificabile, cache, throttling, timeout e deduplicazione hash, fallback fra provider.
- Ogni asset nel manifest: URL originale, autore, licenza, titolo, data accesso, contenuto SHA256, scena narrativa e revisione qualità.
- Open Library e Covers NON sono pensati per backend di massa. Wikimedia e musei usano quote condivise e termini specifici.
- Open-Meteo Free e MusicBrainz Free riportano limitazioni per uso commerciale; non attivarli in output monetizzati senza titolo d'uso.
- API SpaceX V4 è archiviata dal 2026: solo come riferimento storico se ancora disponibile.
- Nessuna API qui sostituisce il sistema di generazione AI gratuito AI Horde già integrato in prova separata.

## Fonti di esclusione

Non inserire come *senza chiave* Europeana, Smithsonian, Pexels, Pixabay, Freesound, Guardian Open Platform o REST Countries v5: per gli usi indicati richiedono una key, o autenticazione appropriata.

Per il catalogo completo con endpoint, esempi, limiti e note delle licenze, usare il file JSON V2 consegnato nella conversazione e importarlo nel progetto soltanto dopo validazione dei provider.
