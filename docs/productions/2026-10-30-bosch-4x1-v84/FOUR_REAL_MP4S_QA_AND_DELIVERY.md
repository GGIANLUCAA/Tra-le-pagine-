# ArtVision · Bosch 4×1 — Quarta opera realizzata, revisioni V77–V84 (30/10/2026)

## Fatto reale, senza nuovo Google TTS

Il proprietario ha chiesto «Continua a produrre» dopo aver ricevuto tre opere 4×1. Per la quarta opera precedentemente concordata — Hieronymus Bosch, *The Garden of Earthly Delights* (Museo del Prado) — sono stati ottenuti **quattro MP4 differenti**. Il Critico Standard è il **master originale V22** che l'utente ha caricato come `39775.mp4` e apprezzato per voce/spiegazione. **NON è stato rigenerato**. L'identica traccia Gacrux originale è stata estratta e riutilizzata byte-per-byte nel nuovo Critico Museum. Nessuna nuova Google TTS, nessuna API video a pagamento.

## Identità dei master reali, quattro slot esatti

| Slot | Nome consegnato | Durata | SHA256 dei bytes MP4 verificati | Origine |
| --- | --- | ---: | --- | --- |
| Critico Standard | `01_Bosch_Critico_Standard_Gacrux_V22.mp4` | 124.192667 s | `2c59c58185ed3d7c51d280bf9c8442414cddf163a231fef08fd7a37d657b0ded` | Originale user-upload / Bosch V22 immutabile, 1080×1920 |
| Critico Museum | `02_Bosch_Critico_Museum_Gacrux_V84.mp4` | 124.2 s | `73b1a97d0640123e38184db7f20334c0de4db318594a8dd728ff0e537253854b` | Nuova regia Museum V84, 720×1280 |
| Cinema Standard | `03_Bosch_Cinema_Standard_V77.mp4` | 49.7 s | `90bb86598788c475e0b0599ca505f354da8c5ffccff13016806fdbd5f02aa844` | Nuovo musicale V77, 720×1280 |
| Cinema Museum | `04_Bosch_Cinema_Museum_V80.mp4` | 51.6 s | `67ad38e0c3ec63c6c6a9e2c925252a515208dd357d0e6c26b0c5dd762177d508` | Nuovo musicale Museum V80, 720×1280 |

L'AAC delle **due** versioni Critico è bitwise identico (estrazione FFmpeg ADTS, SHA256 `775232ee40d06176bb4f4462c82d66e7ac0cdcfefc4b4d8c67e9427370b15edb`). Il vecchio copione `modules/artvision_critico/production_series/bosch_giardino_delizie_v21.json` è una ricetta storica, non un ordine per produrre nuovamente la voce o reinserire la domanda retorica finale scartata nel master V22.

### Source e fonti
- Conservazione originale: Museo Nacional del Prado, https://www.museodelprado.es/en/the-collection/art-work/the-garden-of-earthly-delights-triptych/02388242-6d6a-4e9e-a992-e1311eab3609
- Riproduzione pubblica di alta risoluzione: Commons `File:The Garden of Earthly Delights by BoschFXD.jpg`, `https://commons.wikimedia.org/wiki/File:The_Garden_of_Earthly_Delights_by_BoschFXD.jpg`; ottenuta via provider alternativo PD verificato in GitHub Actions `41024818174` artifact `12963745760`, 6800×3871 px, SHA256 JPEG normalizzato `830978840378c93991b16ed9219e1a78343c633aa8b62035fa65bf9f9ff26cd9`; licenza Public Domain Mark. Il file risulta effettivamente presente nell'artifact e nella sessione ChatGPT, **non nel repository come bytes**.
- Musica **Water Lily — Kevin MacLeod** CC BY 4.0, fonte https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035 e licenza https://creativecommons.org/licenses/by/4.0/ , SHA registrazione `b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6`.
- **Museum**: stanza/prospettiva e cornice sono compositi digitali/ricostruzioni creative. **NON sono la vera galleria Prado né una riproduzione documentata della cornice originale.** Le tre scene del trittico sono pixel autentici della foto PD, non animazioni IA. Per una release che pretenda frame autentico vale V80: verificare un fotogramma documentato specifico o dichiarare sempre la ricostruzione.

