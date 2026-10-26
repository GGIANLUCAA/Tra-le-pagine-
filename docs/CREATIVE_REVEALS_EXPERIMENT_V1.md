# Creative Reveals — prova opzionale (26/10/2026)

**Stato: sperimentale, non approvato artisticamente.** Questa PR NON modifica master, renderer V6/V12/Critico, `config/editorial_rules.json`, `config/cinematic_techniques_v23.json`, sito e pubblicazione. Non si applica alcun effetto a tutti i video.

## Funzione
Genera una **prova tecnica di tre secondi** usando soltanto Python, NumPy, Pillow, OpenCV e FFmpeg, senza API AI o costi di crediti. Parte da una singola immagine: rivelazione acquerello, inchiostro, linea→colore (dalla stessa immagine), oppure nessun effetto. La sorgente resta intatta e l'MP4 di anteprima usa un nome nuovo. Niente crossfade tra quadri, niente immagini sovrapposte o ritagli forzati.

Il suggerimento corrente è volutamente semplice, **non un regista AI che comprende il libro**. In modalità `auto`:
- `libri + fiaba` → `watercolor`
- `libri + mistero` → `ink`
- `libri + illustrato` → `line_art`
- `neutro` e `artvision_*` → `none`

La modalità ArtVision evita di modificare automaticamente riproduzioni autentiche. Per scelte narrative complete servono comunque storyboard, voce reale, fonti e verifica dei raccordi.

## Da Android (GitHub Actions)
Una volta disponibile il workflow nel repository: Actions → **Creative Reveals - Experimental Preview** → Run workflow → `auto`, `libri`, `fiaba`, `3`. Scaricare l'artifact `CREATIVE_REVEALS_PROVA_3S` (MP4 + immagine di prova + scheda JSON). Su una branch sperimentale, il workflow potrebbe non comparire in Actions finché non è presente sul ramo predefinito; i test si possono già eseguire nella PR. Non richiede secret. Il workflow NON pubblica nulla.

## Localmente
```bash
python -m pip install 'numpy>=1.24,<3' 'pillow>=10,<13' 'opencv-python-headless>=4.8,<5'
sudo apt-get install -y ffmpeg
python src/creative_reveals_experimental.py --out output/creative-reveals/PROVA_DIRETTORE_3S.mp4 --effect auto --format libri --mood fiaba --duration 3
python -m unittest discover -s tests -p 'test_creative_reveals_experimental.py' -v
```

Per una **singola illustrazione già autorizzata**, utilizzare `--image /percorso/scena.png` e un nuovo `--out`. NON indicare un MP4 master come immagine. Senza `--image` viene creata una scena illustrata procedurale originale destinata solo al test; non è un quadro autentico né un fatto storico.

## QA e limiti
1. Costi API pari a **zero**; CPU, eventuali minuti GitHub Actions e conservazione artifact hanno comunque limiti/costi secondo il piano.
2. La prova è **muta** (non sostituisce un episodio con voce). Durata proposta 3 secondi a 24 FPS, 540×960, H.264.
3. Verificare su Android primi, medi e ultimi fotogrammi; evitare visi tagliati, distorsioni, ghosting e animazioni fuori contesto.
4. Il JSON registra hash di sorgente/MP4, proposta del regista, formato e motivazione. Output `rendered_needs_artistic_review`, mai master Gold.
5. Se l'effetto non aggiunge valore usare `none`; un risultato riuscito NON approva l'effetto automaticamente per altri video.
