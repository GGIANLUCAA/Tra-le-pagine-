# ArtVision V92 — Klimt, due Cinema revisionati, veri MP4 e backup verificato (31/10/2026)

## Motivazione / difetto corretto
Dopo le revisioni **Critico Standard V91S** e **Critico Museum V91**, revisione NON DISTRUTTIVA dei soli due slot **Cinema Standard** e **Cinema Museum** di Klimt *The Kiss*. Dai fotogrammi reali degli originali: Cinema Standard aveva un finale con quadro troppo piccolo e bande nere; Cinema Museum continuava a mostrare sala/cornice durante parte della visione ravvicinata. Sono stati mantenuti i master originali V72/V73 (e lo ZIP Dropbox) senza alcuna sovrascrittura.

**Metodo:** sorgente pittorica autentica PD 4096×4188, SHA-256 `43e998b7b9dc6f935918dbd55ff1a3f34052b932d563e74e5d2d5dceb2660b24`; micro-camera e riprese motivate da volti, mani, rettangoli, cerchi, oro, fiori. Niente volti o dettagli inventati. AAC della musica originale **riutilizzato bit per bit** con ffmpeg stream copy, zero TTS/video AI e zero API a pagamento. Il renderer riproducibile è incluso negli ZIP, non è stata introdotta un'altra pipeline autonoma.

## MP4 reali V92
| Slot (sempre uno dei quattro originali) | Nuovo MP4 / durata | SHA-256 | Byte | AAC SHA-256 |
| --- | --- | --- | ---: | --- |
| Cinema Standard | `Klimt_Cinema_Standard_V92_REVIEW.mp4` / 47 s | `976e41fe604d0eac5396968a01eed5c3c7f42e5d71789a81a63a93e6de22816c` | 26.637.375 | `da38f2cc95030ccb137266d85e5f400eae83e8fe6ad41cb9f4ba7bd42759ff67` |
| Cinema Museum | `Klimt_Cinema_Museum_V92_REVIEW.mp4` / 52 s | `abc53905dda19f66e3bed9bed4bfc96e7627c583b52ca976dbff3dc70131cd10` | 26.063.294 | `5d68dcdf5cd3ad27e3ecd1bf08ec3f04b3e6929227458bfab18e927820804e9d` |

- Entrambi **H.264 720×1280, 20 fps**, rispettivamente **940** e **1.040 frame**. **FFmpeg -xerror decodifica integrale PASS**, verificata anche sui file destinati ai pacchetti.
- Gli hash AAC coincidono **esattamente** con le rispettive versioni originali; le due tracce Cinema sono diverse tra loro, come nei master. Musica: **Kevin MacLeod, Dreams Become Real, CC BY 4.0**; attribuzione inclusa.
- Standard: intro di forte impatto su volti/mani, passaggio ai motivi e prato, finale con **riproduzione completa del dipinto a larghezza quasi piena**, su fondale sfocato coerente, senza bande nere vuote. La tela originale è quasi quadrata: nel formato verticale 9:16 il quadro completo non può riempire l'altezza senza ritagli.
- Museum: sala e cornice dell'originale mantenute soltanto **0–10,5s** e **42–52s** (con brevi transizioni di entrata/uscita 10,5–11,3s e 41,3–42s); tra le due, dettagli pittorici senza cornice. **Sala e cornice sono ricostruzioni digitali, NON autentica sala/cornice del Belvedere**; non promuovere come autentiche né Gold V25.

## Backup fisico in Libreria privata
Cartella `/ArtVision/Klimt/V92_CINEMA_REVIEW/`:

- Standard MP4: `Klimt_Cinema_Standard_V92_REVIEW.mp4`; ZIP `KLIMT_CINEMA_STANDARD_V92_REVIEW_ANDROID.zip` **27.782.608 B**, SHA-256 `80797e6ec68e0dcb089756743c8b66025a4c52e69a5aea49b30eb90869d1d651`.
- Museum MP4: `Klimt_Cinema_Museum_V92_REVIEW.mp4`; ZIP `KLIMT_CINEMA_MUSEUM_V92_REVIEW_ANDROID.zip` **27.167.808 B**, SHA-256 `e79b7927fa7d20172647e72930b8e65b3954a04f28fbd127169b779990281b6c`.
- **Tutti e quattro caricati realmente e scaricati nuovamente**, SHA-256 identico al sorgente, **ZIP CRC PASS** (11 membri ciascuno) e MP4 interno hash identico al singolo.
- Ogni ZIP include vero MP4, copertina verticale 1080×1920, quattro bozze post (Facebook, Instagram, TikTok, YouTube), confronto fotogrammi originali/V92, QA JSON, fonte/licenze, renderer e LEGGIMI. Post NON pubblicati.
- Le due versioni Critico V91S/V91 e gli originali 4×1 rimangono intatti. **V92 sono revisioni degli stessi due slot, NON quinto e sesto video.**

## QA artistica e archivio — dichiarazioni precise
Il controllo estetico è stato eseguito su **contact sheet e fotogrammi campionati** di entrambi i video, non una visione/ascolto umano integrale. Le transizioni sono tagli motivati e richiedono giudizio finale del proprietario. **Gold V25 = 0, non approvato.** MP4/ZIP sono disponibili e verificati in **Libreria ChatGPT**, non nel player del sito: **site_import_verified=false, android_playback_verified=false**.

Verifica Cloudflare R2 `video-library-studio`, GET List Objects 31/10/2026 HTTP 200: prefissi esatti `ArtVision_Socrates_Cinema_Museum_V61_Senza_Persone_Review.mp4`, `Klimt_Cinema_Standard_V92`, `Klimt_Cinema_Museum_V92`, `Socrate_Critico_Museum_V90R3`, `Klimt_Critico_Standard_V91S` tutti **[]**. Questo prova solo l'assenza di oggetti con quei prefissi, non una ricerca globale su tutte le possibili chiavi. Il plugin import ChatGPT Video Library richiede fileParams selezionato dal proprietario: nessun upload R2 simulato, nessun playback Android dichiarato.

## Prossimo lavoro utile
1. Confronto artistico reale **Critico V91S/V91 + Cinema V92 Standard/Museum** con benchmark Socrate V90R3; correggere solo difetti visibili, non ritoccare inutilmente i master.
2. Ripristino Socrate Cinema Museum V61 nel sito con flusso autorizzato e **prova reale player**; se import via fileParams non è disponibile all'automazione, non dichiarare successo.
3. Solo dopo QA e due piloti end-to-end verificati considerare produzione seriale. Nessuna sesta opera, nessun social, nessuna spesa API o task duplicato.
