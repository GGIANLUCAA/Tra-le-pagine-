# ArtVision — Critico Bruegel: prova di autocritica e revisione regia V330 → V331 (12/11/2026)

## Scopo
Migliorare concretamente la regia del **Critico Standard** esistente di *The Fall of the Rebel Angels* (1562) senza rigenerare voce, inventare scene, modificare V144 approvato o creare false prove artistiche. Il WAV Gacrux, cache ASR e il dipinto provengono da precedenti artifact verificati con hash. La revisione è **privata** e non è un nuovo slot ArtVision 4×1.

## Primo ciclo V330 — evidenze REALI
- GitHub Actions: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43271274513 (SUCCESS).
- Artifact di sola revisione: 13968576928.
- MP4 nuovo: `BRUEGEL_THE_FALL_OF_THE_REBEL_ANGELS_CRITICO_STANDARD_V330_REVIEW.mp4`.
- SHA256 MP4: `3ab8240ab642133f60f6a27972290b58dd5de2a203a2a8ef60419e39b156d199`.
- WAV Gacrux originale SHA256: `e50f97bf6bf272bdda3a1b8577acf492f974d5c88d2b336d35cf976c5a814ade`.
- 115.8 s, 720×1280, 20 fps, FFmpeg full decode, ZIP CRC e SHA fisici: PASS.
- 18 frasi ASR → 54 JPG **dal vero MP4**, non dalla ricetta; revisione semantica e artistica tuttora PENDING.
- A/B V144→V330: sharpness Laplacian su frame decodificati 2058.222 → 2208.233 (**+7,29%** nei secondi 4–36). Questo indice non prova miglioramento artistico.
- Due lunghe sequenze statiche della V330: ~25,55s (3,5–29,05) e ~17,7s (98,05–115,75); il test segnala anche stacchi di camera da rivedere. **La V330 NON è stata promossa a Gold.**

## Secondo ciclo V331 — ipotesi verificabile
- Mantieni V144 e V330 INALTERATI; crea V331 come candidato separato.
- Riduci le lunghe pause visive: primi due capitoli e capitolo conclusivo usano **le seconde frasi da ASR reale** per alternare composizione generale → soggetto pertinente. Nelle parti panoramiche applica un piccolo spostamento/zoom motivato senza dipinto o musei generati.
- Conserva il passaggio autentico cielo → caduta sincronizzato con la frase del capitolo 4.
- Verifica V331 con FFmpeg, CRC ZIP, 54 screenshot frase e A/B contro ENTRAMBI V144 e V330.
- Il gate non accetta una riduzione trascurabile: richiede almeno **10 secondi in meno** di lunghe soste statiche rispetto a V330 e nessun calo medio di nitidezza superiore al 25% (se la composizione cambia, è un guard indicativo, non giudizio artistico).
- Anche con gate tecnici verdi restano obbligatori ascolto e visione a velocità normale, soggetto realmente visibile, diritti territoriali, eventuale confronto umano e approvazione separata.

## Secondo ciclo V331 — prova reale completata

- Workflow: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43272380718 — **SUCCESS**, 6 test offline PASS, stesso dipinto e SHA WAV, nessuna TTS.
- Artifact di revisione privata: `13967948513`, 30 giorni di conservazione, contiene MP4, ZIP, QA e 54 fotogrammi estratti.
- Nuovo MP4 V331 SHA256: `8010e97455cd5adb693074e16db9b1aecd9c9d0096ea6d8f8b959ad3cede59f9`.
- Durata 115,8s; 720×1280, 20fps, 2316 frame; byte MP4 22.763.516.
- ZIP `REBEL_ANGELS_CRITICO_STANDARD_V331_REVIEW_PACKAGE.zip` SHA256 `3918b2ec801b15491b8c2dc4bbd2f379feb53bf59de3c8ca598fb9a789e292d2`. FFmpeg full decode, ZIP CRC, frame SHA e verifica WAV: PASS.
- **Correzione misurata:** soglia V110 per intervalli di immobilità prolungata, V330 43,25s → V331 0s, miglioramento 43,25s. È un indice tecnico, non una garanzia di qualità per lo spettatore.
- Nitidezza A/B nel tratto misurato: **+7,32% rispetto a V330** e **+15,14% rispetto a V144** secondo la varianza Laplacian; non equivale a vero aumento di risoluzione sorgente.
- **Residuo:** `CAMERA_JUMP_REVIEW_REQUIRED`; i tagli semantici non vanno automaticamente nascosti con dissolvenze o ghosting. Richiede controllo umano del MP4 con voce. Il verdetto artistico e i diritti di pubblicazione sono PENDING; NON sostituire alcun master approvato.

## Regola di apprendimento anti-regressione
1. Registrare un difetto CON prova MP4 e tempo: non criticare soltanto ricette.
2. Modificare UNA classe di errori per volta; per V331: piani statici prolungati.
3. Produrre MP4 nuovo e verificarne i byte fisici, non il semplice commit o output da job.
4. Confrontare vecchio e nuovo, salvando due versioni distinte.
5. Se i valori o l'osservazione artistica peggiorano, conservare la baseline e NON promuovere.
6. Non trasformare una revisione tecnica in Golden Master o autorizzazione a pubblicare.

**Nessuna nuova chiamata Google/Vidu/OpenRouter, nessuna spesa, nessuna nuova automazione, pubblicazione o modifica dei master precedenti.**
