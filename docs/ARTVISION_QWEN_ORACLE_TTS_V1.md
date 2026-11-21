# ArtVision | Qwen3-TTS 0.6B su Oracle Always Free — provino V1

**Stato reale:** connettore GitHub predisposto, NON server Oracle creato, NON generazione verificata su una VM del proprietario, NON voce sostitutiva approvata. Non cambia i video esistenti né il motore predefinito Google Gemini Gacrux (regola V333).

## Risorse e costo
Secondo i limiti ufficiali OCI aggiornati a novembre 2026, una tenancy **Always Free** usa in totale **2 OCPU ARM Ampere A1 e 12 GB RAM** (1.500 OCPU-ore e 9.000 GB-ore/mese). Alcuni README riportano ancora la vecchia quota 4/24: NON usarla per dimensionare nuove VM Always Free. L'istanza A1 è spesso indisponibile in una regione; `Out of host capacity` non è un problema di codice. Non passare a PAYG per risolverlo senza una scelta informata; monitorare costi e limiti, mantenere le risorse etichettate **Always Free eligible**, evitare storage/risorse fuori quota. Oracle può recuperare VM considerate inattive.

Fonte Oracle: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

## Motore preferito per iniziare
- Engine pure C, con API HTTP e supporto Linux ARM/Italiano: https://github.com/gabriele-mastrapasqua/qwen3-tts
- API documentata: https://github.com/gabriele-mastrapasqua/qwen3-tts/blob/main/docs/serving/api.md
- Variante specifica Oracle (README con limiti storici 4/24, prestazioni basate su VM 4-core): https://github.com/TrinityTF/qwen3-tts-server

Non equiparare velocità del chip Apple M1 o di una VM ARM 4-core alle prestazioni A1 **2-core**: misurare veramente tempi, consumo RAM e qualità italiana. Il modello 0.6B non garantisce una voce migliore di Gacrux.

## Configurazione da browser Android (interventi una tantum)
1. Aprire https://cloud.oracle.com/ e creare/attivare l'account OCI Always Free, con verifica dei limiti nella **home region**. Evitare risorse a pagamento. Se l'A1 non è disponibile, NON creare macchine sostitutive a pagamento.
2. In **Compute > Instances > Create instance**, selezionare **VM.Standard.A1.Flex**, Ubuntu ARM64 contrassegnato Always Free, **2 OCPU e 12 GB RAM** e disco di boot entro i limiti gratuiti. Configurare accesso SSH custodendo la chiave privata; dal telefono Android si può usare un terminale SSH web/Android.
3. Nel server Ubuntu ARM64 installare build tools e OpenBLAS, seguendo il file BUILDING del motore upstream. Comandi di riferimento da verificare con la versione fissata del progetto:
   ```bash
   sudo apt-get update
   sudo apt-get install -y git build-essential libopenblas-dev curl ffmpeg
   git clone https://github.com/gabriele-mastrapasqua/qwen3-tts.git
   cd qwen3-tts
   make blas
   ./download_model.sh
   ./qwen_tts -d qwen3-tts-0.6b --serve 8080
   ```
   Durante `download_model.sh` selezionare **small / 0.6B CustomVoice**. Da server locale fare test su `http://localhost:8080/v1/health` e `POST /v1/tts`.
4. **Sicurezza obbligatoria**: non esporre la porta nativa **8080** a Internet. Pubblicare SOLO un endpoint HTTPS dietro un reverse proxy che **verifica realmente** un Bearer token segreto per tutte le chiamate; configurare TLS, firewall e limitazione dell'accesso. L'engine nativo NON offre autenticazione. Non considerare un semplice URL difficile come protezione. Valutare inoltre accesso privato alla VM per amministrarla.
5. Nel repo GitHub, **Settings > Secrets and variables > Actions**, inserire `ARTVISION_QWEN_TTS_URL` (solo URL base HTTPS) e `ARTVISION_QWEN_TTS_TOKEN` (Bearer verificato dal proxy). Mai copiare password/chiavi in issue, code, screenshot pubblici o documenti.
6. Una volta integrato il workflow nel branch principale, da GitHub Android aprire **Actions > ArtVision | Qwen Oracle ARM - private voice audition > Run workflow**. Scegliere una delle nove voci. Il job salva **VOCE_QWEN_PROVINO.wav**, l'eventuale MP3 e manifest come **artifact privato** nel workflow. Il test su pull request non contatta mai il server.

## Prossimo passo soltanto dopo ascolto
Confrontare il provino italiano con la voce Gacrux approvata: naturalezza, timbro adulto, accenti, pronuncia nomi artisti, pause, continuità tra paragrafi. Solo dopo approvazione esplicita implementare il router di produzione e l'allineamento reale delle parole per le scene. Per il medesimo quadro Critico Standard/Museum usare sempre lo **stesso WAV SHA-256**, non due sintesi. Se Oracle è irraggiungibile, segnalare il blocco e passare a lavorazioni indipendenti: **mai fallback automatico a una voce non approvata**.

**Nota:** questo PR non attiva un'istanza Oracle, non consuma crediti Vidu o Google e non dichiara un MP4 pronto.
