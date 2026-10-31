# ArtVision Böcklin NG 2/80 · DUE CINEMA MP4 reali con readback — 31/10/2026

## Identità e stato
- Arnold Böcklin, *Die Toteninsel* / *L'isola dei morti*, **terza versione 1883**, Alte Nationalgalerie Berlino, inventario **NG 2/80**, olio su tavola, **80×150 cm**.
- **2/4 varianti reali**: Cinema Standard **V100**, Cinema Museum **V101** (V100 Museum scartato per difetto di continuità). Entrambi H.264/AAC 720×1280 20fps, musica ambientale originale sintetizzata localmente senza API.
- **Critico Standard e Critico Museum ancora 0/2**: una singola WAV naturale Google Gacrux deve essere ottenuta solo dopo verifica quota/costo. Non produrre una voce robotica, non dichiarare il 4×1 finito.
- **Gold V25=0**, QA artistica umana integrale pendente, **R2/Android non verificato**, nessuna pubblicazione, nessuna settima opera, nessun costo API.
- I cinque lavori precedenti e i loro 20 slot/master/ZIP non sono stati alterati.

## Prove byte e QA
| Slot | File | Byte | SHA256 | Durata | Full decode |
| --- | --- | ---: | --- | ---: | --- |
| Cinema Standard | `Boecklin_1883_cinema_standard_V100_REVIEW.mp4` | 5.169.480 | `b176560a2d58e4aba6b782d2f02e3b5d22674fc7e16ea520620c83134bf90f26` | 44s | PASS |
| Cinema Museum | `Boecklin_1883_cinema_museum_V101_CONTINUOUS_ENTRY_REVIEW.mp4` | 6.086.102 | `c9f40502b5efdf216ebfe322344aed21f19913a2b869d144b2519bd2b3bd7132` | 52s | PASS |

- GitHub Actions V100 riuscita: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41219085045 (artifact 13049466256). Primo tentativo 41209993018 fallito **ffmpeg mancante**; corretto con binario imageio-ffmpeg e nuovo run riuscito.
- V100 Museum (SHA `6d6629e23d9af09b695c297c8767cc76ebf23e5ba1bf286e32bc49137ccd0ca7`) era tecnicamente integro ma visivamente **bocciato**: 0–12s inquadratura della cornice quasi immobile, salto duro al secondo 12 e ritorno brusco al 45.
- V101 solo Museum: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41219344125 (artifact 13049107776). Il renderer `src/artvision_bocklin_sixth_v101.py` usa foto cornice ad alta risoluzione 3600×6400, zoom geometrico continuo 1→5x e ritorno 5→1x, taglio registrato sulla stessa porzione del dipinto, **nessuna dissolvenza**. Non ritocca il Cinema Standard.
- QA visiva campionata su MP4 scaricati: differenza media assoluta grayscale ai confini 11,95→12,05s da **32,181** (V100) a **13,924** (V101); 44,95→45,05s da **33,027** a **14,354**. Migliora la continuità, **non equivale a validazione artistica definitiva**: permane differenza di resa tra foto della cornice e riproduzione.
- Audio AAC estratto del V100 Museum e V101 Museum **bit-identico** SHA ADTS `c7d6a1c400ee130265e7b38a888d8275fc6cb25ca2f9badbf5cd9392dd331003`.
- FFmpeg full decode **PASS** dei due MP4 anche dopo download di ritorno da Libreria.
- ZIP dei due Cinema scelti `BOECKLIN_NG2-80_TWO_CINEMA_V101_REVIEW_ANDROID.zip` (5 file, 11.587.816 B, SHA256 `0069b3d6a24d5c3d5df04f079c3a14a073af96d1549e168b70cacd54029a4430`), ZIP CRC PASS e download di ritorno SHA identico.
- **Libreria privata**: `/ArtVision/Bocklin/V101_TWO_CINEMA_REVIEW/` contiene i due MP4 singoli, ZIP due Cinema, QA_VERIFIED.json, README.txt, nonché gli artifact ZIP V100/V101 storici. Upload/download readback SHA dei due MP4 e ZIP combinato **identici**. Questo non è un archivio 4×1 completo.

## Fonti e licenze
- Museo: https://search.smb.museum/en/object/obj-967648 .
- Riproduzione fedele PD/PDM 1.0, 4933×2628, SHA256 `f9a7c33f1b7a2aae03aacd192706faee3740cfd9d1d277516dec39795f405ce3`.
- Foto della cornice dello **stesso esemplare**, Sailko 2018 **CC BY 3.0**, 4680×2742, SHA256 `72655ceea488c5f4ecf207dd5a419618685b0ee0c59d553f63cbbba0bb623b65`. La foto documenta la cornice nel 2018, **non** prova che sia originale ottocentesca.
- Sala Museum **ricostruzione digitale dichiarata**, NON vera Alte Nationalgalerie.
- R2/player Android rimane pendente: il plugin Video Library Studio Import richiede `fileParams` genuino selezionato dal proprietario. Non inventare upload o playback.

## Prossimo lavoro utile
- Non rifare V100 Standard né V101 Museum né altri 20 slot.
- Valutazione artistica integrale dei due Cinema; eventuali correzioni solo su difetti nuovi documentati.
- Critico: verifica quota/costo reale della WAV Gacrux prima di chiamata; poi generare una WAV unica e due MP4 distinti con 9 beat e sincronizzazione parola-scena, senza spesa non autorizzata.
- Mantenere Gold V25=0 finché il proprietario non approva; niente settima opera o social.
