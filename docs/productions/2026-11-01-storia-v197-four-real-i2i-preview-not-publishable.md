# La Storia Rivive · V192–V197 — Quattro fotografie AI vere e provino a colori 22,04s

Data: 1 novembre 2026 · Issue #144 · PR #180 · mandato V108.

## Risultati effettivamente prodotti e verificati

Film storico originale: *A Corner in Wheat* (1909), cortometraggio **di finzione recitata**, non cinegiornale. Derivato filmico Commons VP9 1436×1080 con SHA-256 `eacbb947105f9143632e3d4e933ee5e200ba98f5d588c11c552dfb94787de1d9`, crop verticale originale ~603×1072. Riuso come sorgente temporale e visiva: 5 clip B/N in movimento, 5 freeze identici al finale di ogni clip, verificati V189/V190/V191.

Generazione **VERA** image-to-image generativa con spazio pubblico Qwen-Image-Edit e quota gratuita, distinta da DDColor/RealESRGAN:
- Scena 1, finanziere: 576×1024, foto SHA `fc58203726817ed8b5c5ab1b9c34c94ae83c5e92e41d8c59e1e07ef9608c5fa2`, provider free, GH Action [41345246214](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41345246214).
- Scena 2, borsa: 576×1024, foto SHA `d952a39949d1f206aa7967c32aebb92559a5642addb3e22dfe52aa8720d7634a`, stessa Action.
- Scena 3, banchetto: 576×1024, foto SHA `27928588c04f07b924308945f66961e833c6a38313cde9f32547f9b611dc0672`, vero file generato, Action [41344897936](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41344897936). Il report ha respinto il candidato per soglia immagine troppo stretta (minimo lato 850), non per assenza di byte: lo scatto reale è stato scaricato e verificato. **Non promosso dal gate artistico.**
- Scena 4, fattoria: 576×1024, foto SHA `e0870cdf08bf379ea5eb57dc69a550d6d864b0274cb389c266eb454f0ce79d7d`, Free account authenticated, Action [41345932316](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41345932316), saldo addebiti extra zero. Nessun acquisto, nessuna chiamata Vidu.
- Scena 5, granaio: **solo vera pellicola B/N in movimento**. La clip Vidu source-locked NON esiste ancora.

### MP4 V197 creato, scaricabile e verificato in conversazione (NON repository)

`LA_STORIA_RIVIVE_1909_V197_PROVINO_COLORE_NON_PUBBLICARE.mp4`

- 22,04 secondi, 551 fotogrammi, 25fps, 720×1280, H.264 video + AAC musica originale sintetizzata per questo provino.
- 4 sequenze di **vero film storico B/N→freeze dell'ultimo frame→rivelazione fotografica AI→hold colore** di 4,8 s ciascuna.
- Quinta sequenza originale B/N 2,32s, senza Vidu/colore inventato.
- MP4 4.196.745 byte; SHA-256 `e87cf6881b942ef248633c713ebdbd6374afb8cbfe56e2da11068d0343346cff`.
- FFmpeg decodifica completa **PASS**; ffprobe H264/AAC/durata/risoluzione **PASS**; volumedetect media -15,3dB / picco -5,4dB.
- `La_Storia_Rivive_V197_4_Restauri_Anteprima_NON_PUBBLICARE.zip`: 13 file (MP4, 4 fotografie AI, cover bozza, report, 4 descrizioni social, colonna sonora, Vidu source frame); **ZIP CRC e SHA di ogni file PASS**, archivio 9.003.707 byte, SHA-256 `978c6de4267dff5c0eaa64ca55c799cb2b69f3b6f7d850a8b97f05aabba6074e`. Scaricamento sandbox nell'attuale conversazione soltanto, non dichiarare backup GitHub permanente.
- La grafica e il filmato contengono watermark editoriale `PROVINO - NON PUBBLICARE`; i testi social sono bozze non approvate.

## Audit artistico NEGATIVO / blocco pubblicazione

Le quattro fotografie sono vere immagini AI, **ma rappresentano INTERPRETAZIONI** di scena: cambiano alcuni volti, gesti, abiti e oggetti. Scena 1 e 2 hanno correlazione struttura a bassa frequenza rispettivamente 0,632 e 0,5201 e `scene_identity_visual_qa_approved=false`. Non soddisfano la garanzia di fedeltà richiesta dal golden V98. Non usare label `final_approved` e non sottoporre a V99 come se fosse master valido. **Non esportato 4K**: 720×1280 reale encoded, crop originale ~603×1072, foto AI 576×1024.

