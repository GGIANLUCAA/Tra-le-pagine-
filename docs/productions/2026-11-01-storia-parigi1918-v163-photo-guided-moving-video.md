# La Storia Rivive V163 — movimento fotografico: feedback positivo V162 e nuovo confronto reale
Data: 1 novembre 2026 · issue #144 · mandato V108 · soggetto: **Parigi 1918**, pellicola Musée Albert-Kahn AI139599.

## Nuova preferenza editoriale dell'utente (specifica, non approvazione master)
L'utente ha apprezzato esplicitamente **la qualità delle fotografie generative I2I** di Parigi V162 e chiede di **mantenerla nelle prossime produzioni**. Ha chiesto invece che la **parte in movimento sia restaurata molto meglio e si avvicini alle foto**. Non tradurre questo feedback in approvazione dell'intero MP4 V162, della quarta foto DDColor, dei diritti territoriali o della pubblicazione.

**Regola operativa per i successivi video:** usare il livello realistico delle 3 foto Finegrain di V162 come ulteriore esempio stilistico per le fotografie (V98 resta minimo generale); nella parte *in movimento* mantenere la stessa identità, palette e inquadratura del fotogramma restaurato, non tornare a B/N per tutta la sequenza né a una colorizzazione DDColor aggressiva; lasciare vero movimento colorizzato prima del freeze, senza surrogati con zoom di foto fisse. Se la scena non regge il confronto, rifiutare il master.

## Cosa è stato fatto realmente in V163
- Reimpiegati **identici byte** delle 3 foto reali I2I V162, SHA256 rispettivamente:
  1. `5648bc952703a31dfbfec7501be04ff34a9297437a180cfd73a2f12258f7f64c`
  2. `fd6eaee3c6e4ba070b4f6ffeb357284360b102d3c2e9a2b47daa282a2e7e1fc0`
  3. `d2d1d0eef1c2fd0bd195c914d45652345c2c5282d7f2bbcefee7fb133c81d442`
- Stessi cinque MP4 autentici di V162 e **cinque freeze** SHA-lock, stessi soggetti e tempi; nessuna nuova inquadratura inventata, niente Vidu.
- Nuovo `src/storia_rivive_v163_photo_guided_real_motion.py`: dense optical flow DIS current-to-freeze; remap della foto restaurata per propagare *colore e residui limitati di luminanza* sui fotogrammi originali in movimento; confidenza su differenza luminanza per ridurre warp errati/occlusioni; nessun allucinato generative video, nessun frame artificiale aggiunto. Gli oggetti **si muovono nel vero film**, non in una foto animata.
- Primi quattro shot: vero B/N iniziale breve, reveal a colori durante il movimento e foto sul frame esatto; scena 4 ancora DDColor, non I2I. Quinto: altro movimento dal vero film trattato col colore neurale di scena 5, non clip Vidu.
- Nuova regia verticale: finestra video centrale **720×768** contro 720×540 V162; crop unico coerente su pellicola e foto, senza chiamarlo 4K o inventare parti tagliate.
- Musica V162 originale riusata, no nuovo diritto musicale.

## QA misurata sui BYTE e sui veri frame V163
- MP4 `Parigi_1918_V163_Movimento_Restaurato.mp4`, **17,000s, 720×1280, 30fps, H.264/yuv420p + AAC**, 9.818.469 byte; SHA256 `2d282216f143af515380499806f110c4f35e01671c9e9c770eec17c3c7b1b465`.
- **FFmpeg full decode PASS**, FFprobe formato e audio PASS; 510 fotogrammi attesi/scene.
- ZIP Android `Parigi_1918_V163_Kit_Android.zip` **10.363.144 byte**, SHA256 `78b0254e7fd4e8521d681c29673573e1c61108704d836d80752cb330ba3e92e1`, CRC ZIP PASS. Include MP4, copertina, contatto tre viste, QA, quattro bozze social, readme, script e test.
- A/B misurato a ~0,9 s di ciascuna scena: saturazione media HSV film nell'area centrale, V162 → V163: `15,5→105,6`, `11,3→37,8`, `16,2→100,8`, `34,8→49,6`, `21,3→80,4`. È misura di presenza del colore in movimento, **non** giudizio su bellezza o fedeltà.
- Movimento reale su intervalli di quattro frame dopo la comparsa del colore (delta medio grayscale): `14,75`, `5,95`, `8,92`, `17,10`, `16,11`; nessuna slideshow photos zoom spacciata per clip Vidu.
- **4/4 test locali** core flow, sorgente invariata, dimensioni errate fail-closed e hash locking PASS; risultati nel test `tests/test_storia_rivive_v163_photo_guided_real_motion.py`. Foto originali intatte.
- Il MP4/ZIP è stato creato realmente e distribuito dalla conversazione, poi salvato nella Libreria privata `/Restauro storico/`. Non è una GitHub Release, non è stato pubblicato su social/sito.

## Blocco finale rimasto
**Stato `rendered_needs_review`, NON master equivalente a V98.** 3/4 foto I2I, 0 clip Vidu, **0 crediti usati**, diritti Italia da verificare, QA umano di volti, mani, movimento e grading ancora pendente; V91/V94/V96/V99 final gate **NON PASSATO**. Nessuna dichiarazione di approvazione finale.

**Sicurezza operativa:** i cinque originali e le 3 foto sono byte-SHA bloccati, niente POST Vidu, niente token/saldi nei log, niente nuovi cron e nessuna modifica ArtVision/WOW LAB/V98. Non far partire produzione seriale da V163.

## Riproduzione tecnica
Installare Python, OpenCV, NumPy, Pillow, FFmpeg e usare due cartelle di asset V162 autentici:
```bash
python src/storia_rivive_v163_photo_guided_real_motion.py \
  --source-v162-dir /path/to/V162_clips_e_freeze \
  --photos-v162-dir /path/to/V162_actual_I2I_and_DDColor \
  --out output/storia_rivive_v163
python -m unittest discover -s tests -p "test_storia_rivive_v163_photo_guided_real_motion.py" -v
```
I clip di origine non sono nel repo per peso/licenza; preflight SHA fail-closed per i 5 freeze e 5 PNG colore/foto. Il rendering non accetta risorse corrotte o sostituite.
