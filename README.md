# 🎬 Tra le Pagine — Studio editoriale illustrato

## 🎬 NUOVO: Regia armonica V5 — effetti solo quando raccontano qualcosa

L'obiettivo non è avere più filtri, ma far sembrare ogni episodio un **cortometraggio letterario progettato con cura**. Il nostro nuovo V5 preserva colori e volti, richiede una **ragione narrativa per ogni effetto forte**, blocca le combinazioni eccessive e misura la qualità tecnica della voce finale.

- [**GUIDA REGIA ARMONICA V5**](GUIDA_REGIA_ARMONICA_V5.md) — metodo, candidati GitHub studiati, scontorno Rembg realmente testato (non approvato per la produzione indiscriminata) e regole artistiche.
- [**Motore V5**](src/regia_armonica_v5.py) — massimo 3 pennellate/rivelazioni, massimo 4 filtri accessori, senza sovrapposizioni; leggere correzioni colore soltanto su scene dello stesso tono.
- [**Controllo audio/video V5**](src/controllo_master_v5.py) — loudness LUFS e true peak, formato e sottotitoli; non comprime/rovina la voce.
- [**Test V5 riuscito**](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39171695750) — test su 16 inquadrature e provino gratis.
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
