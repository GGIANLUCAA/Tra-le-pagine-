# ArtVision Museum Director V72 — utilizzo Android e stato verificato (29/10/2026)

## Stato reale
- **Funzionante su GitHub**: V69 validazione fonti, V70/V72 scala fisica, V64 camera continua, V68 ricetta quattro varianti, V71 integrazione e piano Socrate.
- **GitHub Actions superato**: run https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40927473346 ; 31 test automatici (6 V69 + 9 scala V72 + 5 camera V64 + 11 integrazione V71), più generazione reale del JSON di piano.
- **Non ancora prodotto da V71/V72**: nuovo filmato MP4. I quattro filmati Socrate V67/V59/V61 precedenti restano separati e NON sono stati alterati; 0/4 Gold Master V25. La QA artistica completa e la verifica dell'archivio privato non sono certificate.

## Android: ottenere il risultato del programma senza PC
1. Aprire la scheda [ArtVision Museum Integration Actions](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/artvision-museum-integration-v71.yml).
2. Aprire l'esecuzione riuscita oppure scegliere **Run workflow** sul ramo principale (se abilitato).
3. In fondo alla pagina dell'esecuzione scaricare l'artifact **socrates-museum-v71-planning-json** (ZIP con JSON). L'artifact è temporaneo: non è un archivio permanente e non contiene un video.
4. La sorgente permanente è nel repository: dossier `docs/productions/2026-10-29-socrates-pilot-v68/MUSEUM_DIRECTOR_DOSSIER_V71.json`, codice `src/artvision_museum_pipeline_v71.py`, `src/artvision_museum_stage_v70.py`, `src/artvision_museum_camera_v64.py`.

## Cosa funziona con il quadro Socrate
- Opera: 129,5 × 196,2 cm; cornice documentata circa 168,275 × 233,680 cm, profondità circa 14,605 cm.
- Cornice: foto del dipinto con cornice di Szilas (2008), CC BY-SA 4.0; non presupporre che la cornice fisica odierna sia identica.
- Sala: ricostruzione ispirata alla foto della Gallery 632, **non** ripresa autentica dell'installazione attuale dell'opera (Gallery 634).
- Distanza iniziale e proiezione prospettica sono **stime di regia**; per opere minuscole non usare lo stesso ingombro video delle tele grandi.
- La camera V64 ritorna senza salto alla posa di partenza. Le scene narrative del Critico devono ancora essere abbinate al WAV/ASR reale dal renderer, non solo ai keyframe del piano.

## Contratto di sicurezza
Niente generazione di nuove opere, duplicazione varianti, conversioni in Gold Master, spese Vidu/TTS, pubblicazione social, o falsa attestazione di archivio. Per la consegna di un nuovo MP4 sono indispensabili asset reali e licenze, renderer compatibile, visione/ascolto integrali, controllo nei primi 0/1/3/5/7 secondi, confronto con Cyclops e Hiroshige approvati, cover/16 post/ZIP e verifica import privata.

Comando GitHub Actions:
```bash
python src/artvision_museum_pipeline_v71.py \
  --dossier docs/productions/2026-10-29-socrates-pilot-v68/MUSEUM_DIRECTOR_DOSSIER_V71.json \
  --out output/MUSEUM_DIRECTOR_SOCRATES_V71_PLAN.json
```
