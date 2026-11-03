# Public Archive Sources V2 — cinque API in piu

Data: 4 novembre 2026. Estensione non distruttiva del selettore V34.

## Nuove API (nessuna chiave)

- vam — Victoria & Albert Museum, opere e immagini, termini da controllare.
- smk — National Gallery of Denmark, ricerca filtrata public domain e presenza immagini.
- wellcome — Wellcome Collection, collezioni e fotografie, licenza diversa per ogni file.
- nasa — NASA Image and Video Library, foto e video; loghi, persone, terze parti e termini da verificare.
- gallica — Biblioteca nazionale di Francia, documenti storici tramite XML SRU.

Totale 11 provider di ricerca configurati (6 V1 + 5 V2); Pixabay, Openverse e Pexels sono altre integrazioni preesistenti.

## Verifica reale GitHub Actions 04/11/2026

Tra i cinque nuovi provider: V&A, SMK, Wellcome e NASA hanno risposto con almeno un candidato; Gallica ha restituito HTTP 403 dal runner GitHub. Gallica rimane sperimentale/non utilizzabile in automazione finche l'accesso non sara verificato. Le risposte e i risultati di ricerca non autorizzano il riutilizzo dei media.

I test di contratto e integrazione V34 sono passati. Un test offline-quality di un modulo ArtVision preesistente e fallito indipendentemente dalle nuove API (ModuleNotFoundError artvision_museum_v119_guard), da correggere separatamente.

## Uso

Nel repository: Actions → Ricerca fonti ufficiali V2 → Run workflow; scegli progetto, provider e una query breve. Esporta scheda HTML leggibile su Android e JSON candidati.

Le regole delle scene consentono ArtVision con musei e Commons; La Storia Rivive con archivi, NASA, Gallica e Wellcome. Un riferimento di ricerca NON e un file multimediale approvato.

## Sicurezza

Diritti italiani, origine, autenticita, revisione visiva e pertinenza sono sempre pending fino alla revisione effettiva. Nessun download automatico, nessuna approvazione, nessuna pubblicazione e nessun servizio a pagamento. Non modifica i render esistenti, i master, V58, V80, V96, V99 o V134.

Ogni adapter e testato con fixture offline e chiamata reale sul PR; un fallimento del servizio resta visibile nel report. Nessun retry di errori 429.

## Riferimenti ufficiali

https://developers.vam.ac.uk/
https://www.smk.dk/en/article/smk-api/
https://developers.wellcomecollection.org/api/catalogue
https://api.nasa.gov/
https://api.bnf.fr/fr/api-gallica-de-recherche
