# ArtVision Museum Director — proposta operativa V69 (29/10/2026)

Stato: SPECIFICA DI INTEGRAZIONE, non renderer implementato, non approvazione Gold Master. Integra V46/V57/V61/V68 senza sovrascrivere master, preset o pilot lock V58.

## Gerarchia delle fonti
1. Scheda del museo/collezione per esemplare esatto, dimensioni in cm e tecnica.
2. Fotografie verificabili della stessa opera con cornice (attuale/storica/originale sono tre categorie diverse).
3. Cataloghi e documentazione conservativa per dettagli mancanti.
4. Se ignoto: ricostruzione scenografica dichiarata; MAI attribuire misure inventate a cornice o sala.

## Scheda per opera obbligatoria
- artwork_id, title, artist, object_url, source_image_sha256, license
- artwork_height_cm, artwork_width_cm, dimensions_source, dimensions_confidence, edition_or_impression_id
- frame_status: original_documented | current_documented | historic_documented | partial_reconstruction | scenic_reconstruction | unframed
- frame_photo_source, frame_rights, frame_outer_dimensions_cm (null se ignote), frame_profile/material/depth, frame_assumptions
- gallery_status: actual_documented | declared_historic_reconstruction | declared_contemporary_reconstruction
- gallery_photo_sources, gallery_dimensions_known_or_unknown, architecture_rationale
- hanging_height_assumption, scale_reference, camera_start_pose, lens/perspective, painting_plane, painting_center_anchor
- entrance/exit beats, lighting rationale, 9:16 safe zones, shot storyboard, provenance/disclosure

## Selezione automatica con vincoli
A. Se esiste cornice fotografata della stessa opera: priorità alla replica, non alla decorazione arbitraria.
B. Se la cornice non è verificata: scegliere materiale/profilo coerente con periodo, tecnica e scala; segnare scenic_reconstruction.
C. Misure dipinto reali non si modificano per adattarle alla parete. Cornice e sala si adattano al dipinto; campo largo rende percepibile la scala. Dimensioni cornice non note = stima non presentata come misurazione.
D. Museo reale solo con fonte fotografica e diritto d'uso; altrimenti ambiente artistico plausibile dichiarato. Sala antica non obbligatoria per opera antica.
E. Centrare la camera sul dipinto, non sul centro vuoto della parete. Evitare visitatori in primo piano, corpi tagliati, titoli coperti.
F. Regia non ripetitiva: selezionare durata, percorso e dettagli in base a contenuto e dimensioni; continuità fisica camera V57/V64.
G. L'ingresso nel quadro è un effetto artistico: nessun falso particolare attribuito all'opera autentica.

## QA bloccante
- Dossier con fonti e misure verificabili, status delle ricostruzioni e diritti.
- Controllo geometrico rapporto d'aspetto, scala tra campo largo e close-up, cornice incassata/ombre, tutti gli angoli.
- Nessuna striscia da pixel stirati, ghosting, tagli innaturali, salto camera, prospettiva incoerente, figura amputata.
- Visione reale 9:16 su telefono: 0/1/3/5/7 s, ingresso, uscita, ultimo frame e intera traiettoria a velocità normale.
- Confronto con Cyclops V46 SENZA STRISCE + Cyclops V57 movimento + Hiroshige Museum Scale; se file non accessibili, confronto NON verificato.
- Controlli V13/V46/V55/V58/V68; ffprobe da solo non certifica qualità artistica.

## Quattro slot, senza confusione
Critico Standard: dettagli autentici + voce Gacrux.
Critico Museum: stesso identico WAV e copione, ma sala/cornice/POV.
Cinema Standard: musica autorizzata e regia dettagli.
Cinema Museum: musica autorizzata, ingresso/uscita continuo e museo specifico.
Quattro MP4 distinti, quattro pacchetti e 16 post originali; nessuna duplicazione mascherata.

## Rollout sicuro
1. Applicare prima a dossier e storyboard del pilota The Death of Socrates V67, senza modificare gli MP4 esistenti.
2. Generare una scheda Museum Director per le due varianti Museum; comparare con riferimenti approvati.
3. Implementare in seguito validator di scheda + adapter camera, con test automatici e review umana.
4. Non avviare nuovi quadri, render pagati, pubblicazioni o nuova automazione. Owner unico e pilot lock V58 restano invariati.
5. Aggiornare il preset globale solo con modifica versionata e verifiche di regressione; questo documento da solo non abilita nuove capacità.

Riferimenti: docs/ARTVISION_MUSEUM_IMMERSION_MODELLO_APPROVATO_V46.md; docs/ARTVISION_START_HERE_QUATTRO_VIDEO_RIPRODUCIBILE_V68.md; config/artvision_four_variants_presets_v68.json; docs/ARTVISION_MUSEUM_NO_CROPPED_VISITORS_V61_20261029.md.
