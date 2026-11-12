# ArtVision · V118 — qualità obbligatoria dei musei e delle cornici

**Data:** 1 novembre 2026. **Priorità massima per tutte le nuove produzioni ArtVision 4×1, Critico Museum e Cinema Museum.**

## Mandato esplicito del proprietario
«**Come regola le cornici e i musei devono essere sempre fatti bene**».

Questa è una **condizione di accettazione**, NON un invito facoltativo ad abbellire l'immagine. I video Museum precedenti tecnicamente decodificabili ma criticati dal proprietario dimostrano che FFmpeg PASS, ZIP CRC PASS, hash PASS e cornice visibile NON equivalgono a realismo museale. Una scena che pare dipinta al computer, senza luce e profondità credibili, è **difettosa** anche se il suo MP4 funziona.

**Regola decisionale:** se museo o cornice sono incoerenti, artefatti, visivamente finti, mal proporzionati o non convincenti nel video in movimento, **RIFIUTARE il Museum come prodotto finito, correggere solo i segmenti Museum e rifare la verifica**. Non etichettare Gold V25, non pubblicare, non distribuire come definitivo. I due Standard e le altre qualità del video NON vanno degradati per correggere la sala.


## AGGIORNAMENTO VINCOLANTE V331 — il quadro deve essere FRONTALE (12/11/2026)
L'utente rifiuta espressamente il quadro visto inclinato sul muro o da una prospettiva arbitraria. L'angolo base è **assiale, di fronte, perpendicolare alla tela**, quadro al centro e lati paralleli all'inquadratura. Non è ammesso scegliere una fotografia reale di sala laterale per la sola comodità del file: la fotografia autentica non garantisce una bella regia. Né è ammesso trasformare con un'omografia la stanza fotografata di sbieco in una falsa vista frontale. Prima di approvare un Museum, eseguire il QA V331 su veri fotogrammi MP4 (`src/artvision_museum_frontal_gate_v331.py`) + controllo artistico a velocità normale; verificare inclinazione, convergenza, centratura e proporzioni e non premiare il solo hash/FFmpeg. Eccezione angolata solo se l'opera stessa la motiva, con storyboard e consenso artistico esplicito. Nei vecchi video con difetto: lasciare `museum_approved=false`, correggere solo i segmenti museo e conservare master Standard. Guida: `docs/ARTVISION_V331_PROSPETTIVA_FRONTALE_OBBLIGATORIA.md`.

## A. Prima di costruire la sala
1. **Opera esatta**: titolo, autore, inventario, museo, fotografia originale e suo SHA256, proporzioni e misure fisiche cm documentate. Dipinto inalterato: mai sostituire il quadro con una versione ridisegnata dall'IA, cambiare personaggi/colori/composizione o inserire una falsa 3D pittorica.
2. **Cornice dell'esemplare preciso**: cercare immagini di installazione istituzionale, fotografia d'insieme e dettaglio, archivi museali/cataloghi con diritti e data. **V80 prevale**: `authentic_documented`, `faithful_reconstruction_documented`, `unverified`. Non chiamare mai «cornice originale» una decorazione generica, neppure se generata in stile barocco. Se non è documentabile, registrare l'incertezza e chiedere/ottenere un'**approvazione artistica esplicita per una montatura alternativa neutra** per quell'opera: altrimenti l'anteprima rimane REVIEW, non finale.
3. **Ambiente**: se si usa una foto reale di museo o un interno progettato, documentarne origine, licenza e se è davvero il museo che conserva l'opera. Una sala digitale **va dichiarata ricostruzione**; l'estetica deve comunque sembrare **fotografica e architettonicamente reale**, non una parete con rettangoli, piani a righe o una cornice appoggiata in 2D.

