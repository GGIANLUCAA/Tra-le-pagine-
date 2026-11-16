# Control Center & Automazione — Piano di miglioramento e handoff per GPT

Data: 16 novembre 2026
Stato: **proposta — nessuna modifica al codice o alla produzione**
Destinatari: proprietario del progetto · agenti GPT che lavorano sul repository

---

## 0. Scopo e come usare questo documento

Questo documento serve a due cose:

1. Descrivere, in modo verificabile, **come migliorare l'automazione e il Centro di controllo** del progetto (ArtVision / La Storia Rivive / WIP "Tra le Pagine").
2. Fare da **handoff per GPT**: contiene i vincoli, le regole e le prove che un agente esterno deve rispettare **prima** di toccare qualsiasi cosa, così da non perdere lavoro già fatto e non degradare il progetto.

Regola d'uso per GPT: **leggere prima l'intero documento, poi i file di regole citati al §9.** Nessuna azione va eseguita se contraddice il §1 o il §5.

---

## 1. Regole inviolabili (guardrail)

Queste regole non si negoziano e valgono per ogni fase:

- **Sola lettura / GET-only.** Il Centro di controllo non scrive, non avvia workflow, non modifica dati.
- **Nessuna spesa automatica.** Nessuna chiamata a servizi a pagamento, nessun credito API, nessuna generazione video, senza autorizzazione esplicita del proprietario.
- **Nessuna pubblicazione automatica.** Produrre un video e pubblicarlo sono permessi separati.
- **Un successo tecnico non è un risultato.** "Run success" ≠ MP4 verificato ≠ Gold artistico ≠ autorizzazione a pubblicare.
- **Non toccare i master approvati** né i workflow di produzione attivi (§5).
- **Modifiche minime, su ramo + PR**, con CI; nessun merge/riavvio automatico su produzione finché non provato su un caso reale.
- **Niente segreti nel repository** (pubblico): nessuna API key, token, URL privato o log grezzo.
- **Niente stati inventati.** Se una fonte non risponde, il dato resta "non disponibile": nessuno zero o "verde" fittizio.

---

## 2. Stato attuale (sintesi verificata dai file)

**Centro di controllo (preview, separato dal sito live)**
- Sorgente UI: `site/control-center-preview.html`; backend: `site/control-center-preview.worker.js`.
- Bundle di deploy generato da `scripts/build-control-center-preview.mjs`.
- Legge **tre fonti**: ultime 100 esecuzioni GitHub Actions, coda ArtVision su `main`, catalogo pubblico via **service binding** `VIDEO_LIBRARY`.
- Funzioni: Home/attenzioni, salute produzioni, diario, statistiche, ricerca quadri, "Ripara con GPT", link a chat ChatGPT (solo in `localStorage`).
- Limiti dichiarati: classificazione dei progetti/opere basata su **regex sul nome**; nessun service worker offline; freschezza dati senza indicatore esplicito di *stale*.

