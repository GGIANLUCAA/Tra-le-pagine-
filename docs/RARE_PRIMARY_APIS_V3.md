# Ricerca rara V3 — 10 nuove API per ArtVision e La Storia Rivive

**4 novembre 2026.** Ricerca su richiesta, senza chiavi nuove, download, addebiti o autopubblicazione. Modulo: src/rare_research_sources_v3.py. Compatibile con i controlli V33/V34, V58, V80, V96, V99 e V134.

## Le dieci funzioni

| Codice | Servizio | Uso concreto |
|---|---|---|
| rijks | Rijksmuseum Search API | Rinvenire identificativi ufficiali delle opere, poi controllare immagini e cornici |
| finna | Finna, Finlandia | Cercare fotografie storiche e dipinti anche di collezioni finlandesi, utili per Simberg |
| getty_museum | Getty Museum Linked Art | Consultare la scheda di un dipinto tramite UUID esatto e verificare dimensioni e registrazioni |
| getty_provenance | Getty Provenance Index | Rintracciare storia di proprietà e scambi tramite UUID ufficiale, non immagini |
| wikidata | Wikidata entity search | Confrontare identificativi di artisti e opere tra archivi (non autorità museale) |
| openverse_audio | Openverse audio | Trovare ambientazioni sonore (rotaie, acqua, folla) con licenze da controllare |
| librivox | LibriVox | Confrontare audiolibri di pubblico dominio e pronunce, non generare voci |
| openlibrary | Open Library Search | Rintracciare edizioni, date e autori per verificare le narrazioni |
| gutendex | Project Gutenberg/Gutendex | Cercare testi classici con verifica separata del dominio pubblico in Italia |
| crossref | Crossref bibliographic REST | Rinvenire pubblicazioni e DOI per verificare affermazioni storiche e artistiche |

Rijks e Finna sono inoltre collegati al selettore delle scene V34, rispettando le classificazioni. Gli altri otto sono strumenti di approfondimento e metadata; **non** entrano da soli nel rendering o nella scelta degli asset.

## Usare da Android

GitHub → Actions → **Ricerca rara V3 - Musei, Provenienza, Audio e Libri** → Run workflow.
Selezionare un provider, una ricerca e massimo 5 risultati; per Getty servono UUID ufficiali (ricerca per titolo non disponibile in questo adapter). Al completamento appare un archivio **RARE_SOURCES_V3_ANDROID_JSON_HTML** con una scheda HTML leggibile su smartphone e i metadati JSON.

Esempi:
- rijks / Night Watch
- finna / Hugo Simberg
- openverse_audio / train station
- crossref / Rembrandt art history
- getty_museum / c88b3df0-de91-4f5b-a9ef-7b2b9a6d8abb

## Policy vincolante

Solo candidati, mai file approvati. Tutti i risultati sono diritti, identità e revisione visiva **pending**. Non riprodurre in automatico il testo degli articoli; i metadati non costituiscono licenza per le immagini. Nessun media scaricato e nessuna copia delle registrazioni LibriVox. Nessun cambio a titoli, copertine, social o master già prodotti. La ricerca non attiva costi per API esterne, ma utilizza minuti GitHub Actions se l'utente avvia un workflow.

Prima della distribuzione attendere test unitari ed esito probe reale (una chiamata per provider). Se un provider restituisce HTTP 429 o errore di rete, registrare il fallimento e non fare retry aggressivi.

## Documentazione ufficiale

- https://data.rijksmuseum.nl/docs/search
- https://www.kiwi.fi/spaces/Finna/pages/53839221/Finna+API+in+English
- https://data.getty.edu/museum/collection/docs/
- https://data.getty.edu/provenance/docs/
- https://www.wikidata.org/wiki/Wikidata:Data_access
- https://api.openverse.org/v1/
- https://librivox.org/api/info
- https://openlibrary.org/dev/docs/api/search
- https://gutendex.com/
- https://www.crossref.org/documentation/retrieve-metadata/rest-api/
