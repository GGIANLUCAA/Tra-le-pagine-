# Menu rapido video — istruzione da riutilizzare nelle chat

Quando Gianluca chiede un nuovo video o una serie, non partire con un questionario
lungo. Apri un menu breve con valori consigliati già precompilati; lui può accettarli,
modificarli oppure dire “usa le impostazioni consigliate e procedi”.

## Menu da mostrare

1. **Lavoro:** un video oppure una serie (numero di episodi).
2. **Idea / prompt:** testo libero; se ha già dato l'idea, riportala senza chiedergliela
   di nuovo.
3. **Categoria:** arte, libri e fiabe, storia, misteri documentati, musica, cultura,
   altro; se non è chiara, proponi la più adatta.
4. **Format:** ArtVision Cinema senza voce, ArtVision Critico con voce, Racconto di un
   libro, Controluce, Visual Music / HyperLumen, oppure proposta di GPT.
5. **Regia:** stile abituale del format, mix consigliato per il soggetto, o tecniche
   indicate da Gianluca. Di default proponi un mix motivato e non troppo complesso.

## Impostazioni che partono già consigliate

- Obiettivo: contenuto chiaro, coinvolgente e curato, con apertura forte e senza
  clickbait ingannevole.
- Durata: decisa sul contenuto e sulla narrazione reale, non su una quota fissa.
- Fonti e materiali: verificare le fonti; riutilizzare materiale valido e controllare
  diritti prima di generare o montare.
- Copertina, testi social e crediti: includerli quando pertinenti al format e richiesti.
- Voce, lingua e musica: rispettare il profilo approvato del format. Non far scegliere
  ogni volta valori già fissati dalle regole.
- Pubblicazione: mai implicita; creare i materiali non equivale a pubblicarli.

## Fonti e strumenti — opzione preimpostata invisibile per l'utente

Preselezionare `config/editorial_rules.json > media_source_priority` senza
aggiungere domande al menu ordinario. Quando viene chiesto `creami un video`,
leggere `docs/FILOSOFIA_FONTI_MEDIA_V33.md`, recuperare immagini riuscite e
scegliere il **materiale più pertinente alla scena**, non il provider più facile.
Per ArtVision solo quadri autentici; per libri originali coerenti quando lo stock
non basta; Pixabay (`PIXABAY`) per foto/clip adatte e ricerche manuali mirate;
AI Horde solo nel percorso sperimentale esplicito. Registrare asset, licenze,
revisioni e fallback nel dossier. Mostrare queste opzioni soltanto se l'utente
vuole cambiare impostazioni o serve un'autorizzazione reale.

## Selezione fonti senza menu aggiuntivi

Le priorita V33 restano preimpostate. Dopo la definizione delle scene usare il
selettore V34 (`src/source_selector_v34.py`, istruzioni nella guida V34)
per preparare percorso fonte/riuso/creazione senza far scegliere ogni provider
all'utente. Il test manuale Pixabay/Openverse non e generazione automatica di
un video, e non sostituisce approvazioni o verifiche dei diritti.

## Regole di dialogo

- Se la richiesta iniziale contiene già l'idea, il numero di video, il genere o altre
  scelte, segnale come già impostate. Non domandare informazioni già ricevute.
- Chiedere al massimo le informazioni davvero indispensabili; le preferenze opzionali
  hanno un valore consigliato modificabile.
- Prima di avviare una serie, proporre un piano breve con i soggetti degli episodi,
  un'identità comune e variazioni di regia. Evitare copie con lo stesso montaggio.
- Un “procedi” autorizza il lavoro richiesto nella sessione. Non autorizza spese non
  indicate, pubblicazione o modifiche permanenti alle regole.
- Se Gianluca chiede direttamente di iniziare, non fermarsi al solo menu: compilarlo
  con i dati già disponibili, mostrare un riepilogo breve e proseguire.
- Distinguere sempre piano, copione, rendering e video controllato; non dichiarare
  completato ciò che non è stato realmente prodotto e verificato.

Questa istruzione è da aggiungere alle istruzioni di un progetto ChatGPT per renderla
disponibile nelle sue nuove chat. Il solo repository non modifica automaticamente le
chat indipendenti che non lo consultano.
