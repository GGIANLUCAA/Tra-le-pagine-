# LA STORIA RIVIVE — V58: OPEN SOURCE, RICERCA SOGGETTI E REGIA A PIÙ RIPRESE
**28 ottobre 2026 — richiesta dell'utente:** massima resa visiva percepita, NON obbligo 4K; produrre video brevi con più scene autentiche quando utili, ritmo sociale e gancio immediato. In futuro usare eventualmente un breve inserto Vidu solo quando incrementa davvero il valore. Poche discussioni ripetitive: la ricerca, la selezione, il piano e la revisione sono responsabilità del sistema entro i permessi e i costi già autorizzati.

## Priorità e ambito
Questo V58 integra e raffina V56/V57, non annulla V55 (MP4 + copertina + 4 post + ZIP + download verificabile + Video Library Studio), V28 (scrittura social originale), V33 (fonti autentiche), V25 (no pubblicazione/spesa automatica). Gli ArtVision 4x1 NON diventano obbligatori qui. Nessun video già approvato deve essere sostituito.

**Nuova regola madre:** scegliere prima una STORIA VISIVA REALE, poi le inquadrature, poi gli effetti; non generare inquadrature per riempire tempo. Misurare successo dalla qualità vista su Android e da metriche social reali dopo la pubblicazione, non da 4K nominale o punteggi immaginari.

## 1. Stack gratuito prioritario: audit 28/10/2026
| Progetto | Ruolo | Licenza codice verificata | Limiti e posizione |
|---|---|---|---|
| DDColor https://github.com/piddnad/DDColor | colorizzazione semantica delle immagini/ancore | Apache 2.0 | Verificare licenze pesi distribuiti e uso commerciale; per singolo frame produce flicker se non stabilizzato; GPU raccomandata. PRIMA OPZIONE per prototipo reale. |
| HAVC https://github.com/dan64/vs-havc | integrazione DDColor+DeOldify+ColorMNet e propagazione | MIT (wrapper) | **NON whitelist commerciale automaticamente**: dipendenza ColorMNet/CMNET2 eredita BY-NC-SA 4.0 / uso accademico, licenze pesi da verificare. Solo percorso sperimentale/research finché ogni componente non è legalmente chiarito. |
| ColorMNet https://github.com/yyang181/colormnet | coerenza temporale avanzata | BY-NC-SA 4.0 | **NON utilizzare per video monetizzabili senza permesso**; stessa cautela per CMNET2 derivato. |
| OpenCV https://github.com/opencv/opencv | propagazione cromatica tramite optical flow, QA / crop | Apache 2.0 | Modulo proprio, evitare flickering senza cambiare geometria e identità delle persone; test di ghosting necessari. Non sostituisce il modello AI di colore. |
| Real-ESRGAN https://github.com/xinntao/Real-ESRGAN | upscaling/de-noise mirato | BSD 3-Clause | Può creare texture artificiali e fluttuazioni; serve confronto visivo e stabilità. Non applicare 4x obbligatorio. |
| PySceneDetect https://github.com/Breakthrough/PySceneDetect | segmentazione di filmati lunghi e tagli | BSD 3-Clause | Segnala tagli, NON sceglie la storia o il soggetto più emozionante. |
| FFmpeg https://ffmpeg.org/ | montaggio, B/N→colori veri, audio, H264/AAC, pacchetti | LGPL/GPL a seconda della build | Vietato confondere transizione tra due tracce con colorizzazione vera. Audio e codec verificati. |
| vid.stab https://github.com/georgmartius/vid.stab | stabilizzazione di riprese mosse | LGPL 2.1+ (versioni recenti) | Può croppare i bordi e rovinare il 9:16; solo quando migliora l'originale. |
| RIFE https://github.com/hzwer/ECCV2022-RIFE | interpolazione fotogrammi (opzionale) | MIT | Non creare movimenti sbagliati, fantasma su mani/animali; mai presumere frame rate nativo più alto. |
| GFPGAN https://github.com/TencentARC/GFPGAN | restauro volti (laboratorio) | verificare codice/pesi | Rischio forte: inventa lineamenti; **OFF di default** per autenticità. |

