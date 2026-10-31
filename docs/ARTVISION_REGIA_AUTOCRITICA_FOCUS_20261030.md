# ArtVision — Regia sincronizzata, autocritica e correzioni controllate (30/10/2026)

**Decisione globale dell'utente.** Nei film Critico, la scena descritta deve essere visibile **mentre le parole vengono pronunciate**, inquadrata correttamente, leggibile e con un tempo di permanenza motivato. La regia e la produzione automatizzata devono imparare dagli errori dei MP4 già finiti, ma **non devono peggiorare i master funzionanti**.

## Non cambiano i quattro format

- Critico Standard: voce Gacrux originale, spiegazione + dettagli autentici sincronizzati.
- Critico Museum: **identica registrazione WAV e identico testo**, ma camera Museum continua e cornice specifica dell'opera.
- Cinema Standard e Cinema Museum: musicali, **senza voce aggiunta**; dinamiche visive proprie, identità delle opere, cornice/misure e QA conservati.
- V58 pilot lock, V25, V46, V55, V57, V68 e i divieti di spesa/pubblicazione rimangono obbligatori. Questo modulo **non sblocca** la produzione in serie.

## Regola di regia PRIMA del render

1. Suddividere la **registrazione Gacrux reale** in frasi/segmenti con start e fine confermati da ASR/ascolto. Non inventare i tempi a partire dal numero di parole.
2. Per ciascuna frase identificare un soggetto, descrizione puntuale e un **rettangolo sorgente** sulla riproduzione autentica: es. volto, mano, libro, gruppo di figure. Il soggetto nel copione deve esistere nell'opera; non generare dettagli mancanti.
3. Per ognuna delle due varianti Critico predisporre una shot list che tenga conto dell'offset reale della voce e includa un crop per segmento. Quando si parla di un soggetto, il dettaglio deve essere già in campo (idealmente 0,2 s prima), restare fino al termine della frase e stare prevalentemente **al centro**; preservare arti, volti e relazioni importanti nel quadro.
4. **Durata dinamica**: la frase e l'importanza pittorica determinano la tenuta del dettaglio; evitare sostituzioni premature, zoom/stacchi decorativi, ripetizioni e ritorni inutili. Se una descrizione comprende più soggetti, creare segmenti distinti o una vera inquadratura di relazione.
5. **Museum**: inserire l'ingresso/uscita nelle pause o nelle parti narrative compatibili, mantenendo regolarità camera V57 e cornice V73 (visibile da fuori, naturalmente fuori campo in dettaglio, rientra nella panoramica finale). Non anticipare la camera al prezzo di perdere il soggetto narrato.
6. **Due Critico, stesso parlato ma regie distinte**: controllare singolarmente entrambi; non assumere che l'allineamento dello Standard valga automaticamente per Museum.

## Autocritica DOPO aver realmente creato il filmato

Una semplice sincronizzazione testuale **non prova** che sul video si veda il soggetto corretto. Il QA è a due livelli:

- **Controllo deterministico offline** — src/artvision_narrative_focus_gate.py: tempi reali della voce, copertura temporale della frase, visibilità geometrica del soggetto, centratura, SHA della stessa traccia audio per i due Critico, frame estratti dal **vero MP4**. Se una scena arriva tardi o taglia il soggetto, l'esito è bloccato e viene suggerita una correzione *non distruttiva*.
- **Controllo visivo**: aprire i REVIEW_FRAMES prodotti dal MP4, confrontare ogni frame col copione e con il dipinto sorgente, e registrare un responso pass o fail riferito all'hash dello specifico frame. Gli errori di identità del soggetto, semantica, atmosfera e moto richiedono interpretazione visiva; non trasformare metadati o un hash in una falsa certificazione artistica. Visionare/ascoltare il video intero a velocità normale, specialmente gli attacchi delle frasi e i primi 0/3/7 s.

### Ciclo di miglioramento senza regressioni

