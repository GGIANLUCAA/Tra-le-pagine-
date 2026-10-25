# Studio video di Gianluca — istruzioni attive

Leggere questo file prima di proporre o produrre video. Il repository principale è
`GGIANLUCAA/Tra-le-pagine-`. Lavorare dal sistema esistente e preservare i master
approvati. Le istruzioni esplicite della sessione hanno precedenza.

## Punto di riferimento unico (revisione approvata 25/10/2026)

Leggere **docs/REGOLE_ATTIVE.md** e **config/editorial_rules.json**, poi il profilo
in `config/video_formats_v13.json`. Ordine: richiesta esplicita → regole attive →
profilo del format → scelte del video → guide storiche. Le vecchie istruzioni
integrali sono in `docs/history/AGENTS_before_2026-10-25.md` solo come storico.
Le guide V12–V31 restano istruzioni dei moduli: in caso di conflitto prevale la
revisione attiva. Non aggiungere in cima altri blocchi «regola più recente»:
aggiornare la fonte unica con versione, motivo e riferimento dell'approvazione.

## Prima di produrre

1. Identificare l'intento: `libri`, `artvision_cinema`, `artvision_critico`,
   `controluce`, `visual_music`, `hyperlumen`. Per un format nuovo verificare prima
   sorgenti/capacità e creare il profilo; non riciclarne uno cambiando l'etichetta.
2. Un Critico resta narrato. Non togliere voce per compensare crediti o problemi
   tecnici; non considerare una traccia AAC prova che contenga il parlato.
3. Recuperare ricetta, materiali e correzioni dei riferimenti. Non inferire con
   certezza voce, font o motore dal solo MP4. Riutilizzare il lavoro valido.
4. Preparare `brief` con `src/video_director_v13.py`: nuove schede contengono
   `editorial_contract` (richiesta e versione regole) ed `editorial_plan` (ricerca,
   promessa, apertura, conclusione, copertina, durata motivata, mix, lingue social).
5. Compilare fonti e note di verifica reali; esempi dell'utente non sono regole.
   Catalogo tecniche esistente: `config/cinematic_techniques_v23.json`. Una voce
   nel catalogo è disponibile, non necessariamente approvata dall'utente.
6. Eseguire `check` prima del render. Le vecchie schede senza contratto sono
   segnalate come storiche: migrare esplicitamente per nuovi lotti. Non inventare
   approvazioni o riscrivere la richiesta originaria per far passare un controllo.

## Ricerca del pubblico prima del video (regola approvata 25/10/2026)

Per ogni **nuovo** ArtVision Cinema, Critico o Collection leggere e applicare
`docs/ARTVISION_AUDIENCE_RESEARCH_V32.md` e la regola in `docs/REGOLE_ATTIVE.md`.
Se il soggetto è libero, confrontare >=3 candidati con interesse umano,
possibili segnali pubblici documentati (o indisponibilità dichiarata), storia
museale, qualità/diritti, originalità e regia prevista. Conservare il confronto
in `editorial_plan.audience_research` e nei materiali dell'episodio; eseguire
il gate preflight V13/V16 quando presente. **Non fabbricare statistiche**.
Se l'utente ha già scelto l'opera, analizzarne comunque il pubblico senza imporre altre opere.
La regia dev'essere specifica del soggetto, non uno stampino.
Questo non cambia i formati approvati né i master storici.

## Firma e regia

- Cinema: baseline V6, opere autentiche, senza voce; identità di serie, nome artista
  e credito MUSIC BY; testi previsti in inglese. Copertina dedicata al soggetto.
- Critico: copertina serie V2, voce Google Gacrux, dettagli coordinati alle parole,
  camera ferma alternata a movimenti motivati e molto lenti. Niente oscillazioni,
  pendoli, avanti-indietro o domande finali fuori contesto. Concludere il pensiero.
- Libri: protagonista, situazione, fatti, scelte e conseguenze; immagini coerenti
  con personaggi e frasi, riflessione finale pertinente. Voce naturale Gacrux.
- Controluce: una storia, fonti e attribuzioni verificabili; ricostruzioni
  riconoscibili come tali. Non presentare immagini illustrative come documenti.
- Visual Music/HyperLumen: note/eventi reali e sincronia documentata, forme leggibili,
  niente numerazioni decorative o sovrapposizioni confuse. Recuperare i generatori
  se il registro li indica ancora mancanti; non dichiararli installati.
