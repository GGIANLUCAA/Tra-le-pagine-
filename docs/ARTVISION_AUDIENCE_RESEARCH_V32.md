# ARTVISION V32 — Audience & Creative Research
**Approvato dall'utente il 25 ottobre 2026.** Regola **SEMPRE** per ogni nuova produzione ArtVision Cinema, Critico e Collection (variante Cinema), prima della scelta definitiva del soggetto e prima del render. Fonte unica delle priorità: `docs/REGOLE_ATTIVE.md` + `config/editorial_rules.json`; questo documento è il manuale operativo, non un nuovo preset. Non modificare master V6, Critico V2, filmati o copertine esistenti.

## Perché
Non produrre un quadro solo perché è bello, celebre o già in archivio. Identificare una ragione umana documentabile per guardarlo (curiosità, emozione, bellezza, tensione, storia reale, particolare inatteso); far nascere **la regia da quella ragione e dall'opera**. Nessuna promessa di viralità o statistiche inventate.

## Prima di ogni filmato: mini-ricerca obbligatoria
1. Recuperare catalogo e ultime consegne, evitandone i doppioni. Definire il pubblico e la promessa editoriale, non un trucco di engagement.
2. Valutare **almeno 3 opere o temi distinti**, con autore, titolo, forza del primo fotogramma, motivo d'interesse umano, storia e fonte museale, riproduzione e diritti, originalità rispetto al catalogo, possibilità di costruire un arco cinematografico. Quando accessibili e utili, ampliare la scoperta a circa **10–20 candidati** prima di ridurre a 3; questo non è un obbligo di ricerca artificiale per ogni ciclo e non deve rallentare per riempire una quota.
3. Cercare segnali pubblici realmente accessibili: Google Trends (domande/tendenze, confronti con termini coerenti), YouTube (temi e interesse documentabile), Facebook/Instagram/TikTok (campioni di contenuti pertinenti e **solo metriche visibili**), Reddit/ricerca culturale, musei e archivi. Separare fonte culturale da dati di interesse. Scrivere URL, data di controllo, parole chiave, luogo/lingua e osservazione. Non chiamare `trend` una intuizione o un contenuto con molti like fuori contesto.
4. Se un servizio è bloccato, richiede login, è a pagamento o non mostra metriche affidabili, segnare il segnale come `unavailable` con motivo, **non inventare numeri o virali**. Continuare usando fonti museali, valore artistico e ipotesi qualitative dichiarate tali. Nessun acquisto o scraping elusivo.
5. Selezionare un'opera dal confronto motivando interesse umano, apertura, filo conduttore, regia, scelta musicale, finale e limiti. Non scegliere un'opera con diritti non chiariti solo perché ha punteggio alto.
6. Preservare nel `editorial_plan.audience_research` del `PROJECT_V13.json`: `candidates` (min 3), `selection_mode` (`research_selected` o `user_specified`), `explicit_user_instruction` (solo nel secondo caso), `selected_work`, `selection_reason`, `viewer_interest`, `creative_direction`, `signal_limitations`, `analytics_feedback`. Per ogni candidato: `artist`, `work`, `visual_hook`, `human_interest`, `historical_anchor`, `asset_rights_notes`, `comparison_reason`; `audience_signal` ha `status: verified` con `reference`, `observation`, `checked_on`, oppure `status: unavailable` e `reason`.
7. Salvare anche un report di episodio `AUDIENCE_RESEARCH_V32.json` (copia approfondita delle scelte/URL/fonti) nel pacchetto quando il flusso di produzione lo permette. Il file non è una prova indipendente della verità dei segnali, serve alla verifica editoriale.
8. Prima del render, `src/video_director_v13.py check` e il controllo condiviso `src/editorial_rules.py` rifiutano nuove schede ArtVision senza confronto documentato. Flussi che bypassano V13/V16 **devono applicare manualmente la stessa regola**; non dichiarare integrati renderer non toccati.

