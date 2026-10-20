# ART VISION V5 — UNIVERSAL ATELIER
**Studio audiovisual internazionale, un solo film, opere originali ad alta risoluzione. 20 ottobre 2026.**

## CONTRATTO CREATIVO DELL'UTENTE (VINCOLANTE)

1. **Una sola versione ben fatta** per artista, non generare versioni corta e lunga in parallelo. Per ora mantenere durata film precedente **150 secondi**, fino a nuova indicazione esplicita.
2. **Inizio sempre riconoscibile**: firma grafica elegante immutabile da un episodio all'altro, con solo **NOME ARTISTA** e, in piccolo, **MUSIC BY Nome Compositore**. Non aggiungere altri slogan, spiegazioni o scritte.
3. **Internazionale / indipendente dalla lingua**: zero narratore, zero testi esplicativi, zero testi nella canzone, zero sottotitoli, zero testo di chiusura o invito esplicito al follow. La regia e la musica devono parlare da sole.
4. **Nessun credito tecnico/museale in sovraimpressione**: i nomi delle opere, musei, licenze e credito MUSICA COMPLETO sono conservati in `DESCRIZIONE_SOCIAL.txt`, `CREDITI_E_FONTI.txt`, `MUSICA_LICENZA_E_CREDITI.json`. Devono essere resi accessibili quando richiesto dalla licenza; NON promettere licenza senza attribuzione.
5. **Fotografia digitale di livello museale**: immagini reali e verificabili, preferenza per sorgenti ad alta risoluzione, preservazione colori e proporzioni, cornice ambientale neutra, nessuna pittura AI inventata. Il file verticale 1080×1920 Full HD non è '4K nativo'. Il motore V5 limita automaticamente zoom se la sorgente non ha pixel sufficienti: ingrandire non crea dettaglio.
6. **Regia originale per opera**: alternare 1, 2, 3 dettagli, whole-first, detail-first, occhio al path emotivo; rallentare vicino a volti, gesti, texture, momenti cruciali; niente split-screen, whip, flash, filtri compulsivi e falsi parallassi.
7. **Musica registrata, strumentale, licenza verificata**; brano diverso o ripetuto raramente nel catalogo. Non estrarre l'audio dai video campione. Il piccolo 'Music by' nel film è informativo ma NON sostituisce attribution completa CC BY nella descrizione social.
8. **Nessun obbligo di costo API** e **nessuna pubblicazione automatica**.
9. **Preservare SEMPRE tutte le versioni storiche** V1, V2, V3, V4, base per libri e narrazioni, non fare retrofit distruttivi.

