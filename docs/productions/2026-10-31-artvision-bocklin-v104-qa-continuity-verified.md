# Böcklin NG 2/80 — V104 verifica fisica dei 4 MP4, difetti di continuità nei Critico (31/10/2026)

**Ambito:** solo QA sui byte originali, senza TTS, workflow rerun, rendering, pubblicazioni o modifiche ai master. Il pacchetto V103 e la coda restano invariati. Nessuna settima opera.

## Fonti e verifica eseguita

- Lettura su `main` di `docs/productions/2026-10-31-artvision-bocklin-v103-quattro-mp4-completi-verificati.md`, coda `queue/artvision_four_variants_s01_20261028.json` e renderer `src/artvision_bocklin_critico_render_v102.py`.
- Materializzati dalla Libreria privata **i due MP4 Critico e lo ZIP completo V103**. SHA256 e byte verificati sul file effettivo:
  - Critico Standard 5.554.975 B, SHA `096926e6ffb0de921fca72726deb4a136227150d1d1a224ccd42e329ee903777`
  - Critico Museum 6.222.614 B, SHA `03eb6c8a77c4572b7ca83c81088c4b3d499b06802dd996a97a505b6fe768a6ed`
  - ZIP completo 27.243.960 B, SHA `468524594b1a69b2c82a49d5d67e1e365b7d9ec83c10df2f5398f70613c16cd9`, CRC PASS
- I due Cinema estratti dallo ZIP sono SHA-identici a V100/V101 (`b176560a...` e `c9f40502...`). **FFmpeg full decode PASS per tutti e quattro** in questa verifica.
- Recuperato l'artifact reale del run GitHub `41231513083` (ID `13053703331`) e letti `VOICE_CACHE_V13.json` e `ALLINEAMENTO_VOCE.json`. **Nessuna nuova generazione vocale**. La cache indica allineamento ASR interpolato 86,283%, non ascolto umano.
- Analizzati tutti i 2.213 frame a 20 fps di ciascun Critico con OpenCV; MAD = media delle differenze assolute tra due frame grayscale consecutivi ridotti a 180×320. I valori sono diagnostici, non una valutazione artistica definitiva.

## Difetti concreti riscontrati, non precedentemente corretti

1. **Critico Museum: due stacchi bruschi al confine della cornice**, proprio dove la regia dovrebbe essere continua. A **5,00 s**, passaggio netto dalla fotografia incorniciata (bordo dorato visibile) al dettaglio pittorico senza cornice, MAD **40,62/255**; a **103,65 s**, ritorno improvviso dal dettaglio alla foto incorniciata, MAD **50,35/255**. Ispezione dei frame immediatamente prima/dopo conferma salto di scala, posizione e bordo. Non è una transizione prospettica continua.
2. **Critico Standard: salti di inquadratura molto evidenti fra capitoli**: **61,20 s** MAD **59,74/255**, **70,75 s** MAD **72,08/255**, **79,10 s** MAD **78,41/255**, **90,90 s** MAD **39,73/255**. I tagli sono presenti nel file originale e corrispondono a cambi di capitolo/coordinate nel renderer; il file non è corrotto. La regia potrebbe richiedere raccordi motivati, non un fade con doppia esposizione.
3. **Controllo parola–scena:** la cache ASR mostra confini di capitolo coerenti con i timestamp generati (ad es. capitolo cipressi 61,22–70,74 s, luce 70,74–79,10 s). Questo **non** sostituisce l'ascolto completo né certifica ogni parola; allineamento interpolato resta da validare.

## Decisione di sicurezza editoriale

**Non sostituire né ritoccare i quattro MP4 V103 sulla base di questo solo audit.** Un crossfade semplice introdurrebbe ghosting, già bocciato in precedenza; una correzione prospettica richiede ricostruire in copia, usando la fotografia Sailko e l'opera autentica, con controllo fotogramma per fotogramma e identico AAC, poi FFmpeg full decode + SHA + confronto visivo prima di selezionare la revisione. Non avviare TTS, nuovi workflow, re-render Cinema, pubblicazione o settima opera. I due Cinema restano candidati apprezzati dal proprietario; i due Critico restano `rendered_needs_review`. **Gold V25 = 0; Android/R2 non verificato.**

**Riproduzione dei numeri:** OpenCV `VideoCapture` sequenziale, BGR→GRAY, `resize(180,320)`, `mean(absdiff(current,previous))`; timestamp del secondo frame = indice/20. Sono stati esaminati campioni visivi a 4,85–5,20 s e 103,45–104,30 s e campioni lungo l'intera durata.
