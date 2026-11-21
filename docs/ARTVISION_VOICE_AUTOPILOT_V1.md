# ArtVision Voice Autopilot V1

## Obiettivo

Dopo che ArtVision salva un nuovo copione nel repository e crea una richiesta nella coda voice_jobs/requests, GitHub Actions avvia un runner locale sul PC. Il runner genera automaticamente una narrazione WAV e MP3 con Qwen3-TTS, riutilizzabile senza duplicazioni nelle due varianti Critico Standard e Critico Museum.

Questa è una prima integrazione tecnica in prova. **Gacrux rimane la voce Critico approvata V333.** Qwen è un candidato disattivato fino all'approvazione del proprietario. Questa integrazione NON modifica la pipeline Gemini attuale e NON cambia la voce dei video esistenti.

## Configurazione una tantum

1. Da GitHub, aprire Settings > Actions > Runners > New self-hosted runner. Sul PC Windows seguire i comandi forniti da GitHub e assegnare l'etichetta artvision-voice. Non condividere il token del runner. Usare privilegi minimi e proteggere il branch main: su repository pubblico, un runner self-hosted richiede particolare attenzione alla sicurezza.
2. Installare Python compatibile con Qwen, ffmpeg e le dipendenze ufficiali qwen-tts, torch, numpy, soundfile. Scaricare i pesi alla prima prova (diversi GB). Un PC i7/16 GB può tentare l'inferenza su CPU, potenzialmente molto lenta; una GPU NVIDIA sarebbe preferibile.
3. Sul runner definire le variabili locali ARTVISION_VOICE_REFERENCE_WAV e ARTVISION_VOICE_REFERENCE_TEXT_FILE: la prima indica un WAV registrato dal proprietario, la seconda un file UTF-8 con trascrizione esatta della registrazione. Conservare entrambi FUORI dal repository pubblico e accessibili solo dal PC.
4. Quando il proprietario ha ascoltato e approvato la prova Qwen, modificare esplicitamente il profilo qwen_owner_candidate nel file config/artvision_voice_profiles_v1.json impostando approved a true. Fino a quel momento la generazione è bloccata intenzionalmente.

## Innesco automatico dopo il copione

Il produttore di copioni deve salvare un file .txt o .md nel repository e creare in voice_jobs/requests un nuovo JSON, sempre con un work_id univoco. Per esempio:

    {
      "work_id": "my_painting_001",
      "format": "critico_standard",
      "script_path": "editorial/my_painting_001.txt",
      "voice_profile": "qwen_owner_candidate",
      "allow_paid_api": false,
      "auto_publish": false
    }

Quando il JSON arriva su main, la GitHub Action artvision-voice-autopilot-v1 genera il WAV/MP3 sul runner in locale. In alternativa si può avviare il workflow manualmente indicando il file già presente. Se il PC è spento, il job resta in attesa secondo le normali regole di GitHub e non può sintetizzare finché il PC non torna disponibile.

Il singolo audio ha un hash che dipende da testo, modello, profilo e campione vocale; riutilizzare un WAV già generato solo quando tutti questi elementi coincidono. L'artifact denominato ARTVISION_VOICE_REVIEW contiene VOCE.wav, VOCE.mp3, COPIONE.txt e VOICE_MANIFEST.json. Il file di riferimento vocale personale non viene inserito nell'artifact né nel repository.

Controllare il piano senza inferenza:

    python src/artvision_voice_autopilot_v1.py --job voice_jobs/requests/my_painting_001.json --plan

## Mancano ancora due collegamenti prima di considerarlo operativo per tutti i video

- Installare e provare effettivamente il runner sul PC con un campione autorizzato, verificando qualità, tempi e consumi reali.
- Aggiungere ai renderer correnti il download dell'artifact, la validazione del WAV/SHA, l'allineamento parole-scene con Whisper e l'uso dello STESSO WAV per entrambe le varianti. I vecchi workflow non sono ancora modificati da questa PR.

**Non dichiarare completato alcun video sulla base di un solo MP3 generato.** Fare QA tecnica e ascolto artistico. Non pubblicare automaticamente, non sostituire Gacrux senza approvazione, non utilizzare API a pagamento, non adottare in fallback Edge o gTTS.

Codice modello: https://github.com/QwenLM/Qwen3-TTS
Studio alternativo: https://github.com/jamiepine/voicebox
