# LA STORIA RIVIVE V74 — RIPRISTINO DELL'EFFETTO DI RIFERIMENTO (29/10/2026)

## Decisione prioritaria dell'utente
**V73 Coney Island è BOCCIATO rispetto alla regia degli esempi, anche se l'MP4 è un video autentico, possiede audio e ha superato la QA tecnica.** La sua colorizzazione progressiva continua NON riproduce l'effetto scelto dall'utente. Non usarlo come gold master né come modello per i nuovi video.

**I riferimenti user-approved sono i video 43054.mp4 e 43056.mp4 (e 43055.mp4 già esaminato precedentemente).** Sono forniti dall'utente come esempi di estetica e regia, NON come media con licenza di riuso da rimontare. NON includerli nei nuovi video.

### Effetto obbligatorio predefinito: VERO VIDEO → FOTO GENERATIVA FERMA
Per ciascun soggetto:
1. **Breve clip storica realmente filmata in B/N**, non una foto animata digitalmente. Sorgente di archivio originale PD/CC0 verificata, file autenticato e timecode. Selezionare un'azione significativa (occhi, gesto, veicolo, acqua, persone) e alcune scene *davvero distinte*.
2. **Ultimo frame esatto della clip B/N** (non frame simile, non altra inquadratura) arrestato senza salto visivo.
3. **Trasformare QUEL frame in una nuova fotografia AI image-to-image**, a colori naturali e con un salto fotografico evidente di nitidezza, profondità, dettagli e materiali. Unico input effettivo = quel frame reale (possibili frame vicini come guide di fedeltà). DDColor da solo, LUT, seppia, upscale geometrico e color grading su fotogrammi in movimento NON bastano.
4. **Transizione rapidissima e armoniosa** dal frame B/N congelato alla stessa scena ricostruita e colorata, tipicamente 0,18–0,4 s. La scena deve rimanere rigorosamente corrispondente; nessun nuovo personaggio, oggetto, volto, gesto o architettura inventata di nascosto.
5. **Fotografia finale ferma**, o con micro-movimento digitale moderato dove la regia lo giustifica, non la prosecuzione del moto originale. La fotografia deve restare abbastanza visibile da permettere di guardare i dettagli.
6. Tagliare alla **successiva vera clip B/N DIFFERENTE** e ripetere. Ritmo variabile, apertura potente nei primi 1–3 secondi, audio e titolo discreto solo LUOGO/ANNO e fonte, senza "prima/dopo" sul video.

### Tempi MISURATI dai due MP4 dell'utente
- **43054.mp4 — variante lenta**, 23,73s 720x1280 a 30fps: 6 segmenti fotografici a colori quasi immobili, tipicamente circa 2s; blocchi colore 2,10–4,13s; 6,07–8,07s; 10,03–12,17s; 14,07–16,13s; 18,00–20,10s; 22,00–23,73s.
- **43056.mp4 — variante veloce**, 20,97s 720x1280 a 30fps: 9 blocchi di foto a colori da circa 0,9s, nei primi ~16,4s; lieve micro-movimento fotografico ammesso.
- **Coney Island V73 — FALLITO**, 17,58s: movimento continuo durante la colorizzazione; nessuna sequenza di photo-freeze verificata. Non tentare di aggiustarlo con una LUT o un filtro cromatico.

### Regola sulla qualità della ricostruzione
- **Sorgente sfocata/sgranata:** possibile ricostruzione fotografica più profonda, ma deve restare plausibile, non alterare la scena e dichiarare le parti interpretative nei metadati.
- **Sorgente nitida/viso leggibile:** maggiore *fedeltà obbligatoria*: occhi, pelle, capelli, mani, abiti, insegne, edifici devono corrispondere meglio, con minimo rischio di allucinazione.
- Preferire **3 fotografie veramente straordinarie a 8 mediocre**, ma non presentare duplicati dello stesso shot come scene differenti.
- L'estetica di una foto fissa moderna e iper-realistica deve essere evidente: il semplice file esportato a 1080 o 4K non è prova di dettaglio ottico.

### Distinzione dall'altro preset sperimentale
V72 «Cinema continuo WOW» resta **un'alternativa, esplicitamente richiesta**, non il comportamento predefinito. Quando l'utente chiede semplicemente "creami un altro video", usare il preset *video → freeze → fotografia AI*, non uno switch verso colorizzazione continua senza approvazione.