Bloccanti:
1. **Manca clip Vidu** autentica della quinta scena, ancora non esiste piano preventivo e autorizzazione **per quella precisa scena** con consenso, gate budget, saldo verificato e fonte persistente consentita dal gateway. Non inventare approvazioni né sostituire con un film B/N colorizzato.
2. QA artistico volti/mani/abiti e continuità insufficiente rispetto a V98 (anche se effetto fotorealistico gradevole): rigenerare fedelmente o scegliere riprese originali più dettagliate.
3. Diritti italiani delle specifiche riprese/ristampa/copia e diritto pubblicazione **non approvati definitivamente**, film originale 1909 di finzione.
4. Mancano pass final gate V91/V94/V96/V99 sul **vero master 4+1**, che non è stato ancora prodotto.
5. Pubblicazione social/sito **non eseguita né autorizzata**; quattro post, cover e musica sono materiali in bozza.

## Iterazione successiva effettivamente utile

Usare V197 come riferimento concreto; migliorare **fedeltà dei volti** con confronto su stessi frame, documentare diritti, poi Vidu `balance`/ `plan` gratuitamente con source-lock della quinta scena e per-scena autorizzazione effettiva prima della singola POST. In assenza di provider/diritti/qualità, restare `rendered_needs_review` e non `final_approved`. Non alterare ArtVision, WOW LAB, V98 e cron V101.

## Vidu — verifica gratuita GET sui byte reali, senza saldo divulgato

Workflow [GitHub Actions 41346744470](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41346744470) **SUCCESS**: riutilizza soltanto il precedente `balance` GET della richiesta `storia-v191-balance-20261101`, eseguito nel gateway unico run **41341787914**, che aveva esito `success`. Sanitizzazione dell'artifact pubblico: `api_access_ok=true`, `numeric_balance_disclosed=false`, `no_paid_generation_sent_by_this_job=true`. **Non certifica un numero di crediti disponibile né l'intercambiabilità Pro consumer/API**. Nessuna POST Vidu di generazione e zero spese in questa verifica.

Per trasformare la scena #5 granaio in una vera clip Vidu: usare la stessa immagine/fingerprint SHA V190, renderla fonte *privata* accessibile al gateway senza pubblicarla inconsapevolmente, richiedere PREVENTIVO GRATUITO `plan`, verificare quota e costo reale, ottenere autorizzazione esplicita esattamente per quella scena e importo, poi un solo POST con ledger idempotente e recupero GET. **Non** dichiarare V197 pubblicabile finché questi passi e QA artistico/diritti non sono completati.

## Esame preliminare dei diritti italiani della pellicola (non liberatoria di pubblicazione)

- **Legge italiana**: [art. 32 L. 633/1941](https://def.giustiziatributaria.gov.it/DocTribFrontend/executePrintArticolo.do?articolo=Articolo+32&codiceOrdinamento=0000000000000320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000&id=%7B012E634A-9F52-4452-B7F7-980D83EDE0C6%7D) — 70 anni dopo morte dell'ultimo fra direttore, sceneggiatori/dialoghisti, autore della musica specifica creata per il film. Vedi anche art. 32-ter sull'inizio del computo dal 1° gennaio dell'anno successivo.
- **Archivio primario**: [Library of Congress, A Corner in Wheat](https://www.loc.gov/item/2012600307/) documenta regia/scrittura D.W. Griffith (1875–1948), scrittura Frank E. Woods, produzione Biograph **1909**, categoria *fiction film*. [Wikisource film](https://en.wikisource.org/wiki/Corner_in_Wheat) osserva che l'ultimo autore dell'opera originale è morto nel **1948**, pubblico dominio in paesi con protezione vita+77 anni o inferiore; questa è una corroborazione **editoriale**, non una certificazione legale.
- Quindi la **scadenza economica dell'opera cinematografica originale in Italia appare verosimilmente il 31/12/2018** (70 anni dal 1948) e dal 01/01/2019, assumendo che non esistano altri coautori rilevanti o nuova musica specificamente creata con termini successivi. Il V197 usa musica sintetizzata originale, non la traccia sonora di altre copie.
- Tuttavia la **specifica versione digitalizzata** è un [file Wikimedia Commons](https://commons.wikimedia.org/wiki/File:A_Corner_in_Wheat_(1909).webm) la cui licenza dichiarata è *public domain in the US*, non autorizzazione specifica Italia. Si è usato un suo **transcode VP9 1080p del 2026**, non l'originale LOC da 1,64 GB; eventuali apporti restaurativi tutelabili, condizioni dell'archivio e diritti residuali non sono stati analizzati da un esperto. **Non marcare diritti Italia conclusi, non pubblicare V197**.
- Verifica ulteriore obbligatoria prima di consegnare un master pubblicabile: documentare provenienza originale del transcode, eventuali color grading/nuovi contributi editoriali del file archivistico, musica originale e licenze di tutti gli asset derivati; quindi revisione giuridica finale oltre ai gate Vidu/V98.
