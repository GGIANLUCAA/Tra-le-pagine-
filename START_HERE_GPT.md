# Inizia da qui — studio video di Gianluca

Leggere `AGENTS.md`, [regole attive](docs/REGOLE_ATTIVE.md) e
[registro dei format](config/video_formats_v13.json). Questa revisione del 25/10/2026
prevale sui vincoli storici incompatibili. Le istruzioni della sessione restano prioritarie.

## V64 — FOTOGRAFIA REALISTICA E FEDELE, NON FALSO RESTAURO (28/10/2026)

**Feedback esplicito dopo V63:** i ~2s FOTO FERMA devono apparire davvero come fotografie moderne nitide: volti, occhi, pelle, capelli, mani, abiti e ambienti convincenti e corrispondenti al film originale. **V63 NON approvato come master definitivo**: crop originale da film Beirut 720×576→~324×576, DDColor+Real-ESRGAN non ricreano dettagli umani sufficienti. Test con AI generativa ha prodotto volti fotorealistici ma **persone/abiti differenti**, quindi scartare come falso restauro. Priorità: nuova fonte PD/CC0 con **vera scansione HD/2K**, volti già abbastanza grandi nel frame; confronto più fotogrammi reali per estrarre dettaglio verificabile; restauro conservativo, ricostruzione image-to-image con vincoli di identità/struttura e controllo umano. **Il file bello ma infedele è REJECT**, così pure il filtro sfocato 1080p. Nessun nuovo master se non supera `src/storia_rivive_quality_policy_v64.py`: `docs/LA_STORIA_RIVIVE_FOTO_FEDELE_V64.md`; `config/storia_rivive_v64.json`. Preferire scartare scena o cambiare fonte piuttosto che inventare lineamenti. V59,V55 e nessuna spesa GPU/HF/Vidu senza autorizzazione.

## V63 — REGIA PRIMA DEL RESTAURO (28/10/2026)

Dopo V62 (18,2s): meglio 20–28 s quando serve; studiare l'intero filmato e confrontare i ritagli 9:16, fermandosi sui volti, gesti e momenti davvero importanti. Priorità al contenuto, NON a scene panoramiche riempitive. Fotografia dal ritaglio originale prima di Real-ESRGAN, NO downscale distruttivo V62, denoise leggero, DDColor, render 1080×1920, hold 1.8–2.8s secondo importanza. Il 1080p NON è 4K. Un image-to-image generativo davvero fotografico può superare il semplice ESRGAN, ma serve compute, licenze e valutazione fedeltà, non è integrato. `docs/LA_STORIA_RIVIVE_DIREZIONE_FOTOGRAFICA_V63.md`, `config/storia_rivive_v63.json`, `src/storia_rivive_director_cut_v63.py`. Provino a verifica artistica; V59, V55 e 0 crediti Vidu invariati.

## V61 — EFFETTO ESATTO: VIDEO B/N → FOTOGRAFIA AI STATICA COLORATA

La scelta di regia è GIÀ stata chiarita dall'utente: analisi dei tre video `43054.mp4` (2s+2s), `43055.mp4` e `43056.mp4` (~0,9s+0,9s). Per ogni ripresa autentica: muove il B/N, seleziona istante significativo, **blocca movimento**, cambia rapidamente in NUOVA fotografia AI ricostruita con colori/distinzione e nitidezza moderna; lascia ammirare la FOTO per 0,9–2 s, poi cut a NUOVA scena. Non serve Vidu. Non basta DDColor su video, non serve 4K nativo. Vedi `docs/LA_STORIA_RIVIVE_FOTOGRAMMA_FOTO_AI_V61.md` prima di nuove produzioni. Senza il file fotografia AI realmente generato e visto non affermare di avere un risultato conforme.

## V59 — Fonti storiche di pubblico dominio, no monetizzazione

Per `La Storia Rivive` non domandare ancora se vuole monetizzare: la risposta è **no**. Seleziona SOLO veri filmati originali PD o CC0 verificati; il software può essere open-source o limitato a usi non commerciali quando consente effettivamente la produzione e pubblicazione prevista. Non usare tool «solo ricerca» per pubblicare senza verifica specifica. Diritti musica indipendenti, nessuna autopubblicazione, mantenere V55. Guida `docs/LA_STORIA_RIVIVE_DOMINIO_PUBBLICO_V59.md`.

## V58 — Storia senza stampini e senza 4K cosmetico

