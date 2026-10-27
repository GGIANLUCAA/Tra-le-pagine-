# Regole attive — 25 ottobre 2026 (revisione 3, Audience V32 + Fonti V33)

Questa revisione applica le decisioni di Gianluca sulla regia modulare.
La configurazione consultabile dal programma è `config/editorial_rules.json`.
La revisione sostituisce i vincoli generali incompatibili nelle guide storiche;
non riscrive filmati, materiali o approvazioni già esistenti.

## Quattro ambiti comprensibili

| Ambito | Cosa significa | Esempio |
|---|---|---|
| Sempre | Requisito comune | Fonti reali, Android, consegna scaricabile |
| Per questo format | Identità che va protetta | Critico con voce, Cinema senza voce |
| Per questo video | Scelta motivata | Apertura, durata e musica di questo soggetto |
| Da provare | Esperimento, non ancora approvato | Nuovo mix o nuova chiusura |

Un esempio dell'utente resta uno spunto. L'approvazione di un filmato non significa
che ogni suo dettaglio diventi obbligatorio in tutti i film futuri. Per una nuova
regola riutilizzabile registrare ambito, motivo, riferimento, approvazione e versione.

## Decisioni consolidate

| Prima | Ora |
|---|---|
| Apertura unica o sempre dettaglio → totale | Repertorio di aperture; scelta motivata sul soggetto |
| Quota fissa di scene, effetti, tipi di inquadratura | Nessuna quota estetica: ogni scelta deve avere una funzione |
| 3–8 tecniche sempre | Il mix esplicito può essere più semplice o articolato; nessun riempimento automatico |
| Finestre di durata prese come obbligo | Durata proposta motivata; per narrati revisione sull'audio effettivo |
| Musica obbligatoriamente nuova ogni volta | Riuso consentito quando coerente, senza rotazione meccanica |
| Domanda, CTA o hashtag standard obbligatori | Elementi pertinenti, secondo post e piattaforma |
| Post Facebook sempre italiano | Lingua esplicita per piattaforma; testi Cinema a schermo internazionali |
| Copertina uguale pixel per pixel | Firma invariata, composizione adeguata al soggetto; vecchie cover preservate |
| Più effetti o versione più recente = migliore | Confronto sullo stesso obiettivo e revisione del risultato |
| Audio presente = voce corretta | Verificare parlato, identità vocale e corrispondenza con immagini |
| MP4 generato = finito | Tecnica, revisione artistica e consegna sono verifiche distinte |

Restano i controlli no ghosting, fonti/diritti, voce di riferimento, format,
conservazione degli originali e assenza di pubblicazione implicita.
I limiti tecnici del renderer vanno dichiarati e non confusi con regole artistiche.
Un formato nuovo o una variante con sottotitoli/voce diversa richiede un profilo
compatibile: il percorso attuale mantiene i profili approvati.

## Ricerca pubblico e regia motivata — VINCOLANTE per ArtVision (25/10/2026, V32)

Approvazione esplicita dell'utente: non scegliere un quadro soltanto perché è bello o famoso.
**Prima di ogni nuovo ArtVision Cinema, Critico o Collection**, se il soggetto
è da scegliere confrontare **almeno tre** opere/temi distinti e scegliere in base a una ragione umana di visione: interesse
pubblico verificabile quando disponibile, impatto visivo iniziale, storia vera,
possibilità di regia, originalità del catalogo, riproduzioni e diritti. Ampliamento
facoltativo a 10–20 candidati quando le fonti lo rendono davvero utile, senza
trasformarlo in una quota burocratica.

Se l'utente indica già l'opera, non sostituirla: la ricerca sul suo interesse
resta obbligatoria, ma il confronto con tre altre opere è facoltativo e va
registrato il vincolo esplicito della richiesta.

I segnali di Google Trends, Facebook, Instagram, TikTok, YouTube o altre fonti
si registrano con URL, data, contesto e osservazione, **senza inventare numeri
di visualizzazioni o viralità**. Se un segnale non è accessibile: annotare
`unavailable` e motivo, ragionare qualitativamente e non presentare ipotesi
come dati. Una scelta artistica può privilegiare un'opera meno cercata per
una motivazione documentata.

**La regia nasce dall'opera e dall'interesse umano**, non da 8/10 crop ripetuti:
apertura, dettagli, andamento, musica/voce e finale devono rispondere a una
promessa concreta al pubblico, rispettando stile del format, no ghosting
e controlli 0/1/3/5/7. Dopo una pubblicazione, confrontare solo metriche
realmente accessibili (retention, completamento, durata media, condivisioni).
Nessun KPI inventato, nessun automatismo di approvazione Gold Master.

