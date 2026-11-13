# Artist Gallery · Seconda serie · Produzioni reali 13 novembre 2026

## Mandato
Proseguire **in serie** il format galleria d'artista già approvato artisticamente con **Evelyn De Morgan**, usando immagini autentiche, regia sobria, immagini dei dipinti completi, musiche appropriate e consegna scaricabile Android.

**Stato di questo lotto: tre MP4 creati e decodificati con successo**, tutti in revisione artistica del proprietario. Non sono master approvati Gold, non sono le 4 varianti ArtVision 4×1 e non sono pubblicati sui social/sito.

| Artista | Titolo pubblico | Durata | Opere usate | Musica Kevin MacLeod | MP4 SHA256 | Run e artifact |
|---|---|---:|---:|---|---|---|
| Arnold Böcklin | The Island Beyond Time | 50 s | 10 immagini di opere autentiche | Myst on the Moor · CC BY 4.0 | `171d854fa0552b5ab5bb114c582449232db37b99f2eebea446b617b8ec568d02` | [run 43360752253](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43360752253), [artifact #14008615799](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43360752253/artifacts/14008615799) |
| Edward Burne-Jones | Dreams of the Golden Age | 52 s | 10 immagini di opere autentiche | Immersed · CC BY 4.0 | `447837d24a0cc733feb2436c2b90161eaa933ed467a54f914eb2ce7543061dfb` | [run 43360752253](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43360752253), [artifact #14008191540](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43360752253/artifacts/14008191540) |
| Franz von Stuck | Shadows of Desire | 46 s | 10 immagini di opere autentiche | Lightless Dawn · CC BY 4.0 | `637d40382edda3ab6767cbf20ed130d1b717189195d3ea2976d5b8412414e697` | [run 43361199860](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43361199860), [artifact #14007764125](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43361199860/artifacts/14007764125) |

## Verifica indipendente di consegna

- Sono stati effettivamente scaricati i tre artifact da GitHub. I rispettivi MP4 sono stati estratti, esaminati con FFprobe, decodificati integralmente senza errori con FFmpeg, confrontati tramite hash SHA256 e controllati via ZIP CRC.
- Il loro contenuto visivo è stato esaminato su contact sheet ricavate dal vero MP4, non da copertine inventate.
- Le prime versioni avevano ripetizioni di immagini (Böcklin) e opere con nudità troppo visibile per il taglio social (Burne-Jones e von Stuck). Le versioni **qui elencate sono quelle corrette**, dopo nuova selezione e nuova decodifica. Non confondere con gli artifact delle run precedenti.
- Sono stati creati localmente due archivi aggiuntivi: **TRE_NUOVI_VIDEO_ARTISTI_ANDROID.zip** (3 MP4 direttamente alla radice, senza ZIP annidati) e **TRE_NUOVI_ARTISTI_PACCHETTO_COMPLETO.zip** (tre video alla radice, copertine, anteprime, fonti e social). ZIP CRC e SHA del MP4 estratto PASS. La presenza nel container non prova disponibilità permanente su GitHub né che il browser Android specifico abbia scaricato il file.
- Arte e musica restano da ascoltare/visionare integralmente e **approvare artisticamente** da parte del proprietario. Si applicano V320/V322/V326 e skill `artvision-video-evidence`.
- Le licenze su ogni riproduzione/museo e eventuali restrizioni territoriali restano da esaminare per pubblicazione. La licenza musicale CC BY 4.0 richiede attribuzione nei testi social. **Nessuna autopubblicazione** o acquisto di crediti.
- Ogni episodio è un video galleria per artista, separato dalla produzione 4×1; zero API a pagamento.

## Continuità seriale

Per i prossimi episodi consultare prima questo registro e `docs/productions/2026-11-13-artist-gallery-prima-cinquina.md`, evitando duplicati con Evelyn De Morgan, Vrubel e i cinque episodi precedenti.

Possibili prossimi artisti indipendenti, da cercare e non trattare come già preparati o renderizzati: **Edward Robert Hughes, Carlos Schwabe, William Degouve de Nuncques, John Martin, Peter Nicolai Arbo**. Scegliere in base a opere autentiche, permessi delle riproduzioni e qualità visiva; se mancano almeno sei fonti adatte, segnare BLOCKED_SOURCE e passare a un altro.

Codice corrente: `config/artist_gallery_next_three_20261113.json`, `scripts/artist_gallery_next_three_v1.py`, `.github/workflows/artist-gallery-next-three-v1.yml`. Il workflow rimane impostato sul SOLO von_stuck per la revisione isolata; per nuovi artisti programmare una nuova lavorazione indipendente invece di rilanciare vecchi MP4.
