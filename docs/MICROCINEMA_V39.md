# MicroCinema V39 — provini gratuiti di 5–10 secondi (TRIAL)

Revisione 27/10/2026. Modulo opt-in. Le regole AGENTS.md, docs/REGOLE_ATTIVE.md, V33/V34 e V38 hanno precedenza. Non cambia i master, le cover, Gacrux, i post, le automazioni o il sito.

## Obiettivo artistico

Creare una piccola scena cinematografica SOLO quando aiuta una frase o un momento importante. Nessuna quota di effetti e nessun clip di riempimento. Conservare stile, colori, personaggi, coerenza dei luoghi e ritmo del racconto. Non creare figure geometriche, movimenti oscillanti o artifici vistosi.

## Effetti disponibili nel prototipo

- slow_push: movimento continuo e molto leggero della camera sulla foto; libri e ArtVision.
- focus_reveal: stessa immagine che entra a fuoco; libri e ArtVision con cautela.
- light_travel: luce narrativa appena percepibile; soltanto libri/ricostruzioni, non opere autentiche.
- depth_layers: moto relativo di soggetto e fondale della STESSA illustrazione, solo libri. Richiede fondale pulito e PNG RGBA scontornato della stessa immagine, entrambi uguali per dimensione.

Non sono vere animazioni generative: il motore non fa camminare le persone e non crea acqua in movimento. Non inserire tra ogni coppia di immagini. Per ArtVision non sovrapporre due quadri e non simulare il contesto reale di un museo: il POV museo e cornice resta un effetto separato che richiede autentiche fonti o contesto dichiaratamente illustrativo.

## Prova dal telefono Android dopo il merge

1. Aprire GitHub, repository GGIANLUCAA/Tra-le-pagine-, Actions.
2. Selezionare MicroCinema V39 - provino gratuito, Run workflow.
3. Fornire un'immagine sotto episodes/ oppure il percorso episodes/NOME_EPISODIO/scene_premium.zip e indicare il numero scena da estrarre (1-35); scegliere formato, tecnica e 5/7/10 secondi.
4. Recuperare negli Artifacts ZIP il video H.264 e il manifesto JSON. Il workflow non pubblica e non archivia permanentemente sul sito.

Il server GitHub esegue CPU FFmpeg/OpenCV. Non si installa nulla su Android e non servono chiavi API. Il workflow manuale non si attiva per i render programmati.

## CLI per motori e integrazione futura

Esempio: python src/microcinema_v39.py --image episodes/ESEMPIO/images/scena.png --effect focus_reveal --format libri --seconds 7 --out output/scena.mp4

Per profondità: python src/microcinema_v39.py --image episodes/ESEMPIO/images/fondale.png --foreground episodes/ESEMPIO/images/soggetto.png --effect depth_layers --format libri --seconds 8 --out output/scena3d.mp4

Requisiti: Python 3.11+, numpy, opencv-python-headless, ffmpeg/libx264 e ffprobe. L'effetto depth_layers non è nel menu Actions: richiede preparazione manuale dei materiali.

## Inserimento opt-in nei racconti già esistenti (V4)

Il renderer dei libri carica il file effetti_v4.json, e ora riconosce FACOLTATIVAMENTE il campo microcinema in una scena. Esempio da aggiungere SOLO a una scena narrativamente motivata:

```json
{
  "cue": 8,
  "effect": "cinematic_pan",
  "microcinema": {
    "effect": "focus_reveal",
    "seconds": 7,
    "reason": "Al momento della scoperta, l'immagine si rivela lentamente."
  }
}
```

Il campo va inserito nell'elenco scenes già esistente, senza sostituire le altre direttive. Il video narrativo usa ancora src/render.py --effects v4, la voce Gacrux e gli stessi cue: la microclip occupa i primi 7 secondi della scena, senza allungarla né spostare il parlato. Se la scena dura di più, il fotogramma finale rimane fermo fino al cambio successivo; se dura meno di 7 secondi, la preparazione viene bloccata. Non sovrapporre postfx o brush/sketch reveal. Il generatore conserva il report V39 e lo registra anche nel manifesto V4; rende comunque obbligatoria la verifica artistica del MP4 completo.

La sincronizzazione con la frase resta da verificare nel video completo: l'allineamento tecnico è basato sui cue esistenti, non dimostra che l'effetto sia narrativamente pertinente. Questo collegamento non è operativo per ArtVision Cinema/Critico, dove rimane soltanto la generazione di un provino separato. Non modifica nessun master storico e non inserisce clip automaticamente nei video nuovi: serve una decisione esplicita per scena.

## Controllo e limiti

Prima di registrare nel progetto definitivo: fonti/diritti secondo V33/V34, verifica dei volti, bordi e raccordi a 0/1/3/5/7 secondi, revisione tecnica del MP4 e allineamento alla voce reale. Il JSON segna rendered_needs_review, non video approvato. Il generatore autonomo crea solo clip; il collegamento V39 con il renderer V4 dei libri esiste ora in via sperimentale. Non è stato ancora certificato su un episodio completo da GitHub Actions. Nessuna azione di pubblicazione.

Le fonti che vale la pena studiare in seguito (NON integrate e NON necessariamente funzionanti su runner CPU):
- FFmpeg: https://ffmpeg.org/ffmpeg-filters.html
- DepthFlow: https://github.com/BrokenSource/DepthFlow — parallax depth GPU/GLSL
- PixFlow: https://github.com/inematds/pixflow — storyboard YAML, Remotion, GLSL
- Frame By Plane: https://github.com/Cre-Pan/Frame-By-Plane — livelli Blender
- Wan 2.2: https://github.com/Wan-Video/Wan2.2 — vero image-to-video, modello TI2V-5B documentato su GPU con almeno 24 GB VRAM
- Hugging Face ZeroGPU: https://huggingface.co/docs/hub/spaces-zerogpu — demo gratis con limiti e code, non API illimitata

I repo citati sono spunti, non codice copiato. Verificare licenze del codice, dei pesi IA e dei media per il riuso commerciale. Nessun nuovo provider è collegato; nessun costo automatico è autorizzato.

Test: python -m unittest discover -s tests -p 'test_microcinema*.py' -v. I test tecnici non certificano il valore artistico.