La guida `docs/ARTVISION_AUDIENCE_RESEARCH_V32.md` specifica la griglia
qualitativa /100 e i campi per `editorial_plan.audience_research`.
Per nuovi progetti ArtVision il preflight V13/V16 blocca il render senza
confronto documentato, scelta e ragione di regia. Altri renderer che non
chiamano quel preflight devono applicare la stessa regola esplicitamente.
Questa è una regola **sempre** per ArtVision, non un esperimento e non
un nuovo preset visivo. Non modifica video/master esistenti.

## Filosofia fonti e API V33 — VINCOLANTE per tutti i nuovi contenuti (25/10/2026)

Approvazione esplicita dell'utente: priorità a sistemi e API gratuiti già disponibili,
senza perdere qualità né cambiare il linguaggio del singolo format.
**Prima recuperare asset approvati; poi scegliere fonti autentiche o archivi quando
servono fatti/opere reali, stock pertinente quando serve ambientazione, illustrazione
originale quando il racconto richiede personaggi o azioni precise**.
La preferenza di provider è guidata da pertinenza narrativa, diritti e autenticità,
non da una classifica rigida o dalla quantità di immagini generate.

**Pixabay** è il nome corretto del servizio. Il segreto già inserito `PIXABAY`
ha priorità nell'adapter; `PIXABAY_API_KEY` è alias facoltativo;
`PRIXIBAY2` non viene utilizzato automaticamente senza verifica.
AI Horde resta sperimentale (chiave principale `AIHORDE_API_KEY`), Google
Gacrux mantiene `GEMINI_API_KEY`, OpenRouter `OPENROUTER2` non autorizza
modelli a pagamento e non è ancora attivo per inferenza.
Secondi account non si usano per aggirare quote; niente API costose automatiche.
Pixabay richiede ricerche reali e cache 24h; il bridge non ha ancora cache
persistente, quindi evitare richieste duplicate e volumi massivi.

Per ogni nuovo progetto V13 annotare in `editorial_plan.media_sourcing` la
sorgente e la decisione **di ogni asset visivo**. Il check V13 blocca mancanza
di verifica di diritti, pertinenza, fonte, esame visivo, oppure l'uso di immagini AI
come quadro autentico/prova di cronaca. Nessun campo tecnico certifica bellezza.
Risultati/diritti/seed/hash sono riusabili solo se registrati; gli asset già approvati
non vengono riscritti. Le 45 API V2 sono un catalogo, non 45 connettori attivi.

Dettagli e differenze tra format: `docs/FILOSOFIA_FONTI_MEDIA_V33.md`.
Le nuove chat indipendenti devono leggere o ricevere le regole esplicitamente:
il repository non può imporle a una chat che non lo consulta.

## Descrizioni social di alta qualita e recuperabili nel sito — VINCOLANTE (26/10/2026)

**Conferma e irrigidimento della V28**, non un nuovo format. Ogni nuovo video ha post **differenziati** per Facebook, Instagram, TikTok e YouTube, con fatti verificati e taglio narrativo scelto sul contenuto (autore, vicenda, interpretazione prudente, contesto storico, museo, personaggi, emozione). Identita editoriale riconoscibile ma apertura, ritmo e prospettiva mai meccanicamente identici.

**Pubblico:** solo contenuto interessante su opera/storia e crediti realmente obbligatori; niente montaggio, zoom, render, script, prompt, metodologia, algoritmi o informazioni che lo spettatore non deve conoscere. **Privato:** regia, ricette, prompt e conti restano nel dossier tecnico.

La consegna include quattro file social curati, **scheda visuale** nello stile editoriale approvato e **scheda testuale** corrispondente. Per i video importati realmente, queste descrizioni devono essere salvate nella scheda del singolo video su Video Library Studio ed esportabili dal telefono. Nessun testo generico generato dalla categoria vale come post pronto. Se il video non e ancora sul sito, dichiararlo e non simulare il salvataggio.

Il sito applica filtri strutturali contro campi vuoti/identici/cliche e dettagli tecnici, ma revisione umana del contenuto e verifica di fonti/diritti restano indispensabili. Vedere `docs/ARTVISION_EDITORIAL_POST_STANDARD_V28.md` e `docs/VIDEO_LIBRARY_DOSSIER_V1.md`.

## Riferimento positivo e originalita narrativa — VINCOLANTE (26/10/2026, V38)

**Feedback approvato:** *La macchina del tempo* di H. G. Wells e stato giudicato un **buon risultato**, piu bello dei video precedenti soprattutto per una maggiore ricchezza/varieta delle immagini; restano migliorie possibili. Registrare questa valutazione come **riferimento qualitativo positivo**, non come `GOLD MASTER`, licenza, promessa di successo o istruzione per copiare il suo montaggio.

