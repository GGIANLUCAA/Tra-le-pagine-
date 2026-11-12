# Regia V326 — studio dei 5 reels del proprietario (12 novembre 2026)

## Scopo: rubare i principi, mai copiare il prodotto

Riferimenti consegnati nella chat: 57966 (Carrington), 57967 (Mednyánszky),
57968 (Rockwell), 57969 (Tagore), 57970 (Caravaggio). I video sono esempi
di **linguaggio visivo**, NON sorgenti autorizzate alla ripubblicazione:
nessun riuso di fotografie, musiche, frame, soundtrack, voiceover o animazioni
senza un controllo indipendente su fonti/diritti. Non esiste prova di viralità
o retention senza analytics originali.

Osservazioni da usare come criteri editoriali, non prescrizioni:
- **57966 Carrington**: immagini memorabili e soggetti sorprendenti; rischio
  di accumulare quadri più rapidamente di quanto l'occhio possa interpretarli.
  Convertire la sorpresa in dettaglio → relazione → rivelazione.
- **57967 Mednyánszky**: coerenza malinconica e atmosfera profonda;
  rischi di gamma e intensità uniformi, il buio sullo smartphone nasconde
  il soggetto. Cercare un cambiamento emotivo giustificato dall'opera.
- **57968 Rockwell**: leggibilità immediata e accessibilità; evitare gallerie
  con cambio immagine sempre uguale. Controllare code nere e pause inutili.
- **57969 Tagore**: curiosità iniziale e identità dell'artista; evitare
  superlativi assoluti non dimostrati e cartelli finali eccessivi.
- **57970 Caravaggio**: dettaglio → scoperta → composizione leggibile.
  Conservarne la *logica dello svelamento*, non replicare in ogni video
  la stessa sequenza/cronologia.

## Due linguaggi, non un template uguale per tutti

1. **Artist gallery**: varie opere originali di un artista, ritmo musicale,
   legami di forma/luce/gesto fra dipinti distinti; il cambio opera ha sempre
   una motivazione. Nomi e titoli leggibili, senza costante sovrimpressione.
2. **Single painting discovery**: un'opera autentica, indizi e dettagli coerenti
   con posizione nel quadro, ingresso/uscita su composizione completa.
   Non inventare profondità o animare i volti nel modo sbagliato.
3. **Critico narrato ArtVision**: usare esclusivamente le frasi allineate al
   vero WAV/ASR; ogni beat contiene l'oggetto pronunciato nel suo campo.
   Il modulo V326 segnala l'assenza di un visual_anchor ma non può certificare
   che il dipinto contenga realmente quell'oggetto.
4. **Museum**: prevalgono V80/V82/V118/V119 e le quattro varianti. L'idea
   dei reels NON autorizza jump-cut impossibili attraverso la cornice,
   ricostruzioni false o ingrandimenti sfocati della sala.
5. **La Storia Rivive**: rimangono prioritari 4+1, colore realmente misurato,
   identità dei soggetti e i gate V91/V94/V96/V99/V323. Nessun nuovo format
   artistico sostituisce gli obblighi del restauro.

## Decisioni di regia da prendere prima del render

Per ciascun shot, quando possibile, registrare:
- opera/accession/source_url/diritti/hash; regione effettivamente visibile,
  persona o elemento chiave, tipologia di campo e motivazione del movimento;
- inizio/fine o durata di progetto (facoltativi ma consigliati);
- visual_anchor, purpose, complex_detail quando serve;
- spoken_anchor per i narrati, da confrontare con vero copione e vero WAV;
- rhythm_justification quando un brevissimo flash, una lunga pausa o un taglio
  insolito sono voluti e narrativamente giustificabili.

Il ritmo non deve essere pianificato con una regola "ogni N secondi".
Il V326 segnala **per review**, non vieta automaticamente, flash < 1,1s,
dettagli complessi < 2s, lunghe pause statiche in uno short, tre ripetizioni
di opera/focale/movimento, durate meccaniche, cartelli conclusivi > 2,5s
e sovrapposizioni non chiarite. Le soglie sono euristiche, non prove
psicologiche di piacere/retention. Esistono eccezioni legittime.

Per titoli: design pulito, dimensioni leggibili in apertura e cover, senza
coprire dipinti o rendere tutto identico. Per il Cinema V6 rispettare il
titolo iniziale e il divieto di testo interno; non alterare Gold Master.

## IMPLEMENTAZIONE REALE DI QUESTA MODIFICA

Il modulo "src/director_reference_v326.py" è gratuito/offline:
- "analyze_scenes" analizza campi opzionali in storyboard;
- "inspect_black_tail" decodifica gli ultimi max 6s di un MP4 con FFmpeg
  e segnala una vera coda quasi nera. Un nero può essere intenzionale:
  richiede visione, non un rifiuto automatico.

INTEGRAZIONI:
- "src/artvision_editor_v19.py" ora invoca analyze_scenes su V19; il rapporto
  "EDITOR_REPORT_V19.json" contiene i fatti V326, mai una "approvazione".
- "src/quality_director_v17.py" ora esegue black-tail scan sul video reale,
  ove presente, e scrive il risultato nel "QUALITY_REPORT_V17.json".
- ".github/workflows/quality-director-v17.yml" testa la regressione V326 e
  consente da Android un input facoltativo "brief_path" per eseguire V19+V326
  insieme al rapporto V17. NESSUN nuovo cron, nuovo provider o deploy del sito.

Prova riproducibile senza nuovi crediti:
    python src/artvision_editor_v19.py \
        --brief templates/ARTVISION_REEL_STYLE_V326_CANDIDATE.json \
        --out output/regia-v326

Dopo un render autonomo già autorizzato:
    python src/quality_director_v17.py \
        --video /percorso/al/video.mp4 \
        --format artvision_cinema \
        --out output/revisione-v326

Test:
    python -m unittest discover -s tests -p 'test_director_reference_v326.py' -v
    python -m unittest discover -s tests -p 'test_artvision_editor_v19.py' -v
    python -m unittest discover -s tests -p 'test_quality_director_v17.py' -v

Il template V326 è solo una PROPOSTA di 24,8s su opere John Martin già citate
nel progetto: non è MP4 prodotto, non è approvato, tutte le fonti/uso
commerciale e la musica richiedono verifica nuova.

## Gate finale non delegabile

- Guardare MP4 vero **con audio**, **muto**, e ascoltare solo audio.
- Confrontare gesto–frase–campo–tempo parola per parola ove narrato.
- Revisione dei primi 3s e dei 3s finali, controllo mobile su Android.
- Preservare fonti e autentica pittura, diritti, varianza rispetto agli
  ultimi 3–5 episodi, fedeltà dei volti, raccordi e credibilità del movimento.
- QA MP4/codec/durata/hash/file leggibile/cover/ZIP/stato reale.
- Se manca approvazione artistica: "rendered_needs_review", NON Gold/publish.

## Cosa resta da fare (non dichiarare già operativo)

Questo V326 non genera nuovi filmati e non integra un nuovo renderer.
Non dimostra né rende "umano" un video mediante sole soglie. I renderer
dell'owner devono produrre storyboard arricchiti e richiamare esplicitamente
V19 prima del rendering perché i campi V326 diventino obbligatori nel loro
percorso. Il QA V17 può controllare i veri master quando viene invocato.
Nessun vecchio lavoro è stato rielaborato o pubblicato da questa modifica.

Non usare nuove API a pagamento o riavviare duplicati di cicli automatici
soltanto per testare una regola editoriale.
