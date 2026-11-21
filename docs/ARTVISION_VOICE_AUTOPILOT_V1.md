# ArtVision Voice Cloud V1 — esclusivamente Android, browser e cloud

## Scelta del proprietario — 21 novembre 2026
Non utilizzare PC (nemmeno come runner), voce Google/Gemini o sintesi locale. Per le nuove voci usare Qwen3-TTS tramite servizi terzi, iniziando dalla demo ufficiale Hugging Face Qwen/Qwen3-TTS (ZeroGPU). Tutto l'uso e la configurazione avvengono dal browser Android. Non promettere che il livello Free possa sostenere produzioni di massa.

La pipeline storica Gemini/Gacrux del ramo main non viene modificata da questa proposta: soltanto dopo scelta e ascolto del proprietario si può cambiare il narratore del Critico. Non ripiegare sulle vecchie voci e non attribuire un'approvazione non concessa.

## Come dovrebbe essere il flusso

1. ArtVision scrive un nuovo copione e lo salva come file nel repository.
2. Il produttore di copioni crea un job JSON nella cartella voice_jobs/requests/; quando arriva su main GitHub Actions lo rileva automaticamente.
3. Una GitHub Action gira su ubuntu-latest (server di GitHub, non sul telefono né sul PC), scarica privatamente il campione audio e la sua trascrizione da un dataset privato Hugging Face e invia la sintesi al servizio Qwen3-TTS ZeroGPU.
4. Al completamento salva un WAV, un MP3, il copione e una manifest SHA nell'artifact GitHub. Un'unica narrazione deve essere riusata per Critico Standard e Critico Museum.
5. Il renderer va collegato per leggere i risultati reali, verificare la SHA, allineare Whisper e montare i video, conservando la revisione artistica.

**Stato V1**: workflow in PR draft; test offline del codice, nessuna sintesi Qwen reale ancora svolta. Manca ancora il collegamento end-to-end al produttore di copioni e ai renderer storici. Questo non è un sistema di massa già funzionante.

## Setup una volta sola dal browser Android

### A) Prova vocale immediata
Apri https://huggingface.co/spaces/Qwen/Qwen3-TTS sul telefono. Vai su "Voice Clone (Base)", seleziona 1.7B, carica 15–30 secondi di voce pulita e incolla la trascrizione esatta. In "Language" la demo ufficiale corrente ha "Auto" ma non una voce esplicita "Italian": fare un test con testo italiano prima di approvare qualità e pronuncia.

### B) Archivio del campione per l'automazione
Crea un dataset **privato** nel tuo account Hugging Face e carica due file: voice_reference.wav e voice_reference.txt (trascrizione esatta). Non caricare la voce in una repository pubblica. Il file wav è un riferimento personale; il servizio pubblico ZeroGPU che lo elabora è un ulteriore soggetto esterno, quindi valutare la relativa privacy.

### C) Collegamento GitHub dal browser
Nel repository vai a Settings > Secrets and variables > Actions:
- Secret HF_TOKEN: token Hugging Face con accesso in lettura al dataset privato, preferibilmente limitato a questo dataset.
- Variable ARTVISION_HF_VOICE_DATASET: percorso owner/nome-dataset del dataset privato.
Non incollare token nelle chat, nei file o nei log.

## Profilo e richiesta di test

Il profilo in config/artvision_voice_profiles_v1.json è qwen_hf_candidate, non approvato. Per una demo testata consapevolmente si può usare review_only=true con un copione di massimo 350 caratteri.

Esempio: creare editorial/my_painting_sample.txt e voice_jobs/requests/my_painting_sample.json:

    {
      "work_id": "my_painting_sample",
      "format": "critico_standard",
      "script_path": "editorial/my_painting_sample.txt",
      "voice_profile": "qwen_hf_candidate",
      "review_only": true,
      "allow_paid_api": false,
      "auto_publish": false
    }

Dopo ascolto e approvazione esplicita si può cambiare approved a true. Solo allora i job senza review_only possono generare la voce Qwen scelta.

## Costi e limiti reali

La demo Hugging Face ZeroGPU offre circa 5 minuti GPU/giorno a un account Free autenticato, non 5 minuti di narrazione garantita. Il modello e la demo possono richiedere più chiamate per un copione lungo; limiti, code, timeout e cambi endpoint possono interrompere il processo. Il codice attuale fa al massimo 4 segmenti per job, nessun fallback ad API a pagamento. Una quota gratuita esaurita **non viene aggirata** cambiando account o passando a un servizio a pagamento.

Per una produzione continuativa di molti video, dopo la prova valutare un server Qwen dedicato su Oracle Cloud Always Free (disponibilità, account e prestazioni da verificare) o un provider API a pagamento solo con consenso specifico. Alternative: Replicate Qwen3-TTS, ma non è una tariffa gratuita illimitata.

La GitHub Action è intenzionalmente solo una prima integrazione. Non va unita al main per produzione finché non sono stati testati API, qualità in italiano, autorizzazioni, accesso al dataset, copie audio e montaggio. Non registrare spese e non dichiarare video completi quando manca WAV reale.

Riferimenti:
- https://huggingface.co/spaces/Qwen/Qwen3-TTS
- https://huggingface.co/docs/hub/spaces-api-endpoints
- https://github.com/QwenLM/Qwen3-TTS
- https://github.com/TrinityTF/qwen3-tts-server
