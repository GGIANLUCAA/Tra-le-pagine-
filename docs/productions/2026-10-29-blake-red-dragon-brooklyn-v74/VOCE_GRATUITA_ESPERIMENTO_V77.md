# ArtVision Blake — alternative vocali davvero gratuite (esperimento V77)

## Fonti ufficiali consultate 29/10/2026

1. Google **Gemini Developer API** dichiara che `gemini-3.8-flash-tts` ha un Free Tier per token di testo e audio (https://ai.google.dev/gemini-api/docs/pricing). **La voce Gacrux resta la prima scelta approvata**.
2. Google specifica che **l'API key eredita il livello di fatturazione dal progetto Google Cloud associato**, quindi possedere la chiave non dimostra da sola il costo zero (https://ai.google.dev/gemini-api/docs/billing/). Un progetto associato a un conto di fatturazione attivo può generare costi, anche se quel modello è gratis nel Free Tier. Verificare l'etichetta Free nel progetto, non forzare a `true` una variabile non attestata.
3. **Kokoro-82M** (https://huggingface.co/hexgrad/Kokoro-82M) è open source Apache-2.0, con voce maschile italiana `im_nicola` e femminile `if_sara`. Il modello si esegue localmente senza chiamate API a pagamento e senza segreti Google.
4. Su repository GitHub **pubblico** i runner standard `ubuntu-latest` sono gratuiti (https://docs.github.com/en/billing/concepts/product-billing/github-actions). Il repository di ArtVision risulta pubblico; lo storage degli artifact va comunque mantenuto entro le quote incluse.

## Esperimento, non cambio del contratto
- Unico obiettivo: dimostrare che il copione italiano di Blake di 282 parole può diventare un WAV reale **senza addebiti di servizi vocali**. Tentare due Critico **sperimentali** con WAV letteralmente identico per entrambi.
- Voce sperimentale **Kokoro Nicola non è Gacrux**. Non falsificare il nome della voce nelle schede o nei file. Questi filmati non contano come Gold Master 4×1, non sostituiscono l'audio Gacrux richiesto dal contratto V58/V68.
- Controllare intelligibilità, accento, naturalezza, pronunce, cadenza e sincronia. Una voce di qualità insufficiente va scartata, anche se gratuita.
- Nessuna produzione in serie, nessuna pubblicazione sociale, nessuna modifica dei Cinema V76, dei master Socrate o dei preset globali; nessuna richiesta di chiavi o abbonamenti aggiuntivi.
- Output sperimentale: `output/artvision-blake-free-voice-v77/`, allegato GitHub Actions con WAV demo, WAV completo e, **solo se il TTS funziona davvero**, due MP4 sperimentali e ZIP.