Quando viene chiesto «un nuovo video storico», fare autonomamente ricerca qualitative di almeno 3 filmati d'archivio, scegliere scene con azioni vere, progettare un gancio forte e un montaggio anche multi-shot quando serve. Percepito nitido a 720p/1080p meglio di falso 4K. Colorizzazione AI reale non seppia, continuità, fonte esatta; montare con FFmpeg e materiali colorizzati già verificati. Vidu solo opzionale e a pagamento previa approvazione per clip. Leggere `docs/LA_STORIA_RIVIVE_OPEN_SOURCE_E_MONTAGGIO_V58.md` e il registro `queue/storia_rivive_candidates_v58.json`; nessuna domanda ripetuta sui preset già decisi.

## La Storia Rivive: riferimento estetico V57

Non chiedere di nuovo che effetto desidera l'utente: **colore vero ben definito, volti realistici, dettaglio moderno**, come i tre MP4 di riferimento; non seppia né sola dissolvenza. Leggere `docs/LA_STORIA_RIVIVE_QUALITA_V57.md` prima di avviare la categoria. Il test gratuito accettabile è una clip 2–3s colorizzata DAVVERO con AI, non un'altra tinta cosmetica. Preservare separazione archivio autentico vs ricostruzione generativa e budget 0 senza autorizzazione.

## La Storia Rivive V56 — avvio senza questionari

Per richieste di video da filmati storici usare il format `storia_rivive` e il suo contratto in `docs/LA_STORIA_RIVIVE_CONTRATTO_V56.md`, con preferenze già impostate: film originale autentico, CC0/diritti controllati, primo frame memorabile, restauro fedele, 0 crediti di default e pacchetto V55 completo. Non chiedere nuovamente le regole o le scelte già note; distinguere sempre pilot progettato, MP4 realmente pronto e archivio realmente sincronizzato.

Quando Gianluca chiede un video o una serie, usa il [menu rapido](docs/ISTRUZIONI_MENU_VIDEO_NUOVE_CHAT.md):
precompila le scelte già presenti nella richiesta, mostra le opzioni consigliate e
lascia modificare le altre senza trasformarle in domande obbligatorie. “Usa le
impostazioni consigliate e procedi” consente di continuare senza un altro giro di
conferme. In una chat indipendente, non presupporre che il repository sia accessibile.

Gianluca può chiedere:

> Crea cinque video Critico d'arte su soggetti diversi. Segui START_HERE_GPT.md,
> studia ogni opera, mantieni la voce Gacrux e proponi un mix motivato per ciascuno.
> Riusa le tecniche approvate e conserva le impostazioni di ogni risultato.

Oppure:

> Migliora questo video mantenendo il format e la voce. Usa l'apertura del video X
> e il ritmo del video Y se sono compatibili. Recupera prima le loro schede.

## Priorità permanente sulle immagini (V33)
## ArtVision 4x1 — guida rapida V54 (28/10/2026)

Per ogni opera scelta per la produzione **seriale ArtVision**, ora sono quattro i video distinti: Critico Standard, Critico Museum, Cinema Standard e Cinema Museum. Il limite precedente di due video V53 è superato. Leggere `docs/REGOLE_ATTIVE.md` e `docs/ARTVISION_FOUR_VARIANTS_CONTRACT_20261028.md`. Un'unica ricerca visiva e storico-artistica deve individuare almeno tre particolari autentici, tensione centrale, progressione emotiva e un momento forte *motivato*, non effetti casuali. Non usare lo stesso stampino di montaggio su opere diverse.

Creare il dossier vuoto con `python src/video_director_v13.py four-brief --topic "Opera" --artist "Autore" --out output/ARTVISION_4X1_PLAN.json`, compilarlo senza inventare verifiche, poi `python src/video_director_v13.py four-check --plan output/ARTVISION_4X1_PLAN.json`. È un controllo strutturale a costo zero, non una verifica estetica. Se il dossier 4x1 è legato al progetto V13 con `serial_mode` e `artvision_4x1_plan`, anche il preflight ordinario lo blocca quando incompleto.

Dopo ogni MP4 realmente visto e ascoltato usare `src/artvision_learning_loop_v1.py` per registrare difetti specifici contro il SHA256 esatto, conservare lezioni e scegliere **una sola sperimentazione misurabile** per la produzione seguente. Niente falsi Gold Master, spese automatiche o autocritiche inventate.



Per **qualsiasi nuovo video/serie** applicare `docs/FILOSOFIA_FONTI_MEDIA_V33.md`
e `config/editorial_rules.json > media_source_priority`:
riusa prima asset approvati **pertinenti**, per arte/cronaca privilegia fonti
autentiche e licenziate; usa Pixabay (`PIXABAY`) o Openverse per stock coerente;
per scene narrative specifiche privilegia illustrazioni originali con personaggi
consistenti (AI Horde sperimentale); non usare Canva Premium per default.
Compila `media_sourcing` per ogni asset prima del check V13. Nessuna spesa
o pubblicazione automatica e niente nuovi secret da richiedere se già disponibili.
Una fonte catalogata non è necessariamente un connettore attivo.

