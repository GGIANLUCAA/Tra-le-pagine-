# TRA LE PAGINE — STUDIO IBRIDO V6
*Estensione modulare senza ricostruire il sistema. Ricerca e primo impianto: 20 ottobre 2026.*

## Regola assoluta: mantenere il motore
Il nucleo operativo rimane **GitHub Actions + Gemini TTS + FFmpeg + regia armonica V5**. Non sostituire `src/render.py`, `src/episode_v3.py`, `src/regia_armonica_v5.py` o il workflow `render-v3.yml`. Conservare ogni episodio e ogni effetto storico. Il V6 non modifica la produzione, non la pubblica e non consuma crediti.

**Da leggere quando un utente chiede un nuovo video:** questo file, `METODOLOGIA_TRA_LE_PAGINE_V3.md`, `GUIDA_REGIA_ARMONICA_V5.md`, `config/studio_ibrido_tools.json`. Poi creare *soltanto* una nuova cartella episodio e i relativi dati. **Mai riscrivere il motore perché cambia il titolo della storia.**

## Cosa funziona già nella PR V6
- Catalogo **23 motori e servizi** con URL e stato di adozione: `config/studio_ibrido_tools.json`.
- Selettore **deterministico** di inquadrature: `src/studio_ibrido_v6.py`. È una proposta tecnica, non un'AI creativa autonoma.
- Lettura `scene_cues.json`, metadati e immagini disponibili (`scene_premium.zip` oppure cartella `images/`).
- Riciclo delle immagini senza ripetere chiamate di generazione; riconoscimento di scene che riutilizzano un asset.
- Pacchetto in `output/studio_ibrido/`: `PIANO_SCENE_V6.json`, `STORYBOARD_V6.html`, `CATALOGO_TOOLS_V6.json`.
- Workflow manuale `.github/workflows/studio-ibrido-v6.yml` e test automatici della PR: solo Python standard library.
- Quattro formati aggiuntivi al format libri: cronaca, documentario, fiabe e social; **nessun nuovo motore video è stato ancora collaudato**.

## Uso rapido su GitHub dal telefono
1. Aprire il repository → **Actions** → **Tra le Pagine - Studio Ibrido V6**.
2. Premere **Run workflow** e inserire lo *slug* dell'episodio che esiste in `episodes/`, ad esempio `03_siddharta`.
3. Scegliere *formato* e *budget zero*. Avviare.
4. Aprire la run riuscita → **Artifacts** → scaricare `STUDIO_IBRIDO_V6`.
5. Aprire `STORYBOARD_V6.html` e controllare l'ordine delle scene sul telefono.
6. Approvare o correggere **copione, fonti, immagini e regia** prima di qualsiasi generazione vera.

Da un ambiente Python nella radice del repository:
```bash
python src/studio_ibrido_v6.py --episode 03_siddharta --format libri --budget zero
python -m unittest discover -s tests -p "test_studio_ibrido_v6.py" -v
```
Questo comando **non crea MP4**: prepara scene e suggerimenti. Per produrre MP4 si usa il workflow V5 esistente, dopo approvazione e completamento delle immagini.

## Roadmap a moduli e loro costi reali
**Fase A (già aggiunta al ramo V6, zero API):** catalogo tool, rapporti, HTML storyboard, controllo fonti minime e scena/asset. Le librerie V5 e la voce Gemini restano identiche.

**Fase B (candidati a costo zero *solo con capacità di calcolo disponibile*):**
- Test `Qwen3-TTS` con narrazione italiana su un testo campione, confronto A/B con Gemini. GPU in esecuzione, checkpoint separati, consenso per eventuale voice cloning. La libreria Apache 2.0 non rende gratuita la GPU.
- Test `Z-Image-Turbo` e `Qwen-Image` (versione originaria) su 2 inquadrature singole 9:16, attenzione a mani, ambienti e identità. Non usare `Qwen-Image-2.1` nei video commerciali con licenza RESEARCH non commerciale.
- Test `Real-ESRGAN` su un dettaglio, mantenendo un confronto originale/elaborato. Non sostituire in automatico tutte le immagini.
- Test `PaddleOCR` solo per individuare scritte spurie e `PySceneDetect` per analizzare video importati.
- Test `FunClip` per estrarre segmenti da video di cui si posseggono diritti.