**Regola permanente anti-stampino:** ogni storia/opera deve determinare autonomamente durata, quantita di immagini *distinte*, ordine e durata delle scene, ritmo, variazioni di camera, apertura, musica e finale. La copertina mantiene la firma della serie ma il racconto non deve ripetersi meccanicamente. Vietato trarre dalla *Macchina del tempo* una durata standard, 16 illustrazioni obbligatorie, un numero prefissato di effetti o transizioni e un medesimo schema di montaggio.

Prima di acquisire asset, individuare beat narrativi, luoghi, azioni, emozioni e cambi di significato; motivare scelte di durata e mix e allinearle alle parole e all'audio reale. **Più immagini è positivo solo quando aumenta pertinenza e interesse, non se introduce ripetizioni o filler.** Per racconti diversi sono validi anche pochi quadri lunghi o molti cambi, quando servono alla storia.

Documento operativo `docs/FEEDBACK_REGIA_NARRATIVA_V38.md`; configurazione `config/editorial_rules.json > creative_variation, creative_references`. Il controllo strutturale non certifica la bellezza né trasforma automaticamente il filmato in master approvato.

## Consegna file verificabile su Android — regola permanente (27/10/2026)

**Richiesta esplicita dell'utente dopo ripetuti errori "Library file not found":** per ogni nuovo file generato e consegnato in ChatGPT (MP4, immagini, ZIP, PDF, documenti o altri allegati) non basta stampare un link o affermare che il render è riuscito.

1. Verificare nella sessione corrente il **percorso effettivo** del file, che esista, sia non vuoto e del formato richiesto; per MP4 controllare con ffprobe e, quando possibile, la decodifica completa; per ZIP testare CRC e contenuti. Non inventare link sandbox.
2. Consegnare il **file singolo principale con nome breve ASCII**, preferibilmente direttamente in /mnt/data senza sottocartelle. Per video e consegne soggette a errori Android fornire **anche ZIP con soltanto i file finali**, separato dai sorgenti; verificare entrambi. Creare copia leggera H.264/AAC solo se serve, senza sostituire l'originale.
3. Non confondere **file verificato localmente**, **collegamento sandbox accessibile sul telefono**, **Artifact GitHub ancora disponibile** e **asset davvero ospitato su Video Library Studio**: sono verifiche distinte. Non si può certificare dal server che l'app ChatGPT risolverà sempre i link; non promettere che la sola ridenominazione o lo ZIP eliminino un errore della piattaforma.
4. Se il download via ChatGPT fallisce, offrire un secondo percorso realmente esistente (ZIP, Artifact GitHub oppure, previa autorizzazione e verifica del caricamento, URL stabile su Video Library Studio/R2). Non pubblicare file privati su un repository pubblico né creare URL immaginari.
5. Segnalare con precisione l'eventuale limite di accesso e non chiamare "consegnato" un file assente o un link non verificato. La preferenza vale per ogni nuova consegna, non soltanto per i video.

Per gli episodi con audio resta disponibile V36 in docs/VIDEO_DOWNLOAD_V36.md e src/video_download_fallback_v36.py. Per i microclip senza audio usare un confezionamento ZIP equivalente senza alterare il video originale.

## Dal soggetto al risultato

1. Registrare richiesta, format, presenza della voce, lingua e obiettivo. Se si
   migliora un Critico, non convertirlo in Cinema per ottenere un'immagine migliore.
2. Studiare il soggetto: fonti, dettagli, storia, fatti documentati e incertezze.
   Un mistero/furto/ritrovamento è una possibilità narrativa, mai un fatto inventato.
3. Formulare una promessa interessante e indicare dove verrà mantenuta. Primo
   fotogramma, titolo e copertina devono corrispondere al contenuto. I checkpoint
   0/1/3/5/7 servono al controllo e non impongono un'introduzione di sette secondi.
4. Selezionare tecniche dal catalogo esistente. Per ogni scelta indicare motivo e
   stato. `trial` significa prova; `approved_option` richiede approvazione registrata.
   La presenza nel catalogo V23 non equivale all'approvazione di Gianluca.
5. Nei narrati sviluppare copione e scene insieme, poi allineare all'audio reale.
   Ogni dettaglio citato deve apparire quando serve. Trama e spiegazioni devono
   restare complete anche quando si accorcia. Finale pertinente, voce naturale.
6. Stimare durata, musica, copertina e lingue social. Per un mix nuovo provare una
   sequenza rappresentativa prima del lotto, se utile; se la produzione è già
   autorizzata non imporre ulteriori conferme operative.
7. Prima del render eseguire preflight; dopo render controllare il file realmente
   prodotto. Non valutare la durata finale di un Critico su una versione senza voce.
