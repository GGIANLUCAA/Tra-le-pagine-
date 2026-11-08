# ArtVision LAB — PH02: provino MP4 sulla parete di fondo (8 novembre 2026)

**Tipo:** esperimento indipendente **2,5D** di geometria, cornice provvisoria e zoom fotografico. **NON è un video Museum ArtVision pronto, né un nuovo slot 4×1.** Il laboratorio non modifica alcuna coda, automazione, workflow di produzione, master o licenza.

## Perché serve
Il precedente test della *The Magic Circle* (Tate N01572) nella sala fotografata al Museum Barberini aveva un ostacolo: la porta al centro della parete di fondo. Una precedente prova sulla **parete laterale** mostrava un dipinto troppo schiacciato dalla prospettiva. Questo test ipotizza invece la **porzione destra della parete di fondo**, senza coprire porta, finestre, pavimento o allestimenti originali.

## Ingressi reali e loro limiti
- **Foto vera di una sala VUOTA** del Museo Barberini a Potsdam, fotografo **Daniel Naber** (28/11/2016), [pagina Wikimedia](https://commons.wikimedia.org/wiki/File:Museum_Barberini_Innenraum_leer.jpg), **CC BY 4.0; fotografia modificata per il provino**. **NON raffigura una sala Tate Britain e NON mostra una reale esposizione dell'opera.**
- Originale fotografico recuperato dall'artifact V120, poi conservato nella Libreria privata `/ArtVision/Museum_Lab/V120_RESEARCH_SOURCES/GAL02_PHOTOGRAPH.jpg`. **3648×2736**, SHA-256 **`ea95335ef66afa225351e1dd423c49d5e84aeb15574e97b965fa25c1d5b91db2`**. Lo script rifiuta il render se questo SHA cambia.
- Il preflight V209, per il **nuovo download da Commons**, ha trovato hash **`4eccd18f1fc714305902369d8c2b118f763fc6dec129b89820a3d20242c40e64`**. Si tratta di byte diversi: la causa non è stata ancora dimostrata. NON sostituire in silenzio il SHA nel workflow di produzione. Per questo provino si usa **solo la copia V120 verificata e conservata**.
- Il dipinto utilizzato nel filmato è un **proxy ricavato da un precedente studio geometrico** `MAGIC_CIRCLE_SIDE_WALL_GEOMETRY_ONLY.jpg`, recuperato dalla Libreria privata, non un JPEG della pittura indipendentemente autenticato e licenziato. L'opera antica è PD secondo Commons, ma restano le verifiche sul **preciso file digitale** e sulle eventuali restrizioni territoriali Tate. **Non pubblicare.**
- La cornice scura è un **modello provvisorio per il test**, non una cornice storica documentata dell'esemplare. Materiali/ombre sono approssimativi.

## Geometria di stima (non misure reali della sala)
- Opera Tate *The Magic Circle* (1886), inv. N01572, **altezza 182,9 cm, larghezza 127 cm**: fonte [Tate Britain](https://www.tate.org.uk/art/artworks/waterhouse-the-magic-circle-n01572).
- Per stimare la scala dalla fotografia, assunta porta **1,05×2,10 m** (NON misurata sul posto). Doppia stima indipendente pixel/m sui due lati, ridotta a un unico rapporto isotropico ~106,905 px/m per NON stirare il dipinto.
- Su foto di lavoro 1408×1056, zona libera di parete `(804,350)–(1040,609)`; vano porta `(683,394)–(799,611)`; **tela `(853,379)–(989,575)`**; cornice di prova `(846,372)–(996,582)`.
- Simulazione cornice esterna **1,41 × 1,969 m** (70 mm aggiuntivi per lato), solo per test; non è la misura effettiva della cornice Tate.
- **Sovrapposizione con porta: 0 px²**; distanza dal bordo destro porta **47 px**; margine a destra **44 px**. Rapporto aspetto mostrato **136/196 ≈ 0,6939**, contro vero **127/182,9 ≈ 0,6944**. I 4 lati della cornice stanno nella zona stimata di muro, pur con margini stretti sopra e sotto.
- Limite: una foto singola non consente calibrazione certa di camera, metratura, materiali, profondità o parallax; le misure sono **ipotesi controllabili**, non prove di scala esatta.

## MP4 vero di prova e QA tecnica
- File: `PH02_MAGIC_CIRCLE_BACK_WALL_V1_2P5D_LAB_ONLY.mp4`.
- **12,000 secondi**, **720×1280**, **20 fps**, **H.264, senza audio**, 2.372.509 byte, SHA-256 **`3159967f77d2e3f9e5c98512c9dfc6fca50583f856a1798e7dfda37b2c87ed01`**.
- Generazione offline mediante OpenCV e FFmpeg: zoom ottico simulato, progressione di camera sul dipinto, sua cornice fuori campo nel dettaglio, successivo ritorno alla stessa sala. **Nessuna camera 3D vera e nessuna sintesi Vidu/AI**.
- `ffprobe` conferma proprietà e durata; **`ffmpeg -v error -xerror ... -f null -` decodifica integrale PASS**.
- `PH02_BACK_WALL_CAMERA_8_FRAMES_QA.jpg` mostra 8 fotogrammi decodificati a istanti diversi; ispezione preliminare del filmato, NON review umana integrale e NON V25.
- ZIP completo `ARTVISION_PH02_MAGIC_CIRCLE_LAB_REVIEW_V1.zip` contiene **8 file**: MP4, inquadratura di partenza, 8 frame QA, JSON geometria, README/attribuzioni, script riproducibile e due JPEG sorgenti (foto sala reale e proxy prova). **4.422.398 byte**, SHA-256 **`d604f793fb8faa1e9e28dc23654659e62817699b68b88d5bb28cfc4a10e5b757`**; ZIP CRC PASS.

## Backup fisico e readback, non solo manifesto
Archivio privato: `/ArtVision/Museum_Lab/PH02_BACK_WALL_V1_REVIEW_20261108/`.

- MP4 Library file ID `libfile_242b854b99fc8191ae5f1b4666781a2b` e ZIP `libfile_f28f99c03d7c81919733c6ef68c9e174`.
- **Entrambi riscaricati fisicamente** con `files.materialize`: 2/2 dimensioni e SHA-256 identici alla generazione. ZIP del readback CRC PASS.
- Nulla è stato caricato nel sito pubblico, nello storage R2, su social o nella coda delle 40 varianti.

## Esito e prossima azione
**Esito tecnico limitato:** la parete di fondo libera **può accogliere un ingombro plausibile** dell'opera, senza bloccare la porta e senza alterare le dimensioni relative del quadro. La variante Museum **resta BLOCCATA per uso finale**: (1) immagine autentica dell'esatto quadro + diritti del file, (2) cornice storica documentata oppure modello neutro espressamente approvato, (3) camera reale 3D con prospettiva/parallax/occlusioni coerenti, (4) scala fisica confermata da un riferimento misurato, (5) QA estetico integrale e approvazione proprietario.

**Non promuovere V119 a preset pronto.** L'owner può leggere l'esito come ipotesi e base per un successivo provino 3D verificabile, non come nuovo MP4 finale.

## Verifica complementare sulla differenza dei JPEG
Il file V120 effettivamente letto ha **1.431.648 byte**, dimensioni **3.648×2.736**, **zero campi EXIF** (analisi `Pillow.Image.getexif()`), pur essendo un JPEG valido. La scheda Wikimedia dell'immagine indica per il proprio **file originale attuale circa 1,72 MB** e metadata della Canon PowerShot G12: [pagina della foto](https://commons.wikimedia.org/wiki/File:Museum_Barberini_Innenraum_leer.jpg). Quindi la copia V120 è **verosimilmente una derivazione ricompressa o senza metadati**, NON da chiamare byte-identica all'originale Wikimedia. La differenza di SHA V209 è pertanto comprensibile ma **non spiegata in modo definitivo**, perché non abbiamo i pixel della versione corrente per una comparazione diretta: servono confronto visivo/pixel e registrazione separata di `original_commons_sha256` e `derived_v120_sha256`. Il provino resta riproducibile dalla **copia derivata V120 con hash fissato**, senza cambiare il preflight ufficiale.
