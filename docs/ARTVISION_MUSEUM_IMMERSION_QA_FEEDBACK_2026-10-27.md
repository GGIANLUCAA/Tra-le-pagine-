# CHIARIMENTO DELL'UTENTE — DIFETTO PRINCIPALE CORNICE/QUADRO (27 ottobre 2026, sera)

L'utente ha precisato: «Quello che non mi piaceva era la centratura della cornice con il quadro: sembra una foto messa sopra una cornice, ma si vede palesemente». **Questa è la diagnosi artistica primaria; non reinterpretarla soltanto come problema di zoom, stacco, velocità o movimento.** La V2 era complessivamente gradita, ma l'innesto fisico del dipinto dentro la cornice era palesemente artificiale. La V3 ha peggiorato il risultato tentando di correggere altre cose.

## Soluzione visiva necessaria, prima di qualsiasi nuovo render

- Non usare un JPEG rettangolare semplicemente incollato sopra la foto della cornice. Definire la **luce/apertura interna della cornice**, non il suo bordo esterno. L'opera deve stare **dietro il battente e sotto il labbro interno della cornice** (layer frame foreground), con occlusione fisica visibile sui quattro bordi.
- Allineare centro, rapporto larghezza/altezza e prospettiva dell'opera al vano interno; evitare deformazione o crop che tagliano elementi artistici importanti. Se il rapporto non corrisponde, è la cornice a dover essere adattata, non stirare il dipinto.
- Creare un convincente **contatto fisico**: piccolo sottosquadro e ombra di contatto interna coerente con le luci della sala, eventuale passe-partout SOLO se appropriato, gradiente di ombra negli angoli, profondità reale della cornice e niente linea piatta super-netta da compositing.
- Applicare colorimetria, esposizione e texture coerenti con illuminazione museale; conservare fedelmente i colori dell'opera, senza rendere tutto innaturalmente omogeneo.
- Nei fotogrammi intermedi del push-in verificare al 100%, 200% e in movimento che il dipinto rimanga **dietro il bordo interno** su tutti e quattro i lati e non sembri sovrapposto. La cornice può essere 3D/reprojected con vera geometria; evitare zoom 2D su composizione piatta se compromette il realismo.
- **QA BLOCCANTE PRE-RENDER:** approvare visivamente un unico still nitido a distanza media e uno ravvicinato, con cornice e quadro uniti fisicamente; poi una breve sequenza del movimento. Solo se questa integrazione è davvero credibile si monta il film completo.
- Lasciare intatto il video V2 positivo; non promuovere la V3 respinta. L'obiettivo è la composizione fotorealistica, non correggere al costo della regia centrale.

---

# ESITO FEEDBACK UTENTE — V3 RESPINTA (27 ottobre 2026)

**VINCOLANTE PER LE PROSSIME PRODUZIONI:** l'utente ha guardato V3 e ha detto esplicitamente «ancora peggio». Il confronto visivo diretto V2/V3 conferma la regressione estetica. **NON usare V3 come riferimento approvato né riutilizzare il suo algoritmo di raccordo automatico SIFT e zoom 2D esasperato.** NON promuoverla Gold Master o qualità museale. Restaurare **V2** come unico riferimento positivo attuale, con i tre piccoli difetti noti (bordo cornice, raccordo ingresso, raccordo uscita).

Diagnosi verificata tramite comparativa di 13 fotogrammi a t=0,2,4,5.5,7.5,8.7,9.3,13,55,57,59,61,63 s:
- In V3 nei primi secondi il quadro cresce troppo velocemente: a 2 s occupa già gran parte del frame; a 4 s si vede un bordo orizzontale enorme; a 7–9 s zoom e panoramica spostano la composizione e compromettono la naturalezza.
- In V3 il rientro a 59–61 s reintroduce bruscamente la cornice e perde la fluidità originale.
- La registrazione geometrica dei pixel ai punti di stacco non sostituisce la **continuità del moto**, della velocità e della percezione: il miglioramento metrico di un match-cut ha prodotto una regressione visiva.
- V3 non va «aggiustata di nuovo»: conservarla soltanto per diagnosi. Lavorare su una **copia della V2**, preferibilmente con test brevi A/B dei soli raccordi che devono essere effettivamente guardati prima di renderizzare un nuovo film intero.
- Il feedback dell'utente prevale su ogni QA esclusivamente tecnico («ffmpeg decodifica» non equivale a qualità artistica). Evitare ulteriori video completi finché l'apertura breve non è visivamente convincente.

