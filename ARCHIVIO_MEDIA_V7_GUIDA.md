# TRA LE PAGINE — ARCHIVIO MEDIA V7 (riuso legale, smartphone-only)
*Nuovo modulo add-on: 20 ottobre 2026. Voce Google/Gemini INVARIATA.*

## Che cosa cambia, esattamente
Il tuo telefono serve solo per avviare workflow e aprire file. **La ricerca e l'eventuale download avvengono sui server GitHub Actions**, non sul telefono.

Invece di generare ogni nuova fotografia, **prima si cerca materiale già esistente** e lo si confronta con ogni frase della storia. Un materiale viene riutilizzato solo se coerente e con diritti adeguati. L'archivio non ricrea mai copioni altrui, non scarica filmati protetti da TikTok/YouTube senza autorizzazione e non spaccia immagini generiche per documentazione di eventi reali.

La voce ufficiale rimane **Google Gemini TTS**, con le stesse impostazioni già approvate. Si mantiene il vecchio renderer V5, la libreria effetti V4/V5, tutti i progetti originali e V6. Questa funzione NON cambia nessuno di tali file.

## Le due fonti già collegate a livello di codice
| Servizio | Cosa | API key | Come funziona ora |
|---|---|---|---|
| Openverse | Foto Creative Commons CC0 e CC BY | Non richiesta entro i limiti anonimi | Cerca, mostra le anteprime e scarica solo una **immagine selezionata**, se proviene da dominio Wikimedia autorizzato |
| Pexels | Fotografie e clip stock | **PEXELS_API_KEY** gratuita (opzionale) | Cerca, mostra le anteprime e importa una foto o clip scelta dall'utente (limite 45 MB video) |

Openverse cerca anche contenuti da altri archivi: quelli non ospitati nel dominio autorizzato sono **solo suggerimenti da aprire alla fonte**, non sono scaricati automaticamente. Metadati e licenze richiedono sempre una verifica: CC BY impone crediti, link alla licenza e indicazione delle modifiche. Sono escluse automaticamente le varianti NC (non commerciali), ND e SA dal flusso di importazione semplificato. Pexels non consente di ridistribuire file stock così come sono né di usare la sua API per creare un concorrente.

Gli strumenti catalogati in V6 (Qwen, Wan e Hunyuan) restano disattivati. Prima usare gli asset già presenti nell'episodio e in archivio; solo se manca qualcosa valutare AI.

## Dal telefono Android — senza installare programmi
1. Apri [Actions → Archivio Media V7](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/archivio-media-v7.yml).
2. Premi **Run workflow**.
3. Imposta **mode = discover**, **provider = openverse**, **kind = image**, **query = river India** (o un soggetto utile alla scena).
4. Premi **Run workflow**.
5. Nella run riuscita, sotto **Artifacts**, scarica `ARCHIVIO_MEDIA_V7_discover` ed estrai lo ZIP (Android gestisce gli ZIP). Apri `SFOGLIA_MEDIA_V7.html` con Chrome.
6. Le schede indicano anteprima, autore, fonte, licenza e **ID**. Apri la pagina originale e controlla il tipo di licenza, i volti, l'attinenza alla storia e altri eventuali diritti.
7. Seleziona il file che vuoi importare: riapri **Run workflow** con **mode = import** e incolla **asset_id**. Mantieni uguali `provider` e `kind`.
8. Scarica l'Artifact `ARCHIVIO_MEDIA_V7_import`, che contiene l'immagine/clip più `PROVENIENZA_V7.json` e `CREDITI_DA_VERIFICARE.txt`. **Non finisce direttamente nel MP4**: va prima controllato e associato alla scena corretta.

