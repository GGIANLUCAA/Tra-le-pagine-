# ArtVision · ciclo ricerca + produzione · 19 novembre 2026, 09:33 Europe/Rome

## Verifica aggiornata e anti-duplicati
- Letto su main `data/archivio-generale/opere.json`, generato **2026-11-19T07:17:36Z**: **95 opere**, **153 slot documentati**, **127 non documentati** (NON sono slot pronti), **27 opere con quattro render documentati**, **545 elementi del sito**, dei quali **11 indisponibili**. Stato archivio `live_api` non prova che un singolo MP4 sia pubblicato.
- Letta `queue/artvision_new_series_20261114.json`: Ryder 1928.8 Cinema Standard + Museum già renderizzati; Beard 1971.104 foto HD non autorizzata; Critico resta vincolato alla voce Gacrux.
- Letto `research/artvision_cycle_handoff_20261119_0435.md`: Raffaello Scuola di Atene run 44413279766 artifact-only (non contare come nuovo soggetto), Delacroix/Turner Museum documentati, Segantini Belvedere 403 e Wikimedia 429: non ripetere endpoint.
- Letto `research/caravaggio_tre_opere_laiche_20261107.md`: I bari, Bacco e Medusa hanno museo/inventario e candidati immagine, ma nessun file locale verificato SHA256/pixel e licenza esatta/territoriale completa; non READY.
- Letto `docs/ARTVISION_RICERCA_OPERE_FONTI_HUB_20261107.md`: Monet Japanese Footbridge NGA 1992.9.1 è una fonte CC0 candidata, ma non ha file SHA verificato e non è nuova opera EXTRA pronta.
- La documentazione V330 `docs/productions/2026-11-12-artvision-music-v330-20-licensed-tracks-and-munch-pilot.md` specifica che i brani di catalogo partono `recording_verified:false`; la mera presenza nel catalogo non prova che l'audio scaricato e la licenza siano verificati.

## Strategie gratuite e blocchi
1. Coda nuova serie: Ryder già completato nelle due varianti Cinema; Beard bloccato sui diritti della foto precisa. Non duplicare né utilizzare preview proprietari.
2. Caravaggio: schede ufficiali e candidate immagini esistono, ma mancano bytes/hash/pixel, prova riuso commerciale per file preciso e vincoli italiani per Uffizi. Non sostituire con TTS o immagini generate.

## Decisione e handoff
Nessuno slot legalmente/tecnicamente READY provato da questi documenti. Non è stato effettuato un nuovo rendering, dispatch, download, pubblicazione, spesa o modifica alle code. **0 MP4 nuovi**; non dichiarare file o ZIP scaricabili. Per un prossimo Cinema Standard: prima verifica anti-duplicati sul registro aggiornato e checkpoint di variante, poi recupera un esemplare museale CC0 con download effettivo e SHA/pixel, musica V330 materializzata e autorizzata, lock concorrenti; solo dopo render e QA FFmpeg, ZIP e readback. Se una fonte fallisce due tentativi gratuiti, passare a opera distinta, non riprovare i medesimi endpoint bloccati. Non creare automazioni né cambiare orari.
