# Collana ARTIST GALLERY — Prima cinquina (13/11/2026)

**Richiesta del proprietario:** dopo aver approvato artisticamente `Evelyn De Morgan — Worlds of Light and Shadow`, vuole produrre **in serie** altri video con la stessa qualità, ma **durata maggiore e quadri completi**. Alla proposta dei primi cinque ha risposto «Sì, va bene».

## Distinzione importante
Questo è un formato galleria d'artista, un solo reel per artista, NON le quattro varianti dell'ArtVision owner 4×1; non occupa né cambia la coda owner `queue/artvision_owner_selected_ten_20261102.json`. La produzione è isolata nel branch `feature/artvision-curated-agent-skills-20261112`, senza cron, POST a pagamento, pubblicazione su sito/social o modifiche ai Gold Master. L'approvazione De Morgan non autorizza pubblicazioni o approvazione automatica di nuovi MP4.

## I primi cinque

| Episodio | Promessa narrativa / regia specifica | Opere candidate (da verificare per singola riproduzione) | Musica candidata V330 |
|---|---|---|---|
| **John William Waterhouse — Women of Myth** · 50 s | Elementi d'acqua, figure mitologiche e gesti sospesi. Apertura su *The Lady of Shalott*, alternanza di composizioni intere e dettagli di volti. Finale sobrio su una figura solitaria | The Lady of Shalott; Circe Invidiosa; Hylas and the Nymphs; The Soul of the Rose; A Mermaid; The Magic Circle; Boreas; Lamia; Ophelia; Ulysses and the Sirens | **Dreams Become Real**, Kevin MacLeod, CC BY 4.0 |
| **Odilon Redon — The World of Dreams** · 47 s | Da fiori/forme luminose verso visioni e occhi, con *The Cyclops* mostrato integralmente e senza presunte ricostruzioni in 3D | The Cyclops; Closed Eyes; Ophelia; The Eye, Like a Strange Balloon; The Buddha; The Birth of Venus; The Golden Cell; Butterflies; The Shell; The Green Death | **Evening Fall (Piano)**, Kevin MacLeod, CC BY 4.0 |
| **Fernand Khnopff — The Beauty of Silence** · 49 s | Silenzio, sfinge, memoria e sguardi. Ampio respiro su *Caresses* e *I Lock My Door Upon Myself*, niente zoom seriali | Caresses; I Lock My Door Upon Myself; Portrait of Marguerite; Memories; Hortensia; Jeanne Kéfer; Silence; The Abandoned Town; Listening to Schumann; Incense | **Night on the Docks (Piano)**, Kevin MacLeod, CC BY 4.0 |
| **Gustave Moreau — Gods and Visions** · 52 s | Oro, mitologia e composizioni monumentali. *The Apparition* come gancio, progressione verso dettagli e quadri interi, finale su un'opera completa | The Apparition; Jupiter and Semele; Oedipus and the Sphinx; Galatea; The Unicorns; Orpheus; Prometheus; Young Man and Death; Salome; Hercules and the Lernaean Hydra | **Darkest Child**, Kevin MacLeod, CC BY 4.0 |
| **Marianne Stokes — Quiet Enchantment** · 46 s | Racconto visivo quieto e luminoso, temi fiabeschi e quotidiani, opere spesso intere; musica delicata | The Queen and the Page; On the Way to the Fields; Primavera; Madonna and Child; Sweet Dreams; Candlemas Day; An Angel; St Elizabeth of Hungary Spinning for the Poor; Schneewittchen; A Woman of Desze; Aucassin and Nicolette | **Calmant**, Kevin MacLeod, CC BY 4.0 |

**Attenzione:** le durate sono obiettivi, non tempi universali. Titoli, datazione, versioni del dipinto e diritti vanno ricontrollati sulla singola immagine prima dell'uso. In particolare, le fotografie museali possono avere termini distinti dal copyright scaduto sul dipinto.

## Codice operativo, senza promesse di qualità automatica

- Dati: `config/artist_gallery_first_five_20261113.json`.
- Renderer: `scripts/artist_gallery_first_five_v1.py` (scarica dal catalogo Commons i file originali con metadata di autore/licenza, pixel minimi e SHA; rifiuta copie inappropriate o fonti insufficienti).
- Verifica: `ffprobe` per MP4 H.264/AAC, `ffmpeg -xerror` full decode, ultimo frame, SHA256, ZIP CRC, lettura del vero MP4 dentro ZIP; copertina, contact sheet, manifest fonte e caption.
- CI: `.github/workflows/artist-gallery-first-five-v1.yml`, 5 job **seriali** che non si duplicano: ogni artista è indipendente; nessun'altra produzione viene modificata.
- Stato prima delle verifiche: **PREPRODUCTION**. Dopo QA: **TECHNICAL_PASS_ARTISTIC_PENDING**. Diritto riuso commerciale e pubblicazione sempre **PENDING** senza verifica aggiuntiva.
- Se un file non è accessibile o ha licenza insufficientemente documentata: riportare **BLOCKED_SOURCE** e proseguire con gli altri candidati, mai fare un'opera artificiale.
- Nessun elemento delle clip di riferimento dei social viene ripubblicato; si riutilizzano solo criteri di regia.

## Consegnare su Android, evitare vecchi errori

**Non usare ZIP annidati.** In ogni ZIP deve trovarsi direttamente un solo MP4 alla radice insieme a copertina, testo, fonti e QA. Il rapporto GitHub deve dimostrare che il file è effettivamente leggibile; un link alla pagina Actions non prova che un Android sia riuscito a scaricarlo. Prima della consegna preferire link MP4 diretto e download effettivamente verificato.

## Fonti di selezione
- Waterhouse: https://commons.wikimedia.org/wiki/Paintings_by_John_William_Waterhouse
- Khnopff: https://commons.wikimedia.org/wiki/Category:Caresses_by_Fernand_Khnopff e https://commons.wikimedia.org/wiki/File:Fernand_Khnopff_-_I_lock_my_door_upon_myself.jpeg
- Marianne Stokes: https://commons.wikimedia.org/wiki/Category:Marianne_Stokes
- Moreau: https://musee-moreau.fr/en/collection/objet/jupiter-and-semele-jupiter-et-semele
- Catalogo 20 musiche: `config/artvision_music_20_v1.json` su main (in questo branch si usa la corrispondente selezione esplicita dei cinque brani con file da verificare al primo uso)
