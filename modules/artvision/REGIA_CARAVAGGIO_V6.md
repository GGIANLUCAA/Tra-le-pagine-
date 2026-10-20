# ART VISION CINEMA V6 — CARAVAGGIO (film completo, da valutare)
Data: 20 ottobre 2026. Baseline **Cinema V6 Van Gogh approvata**, non sovrascritta.

## Produzione verificata
- GitHub Actions [run #2 — SUCCESS](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39460424298) del workflow `.github/workflows/artvision-caravaggio-v6.yml`.
- Nuovo film Caravaggio completo: 150.000s, Full HD verticale 1080×1920, 24fps, H.264 + AAC.
- **17 opere autentiche** dai relativi file Wikimedia Commons, metadata e condizioni in `RIGHTS_AND_SOURCES.json`; **66 inquadrature curate**.
- Filmato e cover verificati localmente e tavola regia ispezionata (13 fotogrammi distribuiti sul filmato).
- Music track diverso da Van Gogh: **Darkest Child** (Kevin MacLeod), registrazione vera, CC BY 4.0; niente voce o liriche. Rispettare attribuzione nella descrizione.
- Il primo tentativo ha fallito perché Wikimedia Commons restituiva 429 su alcune miniature e c'erano soltanto 38 shot, sotto la soglia creativa. Nel secondo sono stati predisposti 1.9k fallback, scansioni PD alternative per Judith/Narcissus e una regia distribuita di inquadrature extra. Il secondo test è riuscito.
- Nessuna API video a pagamento, nessuna pubblicazione automatica. **La V6 Van Gogh resta la versione GOLD MASTER approvata**; Caravaggio va valutato dall'utente separatamente.
- La fonte fotografica del Bacco 1595–97 di Wikimedia è di **Sailko, CC BY 3.0**. Attribuzione di Sailko, licenza, link e note di modifica in documento social. La pagina Wikimedia riporta esplicitamente una nota su ulteriori permessi italiani per sfruttamento commerciale del bene culturale; NON affermare automaticamente la piena monetizzabilità.
- Altre fonti dichiarate PD/CC0 in `RIGHTS_AND_SOURCES.json`; esaminare singolarmente termini di riuso, anche italiani, prima di vendita/promozione.

## Codice additivo riutilizzabile
- `modules/artvision/export_caravaggio_v6.py`: selezione di Commons File con immagine alta definizione e filtro per licenza, fallback cache durante rate limit.
- `modules/artvision/director_caravaggio_v6.py`: nuova sceneggiatura in cinque movimenti e 66 inquadrature individuali. Riusa l'**identico motore cinematografico** `modules/artvision/director_cinema_v6.py` senza modificare i sorgenti approvati.
- `.github/workflows/artvision-caravaggio-v6.yml`: workflow Android-ready che scarica, monta, valida e carica artifact.
- Pacchetto locale: `ArtVision_CARAVAGGIO_Cinema_V6_PACCHETTO_FINALE.zip` con lo stesso film H.264, cover, storyboard e attribuzioni integrate.

## Pattern creativo permanente
Per ogni nuovo artista NON usare ciecamente le coordinate di Caravaggio o Van Gogh. Creare una nuova mappa di luoghi emotivi nel quadro, corrispondenze tra scene, dettagli ricorrenti e una musica con licenza diversa. Conservare lo schema di regia V6 approvato: opere autentiche dominanti, tagli spesso 2–4s, apertura internazionale artista + piccolo MUSIC BY, zero testo successivo, nessuno split-screen, un solo film completo.
