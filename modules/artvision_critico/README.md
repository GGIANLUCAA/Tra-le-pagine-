# ArtVision Critico V1 — Salvador Dalí: il sogno dell'ape

**Modulo additivo** del progetto Tra le Pagine: nessuna modifica ai motori di libri V3/V4/V5 né alla baseline artistica **Cinema V6 Gold Master** Van Gogh/Caravaggio. Non è una nuova versione di V6 e non la sostituisce.

## Scopo
Un approfondimento in italiano di circa 7–10 minuti (durata finale determinata dalla voce), con interpretazione critica facile da seguire, 16 battute e zoom editoriali sulla vera opera:
- ape e melagrana minuscole; gocce; Gala; scoglio e mare;
- melagrana gigante; pesce; prima e seconda tigre; baionetta;
- elefante e obelisco; costruzione geometrica; metodo preparatorio; Freud; conclusione.

Il **punto preciso di messa a fuoco** di ogni passaggio è memorizzato in `dali_sogno_ape.json`. Nessuna animazione generativa del quadro, nessun filtro che alteri le figure, niente musiche copiate dai social. Il motore riusa **identita_visiva_v6.cover/signature** così fascia scura, filetto oro, font, titolo dell'artista e «MUSIC BY» restano coerenti col marchio. La copertina aggiunge solo un sottotitolo alto.

## Voce e sincronizzazione
Tenta prima la **stessa voce Google Gemini / Gacrux** già configurata per i libri tramite `src/gemini_voice.py`, con narratore unico e tempi di frase da Whisper quando disponibili. Se fallisce per chiave/quote/rete, prova **Edge DiegoNeural** e dichiara il fallback nel report. Non sintetizza mai un video in silenzio o con testo letto da un motore offline robotico.

La durata del montaggio dipende dal parlato reale; ogni zoom si lega alla battuta corrispondente. Genera `REGIA_DETTAGLI_E_SYNC.json`, con secondi e focale di ogni sequenza, oltre al copione originale.

## Musica
**Night on the Docks – Piano**, Kevin MacLeod, licenza CC BY 4.0; un'unica registrazione in loop leggero sotto la narrazione, nessun cambio brano.
- https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100135
- https://creativecommons.org/licenses/by/4.0/

Attribuire musica e modifiche nel post pubblico. L'assenza temporanea del download musicale non deve impedire la creazione dell'anteprima con voce.

## Diritti — importantissimo
Il dipinto di Dalí **NON è in pubblico dominio**: © Salvador Dalí, Fundació Gala-Salvador Dalí / VEGAP e diritti delle immagini gestiti dal museo. Le riproduzioni di prova servono alla **revisione privata critica**, non sono un'autorizzazione alla pubblicazione, alla monetizzazione o al caricamento sui social. Prima di pubblicare richiedere le autorizzazioni necessarie o verificare specifica eccezione normativa applicabile alla critica. Il motore produce file **solo in artifact GitHub**, non pubblica su alcun social, non committa le riproduzioni sul repository.

Fonti di verifica:
- https://www.museothyssen.org/en/collection/artists/dali-salvador/one-second-awakening-dream-provoked-flight-bee-around-pomegranate
- https://www.museothyssen.org/coleccion/visor-tecnico/en/one-second-before-the-awakening/
- https://www.museothyssen.org/restauracion/salvador-dali-estudio-tecnica-genio
- https://catalogues.salvador-dali.org/catalogues/en/heritageobject/1199-46ee/
- https://www.museothyssen.org/uso-imagenes-terminos-legales/copyrights

**Data controversa**: la Fondazione Dalí indica c. 1944; il catalogo corrente e gli studi tecnici del Museo Thyssen indicano 1947. Non spacciare l'una per certezza universalmente condivisa.

## Come usarlo da Android
1. GitHub → repo `GGIANLUCAA/Tra-le-pagine-` → **Actions**.
2. Apri **ArtVision Critico V1 – Dalí** → **Run workflow**.
3. Attendi il completamento; apri l'esecuzione e scorri a **Artifacts** → **ARTVISION_DALI_CRITICO_V1**.
4. Troverai **MP4 verticale 1080×1920**, copertina JPG, storyboard sincronizzato JSON, copione, crediti e avvertenza sui diritti.

Il workflow parte anche una volta quando viene creato/aggiornato il proprio file, per realizzare il primo provino. I vecchi workflow, backup e video rimangono intatti.

## Evoluzione
Il modulo resta indipendente: in futuro altri quadri possono avere un nuovo file JSON e un proprio workflow, mantenendo il motore qui come **V1 ripristinabile**. Migliorie di qualità come macro-dettagli certificati dal museo, tracking parola-per-parola, più angolazioni per battuta e musica originale si implementano come V2 separata, dopo revisione umana.
