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
3. Fornire un percorso reale di immagine che esista nella cartella episodes/ del repository; scegliere formato, tecnica, 5/7/10 secondi.
4. Recuperare negli Artifacts ZIP il video H.264 e il manifesto JSON. Il workflow non pubblica e non archivia permanentemente sul sito.

Il server GitHub esegue CPU FFmpeg/OpenCV. Non si installa nulla su Android e non servono chiavi API. Il workflow manuale non si attiva per i render programmati.

## CLI per motori e integrazione futura

Esempio: python src/microcinema_v39.py --image episodes/ESEMPIO/images/scena.png --effect focus_reveal --format libri --seconds 7 --out output/scena.mp4

Per profondità: python src/microcinema_v39.py --image episodes/ESEMPIO/images/fondale.png --foreground episodes/ESEMPIO/images/soggetto.png --effect depth_layers --format libri --seconds 8 --out output/scena3d.mp4

Requisiti: Python 3.11+, numpy, opencv-python-headless, ffmpeg/libx264 e ffprobe. L'effetto depth_layers non è nel menu Actions: richiede preparazione manuale dei materiali.

## Controllo e limiti

Prima di registrare nel progetto definitivo: fonti/diritti secondo V33/V34, verifica dei volti, bordi e raccordi a 0/1/3/5/7 secondi, revisione tecnica del MP4 e allineamento alla voce reale. Il JSON segna rendered_needs_review, non video approvato. Questo generatore crea solo il clip: l'inserimento sincronizzato nei renderer esistenti è un passaggio successivo, non viene dichiarato implementato. Nessuna azione di pubblicazione.

Le fonti che vale la pena studiare in seguito (NON integrate e NON necessariamente funzionanti su runner CPU):
- FFmpeg: https://ffmpeg.org/ffmpeg-filters.html
- DepthFlow: https://github.com/BrokenSource/DepthFlow — parallax depth GPU/GLSL
- PixFlow: https://github.com/inematds/pixflow — storyboard YAML, Remotion, GLSL
- Frame By Plane: https://github.com/Cre-Pan/Frame-By-Plane — livelli Blender
- Wan 2.2: https://github.com/Wan-Video/Wan2.2 — vero image-to-video, modello TI2V-5B documentato su GPU con almeno 24 GB VRAM
- Hugging Face ZeroGPU: https://huggingface.co/docs/hub/spaces-zerogpu — demo gratis con limiti e code, non API illimitata

I repo citati sono spunti, non codice copiato. Verificare licenze del codice, dei pesi IA e dei media per il riuso commerciale. Nessun nuovo provider è collegato; nessun costo automatico è autorizzato.

Test: python -m unittest discover -s tests -p test_microcinema_v39.py -v. I test tecnici non certificano il valore artistico.