### Per cercare video senza generazione AI
Crea gratis una Pexels API key sul [sito ufficiale](https://www.pexels.com/api/). Dal browser GitHub apri **Settings → Secrets and variables → Actions → New repository secret**, crea `PEXELS_API_KEY` e incolla la chiave. **Non scriverla mai in un messaggio, screenshot o file pubblico.** Apri il workflow, scegli `provider=pexels`, `kind=video`, `mode=discover`, e cerca ad esempio `forest river vertical`.

Tutto il lavoro rimane sui server GitHub. Per gli asset video selezionati, il modulo verifica estensione reale MP4, host consentito e grandezza massima: non crea né pubblica un nuovo episodio in automatico.

## Funzioni di sicurezza e risparmio già presenti
- **Zero generazione AI** nel workflow di ricerca; non chiama Gemini e non consuma crediti di sintesi.
- Non scarica contenuti nella fase `discover`: solo anteprime come collegamenti alla fonte (non archiviate né pubblicate).
- Scarica **un solo elemento**, dopo scelta dell'ID: non è un crawler di download di massa.
- Filtri iniziali CC0/CC BY, crediti obbligatori per i candidati e revisione manuale del singolo file.
- Solo HTTPS su un insieme limitato di host per i file, blocco redirect, controllo firme dei file e dimensioni; niente scraping indiscriminato.
- Il pacchetto importato rimane nell'Artifact GitHub **14 giorni**, poi scade; non è un archivio permanente.
- Non modifica il repository, non scrive sui vecchi episodi, non salva credenziali in file e **non pubblica** su social.
- L'uso di GitHub Actions potrebbe consumare minuti della quota del piano GitHub: gratis non significa necessariamente senza limiti.

## Come recuperare un'immagine nella regia esistente
1. Scegli **quale frase/inquadratura** devi illustrare tramite il piano V6.
2. Recupera prima l'immagine già presente; se inadatta cerca negli archivi.
3. Scegli un file con licenza adatta, correttezza storica e contesto adeguato.
4. Dopo l'approvazione, l'immagine potrà essere inserita nella cartella `images/` o nel `scene_premium.zip` dell'**episodio nuovo**, con il nome richiesto (es. `scena_07.jpg`).
5. Rimonta usando V5 senza ricreare la voce se la traccia Google esiste e rimane approvata.
6. Aggiungi la nota dei crediti alla descrizione video e conserva `PROVENIENZA_V7.json`. Indica eventuali modifiche.

**Attenzione:** il passaggio 4 è una fase editoriale supervisionata, non ancora automatizzata da V7. Non sostituire una scena preesistente o approvata senza richiesta esplicita.

## Prossimi moduli (NON ancora integrati)
- Pixabay tramite API ufficiale e licenza Content License, inclusi effetti sonori.
- Wikimedia Commons via MediaWiki API con crediti e licenza letti direttamente dalla pagina.
- Internet Archive e filmati storici con controllo elemento per elemento. L'archivio ospita anche opere protette: presenza nel sito NON significa pubblico dominio.
- NASA per documentari spaziali, distinguendo le immagini istituzionali e i loghi o persone.
- Una biblioteca di clip e scene storiche approvate dall'utente, per riusarle in più episodi senza ricerche ripetute.
- Un *selettore per scene* che classifichi risultati in base a qualità, diritti, soggetto e ambiente, poi chieda approvazione.

## Fonti ufficiali per verificare i diritti
- [Openverse API](https://api.openverse.org/v1/)
- [Pexels API e condizioni](https://www.pexels.com/api/documentation/)
- [Pexels License](https://www.pexels.com/license)
- [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- [Pixabay Content License](https://pixabay.com/service/license-summary/)
- [MediaWiki API Imageinfo](https://www.mediawiki.org/wiki/API:Imageinfo)
- [NASA Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)

**Regola di produzione permanente:** prima *riusa* asset approvati, poi *cerca* materiale licenziato, e **solo infine genera** il materiale mancante con AI. Un poster, un fotogramma estraneo o un finto filmato d'archivio non diventano materiale autentico soltanto perché provengono da un sito noto.
