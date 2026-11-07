# ArtVision 4×1 — ponte stabile tra laboratorio e produzione (V1, 7 novembre 2026)

## Decisione del proprietario
Due chat possono lavorare in parallelo senza confondere i compiti:
- **Laboratorio tecnico musei e cornici (questa chat)**: ricerca approfondita, fotografie e licenze, geometria e scala fisica, prove di camera, benchmark e QA. Scrive dossier e *proposte*, NON modifica la coda o i master di produzione.
- **ArtVision 4×1 · Produzione seriale (altra chat + automazione owner già attiva)**: prende decisioni operative sulla coda autorizzata, rende e verifica i veri MP4, esegue QA/backup e gestisce gli impedimenti. Sola automazione owner ID `6adca191603c8191a90d5190901cd034`.
- **Ricerca nuove opere e fonti**: già separata e automatizzata giornalmente, usa `docs/ARTVISION_RICERCA_OPERE_FONTI_HUB_20261107.md` e `research/artvision_future_works_index_v1_20261107.json`; non sostituisce il laboratorio cornici e non cambia la produzione.

**Le chat non si trasmettono messaggi in tempo reale.** La condivisione affidabile avviene tramite repository GitHub (main), documenti, prove e link agli asset autentici. Una conversazione lunga senza checkpoint non è un archivio completo. Questa procedura non crea automazioni, render o spese aggiuntive.

## Unico registro di collegamento
`research/artvision_museum_frames_handoff_v1_20261107.json` è il punto di ingresso per il lavoro di questo laboratorio. Contiene:
- `id` stabile, opera esatta + inventario (se legata a un dipinto), e **categoria** (sala, cornice, camera, regola);
- link al **dossier verificabile**, fonti ufficiali, fotografie/asset con autore, attribuzione, licenza e condizioni territoriali;
- dimensioni fisiche in cm e corrispondenza con geometria/metri, foto/texture/mesh e SHA-256 realmente verificato (mai inventato);
- file ZIP/MP4 di prova, SHA-256 e link a backup reale, confronto A/B, errori osservati, FFmpeg QA, ispezione prospettica/ombra/montaggio e giudizio artistico;
- `research_status`, `production_handoff`, `owner_approval`, `blockers`, `next_action` e origine della decisione.

Per materiali grandi (MP4, texture, fotografie) conservare i **byte veri** solo in una destinazione appropriata/autorizzata (Libreria, archivio privato, artifact/release secondo diritti), con SHA e download di ritorno quando possibile. **Un percorso locale /mnt/data, il solo filename, una foto candidata o un manifest non provano il file disponibile** a un'altra chat.

## Quattro livelli non confondibili
1. **`candidate`** — idea o fonte identificata, senza autorizzazione di riutilizzo o disponibilità bytes.
2. **`source_checked`** — fonte/licenza/esemplare e misure documentati; se asset ancora da scaricare lo si dice. Non basta per un MP4.
3. **`trial_qa_passed`** — asset fonte originale realmente letto e hash controllato; prototipo MP4 vero con QA geometrico, continuità, cornice e scala + controllo visivo. Il prototipo è ancora *sperimentale*.
4. **`production_approved`** — soltanto dopo consenso concreto del proprietario per l'adozione di una nuova regola/preset, identificabile e registrato, più gate dei diritti e della qualità. L'approvazione di un preset NON approva il singolo filmato né lo rende Gold V25.

`production_handoff` assume SOLO `research_only`, `proposed_for_trial`, `approved_for_adoption`. La produzione deve ignorare `research_only` come istruzione e non trattare `proposed_for_trial` come asset pronto; può fare un provino circoscritto quando già autorizzato dalla coda e dalle regole. Una proposta non cambia AGENTS/REGOLE_ATTIVE/queue/renderer automaticamente.

## Regole comuni già attive — nessuna riscrittura
- Restano intatte `AGENTS.md`, `docs/REGOLE_ATTIVE.md`, V80, V118, V119, `config/artvision_museum_library_v119.json` e la coda `queue/artvision_owner_selected_ten_20261102.json`.
- **GAL01–GAL05 e FRA01–FRA05 sono descrizioni di candidati, NON dieci asset creati o approvati**. Il laboratorio deve sempre preferire una cornice documentata per l'esatto quadro; eventuale scena neutra va etichettata come ricostruzione, mai luogo reale dell'opera.
- La pittura mantiene dimensioni fisiche documentate; sala e cornice coerenti, ingresso/uscita in camera continua, cornice fuori campo nei dettagli, no plastica/disegno/porte dietro il dipinto, niente scene statiche mascherate da video. La sola decodifica FFmpeg non equivale a qualità artistica.
- L'owner ha autorizzato il riuso selettivo di ambienti precedenti quando veritieri e adatti: il laboratorio registra *esattamente* quali asset sono recuperabili/compatibili, non promuove una foto senza una scena 3D/MP4.
- Niente nuova automazione concorrente, pagamenti non approvati, modifica master, pubblicazione o Gold automatico. Questa è una **procedura di comunicazione**, non un nuovo format video.

## Passaggio controllato tra chat
**Laboratorio → produzione:** al termine di uno studio solido, aggiungere al registro ID, percorso dossier, stato verificato, link/sha/diritti, limiti e prossima azione. Se è un cambiamento di regia o di asset globale, marcarlo `proposed_for_trial`; prima di promuoverlo a regola operativa serve consenso del proprietario registrato. Pubblicare su GitHub il commit ed eventualmente indicarlo nell'altra chat.

**Produzione → laboratorio:** quando incontra un blocco di sala/cornice, produce un rapporto preciso (opera/inventario, peso/altezza in cm, foto fallita, requisito non soddisfatto, asset tentato, prova del difetto, slot e prossimo bisogno) senza generare una nuova richiesta vaga. Il laboratorio aggiorna il medesimo ID e fornisce alternative, mantenendo intatta la coda.

**Lettura dall'altra chat:** iniziare da `AGENTS.md` e da questo file; leggere solo le voci `approved_for_adoption` come nuove istruzioni approvate, e tutte le altre come materiale di ricerca consultabile. Se il proprietario cambia idea, documentare la data e il riferimento e aggiornare una sola volta la policy globale dopo la verifica, senza cancellare lo storico.

**Criterio di successo:** un test riproducibile su un'opera reale passa da dossier documentato → prototipo visivamente controllato → approvazione (se richiesta) → uso in una delle quattro varianti, senza dover rispiegare il lavoro tra chat, senza duplicati e senza peggiorare i master già buoni.
