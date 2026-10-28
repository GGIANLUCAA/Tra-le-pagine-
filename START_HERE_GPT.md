# Inizia da qui — studio video di Gianluca

Leggere `AGENTS.md`, [regole attive](docs/REGOLE_ATTIVE.md) e
[registro dei format](config/video_formats_v13.json). Questa revisione del 25/10/2026
prevale sui vincoli storici incompatibili. Le istruzioni della sessione restano prioritarie.

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

