# Regia Supervisor V1 — piano di montaggio comune, senza regressioni (10/11/2026)

## Problema diagnosticato nel repository

Esistono gia:
- V21 Creative Director e V23 Cinematic Director: consulenza tecnica e artistica, non correzione automatica dei veri render.
- V17 Quality Director: metadata MP4, fotogrammi campionati, silenzi e progetto V13; non ha da solo una timeline visiva completa.
- V70 La Storia Rivive: ritmi B/N, reveal e fermo, guardrail specializzati.
- ArtVision Focus V1 / V82: verifiche parola-oggetto soltanto dove il renderer emette la traccia camera e la voce allineata.
- ArtVision Learning Loop V1: archivio delle recensioni verificate, non una AI che vede i film da sola.

La lacuna comune era una shotlist verificabile per anticipare errori di regia prima di sprecare render, senza pretendere che tutti i format condividano ritmo, effetti e numero di immagini.

## Implementazione di questo intervento

- src/studio_regia_supervisor_v1.py: preflight gratuito di una shotlist. Errori bloccanti (fonti/diritti dichiarati mancanti, timing sovrapposti, soggetto narrato assente dalla pianificazione, crossfade/ghosting, camera inappropriata) e problemi da revisionare (immagini ripetute, dettagli troppo brevi, enormi salti dello sguardo, scarsa risoluzione effettiva, stesso movimento ripetuto).
- src/quality_director_v17.py --regia-plan: unisce i codici preflight ai vecchi report V17. Produce STUDIO_REGIA_SUPERVISOR_V1.json accanto al report JSON/HTML senza confondere le loro fonti di evidenza.
- .github/workflows/quality-director-v17.yml: accetta opzionalmente shotlist e MP4 gia presenti nel checkout. Se il QA fallisce non usa piu la clausola || true per nascondere l'errore; mantiene gli artifact con if: always().
- Test di regressione a costo zero. Non aggiunge automazioni, cron, chiamate IA, render, nuove spese o pubblicazioni.

### Formato shotlist

Esempio di struttura per un Critico con voce. I campi e i tempi di esempio NON descrivono un MP4 reale:

    {
      "schema": "studio-regia-shotlist-v1",
      "format": "artvision_critico",
      "video_duration_s": 6,
      "delivery_resolution_px": [1080, 1920],
      "narration": {
        "wav_sha256": "SHA256_REALE_64_CARATTERI",
        "timing_verified": true,
        "segments": [
          {"start_s": 0.0, "end_s": 3.0, "subject_id": "gruppo"},
          {"start_s": 3.0, "end_s": 6.0, "subject_id": "volto"}
        ]
      },
      "shots": [
        {
          "id": "shot_01", "start_s": 0, "end_s": 3,
          "source_verified": true, "rights_verified": true,
          "asset_id": "dipinto_originale", "composition_group": "wide",
          "visual_subject": "Gruppo", "visible_subject_ids": ["gruppo"],
          "reason": "Inquadrare il gruppo mentre viene descritto",
          "shot_type": "wide", "focus_xy": [0.5, 0.5],
          "camera": {"move": "locked"}
        },
        {
          "id": "shot_02", "start_s": 3, "end_s": 6,
          "source_verified": true, "rights_verified": true,
          "asset_id": "dipinto_originale", "composition_group": "portrait",
          "visual_subject": "Volto", "visible_subject_ids": ["volto"],
          "reason": "Mostrare il volto senza tagliarlo",
          "shot_type": "detail", "focus_xy": [0.6, 0.4],
          "camera": {"move": "slow_push"}
        }
      ]
    }

FONDAMENTALE: i segmenti voce devono usare il tempo effettivo del VIDEO, con offset gia applicato, non il tempo fittizio del copione. visible_subject_ids e source_verified sono attestazioni dello storyboard: il software non identifica davvero soggetti o licenze. In Museum il movimento deve rispettare la continuita di ingresso/uscita e richiede i gate V80/V118/V119 separati. In Storia Rivive si applicano comunque V70/V91/V94/V96/V99: questo supervisore non sostituisce ne aggira i loro criteri.

### Esecuzione (senza render)

    python src/studio_regia_supervisor_v1.py --shotlist percorso/SHOTLIST.json --out output/REGIA_PREFLIGHT.json
    python src/quality_director_v17.py --format artvision_critico --regia-plan percorso/SHOTLIST.json --out output/quality-v17

Con MP4 locale realmente disponibile:

    python src/quality_director_v17.py --video percorso/MASTER.mp4 --format artvision_critico --regia-plan percorso/SHOTLIST.json --out output/quality-v17

## Cosa manca prima di chiamarlo regista autonomo

1. Integrazione produttiva reale: ogni renderer deve esportare shotlist con valori misurati; V1 non riscrive da solo gli script indipendenti o gli MP4 preesistenti.
2. Visione/audizione vera: analizzare i frame e le parole, verificare la visibilita di persone/oggetti, volti, tagli e movimento. Il report V1 non prova la semantica di un frame.
3. A/B non distruttivo: correggere una sola variabile per volta (inquadratura, durata, timing o movimento), conservare master originale e tornare indietro se N+1 peggiora.
4. Cicli seriali: inserire il preflight nel workflow owner gia esistente di ciascun format solo dopo prova su un episodio, con contratto di input specifico e senza creare scheduler concorrenti.
5. Misurare i risultati: conservare gli hash dei video, note precise e feedback dell'owner. In seguito confrontare retention reale quando disponibile, senza inventare il tasso di successo e senza usare punteggi finti.

## Approccio cinematografico (ipotesi di test, non regole universali)

- Soggetto e promessa visiva leggibili nei primi secondi; non necessariamente una raffica di tagli.
- Tagliare quando cambia informazione, rapporto fra soggetti o significato, non ogni X secondi. Le riprese complesse richiedono spesso piu tempo di lettura.
- Con la voce: frase e soggetto si devono sovrapporre nel video reale. Camera ferma mentre si studia un dettaglio; eventuali panoramiche motivano una scoperta.
- Con la musica: usare frasi e onset verificati della traccia, non un BPM inventato.
- Per il restauro: il colore si deve poter ammirare e la ricostruzione deve provenire dallo stesso frame autentico; la durata del reveal rimane al gate V70/V96, non si deduce dalla shotlist generica.

Ricerca di supporto:
- Tim J. Smith (2012), The Attentional Theory of Cinematic Continuity: la continuita dipende anche da dove guarda lo spettatore.
- Balzarotti et al. (2021), The Editing Density of Moving Images Influences Viewers' Time Perception: i tagli cambiano sguardo e percezione del tempo, non garantiscono di per se bellezza.
- REGen (NeurIPS 2025): narrazione e selezione di inserti documentaristici sono due passaggi collegati da una ricerca semantica di video pertinenti.

Questo codice e una prima riparazione verificabile del processo di regia, non un'affermazione che i video finali siano diventati migliori prima del confronto reale.
