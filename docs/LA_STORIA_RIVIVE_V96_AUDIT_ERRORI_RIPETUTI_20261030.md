# La Storia Rivive — V96: autopsia degli errori ripetuti e blocco permanente (30 ottobre 2026)

**Evidenze dirette realmente esaminate**
- Schermata utente `44371.jpg` (864×1536): Bombay 1929, venditore con turbante, frutta e altre persone, maxi targa opaca in basso.
- Video utente `44486.mp4` (720×1280, 30 fps, 29,0667 s, H.264/AAC): il **vero** master New York 1911 V95.1, SHA e durata coerenti con l'MP4 della GitHub Release.
- Riferimenti qualitativi originali forniti: `facebook_20261028_142708.mp4` (23,733 s), `142737.mp4` (20,233 s) e `142900.mp4` (20,967 s); tutti 720×1280. Questi esempi sono SOLO riferimenti, NON asset da riutilizzare.
- Ripetuto punto di fallimento verificato nel codice: `src/storia_v83_new_york_1911.py`, `tools/storia_new_york_1911_v95_real_vidu_once.py`, workflow precedente `.github/workflows/storia-new-york-1911-v95.yml`.

## Difetto 1: fotografie colorate anziché fotografie moderne restaurate
Il renderer V83 produce `PHOTO_AI_*.png` usando `DDColor`, una regolazione di saturazione (anche forte), CLAHE e sharpening. Questi elaborano colore e nitidezza, ma **NON creano necessariamente un vero restauro image-to-image dei dettagli facciali**. La prima foto del venditore Bombay presenta pelle, occhi, bocca e tessuti artificiali o troppo levigati; colori degli oggetti e dei vestiti poco credibili. La screenshot non ha la nitidezza dei volti dei video riferimento. Il codice V92 Bombay fa analogamente solo chroma neurale source-locked.

**Correzione vincolante:** per i quattro hold fotografici usare effettivamente restauri image-to-image di un fotogramma HD e confrontare visivamente con frames contigui prima e dopo, verificando occhi, pori, capelli, età, abiti, oggetti, numeri di persone e identità. DDColor da solo è **preparazione**, non scena fotografica approvata. Non inventare volti a partire da una fonte troppo piccola: cambiare inquadratura se la fonte non supporta fedeltà e dettaglio. Due candidate quando disponibile.

## Difetto 2: Vidu inserito senza corrispondere alla stessa ripresa originale
Il codice NY V95 fa `cut=12.0` e inserisce lì cinque secondi generati da un **fotogramma della pellicola originale a t=325.0 s**, diverso dall'inquadratura effettivamente presente nel master a 11.9 s. Si passa dal portone con uomini al traffico arancione di una strada: non è la continuazione del fotogramma fermato. 
- Al confine **11.97 → 12.03 s**: correlazione di luminanza circa **0,70**, differenza luminanza media ~43/255 su thumbnails 144×256.
- Al confine **17.07 → 17.13 s**: correlazione circa **0,40**, differenza media ~70/255.
Questi sono tagli tra riprese differenti, NON continuità del restauro. Le scene reali possono essere montate con stacchi professionali, ma l'ingresso **dentro la propria sequenza Vidu** deve partire dalla stessa posa e composizione sorgente.

**Correzione:** scegliere *5 vere riprese distinte*; la 5ª ha 0.6–1.5 s di pellicola originale B/N in movimento, freeze sul **fotogramma sorgente verificato** → stesso frame come prima immagine del clip Vidu, con ripresa realmente a colori in movimento circa 5s, colore entro 1.15s. La 5ª inquadratura entra solo al suo normale inizio di capitolo, mai al secondo arbitrario 12.0 dentro una scena diversa.

## Difetto 3: tonalità e ritmi inadatti ai riferimenti
Il master V95.1 mostra 4 hold fotografici di circa **3.2–4 secondi** ciascuno (la scena 4 fino a 29 s), prevalentemente immobili. Per una cinquantina di frame adiacenti alla fine di ciascuna scena si osserva movimento medio quasi nullo (~0.00–0.05 livelli di luminanza fra immagini distanti 0.5 s). Esempi: 3–5.5, 9–11.5, 20–22.5, 26–28.5. I video riferimento hanno reveal più rapido e immagini con dettagli di persone chiari, non lunghi freeze che non mostrano abbastanza qualità.
La sequenza Vidu del video NY ha saturazione mediana HSV ~**109–128** nei secondi 13–16, mentre le fotografie circostanti vanno spesso da **14 a 31**. Il risultato è una colorazione arancio molto più intensa e un'immagine quasi stilisticamente estranea alle quattro fotografie.

