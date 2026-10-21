## Produzione intensiva V15 — priorità corrente

[Obiettivo 10 video al giorno in autonomia](docs/PRODUZIONE_INTENSIVA_V15.md).
Coda, preflight e registro verificato disponibili; servizio completo di produzione
continua ancora da integrare e misurare. Il limite di due video/settimana è superato.

## Crescita dei canali — priorità corrente V14

[Piano di sviluppo di 90 giorni](docs/PIANO_CRESCITA_V14.md) · [Pagina mobile](docs/creator-growth.html).
Prima crescita organica, serie riconoscibili e qualità. Commissioni, sponsor e
outreach sono rimandati. Il planner prepara la coda senza pubblicare o consumare API.

# 🎬 Tra le Pagine — Studio editoriale illustrato

## GPT: comincia da qui — Direzione video V13

**[START_HERE_GPT.md](START_HERE_GPT.md)** →
**[AGENTS.md](AGENTS.md)** → **[Playbook operativo](docs/GPT_VIDEO_PLAYBOOK.md)**.

Il nuovo ingresso collega formati, regie approvate e moduli reali. Include scheda
di progetto, controllo preventivo, ricetta dei filmati, riuso della voce Google
verificata e report esplicito dei tempi stimati. Nessuna API nel planner.

- **Arte senza voce:** Cinema V6 Gold Master. I workflow V1–V5 sotto sono storici.
- **Critica parlata:** guida della serie Critico V2, con copertina titolo opera + artista.
- **Libri:** regole V12, **nessun sottotitolo**. I riferimenti ai sottotitoli sotto sono storico.
- **Controluce e musica:** verificare stato e sorgenti nel [registro](config/video_formats_v13.json).
- **Laboratorio:** sorgenti consegnati conservati in [integrations/video_library_laboratorio](integrations/video_library_laboratorio/).

```bash
python src/video_director_v13.py formats
python src/video_director_v13.py brief --format libri --topic "Il libro richiesto" --out output/nuovo_video
```

Le sezioni seguenti documentano l'evoluzione del progetto; non prevalgono sulle
regole correnti indicate sopra. V13 non produce autonomamente video da un titolo:
guida GPT nel completare i materiali e usare i renderer già disponibili.

---

## 🎬 NUOVO: Regia armonica V5 — effetti solo quando raccontano qualcosa

L'obiettivo non è avere più filtri, ma far sembrare ogni episodio un **cortometraggio letterario progettato con cura**. Il nostro nuovo V5 preserva colori e volti, richiede una **ragione narrativa per ogni effetto forte**, blocca le combinazioni eccessive e misura la qualità tecnica della voce finale.

- [**GUIDA REGIA ARMONICA V5**](GUIDA_REGIA_ARMONICA_V5.md) — metodo, candidati GitHub studiati, scontorno Rembg realmente testato (non approvato per la produzione indiscriminata) e regole artistiche.
- [**Motore V5**](src/regia_armonica_v5.py) — massimo 3 pennellate/rivelazioni, massimo 4 filtri accessori, senza sovrapposizioni; leggere correzioni colore soltanto su scene dello stesso tono.
- [**Controllo audio/video V5**](src/controllo_master_v5.py) — loudness LUFS e true peak, formato e sottotitoli; non comprime/rovina la voce.
- [**Test V5 riuscito**](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39171695750) — qualità cromatica e provino gratis.
- [**MP4 di 130 secondi con V5 riuscito**](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39171898138) — voce Gemini originale, 16 inquadrature, 2 rivelazioni, 2 filtri delicati, sottotitoli e controllo audio.
- [**Test scontorno Rembg**](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39171114735) — funzionante su CPU, ma contorni talvolta scorretti: prova separata, **non attivata** nel montaggio.
- [**Render multi-episodio protetto**](.github/workflows/render-v3.yml) — controllo degli effetti prima di spendere crediti Gemini, QA audio automatico dopo l'MP4.

**La coerenza è più importante del numero di filtri.** Il nuovo motore non impone più lo stesso effetto iniziale a tutti i libri. La pubblicazione resta bloccata fino a consenso esplicito.


