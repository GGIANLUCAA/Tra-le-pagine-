# Stato reale — La ballata del vecchio marinaio (28 ottobre 2026)

**Stato: ASSET_DOWNLOAD_BLOCKED / VOICE_QUOTA_UNCONFIRMED / NO_MP4.**

## Lavori effettivamente completati
- Copione originale italiano di 380 parole; 20 passaggi narrativi con inizio, sviluppo e finale.
- Storyboard e schede visuali V35 con 20 incisioni differenti di Gustave Doré, tutte da una stessa serie storica.
- PROJECT_V13 in stato di bozza, copertina prevista, quattro testi social distinti con attribuzioni.
- Ricerca fonte: testo originale Samuel Taylor Coleridge (1798), https://www.gutenberg.org/ebooks/151; incisioni Doré, https://commons.wikimedia.org/wiki/Category:The_Rime_of_the_Ancient_Mariner_by_Gustave_Dor%C3%A9
- Nessuna richiesta Vidu o altra API video a pagamento. Nessuna pubblicazione.

## Test realmente eseguiti
- Primo workflow gratuito https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40692465019: la prima immagine Wikimedia restituisce HTTP 429; il controllo delle fonti non termina.
- Secondo workflow gratuito https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40692607025: stesso 429 su upload.wikimedia.org, unico fallback proxy restituisce 404. Nessuna immagine consegnata, nessun ZIP, nessun MP4.
- L'errore non dimostra che le incisioni non siano riutilizzabili; indica un limite di acquisizione su GitHub Actions. Non riprovare ripetutamente o aggirare protezioni del provider.

## Gate ancora mancanti
- Acquisizione delle 20 immagini originali, SHA256 e licenza verificata per ciascuna; verifica visiva e corrispondenza con frase.
- Quota gratuita Gemini Gacrux non confermata: non effettuare TTS a pagamento o sostituzioni silenziose.
- Render reale 9:16 H.264/AAC, durata, sincronizzazione, musica originale, QA V44/V55, ZIP SOLO VIDEO V36, pacchetto completo, eventuale import reale in Video Library Studio.
- **Non definire il progetto FINALE, pronto o pubblicabile.**

La pipeline gratuita resta nel repository per una futura acquisizione quando il rate limit cesserà, senza consumare crediti video.
