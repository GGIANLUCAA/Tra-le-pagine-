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
