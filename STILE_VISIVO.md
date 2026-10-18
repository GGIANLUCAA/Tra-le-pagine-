# TRA LE PAGINE — STILE VISIVO (riferimento: video caricato dall'utente)

## Direzione creativa confermata
Il riferimento reale è un racconto di Pagine Lampo di circa 3:20 (formato 360x640), con personaggi **cartoon 2D ben disegnati**, sfondo bianco, pose espressive, ambientazioni essenziali, sottotitoli piccoli in basso e una nuova illustrazione ogni 6–10 secondi circa.

**NON fare**: fotografia realistica/cinematografica, luci scure, sfondi neri o petrolio a pieno schermo, quadri geometrici fatti da Python, testo scritto direttamente nell'immagine, collage di 12 riquadri, piccoli personaggi identici in pose rigide.

**FARE**: illustrazione digitale editoriale di qualità, look cartoon per ragazzi/adulti, bianco caldo #F9F8F3, linee pulite, ombre morbide, colori naturali con accenti blu e oro, personaggi grandi, espressioni comprensibili, poche comparse. Un personaggio mantiene capelli, volto, abbigliamento ed età in ogni scena.

## Formula per minimizzare i costi
- Circa 2:13 di narrazione = **16 inquadrature**, costruite a partire da **12 immagini AI** (quattro ritorni ravvicinati su immagini precedenti).
- Una singola generazione per immagine; prima approvare 1 test di stile, poi produrre solo le altre 11.
- 9:16 verticale, minimo 720x1280; nessuna scritta impressa nell'illustrazione.
- Allineamento scena/voce tramite `scene_cues.json`: ogni taglio parte **dalla frase effettiva**, non a intervalli uguali.
- Movimenti di camera leggeri, mai eccessivi. No generazione video AI frame-per-frame.
- Voce Kokoro già funzionante; il testo rimane invariato per conservare il risultato apprezzato.

## Coerenza dei personaggi
- Dr. B.: uomo austriaco sui 40-50, sottile, capelli castani pettinati all'indietro, viso segnato, completo grigio e camicia chiara. Nei flashback viso più stanco e capelli un po' disordinati.
- Mirko Czentovic: uomo corpulento, capelli scuri curati, completo scuro, espressione impassibile.
- Ambientazione: Vienna e transatlantico nel XX secolo, non abiti moderni.
- Personaggi originali del racconto, non copie dei protagonisti del video di riferimento.

## Grammatica visiva
- La narrazione menziona una nave → mostra la nave; una stanza → stanza; un libro → libro.
- Le emozioni emergono da postura, occhi e gesti, non da immagini astratte.
- Sottotitoli 1–2 righe in basso, bianchi con contorno scuro e alta leggibilità.
- Titolo del format piccolo in alto, nessuna filigrana del video di riferimento.
- Immagini a pieno schermo con ampio spazio negativo: evita tagli su teste e mani durante zoom/pan.

## Pubblicazione
Questa è la specifica da applicare. La vecchia modalità 'draw_scene' rimane solo come fallback di debug; se compare "ANTEPRIMA TECNICA" in `STATO_IMMAGINI.txt`, **NON pubblicare il video**.
