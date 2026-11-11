# La Storia Rivive · Parigi 1918 — V160, nuovo provino video reale

Data: 2026-11-01. Priorità issue #144 e mandato V108. **Questo è un provino di montaggio, non un master finale 4+1, non un video approvato né pubblicato.**

## Provenienza e verifica reale

- Film originale: *Arrivée d'un train de Marseille et voyageurs dans la cour de la gare de Lyon. La traversée de Paris à la nage — AI139599*, Musée Albert-Kahn / Le Saint Lucien, Wikimedia Commons.
- Pagina: https://commons.wikimedia.org/wiki/File:Arriv%C3%A9e_d%27un_train_de_Marseille_et_voyageurs_dans_la_cour_de_la_gare_de_Lyon._La_travers%C3%A9e_de_Paris_%C3%A0_la_nage_-_AI139599.webm
- Dichiarazione Commons: CC0; controllo indipendente dei diritti Italia ancora **pending**, nessun permesso di autopubblicazione.
- File fonte realmente scaricato e verificato byte-per-byte: 11.148.380 byte, SHA1 `aa471da773d14f422d1387654601ca03b5224455`.
- FFprobe locale: VP9, 720×576, 30 fps, 283,064 s. Attenzione: metadata pagina Commons dichiara larghezza 768, ma il raster realmente **decodificato** ha larghezza 720 e SAR non quadrato. Correzione del workflow V160 per usare il dato effettivo.

## Cinque inquadrature reali del medesimo film

Il film comprende più occasioni, e quindi il titolo editoriale è **PARIGI · 1918**, non un singolo giorno o evento. Timestamps dei cambi scena reali individuati via FFmpeg: 22,547 · 86,181 · 131,481 · 208,181 · 238,381 secondi.

| Scena | Inizio sorgente, s | Motivo visivo | Montaggio V160 |
| --- | ---: | --- | --- |
| 1 | 22,90 | folla presso la stazione | 1,4 s film originale + 1,95 s freeze cromatico |
| 2 | 86,80 | teatro/cinema e persone | 1,4 s film originale + 1,95 s freeze cromatico |
| 3 | 132,10 | esercizi commerciali e passanti | 1,4 s film originale + 1,95 s freeze cromatico |
| 4 | 208,65 | movimento sul boulevard | 1,4 s film originale + 1,95 s freeze cromatico |
| 5 | 238,90 | folla al banco di giornali | 1,4 s film originale + 1,95 s **vera pellicola originale in movimento** con viraggio |

Freeze acquisito **dall'ultimo frame effettivo del segmento MP4 decodificato** per ciascuna scena. Nessun falso video AI. Il restauro tonale è una trasformazione fotografica prudente dei byte della fonte, **non** generative image-to-image e non va confuso con il V98. Musica sintetizzata originale, titolo discreto, nessuna voce.

## Output tecnico controllato

- MP4 **creato davvero in ambiente di lavoro ChatGPT** (non caricato su GitHub, non pubblicato su sito/social): `LA_STORIA_RIVIVE_PARIGI_1918_V160_PROVINO.mp4`
- Durata 16,533 s, 720×1280, video H.264, audio AAC, FFmpeg **full decode PASS**.
- 1.913.165 byte; SHA256 `75f80f452eec0c981e209d0b14552053f612bb4f22ff2fc0edd394d62d65daa5`.
- Sono stati creati anche `LA_STORIA_RIVIVE_PARIGI_1918_V160_KIT.zip` (1.987.901 byte), copertina JPG, QA JSON e quattro bozze social. I download esatti sono forniti **nella chat che ha generato i file**, non tramite link GitHub non verificati.
- Controllo visivo su campionamento di dieci frame del vero MP4 eseguito; restano limiti importanti: composizione archivistica orizzontale entro video verticale, fonte SD, colore solo tonale, freeze relativamente statici, mancanza dettagli moderni e movimento Vidu.

## Stato non falsificabile

`rendered_needs_review`. **0** fotografie AI I2I moderne; **0** clip Vidu; **0** crediti consumati; **0** pubblicazioni; **0** approvazioni artistiche. Golden V98 **non superato**. V91/V94/V96/V99 final gate non può passare senza 4 I2I reali source-locked + 1 Vidu autentico; non trattare la semplice codifica H.264/AAC come un PASS finale. Nessun intervento su ArtVision, WOW LAB o cron 3 ore.

## Prossimo passo

Ricerca di fonte 2K/HD con cinque shot coerenti, diritti territoriali verificabili, produzione reale di quattro restauri I2I con revisione umana e quinta clip Vidu autorizzata e deduplicata; confronto diretto con V98 prima di master/serie. L'ulteriore sperimentazione su V160 può servire a studiare gli inquadramenti, **non** sostituire il vero 4+1.

## V161 · riproducibilità GitHub Actions (1 novembre 2026)

Il provino V160 era stato prodotto solo nell'ambiente della conversazione: il workflow originario conservava **la pellicola**, non l'MP4. La modifica V161 introduce `src/storia_paris1918_v161_preview.py` e collega il render a `.github/workflows/storia-v160-paris1918-source-review.yml` dopo la verifica dei byte SHA1 originali. Crea un **nuovo provino tecnico B/N** con 5 finestre temporali, 4 freeze dall'ultimo frame decodificato di ogni segmento, quinta scena originale in movimento, sottofondo sintetico originale, MP4 H264/AAC, copertina, 4 testi social, QA JSON e ZIP Android. L'output è salvato in un artifact Actions di revisione (7 giorni), **non** in release pubblica.

Non confondere il provino V161 con il V160: il V161 è dichiaratamente **in bianco e nero**, senza falsa tinta presentata come I2I, e ha SHA/byte diversi. Il controllo sorgente rifiuta SHA1 diverso e il render richiede decodifica completa FFmpeg e contenitore H264/AAC 14–35 s. I 5 timecode non equivalgono da soli a un'approvazione visiva delle cinque riprese. Rimangono **zero** I2I, **zero** Vidu, nessuna verifica indipendente dei diritti italiani, nessuna approvazione artistica o pubblicazione. Stato `RENDERED_NEEDS_REVIEW` solo quando il workflow ha davvero creato e verificato il file; in caso di job fallito, non dichiarare il video disponibile. Nessun credito consumato.
