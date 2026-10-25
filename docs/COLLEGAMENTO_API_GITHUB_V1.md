# Collegamento chiavi e fonti gratuite V1 — Tra le Pagine

**Stato:** adapter aggiuntivo di ricerca documentale: non sostituisce il render, il controllo editoriale, la voce Gacrux, l'Archivio V7 o il generatore AI Horde.

## Secret registrati dall'utente (screenshot 25/10/2026)

| Nome | Uso corrente |
|---|---|
| `AIHORDE_API_KEY` | Generatore originale di prova `immagini-gratuite-v1.yml`, solo con avvio manuale |
| `AIHORDE_API_KEY_2` | Riservato, non selezionato automaticamente per aggirare quote o code |
| `GEMINI_API_KEY` | Usato dai workflow voce già operativi, non alterato |
| `OPENROUTER2` | Riconosciuto per il controllo configurazione; **nessuna inferenza attiva** |
| `PIXABAY` | Alias accettato dal nuovo adapter per immagini e piccoli video |
| `PIXABAY_API_KEY` | Nome alternativo già documentato nel progetto |
| `PRIXIBAY2` | Nome visto nello screenshot, **non** usato automaticamente: può essere un refuso |
| `PEXELS_API_KEY` | Previsto da Archivio Media V7 se esiste; non indicato nello screenshot |

I nomi `AIHORDE_AP...` e `GEMINI_API...` erano troncati nella foto: il sistema non può inferire che il nome completo sia esattamente quello previsto, né leggere i valori degli Actions secrets.

## Uso da Android
1. Vai in GitHub → [Actions → Fonti immagini gratuite V1](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/fonti-immagini-gratuite-v1.yml).
2. **Run workflow → provider=status**. L'Artifact `fonti-immagini-v1-...` contiene `REPORT.json` con **soltanto booleani** per la presenza dei secret. Non mostra token.
3. Poi **provider=pixabay**, `kind=image` o `kind=video`, `query=victorian garden`, `limit=3`. Vengono cercati fino a tre candidati, non scaricati.
4. Per materiali Creative Commons usa **provider=openverse**, `kind=image`, con nessuna API key.
5. Apri ogni pagina originale, verifica licenza, attribuzioni, fedeltà al copione e adeguatezza commerciale.
6. Per immagini narrative che non esistono negli archivi prova separatamente **[Immagini gratuite V1 / AI Horde](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/immagini-gratuite-v1.yml)** con nome modello esplicito e account primario.

Il workflow di ricerca ha una modalità di default `status` senza rete; non attiva generazione o pagamento automatici.

## Scelta tecnica

- **Prima:** archivio approvato → fonti pubbliche senza chiave (Openverse V7) → fotografia/video Pixabay selezionato. Per illustrazioni originali, AI Horde separato come ultima opzione.
- L'API Pixabay chiede una ricerca fatta da un utente vero e cache di 24 ore; sconsiglia query automatizzate in massa e download sistematici. Perciò questo bridge è **una ricerca singola esplicita da Android**, non un crawler continuo.
- 429, limite o payload non valido interrompono senza retry a raffica. Non si registrano token, URL con chiave o risultati a pagamento.
- OpenRouter non viene chiamato: i modelli `:free` hanno limiti e nessuna chiave garantisce il diritto a usare modelli a pagamento. Nessuna spesa autorizzata.
- Le due chiavi AI Horde non sono usate in parallelo per manipolare le quote dei volontari.
- Accesso ai dati e uso commerciale dell'immagine NON sono la stessa cosa; `review_required=true` resta fino ad approvazione.

## Limiti del modulo

La ricerca restituisce fino a cinque **candidati con link alla fonte**. Non scarica e non registra immagini nel catalogo video, non produce MP4, non pubblica. Test offline `tests/test_free_sources_bridge_v1.py`. I provider aggiuntivi del catalogo V2 da 45 fonti non sono ancora integrati.

Fonte primaria: [Pixabay API](https://pixabay.com/api/docs/) (cache 24h e no download di massa); [Openverse API](https://api.openverse.org/v1/); [OpenRouter limits](https://openrouter.ai/pricing).
