# 🏛️ ArtVision Cinema V6 — VERSIONE APPROVATA / GOLD MASTER
**Stato: APPROVATA DALL'UTENTE il 20 ottobre 2026.**
**Baseline creativa obbligatoria per i nuovi video artistici finché l'utente non ne approva un'altra.**

> La V6 su Vincent van Gogh è stata esplicitamente giudicata dall'utente «di gran lunga il migliore per qualità». Salvare, non alterare e non sostituire con V1–V5 per impostazione predefinita. Sono consentiti miglioramenti, ma ogni nuova regia deve nascere come V7/V8 separata; mantenere V6 ripristinabile.

## PRINCIPIO FONDAMENTALE: VIDEO DI REGIA, NON SLIDESHOW

Il riferimento qualitativo non è una galleria di fotografie con zoom automatico. Il film deve avere una narrazione **visiva senza parole**. Studiare le vere opere, costruire corrispondenze cromatiche ed emotive, alternare ritmi e tipi di inquadratura, produrre un film con personalità dell'artista.

La prova approvata usa 19 opere **autentiche** e 55 inquadrature **composte individualmente** lungo un arco di 150 secondi, in cinque movimenti:

1. Il volto e il giallo — attacco sullo sguardo dell'autore, passaggio al colore.
2. I fiori e il blu — match-cut su pennellate, contrasti, ritorni di forme.
3. Paesaggi e materia — cielo/cipressi/alberi/texture, alternanza tra visione e particolare.
4. Figura e gesto umano — volti, mani e relazioni, con brevi respiri.
5. Tensione e ritorno ai motivi iniziali — climax misurato, chiusura poetica circolare.

Non replicare il dettaglio→intero per ogni quadro. Scegliere volta per volta ritratto immersivo, dettaglio reale, texture, composizione intera, match-cut, stacco, dissolvenza breve o ritorno a opera già vista. Stacchi spesso ogni 2–4s; qualche pausa più lunga solo quando serve. Il ritmo deve respirare con la musica e mantenere **opere a pieno schermo** per gran parte del film.

## REGOLE VISIVE VINCOLANTI

- Un solo film completo per artista, per ora 150 secondi; 9:16 verticale Full HD 1080×1920 24fps H.264/AAC.
- Niente seconda versione breve automatica, niente voce, niente testo esplicativo, niente liriche.
- Stessa firma d'apertura elegante: **NOME ARTISTA**, sotto **MUSIC BY COMPOSITORE** piccolo; niente altri testi durante il video.
- Riproduzioni museali vere e attribuite, meglio master 2K–4K quando disponibili, colori fedeli, niente dipinti creati da AI o ritocchi che modificano l'originale.
- Fotografie/colori/volti devono riempire lo schermo, con cornici/scenografie neutre soltanto quando si mostra volutamente l'opera completa. **Mai tornare ai quadri piccoli su ampio nero della V5.**
- Camera lenta ma viva, significativa per opera; non troppo frenetica né immobile; **nessuno split-screen**, effetti di slide, transizioni decorative, falsi 3D, testo invasivo o filtri indiscriminati.
- Musica realmente registrata, strumentale, con licenza controllata, coerente con l'artista. Brano diverso per artista quando possibile; registrare titolo, autore, URL, SHA256 e condizioni d'uso.
- Per CC BY attribuire autore, titolo, licenza, link e trasformazioni nella **descrizione pubblica** e file di accompagnamento, non obbligatoriamente in sovrimpressione sul film, purché ciò soddisfi la licenza applicabile. Normativa musei/beni culturali da verificare prima di monetizzare.
- Niente pubblicazione automatica. Non definire un nuovo video “approvato” senza feedback reale dell'utente.

## CODICE ESATTO DA CONSERVARE

- Motore di montaggio curato e approvato: `modules/artvision/director_cinema_v6.py`
- Ricerca e salvataggio immagini museali: `modules/artvision/export_v6_assets.py`
- Workflow dedicato: `.github/workflows/artvision-cinema-v6.yml`
- Guida analitica con arco emotivo: `modules/artvision/REGIA_CINEMA_V6.md`
- **Questa guida**: `modules/artvision/V6_APPROVATA_GOLD_MASTER.md`
- Motori V1–V5, workflow di libri narrati, altri moduli: **intoccati e recuperabili**.
- Non cambiare il preset creativo nel file V6: per esperimenti usare nuovo modulo/versione e confronto editoriale.

I due esempi `No-Cuesta-Saber-fdown.net.mp4` e `Enfermedad-cromtica-fdown.net.mp4` sono solo riferimenti di linguaggio audiovisivo: NON ricopiare o redistribuire scene e musica altrui.

## ARCHIVIO CAMPIONE — INTEGRITÀ DELLA V6

