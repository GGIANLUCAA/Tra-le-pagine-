# ArtVision — architettura evolutiva (decisione 11/11/2026)

## Mandato
Il sistema di produzione autonoma non è un prodotto immutabile: va progettato per poter sostituire, migliorare e collaudare singoli componenti senza riscrivere tutta la pipeline né perdere i video esistenti. Questa è una decisione del proprietario, applicabile alla futura catena event-driven.

## Confini dei moduli
- **Scout e diritti:** candidati, provenienza, licenze e limiti di utilizzo; dati verificabili, nessun asset inventato.
- **Editoriale:** scelta opera/variante, copione, titolo grande e autore ben leggibile, storyboard e revisione naturalezza.
- **Asset e movimento:** selezione clip, animazione e provider (es. Vidu) intercambiabili, ma ogni costo e diritto passa dal gateway esistente.
- **Render:** un solo lavoro pesante attivo, lock e deduplica atomici; nessun master sovrascritto.
- **QA:** test tecnici separati dalla revisione artistica; gli esiti non si confondono.
- **Delivery:** MP4, ZIP Android, copertina, testo social, hash e link verificato; nessuna pubblicazione automatica.
- **Orchestrazione:** eventi di completamento, selezione prossima attività, retry limitati, quarantena singolo candidato e preparazione parallela sicura.

## Contratti e versioni
Ogni fase deve ricevere un manifest versionato con ID stabile (opera + variante + versione), input SHA, stato, fonti/licenze, crediti/costi autorizzati, output SHA e motivazione di eventuale stop. Modifiche incompatibili richiedono una nuova versione dello schema e migrazione esplicita. I master approvati rimangono immutabili.

## Evoluzione senza regressioni
1. Sviluppare su branch/PR, mai direttamente su master o produzione.
2. Test unitari, simulazione dry-run, test integrazione senza spesa, poi canary su un solo candidato.
3. Confronto reale con benchmark approvati: movimento, regia, voce, titolo/artista, scala museale, sincronizzazione e Android.
4. Attivare con flag; rollback rapido se peggiora qualità, costi o affidabilità.
5. Registrare metriche: video validi consegnati, tempo di ciclo, duplicati, errori, costo per video, bocciature artistiche.
6. Analizzare periodicamente i risultati e proporre miglioramenti; niente auto-modifica del codice di produzione senza test e controllo.
7. Se un candidato fallisce, isolare solo quello e continuare con preparazione degli altri; non forzare un nuovo render se lo stato del lock non è verificabile.

## Stato di implementazione
Questo documento è una regola di progetto e una roadmap, **non** una pipeline già funzionante. Il selettore V1 della PR #258 è ancora in dry-run. L'integrazione eventi, lock live, recupero guasti, test end-to-end e consegna automatica devono essere implementati e verificati separatamente.
