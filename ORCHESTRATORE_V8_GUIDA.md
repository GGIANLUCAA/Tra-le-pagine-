# TRA LE PAGINE — ORCHESTRATORE V8
*Prima integrazione controllata fra V6/V7 e gli episodi del renderer storico. Modalità smartphone-only.*

## Obiettivo
Non aggiungere venti modelli AI: **collegare e riutilizzare le capacità già funzionanti**, con eventuale materiale personale fornito dall'utente. Voce **Google Gemini TTS INVARIATA**, FFmpeg/V5 e V3-V7 **non modificati**.

### Nuove capacità effettive
- Legge `episodes/<episodio>/scene_cues.json` e il catalogo V6.
- Moduli di provenienza media: **EpisodePlugin** (immagini dell'episodio) e **ManualPlugin** (manifest che mappa immagini già presenti in una cartella del progetto).
- Priorità agli asset esistenti, senza generarli; suggerisce asset simili da altri episodi **senza copiarli automaticamente**.
- Report JSON + anteprima HTML consultabile su smartphone; indicazione scena per scena di **presente/mancante**.
- Se si concede **Gate 1**, conversione in JPG e deduplicazione immagini in uno **staging isolato**, senza toccare la cartella storica. La deduplicazione SHA256 evita due conversioni inutili nello stesso staging.
- Blocco completo se manca un'immagine, le fonti editoriali necessarie o il Gate 1.
- **Nessuna API Gemini** in V8: la voce resta Google, ma la sintesi avviene solo con il precedente workflow video. Nessun contenuto pubblicato.

### Limiti reali (non dire che è già uno studio autonomo completo)
- Il workflow V8 **non genera MP4 e non richiama automaticamente il renderer**: prepara un episodio pronto per i controlli e il collegamento successivo.
- Non integra automaticamente nuovi risultati V7 da un'altra run: gli artifact V7 scadono e richiedono importazione autorizzata in un ambiente disponibile al workflow.
- Le clip VIDEO non entrano ancora nel renderer originale che usa immagini fisse. La libreria proposta V8 è **solo immagini**.
- Il matching tra descrizioni è per parole, non una AI che comprende davvero le immagini. I suggerimenti non equivalgono a immagini corrette.
- Nessuna cache vocale **persistente tra run** implementata; il risparmio attuale è il riuso delle immagini e la prevenzione di sintesi non necessaria.
- GitHub Actions ha quote: il piano GitHub Free ha risorse gratuite limitate, non illimitate.

## Guida Android
1. Vai a [Actions → Orchestratore V8](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/orchestratore-v8.yml).
2. Tocca **Run workflow**, scegli `03_siddharta`, `libri`, `plan`; lascia **gate1_approved = false**.
3. Nella run riuscita, in **Artifacts**, scarica `ORCHESTRATORE_V8_plan`.
4. Apri `REVISIONE_GATE1_V8.html` dal telefono, leggi `PIANO_V8.json`. Il piano indica quali scene hanno immagini disponibili.
5. Una volta approvati copione, fonti e storyboard, scegli `prepare` e imposta **gate1_approved = true**.
6. Se tutti gli asset sono presenti e ammessi, l'output contiene `stage/episodes/<episodio>` con tutti i JPG e i file necessari per il successivo preflight V5. Se mancano asset, V8 ferma la preparazione con un messaggio.
7. **Gate 2** sarà il controllo dell'MP4 finale: non esiste nessuna pubblicazione automatica.

La modalità plan funziona senza scaricare nulla, e il telefono fa solo da telecomando.

## Manifest media personali — solo materiale già disponibile al runner
Se hai materiale che sei autorizzato a usare per un progetto privato, si può predisporre una mappa (esempio: `input_v8/media.json`):

```json
{
  "3": {
    "path": "input_v8/mia_foto.jpg",
    "source": "foto_fornita_utente",
    "license": "uso_personale_da_verificare",
    "approved_for_private_project": true,
    "private_only": true
  }
}
```

Comando CLI facoltativo nella root del checkout:
```bash
python src/orchestratore_v8.py --episode 03_siddharta --format libri --manifest input_v8/media.json --mode plan
python src/orchestratore_v8.py --episode 03_siddharta --format libri --manifest input_v8/media.json --mode prepare --gate1-approved --out output/orchestratore_v8_nuovo
```

**Non caricare foto personali o file riservati nel repository GitHub pubblico.** Il workflow Android standard usa solo asset già presenti nel repository; i manifest privati non hanno ancora una UI di caricamento sicuro. Per materiali privati servirà storage privato collegato in futuro.

L'uso personale non rende automaticamente legittima qualsiasi acquisizione di materiale protetto, né permette di eludere DRM, paywall o protezioni. L'orchestratore accetta file locali forniti legittimamente, senza scaricare da siti non autorizzati e senza pubblicare.

## Compatibilità e test
- `src/orchestratore_v8.py` usa l'API di `src/studio_ibrido_v6.py`; V5 e V7 restano intatti.
- `tests/test_orchestratore_v8.py` verifica sicurezza percorsi, Gate 1, preparazione separata, riuso, foto personali esplicitamente approvate, immagini mancanti e assenza di pubblicazioni. Il CI richiama anche i test V6 e V7.
- Lo staging V8 viene **verificato dal validatore V3/V5 originale** (importazione della funzione `episode_v3.validate`), senza modificare il vecchio codice: vengono verificati copione, cue point, asset minimi e immagini complete prima di dichiarare la cartella pronta.
- La conversione JPG avviene soltanto in `prepare`, via Pillow già utilizzato dal renderer V5.
- Zero chiavi API in questo workflow, `permissions: contents: read`, nessun push e nessun trigger di pubblicazione.

## Prossime migliorie con beneficio superiore a nuovi modelli AI
1. **Media bridge vero V7→V8**: deposito privato persistente dei file scelti, con nomi e provenienze, senza reinviare da Android.
2. **Render V5 da staging**, sfruttando esattamente la vecchia voce Google e il vecchio FFmpeg: test con una copia di un episodio noto prima di attivarlo.
3. **Cache Gemini** per traccia audio + tempi di parola con chiave hash da testo/modello/istruzioni, in deposito non pubblico per evitare una nuova chiamata quando non cambia nulla.
4. **Anteprima visuale vera** delle scene con le immagini (non soltanto l'elenco testuale) e pulsanti Android per approvare/sostituire.
5. **Libreria SQLite semplice**: partire da ricerca per testo/descrizione/episodio. Solo in seguito embeddings locali e indicizzazione semantica (sqlite-vec).
6. **Timeline aperta**: eventuale OpenTimelineIO per esportare struttura montaggio, senza sostituire FFmpeg.
7. Gate 2: MP4, revisione su telefono e pubblicazione esclusivamente su comando separato.

## Progetti esterni da valutare, non installati
- [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO): timeline ed editor export, non contenitore di media.
- [sqlite-vec](https://github.com/asg017/sqlite-vec): opzione leggera per futura ricerca semantica; prima una biblioteca testuale senza GPU.
- [FFmpeg](https://ffmpeg.org/): composizione finale, già presente.
- [GitHub Actions](https://docs.github.com/en/actions/reference/limits): limiti gratuiti da rispettare.

**Priorità:** non toccare Google TTS, non aggiungere video-AI a pagamento, salvare tutte le versioni, ridurre i passaggi manuali da Android e provare ogni nuova integrazione in un ramo separato.
