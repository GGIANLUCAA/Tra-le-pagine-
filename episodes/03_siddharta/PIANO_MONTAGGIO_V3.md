# TRA LE PAGINE — EPISODIO 03: SIDDHARTA
## Piano finale di montaggio V3 — approvazione dell'opzione A

**Stato:** pianificazione; il MP4 completo non è ancora stato montato. Documento del 18 ottobre 2026.

Il copione di Siddharta (Hermann Hesse), la traccia Gemini in italiano (durata **190,38 secondi**) e il file di allineamento delle frasi sono già stati generati. Il progetto prevede **15 immagini originali e 16 passaggi visivi**. **Non rigenerare voce e copione.** Usare gli asset narrativi creati nel dialogo e aggiungere solo quelli mancanti.

Le scene già generate esistono negli allegati della conversazione e nel container di produzione, **non sono ancora tutte caricate nel repository GitHub**. Questo file non avvia alcun workflow.

## Sequenza audiovisiva esatta

I tempi sono ricavati dai punti di inizio frase in `output/TIMING_FRASI.json` dell'episodio 03 (allineamento della voce). Eventuali piccoli aggiustamenti saranno effettuati ascoltando il file finale.

| # inquadratura | Intervallo audio | Asset | Evento realmente narrato | Stato |
|---|---|---|---|---|
| 01 | 00:00.0–00:25.7 | scena_01 | Apertura: Siddharta ragazzo insoddisfatto presso il fiume; primi piani/cambio lieve a 00:11 senza aggiungere un asset | DISPONIBILE |
| 02 | 00:25.7–00:29.4 | scena_02 | Partenza da casa con Govinda | DISPONIBILE |
| 03 | 00:29.4–00:42.0 | scena_03 | Asceti samana, rinuncia e meditazione | DISPONIBILE |
| 04 | 00:42.0–00:49.7 | scena_04 | Incontro con Gotama Buddha | DISPONIBILE |
| 05 | 00:49.7–00:58.3 | scena_05 | Govinda segue il Buddha; Siddharta prosegue solo | DA GENERARE |
| 06 | 00:58.3–01:07.2 | scena_06 | Kamala nel giardino della città | DISPONIBILE |
| 07 | 01:07.2–01:11.7 | scena_07 | Kamaswami e commercio | DISPONIBILE |
| 08 | 01:11.7–01:25.0 | scena_08 | Lusso e gioco d'azzardo, Siddharta stanco | DISPONIBILE |
| 09 | 01:25.0–01:28.8 | scena_09 | Abbandono notturno della città | DA GENERARE |
| 10 | 01:28.8–01:41.6 | scena_10 | Disperazione sulle rive del fiume e la sillaba Om | DISPONIBILE |
| 11 | 01:41.6–01:59.5 | scena_11 | Vasudeva accoglie Siddharta al fiume | DISPONIBILE |
| 12 | 01:59.5–02:06.7 | scena_12 | Kamala riappare con il figlio, incontro al fiume | DA GENERARE |
| 13 | 02:06.7–02:28.6 | scena_13 | Il figlio fugge; Siddharta capisce di non poterlo trattenere | DISPONIBILE |
| 14 | 02:28.6–02:39.2 | scena_14 | Siddharta maturo comprende la saggezza del fiume | DA GENERARE |
| 15 | 02:39.2–02:51.8 | scena_15 | Govinda anziano ritrova Siddharta | DISPONIBILE |
| 16 | 02:51.8–03:10.4 | scena_14 | Ritorno all'immagine del fiume e riflessione finale | RIUSO della scena 14 |

**Nota:** la prima immagine resta circa 26 s perché introduce il protagonista e le premesse. Prevedere 2–3 variazioni molto lievi sulla stessa illustrazione, senza falsi tagli rapidi. La scena del figlio dura circa 22 s: una nuova inquadratura interna/dettaglio del padre può migliorarne il ritmo senza richiedere altre immagini, e senza anticipare eventi.

## Quattro immagini ancora necessarie

**scena_05.jpg — Separazione da Govinda:** Siddharta giovane osserva Govinda che segue la comunità di Gotama nella foresta. I due hanno fisionomie distinguibili; sentimento rispettoso, non drammatico.

