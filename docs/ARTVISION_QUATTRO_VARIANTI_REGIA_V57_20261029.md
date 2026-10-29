# ArtVision — Regia 4×1 V57: quattro film distinti, un'unica ricerca

Data: 29 ottobre 2026. **Stato: test tecnico V46 con The Cyclops realmente renderizzato; approvato dall'utente come riferimento stilistico della camera Museum il 29/10/2026.** Preserva il modello V46 già approvato.

## Pilota pratico, non nuovo quadro

Film **The Cyclops — Odilon Redon, Museum camera V57**, nuovo filmato 34,0 secondi H264/AAC 1080×1920, SHA256 Android **4d746edb3cd1083605ff11b0dce2bbfbe0e37eda01b836b8243894c732d509bb**; master 81.285.460 byte, Android 23.474.543 byte.

- Materiali reali recuperati dal kit Google Drive ArtVision **1UKsFzc_1w4CsZYcUb9iWHrwThcGmCuip**: `MUSEUM_REALFRAME_STILL.jpg` (galleria + cornice scenografica già approvata), `ORIGINAL_REDON.jpg` **2846×3579**, `AUDIO_ECHOES_OF_TIME_CC_BY4.mp3`; il film riferimento già approvato è `ArtVision_The_Cyclops_SENZA_STRISCE_CORRETTO_20261027.mp4`, Drive **1w9mb1N5hrGAaB870JANHoKk98MiibtpW**.
- Il test NON ricicla come nuovo quadro né produce una quinta versione: cambia il percorso della camera e controlla la continuità dei pixel del dipinto originale. **Una sola camera 2.5D** dal museo dentro il quadro e ritorno; non è una vera presa 3D con parallax, né fotografia di una sala reale o replica attestata della cornice storica.
- L'originale Redon è registrato con corrispondenze SIFT+RANSAC rispetto allo still museale: bounding box reale dell'immagine nell'illustrazione **x399..683, y548..904 su 1080×1920**; la prima prova con box erroneo **x346..586, y474..778 è stata scartata** perché l'opera sembrava incollata davanti alla cornice.
- L'originale pittorico viene ricampionato **dall'immagine autentica 2846×3579 a OGNI fotogramma**, nella stessa proiezione della sala; niente cut scena museo↔quadro, niente cornice 2D improvvisata.
- Ritmo: galleria con titolo esatto 0–3,7 s, ingresso graduale fino a 9 s, occhio del ciclope, crinale, Galatea, ritorno al quadro intero, uscita fino a 34 s.
- QA materiale: 816 fotogrammi decodificati in OpenCV, 22 frame distribuiti realmente estratti e visionati, MP4 e ZIP con SHA256/CRC verificati. **L'utente ha approvato la regia del provino il 29/10/2026. La pubblicazione resta soggetta a V25.**

## Conferma del modello V57 (29 ottobre 2026)

Il nuovo provino di The Cyclops, 34 secondi (SHA256 4d746edb3cd1083605ff11b0dce2bbfbe0e37eda01b836b8243894c732d509bb), è stato apprezzato e approvato dall'utente come riferimento di regia con ingresso ed uscita continui. Questa approvazione riguarda lo stile della camera, non la pubblicazione V25 né le opere successive. Le due varianti Museum ereditano il movimento, ma richiedono sala/cornice specifiche per l'opera, scala realistica e verifica delle fonti. Critico Museum conserva identica voce Gacrux e stesso copione del Critico Standard; Cinema Museum resta musicale e senza voce. Le versioni Standard NON si trasformano in Museum. Ogni quadro resta composto da quattro video distinti; il provino non conta come un nuovo quadro.

## Le QUATTRO versioni obbligatorie (non ridurre o confondere)

| Variante | Voce/audio | Regia obbligatoria | Uso della sala |
|---|---|---|---|
| **1. Critico Standard** | Google Gemini **Gacrux autentico** in italiano, voce verificata e timecode; copione scientifico, naturale, approfondito | Copertina Critico; ingresso standard nella pittura, dettagli sincronizzati, interpretazioni separate dai fatti | Nessuna scenografia Museum obbligatoria |
| **2. Critico Museum** | **Identico audio WAV, stesso copione parola per parola** della 1 | Dentro la stanza credibile, scala reale, vero rapporto quadro/cornice, movimento V46 dentro il quadro, dettagli visualizzati su timecode narrativi, ritorno fisico alla medesima sala | Sì. Non limitarsi a montare la voce su un video Cinema Museum |
| **3. Cinema Standard** | Solo musica originale licenziata, **senza voce** | Regia visuale sui dettagli autentici, progressione emotiva e durata motivata; tagli/movimenti ritmati, non ripetizioni zoom generiche | No, salvo specifica scelta editoriale non caratterizzante |
| **4. Cinema Museum** | Solo musica originale licenziata, **senza voce** | POV V46 continuo nello spazio: sala/oggetto fisico, frame valorizzante, passaggio quadro↔interno source-authentic, ritorno alla stessa cornice/sala | Sì, senza tagli netti o semplice JPEG zoompan |

