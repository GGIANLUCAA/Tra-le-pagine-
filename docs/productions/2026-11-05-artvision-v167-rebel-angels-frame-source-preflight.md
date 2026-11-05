# ArtVision V167 — Rebel Angels: preflight fotografico (05/11/2026)

## Stato coda verificato
Lettura diretta di `queue/artvision_owner_selected_ten_20261102.json` su main: 20/40 slot tecnici; The Fall of the Rebel Angels 2/4, mancano Critico Museum e Cinema Museum. Nessun MP4 nuovo prodotto in questo preflight. Non modificare la coda.

## Nuova verifica della fonte fotografica (metadati pubblici, NON download)
- File: https://commons.wikimedia.org/wiki/File:Pieter_bruegel_il_vecchio,_Caduta_degli_angeli_ribelli,_1562,_37.JPG
- Opera: Pieter Bruegel the Elder, *The Fall of the Rebel Angels*, 1562, Royal Museums of Fine Arts of Belgium, inventario 584, olio su tavola, **117 × 162 cm**.
- Fotografo Sailko, scatto 9 marzo 2016, fotografia personale licenziata **CC BY 3.0**; attribution + link licenza + indicazione modifiche obbligatori.
- File originale indicato dalla pagina Commons: **3456 × 2304 px, 6.375.902 byte, SHA-1 da metadati Commons `da49389d98e10b95adc0735ad845dd31f010d02e`**.
- Questo SHA-1 è una **dichiarazione di Commons, NON un hash ricalcolato sui byte scaricati**. La pagina identifica l'opera ma non certifica che la cornice sia storica/originale, né dimostra che la foto riprenda un'intera sala museale.
- Ulteriori foto Sailko della stessa opera: `...,_19.JPG` e `...,_23.JPG`; sono candidate indipendenti da esaminare, non asset approvati.
- Verifica web della pagina effettuata 05/11/2026. Tentativo di recupero file da ambiente di esecuzione: **ConnectionError** verso commons.wikimedia.org; nessun JPEG fisico acquisito, nessuna SHA-256 calcolata, nessuna valutazione prospettica/visiva.

## Gate obbligatorio prima di render
1. Recuperare realmente i byte JPEG con sorgente autorizzata, SHA-256 e dimensioni; confrontare SHA-1 con il dato Commons quando si usa l'originale.
2. Ispezionare visivamente foto e cornice per esemplare 584, geometria completa e compatibilità scala 117 × 162 cm. Non chiamare la cornice «originale del 1562» senza documentazione.
3. Recuperare quadro HD autentico già documentato SHA-256 `09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5`; se non disponibile non improvvisare.
4. Per Critico Museum riusare **identica** WAV Gacrux V144 SHA-256 `e50f97bf6bf272bdda3a1b8577acf492f974d5c88d2b336d35cf976c5a814ade`; vietato rigenerare TTS.
5. Rendere un solo candidato per volta, FFmpeg full decode, SHA-256, ZIP CRC, salvataggio durevole + download/readback, QA visiva e diritti territoriali. Nessun Gold, pubblicazione o spesa.

**Conclusione:** metadata/licenza fotografica verificati, ma **Museum rimane BLOCCATO** per mancanza dei byte e della verifica visiva della cornice. I due MP4 Standard esistenti sono intatti.
