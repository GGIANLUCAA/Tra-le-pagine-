# ARTVISION V31 — PRODUZIONE AUTONOMA OGNI TRE ORE
**24 ottobre 2026 · contratto operativo per nuove produzioni, ADDITIVO.**

Questo documento è la riscrittura operativa della richiesta di produrre **un video artistico originale ogni tre ore**, con un mix reale di Cinema senza voce, Critico d'arte narrato e raccolte tematiche di più dipinti. **Non sostituisce** le regole o i master preesistenti. Si applica a ogni esecuzione programmata della routine "ArtVision — Video ogni 3 ore".

## 0. La gerarchia esistente non cambia
Consultare, all'inizio di OGNI ciclo, prima di progettare o scegliere l'opera:
1. `AGENTS.md` (preferenze più recenti e accesso agli strumenti)
2. `docs/ARTVISION_CONTRATTO_PERMANENTE_V25.md`: invariabilità Cinema V6, rapporti audiovisivi, diritti, foto reali, MP4 e pacchetto verificato
3. `docs/ARTVISION_EDITORIAL_POST_STANDARD_V28.md`: post umani, documentati, distinti, senza linguaggio tecnico
4. `docs/REGIA_CINEMATOGRAFICA_V23.md` + `config/cinematic_techniques_v23.json`
5. `docs/CREATIVE_DIRECTOR_V21_STANDARD.md`, `docs/MUSIC_POLICY_V20.md`, prescrizioni QA V17/V19, stati V16/V13
6. Preset approvato *del formato concreto*: Cinema V6 `modules/artvision/APPROVED_PRESET.json`, `modules/artvision/IDENTITA_VISIVA_FISSA_V6.json`; Critico V2 `modules/artvision_critico/production_series/README_SERIE_QUATTRO_V2.md` e guida narrativa senza marchi. Confrontare sempre con un riferimento davvero approvato.

Le istruzioni più recenti dell'utente per una specifica opera prevalgono su questo documento. **Non sostituire** un Gold Master con un esperimento.

## 1. Cadenza e selezione: uno ogni 3 ore
La routine si esegue ogni 3 ore (circa **8 sessioni/giorno**), non solo un promemoria. Ogni iterazione è un tentativo completo: ricerca → scrittura → regia → rendering → controllo → consegna reale. Non avviare cicli duplicati per la medesima fascia oraria. Se il lavoro precedente è ancora attivo, recuperarne stato e artefatti prima di produrre un doppione.

Consultare ultime produzioni e registro `queue/artvision_autoproduction_v31_state.json` (se presente e aggiornato), GitHub Actions, Libreria ChatGPT e videoteca solo con i loro strumenti autorizzati. Dati non visibili = sconosciuti, non presumere che il film esista. Preferire una **tipologia diversa dalle ultime due**, senza rigidità che peggiori l'opera.

### Tre tipologie da alternare nel tempo
**A — ArtVision Cinema** (`artvision_cinema`): nessuna voce, soli dipinti autentici, musica strumentale licenziata, fotografia/regia poetica, originale Cinema V6 immutabile. Per un artista solo oppure una sola opera, nessun pretesto per fare 13 croppini uguali.

**B — ArtVision Critico** (`artvision_critico`): narrazione **in italiano**, unica voce approvata Google Gacrux, ritmo comprensibile e umano; fatti museali verificati, interpretazioni distinte da fatti, dettagli sincronizzati con l'effettivo parlato WAV, minima camera unidirezionale stabile. Copertina serie Critico V2 (non copertina V6). Il renderer V2 esistente NON è universale: preparare config, asset e WAV pertinenti. Se il TTS naturale non è disponibile/consentito, **non** fingere un narrato e non usare un fallback robotico; segnalare il limite, conservare la bozza, scegliere eventualmente un episodio A/C completo, e tentare nuovamente B al prossimo ciclo idoneo.

**C — ArtVision Collection** (VARIANTE editoriale di `artvision_cinema`, non inventare adapter `artvision_collection` inesistente): 2–6 capolavori con un collegamento reale e non generico (tema, luce, paura, bellezza, due artisti in dialogo). Senza voce per impostazione iniziale, salvo che un format narrato approvato sia disponibile. Ogni opera va identificata e accreditata; regia con arco complessivo autentico, non carrellata casuale di immagini. Copertina in famiglia Cinema V6 adattata al tema, senza sovrascrivere la baseline né usare titoli lunghi in lingua obbligata.