## Selettore scene/fonti V34

Applicare i criteri permanenti V33 tramite `docs/SELETTORE_FONTI_V34_GUIDA.md`.
Dopo lo storyboard e prima dell'acquisizione utilizzare `src/source_selector_v34.py`
per proporre un percorso scena per scena. `plan` offline, ricerca singola
`discover` su Pixabay/Openverse per sole scene pertinenti; non considerare
le 45 API integrate. Il controllo artistico e il render restano separati.

## Riferimento creativo V38 (26/10/2026)

Consultare `docs/FEEDBACK_REGIA_NARRATIVA_V38.md` e `config/editorial_rules.json > creative_variation`. Il filmato **La macchina del tempo** e un riferimento **positivo per ricchezza visuale e varieta** ma non un modello da replicare ne un Gold Master. Ogni storia sceglie durata, immagini, ritmo e regia a partire da beat e necessità della narrazione; non copiare le 16 immagini o circa tre minuti del riferimento. L'identita di serie resta coerente, il montaggio cambia per ogni soggetto.

## Procedura dell'agente

1. Recuperare riferimenti e regole; identificare il format richiesto.
2. Creare una nuova scheda con `brief`; compilarla con ricerca e scelte motivate.
3. Eseguire `check`, risolvere i blocchi, usare i renderer realmente disponibili.
4. Controllare file, parlato e immagini; consegnare MP4, cover, post e dati di replica.
5. Salvare le correzioni con ambito e versione; pubblicare solo se autorizzato.

```bash
python src/video_director_v13.py formats
python src/video_director_v13.py brief --format artvision_critico --topic "Opera scelta" --out output/nuovo_video
python src/video_director_v13.py check --project output/nuovo_video/PROJECT_V13.json
```

Il brief contiene `editorial_contract` e `editorial_plan`. Una scheda vuota è
una bozza: check blocca la produzione finché dati e revisioni sono incompleti.
Il cambio Critico → Cinema non può avvenire silenziosamente. I numeri di scene,
le durate e le tecniche si scelgono per il contenuto, senza quote estetiche fisse.

Per lotti e ripresa consultare V15/V16 nel [playbook](docs/GPT_VIDEO_PLAYBOOK.md).
Android è il mezzo operativo. Nessun nuovo servizio a pagamento viene attivato.
Questo file non è un generatore di video né una funzione installata sul sito live:
serve all'agente con accesso al repository per eseguire il lavoro con i motori esistenti.


## Consegna obbligatoria V55: ChatGPT e Video Library Studio

Per ogni nuovo video (non solo ArtVision) applicare `docs/REGOLE_ATTIVE.md > V55`: MP4 scaricabile in ChatGPT, ZIP alternativo reale, copertina approvata, 4 post social curati e file di fonti/ricetta; importare e verificare lo stesso master e dossier sul sito privato prima di dichiarare la consegna completa. Il sito genera il ZIP completo on demand con link temporaneo; non considerare automaticamente presente il post originale se il sito ha soltanto una scheda generica.

L'apertura (primo frame e primi 1/3/5/7 secondi) decide l'interesse: organizzare un dettaglio significativo, una scoperta e una progressione, con voce/musica adatta e titoli leggibili. Controllare fotogrammi reali e ascoltare tutto l'inizio; niente ingressi museali vuoti, niente stesso stampino. Strumento per ArtVision: `src/artvision_delivery_v55.py`. La verifica tecnica non certifica emozione, la presenza locale non prova la disponibilità del link su Android.

