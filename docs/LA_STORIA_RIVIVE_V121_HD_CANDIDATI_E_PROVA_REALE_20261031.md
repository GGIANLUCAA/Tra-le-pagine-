# La Storia Rivive V121 — tre possibili pellicole HD per nuovi piloti (NON APPROVATE)

Ricerca pubblica 31/10/2026; conservare i sette vecchi titoli V58 solo come materiale di studio 480p/576p (audit separato). Questi tre URL sono **nuovi candidati**, non asset, video creati o diritti convalidati.

| ID | Tema e motivo editoriale | Commons file originale | Quota scaricamento | Diritto e QA |
|---|---|---|---|---|
| `france_cotton_mill_1920` | Macchine, operai e gesti della filatura/tessitura 1920; soggetto industriale con potenziale sorpresa visiva | [Filature et Tissage du coton (1920)](https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm), video dichiarato 1920×1080 / 63.47 MB | Sotto 160 MiB | PD/PDM dichiarato Commons, ma autore sconosciuto, fonte YouTube; **diritti Italia e dettaglio reale non verificati** |
| `white_house_1917_1921` | Pecore sul prato della Casa Bianca, parate e scene insolite del periodo | [Video Clips of Woodrow Wilson, part 1](https://commons.wikimedia.org/wiki/File:Video_Clips_of_Woodrow_Wilson_(1917-1921,_Part_1).webm), 1920×1080 / 117.74 MB | Sotto 160 MiB | NARA, marcatura public domain U.S. Federal Government; **date di singole scene e diritti residui in Italia da verificare** |
| `versailles_treaty_1919` | Arrivi e cerimonia Versailles 1919, folle e dettagli di firme/volti | [Treaty of Versailles (16 fps)](https://commons.wikimedia.org/wiki/File:The_signing_of_the_peace_treaty_of_Versailles_(16_fps).webm), 1920×1080 / 44.1 MB | Sotto 160 MiB | Commons indica pubblico dominio USA, ma **avverte che potrebbe non esserlo fuori dagli USA**. Uso in Italia sospeso finché verificato |

Le tre pellicole sono state aggiunte al banco editoriale `queue/storia_rivive_candidates_v58.json` con metadati verificabili e **nessun flag `rights_italy_verified`, `source_native_visual_review`, `historical_attribution_verified` o `original_film_sha256_verified`**. V101 mantiene `blocking_issues` e V102/V118 vietano I2I finché i gate non sono soddisfatti. Nessun consenso Vidu o social viene concesso.

### Esperimento reale gratis su prima fonte

Workflow PR-isolato `.github/workflows/storia-v121-real-film-audit.yml` seleziona **soltanto** il documentario cotoniero, senza schedulare a pagamento nulla e senza mettere i file originali negli artifact. Legge i metadata Commons; se il film è entro 160 MiB, scarica il WebM autentico, confronta file size/SHA, verifica il raster effettivamente decodificato con `ffprobe`, campiona 12 PNG e rileva candidati di tagli FFmpeg. Pubblica nel solo artifact GitHub Actions i JSON `SCOUT_REPORT.json` e `REAL_FILM_AUDIT_V121.json`, **non** un video finito.

Se la richiesta Wikimedia è rifiutata, il workflow dura troppo o i candidati tagli sono insufficienti, registrare lo stato di errore reale. Non falsificare pass, non sostituire il test con clip synthetic HD e non procedere verso I2I/Vidu senza analisi dei fotogrammi, conferma di riprese realmente diverse, valutazione diritti Italia e fedeltà degli oggetti.

### Vincoli anti-regressione

- Dimensione *1920×1080* nel sito significa raster nominale del file, non scansione 2K né volto realmente nitido. Verificare visivamente il film e non fare 1080p upscaled come prova di dettaglio.
- `france_cotton_mill_1920` non diventa pronto alla pubblicazione perché Commons mostra una licenza. Lo stesso vale per gli altri due.
- Lo schema finale resta quello V98: quattro I2I autentiche + una Vidu source-locked, cinque **vere** riprese, durata 14–35 s, QA V91/V94/V96/V99 sui byte finali + revisione artistica.
- No spesa, ricariche, acquisti, pubblicazione, modifiche ArtVision/WOW LAB o automatizzazione master ogni tre ore prima di tre piloti reali.