### Gate tecnici e creativi
1. Prima di scaricare un modello/call gratuita, esaminare origine e movimento autentico, diritti, qualità del crop, possibili inquadrature.
2. Prima del render finale: foto AI realmente prodotta, file SHA e risoluzione verificati; confronto affiancato con esatto source frame; rifiutare bassa cromia, texture pittorica, alterazioni di persone o oggetti.
3. Il montaggio completo deve superare **src/storia_rivive_v74_effect_gate.py** (blocchi foto a colori relativamente statici preceduti da moto B/N; impiegare `--min-cycles` appropriato). Il gate numerico non prova né fedeltà dei volti né qualità artistica, che richiede revisione visiva.
4. MP4 H264/AAC con musica o sound design originale; niente watermark; ZIP, copertina, fonti, 4 post; prova decodifica completa e download Android; backup GitHub Release e sito privato verificato, senza dichiarare upload non effettuato.
5. **Se non c'è fotografia generativa AI sufficientemente bella e fedele: non consegnare falsamente un "video completato"**. Segnala quale scena e perché è in stato FAILED_ART_REVIEW.

## Retrospettiva e prevenzione
- Errore precedente: V73 ha seguito letteralmente il piano di colorizzazione continua invece del preset approvato 43054/43056, creando un prodotto formalmente valido ma fuori formato.
- Correzione: i workflow per La Storia Rivive DEVONO dichiarare `editorial_preset: freeze_ai_photo_reference_43054_43056` oppure `continuous_motion_color_experimental`. Default = primo.
- Non reinterpretare un feedback sulla qualità fotografica come consenso a sostituire l'effetto video→foto.

**Non è necessario proporre all'utente di ripetere le regole: sono tutte descritte qui e nei documenti V61/V64/V68/V69.**

## V75 — Feedback positivo e perfezionamento del formato (29/10/2026)

**L'utente APPROVA l'effetto realizzato in Parigi V74**: ripresa storica autentica in bianco e nero con movimento → blocco dello stesso fotogramma → fotografia AI restaurata a colori, fotorealistica e FERMA → successiva ripresa autentica. Non cambiare questo effetto né reinterpretarlo come colorizzazione in movimento. V74 è ora riferimento positivo per la regia, pur restando migliorabile nella qualità fotografica.

### Due modifiche richieste e approvate
1. **Durata leggermente maggiore rispetto a Parigi V74 (14,4 s).** Impostazione editoriale orientativa per i prossimi episodi: **22–28 secondi**, variabile secondo l'azione e la qualità delle scene, senza allungare artificialmente singoli fotogrammi o riciclare riprese. In genere 4–6 trasformazioni davvero diverse e significative; qualità prevale sul numero. Se esistono solo tre foto eccezionali, non riempire con materiale mediocre. Il video deve iniziare a incuriosire entro i primi 1–3 s.
2. **Un bel titolo iniziale con anno ben leggibile**, e località corretta. Titolo cinematografico/museale elegante, curato nella tipografia e nelle proporzioni, ad esempio `PARIGI · 1898` / `CONEY ISLAND · 1903`, eventuale credito archivio piccolo e discreto. Idealmente appare nei primi **0,8–1,5 s sopra una vera ripresa in movimento** (senza cartello nero fermo o attesa vuota), poi si ritira per lasciare spazio alle scene. Niente «prima/dopo», diciture tecniche o paragrafi; niente voce per questo format. Verificare il periodo esatto sulle fonti, non inventare l'anno.

### Indicazioni per montaggio e QA
- Eseguire il formato **V74 approvato**, il titolo non deve coprire i volti, l'azione o la trasformazione né appesantire la prima inquadratura.
- I blocchi fotografici devono essere abbastanza lunghi da far ammirare i dettagli (preferibilmente 1,5–2,5 s, con flessibilità artistica).
- Allungare l'episodio aggiungendo scene vere, soggetti WOW e fotografie AI approvate, **non** mediante zoom/fermi troppo lunghi o duplicati.
- Esportare e verificare MP4/ZIP scaricabili, titoli, musica originale e controllo artistico. Backup GitHub diretto e sito privato soltanto se effettivamente caricati/verificati.
- Queste sono preferenze permanenti per i **prossimi episodi**. Non dichiarare di aver già rifatto video precedenti senza averlo eseguito.

**Stato:** effetto V74 APPROVATO dall'utente; introduzione/ritmo V75 miglioramenti richiesti per nuove produzioni.
