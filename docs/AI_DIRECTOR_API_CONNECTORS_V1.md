# AI Director · Fonti gratuite senza chiavi API

**Decisione del proprietario (12/11/2026):** non utilizzare Europeana. 
Il progetto non richiede alcuna chiave Europeana e non effettua richieste all'API.
I client di ricerca esistenti vengono riutilizzati anziche' duplicati.

## Provider reali già implementati e usati

| Categoria scelta su Android | Ordine delle fonti | Credenziali |
| --- | --- | --- |
| historical_video | Library of Congress, Internet Archive, Wikimedia Commons | nessuna |
| historical_photo | Library of Congress, Wikimedia Commons, Wellcome Collection | nessuna |
| art | Art Institute of Chicago, The Met, Cleveland Museum, Wikimedia Commons (riserva) | nessuna |
| general | Library of Congress, Art Institute of Chicago, Wikimedia Commons | nessuna |

Ogni azione manuale cerca su massimo tre archivi (quattro per le opere d'arte), restituisce 1–3 candidati
per provider, evita richieste di massa, non ritenta su errori e conserva
indipendentemente i risultati di altri provider in caso di un guasto.
La API The Met usa già il nuovo endpoint v1.1, non il vecchio v1 deprecato.

**Pertinenza testuale:** il sistema confronta i termini effettivi della ricerca
con titolo, autore e data del record. Per ArtVision il campo facoltativo
`artist` richiede che il nome sia presente nei metadati del creatore,
non soltanto nel titolo. Vengono registrati gli scarti `excluded_by_relevance`.
Un esito positivo dimostra soltanto corrispondenza dei campi: non prova
attribuzione storica, autenticità, provenienza delle immagini o licenza.
Se la ricerca è troppo specifica e non trova nulla, il report deve dire
che mancano candidati; non allargare automaticamente la query a caso.

**Diritti e qualità:** anche se il catalogo riporta pubblico dominio o CC0,
la pubblicabilità in Italia, la fonte originale e la pertinenza visiva
richiedono una verifica sul singolo record. La fonte non viene selezionata,
scaricata, restaurata o pubblicata in automatico. Tutti i risultati sono
bozze di ricerca, NON sono prove di licenza o autenticità.

## Uso dal solo telefono Android

1. Apri GitHub: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/ai-director-external-apis-v1.yml
2. **Run workflow** → scegli una categoria:
   - historical_video per La Storia Rivive e filmati d'epoca;
   - historical_photo per fotografie storiche;
   - art per ArtVision 4x1;
   - general per ricerca mista.
3. Inserisci il soggetto con parole chiave pubbliche, per esempio Venice 1896
   oppure The Goldfinch. Per ArtVision usa anche il nuovo campo **artist = Carel Fabritius**:
   il filtro verifica la corrispondenza dei metadati dell'autore. Un nome
   presente soltanto nel titolo della scheda non vale come prova di attribuzione.
4. Mantieni provider=auto per controllare tre fonti;
   oppure seleziona un solo archivio. La casella execute=true autorizza
   le sole richieste HTTP di ricerca pubblica, senza crediti o API keys.
5. A fine run → Artifacts → AI_DIRECTOR_KEYLESS_SOURCES → estrai lo ZIP
   e apri director/ANDROID_REPORT.html su Android. CANDIDATES.json contiene
   i record e i link alle fonti, DIRECTOR_BRIEF.json il dossier non approvato.

La fase ricerca non chiama modelli linguistici a pagamento, Vidu, TTS o altri
servizi di produzione. Se gli archivi non rispondono, il report documenta
la mancanza di candidati, senza inventare materiale o bloccare la produzione
seriale già attiva. Il workflow resta **manuale** finché la qualità dei
candidati e i tempi non siano valutati su casi reali.

## Architettura

- src/public_archive_sources_v1.py / v2.py:
  adapter delle fonti già presenti, non clonati.
- src/ai_director_keyless_archives_v1.py:
  selezione per formato, ricerca limitata, fallback, deduplicazione,
  normalizzazione dei candidati e bridge verso AI Director.
- src/ai_director_v1.py:
  produce piano/report editoriali e controlli di regia esistenti;
  queste fonti possono entrare in source_notes come **metadata non verificati**.
- .github/workflows/ai-director-external-apis-v1.yml:
  test offline in PR/push e ricerca **solo su Run workflow**.
- tests/test_ai_director_keyless_archives_v1.py:
  test offline con provider simulati e adapter reali senza Internet.
- src/ai_director_external_apis_v1.py:
  mantiene soltanto client sperimentali Gemini Frame/Groq Whisper,
  disabilitati dal gate costo zero; non contiene più client Europeana.

La policy config/ai_director_external_api_v1.json mantiene
default_deny=true, routes=[] e non autorizza inferenze. In particolare,
Groq Whisper ha prezzi pubblicati a consumo: non attivarlo sulla presunta
gratuità della chiave. Cloudflare AI e Gemini Vision richiedono ulteriori
verifiche, senza accesso a credenziali di produzione.

## Riproduzione offline

    python -m unittest discover -s tests -p 'test_ai_director_keyless_archives_v1.py' -v
    python -m unittest discover -s tests -p 'test_ai_director_external_apis_v1.py' -v
    python src/ai_director_keyless_archives_v1.py --category historical_video --query "Venice 1896" --output output/keyless

Il comando senza --execute è dry-run, quindi non effettua chiamate API.
La reale disponibilità delle fonti verrà attestata solo tramite una run
manuale che esegua richieste e restituisca candidati verificabili.

## Documentazione ufficiale delle fonti

- Met: https://metmuseum.github.io/
- Art Institute: https://api.artic.edu/docs/
- Library of Congress: https://www.loc.gov/apis/json-and-yaml/
- Wikimedia API: https://www.mediawiki.org/wiki/Wikimedia_APIs/Access_policy
- Internet Archive: https://archive.org/developers/
- Cleveland: https://openaccess-api.clevelandart.org/
- Wellcome: https://developers.wellcomecollection.org/

Le API ufficiali possono cambiare endpoint e limiti. Nessuna
garanzia di risultati o qualità artistica senza un test live.
