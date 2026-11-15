# ArtVision / Arbo Critico V333 — verifica accesso Gacrux del 15/11/2026

## Dati confermati, senza visualizzare la chiave
- Il segreto GitHub `GEMINI_API_KEY` esiste (ultimo aggiornamento 18/10/2026). La prova di sola lettura [Actions #43696004755](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43696004755) confronta *solo* il suffisso mascherato con quello mostrato in Google AI Studio: compatibile con **Progetto gpt**; un suffisso coincidente non equivale a confronto crittografico completo.
- Su Google AI Studio il progetto era **Free Tier**; nello screenshot Google Cloud la fatturazione di quello stesso progetto era disabilitata. Non sono state create chiavi, non è stata modificata la fatturazione e non sono stati acquistati crediti.
- Documentazione prezzi ufficiale Google: `gemini-3.8-flash-tts` ha input e output gratuiti nel **Free Tier / Standard**: https://ai.google.dev/gemini-api/docs/pricing .
- Le due variabili V333 di repository `GEMINI_TTS_FREE_QUOTA_CONFIRMED` e `GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED` sono state impostate `true` e verificate, senza modificare il segreto.

## Due prove reali, nessun video completato
1. [Run Arbo #43696305445](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43696305445): preflight e controllo costi PASS; la richiesta vocale `client.interactions.create(model='gemini-3.8-flash-tts')` è stata rifiutata: **404 Model not found**. Nessun WAV, MP4 o ZIP Critico valido.
2. [PR #310](https://github.com/GGIANLUCAA/Tra-le-pagine-/pull/310) ha sperimentato l'endpoint documentato `client.models.generate_content` con stessa voce `Gacrux` e stesso modello. [Run #43696854132](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43696854132): preflight e cost gate PASS, ma risposta **400 INVALID_ARGUMENT**, campi `speechMetadata` e `speechConfig` non riconosciuti dal backend Gemini Developer API di questo progetto. Nessun WAV, MP4 o ZIP Critico valido.
3. Dopo due tentativi, **STOP automatico delle prove TTS** secondo la regola owner anti-blocco. Rollback V334 del solo cambio API proposto in #310 per non lasciare nel ramo main un backend alternativo non funzionante.

## Stato operativo
- `CRITICO_STANDARD_ARBO = BLOCKED_GOOGLE_TTS_API_MODEL_ACCESS_404_400`; `CRITICO_MUSEUM_ARBO` resta distinto e mancante; non contare prove come consegne.
- L'errore HTTP **non** dimostra mancanza di credito, né autorizza una voce diversa. Voce obbligatoria: **Google Gemini TTS Gacrux italiana** in profilo approvato. Mai gTTS/Edge.
- Nessun lavoro Cinema o master approvato modificato, nessuna pubblicazione o Gold.
- Prossimo intervento prudente: verificare nella console Google che **esattamente la chiave/progetto Free Tier** abbia accesso operativo al modello `gemini-3.8-flash-tts` tramite l'endpoint correttamente supportato; solo dopo un controllo indipendente ripetere un singolo tentativo. Alternativa: riutilizzare **WAV Gacrux preesistente per il medesimo copione**, con hash del file e del testo verificati. Intanto continuare Cinema Standard/Museum indipendenti senza TTS.

## QA e contatori
- Nuovi Critico MP4 con FFmpeg/SHA/ZIP validati in queste due prove: **0**.
- Stati tecnici, artistici, diritti e pubblicazione sono distinti.

## Verifica aggiuntiva 15/11/2026 — secondo segreto storico
- Run privata in sola lettura [#43698067352](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43698067352), su branch dedicato `audit/artvision-gacrux-secondary-key-20261115`: `GEMINI_API_KEY2` **ESISTE** ma il valore completo risulta **identico** a `GEMINI_API_KEY` secondo confronto locale costante nel runner. Nessuna chiave/parte della chiave scritta nei log. È coerente con la chiave mascherata del progetto `Progetto gpt` mostrata in Google AI Studio.
- La produzione riuscita di Böcklin il 31/10 aveva effettivamente utilizzato `secrets.GEMINI_API_KEY2` (run #41231258203), ma ciò **non prova che il valore del secret sia ancora quello di allora**. La seconda variabile non offre ora un account Google indipendente né aggira i 404/400 recenti.
- **STOP** a ulteriori tentativi TTS con entrambe le variabili finché non si verifica una chiave e un endpoint realmente abilitati; mantenere Gacrux e l'audio storico approvato, niente altri provider e niente cambio/fatturazione automatica. Una chiave differente presente in Google AI Studio (progetto `Progetto gemini video`, Free Tier con billing disabilitato) **non è stata copiata** in GitHub né usata per effettuare richieste; occorrono controllo dei permessi API e autorizzazione specifica prima di eventuale sostituzione del SOLO secondo secret.
