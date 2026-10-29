# LA STORIA RIVIVE — V76 SOCIAL MUSEUM (29/10/2026)

**OBIETTIVO:** adattare ai social l'effetto V74/V75 approvato dall'utente, senza snaturarlo. Questa versione è un TEST, non la dimostrazione che sia già virale.

## Regia imprescindibile
1. Inquadrare vero **FILM storico in movimento**, B/N, provenienza e diritti documentati.
2. Fermare su **quello stesso fotogramma** (nessun salto di persona/scena). Reveals in circa 0,2–0,4 s.
3. **Fotografia AI fotorealistica** a colori generata image-to-image dal frame e vincolata alla scena, fisicamente ferma (non sola colorizzazione del video), per circa 2–4 s.
4. Proseguire su un'altra scena davvero distinta in movimento B/N. Non contare zoom/ritagli come scene nuove. Fare una verifica visiva di volti/mani/abiti/architettura; fotogramma di partenza più nitido => ricostruzione più fedele, fonte povera => ricostruzione più profonda ma plausibile.
5. Titolo iniziale SOLO luogo e annata, ad esempio `PARIGI · 1896—1900`; tipografia serif museale leggibile su smartphone, 1,5–2 s sul film autentico già in movimento, nessun cartello vuoto, logo lungo, parlato, «prima/dopo», watermark o altro testo tecnico.

## 8 migliorie Social Museum da mettere alla prova
- **HOOK:** scene immediatamente leggibili entro 1 secondo, primo foto-reveal idealmente entro 2–3 s (senza tagliare la scena storica fuori contesto). Nell'esperimento Parigi V76 il primo reveal comincia circa a 1,97 s.
- **PHOTO REVEAL:** differenza ottica evidente per volti, abiti, oggetti e atmosfera; la qualità non si misura solo dalla saturazione. Deterioramenti originali possono giustificare una ricostruzione più profonda, ma segnalarla nei metadati.
- **MUSICA E SOUND DESIGN:** composizione originale e accenti sincronizzati alle trasformazioni; eventuale rumore di cavalli/ferro/folla sempre dichiarato *ricreato*, non audio storico originale; nessuna voce.
- **RITMO VARIABILE:** foto finale di ogni scena ferma indicativamente 3–4 s quando ricca di dettagli, più breve se poco leggibile; video intero solitamente 20–26 s. Non allungare attraverso frame duplicati di una nuova scena immaginaria.
- **UMANITÀ:** chiusura possibilmente su uno sguardo, figura o gesto che crea connessione, invece di un quadro distante; è ipotesi editoriale da testare.
- **COPERTINA:** immagine ricostruita già effettivamente nel film, città/anno eleganti e leggibili in miniatura. Grafica consistente ma soggetti sempre diversi.
- **LOOP NATURALE:** evitare titoli finali e fade-to-black lunghi; se il montaggio lo permette, forte differenza fra foto finale colorata e primo B/N per favorire una revisione. NON dichiarare replay verificati senza metriche.
- **ANALYTICS POST PUBBLICAZIONE:** registrare per singolo video piattaforma, soggetto, durata, prima trasformazione, impression, tempo medio, completamento, replay, condivisioni, salvataggi, follow e clic. Nessuna ottimizzazione basata su numeri inventati. Confrontare almeno 6 soggetti diversi e, quando disponibile, esperimenti A/B sull'apertura.

## Esperimento concreto V76 (Parigi 1896–1900)
Tre scene autentiche già usate nei lavori Parigi V71/V75, tre fotografie AI preesistenti verificate per hash. Nuovo montaggio:
- 0–5,53 s: pompieri a cavallo, primo reveal ~1,97 s e foto a colori ~3,27 s;
- 5,53–12,83 s: Notre-Dame, secondo reveal ~8,9 s;
- 12,83–20,47 s: marciapiede mobile e persone, terzo reveal ~16,1 s, chiusura umana.
Pellicola autentica B/N, foto generative realmente ferme, titolo città/anno, musica originale e ambienti sonori creati, zero spese Vidu. Fonti: https://commons.wikimedia.org/wiki/File:A_Trip_Through_Paris,_France,_Late_1890s.webm.
**Importante:** questo è una nuova regia sui *medesimi tre soggetti*, non nuova ricerca, non tre fotografie AI appena generate. V75 resta immutata. Non pubblicare automaticamente su social/sito privato e non spacciarlo per autorizzato commercialmente in Italia senza controllo diritti. 
QA strutturale: confrontare movimento e saturazione nei blocchi B/N e foto ferme, decodifica totale H264/AAC, ZIP CRC, hash e download esterno GitHub Release.

## Default e versionamento
- V74: formato Video B/N → Freeze → Foto AI corretto.
- V75: durata maggiore 20–26s e titolo elegante città/anno.
- **V76:** applicare in futuro hook, gestione ritmo, soundtrack, finale umano, copertina e test post pubblicazione **senza cambiare il preset di base**.
- Coney Island V73 colorizzazione continua resta respinto salvo richiesta esplicita di variante diversa.

In pipeline includere `editorial_preset=freeze_ai_photo_reference_43054_43056`, `social_museum_v76=true`, `human_artistic_review_required=true`, `no_paid_api_without_approval=true`, `social_autopublish=false`.
