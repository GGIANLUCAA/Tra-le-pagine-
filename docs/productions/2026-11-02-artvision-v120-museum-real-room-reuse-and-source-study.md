# ArtVision V120 — primo vero provino VIDEO di riutilizzo Museum + 5 sale fotografiche documentate
**2 novembre 2026 — eseguito su richiesta «Continua in autonomia».**

## Motivazione e risultato effettivo
L'utente ha bocciato esplicitamente le sale piatte/procedurali degli ultimi V114/V116/V117 e ha approvato in precedenza il video **The Cyclops — senza strisce corretto** come camera/cornice, e **Hiroshige — Museum Scale** come rapporto fisico reale. La sola V119 di documentazione non bastava: qui è stato **realizzato e verificato un MP4 autentico**, sfruttando i frame del riferimento video Hiroshige dell'utente (senza ridisegnare sale con rettangoli e griglie).

**Prova V120**: *Il cardellino* di Carel Fabritius (Mauritshuis inv. 605, **33,5 × 22,8 cm**), scala paragonabile a quella di *Sudden Shower* Hiroshige nel riferimento (**circa 35 × 24 cm**). Il dipinto appare come una piccola tavoletta sulla parete accanto a un adulto, non come quadro monumentale.

- **Vero MP4 11,00s**: `ArtVision_V120_Provino_Museo_Realistico.mp4`; **720×1280, 20fps, H.264/AAC**, **3.831.467 byte**, SHA256 `2252efad7596314880670406ab65ea5cfa78de92a1bf919f7e7392b49dfb7a8c`.
- **ZIP Android reale, CRC PASS**, cinque membri: `ArtVision_V120_Provino_Android.zip`, **4.016.861 byte**, SHA256 `e940814988e17ccead4257df36f877965c1a8816e71f6fb10159d20c2449d777`. Contiene vero MP4, foglio fotogrammi, QA, READ ME, **codice Python di elaborazione**.
- `ArtVision_V120_Provino_Controllo_Fotogrammi.jpg`: campioni estratti dal vero MP4 ai secondi 0/1/2/3/4/5/5,5/6/7/8/9/10.
- `ArtVision_V120_Provino_QA.json`: diritti, scala, tracking, byte/SHA, limiti.
- **Full decode FFmpeg `-xerror` PASS**; audio originale creato localmente senza API/crediti esterni.
- Esercizio di compositing **pixel-registered** del dipinto autentico, tramite SIFT + RANSAC (stima della planarità/sua proiezione nel video) e interpolazione continua PCHIP, sulla vera sala mostrata nel master approvato di Hiroshige; **5,5 s di avvicinamento e 5,5 s di ritorno mediante inversione temporale perfettamente simmetrica**.
- **Correzione effettivamente eseguita PRIMA del provino consegnato**: le prime versioni da ~14 s mostravano ancora l'opera di Hiroshige dietro Fabritius e titolo sovrapposto; BOC­CIATE, non consegnate. Dopo taratura quad esatta, nuovo video 11s con quadro precedente non visibile nei campioni. Questa è autocritica V44, non una validazione Gold.
- Il video è un'**anteprima tecnica, NON un video Critico/Cinema completo, NON una nuova quinta versione del quadro**, e richiede la revisione artistica del proprietario. La **cornice in legno scuro è scenografica del video Hiroshige, non autenticata per l'esemplare Fabritius**. Il museo digitale che appare nel video non è il Mauritshuis. Sul video si vede *un visitatore del riferimento esistente*, non è stato creato un nuovo personaggio.
- Sorgente V46 Hiroshige: `ARTVISION_HIROSHIGE_MUSEUM_SCALE_ANDROID_20261027.mp4`, **64,7s**, 1080×1920, 24fps, SHA256 `4c652f526b91bb22332055e0484f3a616d1168ae85599bb7e81da197ce29356c`. Fonte Fabritius dalla vera riproduzione di pubblico dominio Commons *Carel Fabritius - The Goldfinch - 605 - Mauritshuis.jpg* SHA fonte `b3c68e063addcb1cb4b49fb58b240750084b74cfb5957d91afa4db688f55830c`, artwork derivato da MP4 Standard V117 autentico già generato.
- **Limiti reali**: non è una sala 3D modellata ex novo; è compositing registrato su un'installazione digitale fotocredibile approvata; colore/materiali e frame non automaticamente idonei ad altre opere, e occorre verificare fonti/diritti dell'intero asset prima di ogni pubblicazione.

