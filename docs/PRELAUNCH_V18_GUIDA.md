# Studio pre-lancio V18 — selezione, regia e memoria senza nuove API

## Scopo

Nel progetto **Tra-le-pagine-**, prima dell'avvio dei canali social, prepariamo una scorta di idee, confrontiamo le regie già riuscite e rendiamo leggibile dal telefono un rapporto editoriale. Il software funziona senza servizi AI esterni e non modifica Cinema V6 Gold Master, Critico V2, libri V12, la voce Google o i renderer V16.

## Da Android

1. Aprire **Studio → Scorta pre-lancio V18**: `docs/prelaunch-v18.html`. La pagina legge gli otto argomenti V14 e sedici nuove proposte V18 dal repository **pubblico** GitHub.
2. Cercare argomenti, filtrare per genere, marcare i preferiti. I preferiti vengono conservati nel browser locale; non sono salvati sul server e non modificano GitHub. **Esporta selezione (JSON)** per ottenere una copia e condividerla in una chat futura.
3. Per eseguire i controlli completi: da GitHub Android, **Actions → Pre-lancio V18 → Run workflow**, poi scaricare l'artefatto `editorial-prelaunch-v18`. Dentro ci sono un report mobile HTML e un JSON per la coda, più l'indice ricette.
4. Consegnare le scelte all'agente: recuperare i materiali e le V13 recipe esistenti. L'agente deve distinguere proposta editoriale, scheda con fonti e diritti, e MP4 verificato. Non cambiare una tecnica vincente solo per soddisfare una formula social.

## Funzioni reali

- `src/prelaunch_editor_v18.py` combina `templates/CREATOR_IDEAS_V14.json` con `templates/PRELAUNCH_ADDITIONS_V18.json`, segnala duplicati esatti di tema+angolo, suggerisce verifiche sui titoli simili e usa le domande della policy di qualità V17 per ogni genere.
- Una idea NON passa a preparazione V16 senza riferimenti documentali per fonti/diritti/visivi, scheda V13 compatibile e preflight valido. Nessun punteggio predittivo di views. Il punteggio editoriale esiste **solo quando un revisore lo compila motivandolo**, da 0 a 3 per quattro voci.
- `src/creative_memory_v18.py` cerca `VIDEO_RECIPE_V13.json` realmente disponibili, verifica hash del master, copertina e sorgenti, scrive un indice senza copiare materiali. La presenza/hash corretti **non prova** approvazione artistica; il preset realmente usato va letto dai sorgenti.
- `docs/prelaunch-v18.html` è un pannello consultabile dal telefono; le preferenze locali non sincronizzano dispositivi e si perdono se si cancellano i dati del browser.
- Il workflow GitHub usa il runner gratuito **nei limiti e nelle quote del proprio piano**, senza TTS, GPU, crediti generativi o spese API. Il semplice piano non produce video e non attiva pubblicazioni.

## Che cosa manca ancora

Le 24 idee sono **solo bozze**, non 24 MP4, non 24 episodi fattualmente verificati e non 24 progetti pronti al render. I video precedenti possono esistere in Artefatti, Library o servizi esterni: l'indice ricette cerca solo i file presenti nel checkout, quindi può essere vuoto anche se esistono master già creati altrove. Recuperarli prima di rigenerare o giudicare che non esistano.

Non essendoci ancora un canale social attivo, non ci sono risultati, retention o follower da analizzare; il modulo non crea numeri ipotetici. Meta e YouTube richiedono verifiche su originalità, diritti, provenienza dei materiali e modalità di distribuzione.

## Comandi locali opzionali (l'utente può rimanere su Android)

```bash
python src/prelaunch_editor_v18.py --out output/prelaunch-v18
python src/creative_memory_v18.py --scan output --scan episodes --out output/creative-memory-v18
python -m unittest discover -s tests -p 'test_prelaunch_editor_v18.py' -v
```

I comandi scrivono **solo** cartelle di report nuove. Non sovrascrivono report preesistenti. Lo studio resta libero di usare immagini, TTS e renderer già approvati; è vietato inferire o installare nuove API a pagamento dal solo desiderio di maggiore qualità.

## Strategia pratica

Priorità editoriali prima del lancio: rafforzare critica d'arte e libri narrati, mantenendo Cinema V6 come vetrina. Le altre categorie restano nel laboratorio senza perderle. Preparare una scorta verificata; non confondere l'obiettivo di produzione intensiva di 10 video/giorno con la frequenza di pubblicazione, da misurare dopo il lancio.

Un percorso realistico è: scegliere le idee → controllare catalogo e diritti → costruire brief V13 → preflight qualità V17 → render con il preset valido → ascolto/visione e revisione V16 → archivio e scheda → eventuale pubblicazione autorizzata → dati reali e lezioni. **Nessun passaggio a pagamento viene avviato dal V18.**
