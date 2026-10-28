# ArtVision 4x1 — contratto operativo (28 ottobre 2026)

## Scopo
Per ogni nuova opera selezionata, preparare **quattro varianti** da un unico dossier verificato, senza considerare un piano come produzione completata:
1. Critico Standard: copertina standard, voce naturale Gacrux verificata, narrazione sincronizzata, ingresso standard.
2. Critico Museum: stessa narrazione e stessa voce, Museum Immersion con ingresso e ritorno alla medesima sala.
3. Cinema Standard: senza voce, musica verificata, regia Cinema V6 sui dettagli.
4. Cinema Museum: stesso impianto artistico/musicale del Cinema, ma ingresso e uscita museale V46.

Questo contratto **integra**, non sostituisce, AGENTS.md, docs/REGOLE_ATTIVE.md, V20/V23/V25/V28/V31/V32/V44/V46 e i preset. La richiesta specifica dell'utente prevale.

## Sequenza eseguibile
1. **Preflight**: consultare coda, catalogo, hash e lavori in corso; evitare duplicati, collisioni e sovrascritture. Se scelta libera, confrontare almeno 3 opere (V32). Conservare ID opera e fonti.
2. **Dossier madre**: museo e misure in cm dalla fonte primaria, riproduzione autentica e licenza, ricerca della cornice realmente documentata, scala rispetto a visitatore e sala; separare documentazione da ricostruzione. Registrare provenienza e licenza della specifica registrazione musicale, non solo della composizione.
3. **Piano**: quattro storyboard distinti e due coppie con contenuti coerenti; la variante Museum deve aggiungere un'esperienza visiva vera, non una semplice cornice appiccicata. Nessuna durata o numero di scene fisso. Il momento wow deve aggiungere significato.
4. **Asset e voce**: acquisire una volta sola gli asset leciti e riusarli; Critico: voce Gacrux realmente generata e ascoltata, non AAC vuoto o TTS sostitutivo. In assenza di voce verificata, segnare Critico bloccato e non convertirlo in Cinema.
5. **Render**: MP4 9:16 H264/AAC, cover JPEG, primo fotogramma con titolo inglese esatto e artista secondo template master approvato; nessun testo sovrapposto alle scene. Confrontare la copertina master prima del render. Nessun credito video IA a pagamento senza autorizzazione specifica per singola chiamata.
6. **Museum gate**: scala fisica e cornice documentate o dichiarate ricostruite; quadro dietro battuta interna, ombre e prospettiva; entrata e uscita dalla stessa sala; verificare tutti i bordi e fotogrammi intermedi, niente edge-stretch, strisce, ghosting, salti o deformazioni. Confrontare Cyclops SENZA STRISCE e Hiroshige Museum Scale realmente recuperati; se indisponibili non dichiarare confronto effettuato.
7. **Consegna per variante**: quattro post italiani autentici e differenti (Facebook, Instagram, TikTok, YouTube) secondo V28, copertina, MP4, storyboard, ricetta JSON, dossier editoriale, fonti e diritti, QA e ZIP. Quindi 16 post per quattro video, salvo esplicita richiesta diversa.
8. **QA**: ffprobe, decodifica integrale, audio ascoltato, visione a velocità normale su smartphone, copertina e primo frame confrontati, integrità ZIP e verifica reale dei percorsi Android. Il QA tecnico non è approvazione artistica. Usare V44 quando applicabile. Ogni variante ha stato indipendente: planned / blocked / rendered_needs_review / approved_for_final_delivery, con hash reale.
9. **Autocritica**: registrare 2–3 difetti specifici osservati per ciclo e una correzione misurabile per il ciclo successivo; non inventare risultati di social né auto-promuovere Gold Master.
10. **Distribuzione**: nessuna pubblicazione social automatica, nessun costo, nessuna API video a pagamento implicita. Registro aggiornato solo per file effettivamente creati e verificati.

## Regola di fallback
Se una delle quattro varianti non è producibile, mantenere separatamente lo stato delle altre; non consegnare una copia rinominata come variante diversa e non dichiarare il gruppo completo. La qualità prevale sulla cadenza di tre ore.

## Direzione emotiva obbligatoria — V1 (28 ottobre 2026)
Questo è un **gate di progettazione**, non una promessa di viralità o un punteggio di bellezza calcolabile.

