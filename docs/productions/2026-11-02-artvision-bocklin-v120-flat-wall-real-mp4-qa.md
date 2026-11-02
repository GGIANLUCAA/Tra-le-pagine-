# ArtVision Böcklin V120 — QA fisica V118/V119 dei Museum, 2 novembre 2026

## Evidenza diretta (non render, non Gold)
Il pacchetto originale V107 `ARTVISION_BOECKLIN_4X1_V106_REVIEW_COMPLETO.zip` è stato materializzato dalla Libreria privata `/ArtVision/Bocklin/V106_REVIEW_4X1_ANDROID/` (46.200.145 byte, SHA-256 `e864f4803f5094b4a926c687921a0e64a2f2af24fca8087c1bb2be27cd812dc5`). Estratti **5 MP4 reali**, con SHA coincidenti con il manifest V107; nessun master sovrascritto.

Sono stati estratti e **osservati fotogrammi autentici** a 0,1–110 s per Critico Museum e 0,1–51 s per Cinema Museum, confrontati con gli Standard. In entrambi i Museum il quadro con cornice appare su una **parete grigia piatta, priva di pavimento, profondità architettonica, illuminazione/ombre di contatto e riferimenti metrici**. Non è una sala museale credibile secondo le nuove regole V118/V119. Il difetto è visibile già nell'introduzione e ricompare nell'uscita. Il renderer originale V102 `room(photo)` costruisce letteralmente un piano grigio RGB/BGR uniforme e vi incolla la foto; questa è la causa tecnica confermata per Critico Museum V102/V106. Cinema Museum V101 presenta visivamente la stessa tipologia di fondale.

### Misurazione ripetibile sui veri MP4
`src/artvision_museum_flat_wall_gate_v120.py` campiona con FFmpeg un frame a **0,20 s** e uno a **durata − 1,00 s**, scala 180×320, quantizza RGB in intervalli di 8 livelli e misura la frazione occupata dal colore più frequente. Soglia conservativa: **45% in entrambi gli estremi** = sospetto fondale piatto, review obbligatoria; il PASS non certifica fotorealismo.

| File reale | SHA-256 (prefisso) | Colore dominante intro | Outro | Gate |
|---|---|---:|---:|---|
| Critico Standard V102 | `096926e6ffb0` | 16,87% | 25,71% | Non segnalato |
| Critico Museum V102 master | `03eb6c8a77c4` | 70,35% | 65,13% | **FLAG** |
| Critico Museum V106 candidato | `c1c54dba4f01` | 70,07% | 64,65% | **FLAG** |
| Cinema Standard V100 | `b176560a2d58` | 14,66% | 6,62% | Non segnalato |
| Cinema Museum V101 | `c9f40502b5ef` | 64,81% | 49,85% | **FLAG** |

Risultato reale: gate 3/3 Museum segnalati (compreso il master V102) e 0/2 Standard segnalati. Campionamento e osservazione diretta di frame **non** equivalgono ad ascolto integrale, playback smartphone a velocità normale o QA completa frase-inquadratura. Nessuna nuova certificazione di sincronizzazione audio.

## Decisione anti-regressione
- **Böcklin Critico Museum V106 e Cinema Museum V101: non promuovere a prodotto Museum finale/Gold** finché ingresso e uscita non sono ricostruiti in un ambiente 3D/fotografico credibile con dimensioni reali **80×150 cm**, materiali, pavimento, luce, prospettiva e cornice documentata, con QA reale del nuovo MP4.
- **Non cancellare il feedback positivo storico sul Cinema Museum V101**: il nuovo blocco è una valutazione specifica alla regola V118/V119 più recente, non una negazione dell'apprezzamento iniziale.
- **V112 e V113**: nel JSON di coda risultano render locali tecnicamente riusciti ma **MP4 non persistiti in Library** per `library_storage_limit_exceeded`. Non sono stati verificati in questa esecuzione; non promuoverli automaticamente né ripetere rendering a vuoto.
- Preservare V102/V105/V106/V109/V110/V112/V113 e tutti gli Standard/Cinema originali. Nessuna nuova voce Gacrux, AI, costo, pubblicazione, ZIP o settima opera. Gold V25 = 0.
- R2/Android **non verificato**; l'import del plugin richiede un fileParams genuino scelto dal proprietario. Non dichiarare upload/player.

Il gate è un **filtro negativo**: blocca una regressione visiva nota, ma un video non segnalato può comunque avere museo falso, scala sbagliata, cornice errata o cattiva regia. Richiede sempre revisione artistica umana V118/V119.
