# ArtVision Critico — Produzione in serie V2 (4 episodi, 21 ottobre 2026)

**Sistema additivo e indipendente**. Non sostituisce né modifica i video libri, Van Gogh, Caravaggio, Dalí, Picasso, Munch e Vermeer.

## Prima produzione — quattro film

- `leonardo_gioconda.json` — Leonardo, *La Gioconda*, 407 parole, 8 tappe visive;
- `klimt_bacio.json` — Klimt, *Il Bacio*, 476 parole, 9 tappe;
- `hokusai_grande_onda.json` — Hokusai, *La Grande Onda*, 565 parole, 11 tappe;
- `botticelli_venere.json` — Botticelli, *La Nascita di Venere*, 411 parole, 8 tappe.

Il minutaggio finale non viene inventato: si ricava dalla traccia vocale reale. Un unico narratore Google Gemini Gacrux viene tentato per primo, con fallback Edge dichiarato nei metadata. Musica sottofondo CC BY 4.0: Kevin MacLeod, Night on the Docks – Piano; citazione e licenza accompagnano ogni film.

## Nuovo design universalizzabile (COVER V2, FISSATO)

- Copertina verticale 1080×1920 unica: sfondo scuro, tela reale incorniciata, sottile linea dorata, **solo titolo dell'opera più grande** + **nome artista**.
- Niente frase esca, niente `Tra le Pagine`, niente `ArtVision Critico`, niente `MUSIC BY` stampato sul video. Così non si producono testi italiani da cancellare manualmente quando si traduce.
- Identità visiva invariabile tra i 4 episodi. Titolo localizzabile da `artwork`, artista da `artist`, voce da `beats[].speech`.
- Durante il video, solo autentica immagine dell'opera, zoom ancorati ai dettagli descritti, dissolvenze morbide; **nessuna didascalia o titolo sezione**.
- A fine film, solo due simboli piccoli non verbali per like e iscrizione.
- Per dipinti larghi: vista integrale dell'opera sopra e macro dettaglio sotto, per non ridurre il quadro a un ritaglio. Per ritratti: inquadratura ampia, con movimenti su volto/mano/sfondo e visione intera conclusiva.

## Produzione

Renderizzatore: `render_series_v2.py`.

Avvio dal telefono: GitHub repository `GGIANLUCAA/Tra-le-pagine-` → Actions → `ArtVision Critico V2 - Serie di quattro opere (multilingua ready)` → Run workflow.

I 4 job indipendenti producono 4 artifacts separati; ciascuno contiene:
`ARTVISION_<ID>.mp4`, `COPERTINA.jpg`, `COPIONE_IT.txt`, `REGIA_SINCRONIZZAZIONE.json`, `DIRITTI_E_FONTI.txt`.

Solo dopo il successo di FFprobe (2 tracce audio+video, Full HD, file non vuoto) il master viene archiviato. NESSUNA pubblicazione automatica.

## Multilingua futura

Non bruciare sottotitoli né frasi italiane nel master.
Ogni lingua potrà:
1. mantenere esattamente scene, crop, stile e musiche;
2. sostituire il testo pronunciato con traduzione controllata e voce target;
3. rigenerare la sola intestazione titolo sulla copertina attraverso la traduzione di `artwork`;
4. sincronizzare gli stessi dettagli ai nuovi tempi della recitazione.

Non tradurre acriticamente i titoli di opere storiche: utilizzare il titolo con cui sono note nella cultura target.

## Origine / diritti

I quattro originali scelti sono pubblici domini in Italia (Leonardo, Klimt, Hokusai, Botticelli). Le riproduzioni derivano da Wikimedia Commons e hanno link specifici nei JSON; controllare le licenze/condizioni specifiche della fotografia e nei paesi di destinazione. La licenza della musica richiede attribuzione e indicazione delle modifiche. Rispetto delle condizioni e delle quote Google di sintesi vocale.

## Estensione V53 — Critico per nuove opere, abbinato al Cinema (28/10/2026)

Per la produzione a coppie leggere `docs/ARTVISION_PRODUZIONE_A_COPPIE_V53.md` e `queue/artvision_dual_format_s01_20261028.json`. Il renderer esistente accetta ora una **configurazione JSON preparata per una nuova opera** senza introdurre nuove identità editoriali e senza alterare i vecchi episodi:

```bash
python modules/artvision_critico/production_series/render_series_v2.py --config queue/configs/wright_air_pump_critico.json --require-gacrux
```

Il percorso è **solo un esempio di invocazione**, non prova che tale file già esista. Creare il JSON e verificarne immagini/diritti, copione italiano originale (beats con `speech`, `focus`, `zoom_start`, `zoom_end`), fonti, musica e dettagli prima del render. Il JSON deve comprendere `id`, `artist`, `artwork`, `commons_title`, `image_ratio_min`, `image_ratio_max`, `sources`, `beats`, `music`; si può usare un episodio storico come **schema tecnico**, NON come copione standard. Il renderer non effettua da solo le verifiche storico-artistiche.

Il comando `--config` **impone la voce Google Gacrux reale**: senza `GEMINI_API_KEY`, o se il tentativo termina su Edge, il render viene bloccato anziché dichiarare Critico un video con voce diversa. Le vecchie invocazioni `--episode id` rimangono compatibili; `--require-gacrux` è disponibile anche lì. Non sono approvati automaticamente usi a pagamento del TTS o della generazione video. Dopo il render sono ancora necessari ascolto, sincronizzazione, post V28, QA V44, ZIP e revisione artistica. Non assumere che il nuovo `--config` abbia già generato o testato un nuovo MP4.
