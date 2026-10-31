# La Storia Rivive · V123 — QA visivo del contact sheet reale 1920

Data: 31 ottobre 2026. Ambito solo Restauro storico. Fonte davvero scaricata: `Filature et Tissage du coton (1920).webm`, SHA256 `e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9`, 66.553.161 byte, 1920×1080 FFprobe, durata 524,96s. Artifact originale con i byte del report: [run 41154281234](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41154281234/artifacts/13024616979). Artifact con il contact sheet fotografico realmente estratto: [run 41156453445](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41156453445).

## Esito della revisione visiva dell'assistente (NON approvazione dell'utente)

Ho esaminato il JPEG `ORIGINAL_FILM_CONTACT_SHEET.jpg` effettivamente prodotto dal runner su 12 PNG provenienti dalla pellicola originale. La valutazione delle immagini a bassa risoluzione è solo una prima esclusione editoriale, NON riconoscimento dei movimenti nel film completo.

| Frame | PTS approssimativo | Contenuto visibile nel contact sheet | Utilizzabile già ora come foto I2I? |
| --- | ---: | --- | --- |
| frame_01 | 0,00s | Logo animato/statico Pathé-Baby, non scena storica | NO |
| frame_02 | 43,76s | Macchina/cotone in attività, ma area centrale sovraesposta e poco leggibile | SOLO possibile ripresa da rivedere |
| frame_03 | 87,52s | Cartello scritto con sottotitoli | NO |
| frame_04 | 131,28s | Schema/disegno tecnico dei cilindri di lavorazione | NO: non è una fotografia di scena |
| frame_05 | 175,04s | Cartello scritto | NO |
| frame_06 | 218,80s | Bobine/macchinari veri, soggetti plausibili | Possibile ripresa, QA da fare |
| frame_07 | 262,56s | Cartello scritto | NO |
| frame_08 | 306,32s | Cartello scritto | NO |
| frame_09 | 350,08s | Telaio/filamenti di tessitura visibili | Possibile ripresa, QA da fare |
| frame_10 | 393,84s | Cartello scritto | NO |
| frame_11 | 437,60s | Cartello scritto | NO |
| frame_12 | 481,36s | Cartello scritto | NO |

**Criticità reale di V122:** il ranking visivo aveva selezionato `frame_04`, `frame_05`, `frame_06`, `frame_09`, `frame_10` per nitidezza/contrasto/PTS; solo **2 delle 5** sono immagini fotografiche di un macchinario. Non consentire spesa I2I o Vidu per le altre tre.

Nel campione originale 12 frame, **non si vedono 5 riprese fotografiche valide**, ma ciò **non esclude che il resto del lungo film (8m45s) ne contenga altre**. Per il prossimo tentativo occorre campionare in modo più intelligente i tratti tra i cartelli, non affermare che tutta la pellicola sia inadatta. Proiezione del sole/sfarfallio, grana, volti, mani, carattere 1080p upscaled e autenticità degli stacchi richiedono ancora revisione.

## Correzione tecnica V123, PR #147 (dipendente da #145)

- `src/storia_rivive_frame_rank_v101.py`: un filtro pixel-only **advisory e conservativo** marca a rischio di `LIKELY_INTERTITLE_LOGO_OR_BLACK_CARD` le immagini prevalentemente nere con piccole forme bianche ad alto contrasto, e `LIKELY_DIAGRAM_OR_LIGHT_CARD` i raster quasi interamente chiari. Non usa OCR, nessuna API e **non certifica il soggetto**; possibili falsi positivi e falsi negativi, che vanno sempre risolti guardando il film.
- Queste immagini vengono escluse dai 5 lavori fotografici; se restano meno di 5 si usa `INSUFFICIENT_PHOTOGRAPHIC_SCENE_CANDIDATES` ⇒ `SOURCE_REJECTED` nell'autopilota. Non forzare restauri di caratteri tipografici come se fossero persone o scene fotografiche.
- Nuovi unit test `tests/test_storia_rivive_v123.py` verificano intertitle, diagramma, macchinario geometrico e blocco selezione. I test non sostituiscono la prova sul film reale, che verrà eseguita nel workflow `.github/workflows/storia-v121-real-film-audit.yml`.
- Qualsiasi esito positivo del filtro rimane `REVIEW_REQUIRED`: per 5 vere riprese è necessario verificare foto, tagli, mani, volti e significato storico, più diritti Italia e gate V91/V94/V96/V99.

**Stato reale:** zero fotografie I2I approvate, zero clip Vidu, zero nuovi MP4/ZIP master, zero crediti API, nessuna pubblicazione. Benchmark SF1906 V98, ArtVision e WOW LAB invariati.