Per ogni opera il dossier madre deve contenere una `emotional_direction` verificabile:
- `central_tension`: il contrasto umano, storico o visivo che rende l'opera interessante, fondato su ciò che si vede e sulle fonti.
- `intended_feeling`: una o due emozioni principali (meraviglia, inquietudine, tenerezza, malinconia, tensione, ecc.), non un elenco generico.
- `evidence_details`: almeno tre dettagli specifici dell'opera con posizione/descrizione, fonte dell'immagine e significato; se un dettaglio è interpretativo dichiararlo.
- `reveal_order`: ordine motivato di scoperta, dal primo stimolo alla rivelazione e alla chiusura; evitare di mostrare subito tutto se distrugge la sorpresa.
- `visual_audio_cues`: per ogni scena dettaglio reale, emozione cercata, movimento motivato, durata indicativa, musica/pausa e, nei Critico, frase esatta con timecode verificato.
- `wow_justification`: quale nuova comprensione produce il momento più forte, non soltanto quale effetto usa.
- `four_variant_delta`: perché le due varianti Standard e Museum aggiungono esperienze diverse pur mantenendo fatti, voce e messaggio coerenti.

**Gate pre-render:** rifiutare storyboard che contengano solo "zoom", "pan", "wow", "epico" senza dettagli identificati e funzione narrativa. Nessuna immagine riempitiva, tagli arbitrari, primi piani troppo degradati o passaggi che contraddicono la voce. Per la variante Museum l'entrata/uscita deve rafforzare la scoperta, non ritardarla inutilmente.

**Gate dopo render:** rivedere l'intero video a velocità normale, anche senza audio per controllare la leggibilità del percorso visivo; poi con audio per verificare tensione, pause, enfasi e raccordi. Annotare almeno un punto che emoziona o sorprende *per una ragione spiegabile* e 2–3 debolezze concrete. Se non emerge alcuna progressione significativa, stato `rendered_needs_review`, mai Gold Master automatico.

**Apprendimento:** registrare i feedback dell'utente e, quando disponibili, dati reali di retention, completamento, salvataggi e condivisioni per variante. Confrontare ipotesi e risultati senza inventare metriche; modificare poche variabili per ciclo. Le emozioni non si certificano con ffprobe o con un algoritmo.

## Estensione V55 — apertura e consegna obbligatoria per ogni variante

Ogni variante deve avere `opening_0_7` specifico: primo frame con titolo/artista, particolare originale visivamente riconoscibile, gancio 0–3 s, scoperta 3–7 s, crop leggibile su telefono e cue audio coerente. Nelle versioni Museum non dedicare tutta l'apertura a un corridoio ripetitivo: il museo è un mezzo per rivelare la scala e la presenza reale dell'opera. In Critico preservare la narrazione studiata, in Cinema la regia musicale. I momenti iniziali devono avere contenuto autentico, non un mero cambio di effetti.

**Consegna per ognuno dei 4 MP4, separata:** creare con `src/artvision_delivery_v55.py pack` MP4, cover JPG, quattro POST_*.txt distinti, fonti/diritti, ricetta e ZIP integrale. Guardare il foglio `APERTURA_PRIMI_7_SECONDI.jpg` e il film a velocità reale; registrare la valutazione nel template `templates/ARTVISION_OPENING_REVIEW_V55.json` con SHA256 vero. Mantenere stato di **distribuzione** separato dallo stato **artistico**. Importare al più presto sul sito archivio personale con percorso realmente disponibile, senza pubblicazione social; dichiarare `archive_sync_pending` quando non provato. I link di ChatGPT sono ammessi solo dopo creazione/verifica del percorso reale in quella sessione; salvare anche ZIP per Android. Il sito ha ZIP dinamico firmato: provarne la disponibilità nella scheda, non creare doppioni permanentemente.

## Implementazione V54 — comandi reali e limiti dei controlli (28/10/2026)

**Creazione senza spesa del gruppo e delle quattro schede V13 collegate:**

```bash
python src/video_director_v13.py four-brief --topic "The Goldfinch" --artist "Carel Fabritius" --out output/fabritius/ARTVISION_4X1_PLAN.json
```

