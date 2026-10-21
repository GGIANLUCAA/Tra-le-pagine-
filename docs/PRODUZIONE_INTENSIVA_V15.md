> Aggiornamento: [esecutore autonomo V16](PRODUZIONE_AUTONOMA_V16.md) aggiunge avvio dei renderer preparati e recupero dello stato. Le limitazioni indicate sotto descrivono la versione V15.

# Produzione intensiva V15 — obiettivo 10 video al giorno

Richiesta di Gianluca del 21 ottobre 2026: **almeno dieci video ben fatti al giorno,
con produzione autonoma**. Questa istruzione prevale sulla cadenza proposta nella
V14. Obiettivo di riferimento: 70 video/settimana; 300 in un periodo di 30 giorni.
Sono obiettivi produttivi, non risultati già raggiunti o promesse di crescita.

## Architettura operativa

La capacità va costruita come uno studio con una coda continua. L'agente prepara
ricerca e regia, recupera materiali già riusciti, avvia i motori, gestisce gli
errori e fa il controllo finale. Gianluca può scegliere la direzione e rivedere i
risultati dal telefono: non deve approvare ogni singola operazione già autorizzata.
Il tempo di macchina e il lavoro dell'agente vanno distinti dal tempo dell'utente.

| Stadio | Obiettivo operativo | Cosa produce |
|---|---|---|
| Ricerca e selezione | Scorta editoriale di 30 idee; portare avanti la preparazione mentre altri video renderizzano | Angolo originale, fonti, promessa e serie |
| Preparazione | Almeno 12 pacchetti pronti per il lotto giornaliero, inclusi 2 di riserva | Copione, asset, diritti, storyboard, voce disponibile o costo quantificato |
| Render | Tre lavorazioni parallele iniziali, aumentabili dopo misura delle risorse | MP4, copertina, ricetta e rapporto tecnico |
| Revisione dell'agente | Visione e ascolto, confronto immagini/parole e rispetto della serie | Passaggio, correzione o scarto motivato |
| Consegna e registro | Raggiungere 10 finali distinti controllati | Identità del video, hash, ricetta, esito e data italiana |
| Analisi | Studiare i risultati dei video distribuiti senza rallentare tutta la produzione | Lezioni per il lotto successivo |

Dodici pacchetti e tre render paralleli sono configurazioni di partenza, da
misurare. Le riserve aiutano con gli scarti, ma non garantiscono dieci successi.
La scorta si riempie con storie e opere diverse; cambiare solo musica o titolo
non rende nuovo un contenuto. Non rigenerare automaticamente i video già riusciti.

## Formati e qualità

ArtVision Cinema, Critico e libri restano linee indipendenti. L'agente distribuisce
il lotto fra i motori realmente pronti, secondo materiali e qualità; non esiste una
quota obbligatoria per categorie prive di sorgenti. Visual Music e HyperLumen
richiedono ancora recupero dei generatori prima di diventare linee affidabili.

- Preservare Cinema V6 e Critico V2; stesso linguaggio di serie, regia specifica
  per ogni opera. Nessun modello Van Gogh replicato cambiando soltanto il nome.
- Conservare voce Google, ritmo narrativo naturale e divieto di sottotitoli.
- Usare immagini già disponibili solo se pertinenti; copiare materiale di terzi
  senza diritti non è una scorciatoia produttiva.
- Correzioni e tentativi non sono video aggiuntivi. Un progetto consegna una sola
  versione finale salvo richiesta esplicita di varianti.
- Produzione giornaliera e pubblicazione social sono ritmi distinti. I dieci file
  prodotti possono alimentare archivio e calendario; la distribuzione segue le
  autorizzazioni e la strategia delle singole piattaforme.

## Cosa è stato implementato adesso

1. Policy `config/production_v15.json`: target 10/giorno, lotto massimo 12,
   parallelismo iniziale 3, massimo 2 tentativi prima della diagnosi.
2. Coda `queue/production_v15.json` e comando `src/production_batch_v15.py plan`:
   verifica preflight, originalità dichiarata, tentativi, disponibilità dei materiali,
   necessità di nuove chiamate a pagamento e consegne già registrate.
3. Registro delle consegne: `record` accetta MP4 reale, audio/video presenti,
   ricetta corrispondente e revisioni dell'agente compilate. Lo stesso MP4, ID o
   contenuto non incrementa due volte il totale. Una ricetta o un file cambiato
   rende la ricevuta non verificabile al successivo controllo locale.
4. Relazione giornaliera con numero verificato, elementi pronti, elementi bloccati
   e distanza dal traguardo. La data predefinita è quella di Europe/Rome.
5. Istruzioni GPT e pagina del piano aggiornate: la produzione intensiva sostituisce
   il precedente limite di due video/settimana.

