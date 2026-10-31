# Böcklin NG 2/80 — V105 Critico Museum, raccordi prospettici reali (31/10/2026)

**Ambito:** revisione non distruttiva del solo slot `critico_museum`, da master V102; **NON** quinta variante, nessun altro render. Quattro slot Böcklin V103 e tutti i precedenti restano preservati. Due Cinema già apprezzati dal proprietario **immutati**; Critico Standard V102 **immutato**. Nessun TTS/Gacrux, workflow, API, acquisto o social.

## MP4 candidato fisico e verifica

- Master di partenza: `Boecklin_1883_critico_museum_V102_GACRUX_REVIEW.mp4` — **6.222.614 B**, SHA256 `03eb6c8a77c4572b7ca83c81088c4b3d499b06802dd996a97a505b6fe768a6ed`.
- Revisione: `Boecklin_1883_critico_museum_V105_CONTINUOUS_ENTRY_EXIT_REVIEW.mp4` — **14.442.272 B**, SHA256 `a90df875f26532137d1fd0e415bb3795be4f68f1c3ab9d854edb52ba087c662c`.
- **110,65 s, 720×1280, H.264 20 fps, 2.213 frame, AAC**. FFmpeg `-xerror` decodifica completa **PASS**.
- Traccia audio **ADTS bit-identica** al V102, SHA256 `3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e`. Nessuna rigenerazione vocale.
- Uniche finestre visive ricomposte su copia: frame **80–99** (4,00–4,95 s) e **2053–2072** (102,65–103,60 s). La restante regia è invariata a livello editoriale; il contenitore video è stato ricodificato CRF18, quindi i byte video degli altri frame non sono bit-identici al master.
- Fotogrammi originali già presenti nel master: registrazione SIFT + RANSAC delle due rappresentazioni dello stesso quadro, con 66/182/203 corrispondenze inlier. Ingresso: avanzamento geometrico nella fotografia incorniciata e passaggio alla riproduzione pittorica registrata; uscita: percorso inverso usando un frame fotografico più ampio, per evitare buchi e stiramenti al bordo superiore. Nessuna scena inventata, nessun fotogramma AI.

## Misure reali sul video decodificato

MAD = media della differenza assoluta tra frame grayscale consecutivi, ridotti a 180×320. Diagnostica del movimento, **non** giudizio artistico definitivo.

| Misura | V102 originale | V105 candidato |
|---|---:|---:|
| Salto al confine ingresso, 5,00 s | 40,46 | **1,68** |
| Salto al confine uscita, 103,65 s | 50,23 | **0,39** |
| Picco nell'intera finestra ingresso | 40,46 | **27,29** |
| Picco nell'intera finestra uscita | 50,23 | **31,55** |

Il nuovo picco in entrambe le finestre è inferiore alla soglia diagnostica 35/255. Ispezionati fotogrammi decodificati lungo entrata/uscita; non sono stati accettati prototipi intermedi con bordi rettangolari, cielo stirato o transizioni più brusche.

## Libreria e readback fisico

Cartella privata: `/ArtVision/Bocklin/V105_CRITICO_MUSEUM_CONTINUITY_REVIEW/`.

Caricati **MP4 candidato, QA_V105.json e renderer_V105.py**. Il MP4 è stato **scaricato nuovamente** dalla Libreria: **14.442.272 B**, SHA256 `a90df875f26532137d1fd0e415bb3795be4f68f1c3ab9d854edb52ba087c662c` identico all'output; **FFmpeg full decode del file scaricato PASS**.

**Stato:** V105 è soltanto `candidate_review_only`. Ascolto e visione umana integrali, sincronizzazione semantica frase–inquadratura e approvazione proprietario ancora pendenti. **Gold V25 = 0; R2/Android player non verificato.** Non sostituire il V102 selezionato né aggiornare la coda come Gold prima del parere umano. Nessuna settima opera o nuova automazione.
