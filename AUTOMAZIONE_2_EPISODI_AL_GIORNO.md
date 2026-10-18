# TRA LE PAGINE — DUE EPISODI AL GIORNO (guida Android)

Aggiornato il 18 ottobre 2026.

## Stato del sistema

- Due appuntamenti ChatGPT attivi ogni giorno: orientativamente **9:00 e 18:00** (orario italiano).
- Ogni appuntamento prepara una nuova proposta editoriale con libro, copione, storyboard e anteprima; non ripete il titolo della precedente.
- Gemini TTS, sottotitoli e montaggio FFmpeg sono già stati usati con successo per gli episodi 01 e 02.
- Nuovo workflow generico: .github/workflows/render-v3.yml. Permette di scegliere la cartella del libro anziché usare sempre l'episodio 01.
- Sicurezza: in mancanza dell'OK esplicito l'invio alla coda non produce nulla; se mancano le illustrazioni definitive il workflow si blocca PRIMA di usare crediti o quote Gemini.
- Copertina coordinata prodotta dal codice V3 in 1080x1920; il filmato attuale rimane 720x1280 finché non testiamo un upgrade.

**Limite reale:** al momento sono automatiche due ANTEPRIME, non due MP4 completi ogni giorno. Le illustrazioni originali non possono essere prodotte in massa dalla sola API ChatGPT Plus, e Google non offre un piano immagini gratuito comparabile alla voce.

## Primo collaudo V3 effettuato senza spese (18 ottobre 2026)

Il nuovo generatore è stato **testato con risorse storiche**, senza chiamare Gemini e senza produrre nuove immagini.

- [Test di validazione V3 riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39140109824): controlla lo storyboard premium dell'episodio 01, blocca l'episodio 02 che non ha ancora immagini premium nel repository e verifica il motore della copertina.
- [Test di sicurezza della coda riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39140196236): una richiesta non approvata non produce MP4 e non chiama servizi esterni.
- [Collaudo offline del video già esistente riuscito](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39142063491): recupera il MP4 dell'episodio 01 da un precedente artifact, legge audio e video con ffprobe, crea una **nuova copertina coordinata 1080×1920** partendo dalla scena 01 senza scritte, e produce `CONTROLLO_QUALITA.txt`. Dopo una prima prova è stato risolto un errore di titoli sovrapposti.
- La **produzione completamente nuova**, da copione a Gemini a MP4 attraverso il workflow `render-v3.yml`, deve ancora ricevere il primo test con un nuovo episodio approvato e immagini definitive. Non si afferma il contrario.

**Da Android, per vedere il test senza generare nulla:** apri il collaudo offline riuscito → scorri a **Artifacts** → scarica `COLLAUDO_V3_EP01_SENZA_API` → estrai e osserva `COPERTINA_SERIE.jpg` e `CONTROLLO_QUALITA.txt`. È un test del motore, non un nuovo episodio.

**Per provare poi un nuovo episodio reale:** attendi la proposta delle 9:00 oppure delle 18:00, leggi copione e storyboard, correggi o dai OK. Dopo che le illustrazioni verticali definitive sono state generate e caricate, possiamo avviare `render-v3.yml` indicando il nome esatto della cartella dell'episodio. Il sistema blocca il render se manca un'immagine.

**Importante:** l'OK per il montaggio non autorizza alcuna pubblicazione su Facebook, Instagram o YouTube. Pubblicazione e pagamento di servizi API rimangono separati.

## Come usarlo senza pagare altri abbonamenti

1. Ogni mattina ricevi un libro e la sua bozza editoriale.
2. Ogni sera ricevi un altro titolo, con genere diverso quando possibile.
3. Leggi il copione, controlla le immagini campione, correggi o dai OK.
4. Dopo OK ChatGPT completa gli asset e li salva in una cartella separata, se gli strumenti/quote disponibili permettono la generazione.
5. Seleziona e avvia il nuovo episodio con il workflow V3 (oppure chiedi a ChatGPT di aggiornarne la coda dopo il tuo OK).
6. GitHub controlla gli asset, chiama Gemini, monta MP4, sincronizza sottotitoli e crea la copertina coordinata. Solo dopo controlli consegna il download. Non pubblica sui social.

[Apri il workflow multiprogetto V3](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/render-v3.yml)

Puoi avviarlo da Android con **Run workflow** inserendo, come episodio, il nome della cartella, ad esempio 01_scacchi. La cartella deve contenere:
- testo.txt e metadata.json
- scene_cues.json
- DESCRIZIONE_SOCIAL.txt
- scene_premium.zip con scene individuali scena_01.jpg, scena_02.jpg ecc.

L'invio dalla chat utilizza la coda queue/render_request.json, disabilitata finché non è approvata. Questo impedisce render che consumano risorse inutilmente.

## Seconda fase: due MP4 COMPLETI senza intervento

Per produrre due video giornalieri senza nessuna approvazione intermedia serve anche un generatore automatico delle immagini 9:16.

Al listino Google verificato nell'ottobre 2026, Gemini 3.1 Flash Lite Image prevede **circa $0.0336 per immagine 1K standard** e **$0.0168 in batch**; la fascia gratuita per la generazione immagini di questo modello non è disponibile.

Stima orientativa:
- 12 immagini: ~$0.40 per episodio standard;
- 18 immagini: ~$0.60 per episodio standard;
- 2 episodi/giorno: 24–36 immagini, ~$0.81–$1.21/giorno;
- 60 episodi/mese: **$24–$36 solo immagini**, senza rigenerazioni, eventuali altri servizi, tasse e fluttuazioni di prezzo.

La modalità batch può ridurre il costo delle immagini, ma non è immediata e richiede un flusso da configurare. Nessun importo è stato addebitato per questa configurazione.

**Non attiviamo fatturazione senza tuo consenso e budget**. Un limite applicativo può fissare il numero massimo di immagini/riprova per episodio, ma i budget del provider potrebbero essere solo avvisi e non impedire ogni possibile addebito.

Prima dell'automazione completamente autonoma servono due scelte dell'utente:
1. Vuoi mantenere l'approvazione delle anteprime o autorizzare l'esportazione MP4 senza attendere il tuo OK?
2. Accetteresti un piccolo budget per generare immagini automaticamente tramite API, e qual è il massimo al giorno?

Confermate queste scelte, il passo tecnico è collegare il modello immagini alla pipeline, testare un episodio completo e poi attivare la cadenza di due video al giorno.

## Sicurezza editoriale

- Una sintesi non verificata non viene presentata come fedele al romanzo.
- Mai scene geometriche/placeholder, collage tagliati, testo inventato.
- Mai copiare copertine editoriali o altri materiali protetti senza autorizzazione.
- Non inserire dati personali o API key nel repository pubblico.
- Nessuna pubblicazione social automatica: produrre video e pubblicarli sono due permessi diversi.

## Documenti

- [Metodo editoriale V3](METODOLOGIA_TRA_LE_PAGINE_V3.md)
- [Scheda nuovo episodio](TEMPLATE_EPISODIO_V3.md)
- [Workflow di produzione V3](.github/workflows/render-v3.yml)
- [Validatore e copertina](src/episode_v3.py)