**Fase C (GPU remota o locale, non automatica):**
- `Wan2.2` e `HunyuanVideo-1.5` per 1–2 scene veramente adatte al movimento; sempre rispetto del copione e dei volti.
- `CogVideoX` e `RIFE` soltanto dopo confronto di artefatti, costi e licenze.
- `LivePortrait` richiede particolare attenzione ai pesi di InsightFace con restrizioni non commerciali.
- `ComfyUI` come possibile orchestratore esterno, **non** come sostituto del montaggio GitHub.

**Fase D (servizi esterni opzionali):** StarryKit (grafiche), Uniscript (caroselli) e II Content Engine (idee riutilizzabili). Non connessi dal V6; non importare cookie di browser né segreti nel repository.

### Distinzione dei costi
`budget=zero`: nessuna richiesta API o download; soltanto pianificazione sulla CPU esistente. **Costo API del pianificatore: zero, non promessa che tutto il video costi zero**. Il motore V5, con Gemini, può consumare quota di utilizzo del relativo account.

`budget=basso`: il rapporto indica *candidati da testare* per scena; non li attiva. Un futuro adapter GPU dovrà avere un interruttore esplicito, stima preventiva, limiti di spesa, output separati, fallback su V5 e autorizzazione.

## Cronaca: requisito di tracciabilità
Per format `cronaca` e `documentario`, allegare un file `episodes/NOME/fonti.json`:
```json
[
  {"titolo":"Fonte primaria con data e autore","url":"https://esempio.it/documento"},
  {"titolo":"Seconda fonte indipendente","url":"https://altro-esempio.it/analisi"}
]
```
Il controllo V6 riconosce soltanto la **presenza** di due domini distinti: **non dimostra** la correttezza o indipendenza delle fonti. La verifica editoriale rimane umana. Testimonianze e immagini sintetiche non devono essere presentate come autentici filmati di cronaca; le ricostruzioni vanno indicate come tali.

## Come integrare davvero altri motori senza rovinare il lavoro
Ogni futuro adapter deve:
1. Leggere il piano V6 e produrre **solo un asset nel formato richiesto**, in una cartella temporanea distinta.
2. Indicare provider, modello, licenza checkpoint, costo effettivo, tempo, prompt, seed e provenienza.
3. Non sovrascrivere immagini già approvate; offrire confronto A/B e rollback.
4. Non creare chiavi nei file: usare GitHub Secrets o autorizzazioni native.
5. Verificare qualità e sincronizzazione; non alterare il tono della voce.
6. Richiedere **approvazione esplicita** per usare gli asset alternativi nel render V5.
7. Vietare upload automatici su piattaforme social.

## Stato reale (senza promesse artificiali)
| Capacità | Stato |
|---|---|
| Renderer V5 precedente | Conservato, non modificato |
| Catalogo V6 di tool | Creato |
| Pianificatore, storyboard HTML, controlli input | Creati |
| Workflow Actions V6 e unit test | Creati; da eseguire in CI |
| Qwen3-TTS, Wan, Hunyuan, Z-Image, Real-ESRGAN | **Solo candidati catalogati, non installati** |
| Nuovi MP4 con motori GPU | **Non ancora prodotti** |
| Invio social automatico | **Disabilitato** |

La qualità wow dipende da scelte di regia, verifica delle fonti, identità dei personaggi e asset di livello alto, non dal conteggio di plugin.

## Documentazione upstream
Nel catalogo JSON ogni candidato ha il collegamento al repository ufficiale. Verificare **codice, licenze dei pesi, limiti del servizio ospitato e hardware** sul singolo modello prima dell'attivazione.