**Correzione:** pianificare prima i cinque capitoli per effettiva azione/emozione. Di solito B/N 0,6–1,8 s; reveal 0,2–0,7 s; hold foto 1,2–2,4 s (fino a 3,05 solo giustificato); quinta scena Vidu ~5s, movimento dopo reveal ≥3,5s. Non usare il numero 25 s o 5 scene come stampino universale fuori dal preset 4+1. Palette naturale e simile tra foto e Vidu, no arancio dominante o desaturazione che rende due restauri quasi indistinguibili dal B/N.

## Difetto 4: titoli che nascondono il contenuto
Nella foto `44371.jpg` la fascia nera Bombay 1929 occupa circa 190–200 px verticali su 1536 (≈12–13% dell'altezza) e copre parte dell'area espositiva della merce. Il problema è particolarmente grave nei video su persone, mercati, mani e oggetti. Vietati pannelli opachi che coprono soggetti importanti. Titolo inglese città/anno elegante, piccolo e preferibilmente sovrapposto in zona libera, solo per l'apertura, con buona leggibilità e opacità moderata.

## Difetto 5: errore del QA esplicitamente ignorato
Nel workflow NY V95 precedente, il renderer V83 aveva lanciato `NOT_THE_USER_APPROVED_EFFECT` perché riconosceva **solo 2 dei 4 cicli di effetti**; il workflow controllava quel testo e proseguiva comunque alla generazione e pubblicazione di una prerelease, dopo avere rinominato il master bocciato. Il QA vero non era invocato prima della release: passavano `ffmpeg` decodificabile e CRC dello ZIP. La versione V95.1 ha corretto **solo** la colorazione del clip Vidu a 12–17 s; non ha riparato gli altri elementi strutturali/fotografici. **Non chiamarla prodotto finito**.

**Correzioni già applicate al repository**
1. `src/storia_rivive_v96_guard.py`: nuovo gate V96 richiede 4 reali source-film→foto image-to-image e 1 sola vera clip Vidu su 5ª fonte, timeline collegata, hold motivati, titolo non coprente, QA semantico/volti, identità di sorgente, palette, audio/diritti, revisione umana: tutti predefiniti **non approvati** fino a prova concreta.
2. `tests/test_storia_rivive_v96_guard.py`: **12 test** che simulano precisamente errori sopra, tutti passati.
3. `.github/workflows/storia-v96-regression-audit.yml`: Action gratuita legge il *vero MP4 V95.1* e verifica che il gate lo respinga come finale. Risultato atteso: **REJECT** con motivazione, non rilascio fittizio.
4. `src/storia_rivive_final_gate_v91.py`: per nuovi filmati storici richiesti nel preset 4classiche+1Vidu integra il gate V96 oltre a V94; non viene compromesso ArtVision 4×1.
5. `.github/workflows/storia-new-york-1911-v95.yml`: **DISABILITATO** per prevenire un riavvio a pagamento e rimosso l'aggiramento `NOT_THE_USER_APPROVED_EFFECT`; lo storico della release resta disponibile come esempio di errore.

## Cosa significa il controllo V96
**Non promette di capire la bellezza automaticamente.** I test verificano che il progetto non dichiari *finito* ciò che non è stato esaminato visivamente. Non accettare valori come `human_photographic_quality_approved=true` se nessuno ha davvero verificato il filmato. Accompagnare ogni video futuro con contact sheet delle 5 coppie B/N/foto, animazione Vidu all'inizio/metà/fine, timelapse con timecode, richiesta API unica e ricevuta crediti. Nuova spesa **non** autorizzata da questo audit.

## Misure per il prossimo vero episodio
- Soggetto e periodo/luogo unici, cinque riprese originali realmente diverse con licenza documentata.
- Quattro fotografie image-to-image moderne, non solo colorizzate; volti fedeli a ciò che si vede nell'originale (e nei frames vicini).
- Una sola scena Vidu di circa 5s, generata **dopo** l'approvazione visiva della foto sorgente, inserita nel giusto punto e avviata dal vero filmato B/N della stessa inquadratura.
- Nessun altro credito Vidu per tentare di nascondere errori di montaggio.
- Dopo il montaggio, QA **completo** a velocità reale, inclusa musica; eseguire i gate V91+V94+V96, non solo verifiche H264/AAC; release finale solo dopo esito completo e diritti.