## 🎞️ Libreria frei0r: 136 plugin gratuiti disponibili, 8 selezionati e testati

Il nostro sistema V4 può applicare, **solo dove serve alla storia**, una nuova libreria di effetti gratuita integrata direttamente in FFmpeg: glow, vignetta cinematografica, fumetto/inchiostro, stampa a retino, posterizzazione, grana e contorni luminosi.

- **[GUIDA LIBRERIA EFFETTI GRATUITI](GUIDA_LIBRERIA_EFFETTI_GRATUITI.md)** — effetti realmente testati, limiti, configurazione per ogni libro e progetti futuri da valutare.
- **[TEST plugin frei0r riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39168733579)** — 136 plugin disponibili nel runner, 8 filtri provati con successo.
- **[TEST integrato V4+frei0r riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39168938771)** — tre filtri aggiunti a clip V4 di prova.
- **[COLLAUDO MP4 di 2:10 riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39169343642)** — narrazione Gemini esistente + musica + sottotitoli + 16 inquadrature con effetti, senza chiamare API.

I filtri sono gestiti nel modulo [`src/frei0r_extra.py`](src/frei0r_extra.py) e attivati tramite `postfx` nel file `effetti_v4.json`; non si avviano se il campo non è presente.

Il flusso **non pubblica nulla automaticamente** e il primo render completamente nuovo con Gemini attivato in `render-v3.yml` resta da provare su un episodio approvato: la produzione odierna è un *remix offline* collaudato di un episodio precedente.

## 🎨 NUOVO: Effetti cinematografici V4 gratuiti (installati e testati)

Il generatore **V4** aggiunge un modulo visuale gratuito al workflow esistente: **matita → colore**, **pennellate progressive**, **camera cinematografica**, **movimento di profondità leggero** e **luce atmosferica**. Gli effetti possono essere scelti **scena per scena** nel file `effetti_v4.json`, senza cambiare copione, voce Gemini, sottotitoli o copertine.

- [**GUIDA COMPLETA EFFETTI V4**](GUIDA_EFFETTI_V4.md) — effetto per effetto, limiti reali, costo e istruzioni Android.
- [**PROVINO GRATUITO REALMENTE RIUSCITO**](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39166810954) — 8,5 secondi di video usando immagini EP01, nessuna nuova API.
- [**RENDER VIDEO V4 — WORKFLOW**](.github/workflows/render-v3.yml) — seleziona episodio ed effetti `v4` oppure `off` dopo aver approvato le immagini.
- [**Regia V4 di Siddharta**](episodes/03_siddharta/effetti_v4.json) — 16 inquadrature con gli effetti scelti per i momenti del romanzo.

**Non è AI image-to-video con movimento naturale dei personaggi:** per ora il parallax leggero muove la camera virtuale sull'immagine e non scontorna un soggetto. Questo è voluto: costa €0 di API e preserva i volti. Il prossimo vero episodio V4 completo da 2–4 minuti richiederà un test e approvazione artistica.


**Serie italiana di video sui libri**: copione originale verificato, illustrazioni narrative, voce italiana espressiva, sottotitoli, musica e video verticale. Preparazione e gestione possibili da Android.

## 🗓️ NOVITÀ: 2 episodi al giorno

Sono attive due automazioni ChatGPT (verso le **9:00** e le **18:00**, ora italiana) per preparare due nuove **anteprime editoriali**. Il nuovo [render V3 parametrico](.github/workflows/render-v3.yml) accetta episodi diversi e blocca ogni esecuzione che non abbia immagini premium. La [coda](queue/render_request.json) richiede approvazione esplicita.

**Non sono ancora due MP4 autonomi quotidiani**: per quello serve collegare una generazione immagini programmabile e concordare quote e un eventuale budget. Consulta [GUIDA — DUE EPISODI AL GIORNO](AUTOMAZIONE_2_EPISODI_AL_GIORNO.md).

## 📘 Leggi prima le nuove regole

