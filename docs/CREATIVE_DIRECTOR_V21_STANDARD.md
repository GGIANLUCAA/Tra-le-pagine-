# CREATIVE DIRECTOR V21 — STANDARD PERMANENTE DELLO STUDIO
*22 ottobre 2026 · obbligatorio per ogni nuova produzione, senza sostituire i master storici*

## Principio prioritario

Un filmato non è *pronto per la pubblicazione* solo perché il suo MP4 è stato renderizzato. Devono risultare preparati, verificati e congruenti:
1. **Prima immagine realmente forte:** interessante anche in miniatura e in autoplay, pertinente al video, non un logo prolungato.
2. **Apertura 0 / 1 / 3 / 5 / 7 secondi:** ogni passaggio dà informazioni nuove, emozione o vera suspense, senza cambiare foto ogni 2 secondi per automatismo. Niente promesse ingannevoli.
3. **Copertina distinta dal primo fotogramma:** nella griglia del profilo serve un soggetto leggibile a dimensioni ridotte. Le copertine V6 e Critico V2 già approvate restano INVARIATE. L'eventuale JPG candidato V21 NON le sovrascrive.
4. **Montaggio:** inquadrature motivate, voce Google naturale dove prevista, audio dinamico, fotografie/opere coerenti con la scena. Zero sottotitoli impressi, salvo nuova richiesta.
5. **Musica:** scegliere per emozione, ingresso, climax, pulizia della voce, sincronizzazione vera e diritti; riutilizzare un buon brano ogni volta che è appropriato senza ripetere meccanicamente lo stesso montaggio.
6. **Durata NON standardizzata:** determinata da storia, gesto musicale, durata della voce reale, rivelazione e grado di approfondimento; ricavare *dati di durata efficaci* solo dalle performance pubblicate effettive, comparabili per piattaforma e format. Nessun algoritmo esterno impone sempre 30/60/180 secondi.
7. **Testi social:** titolo autentico, descrizioni *diverse* per Facebook, Instagram, TikTok e YouTube, hashtag pochi e pertinenti, crediti completi per immagini e audio, istruzioni di caricamento Android.
8. **Originalità:** varietà di soggetti (volti, opere, sculture, persone, paesaggi, architetture, fotografie inquietanti, natura, forme musicali) **SOLO** quando sono inerenti alla storia e i diritti sono documentati. Non introdurre donne, nudi, immagini inquietanti o AI casuali come clickbait.
9. **Revisione e consenso:** controllo reale di copertina, apertura, finale, audio, diritti e descrizioni prima di rendere pubblico il filmato. L'agente svolge controlli già autorizzati senza chiedere conferma ad ogni singolo file. Pubblicazione pubblica solo con autorizzazione.

## Perché queste regole (fonti ufficiali)

- **Meta, marzo 2026:** valorizza contributo originale, riduce la distribuzione dei reupload e delle modifiche minime: https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/
- **Meta, marzo 2026:** qualified views, deeper engagement e watch time per leggere i ricavi: https://about.fb.com/news/2026/03/creator-fast-track-grow-your-audience-earn-money-on-facebook/
- **Meta anti-spam:** titoli/descrizioni eccessive, hashtag incongruenti e copia sistematica sono controproducenti: https://about.fb.com/news/2025/04/cracking-down-spammy-content-facebook/
- **YouTube:** la promessa di titolo+thumbnail deve essere mantenuta dall'introduzione; studiare retention e momenti di abbandono: https://support.google.com/youtube/answer/16559650?hl=en e https://support.google.com/youtube/answer/9314415
- **TikTok:** non esiste una durata magica, hook immediato e montaggio commisurato al contenuto: https://ads.tiktok.com/business/library/TikTok_Works_Recut_Remix_Reimagine.pdf (indicazioni per creatività pubblicitarie; non legge universale dei feed organici).

## Musica Facebook: comportamento fondamentale

Quando si usa una canzone trovata **dentro Facebook/Instagram**, **non scaricarla o estrarla dall'app** e **non considerarla automaticamente libera su YouTube/TikTok**. Conservare il master universale senza incorporare quella registrazione. Nell'editor Meta scegliere l'ID del brano e il tratto pertinente *solo se il tipo di account, la destinazione, il contesto e la licenza lo consentono*. L'uso commerciale o la monetizzazione possono avere limitazioni; non presumerne l'idoneità.

