# ArtVision · Agent Skills V1 — integrazione prudente (12 novembre 2026)

## Stato
**Proposta di integrazione nel branch di lavoro, non installazione operativa su main.** Questo intervento crea tre skill *originali*, specifiche del progetto, in `.agents/skills`. Codex le rileva se il branch che le contiene viene aperto in un ambiente Codex compatibile. La chat ChatGPT Android **non le installa automaticamente** solo perché sono committate in GitHub.

Nessuna API nuova, package npm, processo periodico, cron, renderer, chiamata AI, segreto, nuovo acquisto, video generato, modifica Gold o pubblicazione automatica.

## Motivazione
Da Skills.sh sono utili le idee di [Verification Before Completion](https://skills.sh/obra/superpowers/verification-before-completion), [Systematic Debugging](https://skills.sh/obra/superpowers/systematic-debugging), [GH Fix CI](https://skills.sh/openai/skills/gh-fix-ci), [Remotion Best Practices](https://skills.sh/remotion-dev/skills/remotion-best-practices). **Non abbiamo copiato le loro istruzioni, file o script**: le tre skill locali sono istruzioni create ad hoc che richiamano strumenti e vincoli già disponibili in questo repo.

## Skill locali
| Nome | Quando usarla | Strumenti esistenti |
| --- | --- | --- |
| `artvision-regia-umana` | Storyboard, voce/scena, ritmo, controllo dell'effetto umano | `docs/REGIA_UMANA_SGUARDI_V1_20261111.md`, V320/V321/V322 |
| `artvision-video-evidence` | Prova tecnica MP4, ZIP, fonte, QA e consegna Android | `src/ai_director_visual_qa_v1.py`, `src/quality_director_v17.py`, V91/V94/V96/V99 |
| `artvision-ci-triage` | Log GitHub Actions, cause e correzioni senza alterare owner | GitHub run/job/log, test già presenti |

La precedenza resta: richieste del proprietario e policy; `AGENTS.md`, `docs/REGOLE_ATTIVE.md` e regole specifiche; poi le skill. Una skill non può promuovere un render a Gold, generare Vidu pagato o pubblicare da sola.

## Attivazione e prove
1. Verificare i tre manifest `SKILL.md`: frontmatter `name`/`description`, nomi univoci, link ai file esistenti.
2. Fare revisione del PR, verificare assenza di modifiche a `.github/workflows`, `src/`, `queue/`, script renderer e master.
3. Se approvato, integrare il branch. Aprendo il repository in Codex, le skill di progetto si trovano in `$REPO_ROOT/.agents/skills`. Rilevamento automatizzato dipende dall'ambiente Codex utilizzato.
4. Prova non distruttiva su un report/artifact già esistente: ottenere diagnosi e segnali da `artvision-video-evidence`, senza rifare il rendering.
5. Valutare separatamente **Remotion Best Practices** solo se utile a una vera pipeline Remotion/React di prova; non avviare `npm install` o aggiungere una nuova pipeline al solo scopo di 'avere la skill'.
6. Se una skill si comporta in modo inadeguato, rimuovere la directory della sola skill senza alterare i video o i workflow.

## Sicurezza e costi
Le skill sono materiale istruttivo: codice o comandi esterni vanno verificati prima di eseguirli. Non affidare credenziali, token o materiali privati a script di terzi senza verifica. Evitare installazione massiva: riduce conflitti di istruzioni, dipendenze e rischi. Eventuali minuti Actions, rendering cloud o servizi esterni non diventano gratuiti grazie a Skills.sh.

## Misure di riuscita
- Diagnosi GitHub con run, primo step causale e stato attuale, senza confondere errore storico e attivo.
- QA che non dichiara successo se non ha aperto il vero MP4 e provato la sua decodifica/download.
- Brief di regia con corrispondenza precisa voce–fonte–timecode e meno formule ripetitive.
- Nessuna regressione del sistema owner, nessuna pubblicazione o spesa non autorizzata.

**Limite dichiarato:** questa fase prepara la disciplina e la disponibilità delle skill per Codex. Non aumenta automaticamente qualità, capacità di rendering o numero di video; l'effetto richiede un test su un video reale, poi confronto A/B.


## Guida operativa SOLO ANDROID (senza computer)
**Vincolo del proprietario:** operatività interamente da smartphone Android. Non chiedere PC, shell locale, Termux, Node.js o installazione con `npx` sul telefono. I comandi negli SKILL.md sono istruzioni per l'agente in un ambiente cloud, **non azioni da eseguire sullo smartphone**.

### Come vedere la proposta
1. Aprire dal telefono [PR #277](https://github.com/GGIANLUCAA/Tra-le-pagine-/pull/277) in GitHub Mobile o Chrome Android.
2. Aprire **Files changed** per vedere le tre skill e questa guida; dalla pagina **Checks** si controllano le verifiche effettivamente eseguite, senza supporre successi.
3. La PR è una bozza isolata: **non eseguire Merge** finché non è validata. Nessun test video è implicito nel suo stato.

### Come usare le skill senza terminale locale
- **Percorso A — ChatGPT Android + connettore GitHub:** chiedere in chat «Analizza la run X con la procedura `artvision-ci-triage`» oppure «Verifica il mio video Y applicando `artvision-video-evidence`». L'assistente deve prima leggere il relativo SKILL.md dal repository e, quando possibile, le prove reali. Questa è applicazione guidata delle istruzioni, **non installazione automatica delle skill nella normale chat**.
- **Percorso B — Codex Cloud su Android:** aprire Codex nell'app ChatGPT o dal sito, usare un ambiente cloud che abbia accesso a `GGIANLUCAA/Tra-le-pagine-`, e selezionare il branch che contiene `.agents/skills`. L'agente Codex può allora rilevare le skill locali del repo; il rilevamento dipende dalla disponibilità e configurazione dell'ambiente. Gli ambienti si configurano tramite web, che può essere aperto da Chrome Android; non occorre un PC.
- **Percorso C — GitHub Mobile:** le Actions con `workflow_dispatch` già presenti sul branch predefinito possono essere avviate dal menu **Actions > Workflows > Run workflow**, scegliendo gli input previsti; un workflow nuovo, invece, deve esistere in `main` per poter essere avviato manualmente tramite GitHub. **Questa PR non aggiunge nuovi workflow**.

### Prompt da usare dalla chat Android
> Nel repository GGIANLUCAA/Tra-le-pagine-, leggi prima AGENTS.md e docs/REGOLE_ATTIVE.md, poi la skill .agents/skills/artvision-ci-triage/SKILL.md nel branch feature/artvision-curated-agent-skills-20261112. Analizza lo stato attuale del workflow/run che ti indicherò e riportami prove, causa e intervento minimo. Non creare costi, non eseguire merge e non pubblicare video.

### Limiti e prossima prova
Senza un MP4 realmente accessibile, il controllo video si ferma a `UNVERIFIED_MEDIA`. Per testare la skill da Android usare un artifact o una Release esistente, controllando accessibilità dei byte, QA tecnico, valutazione artistica e diritti separatamente. Nessun avvio a tempo, costo API, nuova subscription o richiesta di credenziali.
