# La Storia Rivive V295 — audit dei master esistenti (2026-11-05)

## Esito operativo

- **Nuovi finali verificati:** 0
- **Nuovi render:** 0
- **Nuove chiamate video IA a pagamento:** 0
- **Pubblicazioni social:** 0
- **Import privati completati:** 0
- **Coda ArtVision modificata:** no
- **Coda V15 modificata:** no; La Storia Rivive non ha un adapter V15 supportato e nessun pacchetto è pronto per la consegna.
- **Stato complessivo:** `rendered_needs_review` / legacy, non finale e non sincronizzato.

Il controllo ha recuperato i file reali dai release asset e dagli artefatti GitHub, verificato la decodifica completa con FFmpeg, calcolato gli hash esatti, misurato l'audio e ispezionato contatti visivi campionati. Non è stata registrata una review V16: non è stata eseguita una visione/ascolto umano integrale e nessun file supera ancora diritti, qualità artistica e pacchetto V55.

## Master controllati

| Soggetto | SHA256 MP4 | Durata | Audio misurato | Esito |
|---|---|---:|---:|---|
| Bombay 1929 V98.1 | `9babcdce55d5b7090e6b40dd0480ce4d91a8c2416f1ac71a4e1a8c39a1d75119` | 19.13 s | -30.86 LUFS, -21.73 dBTP | Decodifica valida e struttura 4+1 visibile; volume troppo basso, diritti Italia e review artistica pendenti. Revisione legacy, non nuovo finale. |
| Paris 1900–1918 V85 | `d5d3b236f441016c5384a40932853d97d18f226529ba5aa23477e69a5fbd6b1e` | 19.80 s | -32.97 LUFS, -23.12 dBTP | Da separare per periodo secondo V293; volume troppo basso. Non finale. |
| Coney Island 1903 V73 | `7d2c7714fd46efea37b03bd320ec190a516df497073a60de2ba033386604ff47` | 17.58 s | -26.64 LUFS, -9.50 dBTP | Un'unica inquadratura progressivamente colorizzata, non il ciclo fotografico/4+1 richiesto. Scartato come nuovo finale. |
| Venice 1896 V80 | `91e06be4e502bed4934bc1ee20d6167ee1762d54d72323639f3035fb5bab77ee` | 23.93 s | -28.57 LUFS, -17.13 dBTP | Cicli leggibili ma qualità legacy DDColor/upscale; manca prova V98 di immagini I2I moderne e movimento finale idoneo. Non finale. |

## Incidente del test Finegrain gratuito

Il primo test gratuito era stato estratto a 0.65 s da Bombay, cioè da un fotogramma con titolo. L'output ha alterato il testo del titolo e non ha prodotto colore materiale sufficiente. Il file non è una foto restaurata consegnabile.

Misure sull'output esatto:

- sorgente SHA256: `96967a0d492b855ccf8c071b5130adb20b39537b776b69d6f96985056d8bc1f6`
- candidato SHA256: `a2bf75711f1ebfd1c0214636cff9a52e09a6a233e52bf118a1ced9a1ce625e52`
- saturazione media: 18.682 / 255
- quota pixel con saturazione almeno 18: 0.323258
- esito V295: `REJECTED_IDENTITY_GATE` (`real_colour_present`)
- crediti pagati: 0

## Correzione applicata

È stato aggiunto `src/storia_rivive_v295_photo_identity_gate.py`, con test automatici, e il workflow V294 è stato reso fail-closed:

1. usa un fotogramma B/N senza titolo a 3.05 s;
2. conserva gli hash di sorgente e candidato;
3. blocca rapporti d'aspetto alterati, colorizzazioni solo nominali e perdita strutturale;
4. un passaggio autorizza soltanto la review artistica, mai la release;
5. conserva `PHOTO_IDENTITY_GATE_V295.json` nell'artefatto.

## Blocker aperti

- diritti territoriali Italia non documentati per i quattro master;
- review artistica integrale con visione e ascolto non completata;
- loudness sotto obiettivo sui quattro master;
- nessun pacchetto V55 completo verificato (MP4 + JPEG + 4 post + fonti/diritti + ricetta + ZIP completo + ZIP solo-video);
- nessun import privato verificato nel Video Library Studio;
- Paris deve essere separato per epoca; Coney e Venice richiedono un vero rifacimento, non un semplice cambio titolo/musica.

Finché questi blocker restano, gli artefatti sono materiale di revisione e lo stato archivio è `archive_sync_pending`, non una consegna finale.
