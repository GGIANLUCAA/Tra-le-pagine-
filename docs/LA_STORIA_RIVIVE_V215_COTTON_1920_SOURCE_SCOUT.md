# La Storia Rivive V215 — candidata attiva: filatura e tessitura del cotone (1920)

**Stato: SOURCE_RESEARCH_ONLY — non è un video prodotto né approvato.** 02/11/2026.

## Evidenza della fonte

- Scheda ufficiale del file Wikimedia Commons: https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm
- Titolo: *Filature et Tissage du coton (1920)*; descrizione: documentario muto francese; autore indicato **Unknown**; anno **1920**.
- Dati riportati dalla pagina del file: 1.920 × 1.080 px, 524,96 s, 66.553.161 byte, WebM VP9. Dimensioni del **file digitale**, non prova di scansione ottica HD.
- La pagina Commons espone marcature di **public domain** e una dichiarazione di assenza di restrizioni note. Questo NON è una perizia sui diritti residui in Italia, sul riversamento o su materiali derivati. `rights_italy_verified=false`; nessuna pubblicazione automatica.
- La pagina contiene categorie relative alla lavorazione tessile, incluse Rouen e macchinari: non usare tali categorie per attribuire automaticamente **tutte** le riprese a una città, fabbrica o giorno specifico.

## Motivo editoriale

Lavorazione di filatura/tessitura, gesti, macchinari e cambi di scala: potenziale storia industriale con cinque riprese autentiche differenti, più originale dei panorami cittadini già usati. **È un'ipotesi**, non un'analisi visuale del film. V101 deve prima scaricare e decodificare i veri byte, poi V210/V215, V204/V205/V206/V209; verificare cinque stacchi e cinque B/N in movimento leggibili in 9:16.

V214 scansionava i primi 420 s ma il vecchio scout V101 distribuiva 12 campioni sull'intera durata (524,96 s). V215 ora distribuisce i 12 frame entro il segmento analizzato, salva `sampling_window_s=420` e `sampling_period_s=35` nel report, conserva il film originale SHA-locked, e V204/V206/V210 utilizzano lo **stesso periodo registrato**. Nuova cache v4 per non mescolare frame estratti col vecchio periodo. La selezione è ancora un'ipotesi di stacchi; non equivale a frame finale esatto né approvazione artistica.

## Decisione operativa prima di spendere

1. Scaricare l'originale Commons in un run V101 senza provider generativi e conservare SHA/contatto-sheet; scartare se il file non si scarica o il ritaglio mostra scarso dettaglio.
2. Visionare i frame e i lead-in reali: scartare film con cinque finti stacchi, volti sfocati, cartelli o dominanti impossibili da correggere.
3. Verificare licenza/diritti applicabili in Italia e provenienza della digitalizzazione, con fonti esplicite; niente permessi auto-attestati.
4. Solo dopo: quattro veri restauri fotografici I2I e una Vidu dal quinto frame con quota e consenso compatibili col gateway; V91/V94/V96/V99 su MP4, cover, quattro post e ZIP.
5. **Nessun MP4, I2I o Vidu generato da questa scheda.** Nessun credito consumato, nessuna pubblicazione.

Non sostituire mai V98 San Francisco con un nuovo filmato inferiore; ArtVision/WOW LAB restano intatti.

## Esito reale del primo scout HD (02/11/2026) — SOURCE_REJECTED

- [GitHub Actions run V215 #41421362529](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41421362529) **SUCCESS tecnico**: ha scaricato davvero i 66.553.161 byte Commons, film originale SHA-256 `e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9`; 12 PNG 1920×1080 e contatto-sheet reale in [artifact #13130765026](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41421362529/artifacts/13130765026). Non è un MP4 nuovo.
- La pre-selezione automatica V210 precedente aveva **falsamente scelto cinque titoli/diagrammi**: `frame_02` (35s), `frame_04` (105s), `frame_06` (175s), `frame_07` (210s), `frame_11` (350s). Questi cinque NON sono cinque vere riprese cinematografiche utili al restauro V98.
- Ho ispezionato il **vero contatto-sheet 12/12**: 10 frame su 12 sono cartelli testuali su nero; `frame_06` è uno schema/disegno, `frame_10` (315s) mostra realmente bobine e filati. Non ci sono cinque scene autentiche cinematografiche nel campione. Le parole dei cartelli e la grafica non devono diventare «volti restaurati» con I2I.
- Il nuovo filtro V216 intercetta i cartelli ad alto contrasto su nero **prima** del ranking: nei 12 PNG del pilot, 10 hanno frazione pixel quasi neri ≥ 0,70 e pixel chiari ≥ 0,02 (campionamento 160×90). Il filtro è conservativo e non sostituisce la revisione di scene notturne o il giudizio umano; la prova locale sui PNG reali evidenzia solo due campioni non classificati come cartelli, uno dei quali è uno schema.
- **Decisione:** `source_rejected` per questo candidato specifico nel ciclo V101; nessun restauro, nessuna clip Vidu, nessun video finale, nessuna spesa. Il film rimane una fonte documentaria valida per ricerca storica, ma non soddisfa questo formato 4+1. Passare a un nuovo soggetto con 5 vere riprese di persone/oggetti, non insistere con l'I2I sui cartelli.
