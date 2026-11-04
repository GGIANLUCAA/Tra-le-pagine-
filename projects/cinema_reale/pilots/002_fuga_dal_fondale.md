# Pilota 002 — Un animale che sembra sfidare la gravità
project_id: cinema_reale
status: SOURCE_SCOUT_NOT_ARTISTICALLY_APPROVED
updated: 2026-11-04

## Scelta editoriale
Soggetto principale: un cetriolo di mare che si solleva dal fondale e nuota con flessioni del corpo, documentato durante Dive 03 del programma NOAA American Samoa ROV + Mapping Exploration, 29 agosto 2026. Non è un extraterrestre, non vola nell'aria: il movimento è subacqueo reale e non va travisato.

- Fonte: https://oceanexplorer.noaa.gov/multimedia/sea-cucumber-swimming/
- Contesto immersione: https://oceanexplorer.noaa.gov/dive-03-ex2606/
- Video HD NOAA: https://oceanexplorer.noaa.gov/wp-content/uploads/2026/09/ex2606-dive03-seacuke.mp4
- Licenza/credito richiesto dalla pagina: NOAA Ocean Exploration, 2026 American Samoa ROV + Mapping Exploration.
- Scopo: esaminare prima la ripresa vera e scegliere gli intervalli di movimento efficaci, non pubblicare il filmato NOAA tale e quale.

## Candidato alternativo non sovrapponibile
Isopode degli abissi con lunghe antenne che nuota e poi cammina sul sedimento, forse appartenente a una specie nuova. Documentato nella Dive 11 del 10 settembre 2026, circa 5.2 km di profondità.
- Fonte: https://oceanexplorer.noaa.gov/multimedia/unknown-isopod/
- Contesto: https://oceanexplorer.noaa.gov/dive-11-ex2606/
- Video HD NOAA: https://oceanexplorer.noaa.gov/wp-content/uploads/2026/10/ex2606-dive11-isopod_HD.mp4
- Credito: NOAA Ocean Exploration, 2026 American Samoa ROV + Mapping Exploration.
- **Specie non dichiarata nuova**: NOAA scrive soltanto che potrebbe esserlo.

## Concetto regia di prova (da validare su fotogrammi veri)
Nessuna parola, nessuna scritta, nessuna voce, nessun elemento visuale generato con AI. Musica ed effetti sonori originali/licenziati, traccia sonora senza narrazione. Il gesto naturale è tutta la storia: mistero / decollo dal fondale / nuoto completo / gesto di chiusura. La durata va decisa dopo aver visto l'azione, non standardizzata.

Il montaggio NON deve spacciare riprese separate come un unico evento. Se ci sono timbri, nomi o testi già dentro il video sorgente, occorre valutarli e non mascherarli in modo ingannevole. Per social è richiesta sostanziale originalità editoriale, non tagli di stock generici; valutare disponibilità di altre sequenze della stessa immersione per un contributo creativo vero.

## QA prima del render finale
1. Scaricare video NOAA effettivo, verificarne dimensioni, frame rate, durata, hash, fotogrammi a intervalli e crop 9:16.
2. Ricavare punti precisi di hook/svolta/payoff e valutare se la storia si capisce senza spiegazioni.
3. Confermare diritti del video specifico, credit in post/descrizione (in video niente scritte), audio con licenza.
4. Verificare sovraimpressioni già presenti, sicurezza crop, soggetto leggibile e assenza di narrato nel risultato.
5. Render MP4 solo dopo preflight creativo: 9:16, audio completo, intro forte, finale chiaro. Consegna MP4+ZIP scaricabile e QA. Non pubblicare autonomamente.

## Stato vero
Ricerca delle fonti e asset URL verificati come pubblicati dalla NOAA. L'esistenza del file online non certifica frame utilizzabili, originalità artistica né un MP4 finito. Preparato scout remoto GitHub Actions, risultato da controllare prima del montaggio.

## Verifica tecnica reale del 04/11/2026 (GitHub Actions)
- Source scout completato **SUCCESS**: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41887770143
- Artifact di report e contact sheet: ID 13350904039, creato il 04/11, scadenza prevista 18/11. Entrambi i file SD scaricati e decodificati: cetriolo di mare 84.284 s 640×360, isopode 53.787 s 640×360, entrambi H.264 ~29.97 fps. SHA e timecode registrati nell'artifact.
- **Revisione umana dei 12 frame/candidato:** il cetriolo di mare è ben visibile e scenografico da circa 25 a 77 secondi, ma i primi frame contengono scritte NOAA; l'isopode è minuscolo per buona parte del video, inadatto a un crop verticale leggibile senza compromessi. Scelto cetriolo di mare per il test.
- NOAA Media Kit: https://oceanexplorer.noaa.gov/about/media-kit/ richiede il credito della didascalia e avverte che alcune immagini sono soggette a copyright; la pagina specifica https://oceanexplorer.noaa.gov/multimedia/sea-cucumber-swimming/ mostra credito NOAA senza indicazione di copyright. Mettere credito nella descrizione separata, non nel video.
- Avviato render remoto separato, solo FFmpeg CPU, video NOAA HD autentico e colonna sonora atmosferica procedurale originale senza campioni di terzi. Workflow: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/cinema-reale-pilot-002.yml . Output **solo provino da rivedere**, non contenuto social approvato, non pubblicato; la sola riuscita CI non certifica la qualità artistica o l'originalità riconosciuta da Meta.
