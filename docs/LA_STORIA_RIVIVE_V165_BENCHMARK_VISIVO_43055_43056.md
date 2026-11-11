# La Storia Rivive · V165 · benchmark visivo REALE 43055 / 43056 e bocciatura V163

Data 2026-11-01 · issue #144 · ambito esclusivo Restauro storico.

## Decisione esplicita del proprietario

La qualità **OBBLIGATORIA e desiderata per il movimento restaurato** è quella mostrata nei video di esempio inviati in precedenza, specialmente `43055.mp4` e `43056.mp4`. Il fatto che alcune fotografie I2I di Parigi V162 siano piaciute NON approva le altre foto né il filmato V163. Il proprietario ha bocciato le versioni ancora troppo poco realistiche. **Stato V163 = `rendered_rejected_artistic_quality`, mai master V98, mai pubblicabile.**

L'obiettivo non è applicare una semplice tinta ai frame e poi far apparire una foto bella: nella **sequenza che SI MUOVE** devono essere credibili volti, pelle, occhi, capelli, mani, abiti, materiali e profondità, con colore e dettaglio di qualità fotografica **stabili nel tempo**, come nei video esemplari.

## File di esempio confrontati davvero

Due file originali forniti dall'utente e recuperati dalla sua Libreria privata; i video NON devono essere caricati nel repo pubblico né riutilizzati come propri contenuti social senza diritti.

| Ref | SHA-256 effettivo | Dimensione, fps, durata |
|---|---|---|
| `43055(2).mp4` | `86a7dd3d2db0d18ba51b601c3b9a0ad7befe180ff2a2f3e2176abce9c7692cae` | 720×1280 · 30 fps · 20,233 s |
| `43056(2).mp4` | `9db1bbebce888b5cbd9e4fb3dc0a5a4fd13a74a3aeccb188912bdee29a8cfcba` | 720×1280 · 30 fps · 20,967 s |
| `Parigi_1918_V163_Movimento_Restaurato.mp4` | `2d282216f143af515380499806f110c4f35e01671c9e9c770eec17c3c7b1b465` | 720×1280 · 30 fps · 17,000 s · **bocciato** |

I video esempi mostrano, a vista reale, persone spesso in primo/medio piano e figure **nettamente più grandi e leggibili**, pelle e tessuti ricostruiti in modo fotorealistico, colori naturali ma pieni e riprese che occupano quasi tutto il verticale. Il B/N è breve e il reveal a colore ha un effetto immediato. Le due versioni originali contengono una pubblicità di fine video: **non replicare quel cartello**.

Parigi V163: folle lontane con volti illeggibili, dettagli SD morbidi, cast rosso/arancio o sbiadito, fotografia ricostruita molto più nitida della pellicola in movimento, riprese centrali circondate da ampie fasce scure. Soggetto legittimo, risultato visivo **non equivalente** ai due esempi.

**Misura riproducibile sui fotogrammi decodificati**: fra 5 campioni indicativi per video, la frazione mediana di righe con contenuto visivo non piatto è stata `1,000` (43055), `0,948` (43056) e `0,559` (Parigi V163). È una metrica grezza che include titoli/texture ed è sensibile ai soggetti e alla composizione: aiuta a identificare il letterboxing, **NON certifica qualità o realismo**, né è una soglia universale.

## Nuovo requisito editoriale di qualità: identica percezione su FOTO e MOVIMENTO

1. **Selezione della fonte prima dei costi.** Per il risultato desiderato serve una scansione storica possibilmente HD/2K, con persone abbastanza vicine: la fonte SD 720×576 di Parigi V163 non ha dettagli sufficienti per recuperare in modo attendibile tutti i volti. Scartare soggetti in cui cinque scene richiedono crop/zoom estremi e le persone restano minuscole.
2. **Restauro del movimento al livello delle fotografie.** DDColor/RealESRGAN e semplice optical-flow di una foto I2I non ricostruiscono davvero dettagli fotografici **temporali** coerenti. Sono strumenti preparatori e non equivalenti al restauro video generativo/temporale di alta qualità. Occorre sperimentare una vera pipeline temporale source-locked, con verifica dei volti e del movimento; se non disponibile, segnare `motion_restoration_quality_blocked`.
3. **Confronto frame-by-frame a video finito.** Per OGNI scena, fare comparazione a pari formato tra frame B/N originale, video restaurato in movimento e foto I2I. Confrontare con fotogrammi significativi dei due benchmark, osservando vero movimento a colore, capelli, occhi, mani, anatomia, abiti, eventuale sfarfallio e coerenza del soggetto. Non spacciare falsi volti, persone o abiti inventati per restauro storicamente fedele: se qualche ricostruzione non verificabile è artistica, indicarlo esplicitamente.
4. **Campo visivo e ritmo.** Il soggetto deve essere leggibile da smartphone senza ampie fasce nere e senza una finta qualità 4K. Usare un vero 9:16 adeguato, fonti composte per il verticale, crop sensato, cambi di shot autentici; reveal colore rapido e percettibile in movimento, poi tempo sufficiente a vedere i dettagli. Il numero di scene rimane motivato dalla fonte, senza clone di un singolo frame o slideshow.
5. **Regola fail-closed:** se anche una sola scena è mediocre, incoerente o non ha materiale sufficiente, rigenerare quella scena **o scartare la fonte**. Nessun master, nessuna approvazione e nessuna consegna presentata come finale per un `technical_pass` del solo contenitore MP4.
6. **Conservare V98 e i contratti tecnici**: fonte/cinque vere riprese, quattro veri restauri I2I, una sola clip Vidu source-locked quando autorizzata con preventivo/saldo/prepaid ledger, gate V91/V94/V96/V99 sui byte, diritti italiani, QA artistico distinto e niente pubblicazione senza consenso. Questa richiesta di fotorealismo non autorizza POST, acquisti, nuove clip a pagamento o la sostituzione di soggetti storici con altri inventati.

## Comando di confronto locale su video veri (riservato)

```bash
python src/storia_rivive_v165_reference_audit.py \
 --ref43055 '/path/private/43055(2).mp4' \
 --ref43056 '/path/private/43056(2).mp4' \
 --candidate '/path/to/new_candidate.mp4' \
 --out '/path/to/private/qa'
```

Lo script confronta SOLO la presenza di immagine e le caratteristiche visive di fotogrammi autentici, SHA-locked; produce `V165_PRIVATE_REFERENCE_AUDIT.json` e `VISUAL_COMPARE_PRIVATE.jpg` da **guardare realmente**. La comparazione non può mai rispondere `approved=true`; l'esito artistico è umano ed esplicito. Nessun frame da video di esempio deve essere committato nel repo pubblico.

Riferimenti: `docs/LA_STORIA_RIVIVE_V163_RIFERIMENTI_RITMO.md` (regia/ritmo già esistente, non duplicare) e `docs/LA_STORIA_RIVIVE_V99_ANTI_REGRESSIONE.md` (golden V98). ArtVision, WOW LAB, V98 e cron V101 rimangono invariati.
