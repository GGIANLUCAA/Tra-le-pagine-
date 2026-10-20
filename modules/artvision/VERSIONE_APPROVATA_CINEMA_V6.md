# ArtVision Cinema V6 — VERSIONE DI RIFERIMENTO APPROVATA
**Conferma del committente: 20 ottobre 2026.**
**Stato creativo: APPROVATA, CONGELATA COME BASE DI LAVORO.**
La V6 è stata definita dall'utente «di gran lunga il migliore per qualità». Per i prossimi video artistici **partire SEMPRE dalla metodologia V6**, non dai preset V1–V5. Modifiche future esclusivamente additive, confrontabili e reversibili; non abbassare la qualità cercando di semplificare la regia.

## File canonici e backup
- **Codice del film effettivamente realizzato:** `modules/artvision/director_cinema_v6.py` (corrisponde allo script locale usato per renderizzare il Van Gogh V6, a parte il newline finale).
- **Acquisizione sorgenti autentiche:** `modules/artvision/export_v6_assets.py`.
- **Workflow riproducibile dedicato:** `.github/workflows/artvision-cinema-v6.yml`.
- **Guida artistica dettagliata:** `modules/artvision/REGIA_CINEMA_V6.md`.
- **Questo documento:** `modules/artvision/VERSIONE_APPROVATA_CINEMA_V6.md`.
- **Salvataggio GitHub:** branch immutabile `backup-artvision-cinema-v6-APPROVATO-2026-10-20`, creato DOPO questo documento e relativo aggiornamento del metodo permanente.
- Conservare inoltre `backup-artvision-v5-prima-regia-cinema-2026-10-20` per ritorno allo stato precedente.
- I file multimedia pesanti non vanno committati sul repository pubblico; il backup del video è un pacchetto ZIP separato consegnato all'utente. GitHub backup garantisce codice, workflow e documentazione, NON copia perpetua dell'MP4 originale.

## Risultato *realmente verificato* che approva la metodologia
**Film:** Vincent van Gogh — Cinema V6. Un solo film, 150.100 secondi, verticale 1080×1920, H.264 + AAC, 19 opere autentiche, 55 inquadrature. `ARTVISION_VAN_GOGH_CINEMA_V6.mp4` (in consegna denominato `ArtVision_CINEMA_V6_FINALE_150s.mp4`).
**SHA-256 dell'MP4 approvato:** `5c94072d861daf04b99ceceea9ef78ec82661c63284cec9f8e9e68285973dffd`. Dimensione: 86.892.049 byte.
**SHA-256 script locale eseguito:** `dc5facde8522b8e0f166241bde7ad394706d17e15106a650ccc5f5400b82332b`. Il file GitHub ha gli stessi contenuti testuali senza il newline finale.
**Video originale + fonti + storyboard + copertina:** nel pacchetto `ArtVision_VanGogh_Cinema_V6_PACCHETTO.zip`, già fornito all'utente. Non presupporre che link sandbox siano permanenti: se il file non è disponibile in una sessione futura, recuperarlo dall'utente oppure rigenerarlo dai sorgenti museali. Non inventare percorsi.
Il video è stato generato e verificato con ffprobe localmente; **non dichiarare una GitHub Actions V6 riuscita senza controllare una sua run specifica**.

## Le scelte creative da replicare (non copiando le scene)
1. **Le due referenze dell'utente** *No Cuesta Saber* e *Enfermedad cromática* insegnano densità del soggetto, contrasti visivi e ritmo, non autorizzano a copiare video, foto o audio.
2. **No slideshow, no piccoli dipinti su nero:** inquadrature immersive per la maggior parte della durata, con opere vere che dominano lo schermo.
3. **Regia in cinque movimenti emotivi** per Van Gogh: volto e giallo, fiori/blu, paesaggi, gesti umani, climax con ricorrenze e ritorno ai colori. Per i nuovi artisti, inventare i movimenti *in base alle loro opere*.
4. **55 scelte di inquadratura motivate editorialmente** nell'episodio pilota; tempi più spesso 2–4 secondi, con pause intenzionali e qualche dettaglio ripetuto per significato; ritmo che segue immagini e musica. Non imporre sempre 55 scene o identica velocità.
5. **Match-cut ragionati e pochi dissolvenze selettive** quando convergono gesti, linee, forme, colori. Niente split-screen, transizioni spettacolari gratuite, flash aggressivi, parallax falso, zoom perpetuo.
6. **Dettagli autentici con coordinate precise** (occhi, cappello, petali, pennellate, rami, mani, profondità). La mappa nella costante `STORY` vale solo per le opere di Van Gogh; non riciclarla per Caravaggio, Monet o altri.
7. **Apertura coordinata internazionale:** NOME ARTISTA + piccolo «MUSIC BY ...». Dopo spariscono le parole. Non usare voce, sottotitoli, frasi promozionali, didascalie oppure crediti finali visibili.
8. **Musica strumentale vera e autorizzata**: il pilota usa *Dreams Become Real*, Kevin MacLeod, con CC BY 4.0; attribution COMPLETA nella descrizione sociale e nel file licenza. Nuovi episodi preferibilmente tracce diverse, verificando download, durata e termini d'uso. Il solo «MUSIC BY» non soddisfa CC BY.
9. **Fotografia da museo ad alta risoluzione**: Met e Cleveland Open Access, CC0/public domain soltanto quando i metadata lo attestano. Ricerca di print master; niente opere reinventate. Controllare la normativa italiana per riproduzioni beni culturali prima di un uso commerciale.
10. **Consegna:** un solo MP4 finale collaudato, cover, motivazioni nello storyboard, licenze e fonti, descrizione per i social. Non pubblicare automaticamente. Zero API a pagamento obbligatorie.
11. **Controllo umano del risultato** prima di affermare che il video è pronto. Il successo di FFmpeg dimostra solo integrità, non valore artistico.

## Procedura rigorosa per ogni nuovo artista
1. Leggere prima questa pagina e la guida `REGIA_CINEMA_V6.md`, non i default storici delle altre regie.
2. Creare snapshot/branch di sicurezza se si modifica una parte della pipeline.
3. Cercare e verificare almeno 15–25 opere originali riutilizzabili, catalogarle con metadata e sorgente; per gli artisti protetti ottenere licenze/permessi specifici.
4. Curare il nuovo storyboard artista-specifico e i legami formali ed emotivi; non riusare il `STORY` di Van Gogh, salvo che l'artista richiesto sia proprio Van Gogh.
5. Selezionare musica reale coerente e non ripetuta recentemente, verificare licenza e attribuzione.
6. Eseguire `export_v6_assets.py` (riadattato in modo non distruttivo per l'artista scelto) per scaricare immagini vere + musica; eseguire V6 da modulo separato/parametri appropriati.
7. Esaminare contatto regia, differenze di nitidezza, titolo, inquadrature e musica; controllare durata, 1080×1920, H.264/AAC con ffprobe.
8. Produrre **una sola versione** perfezionata e consegnarla; annotare nuova versione in documentazione evitando di sovrascrivere questo standard approvato.
9. Se un esperimento è peggiore, il riferimento resta la Cinema V6. Migliorare solo su esplicita richiesta o con un vantaggio verificato; sempre rollback disponibile.

**V6 È IL GOLD STANDARD ATTUALE.** Le V1–V5 e le pipeline narrative/libri continuano a esistere per compatibilità e altre funzioni, ma non devono più essere usate come modello artistico di default quando l'utente chiede un nuovo ArtVision.
