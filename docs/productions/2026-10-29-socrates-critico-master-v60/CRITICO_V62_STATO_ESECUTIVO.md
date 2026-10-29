# ArtVision Socrate — due versioni Critico V62 — progressione reale e blocco Gacrux

**Target:** gli ultimi due filmati DELLO STESSO QUADRO, `critico_standard` e `critico_museum`, con identico copione e identico file WAV Google Gemini 3.8 Gacrux.

## Risultato effettivamente verificato il 29/10/2026
- Il copione madre originale di 366 parole e dieci beat è stato fissato in `docs/productions/2026-10-29-socrates-critico-master-v60/COPIONE_GACRUX_V62.txt`. Non modificare autonomamente fra i due film.
- Creato il gate `src/artvision_socrates_gacrux_gate_v62.py` e il test `tests/test_artvision_socrates_gacrux_gate_v62.py` (2 verifiche passate).
- GitHub Actions **run 40892861596**, test completato `success`. Stato vero nel log della prova: `blocked_voice_free_tier_not_verified`. Il secret `GEMINI_API_KEY` è presente ma le variabili `GEMINI_TTS_FREE_QUOTA_CONFIRMED` e `GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED` sono VUOTE. **0 richieste TTS**, 0 spese, 0 WAV e **0 nuovi MP4 Critico**. Non interpretare il verde della CI come produzione o permesso V25.
- Google documenta free tier per `gemini-3.8-flash-tts`, ma non prova che QUESTA chiave GitHub sia associata a un progetto senza fatturazione. Chiave ≠ consenso.
- Primo ostacolo concreto: progetto Google AI Studio non attestato free-only e non fatturabile. Dopo verifica REALE del piano e della fatturazione, valorizzare le due repository variables a `true` e riavviare il workflow `.github/workflows/artvision-socrates-gacrux-v62.yml`. Il gate potrà usare Gacrux UNA SOLA VOLTA, archiviare VOCE.wav/cache/timecodes ed evitarne la doppia generazione per l'altra versione.
- In assenza delle attestazioni, continuare ad allestire solo le inquadrature e lo storyboard; non far finta di avere voce o video narrati finiti.

## Dossier artistico pronto per la realizzazione
- Dipinto autentico Met object 436105, `eaff5a04103361fed9fba6f10ea7bed80ccdc595d664b6997c6bd32f0eee06a6`, pubblico dominio.
- Musica Water Lily (Kevin MacLeod, CC BY 4.0), recording SHA `b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6`.
- Standard: montaggio analitico del dipinto (coppa, mani, corpo di Socrate, giovane in rosso, discepoli, Platone, catene, composizione). Prima inquadratura con titolo esatto in inglese, ritmo 0/3/7s.
- Museum: sala Gallery 632 del Met digitalmente ricostruita con **nessun visitatore in primo piano**, vera foto della cornice di Socrate (Szilas), percorso camera unico V57, ingresso/uscita nella stessa sala, licenza fotografica CC BY-SA 4.0 con attribution e ricostruzione dichiarata. Non è la sala attuale documentata.
- Due storyboards e un renderer di produzione voice-required con preflight, 14 immagini di verifica per regia e test tecnico anti-placeholder sono stati creati in questa sessione come ZIP di lavoro: `ArtVision_Socrates_2_Critico_V62_Produzione_Preparata.zip`, SHA `fdee779f0a43300b2bef4ad4783c2f6eb231c186d570f0e1cb50bd8c6c821ff2`, CRC OK, 43 file. I file locali ChatGPT **non sono in automatico presenti su GitHub**: non dichiarare distribuzione runtime solo perché esiste questo ZIP.

## Stato e successive prove
- `critico_standard`: `blocked_voice_free_tier_not_verified`, nessun MP4; schema regia e sorgenti pronti.
- `critico_museum`: `blocked_voice_free_tier_not_verified`, nessun MP4; stesso copione/audio futuro ma regia Museum V57 diversa.
- `cinema_standard` e `cinema_museum`: non rigenerare; Museum V61 senza teste tagliate in review.
- Dopo acquisizione WAV originale: verificare cache SHA del COPIONE ESATTO, timed sentences/ASR, miscelazione musicale con stessa traccia parlata per le due regie, render originali separati, full decode, vero ascolto e visione, ZIP/post e archivio privato V25. No presentazione di tempi stimati come sincronizzazione completa.
- **Pacchetto 4×1 ancora non completo.** Nessuna pubblicazione social o spesa video API.
