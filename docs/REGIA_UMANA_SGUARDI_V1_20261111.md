# REGIA UMANA / SGUARDI V1 — riferimento di qualità (11 novembre 2026)

## Mandato del proprietario
Il video fornito dal proprietario `57505.mp4` («Sguardi in camera») è il riferimento stilistico positivo per i prossimi contenuti: voto visivo **9,2/10**. Usare i **principi** di regia, NON la sua colonna sonora, le immagini, il testo o una formula visiva identica. Obiettivo: video credibili, umani, affascinanti, senza riconoscibili tic di montaggio AI.

## Cosa è stato effettivamente misurato nel riferimento
- File verticale 720×1280, 25fps, 62,08s, audio stereo HE-AAC.
- Circa 24 segmenti visivi prima del cartello promozionale; mediana indicativa dei segmenti 2,2s. NON usarla come durata fissa.
- Apertura su obiettivo, finale sull'occhio: una rima visiva motivata.
- Percorso narrativo: tecnologia -> gesti e famiglia -> collettività -> singoli volti.
- Il finale promozionale di circa 6s appare eccessivo per uno short indipendente.
- La valutazione artistica della musica/voce nel file NON è stata convalidata con un ascolto critico separato: non inventare giudizi di timbro o strumenti.

## Principi operativi per OGNI video
1. **Prima regia, poi renderer**: una frase descrive l'idea unica, la scoperta umana e la relazione tra primo e ultimo fotogramma.
2. **Ogni scena fa un lavoro**: rivela un fatto/gesto, cambia prospettiva, fa respirare, prepara il payoff. Scartare materiale riempitivo anche se bello.
3. **Tagli semantici**: tagliare quando cambia gesto, significato o bisogno percettivo; non ogni N secondi.
4. **Controcampo umano**: alternare persone, dettagli concreti e contesto, evitando macro/zoom automatici ripetuti.
5. **Soggetto originale preservato**: veri filmati in movimento o scansioni documentate; AI soltanto dove giustificata e distinguibile, mai attribuita alla ripresa originale.
6. **Voce**: frase concreta e naturale, respirazione/pausa adatta, niente chiusa filosofica automatica o domanda obbligatoria. Applicare V320/V321, non annullare gli audio già approvati.
7. **Musica**: accompagna anziché guidare artificialmente ogni taglio; niente boom/drone da trailer sempre uguale, finali sonori motivati, voice mix intelligibile.
8. **Motivo visivo**: un dettaglio può ritornare trasformato al finale, ma non ripetere sistematicamente «lente → occhio», la stessa battuta, o lo stesso cartello.
9. **Camera**: movemento reale prioritario; pan/zoom solo per ragione narrativa, continuità fisica e stabilità del soggetto. Preservare identità, proporzioni, cornici e spazi.
10. **QA artistico**: vedere l'MP4 vero per intero **con audio**, **senza audio** e ascoltare **solo audio**, confrontarlo al riferimento e agli episodi recenti; verificare ritmo, umanità, ripetizioni, dettagli pronunciati/ripresi.
11. **Consegna**: validare hash, lettura completa/codec H264+Aac, link Android reale, copertina e testo social; master tecnico `rendered_needs_review` finché non ha superato il giudizio artistico.
12. **Stop regressioni**: non alterare master già approvati, Gold, queue owner, identità storica, V80/V94/V96/V99, divieti di pubblicazione.

## Applicazione per formato
- **La Storia Rivive**: senza voce; 14–35s, filmato storico reale in movimento, transizione B/N→colore entro 1–1,4s **soltanto se esiste un vero restauro cromatico**; non tingere una pellicola monochrome e chiamarla «colorizzazione reale». 4+1 e benchmark V99 continuano a valere. Il montaggio sperimentale di filmati autentici in B/N è un **format di studio separato**, NON un sostituto del 4+1 validato.
- **ArtVision 4×1**: tempi più contemplativi, parole esattamente collegate ai dettagli dell'opera; scene Museum con sala/cornice realistica, ingresso/uscita coerenti e cornice fuori dai dettagli; preservare quattro varianti e audio Critico comune alle due Critico.
- **WOW LAB e documentari**: adattare il ritmo all'azione concreta e alla scena; nessuna ricetta che produca episodi tutti uguali.

## VIDU: usare crediti con intelligenza
Il proprietario **autorizza l'uso dei crediti già disponibili** per migliorare artisticamente video e movimento, ma non autorizza acquisti automatici di nuovi crediti, abbonamenti o addebiti non quantificati.

**Non confondere** credito dell'abbonamento Vidu consumer con saldo API: sono canali diversi. Usare il gateway esistente `requests/vidu/*.json` per `balance`, poi `plan` gratuito, e `generate` soltanto dopo preventivo, materiale originale verificato, codice e tetto di spesa del piano, con deduplica e un solo POST; in caso di errore ambiguo recuperare via GET, mai reinviare la generazione. Se la scena ha già movimento storico credibile, Vidu NON è automaticamente un miglioramento. Preferire 1–2 clip per episodio solo quando l'effetto è realmente superiore.

## Primo esercizio operativo
Workflow isolato `.github/workflows/regia-umana-1895-film-pilot.yml`: un MP4 completo da cinque filmati pubblicamente catalogati dei Lumière (1895), con storyboard sei scene e audio originale. Produzione sperimentale distinta dal master storico V99 e da ArtVision owner; nessun video/sito/social viene automaticamente pubblicato, nessun credito Vidu viene addebitato. QA tecnico e review artistica sono distinti.
