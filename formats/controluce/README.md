# CONTROLUCE — Modulo separato di cronaca narrativa

**Stato: versione pilota di sviluppo.** Nessun file dei libri in `episodes/`, nessun vecchio workflow o script modificato. Il vecchio renderer `src/render.py` è riutilizzato *senza modifiche* soltanto dopo i controlli specifici per la cronaca.

## Come funziona

1. **Ricerca:** `python src/controluce.py collect --date 2026-10-18 --output output_controluce/candidates.json` raccoglie titoli e link RSS dalle fonti configurate in `sources.json`. Se un feed non funziona, il report indica l'errore e continua con gli altri. **Non verifica notizie e non produce un copione automaticamente.** Nessuna chiave AI necessaria.
2. **Selezione e verifica:** si sceglie **una sola storia centrale**, si verificano data dell'evento, fonti originali, fatti e versioni, e si compilano `research.json`, `testo.txt`, `scene_cues.json`, `metadata.json`, `asset_manifest.json`, `DESCRIZIONE_SOCIAL.txt`.
3. **Revisione:** `python src/controluce.py validate --episode formats/controluce/episodes/2026-10-18_trasporti_sud --without-images` esegue controlli strutturali dopo che il redattore ha impostato consapevolmente entrambi i flag di approvazione. In questa fase non vengono spesi crediti.
4. **Materiali:** creare 8–20 immagini premium pertinenti ai momenti della voce. Per foto documentali usare solo materiali autorizzati e verificati; le immagini artificiali devono essere riconoscibili come ricostruzioni quando necessario.
5. **Render:** `python src/controluce_render.py --episode formats/controluce/episodes/2026-10-18_trasporti_sud --engine gemini --effects v4 --out output_controluce/video`. Richiede Python, FFmpeg, dipendenze e segreto Gemini già usati da Tra le Pagine; controlla fonti, diritti, immagini e approvazioni **prima** di chiamare la voce a pagamento. Eredita gli effetti video; restituisce `CONTROLUCE_YYYY-MM-DD.mp4`, copertina, sottotitoli, copione e dossier. Non pubblica.

Il workflow `controluce-ricerca.yml` esegue soltanto una **raccolta di candidate ogni giorno alle 06:30 UTC** (07:30 in inverno / 08:30 in estate in Italia) e la salva come artifact GitHub per 14 giorni. La ricerca può essere avviata manualmente. Il workflow `controluce-render.yml` è **solo manuale**, non programmato. GitHub Actions usa normalmente i workflow presenti nel ramo predefinito: per renderli disponibili nella UI servirà integrare il ramo di sviluppo dopo revisione.

## L'episodio pilota

`episodes/2026-10-18_trasporti_sud` contiene un copione originale sui blocchi degli autotrasportatori nel Sud, basato su cronache del **18 ottobre 2026** e antecedenti; il nome della cartella è un semplice identificativo tecnico storico e non indica Milano come luogo del fatto. I report includono fonti controllabili. **È una proposta non approvata** e manca il materiale fotografico definitivo. Non modificare i due flag su true finché non siano completate le verifiche.

## Protocolli e limiti

- Le fonti indipendenti sono prioritarie nella **scoperta**, non automaticamente vere. ANSA, RaiNews e altri media servono per confronto e controllo; fonti primarie dove possibili. Il report RSS mostra solo candidati e non inferisce data dell'evento dalla pubblicazione.
- Non generare accuse senza prova, non clonare le voci di giornalisti, non imitare Pasolini parola per parola, non falsificare foto di cronaca.
- Il sistema non ha oggi un generatore immagini programmato, un LLM per selezione/ricerca autonoma, né una licenza automatica per fotografie di testate: tutte queste restano integrazioni future da scegliere e autorizzare.
- Non promettere che un MP4 esista se mancano materiali o se il render non è stato testato; non pubblicare in automatico.
- Se serve ripristinare il progetto originale, il ramo di riferimento è `backup/pre-controluce-2026-10-19`, basato sul commit `73b701f25ca5944bc4b0b544ba07c72a401fa6b3`. **Questo è un backup del codice Git; non degli eventuali segreti GitHub, degli artifact temporanei e degli asset fuori repo.**

## Cosa verrà dopo

Aggiungere in modo reversibile: un'interfaccia web per scegliere format/episodio; una pipeline di generazione immagini a costo controllato; un modulo LLM per preparare bozze da fonti verificabili (mai pubblicazione senza revisione); un registro dei preset di regia condivisi; test end-to-end del render con immagini vere.