**GPU gratuita ≠ server autonomo sempre acceso:** Kaggle fornisce GPU gratuita con quote e disponibilità variabili (docs `https://www.kaggle.com/docs/notebooks`); Colab free offre accesso non garantito e limitato (`https://research.google.com/colaboratory/intl/it/faq.html`). GitHub Actions Linux CPU serve per montage/QA, non si presume abbia una GPU NVIDIA. Nessun account nuovo, servizio pagato, credenziale o bypass limite senza consenso. Per video reali: test di **2–3 secondi** con DDColor+propagazione temporale custom su GPU gratuita disponibile; confrontare originale/colore, solo dopo full clip.

## 2. Qualità percepita: non 4K
- Default master verticale **1080×1920** quando migliora la visione; **720×1280 è sufficiente** se il materiale di partenza non giustifica upscaling e il video resta visivamente nitido. Il secondo è il formato effettivo dei tre esempi caricati dall'utente, non «4K».
- A colpo d'occhio il colore deve cambiare la percezione dell'epoca: distinguere pelle, cielo, ombre, tessuti, insegne ed edifici in modo coerente e credibile. Saturazione equilibrata (non slavata e non HDR artificiale), contrasto moderato, dettagli leggibili, facce non plastificate.
- Per ogni inquadratura, prima **massima qualità del master originale**, poi lieve pulizia/stabilizzazione solo se utile, colore AI semanticamente diverso e stabile, dettaglio, crop/letterbox elegante. Nessun pannello sfocato vuoto per riempire il 9:16; non tagliare persone e animali per obbligare crop pieno.
- I colori di archivio sono **interpretazione digitale**, non verità documentata. Riconoscere lo status «autentico restaurato» diverso da «ricostruzione generativa».

## 3. Scelta autonoma degli archivi: migliori TEMI prima dei file
Confrontare ogni volta almeno tre candidati se il soggetto è libero; non inventare visioni, pubblico o engagement. Dimensioni di giudizio qualitative: (A) azione visiva leggibile nei primi 2 s, (B) persone/emozioni/curiosità, (C) trasfigurazione B/N→colore, (D) possibilità di 2–4 frammenti coerenti senza ripetizione, (E) fonte/data/licenza, (F) crop verticale senza mutilazioni e (G) costo/render pratico. Uno score editoriale è una **stima da rivedere dopo visione**, non dati reali delle piattaforme.

**Priorità tematiche ipotetiche per social**, da testare e variare:
1. Vita quotidiana scomparsa: mercati, bambini, artigiani, caffè, lavoro umano — empatia e sorpresa.
2. Città in movimento: cavalli, tram, treni, prime automobili, folla e attraversamenti — dinamismo e colore.
3. Folla, eventi popolari, sport d'epoca, moda — apertura forte ed energia.
4. Una stessa città prima/dopo, con materiali locali datati e **senza simulare stessa ora/evento** — curiosità.
5. Gesti intimi e lavori in estinzione — 1 o 2 inquadrature invece di ritmo nevrotico se gestualità toccante.

Proposte specifiche con pagina file e licenza **dichiarata** CC0 (non ancora tagli/volti/revisione commerciale completa): `queue/storia_rivive_candidates_v58.json`. Fonti del Musée Albert-Kahn, pages Wikimedia Commons. Non pubblicare senza scelta timecodes, documentazione e verifica.
Per esempio «Parigi 1918» può riunire folla per festa sportiva + città **solo con caption che distinguano i momenti reali**; evitare di raccontare due girati separati come sequenza unica di un identico fatto.

## 4. Tre strutture di regia, non stampini
- **Rivelazione singola (8–16 s indicativi)**: un unico gesto incredibile nel vero film → B/N brevissimo, colori AI che emergono nel medesimo movimento → un'inquadratura pulita a colori → finale che completa il gesto; nessun montaggio multiplo obbligatorio.
- **Microstoria a 2–4 riprese (14–28 s indicativi)**: un gancio umano, contesto, particolare, esito. La stessa fonte può offrire diversi frammenti distinti, ma non usare 4 tagli della medesima azione per gonfiare le scene. Transizione B/N→colore applicata a un momento selezionato, non ogni 3 s a intervalli regolari.
- **Reale + ricostruzione separata (12–25 s indicativi)**: film storico colorizzato autentico → **breve inserto visivamente identificato come AI** creato, se davvero richiesto, per contestualizzare un momento NON presente in archivio → ritorno a ripresa autentica o chiusura. Non fingere che ricostruzione faccia parte dello stesso girato. Inserto Vidu non obbligatorio, breve e motivato, mai filler; nessun credito senza nuova approvazione esatta.

