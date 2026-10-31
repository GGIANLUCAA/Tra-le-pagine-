# La Storia Rivive · V122 — primo film archivistico autentico HD: freeze windows

## Prova fisica verificata il 31 ottobre 2026

- GitHub Actions reale: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41154281234 (SUCCESS, artifact 13024616979). L'archivio `STORIA_V121_ONE_REAL_ARCHIVE_AUDIT_41154281234` contiene il report elaborato **dal video originale davvero scaricato**, non un test con MP4 sintetico.
- Fonte: [*Filature et Tissage du coton (1920)*, Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm). File originariamente caricato di **66.553.161 byte**, SHA-256 `e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9`, decodifica FFprobe 1920×1080, durata 524,96s, larghezza utile teorica verticale 608 px.
- FFmpeg ha estratto 12 PNG autentici con PTS/showinfo e ha proposto 144 tagli di scena a 2 fps/soglia 0.30. Sono **tagli possibili**; alcuni potrebbero essere sfarfallio, graffi, dissolve o falsi positivi. Non indicano 144 vere riprese cinematografiche.
- Dal `SCOUT_REPORT.json` reale risultano **3/12 freeze non utilizzabili** per la regia approvata (almeno 0,9s di movimento originale prima del freeze, all'interno del candidato segmento con margine di 0,05s): `frame_01.png` (PTS zero), `frame_07.png` (262,56s, precedente candidato cut 262,0s), `frame_12.png` (481,36s, cut 480,5s). Altri 9/12 hanno almeno una finestra temporale *plausibile*, ma **nessuna** è per questo automaticamente una vera ripresa distinta, un volto fedele o un video approvato.
- Il film completo e i 12 PNG non sono stati incorporati nel codice: la regression `tests/test_storia_rivive_v122.py` conserva **solamente i timestamp PTS reali e i 144 possibili tagli**, con piccoli raster sintetici usati esclusivamente per testare il selettore. Non è una prova visiva dei volti.

## Correzione V122 proposta nella PR #147 (dipende da #145)

- Prima V101 sceglieva 5 PNG basandosi su punteggi visivi e segmenti V113, anche se una o più scene non avevano una vera finestra temporale per mostrare pellicola B/N **prima** della loro foto restaurata. Il gate successivo V118 le avrebbe respinte, facendo perdere il ciclo.
- Ora `src/storia_rivive_frame_rank_v101.py` ricalcola dalla provenienza PTS V112 e dagli stessi tagli V113 la finestra 0,9–2,5s, con clock razionale e margine intra-shot, riusando `check_source_window`. Le immagini vicine al taglio vengono marcate `pre_freeze_window_viable=false` e **scartate prima della selezione delle cinque**. Cinque riprese candidati distinti rimangono un requisito necessario ma non sufficiente.
- Se le finestre valide sono meno di cinque, il risultato è `INSUFFICIENT_PRE_FREEZE_SOURCE_WINDOWS` e viene registrato come `SOURCE_REJECTED`, senza generazioni o addebiti. Se risultano cinque, V118 **ricontrolla indipendentemente** SHA PNG, PTS, film SHA e movimento vero dei pixel; V119/V120 scartano file alterati e semplice sfarfallio.
- Workflow di audit storico `.github/workflows/storia-v121-real-film-audit.yml` esteso per produrre `FIVE_REAL_FILM_SOURCE_CANDIDATES_V122.json` e un contact sheet con 12 fotogrammi reali solo come artifact di revisione non pubblicato.

## Blocchi e vincoli ancora validi

- **Diritti Italia** su questo documentario con etichetta Commons Public domain **non certificati**. Non pubblicare.
- **Cinque vere riprese cinematografiche**, qualità dei volti, mani e macchinari, nitidezza nativa effettiva e regia **non approvate**. Il 1080p nominale può derivare da vecchio master già ingrandito. Il contact sheet deve essere guardato e confrontato con V98.
- 0 fotografie I2I prodotte, 0 nuove clip Vidu, 0 nuovi MP4/ZIP, 0 crediti usati, 0 pubblicazioni. Nessun cambiamento a V98, ArtVision e WOW LAB.
- Prossima prova utile: verificare il report di selezione V122 e il contact sheet dell'ultimo workflow reale; annotare la qualità artistica e/o cambiare fonte. Solo dopo clearance e valutazione umana è opportuno spendere crediti già approvati.
