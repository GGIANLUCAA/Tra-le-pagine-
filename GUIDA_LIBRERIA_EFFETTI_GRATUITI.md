# TRA LE PAGINE — LIBRERIA EFFETTI GRATUITI V4+ (frei0r)

**Aggiornata 18 ottobre 2026.**
**Obiettivo:** tante possibilità, ma una regia sobria e personalizzata per ogni romanzo. Nessuna spesa API per questi effetti.

## Progetto open source verificato

- https://github.com/dyne/frei0r — progetto attivo di plugin per filtri, utilizzabile con FFmpeg.
- https://ffmpeg.org/ffmpeg-filters.html#frei0r — comando \`frei0r\` supportato da FFmpeg.
- https://packages.ubuntu.com/noble/amd64/frei0r-plugins/filelist — 136 plugin .so presenti sul runner Ubuntu del collaudo.
- https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39168733579 — prova reale: 8 plugin testati positivamente, 1 plugin inesistente rifiutato.

Non tutti i 136 filtri sono verificati, utili o adatti ai nostri video: **8 sono stati effettivamente testati**, selezionati e resi configurabili. Altri vanno sperimentati uno a uno senza compromettere gli episodi finiti.

### Catalogo di 8 filtri cinematici pronti

| Nome nel JSON \`postfx\` | Plugin reale | Uso narrativo consigliato |
|---|---|---|
| \`soft_bloom\` | \`softglow\` | Ricordi piacevoli, apparizione luminosa, tenerezza |
| \`golden_glow\` | \`glow\` | Illuminazione, rivelazione, alba, scena positiva |
| \`edge_luminosity\` | \`edgeglow\` | Scelta improvvisa o inquietudine, con discrezione |
| \`ink_graphic\` | \`cartoon\` | Stile graphic novel particolarmente marcato |
| \`cinema_vignette\` | \`vignette\` | Solitudine, claustrofobia e attenzione sul volto |
| \`poster_art\` | \`posterize\` | Ricordo, immagine stilizzata e poster d'epoca |
| \`halftone_pages\` | \`colorhalftone\` | Flashback visivo illustrato, vecchia stampa |
| \`vintage_grain\` | \`rgbnoise\` | Ricordi sfocati, guerra, inquietudine senza glitch |

**Importante:** i plugin vengono **mescolati con l'illustrazione originale** a intensità attenuata (tipicamente 9–31%). Questo protegge volti, sfondi e colore dalle distorsioni esagerate. Non applichiamo filtri a tutte le scene.

## Come funziona nel progetto

1. Si prepara il libro seguendo \`METODOLOGIA_TRA_LE_PAGINE_V3.md\`.
2. Si prepara \`effetti_v4.json\` nella cartella episodio. Ogni \`cue\` specifica un movimento/effetto principale e un eventuale \`postfx\`.
3. Il generatore crea il filmato con \`src/effetti_v4.py\` e, se \`postfx\` è presente, utilizza \`src/frei0r_extra.py\` e un plugin vero da \`frei0r-plugins\`.
4. FFmpeg unisce tutto con voce Gemini, musica e sottotitoli **senza alterare l'audio originale**.
5. Controllo qualità e approvazione utente prima della pubblicazione. Il motore non pubblica nulla da solo.

Formato esempio:

\`\`\`json
{
  "version": "V4-frei0r-free",
  "scenes": [
    {"cue": 0, "effect": "sketch_paint", "seconds": 3.0, "mood": "cool"},
    {"cue": 6, "effect": "brush_reveal", "seconds": 2.4, "mood": "warm", "postfx": "soft_bloom"},
    {"cue": 9, "effect": "parallax_soft", "mood": "dusk", "postfx": "cinema_vignette"}
  ]
}
\`\`\`

I \`postfx\` sono **facoltativi**. La mancanza di \`postfx\` significa che il motore V4 standard funziona senza plugin. Un nome sconosciuto blocca l'esecuzione anziché caricare codice inatteso.

## Verifiche effettuate

- **[136 plugin disponibili e 8 testati](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39168733579)**; 1 nome provato inesistente (\`sepia\`) correttamente rifiutato.
- **[Provino V4+frei0r integrato a 720×1280](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39168938771)**; 8,5 secondi, 3 scene, 3 preset post-elaborati e audio non necessario per il test. Il video è valido secondo ffprobe.
- **[Collaudo integrale offline](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/test-integrale-v4-frei0r.yml)**; riusa narrazione, musica, sottotitoli e immagini di EP01 senza richiedere crediti AI. L'esito della prova va verificato nella relativa run, non presunto.

Il primo montaggio **completamente nuovo** con immagini create ad hoc e la voce Gemini generata da capo è un test editoriale distinto; il collaudo offline verifica soltanto la catena visiva e audio con risorse preesistenti.

## Costo, licenze e limiti

- **Zero euro di costi API aggiuntivi** per i 8 filtri selezionati. Sono applicati localmente, senza API cloud.
- Ubuntu GitHub Actions runner pubblico standard: secondo le regole di GitHub, la disponibilità gratuita e i limiti del servizio vanno rispettati; un repository privato o runner premium può essere a pagamento.
- \`frei0r\` è un progetto di software libero con componenti sotto licenze open source; prima di incorporare codice sorgente o distribuire binari, rispettarne licenze e avvisi di copyright. L'output video originale non è automaticamente una copia del software.
- Non vengono installati modelli AI pesanti né richieste chiavi a pagamento.
- Colori ed effetti hanno sempre scopo narrativo. I preset distorsivi/glitch rimangono esclusi dal catalogo utilizzabile nei video pubblicabili.

## Progetti gratuiti da valutare in una fase separata (NON installati)

1. **G'MIC** — https://github.com/GreycLab/gmic: moltissimi filtri artistici; richiede prova separata delle prestazioni e della licenza dell'uso previsto. Non è necessario per il V4.
2. **rembg** — https://github.com/danielgatis/rembg: scontorno vero del soggetto per 2.5D; i modelli ONNX vengono scaricati al primo avvio. Da provare fuori dalla pipeline principale per evitare allungare troppo le elaborazioni.
3. **Depth Anything V2 Small** — https://github.com/DepthAnything/Depth-Anything-V2: modelli di profondità; solo Small è Apache-2.0, i modelli più grandi risultano non commerciali. CPU e tempi vanno misurati prima di inserirlo.
4. **Spotify Pedalboard** — https://github.com/spotify/pedalboard: compressione/limiter vocali di livello professionale; licenza GPLv3 e possibile impatto sulla voce naturale, da sperimentare con ascolto A/B prima di rendere il processo automatico.

Nessuno di questi quattro è attivo o testato nel nostro generatore. Si aggiungeranno soltanto se una prova gratuita conferma un miglioramento visibile o udibile.

## Regole per il risultato finale

- Una voce comprensibile vale più di 100 filtri.
- Le immagini devono rappresentare **l'evento descritto in quel momento**, non una categoria estetica.
- Massimo 2–3 momenti con reveal/pennellate e 2–4 piccole stilizzazioni per video di 2–4 minuti, salvo motivi editoriali chiari.
- Mai ripetere automaticamente la stessa combinazione su tutti i libri.
- Preset e loro quantità possono essere cambiati senza rigenerare il copione o le immagini.
- **Mai dichiarare finito un video senza controllarne MP4, audio, sottotitoli e coerenza visiva.**

**Motto:** il regista sceglie *quando* un effetto arricchisce la storia; il software decide *come* applicarlo.
