# Audit artistico correttivo — L'isola del tesoro (27/10/2026)

**Stato della versione consegnata:** RESPINTA dall'utente. Non è un master approvato.

## Evidenze osservate (file MP4 e dossier Drive originali)

- File verificato: `Tra_le_Pagine_ISOLA_DEL_TESORO_VIDEO_2026-10-27.mp4`, circa 189.6 s, verticale 720x1280, H.264/AAC.
- Riferimento utente: `facebook_20261026_150948.mp4`, circa 65.7 s, 360x640, 30 fps. Presenta personaggi colorati e oggetti indipendenti su fondo chiaro: le parti disegnate si completano progressivamente, esplicitando ciò che si sta narrando. NON replicare soggetti/personaggi storici del riferimento.
- Il dossier `REGIA_SCENE.json` marca `estimated_timing: true`. I tempi derivano da stima testuale; non sono allineati con affidabilità alle parole effettive.
- Attorno a 65-74 s torna il disegno del barile `images/42.jpg`, mentre la narrazione è sul complotto di Silver; è un abbinamento concettuale lontano dall'azione narrata.
- Attorno a 84-93 s l'effetto d'apertura dell'isola comincia quasi a vuoto: anziché far apparire gradualmente gli elementi narrativi, rivela un'intera tavola con maschera.
- Attorno a 155 s la nuova rivelazione inizia su carta quasi vuota invece di mostrare un soggetto progressivamente disegnato.
- La mappa `images/06.jpg` è riutilizzata in tre contesti diversi (circa 25-38 s e 176-190 s) senza un motivo illustrato diverso né interazione con la narrazione.
- Gamma seppia/carta ripetuta: non soddisfa la varietà espressiva richiesta.

## Radice dei problemi

1. La ricerca asset è stata condotta per **etichetta tematica** ("Silver", "isola", "tesoro") anziché verificare **soggetto + verbo + significato** della frase narrata.
2. La messa in tempo si è affidata alla durata attesa, invece di allineare voce e testo ascoltato.
3. Gli effetti erano un **wipe di un'immagine intera**: mancavano livelli semantici distinti (personaggio, mappa, croce, nave, ambiente).
4. La verifica tecnica MP4 è stata scambiata per sufficiente qualità editoriale.

## Correzione registica (non è un nuovo montaggio)

**Art direction:** illustrazioni originali coerenti, personaggi ed elementi indipendenti, colori selettivi su fondo pulito. Stile grafico ispirato al principio del riferimento, non copia della sua iconografia. No vignette o composizioni di più scene nello stesso frame.

Esempio concreto:
- «Trovò una mappa»: prima appare il bordo del foglio, poi le coste disegnate, infine la piccola croce rossa; la comparsa è ancorata alle parole “mappa” e “croce rossa”.
- «Il cuoco aveva una sola gamba»: entra per primo il profilo completo di Silver, poi la stampella e soltanto dopo gli elementi del ponte; nessun soggetto viene rivelato attraverso un rettangolo di vuoto.
- «I pirati erano pronti a ribellarsi»: composizione leggibile di uomini che si passano armi o parlano sottovoce, NON una ripetizione della scena in cui Jim ascolta nel barile.
- «Il tesoro era già stato spostato»: cassa aperta e buca vuota, poi un chiaro raccordo verso la grotta di Ben Gunn; niente generica dissolvenza sull'illustrazione.

## Nuovi requisiti di accettazione (solo per questa ricostruzione)

- Ogni scena descrive: **frase ascoltata, soggetto, azione, inquadratura, fonte asset, istante di ingresso, motivazione dell'effetto**. Prima creare il copione allineato e solo poi stabilire il cue.
- Non considerare pubblicabile un render con `estimated_timing=true` se la sincronizzazione voce-immagine non è stata verificata manualmente.
- **Disegno per livelli/oggetti** = costruzione semantica, non opacità che rivela un'intera immagine. Valutazione comparativa a velocità normale.
- Immagine coerente nell'aspetto di Jim, Silver, Billy Bones, Ben Gunn, Hispaniola nelle diverse scene.
- Evitare immagini ripetute senza motivazione narrativa documentata.
- QA 0/3/7 s, estratti parlato + frame, frasi cruciali map/Silver/betrayal/treasure, e assenza di zone vuote per effetti.
- File completo, audio parlato presente, 9:16 pieno schermo e download persistente; nessuna pubblicazione senza revisione artistica.

**Vincolo:** questo audit non autorizza a promuovere la prova precedente né a modificare i master già approvati. Non affermare che l'allineamento è stato risolto finché non vi è misurazione dell'audio.
