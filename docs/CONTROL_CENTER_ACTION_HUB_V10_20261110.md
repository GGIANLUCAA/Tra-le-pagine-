# Centro di controllo V10 — Produci / Recupera / Migliora · Ripara GPT mobile

**Data:** 10 novembre 2026. **Decisione:** l'utente vuole intervenire da Android con meno passaggi e istruzioni puntuali. Questa modifica è solo anteprima separata; il sito Video Library Studio live e le automazioni owner non cambiano.

## Esperienza principale
1. Apri «Ripara GPT»: in alto vedi tre programmi (ArtVision, La Storia Rivive e WOW LAB) con lo stato dell'ultima attività GitHub osservabile e il pulsante **Richiedi produzione ora**. **Non è un comando di avvio diretto**: prepara un prompt per GPT. GPT può tentare avvio soltanto se ha strumenti, permessi, budget autorizzato e dopo avere accertato che non esista una lavorazione parallela. Il pannello pubblico resta in sola lettura.
2. Sotto, «Ogni quadro, ogni video» mostra tutte le quattro varianti ArtVision per opera, con la distinzione tra **guardabile**, **catalogato offline**, **scheda già prodotta senza file accessibile**, **variante non individuata** o **fonte non disponibile**. Non chiama «mancante» un master esistente ma non visibile, né dichiara Gold la presenza nel sito.
3. Su ciascuna variante premi **Completa**, **Recupera** o **Migliora**. Il dialogo mostra prima cosa fare e un campo facoltativo per il feedback (es. minuto, zoom, voce, fotogramma) e il collegamento semplice **Copia e apri la chat**.
4. Primo utilizzo: nel pannello «Collega la chat giusta» puoi associare una conversazione alla **singola variante**, all'intera **opera**, al **workflow** o al **progetto**. I link vengono validati e salvati soltanto in localStorage del dispositivo; fallback in ordine *variante → opera → workflow → progetto → ChatGPT nuovo*. Non si possono dedurre automaticamente gli URL privati delle conversazioni senza il primo collegamento volontario.
5. Il prompt trasmesso mediante copia negli appunti contiene opera, slot, eventuale MP4, registro, run, presenza nel catalogo, Gold non attestato, problema, osservazione utente e azione desiderata. Ordina di verificare i dati attuali e il QA, evitare duplicati, conservare i master approvati, non pubblicare o consumare nuove risorse senza consenso.
6. I dettagli di GitHub e il messaggio completo sono chiusi in «Mostra diagnosi e prove» per non complicare lo schermo. Rimangono reperibili in qualsiasi momento.

## Cosa non è ancora possibile dichiarare
- Il tasto «Richiedi produzione ora» **non avvia** automaticamente un job GitHub o ChatGPT (nessun endpoint pubblico con permessi di scrittura).
- «Copia e apri la chat» avvia la copia da un tocco e apre un URL approvato, ma Android/browser potrebbero negare gli appunti. In caso di blocco mostra un'alternativa manuale; l'utente deve sempre incollare ed effettivamente inviare il messaggio.
- Il Centro non legge la cronologia delle chat. Le associazioni private non sono trasmesse al worker, a GitHub o a R2; possono non sincronizzarsi fra telefoni.
- Lo stato dei video viene da un **campione GitHub e dal catalogo pubblico**, non da un controllo in tempo reale di tutte le automazioni native, né dalla lettura integrale degli MP4.
- Per vera produzione one-touch da web servirebbe un backend con autenticazione del proprietario, allowlist di workflow, nonce CSRF, protezione duplicati/limiti e conferma. Non esporre workflow_dispatch su endpoint pubblici.
- La corrispondenza del video alla chat esatta richiede una prima associazione esplicita; il fallback di progetto non è una prova di appartenenza.

## Sicurezza e integrazione
- Ramo: `preview/control-center-action-hub-v10-20261110`, PR bozza; nessun deploy automatico.
- File UI: `site/control-center-preview.html`, modulo di supporto `site/control-center-action-hub.fragment.js` (incorporato nello script inline per la build Worker esistente). Worker API immutato.
- Test: `tests/control-center-preview.test.mjs` e `tests/control-center-owner-action-hub.test.mjs`. Workflow `.github/workflows/artvision-control-center-preview-ci.yml` verifica regressioni e compila bundle isolato.
- Prima di integrare, provare su Android reale: apertura chat già associata, permessi clipboard, apertura app ChatGPT, cambio variante, funzionamento pulsanti, leggibilità e stato catalogo.
