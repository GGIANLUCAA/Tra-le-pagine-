# La Storia Rivive — CHINA c. 1928 · Esito V107 e regole anti-regressione

Data 30 ottobre 2026. Questo documento registra un risultato VIDEO reale e i limiti da non dimenticare nelle produzioni successive.

## Video riproducibile
- V104 via workflow `.github/workflows/storia-china-1928-v104-render.yml`: filmato storico autentico, 4 fermi-immmagine colorizzati con modello DDColor + super-risoluzione appresa RealESRGAN, quinto segmento con movimento reale dell'originale colorizzato semanticamente. Esportazione 1080×1920, 30 fps, audio AAC, H264, durata **20,8 s**, verificato con decodifica FFmpeg. Fonte **720×480**, *non* native 4K.
- Review reale del MP4 ha trovato forti dominanti rosso/arancio e timecode dell'archivio ancora visibile. Non considerare accettabile il solo passaggio tecnico dei controlli di correlazione.
- V105 correzione di crop geometrico sul video reale: rimossi bordo superiore e timecode in basso tramite crop (non inpainting e non nuovi oggetti) e attenuata la saturazione eccessiva.
- V106 attenuazione cromatica ulteriore basata sulla scena (specie 1, 3, e sequenza finale); V107 normalizzazione audio fino a volume medio -18,8 dB e massimo -8,1 dB (misurazione volumedetect), file completo di durata 20,8s, MP4 H264/AAC, verificato con FFmpeg, SHA256 del video `c571aed5f5d20b8a06f1e4c7504a90815d94f42001743577e4cfd2de433a649a` riferito a V106 **prima** della normalizzazione audio; V107 ha SHA diverso e viene riportato nel QA allegato all'artefatto della conversazione.

## Non mentire sullo stato
- **V107 è un MP4 completo come file e montaggio, ma non è il master 4+1 approvato dall'utente**: nessuna clip Vidu effettiva è presente.
- Le quattro immagini sono restauri AI di colore e dettaglio appreso (DDColor + RealESRGAN), **non** vere rigenerazioni diffusion I2I con volti moderni source-locked del livello V98. Non dichiarare qualità 4K apparente quando i volti restano sfocati per i pochi pixel originali.
- Il quinto segmento è **solo la pellicola storica originale in movimento colorizzata con AI**, non un'animazione Vidu. Non chiamarlo Vidu, non sostituirlo con una clip di filmati diversi.
- Il free Space Finegrain ha restituito in fase V103 immagini perlopiù monocromatiche e poi ZeroGPU quota esaurita. Evitare nuove chiamate con quota nulla; non attivare piani a pagamento o addebiti API senza autorizzazione specifica.
- Gateway Vidu `balance` GET senza spesa ha funzionato, ma il sistema richiede preventivo e specifica autorizzazione per un nuovo POST; **non falsificare approvazioni umane**.
- Fonte Commons `China and the Chinese, 1920s - Travelfilmarchive.webm` con PD dichiarato USA e Cina; **la verifica dei diritti italiani resta pendente**, non pubblicare automaticamente il video sui social o nell'archivio pubblico.

## Regole future obbligatorie
1. Se il crop verticale del raster nativo lascia meno di circa 400–500 px di larghezza utile o il volto è privo di dettaglio, classificare la fonte `NEEDS_BETTER_SOURCE`, non promettere foto equivalenti a 4K.
2. Analizzare watermark e timecode *prima* di selezionare le scene; scartare clip con sovrimpressioni invasive, o usare esclusivamente crop reali coerenti. Niente scritte archivistiche rimaste nel video.
3. Freeze *esattamente* sull'ultimo fotogramma del segmento filmico effettivamente inserito nel MP4; i timecode FFmpeg del film possono differire anche di 1–2 fotogrammi. Misurare correlazione e SHA.
4. Restauro fotografico reale source-locked e confronto visivo foto/originale + doppio controllo dopo montaggio; il gate tecnico cromatico non garantisce fedeltà storica.
5. Evitare gradi di saturazione e dominanti rosse irreali, posterizzazione e colori psichedelici. Visionare realmente le scene a colori e verificare il full MP4 e audio.
6. Per un episodio del formato approvato rimangono **quattro veri restauri fotografici di alta qualità + una clip Vidu vera e verificata**, con gate V91/V94/V96/V99 e riferimento V98. Se non raggiunti, fornire soltanto una revisione chiaramente etichettata.
7. Consegna: sempre MP4 realmente generato e verificato, cover, descrizioni social, fonti, ZIP; link reali. Non produrre foto o copertine come surrogato della richiesta VIDEO.
