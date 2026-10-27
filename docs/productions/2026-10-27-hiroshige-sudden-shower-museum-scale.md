# ArtVision — Hiroshige, Sudden Shower — Museum Immersion (27 ottobre 2026)

## Stato e consegna realmente verificata
**rendered_needs_review**: nuovo montaggio dedicato a una xilografia di Hiroshige, opera già comparsa in una precedente collection (*The Shape of the Wind*) ma mai sotto questa regia autonoma nel catalogo controllato. Non promuovere automaticamente a Gold Master senza feedback umano sul film esatto.

- **MP4 Android verificato e scaricabile:** https://drive.google.com/file/d/14X8_TObXEijGlBg8HuyR6ITTlPjJk0dA/view?usp=drivesdk
- **Kit completo verificato (MP4, JPEG, 4 post italiani, fonte, scala, storyboard, ricetta, QA):** https://drive.google.com/file/d/1l6FBjb3HGDTriMuhnna8UKRSocTLvBBU/view?usp=drivesdk
- MP4: **64,7083 s**, 1080×1920, 24 fps, H.264/AAC, **66.691.253 byte**, SHA256 `4c652f526b91bb22332055e0484f3a616d1168ae85599bb7e81da197ce29356c`.
- ZIP: **70.670.800 byte**, **16 materiali**, test integrità ZIP superato. Google Drive verificato tramite rilettura dei metadati, dimensioni corrispondenti.
- Master di lavorazione più grande preservato localmente (108.862.208 byte; SHA256 `b4184e888c6f68d95509e01cb6b53e0b4b32291d6f7f7fc8b1797bd660dc8070`). L'upload Google Drive del master era bloccato da limite file_too_large: nessun retry identico; consegnata copia ottimizzata a **uguale risoluzione 1080×1920**.

## Regola nuova, dimensione fisica reale
Indicazione esplicita dell'utente: se l'opera è piccola deve apparire piccola in sala; se è 8×10 m deve apparire enorme con prospettiva e stanza proporzionate. Regola permanente registrata in `docs/REGOLE_ATTIVE.md` e in `config/editorial_rules.json > museum_immersion_scale`, trasmessa alla routine esistente ArtVision ogni 3 ore.

**Opera:** *Sudden Shower over Shin-Ōhashi Bridge and Atake*, Utagawa Hiroshige (1857); disegno di una xilografia in più impressioni. **Esemplari museali comparabili**:
- Cleveland Museum of Art 1921.318: **35,3 × 23,2 cm**, https://www.clevelandart.org/art/1921.318
- Metropolitan Museum of Art JP644: **36,5 × 24,3 cm**, https://www.metmuseum.org/art/collection/search/37094
La fotografia usata proviene dall'archivio ArtVision, originariamente Commons (https://commons.wikimedia.org/wiki/File:Hiroshige,_Sudden_shower_over_Shin-%C5%8Chashi_bridge_and_Atake,_1857.jpg) e può rappresentare un'altra impressione. NON attribuire la foto specificamente a Cleveland né la sala illustrata a un museo reale.

La scena generata mostra una persona adulta accanto a una **piccola cornice** inserita fisicamente in una parete museale; il quadro si ingrandisce solo con il movimento della telecamera verso di esso. La cornice contiene l'opera dietro i bordi e con ombre di contatto; non è identificata come una cornice storica verificata.

## Regia
Cinema V6 senza parlato. Copertina e frame iniziale: titolo inglese completo e artista con grafica ArtVision (pannello scuro, serif e linea dorata). Apertura visita museo 8s; le scene interne si soffermano sulla pioggia a linee sottili, iscrizioni, barca lontana, passanti e struttura del ponte; ritorno nella stessa sala per 8s. Durata totale 64,7s. Niente ghosting, sovrapposizione tra opere, riempimento a pixel replicati o zoom oltre i limiti del file sorgente. 14 scene centrali su artwork autentico, non generato.

Raccordi al primo e ultimo cambio museo/arte controllati su frame non ricompresso: differenza media rispettivamente **2,87/255** e **0,73/255**, dopo correzione di un precedente scarto di circa 5 pixel. Copertina verificata e video decodificato integralmente FFmpeg senza errori. QA visivo su 24 fotogrammi di video finale, incluso bordi e 11 campioni delle sequenze centrali: nessuna striscia replicate rilevata. Diritti, storyboard, ricerca di 3 candidati, ricetta, QA, quattro post V28 originali sono nel kit.

## Fonte e musica
- File originale xilografia 1920×2909, SHA256 `c79e85e2635842dc18d77eac8d64d4a7002905c8cb811d570354003afa05520d`; fotografa riproduzione di opera di pubblico dominio, verifiche territoriali PD-Art prima di pubblicazione commerciale.
- Registrazione musicale originale da archivio **“Echoes of Time” — Kevin MacLeod**, SHA256 `be9740a15e0395d4e763d8ea5f8691ee2422924f44a03b12c329ecc4a59cc2a8`, licenza **CC BY 4.0**, https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300029. Estratto, volume ridotto, fades; attribuita nei quattro post.
- Sala e visitatore **ricostruzione illustrativa**, non visita autentica a Cleveland o Met. **Nessun credito video a pagamento** e nessuna pubblicazione social.

## Autocritica e prossime iterazioni
1. La stanza è una scena illustrativa animata in 2.5D, non una ripresa tridimensionale con parallax misurato: per realism ancora maggiore servono camera/scene 3D o riprese reali autorizzate.
2. La stampa rappresenta un disegno multiesemplare: per precisione museologica assoluta scegliere in futuro file e misure del **medesimo oggetto inventariato**, inclusa la cornice vera quando documentata.
3. La qualità del ritmo e della musica richiede visione e feedback dell'utente sul MP4 esatto; non si considera automaticamente pronta la pubblicazione solo perché i controlli tecnici sono passati.
