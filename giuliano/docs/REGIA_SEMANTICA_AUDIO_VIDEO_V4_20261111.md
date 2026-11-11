# GIULIANO — Regia sincronizzata con la voce, controllo V4
Data: 2026-11-11. Scopo: eliminare montaggi illustrativi casuali e impedire fotogrammi flash.

## Principi editoriali
- Il soggetto della fotografia deve corrispondere allo specifico significato pronunciato in quel momento, non soltanto al tema generale. Per esempio, quando la voce parla di corde, mostrare mani/corde/movimento; quando parla di ahu, mostrare veri ahu, non statue casuali.
- Preparare uno storyboard **per frase/clausola narrativa**, con finestra vocale verificata e asset autentico, licenza, semantica, inizio/fine visivi, motivo di regia. Non confondere la pubblicazione dello studio (2025) con la data esatta delle riprese sperimentali eventualmente anteriori.
- Le grafiche scientifiche devono mostrare **i dettagli effettivamente citati**: base, inclinazione, centro di massa. Vietato oscurare tali dettagli con sottotitoli o bande.
- Conservare la voce e la colonna sonora approvate quando cambia solo il montaggio. Verificare hash dei pacchetti AAC e/o hash PCM decodificato, e durata audio **integrale** dopo ogni re-mux.
- Niente inserti al limite di 1-6 fotogrammi, immagini residuali o stacchi doppi (due cut a distanza <=0,5s). Verificare il risultato MP4 frame per frame e riparare anche la prima/ultima immagine di ogni clip.
- Durata delle foto definita semanticamente: in media >=2,5 s se sono pensate per essere osservate; eccezioni motivate solo da vera azione o regia. Non costruire 1 foto = 1 frase automaticamente.
- Un filmato del vero esperimento, se disponibile con titolarità verificata, prevale su simulazioni. Non confondere una simulazione con una ripresa autentica. Materiale da un social caricato dall'utente resta **da autorizzare per la pubblicazione**.
- Per il download Android produrre MP4 H.264/AAC 720x1280, una versione leggerissima 480x854 e master 1080x1920, oltre a ZIP e QA.

## Audit dell'episodio Moai
- Base V3: 209,88s, 5.037 frame a 24 fps, 63 inquadrature, 34 blocchi vocali.
- V4: sei sostituzioni complete di durata ~3–6s: (1) ahu 43,75–47,04s; (2) immagini cave/statue abbandonate 47,04–50,17s; (3) diagramma base e inclinazione 74,58–77,58s; (4) persone e corde reali 82,58–88,67s; (5) Lipo/Hunt paper 94,54–98,25s; (6) dimostrazione reale 121,29–124,88s.
- Controllo del master esportato: **54** cut percettivi rilevati, **0** coppie a distanza <=0,5 s dopo la riparazione degli ultimi tre micro-flash.
- Video FullHD e Android totalmente decodificati, audio master AAC + PCM verificato uguale alla V3 approvata, ZIP CRC PASS. Copertura temporale 34/34 blocchi controllata usando la precedente trascrizione allineata (ASR+interpolazione: non equivale ad allineamento fonetico perfetto).
- **Limitazione onesta**: alcuni fotogrammi generali di cava sono contesto visivo, non prova specifica di una statua caduta lungo una strada. Non affermare una corrispondenza letterale se la fonte autentica non lo dimostra.
- File V4 esportati nella conversazione ChatGPT; questo documento GitHub **non contiene** il video binario e non certifica una pubblicazione GitHub/social.

## Regola di accettazione per futuri film
Un QA tecnico 'pass' non autorizza il claim di regia televisiva: è obbligatoria una seconda visione critica dell'intero film con audio e senza audio, e revisione umana del rapporto prova-immagine-narrazione prima della pubblicazione.
