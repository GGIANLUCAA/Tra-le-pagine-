# Azure Speech — integrazione pilota V1 (30/10/2026)

Stato: PROPOSTA/PILOTA, NON ATTIVO. L'utente autorizza l'aggiunta di Azure Speech come alternativa a Google, non la sostituzione della voce approvata.

## Contratto di integrazione
- Provider `azure_speech`, opzionale; Google/Gacrux rimane default e fallback. Nessun cambio ai 4 preset ArtVision, ai render esistenti, alle automazioni e alle regole QA.
- Credenziali esclusivamente in GitHub Actions Secrets (`AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`), mai nel codice, nei log o in frontend. Richiedere all'utente di configurare una risorsa Speech F0 e inserire i segreti, senza incollare la chiave in chat.
- Nessun upgrade S0, nessuna spesa senza consenso; verifica del piano F0 e delle quote prima di ogni generazione; stop al raggiungimento del budget gratuito.
- API REST Azure TTS `https://{region}.tts.speech.microsoft.com/cognitiveservices/v1`, header `Ocp-Apim-Subscription-Key`, `Content-Type: application/ssml+xml`, output audio WAV o MP3; non stampare credenziali. Controllare disponibilità delle voci nella regione.
- Voci candidate italiane: `it-IT-DiegoNeural`, `it-IT-IsabellaNeural`, da verificare nell'elenco ufficiale al momento del test. Parametri SSML pause, rate e pitch moderati e verificati per la voce scelta.
- Prova A/B: medesimo copione, Google e Azure, normalizzazione volume e comparazione di naturalezza, pronuncia, pause, sincronizzazione, costo. Solo approvazione esplicita abilita Azure per i master.
- Conservare audio, metadati provider/voice, testo, hash, durata e timestamps per sincronizzazione. Fallimenti o quota esaurita => Google, senza retry incontrollati.
- La sintesi vocale non costituisce un video completo, un master approvato o un file pubblicato.

## Prossimo passo
Implementare adapter e test in branch separato dopo configurazione sicura dei segreti, senza alterare pipeline produzione. Documentazione Microsoft: https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech
