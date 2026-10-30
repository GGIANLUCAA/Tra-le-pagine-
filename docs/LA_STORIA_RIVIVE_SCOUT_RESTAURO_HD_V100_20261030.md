# V100 — Servizi di restauro storico HD gratuiti: audit e prove sicure (30/10/2026)

**Ambito:** esclusivamente `La Storia Rivive`. Non modifica ArtVision, Vidu, i preset, i video esistenti, il montaggio V96 o i segreti. Questo branch contiene **ricerca + sonde GET in sola lettura**, non un nuovo renderer e non un MP4 finito.

## Prima di introdurre nuove tecnologie: cosa esiste già

- `src/storia_rivive_real_ai_v60.py`: **DDColor** (Alibaba DAMO), colorizzazione semantica.
- `src/storia_rivive_director_cut_v63.py`: **Real-ESRGAN** sulle fotografie; *non* è di per sé ricostruzione moderna sufficientemente fotografica.
- `src/storia_rivive_v77_safe_photo_generator.py`: **Finegrain image-to-image** mediante API Gradio pubblica, input da vero fotogramma, inventory di oggetti, denoise conservativo <=0.27, output sempre in review.
- `src/storia_v98_bombay_five_photos.py`: Finegrain reale per cinque fotogrammi Bombay 1929, con maschere, log e QA. Preset V98 usa denoise 0.45 (potenziale rischio identità); non replicare ciecamente.
- `src/storia_v80_ellis_face_gfpgan_video.py` e `src/storia_v82_ellis_modern_faces.py`: **GFPGAN** volto, locale, in regioni preselezionate.
- `src/storia_rivive_v96_guard.py`: vincoli anti-hallucination / foto vere / temporizzazione / continuità Vidu. Restano obbligatori.
- Finegrain **è già il servizio di rigenerazione delle fotografie cercato dall'utente**. Non costruire una seconda pipeline equivalente in produzione.

## Scelte consigliate

| Soluzione | Paese/origine | Per cosa | Costo e API | Stato |
|---|---|---|---|---|
| Finegrain Image Enhancer, Hugging Face Space | servizio internazionale | Image-to-image fotorealistico, già integrato | Demo API Gradio pubblica su ZeroGPU, quote ristrette | **Operativo nel codice, qualità QA non garantita** |
| CodeFormer, Space ufficiale sczhou | Cina/Singapore NTU | Volto molto degradato, solo ROI dopo analisi | Demo Space ZeroGPU e API Gradio; licenza NTU S-Lab, verificare uso | **Candidato per prova A/B**, mai sostituzione identità |
| GFPGAN TencentARC | Cina | Volti autentici già abbastanza grandi | Codice Apache 2.0, CPU/GPU locale; Space storico `tkawano/GFPGAN` non più reperibile | **Già integrato localmente**, preferire a Space non ufficiale |
| DDColor (Alibaba DAMO) | Cina | Colorizzazione fedele di foto B/N | Codice Apache 2.0, inference locale | **Già integrato; pre-processing, non finale** |
| Real-ESRGAN (Tencent ARC) | Cina | Super-risoluzione di foto / sfondi | Software libero, CPU/GPU proprie; non una API gratuita garantita | **Già usato; non sufficiente da solo** |
| SeedVR2 (ByteDance Seed) | Cina | Restauro TEMPORALE di sequenza filmata reale | Modello open source Apache 2.0, GPU potente; **nessuna API ufficiale gratuita del team** verificata | **Ricerca GPU in prova, disabilitato** |
| PaddleGAN (PaddlePaddle/Baidu) | Cina | Old-video: interpolazione + colorizzazione + EDVR | Software Apache 2.0, GPU/CPU propri, non API cloud gratuita | **Ricerca, non montare automaticamente** |
| HYPIR (XPixelGroup) | Cina | Restauro generativo image-to-image | Codice/model non-commercial only; Colab GPU free quando disponibile; no garanzia automazione | **Disabilitato per rischio licenza e GPU** |
| Qwen Image Edit (Alibaba Cloud Model Studio) | Cina | Editing fotografico sorgente-guidato, ma può inventare | Per nuovi utenti circa 100 immagini gratuite/modello nei mercati specifici per 90 giorni, dopo possono partire addebiti | **Disabilitato: nessuna fatturazione senza consenso e stop only-free confermato** |