Almeno un episodio di ciascuna tipologia nelle 3–5 consegne riuscite consecutive quando le risorse realmente disponibili lo consentono. Variare intensità: mistero, luce, poesia, grandi paesaggi, visioni surreali, simboli, episodi storici. Non fare solo quadri macabri per attirare clic.

## 2. Scelta soggetto ragionata
> **Aggiornamento approvato 25/10/2026 (V32):** questa sezione va letta
> insieme alla regola permanente `docs/ARTVISION_AUDIENCE_RESEARCH_V32.md`
> e alla fonte unica `docs/REGOLE_ATTIVE.md`. Il confronto fra >=3 candidati
> deve contenere prove di interesse pubblico quando accessibili o motivare
> espressamente la loro indisponibilità; la regia deve dipendere dall'opera.
> Conservare il risultato in `editorial_plan.audience_research` e nel
> `AUDIENCE_RESEARCH_V32.json` dell'episodio. Non inventare metriche.
> Le regole attive V32 prevalgono sulle raccomandazioni storiche di V31.


Valutare **almeno tre candidati** prima della decisione, considerando:
- forza del primo fotogramma e leggibilità in autoplay;
- bellezza o originalità visiva/forza delle emozioni; unicità nell'archivio;
- storia vera, simboli o contesto museale documentabile;
- riproduzione abbastanza nitida per il formato (no immagini rimpicciolite/upscale presentato come 4K);
- licenza dell'immagine e della **registrazione** musicale con usi social documentati;
- capacità di realizzare un arco con progressione e finale vero.

Non inventare informazioni, percentuali di viralità, KPI, classifiche o numeri. L'obiettivo è il **potenziale interesse umano**, che verrà confermato solo dalle metriche reali una volta pubblicato.

## 3. Regia: bellissimo, non artificiale
Per ogni video elaborare **0/1/3/5/7 secondi** usando fotogrammi REALI verificabili. Apertura subito forte senza banda testuale ingombrante sul soggetto. Camera per lo più stabile e, se necessario, un solo gesto unidirezionale, senza pan a pendolo, zoom perpetuo, vibrazione, split-screen o transizioni casuali.

Scegliere 3–8 tecniche V23 motivate **dal quadro**. Inquadrature artistiche, rapporti pittorici fra macro, dettaglio e composizione, variazione dell'intensità, pause; movimento e suono coordinati su eventi reali della traccia o della voce, non tempi inventati. Ogni cambio deve aggiungere qualcosa allo spettatore. Primo frame, tre raccordi centrali, chiusura e copertina devono essere riesaminati a velocità reale; controllare volti, coltelli, mani, proporzioni, colori e leggibilità.

**Durata aggiornata su richiesta utente 24/10/2026:** normalmente **45–120 secondi** per A/B/C, senza imporre timer identici; scegliere quando è meglio finire. Critico può andare oltre i 120 secondi per complessità autentica, purché voce, dettagli e finali rimangano interessanti e nessuna parte sia riempitivo. La vecchia finestra Cinema 45–75s è una preferenza, NON un limite vincolante. Un solo master finale per opera/brief.

## 4. Identità e voce
- Copertine coerenti e stabili per ciascuna serie; Cinema V6: firma artista + riga piccola MUSIC BY, stessi font/colori/banda/fade, titolo EN dell'opera solo ove previsto dal preset cover. Non cambiare le copertine già esistenti.
- Critico V2: titolo dell'opera grande in inglese, artista, grafica V2; niente scritte italiane nel video. Voce Gacrux naturale, nessuna alternanza robotica, ducking musicale, frase finale elegante senza domanda forzata, nessun sottotitolo inciso.
- Collection: grafica coerente con il format scelto; indicare correttamente ogni artista/opera nei metadati e crediti. Se compare testo nel film, non introdurre vincoli di lingua per il pubblico internazionale.
- Nessun logo o call-to-action invasiva, nessuna voce nei video Cinema o Collection senza voce.