---

# ArtVision Museum Immersion — feedback e QA dei raccordi (27 ottobre 2026)

## Stato
Feedback positivo dell'utente su *The Ninth Wave* di Ivan Aivazovsky: l'effetto museo è promettente, ma **non è un Gold Master**. Il feedback identifica tre difetti concreti: (1) opera leggermente decentrata o fuori dal bordo interno della cornice; (2) stacco percettibile tra avvicinamento nel museo e primo dettaglio del film; (3) stesso stacco tra ultimo dettaglio e ritorno alla sala.

La V2 approvata come **direzione di qualità**, non come master definitivo, va preservata intatta. È stata esportata separatamente una prova correttiva V3 (nessuna sovrascrittura dell'originale).

## Correzione sperimentale V3 eseguita
- Quadro confinato esclusivamente al **rettangolo interno** della cornice mediante maschera geometrica opaca; niente sbordature.
- La stessa fotografia verificata del dipinto (5815 × 3648) viene usata anche durante l'avvicinamento: non sostituire il quadro sul confine del museo con un'altra immagine/crop senza match.
- L'ultimo fotogramma dell'ingresso è stato registrato geometricamente sui pixel del primo fotogramma del montaggio centrale esistente (matching SIFT/RANSAC). La transizione è un movimento continuo all'interno dell'**unica opera**, senza crossfade tra quadri.
- Per l'uscita, il film centrale finisce prima del taglio verso un cielo diverso; il movimento inverso comincia sulla stessa immagine dell'ultima scena conservata e riporta alla stessa sala e punto camera del primo fotogramma.
- Centro del film e musica già utilizzata mantenuti, senza riscrivere regia o audio del contenuto.
- V3: MP4 verticale 1080 × 1920, H.264/AAC, 24 fps, durata circa 63,96 s. Controlli completati: ffprobe, decodifica integrale senza errori, controllo visivo dei fotogrammi ai due punti di giunzione e dei fotogrammi iniziale/finale.

## Principi operativi riutilizzabili
1. **No cornice che taglia/contamina il dipinto**: definire il perimetro interno dell'opera e verificare una cornice di sicurezza anti-sbordo sui fotogrammi di ingresso e ritorno.
2. **Niente salto tra sala e dettagli**: il raccordo deve terminare sullo stesso ritaglio, scala, posizione e grading della prima inquadratura interna. Controllare fotogrammi adiacenti al taglio, non solo gli still di copertina.
3. **Niente salto al ritorno**: iniziare l'uscita su un dettaglio esattamente coerente con l'ultima scena precedente, ricomporre il dipinto e soltanto dopo rivelare la cornice e la sala.
4. Una sola opera **opaca** per fotogramma; mai ghosting, blend o dissolvenze incrociate tra dipinti. Allineare i pixel, non mascherare il taglio con trasparenza.
5. La V3 è ancora una ricostruzione di sala/cornice non autentiche e un'animazione 2D, **non una ripresa museale documentaria, né un video 8K**. Ricercare geometria 3D e frame storico solo se fonti disponibili.
6. L'effetto Museum Immersion resta **una tecnica opzionale**, da scegliere secondo il soggetto; non un'apertura obbligatoria per tutti i video.

## Ulteriori QA artistici consigliati
Controllo 0–3 s; controllo di prospettiva fisica e consistenza della cornice su tutta la traiettoria; confronto fotogramma prima/dopo *entrambe* le giunzioni a grandezza nativa; conferma di leggibilità esatta titolo/artista; realismo dei materiali del museo; ascolto audio; fonti e diritti separati della foto e della registrazione. Nessun automatismo deve proclamare «Gold Master» solo perché ffmpeg è passato.

Questo documento è un addendum non distruttivo per apprendere dal feedback; il sistema di regole attive e il preset Cinema V6 conservano la precedenza.