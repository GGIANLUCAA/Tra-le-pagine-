# ARTVISION V3 — REGIA ARMONICA: LO SGUARDO GUIDATO

Data: 20 ottobre 2026. **Fonte creativa**: feedback dell'utente sul video Van Gogh V2 e secondo video di riferimento `No-Cuesta-Saber-fdown.net.mp4`, circa 29,42 secondi, verticale 360×640, 30 fps.

## Osservazioni reali sul video di riferimento
- Non presenta movimenti di macchina continui: il materiale pittorico rimane leggibile, alcuni cambi avvengono approssimativamente ogni 2,5–3 secondi. Fotogrammi consecutivi molto simili, salvo stacchi.
- La gerarchia è opera/volto/dettaglio, successione chiara e respiro.
- Il video fornito è solo ispirazione di montaggio; **non copiarne l'audio, il video, i loghi, le grafiche, o altre risorse protette**.

## VINCOLI RICHIESTI DALL'UTENTE (obbligatori in futuro)
1. NIENTE video con sequenza casuale di immagini come slideshow.
2. NIENTE screen split, quadri affiancati a metà, o effetti di sovrapposizione ripetitiva.
3. Movimenti sobri: brevi rallentamenti, pause quasi statiche sui dettagli emozionanti; alcuni momenti più veloci se ragionati.
4. **Ogni opera presentata: dettaglio significativo selezionato in modo motivato → reveal fluido → opera intera tenuta sufficientemente a lungo.** Niente macro casuali, niente zoom folli.
5. Direttore artistico deve riconoscere gerarchia dei dettagli (occhi nei ritratti, fiore nelle nature morte, centro prospettico nei paesaggi). Il montaggio segue il soggetto, non il contrario.
6. Niente musiche generate con onde sinusoidali. **Registrazioni musicali vere** gratuite con licenze valide per uso online e commerciale se previsto; crediti verificati, nel file/social caption. Assenza licenza o audio -> interrompere, mai inventare diritti.
7. Musica armonica all'atmosfera, tempi di sguardo umani, stile diverso per artista; no copia-incolla di preset indistinti.
8. Video distribuito solo dopo revisione materiale, metadati delle opere e verifica copyright sui beni culturali applicabili.

## Architettura V3
Il codice nuovo è **`modules/artvision/harmonic_reveal_v3.py`**. Usa le API museali e il filtro diritti importati dal vecchio `artvision.py`. Compatibilità:
- `style=harmonic_reveal`: **nuovo default**, real piano / dettaglio->intero.
- `style=cinematic_wow`: vecchio V2, preservato per riferimento.
- `style=museum_legacy`: V1, preservato.
Tutti usano il workflow `.github/workflows/artvision-render.yml`, evitando modifiche ai render narrati.
Backup: `backup-artvision-v2-prima-regia-armonica-v3-2026-10-20`.

### Regia curatoriale
La V3 comprende una mappa **reale, artigianale, titolo→focale→ragione registica**, limitata a Van Gogh per il primo episodio. Per nuovi artisti: **prima estendere la mappa**. Non riutilizzare coordinate Van Gogh su Caravaggio/Monet, non scegliere random e dichiarare 'curato'. Per opere senza mappa V3 il renderer rifiuta render se meno di 6 opere curate. In futuro estendere la logica con anteprima umana/AI vision verificata.

### Colonna sonora: fonte autore verificata
- `Calmant`, **Kevin MacLeod**, pianoforte.
- Pagina ufficiale: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100859
- Licenza indicata sul sito dell'autore: **CC BY 4.0** https://creativecommons.org/licenses/by/4.0/
- Registrazione autentica reperita da fonte dell'autore e/o Wikimedia Commons; lo scaricamento deve essere verificato via ffprobe, > durata video.
- **Attribuzione obbligatoria**: '"Calmant" Kevin MacLeod (incompetech.com) — Creative Commons BY 4.0 — https://creativecommons.org/licenses/by/4.0/ — excerpt/fades in ArtVision.'
- È erroneo dire 'non coperta da copyright': è protetta ma concessa gratis con obbligo crediti; monetizzazione secondo licenza CC BY4.0.
- Manifest obbligatorio `MUSICA_LICENZA_E_CREDITI.json` con fonte reale, hash e licenza. Non usare l'audio del video di riferimento, né musica di terzi senza diritti.
- Se l'URL o licenza non è verificabile, **fallire esplicitamente**, non sostituire con sintetizzatore senza accordo.

