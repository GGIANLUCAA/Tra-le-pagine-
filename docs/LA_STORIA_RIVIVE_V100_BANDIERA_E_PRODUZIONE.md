# La Storia Rivive — Addendum V100: bandiera storica, regia e produzione prudente (30/10/2026)

## Ambito e precedenza
Questa guida integra V94/V96/V98/V99, NON sostituisce i gate esistenti, NON modifica ArtVision 4×1 o WOW LAB e NON autorizza pubblicazione, nuovi acquisti o bypass dei diritti. Il benchmark San Francisco 1906 V98 resta il minimo accettabile; un PASS tecnico non equivale ad approvazione artistica.

## Bandiera nel titolo
- Mostrare una **piccola bandiera accanto al luogo e all'anno** (esempio: 🇫🇷 PARIS · 1936) con tipografia elegante e discreta, senza coprire volti, veicoli o oggetti.
- Scegliere la bandiera in base all'entità storica documentata all'epoca delle riprese. Non applicare automaticamente la bandiera nazionale moderna a imperi, colonie, territori contesi o Stati non ancora esistenti.
- Nel dossier conservare country_at_capture, historical_polity, flag_source, flag_era, confidence e decision. Se il contesto è incerto o controverso, omettere la bandiera e conservare soltanto luogo/anno verificati.
- Verificare la resa grafica reale delle emoji su FFmpeg/renderer: preferire un asset vettoriale PNG/SVG con licenza verificata e rapporto proporzioni corretto, senza sostituire silenziosamente con un quadratino o un emoji non supportato.
- Non fare grandi barre opache: rispettare il limite V96 per l'area titolo e le safe zone social; verificare sui fotogrammi del MP4 reale. Bandiera e titolo devono rimanere leggibili ma subordinati alle immagini.

## Produzione e qualità
- Cadenza desiderata: **un ciclo ogni tre ore**, massimo teorico 8 al giorno, non promessa di output. Se il video precedente è in review o mancano fotografie HD fedeli, non consegnare contenuti mediocri per rispettare la cadenza.
- Prima di spendere: selezionare almeno 3 fonti candidate, controllare diritti PD/CC0 del singolo filmato, qualità nativa e timecode esatto. Conservare SHA, frame autentico, crop e tracciabilità dei restauri.
- Per il formato attuale conservare il preset V99 **4 fotografie I2I autentiche + 1 clip Vidu source-locked**, con confronto contro il video V98. L'utente permette di valutare **fino a 2 sequenze Vidu** solo quando il valore artistico è superiore, ma una seconda clip richiede prima aggiornamento esplicito di preset/gate e verifica dei costi/autorizzazioni: non aggirare il vincolo attuale di una sola richiesta fatturabile/episodio.
- La fotografia restaurata deve essere realmente nitida, fedele a persone, vestiti, oggetti e geometrie: niente DDColor-only o semplice upscale cosmetico. Scartare la scena se la fonte è troppo povera per preservare i tratti.
- Regia adattiva: B/N originale in movimento → freeze sul fotogramma esatto → foto I2I a colori, hold leggibile; Vidu deve proseguire dallo stesso frame e avere vero movimento a colori. Niente filmati da prospettive diverse, hold lunghi ripetitivi, palette arancione incongruente, o titoli grandi. Apertura forte e chiusura emotiva, durata non obbligatoriamente identica.
- Audio con licenza verificata e continuo; verificare livelli, sincronizzazione, fade, assenza di clipping e compatibilità con la piattaforma.
- Per ogni asset registrare fonte URL, autore, diritti, data consultazione, termini per uso/pubblicazione, SHA e modello usato. Separare l'originale storico dalla ricostruzione AI e dichiararlo nel post.
- API: controllare quote e limiti effettivi di ChatGPT/API, Finegrain, HF, Vidu e altri provider senza esporre segreti; ledger crediti e idempotenza. Nessun acquisto automatico. Rispettare la policy V94 e il gateway Vidu per eventuali crediti prepagati; non equiparare abbonamento web a consumo API gratuito.
- QA finale: V91+V94+V96+V99, controllo visivo reale volto/oggetti, confronto con V98, H264/AAC, risoluzione reale, audio, file apribile su Android, cover, post con contesto storico/fonti e disclosure AI, ZIP completo, hash e link realmente verificato. Non dichiarare pubblicato un file solo perché renderizzato.
- Autocritica: annotare difetti specifici, fotogramma e causa; sperimentare una modifica alla volta, confrontare A/B e promuovere solo miglioramenti misurabili senza regressioni. Nessuna approvazione umana inventata.

## Checklist di attivazione non ancora completata
Verificare scheduler cloud e lock anti-doppia esecuzione, capacità giornaliera foto I2I, costo effettivo Vidu, asset grafico bandiera con licenza, test renderer Unicode/PNG, diritti dei filmati e pubblicazione separata. Questo documento non equivale all'attivazione dell'automazione ogni 3 ore.
