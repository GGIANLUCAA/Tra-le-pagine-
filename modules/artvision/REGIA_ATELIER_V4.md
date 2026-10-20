# ARTVISION — ATELIER V4 · REGIA DI CONTEMPLAZIONE

Data: 20 ottobre 2026. Questa guida integra e non sostituisce V1, V2 e V3.

## Feedback dell'utente (OBBLIGATORIO nei prossimi video)
La V3 è considerata bella ma ancora troppo prevedibile perché ogni quadro mostra esattamente **un dettaglio → reveal → quadro intero**. L'utente richiede una regia ragionata, originale ed elegante, capace di ipnotizzare senza agitare la camera, e qualità percepita vicina al 4K, con musica autentica variabile e piccolo credito visibile.

### La grammatica di montaggio V4
Ogni lavoro ha una sequenza propria, non un preset applicato in serie:
- 3 dettagli poetici → reveal lungo → intero (Irises, Bouquet).
- quadro completo → avvicinamento lento → 2 dettagli → reveal (Sunflowers).
- quadro completo → dettaglio principale → dettaglio della materia → quadro intero (Flowering Orchard, Large Plane Trees).
- 2 dettagli correlati → quadro intero contemplativo (First Steps, Poplars, Dr. Gachet).
- solo 1 dettaglio significativo dopo la visione intera per alcuni ritratti (The Zouave, Adeline).
- inquadrature sostenute e spazio emotivo nei passaggi finali (Corridor).
- **Niente screen split; niente whip/flash aggressivi; niente zoom per il solo gusto di fare zoom.**
- Espressività da contenuto: occhi e gesto, petali, materia, prospettiva. Ogni ritaglio è accompagnato da una ragione `why` nello storyboard. Mai dettagli casuali.

### Qualità e rispetto delle opere
- Output **1080×1920 verticale**, 24fps H.264 CRF20, qualità social alta.
- Non attribuire «4K nativo» al video: la percezione dipende dalla risoluzione **dell'immagine museale originale**, nitidezza, luce e regia; ingrandimento non inventa dettagli.
- Le riproduzioni originali restano senza falsificazione: no recoloring, no AI fill, no ritagli irrispettosi.
- Macro solo su asset grandi e per soggetti reali; in caso di fonte sotto 1080 pixel usare meno ingrandimenti e preferire l'opera intera.

### Ritmo
Ogni fase impiega circa 2–4 secondi (può variare): dettaglio quasi fermo, push o reveal con accelerazione e frenata naturale, quadro intero fermo. Ogni opera può usare tempi diversi secondo l'intensità e la ricchezza iconografica. Niente battito metronomico uniforme; alternare silenzio visivo a momenti più densi.
Gli effetti atmosferici (velature di fumo sottili) possono interessare **solo lo sfondo scenografico**, mai coprire l'opera autentica.

### Musica realmente registrata
Sono disponibili nel catalogo `music_library.json`:
- `Calmant` — Kevin MacLeod — CC BY 4.0 — https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100859
- `Evening Fall (Piano)` — Kevin MacLeod — CC BY 4.0 — https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100235
Autore e titolo saranno mostrati in piccolo per pochi secondi nel film, e accreditati **integralmente** nella descrizione social e `MUSICA_LICENZA_E_CREDITI.json`.
CC BY **non** vuol dire «non protetta da copyright». La licenza gratuita consente il riuso con attribution obbligatoria e indicazione degli adattamenti. Vietata la sostituzione silenziosa con registrazioni non autorizzate.

**Regola di rotazione:** scegliere per ogni video un brano autorizzato e adeguato all'emozione, diverso dagli ultimi 2–3 quando disponibili. Controllare `music_library.json` e aggiungere brani verificati nuovi nel catalogo prima di riutilizzare sempre le due stesse tracce; non inventare titoli/permessi/durate. Il brano nel workflow deve essere scelto esplicitamente in `modules/artvision/queue.json`; risoluzione automatica artist-specific prima della produzione.

### Sicurezza dei progetti
Nuovo motore: `modules/artvision/atelier_v4.py`. V1 `artvision.py`, V2 `cinema_wow_v2.py` e V3 `harmonic_reveal_v3.py` restano immutati. Workflow unica UI con `style=atelier_v4` come nuova impostazione preferita. **Non toccare i video narrati.**
Branch backup: `backup-artvision-v3-prima-regia-atelier-v4-2026-10-20`.

### Requisiti di accettazione
- Verificare prima un piccolo test di codice e poi intero MP4, ffprobe e dimensioni reali.
- Esaminare uno storyboard reale con differenti numeri di dettagli e almeno due scene che iniziano dall'immagine intera.
- Verificare la leggibilità di titolo e credito audio nel video su uno schermo verticale.
- Crediti completi e licenze nel pacchetto; pubblicazione solo su approvazione dell'utente.
- Controllare realmente nitidezza della fonte alle focali usate, comprensibilità dei passaggi e durata.
- *Success* su GitHub prova solo la correttezza tecnica, non «qualità WOW». Mai attribuire all'utente gradimento non espresso.
- Per ogni nuovo artista creare una specifica mappa di 1/2/3 dettagli con motivazioni; se non c'è, **fermarsi** prima di generare un video copiato da Van Gogh.

### Metodo ricorrente
Richiesta artista → ricerca musei/licenze → piano curatoriale → musica nuova con licenza verificata → aggiorna coda `modules/artvision/queue.json` con `style=atelier_v4`, `music` e `request_id` unico → GitHub Actions → QA mp4/audio/composizione/crediti → consegna ZIP, JPG e MP4. Non riavviare più processi identici senza motivo.
