# Socrate Critico V64 — due MP4 di prova veri e ritorno Museum corretto

**29 ottobre 2026. Attenzione: I DUE CRITICO COMPLETI NON SONO STATI PRODOTTI.** Questa è una verifica reale della regia e dell'infrastruttura prima della nuova registrazione Gacrux, non un'altra variante Cinema e non una false-positive V25.

## Filmati reali della prova (prodotti in sessione ChatGPT; NON sono nel repository)

1. `critico_standard_VISUALE_SENZA_VOCE_22s.mp4`, SHA256 `99a0f894448a993a37918b442e12315daeb8802ec36741158c9959a1d0b7e57f`, **1,275,702 bytes**, 22.0s, H264/AAC 720×1280 16fps. Regia dettaglio autentico, musica Water Lily, **NESSUNA NARRAZIONE**. I riferimenti sono master verificati 39775 Bosch V22 e 39762 Ofelia V21.
2. `critico_museum_VISUALE_SENZA_VOCE_22s.mp4`, SHA256 `f0e70a805047e80d1e45a4cd61e1c793b5d0a5ae274bd5f5ed481c500a1c97ef`, **3,458,400 bytes**, 22.0s, H264/AAC 720×1280 16fps. Ricostruzione dichiarata di Met Gallery 632 senza visitatori, foto della vera cornice di Socrate, camera in/out continua. **NESSUNA NARRAZIONE**.

Entrambi i MP4 hanno superato ffprobe, decodifica completa FFmpeg, controllo dei frame e SHA256. La scritta "PROVINO REGIA · VOCE GACRUX ASSENTE" è visibile per evitare confusione con un Critico finale. Il titolo inglese reale è conservato nel frame iniziale. Nessun upload privato o pubblicazione social.

**Pacchetti locali reali, ZIP CRC e contenuto MP4 SHA verificati:**
- `ArtVision_Socrates_Due_Provini_Critico_V64_Completo.zip` SHA256 `18b388f9048baf0f4dcc66648862a8729c25c5c678b3e3b8d140fd917c4281eb`, 6,925,445 bytes, comprende due provini, copione, sorgente del renderer corretto, frame QA, stato/diritti.
- `ArtVision_Socrates_Due_Provini_Critico_V64_Solo_MP4_Android.zip` SHA256 `8a57ec7fd95aa50bb23834d034deaa3e552c7d98ebb43d1aed344826cdc04284`, 4,718,442 bytes, contiene solo i due MP4.

## Difetto tecnico reale scoperto e corretto

Il renderer locale Critico Museum V62 costruiva gli ultimi segmenti così:
```python
for i in range(9):  # i=8 completava già il ritorno
    ...
st=starts[9]
a,b=CAMERA_MUS[8],CAMERA_MUS[9]  # riavviava il ritorno da capo!
```
Questa discontinuità aveva **picco medio RGB MAD 92.32/255 intorno a 19.8125 s**, viola il gate V57 e somiglia ai precedenti Museum che l'utente aveva bocciato.

Corretta la funzione affinché gli otto primi segmenti arrivino alla posa 8; il **ritorno finale continuo** va da `starts[8]` fino all'ULTIMO frame con la posa esatta di partenza:
```python
for i in range(8): ...
st=starts[8]
# smooth poses[8] -> poses[9] during starts[8]..duration, ONCE.
```
Misurazione effettiva nuovo MP4 Museum: **picco 26.98/255**, mediana 12.73/255, nessuno spike isolato con il criterio V57 (picco maggiore di 30 E rapporto >2.7 E eccesso >18). Il nuovo helper riutilizzabile `src/artvision_museum_camera_v64.py` ha test automatici in `tests/test_artvision_museum_camera_v64.py`. **Un gate numerico NON prova la bellezza visiva**: resta controllo umano.

La funzione locale del renderer usata per produrre i provini è stata effettivamente corretta, ma **lo script completo di rendering rimane nell'archivio locale del lavoro ChatGPT**; la nuova utility del repository deve essere importata dagli altri renderer compatibili prima di dichiarare distribuzione completa.

## Il PRIMO blocco ancora non superato

Per entrambi i Critico serve **UNA nuova voce autentica Google Gemini Gacrux** che pronunci il **medesimo copione Socrate di 366 parole**, con relativo SHA256 WAV, cache `VOICE_CACHE_V13.json` e tempi ASR. Il progetto della GitHub secret `GEMINI_API_KEY` non è ancora attestato come Free Tier senza fatturazione. Il workflow `ArtVision V62 Gacrux`, run 40892861596, ha bloccato correttamente la sintesi a zero richieste e zero spese; nessun TTS alternativo autorizzato. Un semplice green CI non equivale ad un WAV.

**Azione necessaria:** proprietario verifica nella pagina API Keys/Projects di Google AI Studio che il progetto associato alla chiave GitHub sia marcato Free Tier e che non abbia fatturazione collegata. Solo DOPO tale prova le due variabili di attestazione possono essere attivate e si può chiamare Gacrux una volta sola, generando e riutilizzando la STESSA cache per render diversi, con la regia Critico V2 e Museum V57 corretta.

**Stato ArtVision 4×1:** 2/4 slot Cinema veri in review. I due Critico ancora `blocked_voice_free_tier_not_verified`. Non trattare i 2 provini strumentali come nuovi video finiti; zero approvazioni V25, nessun import privato certificato. Zero spese per TTS/video.