Crea **un solo** `output/fabritius/ARTVISION_4X1_PLAN.json` e quattro sottocartelle con `PROJECT_V13.json` separati (`critico_standard`, `critico_museum`, `cinema_standard`, `cinema_museum`). Ogni scheda V13 usa `artvision_4x1_plan=../ARTVISION_4X1_PLAN.json`, `serial_mode=artvision_4x1` e `artvision_4x1_variant` corretto. **Non vengono creati MP4, voce, musica, immagini, ricerche né approvazioni**; i campi sono intenzionalmente vuoti. Non sovrascrivere cartelle già esistenti.

**Preflight prima dei renderer:**

```bash
python src/video_director_v13.py four-check --plan output/fabritius/ARTVISION_4X1_PLAN.json
python src/video_director_v13.py check --project output/fabritius/critico_standard/PROJECT_V13.json
```

Ripetere il secondo comando per tutte le varianti; il normale `check` include il controllo condiviso 4x1 quando la scheda dichiara la modalità seriale. Il check strutturale **non certifica che le fonti siano vere, che la voce sia stata ascoltata o che la resa sia emozionante**. I passaggi di produzione effettiva seguono gli adapter e renderer V6/V2 esistenti. In caso di blocco riportare precisamente l'elemento mancante.

**Autocritica su un MP4 reale, dopo averlo davvero visto e ascoltato:**

```bash
python src/artvision_learning_loop_v1.py record --review REVIEW.json --video VIDEO.mp4 --ledger output/artvision_learning.jsonl
python src/artvision_learning_loop_v1.py next --ledger output/artvision_learning.jsonl
```

Usare `templates/ARTVISION_4X1_SELF_CRITIQUE_V1.json` come scheda vuota. Collegare almeno due difetti a secondi concreti, gravità, ipotesi di causa, correzione e metodo di verifica; **il tool verifica hash e caratteristiche MP4 con ffprobe, ma non visiona il filmato**. Niente autocritiche finte, niente modifica automatica di master approvati e nessun rating artificiale presentato come previsione di viralità. La lezione proposta è un'ipotesi da confrontare su un nuovo MP4, mai una prova di qualità raggiunta.

**Coda:** `queue/artvision_four_variants_s01_20261028.json` conserva separatamente le quattro varianti per opera. Le voci ereditate dalla precedente coda V53 sono riferimenti storici da riverificare, non attestazioni di consegna. Le due automazioni produttive già esistenti devono evitare sovrapposizioni.


## Consegna V55 — requisito per ognuna delle quattro varianti (28 ottobre 2026)

**Nessuna variante si considera consegnata** se mancano MP4 H264/AAC valido e decodificato, copertina JPEG coerente con il primo frame, 4 post V28 originali, fonti/licenze e ricetta, ZIP completo con CRC e hash, file effettivamente reperibili nella chat e scheda completa su Video Library Studio verificata. Un lotto 4x1 completo ha quattro kit autonomi (4 MP4 + 4 copertine + 4 ZIP completi + 16 post), senza duplicare i master per convenienza.

Usare `src/artvision_delivery_v55.py pack --video ... --cover ... --facebook ... --instagram ... --tiktok ... --youtube ... --rights ... --recipe ... --out ... [--opening-review ...]`. Il comando è solo locale, verifica codec, decodifica integrale, JPEG, unicità dei testi e CRC/MP4 in ZIP, estrae fotogrammi reali a 0.1, 1, 3, 5 e 7 secondi; **non importa sul sito e non certifica accessibilità ChatGPT**. Il file `DELIVERY_STATUS_V55.json` distingue le verifiche non fatte e i blocchi dell'apertura. Controllare visivamente il filmato e la sincronizzazione col parlato prima di compilare l'eventuale review.

**Apertura diversa per opera e per variante:** il primo secondo deve già comunicare identità e qualità; entro 3 secondi una domanda visiva vera o un particolare sorprendente deve fermare l'occhio; entro 7 secondi dare un primo avanzamento narrativo. Le scene Museum non devono iniziare con inutili secondi di corridoi vuoti. Adattare ritmo e struttura all'opera, evitando un identico stampo per ogni video.

La sincronizzazione al sito è un evento separato. Esigere una verifica del catalogo/cover/dossier/ZIP privato quando disponibile, non inventare il successo né link permanenti. Nessuna autopubblicazione social e nessuna chiamata video IA pagata.

