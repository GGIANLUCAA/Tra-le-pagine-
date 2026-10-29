# La Storia Rivive V84 — audit reale delle cinque prove Vidu · 29 ottobre 2026

**Stato:** cinque veri job completati, cinque MP4 Vidu originali scaricati e decodificati, cinque MP4 con 1s B/N→colore, un reel comparativo di circa 25 s e uno ZIP Android. Una sola richiesta POST per job, **nessun retry**. Costo fornitore: **16 crediti ciascuno, 80 totali**. **Non pubblicare il saldo numerico API su GitHub**; saldo prima/dopo nel solo artifact privato. **Nessuna pubblicazione social o archivio sito; revisione artistica necessaria**.

- Workflow: `.github/workflows/storia-vidu-v84-five-motion-tests.yml`
- Motore: `src/storia_vidu_five_motion_tests_v84.py`
- Reel: `src/storia_vidu_v84_compare_reel.py`
- Release di anteprima (URL pubblico diretto da Android, NON prova di approvazione artistica): https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/tag/storia-rivive-v84-vidu-five-full-motion-previews-20261029
- Questa release contiene **nomi di file generati prima che l'errore di mappatura fosse scoperto**. Interpretare i contenuti usando il catalogo sorgenti qui sotto, NON solo il nome del file.

## Errore scoperto con il controllo VISIVO, non dagli automatismi
La mappatura fra immagine e soggetto è stata sbagliata in tre prompt (01, 02, 04), nonostante hash e codec corretti. Il modello ha seguito parole sbagliate rispetto al contenuto effettivo: nuovo tram davanti al cinema, persone/giornali indotti vicino a un tram, passante enfatizzato vicino a un'edicola con prompt da cinema. Questo dimostra che **hash corretto NON verifica il contenuto semantico** e che un punteggio di movimento/saturazione non è QA artistico. Il codice sorgente è stato corretto DOPO le cinque generazioni; per impedire regressioni verifica ora `IMAGE_SUBJECTS_HUMAN_VERIFIED` rispetto a `EXPECTED_SUBJECTS` prima di ogni eventuale nuovo POST.

### Catalogo definitivo dei fotogrammi, verificato visivamente
| Nome file | Oggetto effettivamente rappresentato | Prompt giusto |
|---|---|---|
| FOTO_AI_RICOSTRUITA_01.png | Venditore / chiosco giornali e clienti | NEWSSTAND |
| FOTO_AI_RICOSTRUITA_02.png | Persone vicino all'ingresso della stazione | STATION |
| FOTO_AI_RICOSTRUITA_03.png | Cinema: facciata, insegne, folla | CINEMA |
| FOTO_AI_RICOSTRUITA_04.png | Tram e passanti per strada | TRAM |
| END_MODERN.jpg | Marciapiede mobile Esposizione Parigi 1900 | MOVING_WALKWAY |

### Audit per clip (nome V84 originario da NON confondere col soggetto!)
| Clip originale V84 | Cosa mostra DAVVERO | Stato qualità artistica preliminare |
|---|---|---|
| `01_TRAM_CAMERA_FISSA` | Cinema e folla; prompt di TRAM erroneo: un tram appare/manifesta nel film | **SCARTARE** dall'uso produttivo, alterazione semantica |
| `02_NEWSSTAND_HANDS` | Tram; prompt di EDICOLA erroneo: moti/persone influenzati da soggetto sbagliato | **SCARTARE** dall'uso produttivo |
| `03_STATION_PEDESTRIANS` | Stazione, gruppo e persona centrale che si muove | **PROMETTENTE / RICHIEDE QA**, primo candidato da riguardare |
| `04_CINEMA_CROWD` | Edicola; prompt di CINEMA erroneo: passante foreground fuori dal focus | **NON APPROVATO**, evitare produzione senza verifica |
| `05_1900_WALKWAY_COLOR_MOTION` | Marciapiede mobile 1900, movimento localizzato reale | **PROMETTENTE / RICHIEDE QA**, colori ancora troppo tenui e limitati |

