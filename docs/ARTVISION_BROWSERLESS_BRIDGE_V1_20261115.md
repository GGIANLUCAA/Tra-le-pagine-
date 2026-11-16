# ArtVision Browser · Cloud Bridge V1 (prototipo senza PC)

**Stato:** PR di prova, isolata e non attiva su main. Non modifica video, render, sito, crediti Vidu, voce Gacrux o altre automazioni.

## Perche' esiste
ChatGPT puo' creare un nuovo file requests/browserless/<id>.json usando il connettore GitHub esistente. Dopo l'eventuale merge del workflow su main, GitHub Actions (cloud) controlla che sia una richiesta nuova, esegue test di sicurezza offline, poi invia **una sola chiamata** a Browserless tramite /function documentato. Nessun PC o terminale locale.

**Questa V1 NON e' ancora un agente tipo TinyFish completo:** e' una prova controllata per aprire e leggere una pagina pubblica, seguire fino a quattro link pubblici o digitare testo **non riservato**. Il servizio Browserless rimane a quote gratuite limitate. I dati personali di TRAE non vanno mai nei file o log pubblici di questo repository.

## Installazione Android — richiede azione proprietario
1. Browserless: registrazione gia' completata; apri il pannello API keys sul sito e conserva la chiave solo la'.
2. GitHub Android/web: https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions → **New repository secret** → Name: BROWSERLESS_TOKEN, Secret: incolla la chiave Browserless → **Add secret**. NON incollare il token in ChatGPT, nel codice, nelle Issue, nelle richieste o nelle descrizioni PR.
3. Esaminare e approvare la PR di questo modulo; merge **solo su approvazione proprietario**. Finche' la PR e' draft, nessun uso della API.
4. Primo incarico (dopo merge + secret): tramite ChatGPT/GitHub crea un file nuovo requests/browserless/artvision-demo-001.json con contenuto:

    {
      "version": 1,
      "request_id": "artvision-demo-001",
      "url": "https://example.com/",
      "actions": []
    }

5. Dopo il push su main, apri GitHub → Actions → ArtVision Browser · Browserless cloud bridge V1 → ultimo run. Verifica status=verified_public_page con titolo Example Domain. Non dichiariamo riuscito fino alla prova sul provider.

## Sicurezza (V1)
- **Solo** https://example.com/ e https://docs.browserless.io/ o loro percorsi privi di query/fragment, login, credenziali, porte alternative.
- Il browser usa un contesto fresco a ogni richiesta; niente login o cookie TRAE.
- Fino a quattro azioni, click soltanto su link pubblici dei due host approvati; type_public su elementi indicati con selettore CSS, mai dati personali.
- Niente JavaScript arbitrario, POST da input, acquisti, pubblicazione, upload, invio di password/codici, scraping di dati privati.
- Il workflow PR esegue solo test offline senza segreto. Il token e' letto esclusivamente da secrets.BROWSERLESS_TOKEN, e l'output non lo registra.
- Su errori, assenza del secret o richieste non conformi: blocca; non ritentare la chiamata automaticamente.
- I log di Actions nel repository pubblico possono essere leggibili: **non impiegare questo ponte per sessioni autenticate**. Per lavorare su TRAE autenticato servira' un backend privato e un meccanismo sicuro di accesso/risultati, da verificare separatamente.

## Campi facoltativi del comando
actions puo' contenere al massimo quattro oggetti:
- {"type":"click","selector":"a[href]"}
- {"type":"type_public","selector":"input.search","text":"museum"}

Non e' un linguaggio di programmazione pubblico. Al primo test mantieni actions: [].

## Documentazione ufficiale
- API /function di Browserless: https://docs.browserless.io/rest-apis/function
- Browserless Free: https://cloud.browserless.io/pricing (1.000 unita' al mese, 2 minuti per sessione, salvo cambi del piano).
- GitHub Secrets: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- Plugin privato Browserless creato in ChatGPT: https://chatgpt.com/plugins/plugins_6af9ea66c1248191a5c962e0b5df1058 . E' distinto da questo ponte e potrebbe richiedere permessi che il piano personale non possiede.

## QA
python -m unittest discover -s tests -p 'test_browserless_bridge_v1.py' -v
Tutti i test offline devono passare prima del merge. Un PASS del test non attesta ancora una richiesta reale al browser.