**scena_09.jpg — Fuga dalla città:** Siddharta adulto si allontana di notte dai vicoli della città ricca, lascia alle spalle lampade e ornamenti; tonalità indaco, un solo protagonista riconoscibile.

**scena_12.jpg — Kamala e il figlio:** Kamala ormai matura arriva con un ragazzino sulla riva del fiume; Siddharta in abiti semplici di barcaiolo li incontra. Contenuta tensione emotiva; nessuna morte o violenza grafica.

**scena_14.jpg — Il fiume della comprensione:** Siddharta maturo e brizzolato, stessi tratti del volto, ascolta il fiume al tramonto. È anche l'immagine conclusiva, deve essere più calma, contemplativa e memorabile.

Le immagini devono essere **singole**, verticali 9:16, coerenti nell'aspetto di Siddharta, senza scritte, collage o filigrane, con stile graphic novel 2D pittorico. Nessun testo stampato generato nell'illustrazione.

## Asset già realizzati e mapping ai file

- `scena_01`: `TLP_EP03_SIDDHARTA_V3/images/scena_01.jpg`.
- `scena_02`: `siddharta_e_govinda_verso_l_alba.png`.
- `scena_03`: `asceti_in_meditazione_nella_foresta_чәт.png`.
- `scena_04`: `il_buddha_insegna_sotto_l_albero_della_saggezza.png`.
- `scena_06`: `incontro_al_tramonto_nel_giardino_del_palazzo.png`.
- `scena_07`: `affari_d_oro_nell_emporio_antico.png`.
- `scena_08`: `malinconia_tra_oro_e_dadi.png`.
- `scena_10`: `siddharta_al_tramonto_sul_fiume.png`.
- `scena_11`: `incontro_all_alba_sul_fiume.png` (Siddharta giovane e Vasudeva, controllare visivamente il file).
- `scena_13`: `addio_al_tramonto_sul_gange.png`.
- `scena_15`: `incontro_all_alba_sul_fiume.png` con secondo suffisso nell'archivio (Govinda anziano e Siddharta maturo): verificare a vista quale dei due file omonimi con suffisso sia quello giusto.

La presenza di un nome file in questo piano non significa che sia già nel repository; raccoglierli e prepararli tutti in `scene_premium.zip` prima di lanciare il workflow.

## Montaggio finale in 6 azioni, SENZA ricostruire il progetto

1. Generare solo scene 05, 09, 12, 14; verificare anatomia, età, coerenza, pulizia e nitidezza.
2. Convertire/normalizzare tutte le **15 immagini** in file `scena_01.jpg` … `scena_15.jpg` verticali; includere copertina autonoma `copertina.jpg`, se disponibile. Creare `scene_premium.zip` e caricarlo in `episodes/03_siddharta/` su GitHub.
3. Conservare `testo.txt`, `scene_cues.json` e la narrazione approvata. **Preferire il riuso di `VOCE.wav` e `TIMING_FRASI.json` già pronti**: il workflow V3 attuale richiama Gemini di nuovo; riutilizzo della voce richiede una piccola modalità di montaggio che carichi l'audio esistente. Se non adattiamo il workflow, una nuova generazione Gemini potrebbe avere pause e durata leggermente diverse: in quel caso rigenerare soltanto i tempi delle scene e i sottotitoli.
4. Montare musica discreta, sincronizzare sottotitoli originali sulle parole pronunciate, applicare movimenti lievi e non identici, evitare pause morte e immagini scorrelate.
5. Esportare il MP4 verticale, verificare con ffprobe/visionare interamente audio e frame, controllare che `STATO_IMMAGINI.txt` non dica mai `ANTEPRIMA TECNICA`.
6. Consegnare MP4, copertina coordinata 1080x1920, MP3 voce e pacchetto ZIP; **niente pubblicazione automatica**.

**Decisione editoriale:** il V3 richiede vero controllo di qualità. Se una delle quattro immagini non è conforme, correggere *solo quella*, non rifare voce e copione.

**Stato finale di questo documento:** piano di montaggio terminato. Le quattro scene mancanti e l'assemblaggio completo sono lavori successivi non eseguiti da questa sola pianificazione.