## B. Standard minimo della resa visiva
- **Architettura fisicamente plausibile**: piano del muro, pavimento con prospettiva e fuga coerente, luce realistica, ombre di contatto vere, profondità della cornice con battuta interna, spessore proporzionato, distanze corrette e materiali convincenti (legno, metallo, pietra, intonaco).
- **Scala reale della tela**, inclusi i piccoli pannelli e grandi tele monumentali. Non ingigantire un dipinto di 33 cm come un'opera di 5 metri. Nessun visitatore, sgabello o targhetta generica che introduca anomalie di prospettiva o anatomia.
- **Estetica sobria e specifica per l'opera**: evitare stanze identiche per tutti, faretti sproporzionati, cornici barocche intercambiabili, decorazioni platealmente digitali, finte targhette con testi inventati, fasce nere o scritte invasivi.
- **Transizione museale credibile**: mostrare cornice solo nell'approccio iniziale e nella ritirata finale. Durante voce/spiegazione e dettagli deve essere completamente fuori campo. La cornice scompare per avanzamento prospettico, non per dissolvenza artificiale.
- **Stesso esemplare, stessa montatura, stessa sala e luce** in ingresso e uscita. Niente salto prospettico, doppia esposizione, frame fantasma, texture deformate, righe, zoom sfocati o taglio brusco. Dipinto originale leggibile al suo centro e al giusto rapporto.
- **Nessuna perdita del formato vincente**: quattro video per quadro; Critico Standard e Museum con la stessa voce WAV/AAC; Cinema Standard/Museum con musica, montaggio narrativamente corretto e scene sincronizzate, senza rifare i master Standard già apprezzati.

## C. Gate operativo indispensabile, PRIMA della consegna definitiva
1. **Preflight per quadro**: fonti e foto effettiva della cornice, classificazione V80 e diritti; foto/sorgente per la sala e note sullo stato ricostruito; misure e confronto con la sorgente. Se assenti, marcare i campi `unverified`, non inventarli.
2. **Provino MP4 vero della sala, non una foto**: per entrambe le varianti Museum testare ingressi e uscite in movimento. Estrapolare fotogrammi **reali del MP4** e verificare dall'esterno alla tela, il confine con i dettagli e il ritorno. Controllare visivamente anche una visione a velocità normale su smartphone (o esplicitare che non è stata verificata).
3. **QA doppio**: controllo automatico di geometria/transizioni e integrità H264/AAC/ZIP, **più giudizio artistico umano su materiali, ombre, profondità, credibilità e proporzioni**. Lo script e i checksum non possono certificare che un museo «sembri vero».
4. **Criterio di rifiuto**: se un controllo non è stato fatto, scrivere `museum_status=rendered_needs_review`, `museum_approved=false`, `museum_artistic_review=missing_or_failed`. Se il museo sembra finto, **non promuovere**, non pubblicare e non consegnare come prodotto finale approvato. Correggere soltanto ingresso/uscita e raccordi delle due versioni Museum, preservando audio, centrale, durata e due versioni Standard; poi rieseguire QA.
5. **Archivio scaricabile verificato**: tutti i MP4 finali integri, SHA, URL concretamente funzionante, backup persistente verificato tramite readback; se Library piena, non fingere il salvataggio; GitHub Actions artifact a 30 giorni è solo temporaneo.

## D. Evidenze obbligatorie del dossier Museum
- `artwork_identity`, `museum_source_url`, `art_sha256`, `painting_size_cm`
- `frame_status`, `frame_reference_url` o `frame_search_evidence`, `frame_rights`, `frame_appearance_notes`, `frame_owner_exception_approval` se necessario
- `gallery_reference_url` o `gallery_source_hash`, `gallery_is_actual_museum`, `gallery_digital_reconstruction_disclosed`, `lighting_and_scale_notes`
- `museum_intro_video_sha256`, `museum_outro_video_sha256` o hash dell'MP4 finale con timestamp ingresso/uscita, `real_video_sample_frames_sha256`, `camera_transition_check`, `visual_reviewer`, `museum_artistic_review`
- `museum_approved` può essere `true` **solo** se l'utente ha approvato espressamente il risultato artistico o esiste il processo di approvazione umana autorizzato e verificabile; `V25_Gold` sempre con approvazione distinta.

## E. Applicazione e non regressione
Si applica **a ogni nuova opera e a ogni revisione Museum**, comprese produzioni lanciate da altre chat o automazioni. Si preservano opere/video già archiviati e regole V46, V57, V64, V73, V80, V25. Se un workflow precedente non possiede un controllo sufficiente, non assumere che un rendering riuscito soddisfi questa regola: etichettarlo REVIEW e aggiungere il controllo **prima di qualunque approvazione**.

**Principio da rispettare sempre:** il museo deve convincere **come video vero**, non soltanto come immagine o file tecnicamente valido. Nessun video mediocre sarà presentato come finito. Non fare spese API aggiuntive senza consenso.
