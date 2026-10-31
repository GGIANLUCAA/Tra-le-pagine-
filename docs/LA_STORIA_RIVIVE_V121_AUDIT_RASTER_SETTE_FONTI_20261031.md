# La Storia Rivive · V121 — audit reale del raster originale della coda V58

Data controllo: 31 ottobre 2026. Ambito esclusivo Restauro storico; nessun MP4 nuovo e nessun permesso di pubblicazione.

## Problema rilevato nelle schede originali Commons

Tutti i **sette** filmati correntemente inseriti in `queue/storia_rivive_candidates_v58.json` sono sotto la soglia tecnica V109: altezza nativa pubblicata almeno 720 px e larghezza utile per crop 9:16 almeno 400 px. Non sono sorgenti HD adeguate per quattro fotografie I2I con volti fedeli al livello V98, anche se potrebbero essere utili a studio/storia.

| Candidate id | Raster del file originale pubblicato | Larghezza utile 9:16 | Fonte indipendente della misura | Stato V121 |
| --- | --- | --- | --- | --- |
| `paris_swim_1918` | 768×576 | 324 px | [Commons AI83969](https://commons.wikimedia.org/wiki/File:F%C3%AAte_Am%C3%A9ricaine_et_la_foule_pendant_la_travers%C3%A9e_de_Paris_%C3%A0_la_nage_-_AI83969.webm) | SKIP raster |
| `paris_train_1918` | 768×576 | 324 px | [Commons AI139599](https://commons.wikimedia.org/wiki/File:Arriv%C3%A9e_d%27un_train_de_Marseille_et_voyageurs_dans_la_cour_de_la_gare_de_Lyon._La_travers%C3%A9e_de_Paris_%C3%A0_la_nage_-_AI139599.webm) | SKIP raster |
| `beirut_1919_street` | 768×576 | 324 px | [Commons AI13347](https://commons.wikimedia.org/wiki/File:Sc%C3%A8nes_de_rue_-_AI13347.webm) | SKIP raster |
| `paris_cafe_strike_1919` | 768×576 | 324 px | [Commons AI94492](https://commons.wikimedia.org/wiki/File:La_Gr%C3%A8ve_des_gar%C3%A7ons_de_caf%C3%A9_-_AI94492.webm) | SKIP raster |
| `paris_champs_1918` | 768×576 | 324 px | [Commons AI53745](https://commons.wikimedia.org/wiki/File:Avenue_des_Champs-%C3%89lys%C3%A9es%2C_place_de_la_Concorde_-_AI53745.webm) | SKIP raster |
| `market_rural_1920` | 768×576 | 324 px | [Commons AI140423](https://commons.wikimedia.org/wiki/File:March%C3%A9_couvert_et_sc%C3%A8nes_rurales_-_AI140423.webm) | SKIP raster |
| `china_daily_life_1928` | 720×480 | 270 px | [Commons China 1920s](https://commons.wikimedia.org/wiki/File:China_and_the_Chinese%2C_1920s_-_Travelfilmarchive.webm) | SKIP raster + territorial rights |

Queste sono **dimensioni dei video originariamente caricati su Commons**, non dell'originale negativo 35mm conservato in museo. Se il museo fornisce una nuova digitalizzazione realmente HD, può essere valutata come nuova sorgente con licenza e SHA propri. Non forzare HD moltiplicando pixel già disponibili o inventando persone.

## Correzione tecnica implementata nel ramo della PR #147

- `src/storia_rivive_scout_v101.py` legge `width` e `height` dell'`imageinfo` ufficiale Commons **prima** di aprire il download del video. Mancanza di dimensioni autentiche ⇒ `SOURCE_RASTER_METADATA_MISSING_SKIP_DOWNLOAD`.
- Se il file è 768×576 o 720×480, il preflight risponde `SOURCE_NATIVE_DETAIL_INSUFFICIENT_SKIP_DOWNLOAD`, non crea file video, non avvia FFmpeg, I2I o Vidu. Altezze native almeno 720 pixel e crop 9:16 almeno 400 pixel sono solo requisiti minimi, non approvazioni.
- Se la scheda passa, `ffprobe` verifica **anche i byte realmente scaricati**: larghezza e altezza decodificate devono coincidere con il metadata Commons oppure scatta `SOURCE_DECODED_RASTER_DIFFERS_FROM_COMMONS_ORIGINAL_METADATA`.
- `.github/workflows/storia-rivive-v101-auto-3h.yml` registra `native_original_raster_px` e `native_media_rejected_before_download` in `CYCLE_STATUS.json`; rifiuta la fonte con `SOURCE_REJECTED` e rigenera la cache come `v7-native-raster-preflight`. Il cron resta **solo di ricerca**, non diventa un generatore video.
- Test unitari offline V121 simulano API Commons, risoluzioni reali della coda e verificano che per le fonti povere **non sia chiamato il download**. Un test separato codifica un breve MP4 1280×720 con FFmpeg e ne verifica il raster tramite FFprobe, distinguendo così il controllo sui byte dalla sola scheda metadata. Non è una pellicola storica e non certifica cinque riprese.

## Limiti reali e prossimo passo

Questo controllo è fondato sulle **schede Commons**, non su sette file WEBM fisicamente scaricati e decodificati in questa esecuzione. Il confronto `ffprobe` verrà eseguito solo su nuove fonti che superano la prima soglia. Sono ancora da reperire una o più scansioni HD autentiche; cinque **vere** riprese distinte, diritti Italia e volti leggibili restano da verificare. Le schede CC0 Commons sono un'indicazione di licenza, non da sole una certificazione di ogni diritto; il film China riporta condizioni territoriali particolari.

Nessuna modifica dei vincoli Vidu, dei crediti, dei gate V91/V94/V96/V99, dei master V98, ArtVision o WOW LAB. Non etichettare mai un `SOURCE_REJECTED` come nuovo episodio prodotto.