Distinguere:
- **Meta licensed/native music library:** Instagram indica che la sua libreria musicale generalista è destinata all'uso personale, NON necessariamente commerciale. Aggiunta in app, verificare specifica opera/territorio/uso.
- **Meta Sound Collection:** catalogo distinto con impieghi commerciali consentiti *entro il perimetro dei termini Meta*: non è una licenza universale o automatica per la registrazione ripubblicata su altre piattaforme.
- **Registrazione esterna** licenziata (es. CC BY) o musica originale: può essere incorporata solo nei social/territori realmente permessi; crediti in descrizione e prova della registrazione.
- **Ripetizione:** si può usare lo stesso brano anche su numerosi video quando coerente, ma non usare identico beat-template, inquadrature o crescendo con il solo titolo cambiato. Nel V21 la musica scelta NON viene sovrascritta per cercare artificialmente varietà.
Fonti: https://www.facebook.com/help/instagram/402084904469945 e https://www.facebook.com/help/354736791367645/

## Durata: logica pratica, non timer fisso

- 1 sola rivelazione visiva: finire appena la promessa è mantenuta; niente riempitivi.
- Una critica che richiede contesto: scegliere durata in base ai dettagli da mostrare, voce realmente recitata, comprensibilità e ritmo.
- Cinema d'arte musicale: ascoltare struttura del brano e costruire motivi visuali; non abbreviare arbitrariamente la V6 approvata.
- Libro raccontato: climax, motivazioni e conseguenze contano più di un target numerico.
- Visual Music: tagliare sui veri eventi musicali o note, non su un metronomo falsificato.
- Con dati REALI comparabili dopo la pubblicazione: leggere 3s/7s retention quando disponibile, visione media/durata, completamenti, condivisioni per 1000 e commenti autentici; estrarre ipotesi, MAI dire che un format è viralizzato senza statistiche.

## Sistema installato nel progetto

- `src/creative_director_v21.py`: legge un `PROJECT_V13.json`, uno schema Enigma o un brief compatibile. Decide un **archetipo creativo** in base agli asset pertinenti, non a scelta casuale. Propone prime scene, durata motivata e descrizioni specifiche.
- `config/creative_director_v21.json`: legge lo standard permanente.
- **Libri/critico/Cinema sul V16:** `src/production_runner_v16.py` crea, dopo ogni MP4 nuovo, il pacchetto V21, il controllo dei primi secondi e le bozze social. Se manca il pacchetto, la qualifica dei **nuovi** job è bloccata; i job storici non cambiano.
- **Enigma:** il workflow `.github/workflows/artvision-enigma-render-v1.yml` produce V21 accanto al MP4.
- **Altri renderer storici NON in V16:** l'obbligo è in `AGENTS.md` e nel Playbook GPT; si esegue il workflow manuale V21 finché non esiste un hook specifico. Non si dichiara agganciato un motore non verificato.
- `.github/workflows/creative-director-v21.yml`: prepara il pacchetto **anche senza MP4**, quindi senza fingere di aver visto il video. Avvio da GitHub Actions sul telefono.

## File per nuovo video

`CREATIVE_PACKAGE_V21.json`, `ISTRUZIONI_PUBBLICAZIONE_V21.md`, `POST_FACEBOOK_V21.txt`, `POST_INSTAGRAM_V21.txt`, `POST_TIKTOK_V21.txt`, `POST_YOUTUBE_V21.txt`. Se il master MP4 è disponibile, anche `APERTURA_0_7_V21.jpg` (contact sheet reale, campionato ai primi 0/1/3/5/7 s e qualche fotogramma successivo) e `COPERTINA_CANDIDATA_V21.jpg` (un fotogramma scelto per contrasto tecnico). **La scelta del fotogramma non è comprensione AI delle immagini.**

I file sono da REVISIONARE, non prova di visualizzazioni/monetizzazione e non publicazione automatica. Le descrizioni contengono soltanto il materiale del brief: se il brief è povero il risultato verrà segnalato e completato dall'agente con ricerca accurata, non riempito di fatti inventati. Evitare di inserire dati privati negli input di workflow pubblici.

## Esecuzione

```bash
python src/creative_director_v21.py --brief modules/artvision_enigma/episodes/arcimboldo_vertumnus.json --out output/creative-v21
# Dopo MP4 effettivamente renderizzato:
python src/creative_director_v21.py --brief PERCORSO/PROJECT_V13.json --video PERCORSO/filmato.mp4 --out output/pacchetto-social
# Opzionale: schede statistiche storiche verificate, non KPI simulati
python src/creative_director_v21.py --brief PERCORSO/PROJECT_V13.json --history report_storico_privato.json --out output/pacchetto-social
```

## Cosa resta alla revisione dell'agente

Non confondere test tecnici con bellezza o viralità. Dopo la generazione l'agente deve davvero vedere la miniatura su telefono, controllare l'inizio a 0/1/3/5/7 s, ascoltare tutta la musica, valutare il climax, l'audio Facebook in-app e la leggibilità della storia. La proposta viene approvata/corretta a seguito di verifica, mai semplicemente perché un punteggio automatico di contrasto è alto. Ogni nuova opera può richiedere una diversa archetipologia, anche fuori dalla tassonomia V21, in estensioni additive. Nessuna promessa di risultato o pubblicazione automatica.