### Vincoli reali del gratuito cloud

**Hugging Face ZeroGPU:** documentazione ufficiale indica ~2 min/giorno anonimo, ~5 min/giorno per account gratuito, non illimitato. App pubbliche sono API Gradio, MA un GET del loro schema NON dimostra che il job GPU possa girare gratis ora. Solo test POST con quota e token idonei potrà provarlo. Usare un token personale solo come `HF_TOKEN` GitHub Actions secret, mai pubblicarlo.

**Alibaba:** free trial con validità limitata, regioni e condizioni variabili; dopo consumo possono esserci costi. Non dare per scontato 'zero carta'. Nessun endpoint Alibaba viene chiamato dal probe.

**Google Colab Free:** GPU ad accesso interattivo con limiti dinamici. FAQ vietano usare free Colab come worker remoto automatizzato aggirando interfaccia o con account multipli. Non trasformarlo in un servizio invisibile dietro GitHub Actions.

**GitHub Actions:** runner CPU usabile per scout e passaggi leggeri, ma non fornisce automaticamente le GPU necessarie a SeedVR2; il suo uso può consumare minuti di Actions.

## Esperimento V100: ordine obbligatorio

1. Prova read-only su **stato Space e OpenAPI** (script `tools/storia_free_restoration_api_probe_v100.py`, GET soltanto, senza autenticazione, immagini o GPU).
2. Uno stesso fotogramma archivistico autentico, con SHA e almeno ±2 frame contigui, provare candidate **Finegrain** (attuale) e **CodeFormer/GFPGAN**, **solo** dopo quota gratuita verificata.
3. Confrontare 1:1: volti, numero di persone, oggetti (carro/scala/bagaglio, niente oggetto->persona), geometria, saturazione naturale, texture, bordi, differenze dalla fonte. Misurare nitidezza, ma nessuna metrica da sola approva.
4. Il video originale in B/N rimane identico; cambiano solo i fotogrammi restaurati dopo freeze, se approvati. Niente zoom scambiati per scene e niente modelli che ridisegnano i soggetti.
5. Ogni candidata resta **PENDING_HUMAN_QA** prima della promozione. Stop se quota esaurita, se pannelli/API non disponibili, o se licenza non idonea. Zero fallback a pagamento.
6. Solo a prova riuscita valutare adapter opzionale per nuovi provider e QA automatico V96. Nessun ritorno a DDColor-only come 'HD moderno'.

## Fonti ufficiali (da verificare per eventuali cambiamenti)
- Hugging Face ZeroGPU: https://huggingface.co/docs/hub/spaces-zerogpu
- Hugging Face Space API: https://huggingface.co/docs/hub/spaces-api-endpoints
- Finegrain: https://huggingface.co/spaces/finegrain/finegrain-image-enhancer
- CodeFormer: https://huggingface.co/spaces/sczhou/CodeFormer
- GFPGAN: https://github.com/TencentARC/GFPGAN
- DDColor: https://github.com/piddnad/DDColor
- Real-ESRGAN: https://github.com/xinntao/Real-ESRGAN
- SeedVR2: https://github.com/ByteDance-Seed/SeedVR
- PaddleGAN old video: https://github.com/PaddlePaddle/PaddleGAN/blob/develop/docs/en_US/tutorials/video_restore.md
- HYPIR: https://github.com/XPixelGroup/HYPIR
- Alibaba free quota: https://www.alibabacloud.com/help/en/model-studio/new-free-quota
- Google Colab FAQ: https://research.google.com/colaboratory/intl/it/faq.html
