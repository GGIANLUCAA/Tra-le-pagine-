# TRA LE PAGINE — REGIA ARMONICA V5 (gratuita, approccio editoriale)

## Scopo
Rendere ogni libro un piccolo cortometraggio narrativo, **non** una dimostrazione di filtri:
- prima la verità del testo, la voce e una buona immagine;
- poi il movimento; solo infine un effetto, se quel momento lo giustifica.
- l'utente approva l'anteprima prima dell'MP4, e la pubblicazione è separata.

Non cambiare il sistema Google Gemini/GitHub/FFmpeg, non rigenerare immagini o voci inutilmente.

## Risultato concreto della ricerca e dei collaudi

**Fonti verificabili:**
- [Rembg](https://github.com/danielgatis/rembg) — scontorno con modelli ONNX locali.
- [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2) — il modello Small è Apache-2.0; i modelli Base/Large/Giant hanno licenza CC-BY-NC-4.0 e non vanno usati per un canale commerciale.
- [color_transfer](https://github.com/jrosebr1/color_transfer) — implementazione OpenCV della teoria di trasferimento cromatico nello spazio Lab, MIT.
- [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) — metrica ITU-R BS.1770, MIT.
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — analisi dei tagli in video esistenti, BSD-3-Clause.
- [Spotify Pedalboard](https://github.com/spotify/pedalboard) — compressione/limiting audio, GPLv3; non installato: prima verificare i possibili vincoli di distribuzione e ascoltare un confronto.
- [G'MIC](https://github.com/GreycLab/gmic) — enorme libreria di filtri artistici; utile ma aggiungere altri filtri *non* è una priorità.
- [frei0r](https://github.com/dyne/frei0r) — 136 plugin installabili su GitHub Actions; 8 già testati e disponibili nel nostro motore.

**Codice V5 realmente inserito:**
- [src/regia_armonica_v5.py](src/regia_armonica_v5.py): vincoli editoriali, analisi di sequenza e **lievissima** omogeneità cromatica in Lab.
- [src/effetti_v4.py](src/effetti_v4.py): richiama V5 e genera \`REGIA_ARMONICA_V5.json\` e \`CONTATTO_SCENE_V5.jpg\`; gli effetti e la voce V4 continuano a funzionare.
- [src/controllo_master_v5.py](src/controllo_master_v5.py): controllo FFmpeg dell'MP4 già creato, verifica volume LUFS, picco reale dBTP, formato verticale e tempi SRT. **Non modifica la voce**.
- [render-v3.yml](.github/workflows/render-v3.yml): controlla la regia **prima** di chiamare Gemini; genera un rapporto tecnico dopo il render.
- [Test gratuito e riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39171340680): su 16 inquadrature, 2 rivelazioni, 3 filtri extra e **una sola scena** leggermente corretta nei colori. Provino video 720×1280 riuscito; LUFS e picco misurati su audio Gemini già esistente.

### Prova reale di scontorno Rembg (non usato nei video)

[Workflow gratuito e riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39171114735): Rembg + piccolo modello \`u2netp\` su CPU GitHub; circa 70 secondi per ambiente, installazione, scaricamento pesi e 3 immagini (tempo misurato su quella singola run).

**Verdetto dopo aver guardato i file:** riconosce alcuni protagonisti, ma può includere sagome di persone in secondo piano e sfumature del dipinto. Se separassimo quei livelli automaticamente, creerebbe contorni visibili e buchi nello sfondo. **Non attivarlo automaticamente**. Possibile solo per 1 scena eccezionale dopo verifica della maschera e dei diritti sui pesi del modello. L'assenza di costi API non implica licenze commerciali garantite.

## Regole V5 obbligatorie

### Una ragione narrativa per ogni effetto forte
Ogni \`sketch_paint\`, \`brush_reveal\` e \`postfx\` richiede nel JSON \`reason\` non vuoto; un effetto apparso a caso **fa fallire il preflight prima di consumare crediti Gemini**.

**Budget conservativo per ogni episodio:**
- al massimo 3 rivelazioni matita/colore o pennellate;
- al massimo 4 filtri frei0r;
- mai due rivelazioni di fila;
- mai filtri postproduzione su due scene consecutive;
- camera calma e immagine pulita come impostazione normale; nessun effetto forte automaticamente all'inizio.
- lasciar respirare le parole e non creare bruschi tagli solo per aumentare movimento.

### Continuità dei colori senza rovinare l'atmosfera
V5 confronta fotografie illustrate **solo entro lo stesso gruppo emotivo** \`neutral / warm / cool / dusk\`. La correzione automatica, quando attiva, sposta i canali Lab di **massimo 4, 3, 3 unità**, solo se c'è un evidente scostamento. Non cambia il volto, non rimodella la scena e non impone una palette unica a giorno e notte.

Il campo \`quality.color_cohesion\` può valere \`gentle\` (correzioni minime) o \`off\` (nessuna modifica). La cartella output comprende un foglio miniature per controllare le variazioni visive.

### Audio naturale, non ipercompresso
Il nuovo controllo misura il volume finale e segnala picchi o valori anomali. Non equalizza o comprime automaticamente la voce, poiché Gemini ha già una buona espressività. Per i social valutare in seguito un confronto di normalizzazione *facoltativa* con FFmpeg \`loudnorm\`; mai cambiare voce senza ascolto A/B.

La musica non deve coprire parole chiave; suoni ambientali solo se autentici/coerenti e con licenza chiara (CC0 o propria). Evitare suoni sintetici gratuiti messi in ogni scena.

## Esempio di regia sensata

\`\`\`json
{
  "version": "V5-artist",
  "quality": {
    "color_cohesion": "gentle"
  },
  "scenes": [
    {"cue": 0, "effect": "cinematic_pan", "mood": "neutral"},
    {"cue": 5, "effect": "sketch_paint", "seconds": 2.3,
      "mood": "cool", "reason": "Il protagonista scopre ciò che gli era nascosto"},
    {"cue": 10, "effect": "light_atmosphere", "postfx": "soft_bloom",
      "mood": "warm", "reason": "Al ritorno, una luce lieve segnala una possibilità di pace"}
  ]
}
\`\`\`

\`cue\` è la posizione dell'inquadratura nella sequenza, contando da **zero**. Motivi e tipi di effetti devono riferirsi all'opera reale; gli esempi non sono regole valide per ogni libro.

## Verifica prima del video completo
- Copione verificato e approvato, nessuna scena inventata.
- Immagini singole nitide 9:16, personaggi consistenti; evitare collage.
- Copertina standard del marchio; il titolo non va stampato dentro l'illustrazione AI.
- Un solo effetto *wow* alla volta, legato a un evento narrativo.
- Nessuna modifica forte e arbitraria alle tonalità o ai volti.
- Voce con pause e intensità coerenti; sottotitoli allineati alla voce.
- Report V5 e miniature esaminati, nessun audio clipping evidente.
- Video guardato su smartphone dall'inizio alla fine. **Pubblicazione solo con OK separato**.

## Ricerca futura e priorità
1. **Da provare presto:** composizione 2.5D *solo* con scontorno affidabile e background ricostruito manualmente, non con il risultato grezzo di rembg.
2. **Da valutare:** Depth Anything V2 Small con CPU, su uno o due paesaggi soltanto, con controllo visivo di artefatti e licenza.
3. **Da valutare:** leggero sound design con libreria propria e licenze CC0, senza inserire rumore sotto la voce.
4. **Non prioritario:** ulteriori effetti G'MIC, video generativo AI GPU e filtri deformanti per tutti i fotogrammi.

**Principio finale:** un buon effetto deve rendere il *senso* della scena più chiaro, non rubare l'attenzione al romanzo.