**Automazione**
- Cinque automazioni ChatGPT programmate (all'incirca 9:00 e 18:00) producono **bozze/slot**, non MP4 completi.
- La pipeline produce MP4 tramite workflow GitHub (es. `render-v3.yml`), con QA tecnica (`quality_director_v17.py`) e audit (`studio_integrity_v9.py`).
- Il **collo di bottiglia** è la generazione delle immagini: richiede scelte di budget dell'owner.
- Esistono già i gate/contratti ma **non ancora collegati** alla pipeline/UI: `src/studio_autonomy_gate_v1.py`, `src/studio_autonomy_report_v1.py`.

Fonti principali: `docs/CONTROL_CENTER_V1_READONLY.md`, `docs/STUDIO_AUTONOMY_ROADMAP_V1_20261109.md`, `AUTOMAZIONE_2_EPISODI_AL_GIORNO.md`, `README.md`.

---

## 3. Obiettivi e non-obiettivi

**Obiettivi**
- Rendere il pannello più **affidabile** (classificazione, freschezza dati, installabilità).
- Unificare la **decisione** per episodio (un solo verdetto verificabile).
- Abilitare **azioni sicure** (richieste via file, mai scritture dirette).
- Ridurre il **debito tecnico** (proliferazione di versioni, test).

**Non-obiettivi**
- Non automatizzare la pubblicazione social.
- Non introdurre spese senza consenso.
- Non riscrivere i renderer esistenti né i master approvati.
- Non dare al pannello permessi di scrittura su GitHub/R2.

---

## 4. Piano a fasi

### Fase 1 — Fondamenta (basso rischio)
1. **Classificazione config-driven.** Estrarre le regex di `projectForRun` e `catalogueWorld` (`site/control-center-preview.worker.js`) in un JSON versionato (es. `config/control_center_classification.json`).
   - *Accettazione:* stesse classificazioni sui dati attuali; nessun elemento classificato "other"/"Non rilevato" quando il progetto è noto.
2. **Indicatore di freschezza.** Mostrare "dati aggiornati alle HH:MM" e stato *stale* quando il campione è vecchio.
3. **Test.** Estendere `tests/control-center-preview.test.mjs` a endpoint e nuova classificazione.

### Fase 2 — Quick win PWA/UX
4. **Icone PWA raster** 192/512 (oggi solo `icon.svg`); verifica installazione su Chrome Android reale.
5. **Prefill ChatGPT** nel dialogo "Ripara con GPT" (`chatgpt.com/?q=<prompt breve>`); nessun invio automatico, i casi lunghi restano copia/incolla.
6. **Hardening deploy.** Bundling obbligatorio da `scripts/build-control-center-preview.mjs`; rimozione del fallback remoto storico.

### Fase 3 — Decisione unificata
7. **Collegare il gate.** `src/studio_autonomy_gate_v1.py` diventa il punto unico di decisione (dedup, retry solo read-only, blocco senza fonti/diritti), agganciato a un orchestratore.
8. **Verdetto per episodio.** Formalizzare `STUDIO_AUTONOMY_STATUS_V1.json` (da `src/studio_autonomy_report_v1.py`) come contratto d'ingresso della UI: `video_sha`, durata, diritti, Gold.
   - *Accettazione:* la UI mostra lo stato dal verdetto, non dal numero di run.
9. **Etichette di progetto.** Ogni workflow dichiara il progetto (tag/label): la classificazione non dipende più dal nome.

### Fase 4 — Azioni sicure (solo dopo decisioni dell'owner)
10. **Action-queue.** La UI produce solo `requests/<azione>.json` (pattern già in uso, es. `requests/site/studio_integrity_v9_request.json`); un workflow legge ed esegue. Il Worker resta GET-only.
11. **Automazione budget-gated.** Generatore immagini economico in **batch** con tetto per episodio/giorno, attivabile solo dopo scelta esplicita dell'owner.
12. **Lock/idempotenza.** Un solo produttore per coda (owner ArtVision vs coda storia), per evitare duplicazioni.

### Fase 5 — Igiene
13. **Consolidamento versioni.** Ridurre la proliferazione di script `vN` in moduli + config, con regression test unico.
14. **Audit segreti ricorrente** (riferimento: `docs/API_SECRETS_AUDIT_20261104.md`).

**Sequenza:** 1 → 2 → 3 → 4 (dopo decisioni) → 5 (continuo).

---

## 5. Cosa NON toccare (elenco esplicito per GPT)

- Workflow di produzione attivi e i loro cron/scheduler.
- Master video approvati, Gold, copertine di serie e pacchetti ZIP storici.
- Code del proprietario (`queue/`) e relativi stati.
- Credenziali, binding R2, permessi GitHub, token di amministrazione.
- Il sito live `video-library-studio.600led.workers.dev` (perimetro del pannello è la sola preview).
- La classificazione editoriale già approvata: si può estrarre in config, **non** riscriverla arbitrariamente.

Se una modifica sembra richiedere di toccare uno di questi punti: **fermarsi e chiedere.**

---

## 6. Come validare ogni modifica

- Unit test esistenti: `node --test tests/control-center-preview.test.mjs`.
- CI del pannello sul ramo preview (nessun deploy, nessuna produzione).
- Le modifiche alla classificazione vanno confrontate **prima/dopo** sugli stessi dati reali.
- Le modifiche al Worker vanno provate con il **bundling** completo, non distribuendo il solo `worker.js`.
- Le verifiche su Android (installazione PWA, deep link chat) restano prove manuali sul dispositivo.

---

## 7. Decisioni aperte per il proprietario

1. **Anteprime:** mantenere l'approvazione delle anteprime o autorizzare l'export MP4 senza OK intermedio?
2. **Budget immagini:** accetti un budget per la generazione automatica delle immagini, e qual è il massimo al giorno?
3. **Azioni dal pannello:** vuoi attivare l'action-queue (richieste via file) o mantenere tutto manuale?

Senza risposta a queste domande la **Fase 4 non parte**.

---

## 8. Istruzioni operative per GPT (prompt di handoff)

Quando un agente GPT lavora su questo progetto, deve:

1. Leggere prima: `AGENTS.md`, `START_HERE_GPT.md`, `docs/REGOLE_ATTIVE.md`, `config/editorial_rules.json`.
2. Rileggere i file reali e i log prima di stabilire una causa.
3. Preservare owner e master approvati; usare **modifiche minime** in ramo/PR.
4. Non spendere crediti, non riavviare produzioni concorrenti, non pubblicare.
5. Non inventare stati: se un dato non è verificabile, dichiararlo "non disponibile".
6. Fermarsi e chiedere quando una modifica tocca il §1 o il §5.

---

## 9. Riferimenti

- `AGENTS.md`, `START_HERE_GPT.md`, `docs/REGOLE_ATTIVE.md`, `config/editorial_rules.json`
- `docs/CONTROL_CENTER_V1_READONLY.md`
- `docs/STUDIO_AUTONOMY_ROADMAP_V1_20261109.md`
- `AUTOMAZIONE_2_EPISODI_AL_GIORNO.md`, `README.md`
- Codice pannello: `site/control-center-preview.worker.js`, `site/control-center-preview.html`, `scripts/build-control-center-preview.mjs`
- Test: `tests/control-center-preview.test.mjs`
- Gate/contratti: `src/studio_autonomy_gate_v1.py`, `src/studio_autonomy_report_v1.py`, `src/studio_integrity_v9.py`, `src/quality_director_v17.py`
