# V320 — Naturalezza autoriale e regia anti-stampino (10/11/2026)

**Decisione editoriale del proprietario, globale per tutti i nuovi video.**
Il feedback sul vero Bruegel Critico V3 è: video semplice e apprezzabile, ma
la domanda filosofica finale suona generata e rivela una struttura artificiosa.
Non è un giudizio sull'origine tecnica della voce; riguarda l'insieme di
scrittura, recitazione, ritmo, inquadrature, musica, chiusura e copia social.

## Principio editoriale

Ogni episodio deve sembrare *pensato per questa storia e per nessun'altra*.
Non fingere mai che un'automazione provi una sensibilità umana: la naturalezza
si valuta leggendo, ascoltando e guardando il contenuto reale. Non dichiarare
falsamente che sia stato scritto/ripreso da una persona, né mentire sulla
provenienza se richiesta. Obiettivo: qualità autoriale, non occultamento.

## Scrittura italiana narrata

1. **Mostra e racconta una cosa precisa.** Ogni frase deve apportare un fatto,
   un'osservazione visibile, un gesto, una tensione documentata o una relazione
   autentica. Dove l'immagine non prova ciò che si dice, ricercare o cambiare
   frase/inquadratura. Non inventare dettagli per rendere il testo più “umano”.
2. **Niente conclusioni filosofiche preconfezionate.** Non inserire a fine
   video “il quadro ci lascia una domanda”, “l'opera ci invita a riflettere”,
   “forse il vero mistero è…” o varianti moralistiche sostituibili con qualsiasi
   soggetto. Nessuna domanda finale obbligatoria; le vere domande nate dalla
   ricerca possono restare se servono davvero.
3. **Finale guadagnato.** Chiudere su una scoperta concreta già preparata dalle
   scene, un gesto/suono/dettaglio residuo, un fatto storico rilevante o una
   frase sobria. A volte chiudere senza voce è meglio.
4. **Voce conversazionale competente, non “trailer AI”.** Alternare frasi brevi
   e frasi distese seguendo ciò che si comprende, senza introdurre pause,
   sussurri, enfasi, spiegazioni urlate, retorica del mistero o superlativi
   a ogni riga. Pronuncia corretta e punteggiatura ascoltabile. La voce tecnica
   naturale non basta se il copione è artificioso.
5. **Evita cadenze linguistiche fotocopia:** “Non è solo X, ma Y”,
   “eppure c'è di più”, “ancora oggi...”, “in un mondo in cui...”, “non si
   tratta di...”, “ma cosa succede se...”. Non sono tabù assoluti: se portano
   significato specifico sono ammessi; il problema è il loro uso seriale.
6. **Scegli il punto di vista giusto** per la storia: testimone, critico
   d'arte, osservatore, storico, restauratore o narratore. Non fingere esperienze
   personali non avute, fonti consultate che non esistono o interviste inventate.
   La sobrietà non è monotonia: curiosità, ironia e meraviglia sono ammesse se
   nascono davvero dalla materia.

## Regia e video privi di voce

- Il linguaggio umano non è fatto di tagli identici ogni quattro secondi o
  di zoom progressivi su ogni immagine. Piani fermi, movimenti e raccordi
  cambiano per il soggetto, non per un preset.
- Non riutilizzare meccanicamente la stessa apertura, stessa sequenza wide
  → detail → wide, stesso crescendo musicale o stessa chiusura in ogni video.
  Controllare gli ultimi 3–5 episodi dello stesso formato prima del nuovo.
- Per La Storia Rivive e WOW LAB privi di narrazione: la “voce autoriale” è
  il montaggio. Spostamenti, originali/colore, musica, effetti e pausa finale
  devono seguire la fonte e il moto reale; mantenere V70/V94/V96/V99,
  i vincoli sui volti/diritti e sulle clip Vidu. Evitare effetti-tipo ripetuti.
- Le scritte pubbliche e le quattro copie social devono essere specifiche per
  quell'opera/epoca, non generiche presentazioni promozionali; seguire V134.
- Musei e quadri: autentica scala/cornice e sincronia frase–particolare
  rimangono i requisiti più importanti. Nessuna falsa sala per aumentare wow.

## Gate operativo gratuito

Il modulo src/editorial_human_naturalness_v1.py controlla il testo **prima di
una nuova chiamata TTS**, e supporta anche copia social e scritte a schermo.
Segnala poche formule di finale realmente generiche (blocca un nuovo TTS finché
non si riscrive) e altri indizi da revisione (warning, non blocco automatico).
Non è un rilevatore di testi AI, non “certifica umano”, non scrive/copre scene
e non chiama servizi a pagamento. Un PASS significa soltanto **nessuna delle
formule elencate riconosciuta**, non approvazione editoriale.

Per narrazioni Google Gacrux prodotte da src/gemini_voice.py:
- Se il WAV presente è già verificato da cache e hash, riusarlo senza riscriverlo
  o consumare nuovo credito. La regola è prospettica, non retroattiva.
- Prima di richiedere **una nuova** voce, salvare il report editoriale;
  se contiene formule bloccanti, non invocare la TTS.
- Prima della pubblicazione/revisione artistica finale, la registrazione e il
  MP4 devono essere ascoltati e guardati per intero; il gate è un supporto,
  non sostituisce il giudizio umano. Nessuna auto-approvazione.
- Per i renderer che usano un'altra TTS, il modulo resta disponibile come
  preflight in attesa di integrazione; non dichiarare enforcement universale
  soltanto perché esiste una regola markdown.

## Bruegel — correzione editoriale proposta, NON audio già prodotto

Vecchio finale V144/V3: “La lotta tra bene e male sembra infinita. E il
quadro ci lascia una domanda: il mostruoso appartiene davvero a un altro
mondo, oppure nasce già dentro il nostro?”

**Possibile finale nuovo, da validare sul dipinto originale e sui frame:**

> Al centro, Michele tiene alta la spada. Ma tutto intorno continua il
> disordine: piume, corazze, becchi, corpi che si accalcano. In pochi
> centimetri di pittura, Bruegel ha nascosto una quantità incredibile
> di dettagli. Ne trovi sempre un altro che prima ti era sfuggito.

Non riprodurre automaticamente questa stessa struttura in altri video.
Questa bozza NON modifica il WAV Gacrux o i tre MP4 esistenti.
Se verrà approvata e registrata una nuova narrazione, Critico Standard
e Critico Museum dovranno condividere lo stesso WAV nuovo e verificato.

## Verifica di consegna: cinque domande reali

- La frase finale potrebbe chiudere anche un video su tutt'altro soggetto?
  Se sì, riscrivere.
- Un documentarista reale pronuncerebbe queste parole a voce alta senza
  sembrare uno spot pubblicitario?
- In ogni frase si vede proprio ciò che viene nominato?
- Il pubblico scopre qualcosa di particolare o subisce soltanto effetti?
- Il confronto con altri episodi rivela tic ripetuti nell'apertura, nello
  sviluppo, nel volume o nella conclusione?

**Precedenze:** diritti, correttezza storica, sicurezza, formato, V80/V82,
V91/V94/V96/V99, nessuna spesa non autorizzata, tutela master V25 e
nessuna pubblicazione automatica restano vincolanti. L’umanizzazione
non permette mai di falsificare fatti o soggetti.
