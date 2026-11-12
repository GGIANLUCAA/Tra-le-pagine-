---
name: artvision-video-evidence
description: "Usa questa skill quando devi verificare MP4, ZIP, fonti, QA, hash, link Android o affermazioni di completamento dei video ArtVision e La Storia Rivive. Richiede prove reali prima di dichiarare un deliverable pronto."
---

# ArtVision: evidence before completion

## Prima verifica il contesto
- Leggi `AGENTS.md`, `docs/REGOLE_ATTIVE.md` e le regole della serie.
- Verifica presenza e accessibilità dei *byte reali* del video, non solo manifest, nome, thumbnail o log. Non dichiarare scaricabile un file solo perché esiste una release.
- Conserva l'originale e gli hash; ogni revisione genera un nuovo artefatto. Non sovrascrivere Gold o audio approvato.

## QA tecnico disponibile nel repository
Quando l'MP4 è accessibile **localmente** a un ambiente con FFmpeg, genera un report offline con:

```bash
python src/ai_director_visual_qa_v1.py --video /percorso/video.mp4 --output /percorso/qa_visual.json
ffprobe -v error -show_format -show_streams -of json /percorso/video.mp4
ffmpeg -v error -xerror -i /percorso/video.mp4 -f null -
sha256sum /percorso/video.mp4
```

Interpretazione: `ai_director_visual_qa_v1.py` controlla solo indizi tecnici (tagli sospetti, nero, tracce); può analizzare soltanto i primi 240 s. Non prova sincronizzazione semantica, diritti, autenticità o bontà artistica. Il comando `ffmpeg` serve per verifica di decodifica completa, non per giudizio regia.

Se esistono progetto V13 e i relativi asset, esegui il controllo pertinente:

```bash
python src/quality_director_v17.py --project /percorso/PROJECT_V13.json --video /percorso/video.mp4 --out /percorso/qa_v17
```

Se il formato è La Storia Rivive 4+1 usa il gate esistente e il suo manifest **effettivo**:

```bash
python src/storia_rivive_final_gate_v91.py --video /percorso/video.mp4 --manifest /percorso/final_qa.json
```

Non usare manifest inventati per ottenere PASS; mantieni V94/V96/V99 e V323. Se il comando non può girare, segnala `NOT_RUN` con causa.

## Controlli distinti (nessuna scorciatoia)
1. **Tecnico**: video/audio realmente decodificabili, durata, dimensioni, codec, SHA256, ZIP CRC.
2. **Fedeltà e diritti**: fonte precisa, provenienza, licenza, trasformazioni AI dichiarate, volti/oggetti non inventati; cornici/scala se Museum.
3. **Artistico**: visionare MP4 intero, ascoltare WAV/audio e verificarne l'allineamento con scene, ritmo e titolazione. Serve revisione umana reale, non solo lint o metadata.
4. **Disponibilità Android**: link all'asset esatto, dimensione dichiarata, eventuale SHA, prova download completo/byte readback. Se non verificata, scrivere `DOWNLOAD_UNVERIFIED`.
5. **Pubblicazione**: bloccata salvo autorizzazione distinta, controllo provenienza e QA; il successo tecnico non sblocca sito/social.

## Stati da dichiarare
- `TECHNICAL_PASS_ARTISTIC_PENDING`: report tecnico vero, revisione artistica non completata.
- `UNVERIFIED_MEDIA`: MP4 o contenuto integrale non disponibile.
- `BLOCKED_RIGHTS`: licenza/provenienza insufficiente.
- `RENDERED_NEEDS_REVIEW`: candidato esistente, nessuna approvazione Gold.
- `FINAL_APPROVED`: solo quando tutte le condizioni del progetto sono state realmente documentate, mai per deduzione da un workflow.

Non fare nuovi POST Vidu, chiamate pagate, rilanci massivi o pubblicazione per verificare un video. Riporta link, prove, fallimenti e cosa manca, senza numeri inventati.
