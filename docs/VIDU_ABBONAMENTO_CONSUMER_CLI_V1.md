# Vidu abbonamento consumer — collegamento ufficiale a Tra le Pagine (V1)

**Stato verificato 28/10/2026:** sorgente ufficiale individuata; workflow di sola lettura integrato nel ramo di prova. NON sono stati acquistati crediti, inviati task, scaricati nuovi video Vidu o usati servizi a pagamento.

## La scoperta utile
Il produttore ShengShu offre:
- Repository ufficiale: https://github.com/shengshu-ai/vidu-skills
- CLI: `vidu-cli@0.2.36` o successiva
- Per account consumer internazionale: `VIDU_TOKEN` ottenibile da https://www.vidu.com, menu avatar > **Vidu Token**
- Endpoint `VIDU_BASE_URL=https://service.vidu.com`

**Questa e' diversa da `VIDU_API_KEY` del portale developer platform.vidu.com**, che non risulta configurata nel repository e non usa automaticamente l'abbonamento creativo pagato.

Documentazione ufficiale:
https://github.com/shengshu-ai/vidu-skills/blob/main/README.md
https://github.com/shengshu-ai/vidu-skills/blob/main/references/parameters.md
https://www.vidu.com/vidu-claw

### Android: unica operazione di collegamento
1. Aprire `vidu.com`, entrare nell'account che possiede l'abbonamento.
2. Dal menu avatar aprire `Vidu Token` (se la voce non esiste, la funzione potrebbe non essere disponibile per il piano).
3. **Non inviare il token in chat.** Aprire https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions e creare un nuovo secret `VIDU_TOKEN`.
4. Una volta che questa PR e' integrata in `main`, aprire Actions e lanciare `Vidu abbonamento - controllo gratuito CLI ufficiale`.
5. La verifica chiamera' soltanto `vidu-cli quota pass`, `quota credit` e una quotazione prova: NON generera' video.

### Modalita' del piano
La documentazione ufficiale distingue `claw_pass` (quota pass), `nopeak` (fascia oraria agevolata), `normal` (credito incluso/acquistato). Il costo del singolo task e la disponibilita' nel piano sono stabiliti dal server, non deducibili dai circa 10 euro pagati. Nessun passaggio automatico da pass/offpeak a pagamento.

### SCENA A Il ritratto ovale
Autorizzazione precedente: modello **Vidu Q2 Pro Fast**, 5 secondi, massimo **8 crediti**, una sola clip. La versione CLI consumer `3.1` e' definita **Q2**, NON e' verificata come equivalente al modello API `viduq2-pro-fast`. La prova gratuita nel workflow usa un preventivo sperimentale, NON e' un'autorizzazione a cambiare il modello.
Fotogramma originale `SCENA_07.jpg`: 720x1280, ma mano e candelabro sono troppo vicini al bordo per garantire il gesto senza artefatti; serve QA editoriale sul primo frame.
Non lanciare `task submit` prima del controllo del costo esatto, modello, prompt, immagine e approvazione del fingerprint previsto in V41/V42. Nessun retry automatico.

### Architettura per vera autonomia (prossima fase)
1. Il progetto produce storia, Gacrux, scene e foto autentiche con hash.
2. Il sistema prepara e valida gratuitamente ogni asset, confronta i prompt, verifica in modo gratuito la quota del tuo piano.
3. L'utente autorizza la singola spesa per immagine+prompt+modello+durata+limite, con codice del piano.
4. Soltanto un unico `vidu-cli task submit` per piano approvato; recuperare task ID e aspettare senza nuova generazione.
5. Scaricare MP4 originale del provider e verificare gesto, mani/volti, timing e raccordi nel video completo (gate V44).
6. Master in `rendered_needs_review` fino a revisione umana legata al SHA. Non importare sul sito tra i pubblicabili e non pubblicare sui social autonomamente.

### Alternative
- **Vidu Agent** incluso nella piattaforma: crea storyboard e brevi video multiscena; disponibilita'/prezzi del piano da verificare direttamente nell'account: https://www.vidu.com/project
- **Browser Use**: https://github.com/browser-use/browser-use e **Playwright MCP**: https://github.com/microsoft/playwright-mcp; pilotano browser autenticati ma richiedono macchina/browser cloud e possono avere costi aggiuntivi. Evitare automazioni non autorizzate che eludono limiti di Vidu.
- **ChatGPT Work**: puo' navigare siti con browser proprio in una sessione autorizzata, ma non equivale a un plugin Vidu con crediti trasferiti.
- **GitHub Actions senza token**: non ha accesso ai cookie del browser Android. Non basta l'abbonamento per eseguire job GitHub.

**Sicurezza:** VIDU_TOKEN solo come secret GitHub; niente cookie in repository, login incollati nel codice o prompt. Workflow V1 e' volutamente read-only e non esegue submit. Nessun pagamento o tentativo commerciale e' autorizzato implicitamente.
