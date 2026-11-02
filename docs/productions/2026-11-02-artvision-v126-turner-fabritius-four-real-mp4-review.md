# ArtVision V126 — Turner + Fabritius, due pacchetti 4×1 fisici verificati (02/11/2026)

## Risultato realmente verificato in questa esecuzione

Sono stati recuperati e decodificati localmente gli MP4 originali **Critico V117** dagli artifact GitHub Actions, i **Cinema V55/V50** già esistenti, e sono stati prodotti **due nuovi MP4 di revisione visiva Critico Museum V126**, senza modificare alcun master.

**Turner, The Fighting Temeraire (1839), National Gallery NG524, 90,7 × 121,6 cm**:
- Critico Standard V117: 7.230.964 B, SHA256 `24276b69336f96f238c92d4eb86b678fbaa4f94f105c498c32796ccf360afeb8`, 99 s.
- Critico Museum **V126 revisione**: 21.242.775 B, SHA256 da `QA_MANIFEST_V126.json` nel pacchetto, 99,45 s. Intro/uscita fotografiche da Cinema Museum V55, centro da Critico Museum V117; audio AAC originale copiato bit-identico.
- Cinema Standard V55: 7.705.037 B, SHA256 `59da265649c6d7a7f0eb7b34d85e40fefa25f2cb422ccd77ad427b360b570bd4`, 47,8 s.
- Cinema Museum V55: 25.776.806 B, SHA256 `dcac4d5155598a42fd3fc29f06f455ccf38a5f63da4a0f06ef9286cbaccc4ea8`, 52,2 s.
- Pacchetto ZIP 4 MP4 + 4 copertine English + 16 bozze social + QA/licenze: **62.757.280 B**, SHA256 `dc32c8e72d5f821c1885377c6ae601e445e20349e487690ec9badea6ac31e584`; ZIP CRC e SHA readback per tutti i 4 video **PASS**.

**Carel Fabritius, The Goldfinch (1654), Mauritshuis 605, 33,5 × 22,8 cm**:
- Critico Standard V117: 11.856.857 B, SHA256 `d1bb19d660975f06df33e9c9e44a3991c7eb0817b81573ba2cfcbb9d74e7fcde`, 99,52 s.
- Critico Museum **V126 revisione**: 22.250.664 B, SHA256 da `QA_MANIFEST_V126.json` nel pacchetto, 99,55 s. Intro/uscita dalla scena fotografica digitale Cinema Museum V50, centro dal Critico Museum V117; AAC originale copiato bit-identico.
- Cinema Standard V55: 33.592.473 B, SHA256 `537d7f8683bbac8791a8e629916ee206c845d41673eebd3a8dec1bee7575b1f2`, 43,67 s.
- Cinema Museum V50: 24.192.101 B, SHA256 `5b760c609a51acf9c22a5f39aeb90344ea6914b812290c5fc01164376d3c94bd`, 55 s.
- Pacchetto ZIP 4 MP4 + 4 copertine English + 16 bozze social + QA/licenze: **93.084.575 B**, SHA256 `b9447b89ec645d0036fffdd64d19bf4f73285e6bb3e0df25a8facd8c4c125623`; ZIP CRC e SHA readback per tutti i 4 video **PASS**.

## Provenienza, controllo e limiti

- V117 originali: GitHub Actions [run 41351647619](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41351647619), artifact 13104524785 (Turner) e 13101194533 (Fabritius). **Nessuna nuova TTS**, nessun workflow rilanciato.
- Turner Cinema Standard V55: artifact 12845445991; Museum V55: artifact 12847734987; originali intatti. Fabritius Cinema Standard V55 e Museum V50 recuperati dalla Library privata, senza modificare originali.
- FFmpeg `-xerror` **full decode PASS per 8/8 MP4**; FFprobe H264/AAC; AAC demux ADTS dei due Critico Turner bit-identico SHA256 `5ee4b7cf2f0f4fc5982abe27e576b7a3583373262c4b55ef8f47dd0914287640`, Fabritius bit-identico SHA256 `7a5630505b3d6da889fb1addf01213067411c794c42684704ea381dc7506c80f`. Entrambi confrontati anche con il Critico Museum V117 originale.
- **Non dichiarare** questi pacchetti archivio privato permanente: i due ZIP e gli MP4 V126 sono stati creati nel container della conversazione, e non è stato effettuato upload Library/R2 né verificato playback Android.
- Sono **review**, non master finali: `museum_approved=false`, `Gold V25=0`, niente social. V126 migliora gli ingressi/uscite rispetto alle pareti grigie V117 ma **non** dimostra la sala autentica né una cornice storica; Turner usa foto di quadro incorniciato con credito CC BY-SA 4.0 da verificare; Fabritius è ricostruzione digitale. L'ascolto integrale frase/inquadratura è ancora pendente; restano sottotitoli/titoli in italiano in parti dei Critico V117 e tagli di montaggio da giudicare. Diritti musicali e fotografici devono essere verificati prima di qualunque pubblicazione.
- Il packaging non conta come nuovi render per gli slot Cinema: **due nuovi MP4 di revisione dello stesso slot**, sei master precedenti recuperati byte-identici, **8 file fisici** in due pacchetti di review. Nessuna spesa o pubblicazione.