- **[METODOLOGIA EDITORIALE DEFINITIVA V3](METODOLOGIA_TRA_LE_PAGINE_V3.md)** — filosofia, fedeltà al libro, voce, immagini di qualità, copertina costante, ganci autentici, controlli ed approvazione.
- **[SCHEDA EPISODIO V3](TEMPLATE_EPISODIO_V3.md)** — modulo riutilizzabile per ogni libro: ricerca, copione, storyboard, personaggi, copertina, voce, controlli qualità.
- [Guida visiva storica di EP01](STILE_VISIVO.md) — utile come riferimento del vecchio episodio, **non sostituisce** la metodologia V3.

**Una regola:** la produzione del nuovo video parte **soltanto dopo approvazione dell'anteprima** (copione, storyboard, 2–3 immagini singole campione, copertina). Una eventuale pubblicazione social richiede conferma separata.

## ⚙️ Tecnologia esistente

- **ChatGPT** prepara ricerca, copione, storyboard, immagini, copertina e revisioni.
- **Google Gemini TTS** interpreta il testo con voce italiana espressiva, pausa e intonazione. La chiave resta nel segreto GitHub **GEMINI_API_KEY**: non pubblicarla mai.
- **GitHub Actions** esegue gli script sui suoi server, senza Colab né montaggio sul telefono.
- **FFmpeg** monta il formato verticale con musica, sottotitoli e piccoli movimenti sulle illustrazioni.
- Gli output generati possono essere scaricati come ZIP/MP4 su Android; **non vengono pubblicati automaticamente**.

La vecchia pipeline funziona ancora per i primi video e non è stata modificata. **Il nuovo workflow V3** permette la selezione di qualunque cartella episodio già completa e dotata di immagini premium, con verifica preventiva e copertina coordinata. Non genera automaticamente le illustrazioni: quelle restano il principale collo di bottiglia.

## 📁 Episodi presenti

