# VIDEO LIBRARY DOSSIER V1 — Regola per ogni nuovo video

**Data:** 24 ottobre 2026. **Valida per tutti i generi**: ArtVision Cinema, Critico, Music Motion, Tra le Pagine, Cronaca e nuove categorie.

## Principio obbligatorio

Ogni video ha un solo originale MP4 nell'archivio e un dossier legato al suo nome tecnico. Nessuna copia dello stesso master per pubblicare o modificare post. Conservare originali e riferimenti anche durante l'archiviazione delle schede.

## Integrazione ArtVision V55 — consegna e archivio (28/10/2026)

Dopo ogni nuovo MP4 ArtVision, i QUATTRO post devono esistere davvero e corrispondere allo stesso film, non essere un testo generico creato dall'importer. Il percorso privato di importazione prova prima MP4/playback e copertina; la scheda del sito deve poi recuperare i post originali o un dossier persistente confermato. Il full ZIP dinamico disponibile dal dossier include MP4, JPEG, post, ricetta, diritti e QA: non serve duplicare lo ZIP permanentemente in R2, ma il relativo comando deve funzionare quando richiesto. In ChatGPT produrre anche un ZIP autonomo già integro per il download da Android.

**Gate:** la presenza del film nel catalogo NON prova che i post siano sul sito e non prova che lo ZIP firmato sia stato generato con successo. Stato minimo `archive_sync_pending` finché catalogo, lettura video, cover, 4 post e ZIP privato non sono verificati realmente. Seguire `config/artvision_delivery_v55.json`, `docs/REGOLE_ATTIVE.md > ArtVision V55` e `src/artvision_delivery_v55.py`. I servizi possono avere ritardi: ritentare senza duplicati; non inventare upload, non sovrascrivere schede storiche.

## Automazione già collegata

1. Il workflow esistente .github/workflows/video-library-enrich.yml controlla i video importati.
2. Usando l'identità OIDC delle GitHub Actions chiama l'endpoint privato POST /editorial-seed del worker video-library-import.
3. Crea in R2 catalog/editorial/<nome_video>.json il fascicolo base, senza sovrascrivere schede già curate. Per i video solo su ChatGPT viene proposta una scheda dinamica quando si apre il fascicolo.
4. L'endpoint privato GET /api/editorial recupera anche produzione/notes.json e gli allegati reali produzione/files/<nome_video_codificato>/ già esistenti.
5. I dati non verificabili rimangono da compilare: la bozza di default non significa licenza valida o video pronto alla pubblicazione.

## Obblighi della produzione futura

Al termine di ogni video l'agente deve consegnare o rendere disponibile quanto realmente conosce:
- titolo editoriale specifico, genere, progetto, lingua, data, durata, risoluzione, formato e stato del master;
- quattro testi ORIGINALI e adatti a Facebook, Instagram, TikTok e YouTube, un hook realmente pertinente e hashtag sobri (3–6 quando opportuni);
- titolo della musica, compositore, autore/interprete della registrazione, fonte, termini di licenza e credito obbligatorio se verificabili;
- fonti delle opere e immagini, crediti, permessi e URL consultabili;
- regia scelta, storyboard/scaletta delle scene, script/voce se presente, sincronizzazione musicale quando richiesta;
- prompt, ricetta di produzione, codice e workflow realmente usati, link al progetto o al run GitHub, parametri importanti e controlli qualità;
- master e versioni, identificativo originale, edizione, numero di copie/ristampe solo quando conosciuti, dati di pubblicazione;
- copertina dal video originale, non immagine ricostruita spacciata per un frame reale.

**Vietato inventare** musiche o licenze, fonti visive, link inesistenti, testimonianze, regia specifica o scene non note. Tutto ciò che manca è segnato "Da verificare". I testi automaticamente generati sono bozze da rivedere e non verifiche dei diritti.

## Chiarimento V37 — testo pubblico e archivio realmente persistente (26 ottobre 2026)

La regola editoriale da applicare e quella V28, rafforzata su richiesta dell'utente: non creare una disciplina concorrente.
- Nella scheda di ogni video, **Post social** contiene solo copy destinato al pubblico (quattro varianti autonome, hook, descrizione breve, crediti pubblici dovuti). **Regia e ricetta**, **Ricerca**, **Crediti e fonti** contengono dati specialistici privati.
- Ogni variante si salva nel record R2 `catalog/editorial/<chiave-video>.json`, e si recupera dal telefono mediante la scheda video e nel pacchetto ZIP. Il salvataggio non deve sostituire un testo storico curato.
- I nuovi video senza testi originali non ricevono post precompilati di routine: hanno campi da scrivere e lo stato `bozza/da_revisionare`.
- Impedire la transizione allo stato `approvato` o `pubblicato` quando mancano i post, sono identici, contengono note di produzione o slogan boilerplate. Il controllo letterario e fattuale resta manuale.
- Una modifica ai testi social **non comporta rimontaggio** e non duplica l'MP4 master. Senza importazione nel sito, il dossier non si materializza automaticamente in R2: dichiarare lo stato reale.

## Dove si trova e come si usa

Dalla gestione privata su https://video-library-studio.600led.workers.dev aprire Scheda → Dossier completo / ZIP social.

Nel Dossier sono disponibili: schede/post Facebook, Instagram, TikTok, YouTube, crediti, fonti, sceneggiatura, storyboard, regia, prompt e ricetta, materiali originali e campi di pubblicazione.

Il pacchetto ZIP è generato soltanto su richiesta, mai salvato in più copie permanenti:
- ZIP completo: MP4 originale + copertina + quattro post + scheda JSON + regia + ricetta + crediti + allegati reali disponibili (esclusi ZIP preesistenti).
- ZIP leggero: gli stessi documenti, foto e materiali senza MP4; usabile anche per un video solo su ChatGPT.

Entrambi usano URL temporaneo firmato, non pubblico e senza inserire la chiave amministratore nell'URL del download. Nessuna pubblicazione automatica.

## Precedenze e compatibilità

Questa regola è ADDITIVA rispetto agli standard Cinema V6, voce V13, V19, diritti V20, social V28 e autoproduzione V31. Non cambia montaggio, durata, voce, copertine fisse o motori approvati. La presenza del dossier non significa che il video sia GOLD MASTER o pronto alla monetizzazione.

Quando esistono vere descrizioni, ricette o crediti già salvati nello Studio, tali contenuti hanno priorità su bozze automatiche. Non eliminare o sovrascrivere informazioni storiche.

## Software e verifiche

Sorgenti: site/video-library-v2.html; site/video-library-editorial-core.js; site/video-library-importer-with-editorial.js; .github/workflows/video-library-enrich.yml.

Test: tests/video-library-editorial.test.cjs e workflow .github/workflows/video-library-editorial-test.yml validano dossier, salvataggi, crediti ereditati, ZIP con CRC corretto, firme di download e protezione privata. I test del sito verificano anche la riproduzione degli MP4 originali.

Se la semina automatica fallisce, non bloccare il video: mantenere la scheda dinamica e riprovare al ciclo successivo.