8. Consegnare MP4, copertina, post differenziati, fonti/crediti e dati di replica.\n   V36 download: verificare che il file MP4 esista e sia interamente decodificabile;\n   quando si consegna in ChatGPT fornire anche uno ZIP con SOLO il video,\n   separato dal pacchetto sorgenti. Per errori Android preparare a richiesta un\n   MP4 H.264/AAC leggero. Usare `docs/VIDEO_DOWNLOAD_V36.md` e\n   `src/video_download_fallback_v36.py`. Un controllo locale non garantisce che\n   un link sandbox dell'app ChatGPT sia funzionante; per archivio stabile\n   usare Video Library Studio/R2 solo dopo importazione reale dell'asset.
   Salvare lo stato reale, il percorso verificabile e una versione identificabile.
9. Raccogliere correzioni per video e regole riutilizzabili. Una proposta di regola
   non si autoapprova. Metriche reali, quando disponibili, informano esperimenti;
   nessuna previsione certa di viralità o promozione automatica a master approvato.

## Avvio facile per un video o una serie

- Quando Gianluca chiede di creare un video o più video, avviare il menu breve
  `docs/ISTRUZIONI_MENU_VIDEO_NUOVE_CHAT.md`: singolo/serie, idea o prompt, categoria,
  format e stile. Usare i valori già proposti; mostrare le altre impostazioni solo
  se desidera cambiarle.
- Se la richiesta contiene già queste informazioni, precompilare il menu e chiedere
  soltanto le decisioni essenziali mancanti. La frase “usa le impostazioni consigliate
  e procedi” significa che può iniziare il lavoro senza ripetere l'intero riepilogo.
- Per una serie proporre un elenco degli episodi con identità condivisa e regie
  variate. Una correzione del singolo episodio non modifica le impostazioni globali.
- Nel sito il pulsante “Prepara e copia il brief per GPT” prepara testo da incollare
  in una chat. Salvare impostazioni nel browser non equivale a salvarle nel sito o
  in un repository; usare la copia del brief per trasferirle tra dispositivi.
- Queste istruzioni valgono nelle chat che leggono questo repository o il prompt
  dedicato. Una chat nuova e indipendente non può leggere il repository da sola:
  per applicare il comportamento ovunque, inserire il testo del file dedicato nelle
  istruzioni del progetto ChatGPT o nelle istruzioni personalizzate.

## Collegamento effettivo al codice

`video_director_v13.py brief` crea `PROJECT_V13.json` con:
- `editorial_contract`: formato richiesto, presenza della voce, lingua, versione e
  hash delle regole. Un cambio di format richiede un'istruzione dell'utente registrata
  in `format_change_authorization` con `from`, `to`, `approved_by: "user"`, `instruction`.
- `editorial_plan`: ricerca, promessa, conclusione, copertina, durata motivata,
  mix e lingue social. Ogni fonte richiede reference, finding, verification_notes
  e status `reviewed`, da compilare solo dopo controllo reale.

`check` esegue `src/editorial_rules.py` prima della produzione. V15 usa già questo
check; l'adapter V16 lo ripete anche se chiamato direttamente. V23 rispetta il mix
esplicito senza aggiungere altre tecniche. L'adapter Van Gogh accetta la durata
proposta arrotondata al secondo superiore, con limite tecnico minimo di 4 secondi;
la sua regia storica resta specifica di Van Gogh, non un motore universale.
V25 non impone più otto scene, tre tipi di inquadratura o 3–8 tecniche. Restano
obbligatori soggetti, ragioni, fonti, tempi, cue reali e controlli di consegna.

Le schede storiche senza contratto restano leggibili con un avviso: non sono
automaticamente migrate o certificate dalle nuove regole. Prima di riutilizzarle
per nuovi lotti, creare una nuova scheda e trasferire i materiali validi.
Gli script speciali che bypassano V13/V16 richiedono ancora l'applicazione esplicita
del playbook: questo intervento non dimostra che tutti i renderer siano integrati.

## Riferimenti tecnici da conservare

- Formati e capacità: `config/video_formats_v13.json`, `docs/GPT_VIDEO_PLAYBOOK.md`.
- Cinema: preset V6 e identità visiva approvati; Critico: guida serie V2.
- Tecniche: `config/cinematic_techniques_v23.json`; approvazioni in `editorial_rules.json`.
- Voce: WAV, profilo, cache e allineamento originali con hash coerenti.
- Musica e diritti: V20; controllo scene opache: no-ghosting V1.
- Testi social: V28; fascicolo: `docs/VIDEO_LIBRARY_DOSSIER_V1.md`.
- Produzione e ripresa: V15/V16; qualità: V17; apprendimento: V14/V18.

## Limiti dichiarati

La validazione controlla dati e coerenza delle dichiarazioni. Non vede la bellezza,
non prova che una fonte sia vera e non ascolta il parlato al posto della revisione.
Il menu nell'interfaccia richiede la distribuzione del repository per comparire sul
sito live; le istruzioni non attivano pianificazioni, servizi a pagamento o
pubblicazioni social.
Le nuove regole sono applicabili alle nuove chat solo se il progetto viene letto.