## Un unico dossier, ma niente stampino

- Ricerca primaria: titolo/autore/tecnica, provenienza, dimensioni reali dell'ESATTO esemplare, stato/licenza dei file, scheda di cornice autentica cercata PRIMA di ricostruire, fotografie di riferimento con diritto di riuso, arte originale ad alta risoluzione, musica specifica con licenza. Separare ricerca fattuale da ipotesi creative.
- **Critico:** copione con osservazioni, storia, linguaggio critico e tempi dettagli; prima generare e verificare la stessa voce naturale, dopo montare entrambe le versioni Critico. Non utilizzare altre TTS o servizi a pagamento senza consenso.
- **Cinema:** stessa ricerca madre ma storyboard proprio, raccordi musicali e sequenze poetiche motivate. Può essere più breve/durare più a lungo in base all'opera; non copiare il copione del critico come sottotitolo.
- **Museum:** usare *The Cyclops SENZA STRISCE* per qualità dell'oggetto/cornice/incasso, *Hiroshige Museum Scale* per proporzione dell'opera sul muro rispetto a un adulto/porta. Le misure dell'opera in cm NON bastano: posizionare e misurare camera, cornice, muro, rapporto uomo, luce e profondità. Replica di cornice realmente documentata se autorizzata; altrimenti costruzione moderna/storicamente plausibile **dichiarata**.
- **Primi 7 s:** titolo inglese esatto+artista e immagine originale forte nei primi 1–3 s, entro 7 s un'evoluzione significativa. Evitare intro vuote e tagli che fanno sparire la cornice.
- **Consegna separata 4×:** 4 MP4 autentici + 4 copertine + 4 ZIP + 16 testi social originali + 4 ricette/QA con hash esatto, poi import su archivio privato realmente verificato secondo V25. Non inventare sandbox URL, stato import o approvazioni.
- Budget servizi video IA **ZERO** senza consenso per chiamata/clip. I file renderizzati non sono automaticamente approvati. Qualità del filmato > cadenza/contatori.

## Controllo V57: usare l'effetto «salto isolato», non la differenza grezza

Il QA V56 basato su **massimo MAD 12/255** causava falsi positivi sui film approvati: durante un ingresso fluido sono normali variazioni di 22/255, distribuite uniformemente per molti frame. È stato sostituito da **spike rispetto al movimento circostante**, sui reali frame decodificati 180×320.

| Caso sui video autentici | Picco RGB MAD | Mediana vicina | Rapporto | Esito |
|---|---:|---:|---:|---|
| Cyclops V46 approvato, camera continua | 22,81 | 21,37 | 1,07 | Movimento regolare |
| Cyclops nuovo V57, camera continua | 22,02 | 20,92 | 1,05 | Movimento regolare; regia V57 approvata |
| Hokusai Museum V55C, jump cut | 72,28 | 2,30 | 31,42 | Rifiutare |
| Homer Museum V55B, jump cut | 65,92 | circa zero | molto alto | Rifiutare |

Nel gate script rifiutare un evento solo quando **contemporaneamente** picco ≥30/255, rapporto ≥2,7× e differenza rispetto alla mediana ≥18/255. Non è una certificazione artistica: anche una dissolvenza lenta o una scena mediocre potrebbe passare i numeri. Occorrono sempre verifica frame/cornice, prima-persona, licenze e visione effettiva completa.

## Stato operativo

Il provino Redon V57 è **approvato come modello pratico di regia Museum**, non è una nuova opera, un nuovo Gold Master automaticamente pubblicabile né una quinta variante. Non replicare automaticamente la sua identica sala per opere diverse: prima recuperare o ricostruire una stanza/oggetto realmente compatibile con scala, epoca e frame documentato. Se non si può, segnare `blocked_quality_museum_v46_not_met`, non produrre una finta Museum. Feedback positivo sul MP4 ricevuto: usare V57 per la camera, V46 Cyclops per cornice e Hiroshige per scala. Nessuna approvazione automatica dei prossimi video.
