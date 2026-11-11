# ArtVision V121 — valutazione visiva REALE delle 5 foto V120, senza approvazioni inventate

**Data**: 2 novembre 2026. **Origine**: run V120 [41395451028](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41395451028), artifact #13119426005 (fino al 2 dicembre 2026). Le 5 fotografie JPEG realmente recuperate sono nell'archivio `ARTVISION_V120_FIVE_REAL_GALLERY_SOURCES_REVIEW` insieme a contatto e manifest. Le loro SHA-256 sono state ricalcolate dai byte ZIP e corrispondono al manifest. **Non sono video, non sono sale costruite in 3D e non sono approvazioni del proprietario.**

## Esito del controllo su immagini VISUALIZZATE (non un test estetico inventato)
- **GAL02 | Museo Barberini, Daniel Naber, CC BY 4.0**: migliore base fotografica da STUDIARE. Pareti scure ampie, pavimento parquet e soffitto illuminato; prospettiva visibile. C'è una persona sulla porta. Serve ricostruire la geometria metrica della sala e definire luce/camera; la fotografia singola NON è animazione con parallasse. Attribuzione e indicazione modifiche obbligatorie. **Priorità #1 per provino 3D non finale**.
- **GAL01 | Corcoran, Daderot, CC0**: architettura classica e luce belle, ma pareti molto decorate, porte e piedistallo al centro; non c'è parete disponibile sufficientemente semplice per inserire qualsiasi quadro senza compositing falso. **Solo riferimento materiali/luci, non stanza candidata approvata**.
- **GAL03 | Museum of the Walls, Roundtheworld, CC0 (come dichiarato nel manifest)**: corridoio a volta con pannelli/vetrine; spazio non adatto a riprese di dipinti. **Scartare come sala primaria**.
- **GAL04 | V&A Room 70, 14GTR, CC0**: fotografia reale di galleria espositiva, ma mobili/vetrine/oggetti e scritte coprono le pareti e impediscono un montaggio credibile dell'opera. **Solo riferimento di scala e materiali**.
- **GAL05 | Game Room, Loralielo, CC0 (come dichiarato nel manifest)**: setto scuro e colonna rosa ostacolano la composizione; opere visibili sullo sfondo, difficile mantenere parete neutra. **Scartare come sala primaria**.

Le licenze riportate sono quelle del manifest V120: **riesaminare la pagina Commons e le condizioni effettive prima dell'uso commerciale di ogni asset**, in particolare per fotografie con persone, oggetti e mostre.

## Stato vero dopo V121
- Fotografie raccolte e byte/hashes verificati: **5 / 5**.
- Sale museali come asset animabili, geometricamente ricostruiti e collaudati: **0 / 5**.
- Cornici autentiche per un'opera specifica ricercate e convalidate con queste sale: **0**.
- Provini MP4 Museum verificati V46/V57/V80/V118: **0**.
- Approvals finali / Gold / pubblicazioni: **0**.
- Standard, voci e MP4 precedenti: **NON MODIFICATI**.

## Prossima azione utile (non rimpiazzabile da fotografie ferme)
1. Recuperare la geometria/prospettiva e le misure di riferimento della sala scelta; se non verificabili, realizzare un **ambiente 3D dichiaratamente ricostruito** anziché fingere che una foto piana abbia profondità.
2. Per **una singola opera vera**, recuperare misure fisiche in cm, cornice documentata dell'esemplare e fonte museale; non cambiare dimensioni della pittura per riempire il frame.
3. Produrre un provino MP4 di **camera veramente continua** verso il dipinto e ritorno alla stessa sala; cornice visibile solo prima/dopo l'ingresso nei dettagli. Soprattutto niente zoompan di una singola foto e niente gallerie vettoriali/raster.
4. Confrontare davvero il MP4 con *Redon Cyclops SENZA STRISCE* (qualità/cornice) e *Hiroshige Museum Scale* (scala), documentando giudizio sui fotogrammi e alla velocità reale. Se regressione, correggere le sole varianti Museum, non toccare gli Standard.
5. Sostituire GAL03/GAL05 con fotografie di sale **vuote e angolate appropriatamente**, sempre con diritti verificati, senza promuovere un download a preset approvato.

**Audit ripetibile:** `python src/artvision_v121_photo_source_audit.py --archive PATH_ALLO_ZIP_V120` verifica corrispondenza dei byte e dei metadati rispetto a `config/artvision_v121_photo_source_visual_audit.json`. Non misura fotorealismo. Il comando è gratuito, senza provider o Vidu.

Regole preservate: `docs/ARTVISION_V119_LIBRERIA_MUSEI_CORNICI_ANTI_REGRESSIONE.md`, V46, V57, V80, V118. Richiesta V120 limitata ad acquisizione fotografica una tantum: nessun addebito, render, voce o pubblicazione.
