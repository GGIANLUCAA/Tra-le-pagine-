# VIDU scena A — piano gratuito (NON inviato)

- Episodio: Il ritratto ovale — Edgar Allan Poe
- Narrazione Google Gacrux: «Per leggere meglio, spostò il candelabro. Fu allora che un angolo rimasto buio si illuminò.»
- Intervallo proposto: 48,32–53,32 s del master Gacrux
- Fotogramma originale: SCENA_07.jpg, 720×1280, SHA256 `3387ded0dd0691fd24b91aee94028341291575986675679fc6e8a8d652d973b0` (solo file sorgente locale della conversazione, ancora da importare nel repository)
- Modello: Vidu `viduq2-pro-fast`, image-to-video, 720p, 5 s, `off_peak=true`, `audio=false`, `is_rec=false`
- Costo massimo approvato dall'utente: **8 crediti**, equivalente a ca. 0,04 USD ai prezzi Vidu; modalità normale da 16 crediti **NON AUTORIZZATA**
- Approvatore: utente nella conversazione del 28/10/2026; **il codice fingerprint del preventivo non è stato ancora sottoposto alla sua review**
- Codice preventivo immagine+prompt+durata+prezzo: `BC3BD42AC11A`
- Retry autorizzati: **zero**

## Prompt inglese

In a 19th-century Gothic castle bedroom, the wounded dark-haired traveler in a burgundy velvet coat deliberately slides the brass candleholder to his right with his fully engaged hand. The candle flames and their warm light move naturally across the dark wall, slowly unveiling a previously shadowed part of the room. Keep the older silver-haired servant standing behind him. A restrained, fixed-camera cinematic shot, lifelike coherent arm, wrist and finger motion, natural flame and shadow behavior. Preserve the exact identities, clothing, architecture and composition from the starting image. Do not invent an oval portrait inside this shot: the following edited shot reveals the portrait. No face distortion, no extra fingers or limbs, no morphing, no ghosting, no cuts, no subtitles, no writing, no music or generated speech.

## Esito verifica gratuita

Workflow `ritratto-ovale-vidu-balance-20261028.yml`: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40676036808

**BLOCCO:** `VIDU_API_KEY` assente nell'ambiente GitHub Actions. Impossibile leggere il saldo API. Nessun invio POST a Vidu; crediti addebitati da questa sessione: **0**.

## Revisione prima della spesa

Il fotogramma sorgente ha il candelabro/mano vicino al bordo destro: rischio di movimento fuori inquadratura. Prima di inviare è necessario confermare il frame/prompt ed evitare una chiamata a credito con un'immagine inadatta. La riproduzione del ritratto avverrà al montaggio nel taglio successivo SCENA_08, non con un falso morphing.

Stato attuale: `blocked_no_api_key_and_final_plan_review`. Il video master e ArtVision non sono stati modificati. Nessuna pubblicazione.