## Cinque fotografie di sale MUSEALI REALI reperite come **fonti candidate**, non filmati finali
Un workflow GitHub gratuito e one-shot ha acquisito cinque fotografie esistenti con fonte/licenza e SHA; file ZIP temporaneo nel [run V120 41395451028](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41395451028) **artifact 13119426005**, 9,2 MB, contiene 5 JPG, foglio contatto e manifest.
- Corcoran Gallery of Art, foto Daderot **CC0**, ritratta sala storica con opere/arredi — limitata.
- Museum Barberini Potsdam, foto Daniel Naber **CC BY 4.0**, sala vuota reale ma parete frontale attraversata da porta — candidate per sviluppo prospettico.
- Museo delle Mura Roma, foto Roundtheworld **CC0**, vera sala con pannelli espositivi — ostacoli.
- V&A Room 70, foto 14GTR **CC0**, galleria reale con espositori — ostacoli.
- Game Room contemporary exhibition, foto Loralielo **CC0**, parete scura con arte già presente — ostacoli.

Tutte e cinque sono nel `config/artvision_museum_library_v119.json > real_photograph_research_v120` con url, licenza, nome autore e SHA. **Non equivalgono a cinque scene animate approvate**: servono photo-panoramic research/mapping, diritti e composizione specifica. La V119 dice ancora 5 sale + 5 frame *candidati* in attesa di costruzione e giudizio umano.

## Archiviazione: limitazioni vere, non omettere
- Il video 11s MP4/ZIP è stato verificato **nel container dell'attuale conversazione** `/mnt/data/ArtVision_V120_Provino_Museo_Realistico.mp4` e `/mnt/data/ArtVision_V120_Provino_Android.zip`. Solo i link **sandbox** della sessione sono verificabili localmente, non garantiti nel tempo da Android.
- Tentato upload nella Library ChatGPT `/ArtVision/V120_MUSEUM_LAB`: creata la cartella, ma **tutti gli upload respinti** con `library_storage_limit_exceeded`. **NESSUN byte MP4 salvato in Library**.
- Tentato upload dello ZIP su Google Drive cartella privata `ArtVision - Produzioni da revisionare` via connettore: **403 Forbidden**, non salvato.
- **Non esiste backup definitivo verificato del provino** in sito/Drive/Library. Non dichiararlo pronto per pubblicazione; i file originali V46/V117 restano nei luoghi precedenti; GitHub artifact delle cinque foto ha scadenza 30 giorni.

## V117 interrotto: non confondere il blocco con avanzamento
Workflow V117 [run 41351647619](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41351647619): **Fabritius, Turner, Homer** hanno concluso 2 Critico ciascuno (6/8 totali). Seurat ha fallito: job `124982926865`, *cancelled* durante singola voce Gacrux dopo 100 minuti. Il piccolo artifact Seurat 13105055330 di 180 kB **non contiene MP4 né la voce**. **Non inviare un secondo TTS alla cieca**; prima diagnosi della chiamata incerta e controllo dei saldi. I quattro Cinema preesistenti e le 16 V116 restano intatti.

## Prossima fase
1. Confrontare 11s preview col modello utente originale a velocità normale; chiedere solo feedback artistico sul *provino*, non sugli Standard o sul formato 4×1.
2. Se piace, sviluppare template animati davvero riutilizzabili per scale piccole/medie/grandi; per cornici reali studiare per ogni opera la foto istituzionale V80, altrimenti alternativa scenografica con approvazione specifica; nessuna nuova montatura chiamata autentica.
3. Dopo prove effettive, promuovere solo singoli asset e loro hash in `config/artvision_museum_library_v119.json` — **ora 0 preset approvati**, Gold V25=0 per il provino. Non riprendere automaticamente i vecchi `room_card` di V114/V116/V117.
4. Predisporre backup durevole soltanto se diventa possibile: Library piena e Drive 403 non vanno aggirati cancellando contenuti dell'utente o pubblicando repository.

**Zero nuove chiamate Vidu/video API a pagamento, zero costi provider deliberati, zero pubblicazione social, zero alterazione master esistenti.**