## IMPLEMENTAZIONE
- Preset principale `style=universal_atelier_v5` e modulo indipendente `modules/artvision/universal_atelier_v5.py`.
- Workflow `.github/workflows/artvision-render.yml`; coda `modules/artvision/queue.json`.
- Sonoro di test V5: `Dreams Become Real`, Kevin MacLeod, piano + sintetizzatori strumentali, [scheda ufficiale ISRC USUAN1500027](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027), licenza CC BY 4.0. **Il download deve superare una vera prova tecnica prima di considerarsi operativo.**
- V4 si trova intatto in `atelier_v4.py` (e l'ulteriore regia storica V3 in `harmonic_reveal_v3.py`). Branch backup preventivo `backup-artvision-v4-prima-cinema-universal-v5-2026-10-20`.
- Per ora mappa di dettagli V5 *specifica di Vincent van Gogh*, ereditata da V4. Quando si crea un nuovo artista, va preparata mappa ragionata per immagini diverse; non inventare coordinate e non affermare che V5 supporta qualsiasi artista senza nuovo storyboard.

## CHECKLIST QUALITÀ
- Control frame: opening 0.0s, 1.4s, 3.5s: ARTIST NAME + small MUSIC BY; nessuna ulteriore scritta dentro i quadri né alla fine.
- Verificare autentica attribution in testo social e metadata; nessun copyright bypass.
- Controllare *effettivamente* 1/2/3-details, 2 inquadrature whole-first, ritmo differenziato senza disturbare occhi.
- Minimo 10 opere con foto autentiche e metadata verificati. Niente immagini sostituite da generazione AI.
- Qualità video: MP4 H264/AAC, 1080×1920, 24fps, 150s ±2s; audio senza clipping.
- Misurare pixel dell'originale: sorgente piccola -> nessun macro artificiale, consentire immagine integrale.
- Se il job fallisce, leggere log reale e correggere script con un nuovo test, **non dichiarare MP4 pronto**.
- Solo dopo QA tecnica consegnare una singola versione MP4 più copertina e documenti. Valutazione “magnifico” non si deduce dall'esito verde GitHub, dipende dalla resa artistica e dal giudizio umano.

## IL FUTURO
Rendere V5 più autonoma su nuovi artisti: curatela del soggetto basata su segmentazione/opere e controllo umani, catalogo musicale più ampio, verifica risoluzione source per scene. Non progettare due filmati per lo stesso episodio senza ordine esplicito. Tutti i nuovi upgrade additivi, preservare la capacità di rollback.


## V5 REALMENTE PRODOTTA E VALIDATA — 20 ottobre 2026
- Single final film: Vincent van Gogh, **150.000 sec, 1080×1920, H.264/AAC**, 12 opere autentiche, 49 passaggi diversificati, sola firma artista e piccolo MUSIC BY nei primi secondi; nessun testo nel resto del video.
- [GitHub Actions run #14](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39435930028) SUCCESS, artifact `ARTVISION_14` verificato, MP4 realmente scaricato e cover visionata. Non distribuire la precedente run #13 come versione finale: aveva una copertina eccessivamente vuota.
- Copertina V5 aggiornata: fotografia autentica degli *Irises* avvicinata e pieno schermo, nome artista + MUSIC BY Kevin MacLeod in serif minimale su un velo scuro. Non aggiungere ulteriori testi nel video.
- **Cinque immagini Cleveland Museum migliorate da web JPG 900px a JPEG print originali CC0**: Adeline Ravoux 3400×3389, The Large Plane Trees 3400×2713, Two Poplars 2543×3400, Landscape with Wheelbarrow 3400×2400, Dr. Gachet 2654×3400. Fonte e risultato per immagine in `QUALITA_SORGENTI.json`.
- Nuovo brano, diverso dalla V4: `Dreams Become Real`, Kevin MacLeod, registrazione originale strumentale ~410.07sec da https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreams%20Become%20Real.mp3 ; scheda https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027 ; **CC BY 4.0**. SHA256 `a8ea5df5f969ed8d898af7fe07eb4712233f03e9d83f7ebcc88d1c851f3171b0`. Informazione completa di attribuzione nella descrizione pubblica del post e file licenze; il solo MUSIC BY nel filmato non sostituisce l'attribuzione CC obbligatoria.
- Durata elaborazione V5 con upgrading museale **318,56 s**; 0 API a pagamento, nessuna pubblicazione automatica, dimensione MP4 43.148.391 byte (~41.15 MiB).
- Quality report: 18 dettagli, 17 inquadrature whole, 6 push, 8 reveal; 5 opere con multipli dettagli, 2 con tre dettagli, 6 che iniziano dal quadro intero. Contatto regia allegato, H264/AAC e durata controllati; **success tecnico NON garantisce valutazione estetica perfetta**.
- A differenza di V1–V4, la V5 introduce un limite zoom in base ai pixel sorgenti, evita macro estremi su immagini sfocate e conserva accuratamente i colori. Può diminuire la spettacolarità degli zoom quando i master sono piccoli: è una scelta a favore della qualità museale.
- Git branch `backup-artvision-v4-prima-cinema-universal-v5-2026-10-20`, precedenti motori e workflow narrati conservati.
- FUTURI ARTISTI: costruire e verificare prima un piano soggetti e dettagli specifico; attualmente la mappa esplicita implementata per V5 è di Van Gogh. Non dichiarare altri artisti supportati automaticamente se il piano non è stato preparato.