**Render revisione N → QA frase-per-frase → registro problemi → proposta di modifiche → render revisione N+1 → confronto A/B → QA di nuovo → eventuale promozione tramite tutti i gate già previsti.**

Per ogni problema registrare: artwork_id, slot, segment_id, error_code, original_mp4_sha256, original_qa_frame_sha256, fix_proposed, new_mp4_sha256, new_qa_result, regression_checked. I difetti ricorrenti diventano **test di regressione** nel codice o nel preset, non semplici promemoria. Se N+1 è peggiore, conservare N e **annullare la modifica**. Mai sovrascrivere i master approvati. Un errore non è corretto finché il **nuovo MP4** non supera una nuova revisione. Le proposte di timing/crop sono un input al renderer, non un video automaticamente rimontato.

**Non estendere un difetto specifico di un quadro a tutti gli altri senza evidenza.** Salvare le correzioni locali nella ricetta V68; promuovere a regola globale solo le correzioni generalizzabili, versionate e con regressione positiva.

## Interfaccia del gate (pianificazione e revisione reale)

Il manifest è una scheda aggiuntiva per una singola opera, non sostituisce il V68. Campi chiave:

- schema: artvision-narrative-focus-v1.
- shared_voice: wav_sha256, duration_s, timing_method: verified_asr, asr_with_interpolation_reviewed, forced_alignment_reviewed.
- segments: lista di id, start_s, end_s, speech, subject_id, subject_bbox_xyxy (coordinate relative 0..1 sull'immagine **intera** e autentica).
- variants.critico_standard e variants.critico_museum: wav_sha256 identico, voice_offset_s e video_duration_s effettivi, shots (uno per segmento) con segment_id, start_s, end_s, camera_crop_xyxy.
- In final: anche video_path relativo alla cartella del manifest e video_sha256 reali. Il video deve esistere, altrimenti blocco.
- Facoltativo reviews.json: per ogni slot e segmento, frame_sha256, status "pass", subject_matches_speech true, reviewer non vuoto. I frame sono estratti dal video con ffmpeg, non da una copertina ricreata. Un hash diverso dopo rimontaggio invalida la review.

Esempio di esecuzione da cartella repository:

~~~bash
python src/artvision_narrative_focus_gate.py \
  --manifest docs/productions/OPERA/ARTVISION_FOCUS_PLAN.json \
  --phase plan \
  --out docs/productions/OPERA/FOCUS_PREFLIGHT.json

python src/artvision_narrative_focus_gate.py \
  --manifest docs/productions/OPERA/ARTVISION_FOCUS_PLAN.json \
  --phase final --reviews docs/productions/OPERA/VISUAL_REVIEWS.json \
  --out docs/productions/OPERA/FOCUS_FINAL_QA.json
~~~

Il secondo comando genera frame **reali** nella sottocartella REVIEW_FRAMES. Prima del primo passaggio non si può avere una review valida: eseguire il comando una volta per produrre i frame, confrontarli, compilare VISUAL_REVIEWS.json, rieseguire, quindi controllare tutto il video. Il codice restituisce plan_checks_passed, blocked, needs_visual_review o ready_for_existing_v25_review; **nessuno stato equivale a Gold Master V25, import privato verificato o pubblicazione**. Confrontare FOCUS_FINAL_QA.json con QA V17/V25/V55. Dipendenze: solo Python standard library e ffmpeg per l'estrazione dopo il render.

## Limitazioni reali e integrazione successiva

Questo è un **gate offline riutilizzabile**, non un modello di visione che riconosce autonomamente dita, volti e soggetti dentro un filmato. Servono bounding box verificati e review visiva; non dichiarare auto-miglioramento completo finché il renderer non consuma le proposte, produce la revisione e la confronta. Non esistono nuovi MP4 creati da questa integrazione. Prima di collegarlo come gate obbligatorio al lavoro automatico, ogni renderer Critico deve produrre un manifest con timecode e crop della **propria camera**, senza inferirli falsamente dal solo testo.
