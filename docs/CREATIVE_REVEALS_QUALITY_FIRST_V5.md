# Creative Reveals — qualità prima degli effetti (V5, solo esperimento)

**Scopo:** prevenire il problema del precedente video di Ventimila leghe: MP4 tecnicamente valido ma illustrazioni schematiche e poco coinvolgenti. Questo esperimento NON introduce nuovi default, non sostituisce gli effetti V4/V5 esistenti, non modifica alcun master, non modifica il sito e non pubblica nulla.

## Decisione registica

1. Se l'immagine non è artisticamente valida **senza effetti**, fermarsi. Niente sagome geometriche come surrogato di ambientazioni cinematografiche.
2. Conservare una sola immagine opaca per scena. Vietati ghosting, sovrapposizioni di quadri, distorsioni e crop di volti.
3. Individuare UN motivo narrativo specifico: oggetto rivelato, chiave, Nautilus, finestra, lettera, volto. Non applicare filtri indiscriminati.
4. Dare priorità alla comprensione: narrazione, nome dell'oggetto, tempo dell'effetto, pausa per contemplare il risultato. La durata si sceglie in base alla voce reale.
5. Non rifare la voce già buona. Riusare l'originale verificando hash e allineamento; Gacrux resta la voce del format libri. Se manca allineamento affidabile, produrre soltanto un confronto preliminare.
6. Effetti mirati solo se cambiano positivamente A/B la comprensione e la qualità visiva. Una scena può restare completamente ferma.

## Prova Nautilus

Nel confronto locale A/B (14,32 s), la stessa **illustrazione originale di fantasia** viene mostrata senza effetto e con una trasformazione limitata al sommergibile: blueprint azzurro → colore → oblò luminosi. Il subacqueo e il paesaggio rimangono presenti. Lo stesso segmento di voce/musica Gacrux è recuperato dal vecchio filmato, senza chiamare nuovamente l'API. Il segmento audio proveniva da un allineamento in passato **stimato**, non certificato parola-per-parola. Non chiamarlo video definitivo, ricostruzione storica autentica o prova di sincronizzazione perfetta.

Questo repository contiene soltanto il **motore Python + gate + test** della dimostrazione. Non include né presume disponibili il PNG originale creato durante la chat, il WAV estratto o un archivio multimediale presente sul sito; servono file forniti esplicitamente per riprodurre il render.

## API e librerie

Effetti: Python + NumPy + Pillow + OpenCV + FFmpeg, niente API video. La produzione **di immagini originali** è un costo/servizio distinto dagli effetti: non implicare che il repository ne generi automaticamente illimitate gratis.

GitHub open source esaminati:
- https://github.com/opencv/opencv — usato per edge detection, matte, maschere, rendering
- https://github.com/visioncortex/vtracer — candidato opzionale per vere illustrazioni vettoriali, **non** incluso né obbligatorio
- https://github.com/danielgatis/rembg — possibile segmentazione CPU per singoli soggetti, ma modelli ONNX e dipendenze; **non** installato

## Uso manuale in un ambiente con i file approvati

~~~bash
python -m pip install numpy pillow opencv-python-headless
python experiments/creative_reveals/selective_nautilus_v5.py \
  --image /path/ILLUSTRAZIONE_NAUTILUS_1024x1536.png \
  --audio /path/EXISTING_NARRATED_EXCERPT.wav \
  --output output/EXPERIMENT_NAUTILUS_REVEAL.mp4 --variant effect
python -m unittest discover -s tests -p 'test_selective_reveal_quality_v5.py' -v
~~~

Il preset Nautilus è **mappato manualmente per una precisa immagine 1024×1536** e fallisce sulle altre risoluzioni: non passarvi quadri, foto documentarie o altri soggetti a caso. Non significa che sappia riconoscere il sommergibile semanticamente. Per la produzione di 2–3 minuti i punti di interesse devono arrivare da una scheda scena-by-scena approvata, prima dell'eventuale automazione.

## Criterio promozione

- Visivo convincente da fermo, no riempitivi/volti tagliati
- Voce naturale integrale e parola/evento/cambio immagine verificati sul WAV reale
- Effetto comprensibile in riproduzione normale, non solo nei fotogrammi
- Confronto A/B con fonte e audio identici
- Revisione durata, tenuta, copertina, musica, credits, social, fonte/diritti
- Nessuna promozione a Gold Master automatica. Conservare A/B, maschere e master originale

**Stato: candidate technical experiment, needs artistic review.**
