# Regole attive — 25 ottobre 2026

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
8. Consegnare MP4, copertina, post differenziati, fonti/crediti e dati di replica.
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