## 5. Scrittura social V28, OBBLIGATORIA a ogni sessione
Preparare `POST_FACEBOOK.txt`, `POST_INSTAGRAM.txt`, `POST_TIKTOK.txt`, `POST_YOUTUBE.txt`, `POST_EDITORIAL_RESEARCH.json`. Ricerca in museo, archivio, istituzione ufficiale e ricontrollo delle frasi storiche. **Il post parla dell'opera e aggiunge un fatto, una storia o un significato**; non dice come sono stati fatti video, zoom o montaggio. Umano, semplice, colto ma comprensibile, senza cliché, senza domande stereotipate, senza engagement bait. Facebook normalmente circa 65–120 parole per il nucleo narrativo, ma durata e testo si adattano. Solo 2–4 hashtag pertinenti, titoli e crediti precisi, fonti e licenze CC obbligatorie nel piè di testo. Testi realmente diversi a seconda della piattaforma.

## 6. Pacchetto di consegna = prova concreta
Conservare per ogni nuovo episodio, con ID univoco e senza sovrascrivere:
- `VIDEO_MASTER.mp4` reale, 9:16 preferibilmente 1080×1920 H264/AAC (non chiamarlo 4K se non è 4K);
- `COPERTINA.jpg`, preview e campioni reali primi 0,1,3,5,7s + raccordi e finale;
- quattro POST, `POST_EDITORIAL_RESEARCH.json`, fonti e licenze;
- `VIDEO_RECIPE_V13.json`, `TECNICHE_REGIA.md`, `ISTRUZIONI_REPLICA.md`, `SOURCES_AND_RIGHTS.md`, `MUSIC_RELEASE_V20.json`;
- per Critico, copione IT, WAV/voce verificata, cue reali e regia sincronizzata;
- `ARTVISION_CONTRACT_V25.json` o altri manifest del format; report QA con hash di ogni file, durata **misurata**, codec, quantità di scene e risultato reale;
- ZIP completo con MP4 e materiale per smartphone, scaricabile con link verificato e, se già autorizzato e funziona, catalogazione non distruttiva nella videoteca dell'utente.

**Validazione:** ffprobe di video/audio, decodifica completa ffmpeg, copertina, ascolto voce e mix, integrità zip, fonti e permessi; il QA tecnico NON dimostra il valore artistico. Non qualificare Gold Master senza feedback positivo. Non riferire un indice aggiornato o uno script pronto come se fosse un video consegnato.

Se un asset necessario manca o i limiti gratuiti vengono superati, tentare prima un recupero compatibile con la qualità; se impossibile, registrare il motivo esatto e comunicarlo (non inventare file/link). Non avviare servizi a pagamento o rilasciare token GitHub al codice. **Nessuna pubblicazione automatica su Facebook/Instagram/TikTok/YouTube**: le descrizioni sono pronte per il futuro.

## 7. Stato del ciclo, deduplica e retroazione
Il registro `queue/artvision_autoproduction_v31_state.json` conserva slot temporali, categorie recenti, opere, codec/link solo verificati, esito, errori, asset/fonti, note d'impatto e feedback dell'utente. Aggiornare senza cancellare o duplicare ID preesistenti; non inventare successi. Se una pubblicazione fallisce, lasciare master o bozza recuperabili senza perdere tempo e crediti. Non oltrepassare il buffer di revisioni indicato da V16.

Ogni 3 ore tentare un contenuto nuovo con variabilità e lo standard più recente, riusando ciò che funziona. Riportare all'utente **soltanto consegne reali e/o errori utili**, mai stati immaginari.

## 8. Prima esecuzione
Gli ultimi due filmati della conversazione sono Cinema (Goya Saturn, Holbein The Ambassadors). **Preferire Critico** come prossimo format quando sono disponibili fonte, narratore naturale e renderer; altrimenti Collection di qualità con cause del fallback annotate. Proseguire poi con scelta equilibrata dei tre formati.

_Questa policy è il prompt permanente di produzione; la pianificazione effettiva ogni 3 ore è gestita dalla routine programmata ChatGPT, non da un secondo cron GitHub in conflitto._