Film campione approvato: `ArtVision_CINEMA_V6_FINALE_150s.mp4`
- SHA256: `5c94072d861daf04b99ceceea9ef78ec82661c63284cec9f8e9e68285973dffd`
- 86.892.049 bytes; 150,10 secondi; 19 opere, 55 inquadrature, 1080×1920 H.264+AAC (verifica locale riuscita).
- Pacchetto film+copertina+storyboard+fonti+licenze: `ArtVision_VanGogh_Cinema_V6_PACCHETTO.zip`
- SHA256: `946fb049d795bf9d10a3b5058b036128120dc433945f0eca82b9014d75648bfe`
- Archivio **26 fotografie museali originali + registrazione musicale + metadati**: `ARTVISION_MUSEUM_SOURCES_V6.zip`
- SHA256: `3963e8de6f657b73f7ff59e5215b9a58d1c604f3b70ee9e5e4969509a43738a3`
- Sorgente standalone del render locale `artvision_v6_cinema.py` SHA256 `dc5facde8522b8e0f166241bde7ad394706d17e15106a650ccc5f5400b82332b` (sincronizzare con modulo GitHub se necessario).
- Le copie di media non fanno parte della storia GitHub (limiti di archiviazione). Conservarle separatamente nei file di backup e verificare integrità tramite questi hash.

## METODO RIPRODUCIBILE (PROVA DI VAN GOGH)

1. Conservare questi due archivi zip e il codice prima di qualsiasi modifica.
2. Con Python 3.11, FFmpeg, Pillow, NumPy e OpenCV scaricare/acquisire immagini dalle API istituzionali; per esatta riproduzione del film campione, preferire gli originali già archiviati, non nuovi risultati di ricerca.
3. Estrarre `ARTVISION_MUSEUM_SOURCES_V6.zip` in una cartella di lavoro (contiene `artworks.json`, `music_rights.json`, `original_images/` e `licensed_piano_music.mp3`).
4. Avviare ad esempio:
   ```bash
   python modules/artvision/director_cinema_v6.py --assets /percorso/cartella --out /percorso/output --duration 150
   ```
5. Validare `ffprobe`: video H.264 1080×1920, audio AAC, durata 150s ±2s, niente deformazioni/black bars non intenzionali.
6. Controllare manualmente apertura, almeno 10 inquadrature su più atti, transizioni, qualità degli ingrandimenti, testo e sincronismo audio.
7. Prima di pubblicare verificare fonti di immagini, relative autorizzazioni nel territorio/uso previsto e obblighi d'attribuzione musicali. Il solo MUSIC BY nel film non basta per CC BY.
8. Per un **altro artista**, riscrivere `STORY` con opere e soggetti propri e procurare musica reale nuova autorizzata: NON basta cambiare il nome nella copertina.

### Nota di trasparenza
La V6 **ha prodotto un file reale localmente e l'utente l'ha approvata artisticamente**. Esiste anche un workflow GitHub V6 dedicato, ma non attestare che una sua esecuzione end-to-end abbia avuto esito success se non viene effettivamente collaudata. La baseline viene preservata esattamente proprio per rendere possibili test futuri senza perdere il risultato apprezzato.

## RIPRISTINO
Usare il branch GitHub `ARTVISION_V6_GOLD_MASTER_APPROVATA_2026-10-20`, che congela la versione del codice e delle guide. Non aggiornare questo branch durante esperimenti. Il branch `main` potrà evolvere aggiungendo nuovi motori; V6 rimane la versione da cui tornare indietro.


## Identità grafica unica, obbligatoria dal prossimo episodio

**Richiesta confermata dall'utente il 20 ottobre 2026:** i prossimi film ArtVision devono usare SEMPRE **lo stesso font, dimensioni di riferimento, colori, fascia scura, filetto dorato, posizioni e animazione** del titolo iniziale e della copertina, senza creare un titolo diverso per ogni artista. Solo *nome artista*, *autore musicale* e *opera fotografata nello sfondo* possono cambiare. Per nomi lunghi è consentita esclusivamente la riduzione proporzionale della dimensione (stessa famiglia tipografica), senza cambiare lo stile.

**Fonte normativa per i nuovi video:** `modules/artvision/IDENTITA_VISIVA_FISSA_V6.json`. **Implementazione riutilizzabile:** `modules/artvision/identita_visiva_v6.py` con `signature(frame,t,artist,composer)` e `cover(frame,artist,composer)`. Il disegno replica l'apertura Van Gogh Cinema V6 approvata: titolo DejaVu Serif avorio, sottotitolo MUSIC BY in DejaVu Sans, banda antracite semitrasparente, linea dorata sottile, stessa posizione e sfumatura. Copertina JPG e video devono avere la STESSA impostazione, non solamente un font simile.

Il video originale Van Gogh GOLD MASTER e il Caravaggio già consegnato rimangono **immutati**. Lo script Caravaggio utilizzerà il componente condiviso solo per eventuali render futuri; versione prima della modifica salvata nel branch `backup-caravaggio-v6-prima-identita-grafica-unica-2026-10-20`. Il branch GOLD MASTER Van Gogh resta congelato. In ogni nuovo script regia V6, IMPORTARE la funzione condivisa e NON ridisegnare a mano la copertina.