## Conclusioni tecniche importanti
1. **Miglioramento riuscito sulla transizione:** il primo secondo viene desaturato sullo *stesso video in movimento generato a colori da Vidu*, quindi dal fotogramma 1 al fotogramma finale il movimento Vidu è continuo; **nessun optical flow di colore** del V83.1. Evita gran parte delle scie di crominanza dei test precedenti.
2. Il frame-to-frame movement gate è **necessario ma non sufficiente**: 4/5 superano il controllo semplice di saturazione e movimento, ma 3/5 avevano prompt semanticamente sbagliato. Serve validazione foto/prompt, + ispezione del primo, medio e ultimo frame e video a velocità normale.
3. La scena marciapiede mobile è visivamente molto neutra (pietra e abiti scuri): un gate sulla *mediana saturazione di tutta l'immagine* la boccia erroneamente anche se lampade e alcuni abiti diventano colorati. Occorre combinarlo con **percentuale di pixel saturi in ROI verificata**, ma se l'effetto colore è debole NON dichiararlo spettacolare a prescindere.
4. Nel V83.1 tra varie scene esistevano salti di esposizione fino a ~63 livelli di grigio di media tra due inquadrature (es. 137→74). Nei prossimi 4+1 applicare un controllo sugli *stacchi* e regia sul movimento/luce; non lisciare per forza ogni scena con blur o dissolvenze fantasma.
5. Q2 Pro Fast image-to-video di **sola immagine moderna/restaurata** è preferibile per prove di movimento rispetto a Start-End dal B/N a una foto finale quando quest'ultima congela l'azione. La modifica B/N→colore si costruisce sul **video interamente generato a colori**, con mascheratura della saturazione temporale nei primi ~1s e senza rallentare/fermare le persone.
6. Non generare altre clip a pagamento da questi stessi cinque tentativi: il budget autorizzato è stato esaurito. Prossimo esperimento a pagamento solo con una nuova autorizzazione e immagini/prompt/semantica pre-verificati.
7. Titoli, periodi e diritti: 4 scene provengono dalla serie Parigi 1918, 1 dal 1900. Non affermare mai che siano lo stesso luogo, momento o piano-sequenza storico senza spiegazione. Colori e movimento Vidu sono ricostruzioni artistiche, NON documento originale a colori.

## Cosa è stato realmente verificato
- 5 task Vidu distinti, tutti scaricati e MP4 decodificati, ogni task 16 crediti
- prima/dopo temporale in B/N→colore sullo stesso movimento
- ZIP e MP4 GitHub Release presenti con dimensioni reali
- 4/5 metriche automatiche di colore superate; il quinto è tenue e non passa il gate automatico
- audit visuale su cinque tempi rappresentativi delle cinque scene
- **nessuna** approvazione artistica della clip finale al solo passaggio automatico

## Montaggio V85 ricavato dalle prove — zero nuovi crediti
Abbiamo realizzato **V85** con quattro cicli V82 già esistenti e, nel finale, la vera clip Vidu `05_1900_WALKWAY_COLOR_MOTION` generata nei test V84. La nuova regia dispone tram → edicola → cinema → stazione → marciapiede mobile Vidu, con musica continua e rinforzo cromatico moderato sulla clip Vidu senza optical flow, durata verificata **19,8 secondi** e MP4/ZIP esterni. Nell'audit GitHub Actions i salti di luminanza misurati ai quattro confini sono ~2,56 / 2,82 / 9,74 / 0,7 (la vecchia disposizione raggiungeva circa 63). Il salto più forte del V83 è stato quindi molto ridotto **ordinando le scene**, non sfocandole o fondendo persone diverse. Nessun nuovo POST Vidu; fonte storica mista 1918 + 1900, **anteprima tecnica non approvata per pubblicazione**.
- Nuovo renderer: `src/storia_rivive_hybrid_v85.py`
- Workflow: `.github/workflows/storia-v85-hybrid-final-moving-vidu.yml`
- Download esterno: https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/tag/storia-rivive-paris-1900-1918-v85-4plus1-vidu-moving-finale
- Evitare di qualificare `exposure_seams` come prova di corrispondenza dei volti: serve controllo visivo dell'originale e del generato.
