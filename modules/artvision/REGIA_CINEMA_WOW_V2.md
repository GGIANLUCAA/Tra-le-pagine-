# ARTVISION — REGIA CINEMATOGRAFICA V2 «WOW»
**Data:** 20 ottobre 2026. **Origine:** analisi del video campione caricato dall'utente «Enfermedad cromática» (28,17 s, 9:16, 30 fps) e confronto con ArtVision Van Gogh V1.3 (150,17 s, 24 scene).
**Stato:** identità creativa e criteri di collaudo della nuova V2. Non dichiarare la regia V2 automaticamente installata o collaudata finché i test non lo dimostrano.

## Diagnosi

**Vecchia regia (da non usare come default qualitativo futuro):** ogni opera appare quasi identica alle altre: immagine intera al centro, sfondo sfocato, zoom centrale, 6,42 secondi, dissolvenza uniforme. Musica algoritmica ripetitiva. Non è un film, è uno slideshow.
**Video di riferimento:** sequenze di opere autentiche di Zurbarán, chiaroscuro marcato, attenzione a mani, abiti e volti, alternanza di immagini anche a intervalli sotto il secondo, ricorrenza di soggetti come leitmotiv, continuità estetica e andamento musicale, minime didascalie. L'esempio NON va copiato o ripubblicato, nemmeno nella colonna sonora: serve solo a capire ritmo e linguaggio.

## Nuova regola fondamentale
**L'opera è la sceneggiatura. La musica è il montaggio. La camera è un osservatore, non un filtro.** Il risultato deve essere un *cortometraggio musicale sull'arte*, diverso per Van Gogh, Caravaggio, Zurbarán, Rodin, Kandinsky ecc.

## Linguaggio del film
- **Opere reali e riconoscibili:** partire soltanto dagli asset autentici verificati dal catalogo museale con attribuzione e licenza idonea. Nessuna ricostruzione generativa di dipinti, figure, soggetti o sculture, nessuna deformazione di volti o gesti.
- **Inquadrature con intenzione:** per ogni opera analizzare soggetti focali, linee di forza, luce, pennellate, colore, direzione dello sguardo, motivi ricorrenti. Alternare figura intera (contesto), dettaglio espressivo (emozione), macro pennellata (materia), dialogo tra 2 opere diverse (associazione), ritorno su una opera chiave (motivo).
- **Cropping selettivo, non mutilazione:** mostrare almeno una volta ciascuna opera principale per intero. I dettagli possono usarne aree reali; non tagliare arbitrariamente teste, firme o elementi semantici; preservare colori e proporzioni.
- **Movimento diverso per scena:** push-in con centro motivato, pan tra soggetti, pull-back che rivela il quadro, tracking verticale, reveal dal dettaglio al totale; 2D/2.5D leggerissimo solo se la geometria originale è corretta, niente maschere automatiche con contorni falsi.
- **Transizioni con significato:** tagli in battuta, match-cut per geometria/direzione/colore/motivo (es. mani → mani, cielo → cielo), occasionali overlap/cross-dissolve in stile film; flash/whip solo quando la musica lo richiede. Non ripetere lo stesso preset su tutta la timeline.
- **Chiaroscuro senza alterare quadri:** sfondo, grafica, margini e luci simulate possono essere scenografici, il dipinto reale no. Nero profondo, tipografia editoriale sobria, zero cornici decorative gratuite.
- **Testo:** nome artista nella copertina iniziale; niente sottotitoli o spiegazioni nella sequenza; crediti artistici obbligatori fuori video nella descrizione o final card solo quando richiesti dalla licenza.
- **Musica:** non usare l'audio del video di riferimento senza diritti. Originale composta, oppure stock con licenza commerciale specifica per tutti i social previsti. **Scelta musicale PRIMA dello storyboard**, tempo musicale, battute, eventi e tensione. Produzione musicale con evoluzione dinamica e arrangiamento, non sola ripetizione di 4 onde sinusoidali.

## Struttura di un episodio da 150 secondi (orientativa, non automatismo rigido)
| Tempo | Atto | Regia | Densità tagli |
|---|---|---|---|
| 0–5 s | **Gancio** | aprire su un dettaglio memorabile, artist name typographic reveal entro 1–2 s | 0,7–2 s |
| 5–25 s | **Ingresso nel mondo** | 2–3 opere chiave, atmosfera, prime corrispondenze visive | 2–4 s |
| 25–65 s | **Scoperta** | più opere, dettagli e inquadrature contrastanti | 1,3–3 s |
| 65–95 s | **Respiro** | uno o due lunghi momenti contemplativi, dinamiche basse | 2,5–5 s |
| 95–130 s | **Crescendo** | accostamenti concettuali, ritmo incalzante, ritorno ai motivi | 0,6–2 s |
| 130–145 s | **Climax** | le opere più potenti, tagli sincronizzati e contrasti | 0,4–1,4 s |
| 145–150 s | **Ultima immagine** | rivelazione/ritorno dell'opera-emblema, chiusura musicale intenzionale | 2–5 s |

