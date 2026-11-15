# ArtVision Owner · 10 segnalazioni Centro di controllo · recupero senza duplicati (12/11/2026)

**Ambito:** 10 varianti richieste dal proprietario. Fonti: `AGENTS.md`, `docs/REGOLE_ATTIVE.md` (inclusi V330 musica e V331 Museum frontali), `queue/artvision_owner_selected_ten_20261102.json`, esecuzioni GitHub Actions originali, Library privata. Il pannello segnala alcuni slot come `missing`, ma **mancante come approvazione Museum non significa che il MP4 di revisione non esista**.

**Procedura:** prima recupero, poi prova SHA256+ZIP CRC+FFmpeg video/audio, poi QA artistica/diritti indipendenti. **Nessun render o nuova TTS/Vidu**, niente modifiche a master, siti o coda di produzione. Questa PR non incrementa i conteggi e non assegna Gold.

| # | Opera / variante | Prova MP4 già prodotto | Stato di recupero / impedimento |
|---|---|---|---|
| 1 | The Lady of Shalott / cinema_museum | V166, SHA `5b8eff08ecfcb6ad196085e4e3dc6e670305d6d26d3699cd85dd9b452f189ae5`; ZIP SHA `33a3ef683356279c20f64deb944030a21b98430e7bb021c2eda139d873f0642f` | La queue conserva FFmpeg/Library readback PASS storico, ma **l'archivio originale non è stato individuato nell'attuale elenco della cartella Library `/ArtVision`**. Non attestare disponibilità corrente del download senza trovare byte identici. Ricerca backup necessaria, non nuovo render indiscriminato. |
| 2 | The Night Watch / critico_museum | V179, SHA `45ddd04834593165fde1da908eb6d431c62f176437a75718fc861e14999e8475` | Library `/ArtVision/ARTVISION_NIGHT_WATCH_V179_CRITICO_MUSEUM.zip` materializzata; SHA ZIP `7be66469e7c4e6f6e025ef971fa1072706be595a59d82d1be85a98e66841cd6b` verificato con CRC e full FFmpeg degli MP4 estratti. |
| 3 | The Night Watch / cinema_museum | V180, SHA `1695464e74fd77a027d739704d28efbb7975f6396f5e5e5f9807c32e75f4b97b` | Library `/ArtVision/ARTVISION_NIGHT_WATCH_V180_CINEMA_MUSEUM.zip` materializzata; ZIP SHA `b3ada1f2b4e39f6300ad5c4f66007a85bb64d35764fb63ee0ba278d03228db7f`, CRC e MP4 SHA/full FFmpeg PASS. |
| 4 | The Tower of Babel / cinema_museum | V137 SHA `4a9639be84ecf912ae0a82e8078dcacc1a93ac6bf82433a95d927b98746e5d7f` | GitHub [run #41663098584](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41663098584) SUCCESS, artifact `13242672720` NON scaduto. Precedente R2 GET SHA integrale riportato in coda. Questa PR **riscarica dal GitHub originale e verifica** senza produrre. |
| 5 | The Death of Sardanapalus / critico_standard | V169 SHA `c7d3a2e231b384fb6a082cb61158d3133d3f309c05e0247b228a1ab6ea7a77dc` | GitHub [run #42125709649](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42125709649) SUCCESS, artifact `13459719782` NON scaduto; vecchio Library readback registrato. Questa PR **riscarica e verifica** il file originale. |
| 6 | The Death of Sardanapalus / cinema_museum | V172 SHA `a023436e8e68635e134ca3faeb83e2bffbc78a53d7bbb29afaf33d57851ab9ed` | Library `/ArtVision/ARTVISION_DELACROIX_V172_GITHUB_ARTIFACT_VERIFIED.zip` scaricata e verificata SHA `88d6f249d04cc8e475bc70ec5413c98afc778c14529e235141bfbf9a47c9e1bb`, CRC, MP4 SHA e FFmpeg decodifica completa PASS. Originale GitHub [run #42144732764](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42144732764). |
| 7 | The Fall of the Rebel Angels / critico_museum | V218 SHA `23743fc5eec772c65d5671e36b78497843824b447dfb38ec22851183fe68bf2b` | MP4 già dentro Library `/ArtVision/Rebel_Angels_V218/ARTVISION_REBEL_ANGELS_V218_4_VIDEO_ANDROID.zip`; archivio SHA `3ab5cf5904c4a4de012981aa74f67454bf37834785c5a9ba23c455a97e4b43b4`, CRC, MP4 SHA e FFmpeg PASS. **Non usare il vecchio V213 bocciato artisticamente**. |
| 8 | The Fall of the Rebel Angels / cinema_museum | V200 SHA `708076b42b7a135e5fc49ea16412e686324f809867f1ef125913e71dfc7afe19` | Nello stesso archivio 4×1 V218 sopraccitato, MP4 e full decode verificati. Esistono anche varianti Cinema V208 e V212 già in Library/Actions; non creare nuovo slot da una semplice revisione. |
| 9 | The Garden of Death / critico_museum | V218 SHA `7fe48f41f5da136fdfead63a0067bddc21863121eec25551fbe795443e2313aa` | Library `/ArtVision/SIMBERG_GARDEN_CRITICO_MUSEUM_V218_REVIEW_PACKAGE.zip` scaricata: ZIP SHA `7b1a184b9591f8571880d4112a35fa767397a8f70ca8bbbfd0b6d65810080650`, CRC, MP4 SHA e full FFmpeg PASS. |
| 10 | The Garden of Death / cinema_museum | V225 SHA `6e8a5bbf0e1a37bfa1b5352c3c7da5e317f8f5068412448f7646115094c2eb26` | Library `/ArtVision/Simberg_Garden_V225/SIMBERG_THE_GARDEN_OF_DEATH_V225_REVIEW_PACKAGE.zip` + MP4 materializzati, ZIP SHA `721e02574a9bb436fe56107e3bb7ea9a683f17db`, CRC, MP4 SHA e full FFmpeg PASS. Esiste inoltre una revisione V226; **non contare versioni come slot distinti**. |

### Verifiche eseguite

L'ispezione del 12/11 ha riscaricato i cinque ZIP V179, V180, V172, Bruegel V218 4×1 e Simberg Critico V218: tutti e cinque SHA-256 del ZIP, ZIP CRC, MP4 interni corrispondenti e decodifica FFmpeg video/audio **PASS** su otto file video. Inoltre Simberg Cinema V225: MP4 e ZIP scaricati separatamente, SHA-256 esatti, ZIP CRC e FFmpeg full H264/AAC **PASS**. Per Tower e Critico Sardanapalus sono state controllate run GitHub, job e presenza artifact; la CI di questa PR aggiunge readback vero da artifact originali e pubblica solo JSON.

### Cosa NON dimostrano queste prove

- **Museum non approvati:** V331 dal 12/11 impone opere dritte, centrate e prospettiva frontale verificata estraendo frame reali da MP4. V80/V118/V119 restano obbligatorie: foto di allestimenti storici, ricostruzioni scenografiche neutre e frame dell'opera non devono essere spacciati per sale museali attuali.
- **Critico:** sincronizzazione frase/inquadratura, ascolto WAV e controllo full-speed non sostituibili con hash o FFmpeg. I vecchi V213 Bruegel avevano difetti artistici documentati; una revisione successiva non è automaticamente approvata.
- **Diritti:** riuso commerciale/territoriale delle fotografie e attribuzioni richiede conferma, non solo PD-Art/CC mostrata in registro. Musica V330 è un vincolo per i nuovi video, non modifica retroattivamente le copie esistenti.
- **Gold / sito / social:** nessuna autorizzazione e nessuna nuova approvazione in questa PR.
- **Lady V166:** prova tecnica storica presente, ma URL di download corrente/byte d'archivio non riottenuti in questa verifica. Non dire “recuperato oggi” senza il file.

### Politica anti-duplicazione

Le dieci coppie `opera + variante` hanno candidati originali, **0 nuovi render necessari per il solo stato `missing` del pannello**. Bloccare nuovi render per questi slot finché non siano documentati: file realmente irreperibile in TUTTI gli archivi, motivazione di revisione artistica specifica, nuova V331 camera frontale validata, diritti, assenza di run pesanti in corso e autorizzazioni per eventuali API con costo. Non mutare i contatori dei 36 slot o la coda editoriale con un report di recupero. **Consegna artistica = ancora PENDING**.