**Limite attuale preciso:** questo modulo controlla e conta la coda, non è ancora
un servizio che genera autonomamente dieci nuove sceneggiature e lancia tutti i
renderer 24 ore su 24. I renderer esistono, ma l'integrazione completa e persistente
tra ricerca, asset, voce, render, revisione multimodale e archivio non è completata.
La coda è inizialmente vuota: non trasformiamo i video già realizzati in finte
nuove produzioni. Non è stato attivato un cron che consumi API senza pacchetti
pronti o senza costo definito. I controlli della revisione sono dichiarazioni
tracciate dell'agente, non una certificazione automatica dell'estetica.

## Piano di sviluppo orientato al volume

| Priorità | Lavoro | Criterio per considerarlo pronto |
|---|---|---|
| P0 — capacità e prima scorta | Audit degli asset; preparare 12 soggetti distinti e misurare un lotto pilota | Per ogni lavoro: tempi effettivi di ricerca, voce, render, revisione, costo ed esito |
| P0 — coda persistente | Collegare le schede V13 ai renderer; registrare presa in carico, stato e ripartenza; evitare esecuzioni sovrapposte | Un riavvio riprende il lavoro senza rifare voci o acquistare due volte la stessa operazione |
| P1 — esecutore parallelo | Adapter per ogni motore pronto; tre render concorrenti; isolamento cartelle; timeout; errore su un lavoro non blocca gli altri | Lotto misto riproducibile e risultati separati per progetto |
| P1 — cache e archivio | Recupero automatico di WAV/immagini verificati e ricette; salvataggio persistente fuori dal solo runner | Ogni retry conserva asset validi e ogni consegna ha anteprima e player verificati |
| P1 — revisione autonoma | Estrarre scene e verificare parlato/immagini/audio con strumenti accessibili all'agente; avviare correzioni circoscritte | Esito tracciato e costi misurati, senza chiamare un controllo ffprobe «revisione artistica» |
| P2 — servizio giornaliero | Collegare scheduler, budget giornaliero, riserve e recupero dei fallimenti | Più lotti reali raggiungono il target entro risorse e quote osservate |
| P2 — aumento capacità | Aumentare parallelismo solo dove servono più risorse; misurare collo di bottiglia | Dieci finali controllati, senza accumulo crescente di revisione o calo di qualità |

Il lotto pilota non impone di restare per settimane a due video: serve a scoprire
il limite tecnico prima di impegnare una produzione continuativa. Le attività
possono avanzare nella stessa giornata dove le dipendenze lo consentono. Non
fissiamo tempi di completamento inventati per integrazioni ancora non misurate.

## Budget e dimensionamento

L'abbonamento ChatGPT non dimostra disponibilità di quote API esterne. Il budget
giornaliero non è ancora definito; i video con chiamate nuove non quantificate
restano in preparazione. Questo non richiede conferme ripetute per lavorazioni già
autorizzate: richiede un limite economico utilizzabile dal servizio automatico.

Dimensionare separatamente minuti di runner, richieste voce/immagini, spazio
archivio e revisione. Esempio puramente aritmetico: dieci render da 45 minuti sono
450 minuti di calcolo; con tre risorse equivalenti il minimo teorico è circa
150 minuti, prima di installazione, attese, errori e revisione. Non è un benchmark
del progetto e non include il lavoro necessario per contenuti originali.

Il rapporto del lotto deve registrare anche gli scarti: se 12 tentativi danno solo
8 finali validi, il risultato è 8/10 e il blocco va affrontato. Nessuna riduzione
silenziosa della qualità per raggiungere il numero.

## Interfaccia della coda per l'agente

Ogni elemento contiene `id`, `content_key` (identità editoriale stabile),
`project_file` (scheda V13 relativa al repository), `status` (`preparing` o
`prepared`), `attempts` e `new_paid_calls_required` (false solo se realmente
verificato). Il preflight deve passare; i campi dichiarati non sostituiscono i file.
Le ricevute richiedono `item_id`, `content_key`, `day`, `video_file`, `recipe_file`
e `reviews`: editorial, visual, audio, rights, ciascuno con status passed e note.
I percorsi sono locali al progetto; i materiali archiviati altrove vanno prima
recuperati e verificati. Nessun dato commerciale privato nel repository pubblico.

```
python src/production_batch_v15.py plan --ledger output/production/ledger.json --out output/production/report
python src/production_batch_v15.py record --ledger output/production/ledger.json --receipt output/production/consegna.json
```

I comandi non programmano pubblicazioni e non sostituiscono la pipeline di render.
Le versioni precedenti restano consultabili come storia del progetto; questa è
la policy corrente per l'intensità produttiva.