Non applicare 0,5 s di durata a tutte le immagini per 3 minuti: diventa caotico. Il «wow» è dato dal **contrasto** fra velocità e immobilità.

## Parametri editoriali per l'automazione
- Impostazioni: `style: cinematic_wow` opzionale; V1 invariata come `style: museum_legacy`.
- Generare JSON `STORYBOARD_REGIA.json` contenente: source asset ID, durata, tipo shot, focus x/y, zoom massimo, motivo narrativo, indice musicale/battuta, transizione e ragione.
- Ogni video 2–3 minuti deve disporre di almeno tre linguaggi di inquadratura distinti e almeno due grandi variazioni di ritmo. «Un'immagine/zoom/fade ripetuti» è errore qualitativo bloccante.
- Non consentire più di due transizioni speciali consecutive; limitare flash e whip a punti mirati. Evitare stroboscopia/flash forti per accessibilità.
- Motion: zoom usuale 1–1,25×; macro 1,4–1,65× solo con risoluzione sufficiente. Niente deformazioni, nessun riempimento generativo. Preservare almeno 1 rivelazione totale per opera principale.
- Montaggio guidato da BPM/marcatori e frasi musicali; tagli non tutti su ogni beat. Allineare *intenzionalmente* la maggior parte dei tagli più importanti a battute/transienti.
- Preview: prima render di 15–25 s ad alta qualità con 3–6 opere per approvazione estetica; poi versione completa. Questo evita sprechi di CPU e rende possibile migliorare prima di impegnare 3 minuti.
- Utilizzare `ffmpeg`, OpenCV/Pillow e NumPy; leggere immagini originali dai musei, preferire cache; zero API immagini/voce obbligatorie.
- Consegna completa: MP4, copertina, licenze, storyboard, report qualità, durata e costi, link GitHub run, conservazione storico.

## Direzione artista-specifica (non usare lo stesso preset ovunque)
| Artista/tipologia | Linguaggio suggerito |
|---|---|
| Van Gogh | ritmo pulsante/pennellate in macro autentica, azzurro/giallo **come sono nel quadro**, cielo→campo→sguardo, camera più viva |
| Caravaggio / Zurbarán | lunghi neri, stacchi su gesto e luce, timing incisivo, silenzio musicale relativo |
| Monet | dissolvenze più morbide, luce e paesaggi, meno tagli aggressivi |
| Kandinsky | rigore geometrico, match-cut su forme, ritmo astratto senza distorsioni |
| Scultura | dettagli reali su materia, ombra e più fotografie autorizzate per cambiare prospettiva, NO 3D falso |
| Contemporanei | diritti documentati in modo esplicito per immagini, installazioni, musica e usi social |

## Test di accettazione obbligatorio
1. Mostrare su 20 s un confronto **V1 vs V2** per controllare ritmo, varietà, continuità e qualità.
2. Il render deve passare controlli ffprobe H264+AAC, 9:16, durata richiesta ±2s, audio presente e senza clipping.
3. Controllare manualmente almeno 5 inquadrature, 3 transizioni, la copertina, la chiusura, rapporti d'aspetto e attribuzione opere.
4. **Non dichiarare «wow» riuscito** solo perché il render è green: chiedere il parere dell'utente sulla resa artistica. Favorire scene coerenti, non aggiungere filtri alla cieca.
5. I test V1, libri narrati e nuove modalità devono convivere. Non mutare `render-v3.yml` o moduli narrativi esistenti.

## Backups
Riferimento storico: `backup-prima-artvision-2026-10-20`. Prima di aggiornare il codice ArtVision creare branch aggiuntivo V1.3 per rollback rapido. Nuove estensioni in file separati, mantenere preset storico.

## Da ricordare SEMPRE per prossimi video
L'utente NON vuole *immagini una dietro l'altra* con 6 secondi dello stesso zoom. Non scambiare numero di transizioni con buona regia. Cercare ritmo musicale, scelte poetiche e dettaglio autentico; l'estetica deve essere cinematografica e originale, differente per ogni artista. Il video campione è un riferimento per lo **stile di montaggio**, non un filmato da copiare.
