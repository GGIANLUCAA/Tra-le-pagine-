# V38 — Riferimento positivo e regia narrativa senza stampino

**Approvazione diretta:** feedback del 26 ottobre 2026 sul video **La macchina del tempo — H. G. Wells**. Ambito: tutti i nuovi video; approfondimento specifico per libri, racconti e fiabe. Questa guida consolida **le regole V25 sulla regia motivata**: non le sostituisce, non impone un nuovo preset e non approva automaticamente un master.

## Risultato positivo, non GOLD MASTER

Gianluca ha valutato **La macchina del tempo** più bello dei precedenti, soprattutto per la **maggiore quantità e varietà delle immagini**; ha aggiunto che può ancora migliorare. Il filmato realizzato aveva **16 illustrazioni** e circa **3 minuti**: questi sono **dati descrittivi di quell'episodio**, non un numero minimo, massimo, target, durata standard o template per altri episodi.

Identificatore del riferimento: `TRA_LE_PAGINE_LA_MACCHINA_DEL_TEMPO.mp4`. **Non è dimostrata la sua importazione nel sito Video Library Studio**; non scrivere link inventati e non qualificare il filmato come pubblicato, gold master, approvato legalmente o universalmente ottimale.

### Qualità trasferibili ad altri racconti

- **Ricchezza visuale sensata:** più immagini distinte quando fatti, azioni, personaggi, luoghi e svolte della storia lo richiedono. Non aggiungere immagini per raggiungere una quota o riempire una scena.
- **Aderenza parola-immagine:** individuare i nuclei di significato e usare per ciascuno immagini pertinenti, coerenti nei personaggi e nei luoghi; cambiare visuale quando cambia davvero il contenuto narrato.
- **Mix originale:** alternare, quando appropriato, ambientazioni, azioni, personaggi, oggetti importanti, pause contemplative e momenti emotivi. Il loro ordine è determinato dalla storia, non da un ciclo prestabilito.
- **Regia motivata:** alternare camera ferma, movimenti minimi, variazioni di scala e tagli puliti solo dove aiutano la comprensione. No primi piani tagliati, oscillazioni, sovrapposizioni trasparenti confuse o mosse ripetute senza funzione.
- **Identità coerente:** mantenere la firma delle copertine e del format; differenziare contenuto, atmosfera, ritmo e soluzione registica episodio per episodio.
- **Finale:** chiudere il pensiero o la storia quando il contenuto lo richiede, senza domande artificiali o allungamenti.

## Sequenza di decisione per ogni nuovo video

1. Leggere regole e profilo format, recuperare **solo gli aspetti pertinenti** dei riferimenti positivi; annotare anche i limiti riconosciuti.
2. Studiare storia/opera/pubblico, poi costruire **beat narrativi**, eventi, cambi di luogo/tempo/emozione e possibili bisogni visuali prima di fissare la durata o il numero di immagini.
3. Preparare una proposta motivata: perché questa durata; quali scene e immagini **distinte** sono utili; dove cambia il ritmo e perché; quali scelte di camera aiutano; quali fonti/diritti e fallback si usano.
4. Eliminare immagini ridondanti o decorative, valutare continuità di personaggi, pertinenza scena-parola e allineamento all'audio **effettivo**.
5. Confrontare con i riferimenti solo sulla **qualità trasferibile**, non cercando di ripetere 16 immagini, 3 minuti, stessi secondi per scena, stessa transizione, stesso incipit o stessa musica.
6. Dopo il render valutare prima e dopo le variazioni visive, raccordi e finale; registrare feedback positivo e problemi residui separatamente. Il QA tecnico non certifica la qualità estetica.

## Cosa NON fare

- Non inventare `target_images=16`, `duration=187s`, 20/30 immagini obbligatorie, una scena ogni tot secondi o effetti per scena con valore fisso.
- Non utilizzare casualmente un medesimo template cinetico per libri molto diversi. Un testo calmo puo funzionare con pochi fotogrammi lunghi; un racconto d'avventura può richiedere molte scene nuove.
- Non trasformare il giudizio positivo su un episodio nell'approvazione globale del suo audio, copertina, licenze, fonti o stato di pubblicazione.
- Non sostituire le altre regole: fonti V33, selettore V34, diritti V20, social V28, dossier, copertine approvate, voce e download restano applicabili.

## Tracciamento strutturato

Fonte unica machine-readable: `config/editorial_rules.json` alle chiavi `creative_variation` e `creative_references.time_machine_20261026`.

Nei nuovi `PROJECT_V13.json` i campi dell'`editorial_plan` per durata/mix/tecniche restano motivati. Una nuova sezione facoltativa `narrative_design` raccoglie beat, esigenze delle immagini e motivazione del ritmo, senza imporre un numero di fotogrammi predefinito e senza attribuire valore di licenza a fonti ancora da verificare. I progetti vecchi non sono automaticamente certificati o riscritti.

**Principio:** standardizzare il controllo della qualità, **non** il filmato.

## Controllo operativo V38B — integrato nel preflight V13 (26 ottobre 2026)

Il nuovo modulo offline `src/narrative_variation_v38.py` elabora `PROJECT_V13.json` senza API, video né costi. Il comando esistente `python src/video_director_v13.py check --project ...` restituisce anche un oggetto JSON `creative_review` ed eventuali messaggi `V38` nella lista `warnings`:

- `VISUAL_NEEDS_NOT_PLANNED`: beat dichiarati, bisogni visivi non motivati.
- `VISUAL_COUNT_NOT_MOTIVATED` e `RHYTHM_NOT_MOTIVATED`: più scene previste ma manca la ragione di quantità e ritmo.
- `DUPLICATE_SHOT_WITHOUT_REASON`: due scene consecutive con stessi asset, descrizione e motivazione; annotare `reuse_reason` se il ritorno è davvero voluto, oppure correggere storyboard.
- `REPEATED_CAMERA_UNEXPLAINED`: pattern di movimento uguale ripetuto in una sequenza priva di `camera_reason`; va giudicato artisticamente, non eliminato a priori.
- `REFERENCE_TEMPLATE_RISK`: riferimento positivo usato dichiarando di volerne copiare i parametri, anziché le lezioni trasferibili.

L'output espone **scene e asset osservati**, non obiettivi artistici. Un filmato con un'unica scena pertinente rimane legittimo, così come uno con molte immagini distinte. La stessa illustrazione può tornare per ragioni narrative reali, dichiarabili nel progetto. Tutte le segnalazioni sono advisory e non nuove quote o blocchi rigidi al render. Un check senza segnalazioni non certifica che il video sia bello, che le immagini rappresentino davvero il testo o che i diritti siano in regola.

Test: `tests/test_narrative_variation_v38.py` e caso di integrazione in `tests/test_video_director_v13.py`. Il gate generale V13 sui diritti e sulle fonti resta invariato; master e ricette passate non sono modificati.