**Durata mai fissa, numero scene mai fisso.** Se il soggetto vale solo 9 secondi, 9 secondi belli sono meglio di 25 annacquati. Beat musicali motivati, una composizione riconoscibile, titoli brevi datati verificati, apertura 0–3–7 obbligatoria nel QA e chiusura senza richieste artificiali di commento. Cover elegante da frame reale, titoli non invadenti. V28: 4 post **diversi** per FB/IG/TikTok/YouTube, storia e visita agli archivi, non descrivere il software.

## 5. Inserto Vidu eventuale — controllo costi e integrità
- **Due nature di materiale nel dossier:** `archival_restored` = ripresa originale preservata e resa leggibile, `ai_reconstruction` = generato (nel film e nel post disclosure). L'AI non cambia fatti, mette in scena soltanto ipotesi esplicite.
- Piano Vidu se/quando autorizzato: `purpose`, `prompt` originale aderente a epoca, `shot_duration`, `cost_estimate`, `max_credits`, `explicit_per_clip_authorization`, `caption_disclosure`, `source_story_boundary`; **budget zero per default**. Non usare l'abbonamento o API key come autorizzazione implicita; niente retry o batch pagati.
- Misurare il guadagno artistico dell'inserto confrontando **due versioni** dello stesso soggetto (archivio puro e mix) solo con permessi e budget; se la ricostruzione sembra un video moderno generico, ometterla.

## 6. Montatore offline V58 e stato reale
- `src/storia_rivive_montage_v58.py` è un compositore FFmpeg gratuito: prende veri file localizzati `archive_bw`, `archive_colored` e opzionalmente `ai_reconstruction`; controlla file/timecode/identità della provenienza; compone più scene con audio dichiarato o silenzio marcato; esporta un MP4 verticale per revisione. **Non scarica filmati, non colorizza, non usa Vidu, non certifica diritti né pubblica.**
- Un file colorizzato non presente è **BLOCKED**, non viene rimpiazzato in segreto con sepia. Un inserto Vidu non autorizzato è **BLOCKED**. Ogni testo di ricostruzione generativa è distinto da quello di archivio. Le transizioni su due file richiedono esatto `source_id`, `start` e `duration` corrispondenti.
- Prima della consegna (V55) controllare intero video reale, hash/frame 0.1/1/3/5/7 s, sfarfallio, audio, cover JPEG, 4 post, diritti, ZIP CRC, download Android e catalogo+playback+copertina+social+ZIP nel sito, verificati separatamente. Le modifiche non toccano i master esistenti o automazioni.

## Prossima prova ad alto valore
1. Selezionare 3 fonti fra `queue/storia_rivive_candidates_v58.json` e scaricare solo anteprime/file CC0 piccoli; controllare primo secondo, movimento e crop su telefono. 
2. Preparare 2–3 secondi dello stesso girato con **DDColor REALE** (pesi/licenza verificati), quindi propagazione cromatica temporale custom OpenCV. Confrontare contro i tre riferimenti per colori, dettagli, transizione reale, pelle e costumi.
3. Se test buono, colorizzare i frammenti scelti e montarli tramite V58; consegnare 1 video di qualità, non 5 mediocri. Nessuna produzione multipla promessa finché il primo master non supera il gate.
4. Only later: miglioramento nitidezza e possibile inserto Vidu, **non** come scorciatoia per la colorizzazione. Zero euro e zero crediti finché non arriva autorizzazione esplicita.

Fonti ufficiali: repository e licenze sopra; Kaggle e Colab docs. Attestazioni di installazione/compatibilità/GPU non verificate restano `not_integrated`.
