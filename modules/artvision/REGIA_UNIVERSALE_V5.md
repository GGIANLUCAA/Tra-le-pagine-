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
