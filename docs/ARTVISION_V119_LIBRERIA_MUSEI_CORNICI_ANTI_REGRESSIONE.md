# ArtVision V119 — Libreria riutilizzabile di musei e cornici, scala reale, zero regressioni
Data: 2 novembre 2026. Origine: decisione esplicita dell'utente in conversazione vocale.
**Stato della libreria: PROGETTATA, NON ANCORA REALIZZATA/APPROVATA.** Non dichiarare che cinque scene o cinque modelli video sono già pronti; sono tipi candidati da costruire e collaudare.

## Decisione del proprietario
Non ricominciare ogni volta da una sala generata in fretta: costruire e conservare inizialmente **5 ambienti fotografici/3D credibili** e **5 famiglie di montatura/cornice curate**, ampliabili; selezionare per opera, senza ripetizioni meccaniche. Il riuso serve a **mantenere il livello migliore raggiunto**, non ad applicare lo stesso sfondo o la stessa cornice a tutto. La **grandezza fisica reale del dipinto deve rimanere percepibile** nella vista di sala; la telecamera può avvicinarsi ma il quadro non cresce sulla parete.

## Riferimenti obbligatori già approvati, NON da perdere
1. **Redon, The Cyclops — SENZA STRISCE CORRETTO**, riferimento V46: qualità cornice, tela inserita fisicamente, ingresso/uscita e assenza di distorsioni. Originale e link nel documento V46.
2. **Hiroshige, Sudden Shower — Museum Scale**, riferimento V46: scala umana corretta (piccola stampa resta piccola), prospettiva e distanza camera. Originale e link nel documento V46.
3. Il movimento continuo V57 di Cyclops completa entrambi i riferimenti.
La galleria raster/procedurale V114/V116/V117 (pareti/pavimento disegnati e semplice zoompan) è **RIFERIMENTO NEGATIVO**: non sostituire automaticamente uno dei master approvati con questa tecnica. Un MP4 decodificabile non prova realismo.

## Cinque ambienti CANDIDATI (nessuno è ancora asset approvato)
- **GAL01 | Galleria classica luminosa**: pareti intonacate, parquet/pietra, luce naturale controllata. Opere tradizionali di dimensioni medie, sala fisica dichiarata e prospettiva reale.
- **GAL02 | Galleria contemporanea neutra**: pareti neutre, illuminazione da museo senza faretti teatrali, finiture sobrie. Dipinti e opere moderne.
- **GAL03 | Gabinetto delle piccole opere**: sala intima con rapporto porta-parete leggibile, camera ravvicinabile. Pannelli piccoli, stampe e miniature SENZA ingrandirli sul muro.
- **GAL04 | Sala monumentale**: architettura più ampia, distanza di osservazione e campo visivo adeguati. Tele grandi, polittici e opere di grande formato.
- **GAL05 | Sala storica dai toni profondi**: pittura murale scura, luci coerenti e materiali non finti. Opere storiche adatte alla galleria scura.
Le sale sono **tipologie scenografiche**, mai fotografie del museo che conserva l'opera salvo prova. Vanno dotate di veri asset 3D/fotografici licenziati, geometria, texture, sorgente/hash, illuminazione e percorso camera. Non usare una singola immagine disegnata come surrogato di una vera sala. Per ogni preset: provino reale MP4 di avvicinamento e ritorno + QA sui fotogrammi. Catalogare versione, licenza, sorgenti, hash e approvazione umana.

## Cinque famiglie di cornici CANDIDATE (non cornici autentiche universali)
- **FRA01 | Dorata storica sobria**: profilo e intaglio da verificare sullo specifico esemplare.
- **FRA02 | Legno scuro tradizionale**: spessore, modanatura e venatura coerenti.
- **FRA03 | Legno naturale classico**: montatura discreta per lavori compatibili.
- **FRA04 | Profilo nero o bronzo minimale**: solo se appropriato e documentabile/approvato come alternativa.
- **FRA05 | Cornice per opera su carta, con eventuale passe-partout**: per stampe e disegni, soltanto quando appropriata al supporto e alla documentazione.
**Prima di scegliere un preset cercare la cornice REALE di QUEL preciso quadro (regola V80).** Se documentata replicarla: la libreria offre componenti/costruzione, non licenza di sostituire il profilo autentico. Se sconosciuta, `frame_status=unverified`, bloccare consegna finale finché il proprietario non approva esplicitamente una montatura alternativa per quell'opera. Mai presentare FRA01–FRA05 come «originale del museo».