## Scheda di valutazione (100 punti, stima interna, NON statistica di mercato)
| Aspetto | Max |
|---|---:|
| Interesse osservato del pubblico | 25 |
| Forza visiva immediata | 20 |
| Storia e curiosità autentiche | 20 |
| Potenziale di regia | 15 |
| Originalità rispetto al catalogo | 10 |
| Qualità delle fonti, immagine e diritti | 10 |

Il giudizio editoriale non è una predizione delle visualizzazioni. Se i segnali del pubblico non sono accessibili, assegnare `non valutabile` alla dimensione interesse osservato: non sostituirla con falsi valori. Confrontare anche i limiti e i rischi, non solo il totale.

## Feedback WOW — 28 ottobre 2026

Dopo il video Van Eyck V53 l'utente ha apprezzato la realizzazione e la cornice, ma vuole **opere molto più sorprendenti da guardare**. Per le nuove scelte libere ArtVision dare priorita al soggetto visivamente straordinario PRIMA della messa in scena museale.

Confrontare >=3 candidati non duplicati. Provare in piccolo sul telefono l'immagine d'insieme; indicare cosa incuriosisce nei primi 1–3 secondi, quale particolare cambia la lettura, che storia vera sostiene la scoperta e se il 9:16 conserva il soggetto. Alternare grande spettacolo, mistero, meraviglia, stranezza e bellezza senza ridurre tutto a soggetti cupi. Un quadro storicamente importante non e automaticamente una buona scelta per il format WOW. Se l'opera e imposta dall'utente rispettarla.

Registrare qualitativamente: phone_first_frame_hook, discovery_detail, visual_distinctiveness, narrative_turn, frame_source, artwork_scale, rights, duplicate_check, editorial_risks. Niente promesse di viralita, KPI inventati o scorciatoie sulle fonti e sui diritti. Restano obbligatori V28, V44, V46 e il divieto di API video a pagamento senza approvazione.

## Regia costruita sul contenuto, non stampino
- **Mistero / molti dettagli:** rivelazioni scandite, collegamenti leggibili, pause sui simboli documentati.
- **Emozione / relazione umana:** prossimità e distanza motivate, respiro, musica coerente, durata senza riempitivi.
- **Paesaggio / sublime:** campi ampi e contemplazione, proporzioni protette, pochi movimenti.
- **Conflitto / storia:** prima il gesto decisivo, poi il contesto e le conseguenze documentate.
Sono esempi, **non nuovi preset obbligatori**. Per ogni filmato indicare: perché quel primo fotogramma, cosa imparare o sentire al secondo 3–7, quali dettagli sono pertinenti, perché ciascun raccordo esiste, che cosa chiude l'arco. Tenere conto di diritti, fotografia, voce/musica e format. Rispettare no ghosting, 0/1/3/5/7, tre raccordi e finale, ritmo naturale, V6/V2 e V20/V28.

## Dopo la pubblicazione (quando ci sono dati autentici)
Registrare per video/piattaforma: data, dimensione del campione e fonte; retention iniziale, durata media, completamento, condivisioni/salvataggi quando accessibili; distinguere ipotesi iniziali da osservazioni e non confrontare senza tener conto di durata, lingua e distribuzione. Proporre **una miglioria alla volta** per capire cosa cambia. Senza pubblicazione o accesso Analytics: `not_yet_published` / `not_accessible`, mai KPI inventati.

## Ambito e limiti
La ricerca del pubblico è **permanente**, ma non può ribattezzare un Critico come Cinema o forzare una voce sintetica scadente; alternanza A/B/C quando realmente fattibile. Le richieste specifiche dell'utente prevalgono sulla selezione automatica. Se l'utente impone un'opera, compilare `selection_mode: user_specified`, `explicit_user_instruction` con la richiesta effettiva, almeno un candidato reale e la ricerca del suo possibile interesse; non imporre tre opere diverse né cambiare il soggetto richiesto. La selezione libera mantiene invece il minimo di tre candidati. Non modificare i filmati già approvati. Nessun servizio a pagamento, nessuna pubblicazione automatica e nessuna garanzia di successo.
