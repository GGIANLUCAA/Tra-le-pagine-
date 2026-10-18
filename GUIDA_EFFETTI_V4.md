# 🎨 TRA LE PAGINE — EFFETTI CINEMATOGRAFICI V4 (GRATUITI)

**Versione:** 18 ottobre 2026
**Stato:** motore CPU installato e provino **realmente riuscito**. Non richiede API, account nuovi, crediti immagini né GPU.
**Repo:** GGIANLUCAA/Tra-le-pagine-

## 1. Perché non usiamo un effetto identico in ogni video

La regia sceglie effetti in base al contenuto **reale del copione**:
- un inizio misterioso può partire a matita;
- un incontro/svolta può essere rivelato con pennellate;
- un panorama o una riflessione possono usare il movimento lento della camera;
- un momento poetico può usare lievi variazioni di luce.

**Regola editoriale:** massimo **2–3 rivelazioni forti** per video, quando giustificate. Lo scopo è evitare l'effetto presentazione automatica; una pausa visiva può valere più di venti transizioni.

## 2. Effetti realmente implementati

| Nome tecnico | Cosa fa davvero | Come funziona | Costo API |
|---|---|---|---|
| \`sketch_paint\` | La stessa illustrazione passa da disegno a matita al colore con bordo irregolare | OpenCV \`pencilSketch\` (o Pillow se OpenCV non disponibile), maschera morbida NumPy, FFmpeg | €0 |
| \`brush_reveal\` | Pennellate irregolari rivelano il colore su una versione smorzata | Pillow/NumPy/FFmpeg, una sola immagine definitiva | €0 |
| \`cinematic_pan\` | Movimenti molto lievi, simili a una camera su un'illustrazione | FFmpeg \`zoompan\` | €0 |
| \`parallax_soft\` | Movimento cinematografico più profondo, ottenuto con zoom e oscillazioni lente | FFmpeg \`zoompan\` con intensità diversa; **non separa realmente i personaggi dallo sfondo** | €0 |
| \`light_atmosphere\` | Luci leggermente pulsanti e camera lenta | FFmpeg \`eq\` con variazioni minime | €0 |

**Importante:** la vera animazione 2.5D con un personaggio scontornato e sfondo ricostruito richiede un successivo modulo sperimentale, ad esempio con rembg. Non la dichiariamo attiva né la installiamo automaticamente per evitare scaricamenti di modelli pesanti o immagini rovinate. L'obiettivo attuale è un V4 leggero e robusto, utilizzabile sul runner GitHub standard gratuito di un repository pubblico.

**Qualità:** le immagini originali non vengono rigenerate o deformate da un modello. I personaggi mantengono il proprio volto. L'effetto matita/colore nasce *dalla stessa immagine*, quindi i contorni sono coerenti.

## 3. Cosa resta invariato

Non cambiano:
- la ricerca e la revisione manuale del contenuto;
- il copione verificato;
- la voce **Google Gemini** e la chiave già configurata;
- la sincronizzazione delle immagini alle frasi pronunciate;
- i sottotitoli, la musica e la copertina V3;
- l'approvazione obbligatoria dell'utente;
- il divieto di pubblicazione automatica.

Il motore nuovo è disponibile come **opzione separata**: i video precedenti restano identici e si può ancora selezionare \`off\` per tornare al montaggio classico.

## 4. Provino senza API — collaudo eseguito

[▶ GitHub Actions — test V4 riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39166810954)

Artifact: \`PROVINO_EFFETTI_V4_GRATIS\`.

Il test usa tre illustrazioni premium già presenti nell'episodio 01 e produce 8,5 secondi di MP4 muto (360×640 per minimizzare i tempi). Controlla:
- durata e formato con ffprobe;
- matita → colore e pennellate;
- luce atmosferica;
- punti di cambio scena;
- creazione del manifesto \`REGIA_TEST.json\`.

Risultato: test **PASS**, senza chiamate a servizi esterni.

Il **render completo di 2–4 minuti con V4**, che includesse nuova voce, musica e tutte le immagini, deve ancora essere collaudato in una vera produzione approvata. Il test da 8,5 s non è una prova di prestazioni o qualità editoriale di un episodio intero.

## 5. Come scegliere gli effetti, da Android

Per un nuovo libro:
1. Prepara il copione e lo storyboard con la [Metodologia V3](METODOLOGIA_TRA_LE_PAGINE_V3.md).
2. Identifica **2–3 svolte** dove un reveal aiuta la storia. Le altre scene ricevono movimenti e luci leggeri.
3. Crea nella cartella \`episodes/NN_titolo/\` un file \`effetti_v4.json\`, prendendo spunto da [TEMPLATE_EFFETTI_V4.json](TEMPLATE_EFFETTI_V4.json). Non serve farlo a mano da telefono: puoi chiedere a ChatGPT di scriverlo su GitHub.
4. Dopo aver approvato tutte le immagini singole premium, apri [**Render video V4**](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/render-v3.yml).
5. In **Run workflow** indica il nome cartella (\`NN_titolo\`) e seleziona **effetti: v4**. Fai partire il render **soltanto quando è stato approvato**.
6. Scarica il video dalle **Artifacts** della run. La pubblicazione sui social resta un passaggio separato.

È possibile anche scegliere **effetti: off** per un confronto diretto con il vecchio video.

### Esempio di file

\`\`\`json
{
  "version": "V4-free",
  "scenes": [
    {"cue": 0, "effect": "sketch_paint", "seconds": 3.0, "mood": "cool"},
    {"cue": 5, "effect": "brush_reveal", "seconds": 2.3, "mood": "warm"},
    {"cue": 8, "effect": "parallax_soft", "mood": "neutral"},
    {"cue": 14, "effect": "light_atmosphere", "mood": "warm"}
  ]
}
\`\`\`

\`cue\` è **la posizione della scena nello storyboard, iniziando da 0** (non il numero del file immagine). Le voci non specificate ricevono una regia molto sobria: all'inizio \`sketch_paint\` per ~2,8 secondi, alla fine \`light_atmosphere\`, in mezzo \`cinematic_pan\`.

Valori accettati:
- \`effect\`: \`cinematic_pan\`, \`sketch_paint\`, \`brush_reveal\`, \`parallax_soft\`, \`light_atmosphere\`.
- \`mood\`: \`neutral\`, \`warm\`, \`cool\`, \`dusk\`.
- \`seconds\` per le rivelazioni: da 0,4 a 5,0 secondi; se la scena è troppo corta la rivelazione viene limitata automaticamente a metà della durata.

**Esempio già preparato:** [Siddharta, 16 inquadrature](episodes/03_siddharta/effetti_v4.json); le rivelazioni sono nella prima immagine, nell'incontro con Kamala e nella comprensione del fiume. La generazione del suo nuovo MP4 V4 necessita comunque delle immagini premium sul repository; gli asset generati nella conversazione non si caricano da soli su GitHub.

## 6. Prestazioni e costi

- Librerie: FFmpeg, Pillow, NumPy e OpenCV Headless, tutte installate dal workflow.
- Calcolo: GitHub Actions con CPU, nessun runner GPU o API video.
- La parte \`zoompan\` usa FFmpeg; le maschere complesse vengono renderizzate solo per pochi secondi sulle scene scelte.
- Il provino è stato elaborato correttamente; il tempo totale per una produzione di 3 minuti non è ancora misurato.
- GitHub Actions offre runner standard gratuiti per repository pubblici secondo le regole vigenti. Restano possibili quote tecniche/limiti di utilizzo; non usare runner più potenti senza averne valutato il costo.
- La **voce Gemini** resta soggetta alle quote dell'API. Il motore effetti non chiama Gemini.

## 7. Qualità e principi

- Non aggiungere tre effetti consecutivi solo per stupire.
- La rivelazione deve avere un significato: idea, trasformazione, scelta, illuminazione.
- Gli occhi e le mani non devono cambiare forma durante l'effetto.
- Musica e sottotitoli restano prioritari.
- Consegna soltanto dopo aver guardato tutto il video e controllato sincronizzazione e audio.

**Obiettivo:** effetti «wow» discreti e sensati, ripetibili a costo API aggiuntivo zero.