## Parametri consigliati
- Durata standard 150 s, vertical 720x1280 H.264/AAC, 24fps, voce assente.
- Dettaglio iniziale 3–4 s quasi fermo; reveal 2,7–3,5 s con `smoothstep` (accelerazione dolce, frenata naturale); quadro intero mantenuto circa 2–3,5 s; la mappa peso privilegia volti e opere significative.
- Zoom dettagli massimo circa 1.4–1.65× su source naturale; intensità sotto controllo, nessuna deformazione o scontorno.
- Rispettare l'aspect ratio autentico dell'opera; fondale nero neutro, non duplicare riproduzioni ai lati e niente metà-schermo.
- Un solo nome artista nella cover iniziale; ogni opera resta priva di didascalie invasive.
- Sequenza colore/natura→paesaggio→rapporto umano→interiorità; chiudere con respiro e fade musicale.
- Out: `ARTVISION_VIDEO.mp4`, `COPERTINA.jpg`, `STORYBOARD_REGIA.json`, `MUSICA_LICENZA_E_CREDITI.json`, `OPERE_FONTI_E_DIRITTI.json`, `CREDITI_E_FONTI.txt`, `DESCRIZIONE_SOCIAL.txt`, `REPORT_PRODUZIONE.json`.
- Pubblicazione automatica disabilitata per impostazione permanente.

## Collaudi obbligatori
1. Preflight sintattico Python e FFmpeg, preflight diritti sulle immagini e sul brano.
2. Run GitHub `success`, artifact e MP4 realmente presenti; verifica audio/codec/durata e screenshot multipli nei segmenti dettagli, reveal e quadro intero.
3. Test di qualità su tre opere: rilevare se dettaglio è motivato, se reveal è armonico e se opera intera è leggibile.
4. **Non chiamare questa soluzione definitiva/meravigliosa solo perché il codice gira.** L'utente decide il gradimento artistico. Preservare il file precedente e aggiornare la regia in piccoli passaggi.
5. Nessuna modifica ai libri narrati o ai precedenti modi di ArtVision.

## Procedura futura standard
Richiesta "crea un ArtVision su [nome]" → recuperare la mappa soggetti dell'artista o crearla da vere opere, scegliere musica real/CC adeguata, aggiornare `modules/artvision/queue.json` con `style=harmonic_reveal`, `artist`, `duration`, `request_id` nuovo, `approved_for_render=true`, `publish=false`; attendere job finale, scaricare artifact, controllare e consegnare MP4. Non usare lo stesso repertorio/musica/coordinate per artisti diversi.


## V3 prima produzione COMPLETATA / verificata — 20 ottobre 2026
- GitHub Actions [run #9](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39422133252) **SUCCESS**, artifact `ARTVISION_9` verificato.
- Van Gogh, 16 opere di museo con metadati, 16 scene intenzionali (ognuna dettaglio → camera rallenta → intero), 150,000 secondi, 720×1280, H.264/AAC.
- Vera registrazione scaricata dal sito ufficiale di Kevin MacLeod `Calmant.mp3`; SHA-256 `145d51e68117d5dc47b68cd2ac0577fd3c9d8c7464b49c32b3c25ad882c106c5`. Manifest e licenza CC BY 4.0 in `MUSICA_LICENZA_E_CREDITI.json`; allegare crediti ai post.
- ArtVision V3 0 API a pagamento. Il report riporta 244,5 secondi end-to-end.
- È stato verificato un campione di 27 fotogrammi da 9 opere (dettaglio, reveal, intero). Niente split-screen. Nota visiva: dipinti orizzontali interi usano bande scure verticali per preservare il rapporto d'aspetto, non tagliare l'opera.
- MP4 originale ~35 MB; successiva ricompressione H.264 CRF24 preservando 150s/AAC ~16 MB, volume medio -18 dB, picco -0.8 dB.
- Per evitare doppi render inutili durante gli aggiornamenti, il trigger GitHub Actions automatico ora ascolta solamente modifiche a `modules/artvision/queue.json` (resta anche workflow_dispatch manuale).
- La registrazione è **copyrighted ma licensed CC BY 4.0**, NON 'priva di copyright'; crediti pubblici obbligatori per monetizzazione/licenza.
- ArtVision V1/V2 e tutti i motori libro/narrati sono conservati. V3 per altri artisti richiede mappa di soggetti ragionata, non sempre stessa selezione.
- Verifica creativa finale deve seguire il gusto dell'utente. Il render green dimostra solo affidabilità tecnica.
