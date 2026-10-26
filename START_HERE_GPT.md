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