### Errori di regia risolti (mantenere la versione migliore, evitare regressioni)
- Cinema Museum V77 aveva troppo pavimento e l'avvicinamento sembrava fermarsi nella galleria; V78/V79 correct camera, finitura **V80** con ritorno alla stessa sala. Gate V57 sull'intero Cinema Museum: **1032 frames**, grayscale MAD massimo **34.581/255** vs soglia 35, 0 frame oltre soglia.
- Critico Museum V79 aveva salti nella camera, corretto con scene riordinate/movimenti lunghi; V83 corretto di continuità ma dissolvenze figurative troppo persistenti; **Critico Museum V84** riduce ghosting e allinea inquadrature sui raccordi. Gate V57 V84: **2484 frames**, grayscale MAD massimo **33.926/255**, 0 frame oltre soglia.
- Entrambi i film Museum sono montaggi IN/OUT dello stesso display digitale; movimento per capitoli e dettagli parlati secondo V76/V80.
- Gli altri tre slot non sono stati rigenerati solo per correggere la singola variante, evitando duplicazioni.

### Pacchetti veri nella sessione
- **Completo** `BOSCH_4X1_PACCHETTO_COMPLETO_V84.zip` — **154.136.164 bytes**, **42 entries**, **CRC PASS**, SHA256 `7b9ca1f274cf5cffbd585f42b4b550424b5813c57f4c0d60a9a64c4450c74f56`: quattro MP4 master, cover, 16 post, WAV/registrazione, fonti, ricette, QA e script locali.
- **Android** `BOSCH_4_VIDEO_ANDROID_V84.zip` — **66.325.249 bytes**, 5 entries, CRC PASS, SHA256 `c7e9f50eac0308278c4a6e94d3b01472505234185063d3160b91e8e95ba67463`: 4 MP4 leggeri H264/AAC, compresa copia Android del Critico Standard storico (master 1080p preservato).
- Per ciascuno dei quattro slot esiste una scheda archivio JSON in questa cartella con titolo, fonte, licenza e **quattro post originali FB/IG/TikTok/YT**. Sono testi di staging, NON prova di pubblicazione effettiva.

## Stati e limiti importanti
- Stato: **4/4 MP4 reali renderizzati** (3 nuovi + 1 master originale), **0/4 Gold V25 certificati**; ascolto e visione umana completa di tutti i MP4 ancora da attestare.
- ZIP e MP4 nella sessione ChatGPT **non sono automaticamente salvati in GitHub o Dropbox o nel sito privato**; non fornire sandbox link in turni successivi finché i path non sono verificati.
- **Nessun upload Dropbox BOSCH** autorizzato in questa conversazione: l'autorizzazione precedente era per il pacchetto completo KLIMT con quel percorso preciso. Se necessario ottenere autorizzazione di destinazione prima del trasferimento. Nessun social auto publish.
- Coda e lock V58: solo quattro opere esplicitamente consentite fino a Bosch; **non avviare quinto quadro automaticamente**. Un eventuale quinto quadro passa per decisione editoriale V32 e consenso esplicito.
- QA V57 tecnico non sostituisce approvazione artistica; eventuali revisioni manterranno **lo stesso slot**, aggiornando hash e ZIP.

## Serie iniziale 4×1 ora prodotta
1. Jacques-Louis David — *The Death of Socrates*: 4/4 MP4, pending V25.
2. Gustav Klimt — *The Kiss*: 4/4 MP4, pending V25; ZIP completo caricato in Dropbox su autorizzazione specifica.
3. Katsushika Hokusai — *The Great Wave*: 4/4 MP4, pending V25; pacchetto completo creato ma nessun upload Dropbox certificato.
4. Hieronymus Bosch — *The Garden of Earthly Delights*: 4/4 MP4, pending V25; pacchetto completo creato ma nessun upload Dropbox certificato.

**Le 16 varianti sono un conteggio di slot materialmente renderizzati, non 16 nuovi MP4 di questa sola esecuzione.** Il sistema preserva i master V22 e Cinema preesistenti. Questa documentazione preserva conoscenza/referenze ma NON i grossi bytes master.
