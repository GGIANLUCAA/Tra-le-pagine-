# ARTVISION CINEMA V6 — Regia originale, niente slideshow\n\n**APPROVATA DALL'UTENTE IL 20 OTTOBRE 2026 — baseline GOLD MASTER.** Il film Van Gogh V6 è il migliore tra le varianti secondo la valutazione esplicita dell'utente. Non regredire a V5, conservare esattamente codice e metodologia. Per approvazione, backup, SHA256 e ripristino consultare [V6_APPROVATA_GOLD_MASTER.md](V6_APPROVATA_GOLD_MASTER.md).

## VERSIONE APPROVATA — CINEMA V6 (20 ottobre 2026)

**La regia Cinema V6 è ora il riferimento artistico principale confermato dall'utente.** Quando viene richiesto un nuovo video d'arte, NON usare automaticamente gli esperimenti V1–V5 e NON riproporre slideshow, fondali neri con immagini piccole, zoom sistematici o montaggi tutti uguali.

Leggere prima **[VERSIONE_APPROVATA_CINEMA_V6.md](VERSIONE_APPROVATA_CINEMA_V6.md)** e **[REGIA_CINEMA_V6.md](REGIA_CINEMA_V6.md)**, poi usare il motore **`director_cinema_v6.py`** e il workflow dedicato **`artvision-cinema-v6.yml`**. Per artisti diversi da Van Gogh occorre uno storyboard nuovo specifico: il motore corrente contiene ancora la regia personalizzata per Van Gogh.

**Il vecchio `artvision-render.yml` parte ancora con V5 per compatibilità tecnica: NON equivale al nuovo standard approvato.** Seguire il workflow V6 dedicato finché non si predispone un nuovo artista. Conservare intatti libri narrati, vecchi motori e backup. Una sola versione filmica per artista, salvo diversa richiesta.

20 ottobre 2026. Nuova estensione separata: non modificare video narrati e le regie V1–V5.

## Cosa insegna il confronto con le due referenze reali dell'utente

I file forniti "No Cuesta Saber" e "Enfermedad cromática" sono riferimenti stilistici, **NON materiale da riutilizzare**. Nel primo, dopo l'introduzione, gli stacchi sono spesso ogni 2,5–3 secondi. Le opere e i soggetti dominano lo schermo, con pochi effetti e grande chiarezza. In V5 prevalevano quadri piccoli su nero e scene lunghe quasi immobili: NON ripetere.

## Regia V6, 150 secondi, 55 scelte editoriali manuali

Un unico film, non versioni brevi e lunghe. 19 dipinti autentici, cinque movimenti: (I) il volto e il giallo, (II) i fiori e il blu, (III) paesaggi e materia, (IV) ritratti e gesto umano, (V) tensione e ritorno al blu. I fotogrammi sono collegati da linee, materia e contrasti visivi. Le scene non sono più lo stesso "dettaglio→zoom→intero". Alternare primi piani d'arte a pieno schermo e rare inquadrature intere su fondale cromatico derivato dal dipinto.

Apertura permanente della serie: nome artista, sotto MUSIC BY + compositore in piccolo, tipografia serif. Dopo l'intro non appare altro testo. Nessuna voce, nessuna parola nel brano, niente slogan o call-to-action nel video. Nessuno split-screen o elementi falsi generati da AI. Movimenti leggeri; il montaggio usa prevalenza di stacchi netti e pochi match-cut/dissolvenze motivate.

## Strumenti e fonti

Script: modules/artvision/director_cinema_v6.py. Catalogo di immagini: modules/artvision/export_v6_assets.py. Workflow GitHub dedicato: .github/workflows/artvision-cinema-v6.yml. Media H264/AAC verticale 1080x1920, 24 fps, 150 sec. Fonte fotografica: API istituzionali Met e Cleveland, CC0/pubblico dominio con metadati conservati. Autentica registrazione strumentale "Dreams Become Real", Kevin MacLeod, su licenza CC BY 4.0: attribuzione COMPLETA richiesta nella descrizione pubblica e nel file rights. Una semplice dicitura MUSIC BY nel video non sostituisce la licenza.

Per utilizzo commerciale verificare i diritti delle opere, delle riproduzioni museali e leggi italiane sui beni culturali. Lo sfruttamento commerciale sui social non è garantito automaticamente da CC0.

Non cambiare il progetto originale, conservare il branch backup-artvision-v5-prima-regia-cinema-2026-10-20.

## Regole per successivi episodi

1. Rileggere i due riferimenti come ispirazione, non copiarli.
2. Studiare davvero opere autentiche del singolo artista, scegliere 15–25 riproduzioni di qualità.
3. Comporre a mano (o generare e validare con visione) 40–65 inquadrature con foci iconografici e motivazioni individuali. Non riutilizzare coordinate di Van Gogh.
4. Scegliere musica strumentale reale diversa dalla recente, verificare license, durata e credits.
5. Montare UN film da circa 150 secondi, con intro artist-name + MUSIC BY, poi zero parole.
6. Controllare audio, durata, nitidezza, colori, riproduzioni, transizioni e manifest dei diritti.
7. Consegnare il MP4 esistente realmente collaudato e copertina, non dichiarare riuscita una run in coda.
8. Conservare versione precedente e iterare incrementalmente; niente preset distruttivi.

Il lavoro V6 è un tentativo di regia d'autore misurabile, non una garanzia di "miglior video del mondo". Riservare al giudizio dell'utente la validazione estetica finale.
