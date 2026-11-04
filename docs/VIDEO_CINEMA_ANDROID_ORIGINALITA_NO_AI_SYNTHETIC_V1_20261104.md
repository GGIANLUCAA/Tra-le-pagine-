# Video cinematografici Android — autenticità, originalità, distribuzione (V1, 04/11/2026)

## Decisione editoriale del proprietario
Il progetto non si limita ai restauri storici o ai quadri: produrre contenuti cinematografici di soggetti nuovi, gestiti da Android e renderizzati sui server. Il proprietario chiede che i video non vengano categorizzati come AI dai social, che siano originali/non banali e abbiano potenziale di diffusione. Il risultato dell'etichettatura e la viralità non sono garantibili e non vanno promessi.

## Regola operativa per i video destinati a un flusso non sintetico
- Per il pilota e gli episodi indicati come **riprese autentiche** usare esclusivamente girato reale, con provenienza documentata, copyright/licenza commercialmente compatibile, taglio editoriale originale e correzioni tradizionali (montaggio, color grading, stabilizzazione, normalizzazione audio) tramite FFmpeg.
- Escludere generazione di scene realistiche tramite Vidu, Wan, LTX, ComfyUI e strumenti simili; escludere modifiche AI sostanziali all'azione o ai soggetti. Non rimuovere metadati per aggirare sistemi di etichettatura; se in altri format si usa generazione o alterazione significativa, dichiararla quando richiesta dalle piattaforme. Uso di AI per brainstorming e storyboard non trasforma automaticamente il girato reale in contenuto video sintetico.
- Non affermare che una piattaforma non assegnerà etichette, né che semplice selezione di clip stock basti a classificare un video come originale. Le policy di Meta danno peso al materiale creato direttamente dal creator o a un apporto creativo/informativo sostanziale: semplice compilazione di clip altrui con musica e titoli può essere declassata.
- Privilegiare girato proprio, esclusivo o con licenza adeguata, o una forma editoriale con contributo originale sostanziale. Conservare proof-of-source (URL, autore, licenza, download timestamp, SHA256) e prove di montaggio.
- Per contenuti storici generativi di altro format mantenere i gate già previsti; non chiamarli riprese originali autentiche inalterate.

## Differenziazione creativa e test di potenziale virale
- Scegliere **un solo avvenimento/angolo raro e preciso** per episodio, non «compilation di stock». Ricercare e scartare materiale già ripetuto, loghi e watermark; non promettere assoluta unicità sul web.
- Prima del render redigere una logline originale, un hook visivo autentico (0–1,5 s), progressione narrativa in 3 movimenti e payoff finale, con sound design coerente. Evitare clickbait falso, eventi montati come se fossero un'unica ripresa quando non lo sono, replay ovvi, filtri generici, sovratitoli invadenti.
- Progettare almeno due montaggi **editorialmente diversi** sullo stesso girato autentico per provare in modo lecito hook, ritmo e copertina, senza copie spam.
- Valutare a posteriori retention 3s, completamento, replay, condivisioni e salvataggi; nessuna promessa di viralità.
- Per social: creatività e veridicità prima degli hashtag. Verificare policy e licenze per ogni piattaforma, non assumere che l'assenza di label equivalga a conformità.

## Pilot approvato come tema: tempeste oceaniche
- Formato di prova: MP4 9:16 da 20–30 s, **riprese reali** e audio/sound design con licenza, senza voce per questo pilota; intro cinematicamente forte, escalation visiva e un finale memorabile. No scene AI realistiche.
- Angolo editoriale candidato: **«The Wave You Never See Coming»**; mostrare una singola evoluzione autentica o più scene chiaramente indipendenti, preferendo POV raro da nave, faro o telecamera costiera. Titolo pubblico breve in inglese, non presentare riprese di eventi diversi come una stessa tempesta.
- Preflight: cercare la fonte meno usata e verificare utilizzo commerciale; se non esistono scene sufficientemente originali ed evidenziabili, non forzare un render di stock banale: cercare altra fonte/soggetto.
- Pipeline prima prova: GitHub Actions + FFmpeg già presenti; browser Android come pannello. Remotion/AI cloud solo se giustificati. Non impegnare spese non verificate. Non pubblicare su social o sito senza specifica autorizzazione.
- La consegna richiede MP4 vero scaricabile con link verificato, copertina, post social, fonti/licenze, ZIP, controllo visivo e audio del video intero. Non chiamare «finito» uno storyboard, un log di CI o un rendering incompleto.

## Fonti policy verificate in data 04/11/2026
- Meta original content, 2026-03-13: https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/
- Meta AI info: https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/
- TikTok: https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content
- YouTube: https://support.google.com/youtube/answer/14328491