## Regola fisica fondamentale: scala dimensionale in metri
- Per ogni esemplare esigere larghezza/altezza **della superficie dell'opera in cm con fonte**. Conversione `w_m=w_cm/100`; `h_m=h_cm/100`. Queste dimensioni definiscono il piano tela nel mondo 3D, non il ritaglio video. Misure esterne cornice separate.
- La scena deve avere un sistema metrico unico per muri, porte, pavimento, panca, camera e cornice; nessuna riscalatura di tela ad hoc per riempire il video. Un quadro da 35 cm rimane tale; uno da 3 m richiede spazio reale.
- Campo di vista e distanza focale della camera variano per rendere leggibile l'opera: **si muove il visitatore/camera, non si cambia la scala del dipinto**. Nella vista iniziale includere un riferimento architettonico di scala (altezza porta/muro oppure arredo realmente misurato); evitare figure umane inventate.
- Identico esemplare, dimensioni, sala, luce, cornice e coordinate in ingresso/uscita. La cornice esce dal campo per avanzamento prospettico, NON mediante dissolvenza; nei dettagli non compare.

## Selezione per opera (dossier obbligatorio)
`artwork_id`, `accession`, `source_url`, `image_sha256`, `width_cm`, `height_cm`, `dimensions_source`, `room_preset_id`, `room_preset_version`, `room_asset_sha256`, `room_license`, `room_is_actual_holding_museum`, `room_is_reconstruction`, `frame_status`, `frame_source_url`, `frame_preset_or_bespoke_id`, `frame_actual_or_estimated_outer_cm`, `frame_rights`, `camera_world_scale_m`, `reference_scale_object_m`, `intro_outro_mp4_sha256`, `visual_review_status`, `user_or_authorized_reviewer_approval`.
Se un asset è mancante, `room_preset_id` da solo NON è prova che sia realizzato né idoneo.

## Gate di qualità a tre livelli, con rifiuto automatico dell'abbassamento qualità
1. **Preflight fonti/scalatura:** dimensioni con fonte, ricerca cornice autentica, sala/texture/licenza e ID+versione di preset `approved`. Se preset non esiste o è candidato, **STOP finale**.
2. **Provino in movimento:** montare ingresso→dipinto→uscita in un vero MP4 (non un'immagine). Confrontare con Cyclops V46 e Hiroshige V46/V57; ispezionare bordi/ombre/materiali/scala/prospettiva e movimenti intermedi. Rifiutare regressione o ripetizioni visive evidenti.
3. **Consegna:** solo dopo review estetica del video e QA integrità, permessi e file reali. `museum_status=rendered_needs_review` e `museum_approved=false` fino ad approvazione effettiva. Nessun Gold/pubblicazione automatica.

## Regole operative
- Formato 4×1 invariato: Critico Standard, Critico Museum, Cinema Standard, Cinema Museum. Conservare voci identiche dei Critico; non rovinare gli Standard già buoni.
- Scegliere fra i preset approvati in funzione dell'opera; **niente accoppiamenti arbitrari** fra cornice e pittura, niente cinque scene rigide ripetute senza variazione di camera/luce e composizione.
- Un cambiamento di renderer NON può rimpiazzare un preset approvato con fallback illustrato: **fail closed**, niente video dichiarato definitivo.
- Prima fase: realizzare e visionare i 5 provini sala e 5 campioni cornice in abbinamenti significativi. Registrare ID, versioni, hash e feedback per evitare di ridiscutere sempre gli stessi difetti. Eventuali correzioni non alterano i master già approvati.
- Nessuna spesa esterna, nessuna generazione nuova e nessuna approvazione inventata: V119 è per ora **una specifica di produzione e di accettazione**, non un pacchetto di 10 asset già pronti.

Compatibilità: V46, V57, V73, V80, V118, V25 restano in vigore e prevalgono su scorciatoie visive.
