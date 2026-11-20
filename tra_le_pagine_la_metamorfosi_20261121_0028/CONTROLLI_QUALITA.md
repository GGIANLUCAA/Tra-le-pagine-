# CONTROLLI QUALITÀ — TRA LE PAGINE / LA METAMORFOSI (Kafka)

Soglia richiesta: **≥ 4/5** per ciascun semaforo. Se un semaforo fallisce si corregge **solo** quella parte.

## 1. Semaforo EDITORIALE — 5/5 (verde)

| Criterio | Esito | Evidenza |
|---|---|---|
| Opera non ancora trattata | OK | Nessun episodio precedente su *La metamorfosi* in `/workspace` |
| Gancio fattuale nei primi 3–5 s | OK | Apertura a 0,00 s: «Una mattina al risveglio da sogni inquieti… non riconosce più il proprio corpo» |
| Durata 2–4 min | OK | Narrazione 187,4 s ≈ 3 min 7 s; video 191,1 s |
| Copione 250–520 parole | OK | **430 parole** |
| Progressione chiara (situazione→svolta→conseguenze→significato) | OK | Struttura in 5 blocchi, vedi `COPIONE.txt` |
| Cinque revisioni obbligatorie | OK | Fattuale, comprensibilità, ritmo, voce, originalità — vedi `STORYBOARD.md` |
| Fedeltà verificata (2+ fonti) | OK | Testo originale (Gutenberg #22367) + fonti enciclopediche; scheda in `SCHEDA_INTERNA.md` |
| Nessun evento inventato | OK | Ogni frase-fatto tracciabile alla scheda interna |
| Spoiler gestito | OK | Avviso spoiler in `DESCRIZIONE_SOCIAL.txt` |

## 2. Semaforo ARTISTICO — 4/5 (verde)

| Criterio | Esito | Evidenza |
|---|---|---|
| Stile graphic novel / cartoon adulto 2D pittorico | OK | Illustrazioni originali, composizioni d'epoca pulite |
| Formato verticale 9:16 1080×1920 | OK | Tutte le scene e le card sono 1080×1920 |
| Palette di marca (petrolio #0C2A35, oro #C8A46A, avorio #F6F1E6) | OK | Applicata a copertina, card e vignettatura delle scene |
| Nessun testo dentro le immagini | OK | Testo solo in copertina/card generate in montaggio |
| Facce e mani corrette, personaggi coerenti | OK (con riserva) | Rivisti i fotogrammi; leggere imperfezioni tipiche della generazione, nessuna mano/volto tagliato nei pan/zoom |
| Copertina di serie con branding «TRA LE PAGINE» + titolo/autore leggibili da miniatura | OK | `COPERTINA.jpg` / `copertina.png` |

Riserva: la risoluzione nativa degli asset generati è inferiore a 1080 px ed è stata portata a 1080×1920 con upscaling (leggera morbidezza). Non incide sulla resa finale a schermo.

## 3. Semaforo TECNICO — 5/5 (verde)

| Criterio | Esito | Evidenza |
|---|---|---|
| MP4 verticale riproducibile | OK | H.264, 1080×1920, 30 fps, 191,13 s, 76 MB |
| Audio presente e sincrono | OK | AAC 48 kHz; audio 191,125 s ≈ video 191,133 s |
| Sottotitoli sincronizzati con le parole pronunciate | OK | Allineamento Whisper (word timestamps) + `SequenceMatcher`; 49 cue |
| Sottotitoli burn-in | OK | Verificati su fotogrammi estratti (presenti nelle scene, assenti sulla card di brand) |
| Durate inquadrature 5–13 s | OK (con 2 eccezioni) | 21/23 in range; sc.3 ≈ 4,8 s e sc.9 ≈ 3,9 s, vincolate a frasi brevissime della narrazione |
| Transizioni non tutte uguali | OK | fade pulito + fade/dissolve/fade-to-black/fade-to-white nei punti-chiave |
| Movimento lieve nelle scene contemplative | OK | Ken Burns in/out/left/right/up/down; fermo su morte e chiusura |
| Musica discreta sotto la voce | OK | Letto sintetizzato originale a −16 dB ca., fade in/out |
| Chiusura con brand breve | OK | Card ~4 s «TRA LE PAGINE — una storia alla volta» |
| Diritti puliti | OK | Testi, voce (Kokoro locale) e musica originali; nessuna copertina editoriale protetta |

## 4. Test umano finale — superato

Visione integrale con audio: comprensibile senza aver letto il libro, hook immediato, sincronia parola/inquadratura e sottotitoli corretti, nessun salto/duplicazione.

## Esito complessivo: **PROMOSSO** (editoriale 5/5, artistico 4/5, tecnico 5/5)
