# ArtVision Fish Audio — integrazione API gratuita, Android-only (21/11/2026)

Il proprietario usa solo browser Android; NON richiedere PC o Google TTS nel nuovo flusso. Non inserire token nei commit o in ChatGPT.

## Stato

Questo è un prototipo su PR draft: provider Fish Audio e workflow di sintesi predisposti; CI offline esegue controlli senza chiamate alla API. **Non sono ancora disponibili un test di sintesi reale, una voce Fish approvata e il collegamento completo con i renderer ArtVision.** Non dichiarare video già prodotti. La produzione preesistente sul ramo main rimane invariata.

## Setup 1 volta sola da Android

1. Verificato 21/11/2026: il Secret GitHub `SpeechtoText` è PRESENTE e l'autenticazione all'API Fish con GET /wallet/self/api-credit ha restituito HTTP 200 (senza generare audio e senza mostrare la chiave). Il workflow legge ora `secrets.FISH_API_KEY || secrets.SpeechtoText`, quindi non creare una seconda chiave né rinominare il Secret. Non comunicarla via chat.
2. Nel sito https://fish.audio creare una voce personale privata dall'interfaccia di Voice Cloning usando una registrazione propria pulita, possibilmente 1–2 minuti con registrazioni espressive diverse; testarne una breve narrazione italiana. Il sito restituisce un Voice Model ID / reference_id. Se non appare, consultare la sezione My Voices oppure API docs di Fish.
3. Manca ancora un secondo GitHub Actions Secret: FISH_VOICE_ID (valore: riferimento del modello vocale scelto). Mai incollare l'id vocale in una repo pubblica per default.
4. In GitHub Settings > Secrets and variables > Actions > Variables, creare ARTVISION_FISH_VOICE_APPROVED = true **solo dopo l'ascolto e approvazione esplicita della voce**. Finché non è true, solo job review_only.
5. Quando la PR sarà validata e unita a main, un job JSON sotto voice_jobs/fish_requests attiverà la GitHub Action automaticamente. Prima del merge, avvio manuale solo se il file job esiste nel ramo eseguito.

## Un job di test

Salvare un copione vero (almeno 10 parole e massimo 450 caratteri) in editorial/voce_fish_prova.txt. Creare voice_jobs/fish_requests/voce_fish_prova.json:

    {
      "work_id": "voce_fish_prova",
      "provider": "fish_audio_free",
      "format": "critico_standard",
      "script_path": "editorial/voce_fish_prova.txt",
      "review_only": true,
      "allow_paid_api": false,
      "auto_publish": false
    }

Il job GitHub genera un MP3 e un file manifest con hash, contenuti in un artifact della run. Utilizza in modo esplicito l'header model: s2.1-pro-free e rifiuta fallback sul modello a pagamento. Una sola traccia vocale per quadro, da riutilizzare nei due Critico.

## Limiti

- Il provider Fish Audio dichiara s2.1-pro-free a costo API $0 con Fair Use e senza garanzie; l'offerta è confermata almeno fino al 30/11/2026 ma può cambiare. Non bisogna supporre gratuità indefinita né generazione seriale illimitata.
- Il piano gratuito può conservare e utilizzare audio e richieste per miglioramento; caricare solo registrazioni proprie autorizzate e consapevoli delle condizioni.
- Le condizioni di uso commerciale dei video finali devono essere verificate prima della monetizzazione. Nessuna pubblicazione automatica nella versione di prova.
- Il test va ascoltato integralmente: naturalezza, dizione italiana, timbro, pause, enfasi; il solo file MP3 tecnicamente valido non basta.
- Nessuna API ASR a pagamento: per sincronizzare le parole e le scene usare il Whisper locale già integrato nelle vecchie pipeline o altri metodi offline già presenti.

## Collegamento mancante

Il copione generato da ArtVision deve creare il file JSON di richiesta e il renderer deve prelevare l'asset MP3 verificandone SHA. Per ora questi due passaggi non sono cablati automaticamente in tutti i vecchi produttori; non fingere che questa PR abbia già completato l'automazione end-to-end. Una volta scelta la voce, usare FISH_VOICE_ID nel lavoro senza dover ricaricare la registrazione.

Fonti tecniche:
- https://docs.fish.audio/features/voice-cloning
- https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech
- https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits
