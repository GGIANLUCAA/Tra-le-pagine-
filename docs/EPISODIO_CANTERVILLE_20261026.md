# Episodio — Il fantasma di Canterville (26 ottobre 2026)

**Serie**: Tra le Pagine, libri raccontati; formato italiano con voce.

## Risultato realizzato in questa sessione
- MP4 720×1280, 20fps, H.264/AAC, **186,5 secondi**, file verificato anche con decodifica integrale.
- Audio narrato Google Gemini Gacrux da **185,496 secondi**; non sono stati usati synthesizer locali robotici.
- **17 illustrazioni originali** dell'edizione Oscar Wilde/Wallace Goldsmith 1906, da Project Gutenberg; non dipendono da Canva e nessuna API immagini Premium è stata utilizzata.
- **28 inquadrature** con micro-movimenti e dissolvenze attraverso il nero, senza sovrapposizioni tra immagini; titoli solo apertura/chiusura; niente sottotitoli a video.
- Copertina, soundtrack originale delicata prodotta via sintesi procedurale, post social, manifest con fonti e piano scene.
- Versione Android MP4 di circa **6,4 MB** e pacchetto ZIP di circa **15 MB** con gli originali; versione sorgente video a bitrate più elevato conservata nel workspace della sessione.

## Fonte documentata
**Oscar Wilde, The Canterville Ghost**, illustrated by **Wallace Goldsmith**, John W. Luce & Company, 1906. Ebook: https://www.gutenberg.org/cache/epub/14522/pg14522-images.html
L'opera Wilde (m. 1900) e le illustrazioni Goldsmith (m. 1945) sono di epoca di pubblico dominio; per la pubblicazione commerciale verificare ulteriori restrizioni particolari nell'eventuale giurisdizione.

La sceneggiatura in `voice_jobs/canterville_20261026.txt` è una sintesi italiana originale, non una lettura integrale. Dettaglio verificato: è **Washington Otis** a ripulire la macchia dal pavimento, mentre suo padre offre al fantasma l'olio per le catene.

## Strumenti realmente utilizzati
- `src/gemini_voice.py`, `.github/workflows/canterville-voice.yml` → voce Gacrux tramite `GEMINI_API_KEY` del repository.
- `src/asset_canterville_gutenberg.py`, `.github/workflows/canterville-illustrations.yml` → acquisizione delle tavole da **un'unica edizione gratuita**.
- Regole V33/V34: prima le fonti coerenti, proteggere provenienza, zero nuove API a pagamento.
- Render locale FFmpeg (già nel progetto), esportazione separata per Android. Le clip/video completi **non sono archiviati su GitHub**, sono consegnati come file in chat e non va supposta l'esistenza di un file nel catalogo del sito senza successivo upload.
- Gli script e il dossier nel repository permettono il nuovo recupero di voce e tavole; il montaggio grafico specifico e gli MP4 consegnati sono salvati nel pacchetto della conversazione, non nel sito.

## Autocritica e iterazioni future
Questo episodio sceglie volutamente lo stile **incisione d'epoca animata**, non illustrazioni AI colorate. La bassa risoluzione di alcune tavole storiche non può diventare un originale 4K aumentando artificialmente i pixel. Per futuri libri diamo preferenza a più inquadrature realmente diverse e un controllo artistico umano, non ripetizioni meccaniche; testare un generatore gratuito di scene originali coerenti dove gli archivi non bastano.

**Status**: rendered/technically verified, artistic review pending, not posted. Nessun costo di servizi Premium autorizzato o addebitato da questo dossier.