- Sottotitoli disattivati nei profili correnti. Una variante va autorizzata e
  supportata dal motore; non applicare la preferenza indistintamente ai format futuri.
- Firma di serie coerente, composizione adattabile. Preservare i file storici.
- Durata, scene, effetti, ordine dettaglio/totale e numero di tecniche si motivano
  sul soggetto. Nessuna quota globale, apertura unica o domanda finale obbligatoria.
- Le scelte esplicite del mix in `editorial_plan.techniques` prevalgono sui
  suggerimenti automatici V23. Il planner non esegue automaticamente gli effetti.

## No ghosting e apertura museo

Per i video d'arte: un quadro nitido e opaco alla volta. Vietate dissolvenze
incrociate, doppie esposizioni e blend tra scene (`xfade`, `Image.blend`,
`cv2.addWeighted` tra quadri). Tagli puliti, match geometrico senza sovrapposizione,
eventuale passaggio separato al nero. La grafica di identità non è un secondo quadro.

L'ingresso POV museo → quadro è un'opzione apprezzata (feedback 24/10), non
obbligatoria. Movimento unico, lento e progressivo; riproduzione autentica;
sala illustrativa dichiarata come tale oppure fotografia con fonte e diritti.
Non eliminare l'apertura per risolvere il ghosting: correggere il raccordo.
Eseguire `src/artvision_no_ghosting_gate_v1.py` su ricetta e sorgenti; vedere i
fotogrammi reali e i raccordi a velocità normale. Il test non certifica l'estetica.

## Audio, ricerca e consegna

- Verificare fatti, asset e provenienza prima di consumare TTS. La voce resta Google
  Gacrux salvo istruzione diversa. Nessun rimpiazzo robotico automatico.
- Riutilizzare WAV solo con testo, modello, istruzioni e hash coerenti. Leggere
  `ALLINEAMENTO_VOCE.json`; tempi stimati non equivalgono a sincronia verificata.
- Una traccia musicale è la preferenza, ripetibile se pertinente. Cambi motivati,
  volume che protegge il parlato, fine musicale curata. Nessuna promessa algoritmica.
- Consultare V20 e verificare la licenza della registrazione e delle immagini;
  audio Meta non trasferibile automaticamente ad altre piattaforme.
- Evitare primi piani insistiti su nudità artistica e dettagli cruenti, anche in
  copertina. Nessuna garanzia di assenza di claim, ban o successo social.
- V28: post con storia/fatto verificato, pertinenti alla piattaforma e lingua scelta;
  niente note di montaggio al pubblico. Crediti corretti, nessuna domanda artificiale.
- Controllare MP4 effettivo, durata/codec/risoluzione, fotogrammi di tutte le scene,
  primi secondi e raccordi, ascolto integrale di voce/musica. Mai chiamare 4K un Full HD.
- Salvare ricetta V13 con materiali, hash, preset effettivo, commit e regole usate.
  Consegnare MP4 scaricabile, copertina e kit social. Un render riuscito resta
  `rendered_needs_review` fino alla revisione artistica sul file esatto.
- Prima di registrare/importare in Video Library Studio leggere
  `docs/VIDEO_LIBRARY_DOSSIER_V1.md`. Verificare salvataggio, scheda, anteprima e player.
  Una copia di sorgenti nel repository non dimostra cosa sia installato sul sito live.

## Autonomia e manutenzione

Android soltanto, nessun nuovo costo o servizio senza autorizzazione. Eseguire le
scelte operative già autorizzate senza chiedere conferme ripetitive. Pubblicazione
social, caricamento pubblico e programmazione seguono l'autorizzazione della sessione.
Il vecchio incarico V31 ogni tre ore è documentato nella sua guida: questo
aggiornamento non crea né duplica routine. Un format esplicitamente richiesto
prevale sempre sull'alternanza automatica.

Usare V15/V16 per lotti, checkpoint e ripresa. Contare consegne distinte controllate,
non bozze, copie, anteprime o soli WAV. Il target 10/giorno è un obiettivo, non una
capacità certificata. Budget, costi e quote si misurano; non promettere render continui.
Usare V14/V18 per esperimenti e risultati reali: modificare una variabile importante
alla volta quando si vuole confrontare, nessuna promozione automatica a Gold Master.

Per modifiche al codice eseguire i test pertinenti di
`.github/workflows/video-director-v13-check.yml` e dei moduli modificati.
Non inserire credenziali o link firmati in ricette, log o repository.
