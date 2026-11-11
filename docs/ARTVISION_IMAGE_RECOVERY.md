# Immagini autentiche: recupero e uso da Android

Il motore Cinema V30 (e i wrapper V31) riusa immagini validate prima di scaricarle.
La Collection del 24 ottobre usa lo stesso acquisitore, con le sue soglie dimensionali.
V27/V29 storici mantengono i loro motori; le modifiche al catalogo editoriale condiviso
non avviano più quei due render. Il workflow editoriale continua a validare il catalogo.

## Simberg: originale persistente

`assets/verified/simberg_wounded_angel/ORIGINAL_ARTWORK.jpg` proviene dal pacchetto
verificato della run `40134086889`, artifact `12576730692`. L'hash è fissato nella
configurazione e in `PROVENANCE.json`. La riproduzione è accreditata a Finnish
National Gallery / Hannu Aaltonen, CC BY 4.0, con ritagli e inquadrature dichiarati.
Il renderer controlla hash, dimensioni e decodifica prima del riuso. Non rigenera
l'immagine e non cambia i master esistenti. Il JPEG nel repository non scade con
l'artifact GitHub; conservarne i crediti anche quando viene copiato altrove.

## Dal telefono

GitHub → repository → Actions → ArtVision V31 Hugo Simberg → Run workflow.
Il runner verifica prima il JPEG incluso, quindi la cache, infine gli URL configurati.
Non occorrono Python o un PC sul telefono. I pacchetti finali restano negli artifact
della run; produzione tecnica riuscita non equivale a revisione artistica approvata.

Se il file incluso e la cache mancano, il workflow tenta anche il recupero del vecchio
artifact, finché disponibile. `artvision_seed_image_archive.py` controlla identità,
URL configurato e hash dichiarato nel pacchetto prima dell'importazione. Accetta
solo archivi di provenienza fidata: un hash contenuto nello stesso ZIP non certifica
indipendentemente autenticità o diritti.

## Politica di acquisizione

- Cache legata alla pagina della specifica opera, manifest con URL e SHA256;
  decodifica, dimensioni e hash ricontrollati ad ogni riuso.
- Scritture temporanee e sostituzione solo dopo validazione; HTML e JSON respinti.
- 400/401/403/404 e altri 4xx diversi da 429: un tentativo, URL sospeso per 24 ore.
- 429: nessun tentativo immediato; `Retry-After` numerico o data HTTP rispettato
  mediante sospensione persistita. Default 5 minuti se assente/non valido.
  Commons e upload.wikimedia.org condividono la sospensione; i due proxy weserv
  condividono un'altra famiglia. Non si aggirano limiti con URL equivalenti.
- Timeout, errori di connessione e 5xx: massimo due tentativi per URL, pausa 2s.
- URL duplicati eliminati. Log espliciti per cache, fallimento, cooldown e successo.
- Collection: originale diretto prima dei mirror; URL effettivo nei metadati.
- Se tutto fallisce: errore esplicito, nessun placeholder, nessun render presentato
  come finito. Scegliere un'altra opera richiede un nuovo brief completo.

La cache Actions è un'ottimizzazione eliminabile, non un archivio permanente.
È separata per workflow e per quadro della matrice: i cooldown non sono un rate
limiter globale fra runner concorrenti. Gli altri quadri non sono ancora inclusi
come originali persistenti. Non confondere più URL con più origini indipendenti.
La parte audio mantiene il downloader precedente e non è coperta da questa modifica.

## Verifica

`python -m unittest discover -s tests -p 'test_artvision_image_acquisition.py' -v`

I test non contattano i musei: simulano cache corrotta, provenienza diversa, hash
errato, HTML, risoluzione insufficiente, 404, 429, 5xx, timeout e recupero ZIP.
La copia Simberg reale è stata recuperata dalla run e riprodotta offline con hash
`c4892eea58c9f8c5b73f1ffbc0deb86536115a8c5c3d92f15da14b11ea7a2b50`.
