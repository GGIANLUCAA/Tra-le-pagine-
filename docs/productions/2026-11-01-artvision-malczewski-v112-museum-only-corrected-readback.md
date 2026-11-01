# ArtVision · Malczewski Błędne koło · V112 — solo i due Museum corretti
**Data 1 novembre 2026 · nuovi MP4 REALI, backup Library readback fisico, human review pending, Gold V25 = 0.**

## Feedback dell'utente
«Bello mi è piaciuto… più veloce degli altri… unico difetto… parte con le cornici e musei… lunghezza, soggetto del quadro e spiegazione mi è piaciuta.»
**Preservare integralmente** copione, durata, voce/colonna sonora, inquadrature della spiegazione, e i due Standard. Non rigenerare TTS, non produrre ottava opera e non sovrascrivere master.

## Difetto riprodotto sui veri V111
Le inquadrature d'ingresso/uscita Museum V111 erano una parete grigia piatta, cornice sottile e poco credibile, pavimento sostanzialmente inesistente, blocco inferiore grafico. Screenshot reali V111 estratti dai MP4 Library. La cinepresa non entrava in un vero ambiente spaziale; esce senza sensazione prospettica.

## Correzione concreta V112
Sostituite **soltanto** le finestre:
- Critico Museum: ingresso frame 0–99 (0–5s); uscita ultimi 120 frame (83,1–89,1s); parte centrale invariata editorialmente.
- Cinema Museum: ingresso frame 0–159 (0–8s); uscita ultimi 180 frame (43–52s); parte centrale invariata editorialmente.
Nuova ricostruzione **digitale dichiarata**, non stanza reale del Museo Nazionale di Poznań; luce da soffitto, pareti materiche, profondità pavimento, panca e targa laterale discreta. Cornice scura ebronzo/bronzo dorato ricostruita graficamente guardando fotografie del dipinto incorniciato, **non** autenticata come cornice storica, né fotografia libera da copyright usata come fotogramma. Quadro al vero rapporto 240×174 cm; camera da sala a esatto crop del ragazzo sulla scala, poi ritorna progressivamente alla stessa sala. Durante i dettagli centrali cornice assente.
Fonte in alta risoluzione autentica già usata V110, recuperata nel solo workflow GitHub Actions read-only `41262960601`, SHA256 **0ff83e09be9465a696b8956065f93ddd78f9fb3c1f1e8ebd87b98bc792cad5b9**, 5026×3557.
Python renderer: `src/artvision_malczewski_v112_museum_refinement.py` + sorgente master V111 conservata in Libreria.

## Prove sui MP4 V112 e readback
| Slot revisionato | Durata | Byte | SHA256 | QA |
|---|---:|---:|---|---|
| Critico Museum | 89,10s | 18.714.185 | `e5968d0afc9764d5ecc1e50037326fe780a4460fbcf1a661d921f24f2f49e677` | FFmpeg -xerror PASS, AAC bit-identico V111, SHA Library readback PASS |
| Cinema Museum | 52,00s | 15.970.682 | `baf89b0afc03a0c906382b8bc82fb20328de88768ef036ed599c58cb36036638` | FFmpeg -xerror PASS, AAC bit-identico V111, SHA Library readback PASS |

Videogate scala originale 720×1280, 20 fps, H264/AAC. Video completo ricodificato CRF19: frame centrali preservati editorialmente ma byte compressi non bit-identici.
Misura MAD grayscale 180×320 fra frame consecutivi su file finali (valori bassi = nessun salto brusco automatico, NON review artistica):
- Critico ingresso a 5,00s: **1,306**; uscita 83,10s: **0,094**.
- Cinema ingresso a 8,00s: **1,186**; uscita 43,00s: **0,021**.
MAD nei capitoli centrali V111 vs V112 a campione ~1,7–1,8/255 (sole differenze di ricodifica).
Due MP4 copiati in Libreria `/ArtVision/Malczewski/V112_DUE_MUSEUM_CORRETTI_REVIEW/`, riscaricati effettivamente in container separato: stessi byte, SHA256 identici e full decode FFmpeg PASS su **entrambe copie riscaricate**.
ZIP `ARTVISION_MALCZEWSKI_DUE_MUSEUM_CORRETTI_V112.zip`: 35.429.176 B SHA256 `fedfb977cf73fd9b9a4a1279d4f0147df335b6f5df41bcbf5625455f46cf70a4`, 7 membri, CRC PASS e Libreria readback SHA-identico.
In Libreria anche 2 nuove copertine, confronto real-frame V111/V112, gallery preview, QA e README, script di renderer.

**Preservati** i Critico Standard e Cinema Standard V111 byte-identici e tutte le V110/V111 precedenti. V112 è revisione **dello stesso slot**, non quinto e sesto video; nessuna ottava opera, nessuna spesa, nuova voce, workflow TTS o social. **Gold V25=0**, perché il proprietario non ha ancora giudicato le nuove Museum. R2/site/player Android **non verificato**. Nessun fallace claim di sala reale o cornice storica.

Fonti di contesto: <https://mnp.art.pl/en/project/bledne-kolo-2> ; <https://mnp.art.pl/galeria-malarstwa-i-rzezby/malczewski-w-nowej-aranzacji> ; scan PD <https://commons.wikimedia.org/wiki/File:Bledne_kolo.jpg>.