\n## V69 — scegliere prima la pellicola che si ricostruisce DAVVERO meglio (28/10/2026)\n\nFeedback dopo V68 Parigi: il livello wow dipende soprattutto dal **fotogramma antico di partenza**. Cercare scansioni 35mm con qualità reale superiore, anche di più di 100 anni, persone/volti abbastanza grandi e leggibili, movimento interessante e crop verticale che preserva i dettagli. La scena del cinema con insegna definita funzionava per architettura; per volti cercare primi piani più vicini. Confrontare almeno tre filmati, più frame ciascuno, e **provare realmente due foto AI generative** prima di scegliere il soggetto. Il risultato fotografico a colori, non il solo raster 4K, deve determinare la scelta. Il progetto V69 include `docs/LA_STORIA_RIVIVE_SCELTA_WOW_V69.md`, `config/storia_rivive_v69.json` e `src/storia_rivive_source_selector_v69.py` con blocchi se non sono verificati fonte PD/CC0 in Italia, provenienza scansione, fotografia generativa effettiva e QA volti/oggetti/scena. NON aumentare arbitrariamente FPS/risoluzione per chiamarlo 4K. No Vidu o GPU a pagamento, no autopubblicazione.\n
## REGOLA VINCOLANTE V74 — Effetto approvato La Storia Rivive, 29/10/2026
Feedback esplicito: il film Coney Island V73 (colore continuo sul moto) è **BOCCIATO rispetto all'effetto richiesto**, nonostante MP4 tecnicamente valido. Per OGNI nuovo video storico richiesto genericamente, standard obbligatorio = filmato d'epoca realmente in movimento in B/N → STOP sul frame esatto → **fotografia AI image-to-image nitida, colorata, fotorealistica e fedele** → pausa foto statica o micro-movimento fotografico → nuovo vero filmato B/N diverso. Il riferimento è l'esempio utente `43054.mp4` (6 trasformazioni lente da ~2s) e `43056.mp4` (9 trasformazioni rapide da ~0,9s). Non basta colorizzare il filmato in movimento, applicare LUT, seppia, DDColor, geometrical upscale o una dissolvenza. Se la sorgente è sfocata è ammessa ricostruzione più profonda ma plausibile; se è nitida serve fedeltà superiore a volti, abiti, occhi, mani, oggetti e prospettiva. V72 «cinema continuo» è solo opzione sperimentale se esplicitamente richiesta, **non** preset predefinito. V73 va marcato `REJECT_REFERENCE_MISMATCH`. Regole complete: `docs/LA_STORIA_RIVIVE_EFFETTO_REFERENCE_V74.md`. Verifica strutturale: `src/storia_rivive_v74_effect_gate.py`; la verifica artistica resta obbligatoria, non automatica. Nessun credito Vidu senza consenso, MP4+ZIP realmente scaricabili e sito privato verificato senza dichiarazioni false. Mai chiedere all'utente di ripetere le regole o rimontare i suoi video di esempio.

## V75 — Feedback positivo e perfezionamento del formato (29/10/2026)

**L'utente APPROVA l'effetto realizzato in Parigi V74**: ripresa storica autentica in bianco e nero con movimento → blocco dello stesso fotogramma → fotografia AI restaurata a colori, fotorealistica e FERMA → successiva ripresa autentica. Non cambiare questo effetto né reinterpretarlo come colorizzazione in movimento. V74 è ora riferimento positivo per la regia, pur restando migliorabile nella qualità fotografica.

### Due modifiche richieste e approvate
1. **Durata leggermente maggiore rispetto a Parigi V74 (14,4 s).** Impostazione editoriale orientativa per i prossimi episodi: **22–28 secondi**, variabile secondo l'azione e la qualità delle scene, senza allungare artificialmente singoli fotogrammi o riciclare riprese. In genere 4–6 trasformazioni davvero diverse e significative; qualità prevale sul numero. Se esistono solo tre foto eccezionali, non riempire con materiale mediocre. Il video deve iniziare a incuriosire entro i primi 1–3 s.
2. **Un bel titolo iniziale con anno ben leggibile**, e località corretta. Titolo cinematografico/museale elegante, curato nella tipografia e nelle proporzioni, ad esempio `PARIGI · 1898` / `CONEY ISLAND · 1903`, eventuale credito archivio piccolo e discreto. Idealmente appare nei primi **0,8–1,5 s sopra una vera ripresa in movimento** (senza cartello nero fermo o attesa vuota), poi si ritira per lasciare spazio alle scene. Niente «prima/dopo», diciture tecniche o paragrafi; niente voce per questo format. Verificare il periodo esatto sulle fonti, non inventare l'anno.

### Indicazioni per montaggio e QA
- Eseguire il formato **V74 approvato**, il titolo non deve coprire i volti, l'azione o la trasformazione né appesantire la prima inquadratura.
- I blocchi fotografici devono essere abbastanza lunghi da far ammirare i dettagli (preferibilmente 1,5–2,5 s, con flessibilità artistica).
- Allungare l'episodio aggiungendo scene vere, soggetti WOW e fotografie AI approvate, **non** mediante zoom/fermi troppo lunghi o duplicati.
- Esportare e verificare MP4/ZIP scaricabili, titoli, musica originale e controllo artistico. Backup GitHub diretto e sito privato soltanto se effettivamente caricati/verificati.
- Queste sono preferenze permanenti per i **prossimi episodi**. Non dichiarare di aver già rifatto video precedenti senza averlo eseguito.

**Stato:** effetto V74 APPROVATO dall'utente; introduzione/ritmo V75 miglioramenti richiesti per nuove produzioni.
