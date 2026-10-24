# Regia cinematografica V23 — Biblioteca di linguaggio visivo
*23 ottobre 2026 · integrazione additiva al Creative Director V21*

## Scopo reale
NON applicare 119 tecniche a ogni MP4. Il catalogo \`config/cinematic_techniques_v23.json\`
contiene strumenti di riflessione con **intenzione, applicazione, situazione d'uso
ed errore da evitare**. \`src/cinematic_director_v23.py\` sceglie fino a otto candidati
in base al formato e agli indizi del brief; **non monta nulla e non certifica
la bellezza di un video**. Le interpretazioni dei tag sono ipotesi del planner:
l'agente deve guardare il quadro e ascoltare la voce per confermarle.

### Prima del render
1. Leggi \`AGENTS.md\`, la regia approvata del genere, il catalogo V23 e la ricetta
   del film di riferimento. Preserva i master storici, V6 Gold Master, Critico V2,
   Gacrux e le copertine.
2. Identifica **cosa deve vedere lo spettatore, e perché proprio ora**.
3. Prepara almeno un dettaglio realmente interessante e una progressione
   comunicativa: primi 0/1/3/5/7 secondi, contenuto centrale, esito e finale.
4. Scegli 3–8 tecniche compatibili; una camera FERMA è spesso la prima scelta.
   La scelta può essere diversa ogni volta, anche per lo stesso artista.
5. Per ogni piano annota soggetto, provenienza, crop, \`reason\`, modalità camera,
   ancora di voce e musica. Non inventare coordinate o timestamps se mancano file.

### Durante il montaggio: grammatica di comfort
- **Camera bloccata** quando parla il dettaglio. L'inquadratura può restare ferma
  anche diversi secondi. Nessuna formula fissa per durata o ritmo.
- Eventuali movimenti: UNA SOLA direzione, con motivazione. Tratto unidirezionale
  e partenza/arrivo dolci. Mai oscillazioni sinusoidali, zoom pulsanti, rimbalzi,
  rotazioni gratuite, fake dolly zoom né parallax di figure estratte da quadri piatti.
- Il valore **0–1% di variazione di scala per intero piano** in Critico è una
  prudente scelta di partenza ricavata dalla correzione Bosch V22, NON una regola
  cinematografica universale. Per percorrere veramente una tela vasta si
  possono progettare eccezioni motivate e controllate a velocità reale. Il
  piano può essere del tutto immobile.
- Se si cambia area del quadro, preferire un taglio leggibile o una dissolvenza
  motivata anziché trascinare l'occhio per decine di centimetri attraverso la tela.
- **Eye trace / continuità dell'attenzione:** dopo un dettaglio, l'occhio
  dovrebbe trovare facilmente quello successivo. Se i punti di interesse
  passano da un margine all'altro della tela, valutare un'inquadratura
  totale intermedia, non una panoramica accelerata. V23 segnala salti
  significativi solo quando i centri di ritaglio sono realmente dichiarati;
  non è un giudizio artistico automatico. Fonte:
  https://www.adobe.com/creativecloud/video/discover/edit-a-video.html
- Una dissolvenza breve può sostenere il raccordo; un **match cut** richiede
  che forme/colori/sguardi siano davvero analoghi. Non fare crossfade su ogni piano.
- Ad ogni sostantivo o particolare importante della voce deve corrispondere
  l'immagine pertinente; i tempi derivano dall'audio reale. Senza allineamento
  verifica solo una sincronia STIMATA, mai perfetta.
- Per i video musicali: tagli su frasi/onset realmente analizzati (audio/MIDI);
  non inventare il BPM, e non tagliare a ogni nota per forza.
- Musica con licenza controllata, livelli al servizio della voce; ripetere
  un buon brano quando coerente senza replicare identico montaggio.

### Per formato: cosa cambia davvero

| Serie | Apertura | Camera | Cambi di scena | Finale |
| --- | --- | --- | --- | --- |
| **Critico V2** | Dettaglio autentico + prima frase concreta | Quasi sempre stabile; macro mirate | Sul particolare descritto, con riferimento al totale | Interpretazione fondata, mai domanda posticcia; 0–2 commenti personali |
| **Cinema V6** | Primo quadro con vero potere visivo | Dettaglio / totale, lenti gesti giustificati | Su struttura espressiva della musica e pittura | Nota, respiro e firma già approvati |
| **Enigma** | Anomalia vera da capire | Dettaglio poi progressiva rivelazione | Nuovo indizio, non effetto casuale | Risposta mantenuta |
| **Libri V12** | Protagonista, azione o conflitto immediato | Coerenza spaziale dei personaggi | Su frase reale o nesso causa-effetto | Conseguenza emotiva senza morale aggiunta |
| **Controluce** | Fatto verificato | Evidenze e cronologia | Fonti / prove nuove | Chiarire cosa sappiamo e cosa no |
| **Visual Music** | Evento musicale leggibile | Spazio e geometrie stabili | Note/onset autentici, non metronomo inventato | Risoluzione musicale pulita |
| **HyperLumen** | Forma luminosa leggibile | Moto e luce moderati | Sincronia musicale documentata | Scarica emotiva non lampeggiamenti gratuiti |

### Tre prove sul nostro archivio
- **Bosch V21→V22:** difetto accertato da feedback utente: camera che oscilla
  e dà nausea, con domanda finale estranea. Tecniche candidate:
  \`locked_hold\`, \`panel_geography\`, \`one_claim_one_image\`,
  \`semantic_dissolve\`, \`nonforced_ending\`, \`camera_seasick_gate\`.
  Conservarne il racconto buono, NON replicare le oscillazioni.
- **Füssli / L'incubo:** cavallo → incubo sul petto → donna → scena intera.
  Tecniche candidate: \`human_gaze_start\`, \`negative_space\`,
  \`locked_hold\`, \`detail_return\`. Il dettaglio iniziale deve essere
  riconoscibile, niente movimenti senza scopo.
- **Arte senza voce:** usare \`musical_phrase_cut\`, \`rest_on_resonance\`,
  \`safe_crop\` e \`static_tableau\`; non aggiungere narrazione o effetti a caso.

### Esecuzione dal cellulare Android, senza PC
Il comando è integrato automaticamente nei nuovi pacchetti V21:

\`\`\`bash
python src/creative_director_v21.py --brief modules/artvision_critico/production_series/fuseli_incubo_v22.json --out output/fuseli-piano
\`\`\`

Produce anche \`CINEMATOGRAPHY_PLAN_V23.json\` e
\`CINEMATOGRAPHY_NOTE_V23.md\`. Si può usare il selettore isolato:

\`\`\`bash
python src/cinematic_director_v23.py --brief modules/artvision_critico/production_series/bosch_giardino_delizie_v21.json --out output/bosch-cinema-v23
\`\`\`

Nessuna richiesta a modelli a pagamento, nessun video o copertina sovrascritti,
nessuna pubblicazione automatica. GitHub Actions \`cinematic-director-v23.yml\`
esegue i test e permette di esportare un piano come Artifact sullo smartphone.

### Controllo obbligatorio prima di chiamare «finito» un MP4
1. Campiona fotogrammi veri a 0, 1, 3, 5, 7 s e almeno tre raccordi centrali.
2. Guarda il video a velocità reale sul telefono: nausea, ritmo, leggibilità
   di volti e dettagli. Foto statiche e FFprobe NON rilevano da soli il disagio.
3. Ascolta interamente Gacrux e musica, confrontando le parole con le immagini.
4. Verifica crop, risoluzione reale, fonti, licenze e attribuzioni.
5. Controlla l'ultima frase: conclusione naturale, niente domanda gratuita.
6. Registra scelte, difetti, correzioni e motivi nella ricetta. Il sistema deve
   apprendere dalle correzioni vere, senza inventare metriche o «viralità».

### Letture professionali di riferimento
- StudioBinder — movimento motivato: https://www.studiobinder.com/filmmaking-techniques-camera-movements/
- StudioBinder — repertorio movimenti: https://www.studiobinder.com/camera-shots/camera-movements/
- Adobe — match cut: https://www.adobe.com/creativecloud/video/post-production/cuts-in-film/match-cut.html
- Adobe — J/L cuts: https://helpx.adobe.com/it/premiere/desktop/edit-projects/trim-clips/perform-j-cuts-and-l-cuts.html
- Adobe — Ken Burns su immagini fisse: https://helpx.adobe.com/ph_fil/premiere-pro/how-to/ken-burns-effect.html
- Adobe — montaggio, errori, transizioni: https://www.adobe.com/creativecloud/video/post-production/cuts-in-film.html
- Adobe — ducking del parlato: https://helpx.adobe.com/it/premiere/desktop/add-audio-effects/adjust-volume-and-levels/automatically-duck-audio.html

Queste sono tecniche cinematografiche da cui trarre spunti, NON prove che
una ricetta automatica abbia un'efficacia psicologica garantita sugli utenti.

### Opzione cinematografica: dal museo dentro il quadro (non preset fisso)

**Nuove tecniche facoltative:** `gallery_to_canvas_entry` e `canvas_to_gallery_reveal`. Sceglierle solo quando la cornice e l'ambiente fisico aggiungono valore narrativo: una foto/ripresa **reale e licenziata** dell'opera nella sala → breve avvicinamento morbido → raccordo con l'immagine originale in alta risoluzione → dettaglio motivato. Possibile struttura inversa, dal mistero visivo alla rivelazione del quadro appeso. Non sempre all'inizio: funziona anche in chiusura.

- **No regola fissa:** non introdurla per abitudine o in video consecutivi senza motivo. Per alcune opere il dettaglio immediato è migliore; per altre la cornice è un ottimo primo fotogramma.
- **Autenticità essenziale:** una foto con watermark Flickr non prova alcuna licenza riutilizzabile; cercare autore e autorizzazione della fotografia, oltre alle condizioni d'uso del museo. Non generare una falsa sala spacciandola per documentaria. Se serve una ricostruzione dichiararla nel backstage e non confonderla con una foto del museo.
- **Raccordo credibile:** allineare assi/prospettiva, temperatura cromatica e scala; fare un solo movimento di avvicinamento di norma in circa 2–5 secondi, ma calibrarlo al soggetto e alla musica. Effetto eventualmente fisico (ripresa) o simulato come movimento di camera sulla FOTO REALE, senza fingere 3D interno al dipinto. La vecchia prudenza Critico 0–1% riguarda i microzoom durante la spiegazione, non costituisce limite cieco all'avvicinamento introduttivo dalla sala.
- **QA:** vedere a velocità reale 0/1/3/5/7s, controllare che la transizione non faccia saltare colore, definizione o punto d'attenzione e che il primo secondo abbia un motivo per trattenere lo sguardo.

La scelta è editoriale: la libreria propone, ma nessun renderer deve applicarla automaticamente.