- [EP01 — La novella degli scacchi](episodes/01_scacchi)
- [EP02 — L'arte della gioia](episodes/02_arte_della_gioia)

Per i prossimi episodi creare nuove cartelle, senza cancellare o sovrascrivere quelle precedenti.

## 🧭 Flusso suggerito da smartphone

**Fase A: anteprima, senza render definitivo**
1. Scrivere a ChatGPT: «Applica il Metodo Tra le Pagine V3 al libro ...».
2. Controllare copione, fatti, spoiler, storyboard, 2–3 illustrazioni singole e copertina.
3. Comunicare correzioni o scrivere «OK, procedi con il video».

**Fase B: produzione**
1. Completare le illustrazioni singole, mantenerne fisionomia e ambienti coerenti.
2. Preparare la cartella del nuovo episodio e collegare i cambi di scena alle frasi.
3. Generare con Gemini e verificare l'audio prima del montaggio finale.
4. Produrre MP4, sottotitoli, copertina e descrizione.
5. Controllo qualità completo. Richiedere conferma prima della pubblicazione.

Il repository è **pubblico**: contenuti caricati e codice sono visibili, ma i valori dei GitHub Actions Secrets non vengono mostrati. Non caricare dati privati, chiavi in file o materiale protetto da diritti non autorizzato. Per l'uso dei contenuti generati con AI rispettare licenze, termini dei provider e politiche delle piattaforme social.

## 🗣️ Comando rapido

«Applica [METODOLOGIA_TRA_LE_PAGINE_V3.md](METODOLOGIA_TRA_LE_PAGINE_V3.md) al libro **[titolo] di [autore]**. Voglio prima **solo copione verificato, storyboard, tre immagini verticali e proposta di copertina**; aspetta il mio OK prima del video completo.»

**Proposito:** non fare video seriali indistinguibili, ma racconti illustrati che sembrino **selezionati, scritti e diretti con vera cura**. Gli strumenti AI restano strumenti e non vanno presentati come performance umane se non lo sono.

## 🧩 STUDIO IBRIDO V6 — Moduli add-on (nessuna riscrittura del motore)

Nuovo **catalogo di 23 strumenti** e pianificatore di scene `src/studio_ibrido_v6.py`. Genera un rapporto, un pacchetto di prompt per immagini e uno storyboard HTML da consultare su Android, senza spese API. I modelli esterni restano candidati da testare: **non risultano installati**. Il V5, la voce Gemini, tutti gli episodi e il workflow precedente rimangono invariati.

- [**GUIDA STUDIO IBRIDO V6**](STUDIO_IBRIDO_V6_GUIDA.md) — istruzioni, sicurezza, fonti di cronaca e roadmap.
- [**Catalogo dei 23 strumenti**](config/studio_ibrido_tools.json) — tool cinesi e internazionali, hardware, stato e cautele.
- [**Workflow anteprima V6**](.github/workflows/studio-ibrido-v6.yml) — pianificazione manuale, zero API e pacchetto scaricabile.

## 📂 Archivio Media V7 — riciclare asset prima di crearne di nuovi

**Voce Google Gemini invariata. Solo telefono Android per comandare i workflow su GitHub.**
Il nuovo modulo `src/archivio_media_v7.py` cerca fotografie Creative Commons via Openverse
(senza API key) e contenuti fotografici/video via Pexels (con chiave opzionale).
La ricerca produce una **galleria HTML**, senza scaricare o generare video.
Un secondo avvio, con **ID scelto esplicitamente**, importa un solo file con
provenienza e crediti da verificare. Nessuna pubblicazione o sostituzione automatica.

- [Guida passo per passo V7](ARCHIVIO_MEDIA_V7_GUIDA.md)
- [Workflow mobile V7](.github/workflows/archivio-media-v7.yml)
- [Sorgente importer](src/archivio_media_v7.py)

**Ordine operativo:** riusa asset approvati → cerca fonti licenziate → genera solo le scene mancanti.
Il renderer V5 e i vecchi episodi non sono stati modificati.

## 🧠 Orchestratore V8 — stage sicuro, riuso e controllo da Android
Nuovo modulo **solo additivo** per collegare pianificazione V6 e asset esistenti al formato immagini del renderer V5.
Prepara `PIANO_V8.json`, `REVISIONE_GATE1_V8.html` e, **solo dopo approvazione Gate 1**, uno staging di immagini JPEG senza modificare le cartelle storiche. Suggerisce eventuali riusi da altri episodi ma non copia né genera immagini di sua iniziativa. La voce Google Gemini resta invariata. **V8 non genera ancora MP4**; il collegamento finale al vecchio renderer richiede un collaudo separato.

- [Guida V8 per Android](ORCHESTRATORE_V8_GUIDA.md)
- [Workflow Orchestratore V8](.github/workflows/orchestratore-v8.yml)
- [Sorgente e adapter](src/orchestratore_v8.py)

## 📱 Studio Web V9 — interfaccia Android
Nuova **app PWA mobile** in `docs/`, senza toccare i motori V3–V8. Gestisce nuovi brief (salvati nel browser), mostra episodi e run GitHub reali, apre ricerca V7 / storyboard V6 / preparazione V8 / render storico V5.

**Avvio gratuito semplice:** GitHub **Settings → Pages → Deploy from a branch → main → /docs → Save**. Dopo il deploy apri l'indirizzo pubblicato da Pages e aggiungilo alla Home di Android. I workflow si aprono in GitHub per conferma.

**Opzionale:** `worker/index.mjs` + `wrangler.toml` permettono di ospitare la stessa web app su Cloudflare Workers e lanciare i workflow direttamente con GitHub OAuth, solo dopo impostazione manuale dei segreti e autorizzazione.

- [Guida Android V9 e attivazione](STUDIO_WEB_V9_GUIDA.md)
- [Apri sorgente interfaccia](docs/index.html)
- [Test V9](tests/test_studio_web_v9.mjs)

L'abbonamento ChatGPT Plus viene usato **attraverso ChatGPT** per creare copioni e storyboard, non come API gratuite non previste. Il sito V9 non genera automaticamente nuovi episodi o MP4 senza i workflow V3–V8; la voce Google rimane invariata.

## 🎞 Episodi V10: anteprime vere e lettore MP4 privato
Il pannello Android V9 viene ampliato con schede ricche, titoli reali, miniature tratte dalle **immagini già presenti**, storyboard con scene e lettore MP4 che apre file **solo dal telefono senza caricarli**. La produzione storica conserva Google Gemini TTS. Nessuna pubblicazione automatica di filmati sul sito pubblico.

Le miniature vengono estratte dal repository con `tools/build_episode_previews_v10.py`, pubblicate da `episode-previews-v10.yml` quando i permessi del workflow lo consentono; per le cartelle senza immagini mostra esplicitamente «Nessuna scena illustrata». I video negli Artifact GitHub richiedono download per la riproduzione locale.

- [Guida completa anteprime V10](ANTEPRIME_V10_GUIDA.md)
- [Modulo galleria e video](docs/episode_gallery_v10.js)
- [Verifiche miniature](tests/test_episode_previews_v10.py)

## 🎬 V11 — Studio più facile, videoteca e video BETA da idea

La home Android adesso mette in primo piano **Crea video**, **Videoteca** ed **Episodi**; le funzioni tecniche restano disponibili nel gruppo avanzato. La videoteca legge le Release approvate con player MP4, copertina estratta dal filmato e pulsante di download. Gli MP4 non vengono pubblicati automaticamente: la pubblicazione su un sito GitHub Pages **pubblico** richiede consenso specifico attraverso `pubblica-video-v11.yml`.

L'esperimento `studio-autopilot-v11.yml` può tentare video narrativi completi da una descrizione: testo Google Gemini, fotografie di Openverse/Wikimedia, vecchia voce Google e FFmpeg. Si ferma se mancano immagini/quote, senza sostituzioni finte; il filmato resta in un Artifact per controllo. Questa beta non è ancora stata collaudata end-to-end con chiamate Google reali e non accetta automaticamente cronaca/documentari.

Con GitHub Pages l'avvio dei workflow resta **guidato** attraverso GitHub; con l'integrazione Cloudflare OAuth configurata diventa eseguibile dal pulsante dell'app. **Plus non è un credito API OpenAI**; nessuna API GPT a pagamento è stata introdotta.

- [Guida passo-passo Android V11](STUDIO_WEB_V11_GUIDA.md)
- [Videoteca e MP4](docs/videoteca_v11.js)
- [Workflow pubblicazione approvata](.github/workflows/pubblica-video-v11.yml)
- [Pipeline beta da un'idea](.github/workflows/studio-autopilot-v11.yml)

## 🎞 V12 — Regole permanenti per TUTTI i prossimi video
**Nessun sottotitolo**: la nuova produzione non aggiunge più testo del parlato sull'immagine, non crea file `SOTTOTITOLI.srt`/`captions.ass` e non inserisce tracce sottotitoli nell'MP4. La vecchia implementazione è preservata **solo** nel backup `legacy_backup/render_con_sottotitoli_v11.py`. I video già prodotti rimangono intatti.

**Narrazione più comprensibile:** i riassunti dei libri devono spiegare protagonista, situazione, eventi fondamentali, azioni, conseguenze e conclusione prima delle riflessioni. Il nuovo prompt V12 scoraggia generalità e filosofeggiamenti.

**Immagini che seguono la voce:** il report `REGIA_NARRATIVA_V12.txt/json` abbina ogni scena alla frase esatta del racconto e segnala che la reale pertinenza delle fotografie richiede comunque controllo visivo. Non scambiare una keyword simile per una corrispondenza verificata.

- [Leggi tutte le regole V12](REGOLE_VIDEO_V12.md)
- [Regia narrativa V12](src/regia_narrativa_v12.py)
- [Test MP4 senza sottotitoli](tests/test_no_subtitles_v12.py)

**Importante:** il video `Delitto e castigo` già consegnato NON viene rigenerato: queste correzioni valgono per i video futuri.
