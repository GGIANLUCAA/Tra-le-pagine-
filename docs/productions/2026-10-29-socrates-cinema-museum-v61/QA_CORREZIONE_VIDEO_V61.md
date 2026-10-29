# Socrate Cinema Museum V61 — correzione video intero, sala senza visitatori

Data 29/10/2026; feedback utente esplicito: il Museum V60 era bello ma mostrava una persona seduta con testa tagliata dal crop. Richiesta: **rifare il VIDEO eliminando la persona, mantenere il testo**, non modificare soltanto la foto.

## Video effettivamente prodotto (un'unica revisione del cinema_museum)
- File: `ArtVision_Socrates_Cinema_Museum_V61_Senza_Persone_Review.mp4`
- **SHA256**: `6ae8a2cb1ad3709bea4bab801ddefdaf8e7a00b3f3f65f50ddd81af8e4414afc`
- **Bytes**: `22854775`
- **38.000s**, 24fps, H264/AAC, **1080x1920**. Origine video render nativo a **720x1280**, con upscale Lanczos a 1080x1920 (non cattura 1080 nativa).
- Studio conservato: stesso dipinto originale Met object 436105, stessa foto della cornice autentica Szilas, stessa Gallery 632 fotografata e ricostruita, stessa camera continua 2.5D e medesima musica originale Water Lily; titolo/cognome primo frame invariati.
- Correzione: **rimossi digitalmente i DUE visitatori seduti e la panca dall'immagine sorgente della sala per TUTTA la durata dell'animazione**, con fondo parete e parquet ricostruito dalla medesima fotografia. Video non girato nell'installazione reale di Socrate.
- Controllo frammenti del VIDEO a 0.08s e 37.5s (apertura/uscita) eseguito: la persona tagliata non appare più. Restanti momenti salvataggio 1/3/5/7s e uscita inclusi nel pacchetto.

## QA tecnico
- Decodifica totale FFmpeg `-xerror -i MP4 -f null -` **PASS**; ffprobe H264/AAC 1080x1920 e durata 38.0s **PASS**.
- Nuovo render 720p senza visitatori 912 frame effettivi, misura V57 `peak=14.801/255`, `median=6.710`, `ratio=2.206`, `reject=false`. Il test numerico esclude solo jump-cut macroscopici, non dimostra qualità artistica.
- Copertina JPEG, 4 post originali con crediti, fonti/licenze registrazioni, ricetta, fotogrammi QA.
- ZIP completo `ArtVision_Socrates_Cinema_Museum_V61_Senza_Persone_Completo.zip` **SHA256** `05971e4b25b177328a23ec4a78279c9e9fc0114cd22c1a3daf4308f2e23efb58`, 25.719.181 bytes; **21 file**, ZIP CRC PASS, MP4 nel pacchetto con identico SHA.
- ZIP Android MP4-only `ArtVision_Socrates_Cinema_Museum_V61_Senza_Persone_Android.zip` **SHA256** `2fd1df574e95d6375215a60ba3899518c6edc88baf5725937b66e2508982acdc`, 22.846.512 bytes; 1 MP4, CRC PASS.
- **Visione/ascolto umano integralmente a velocità reale e V25 approvazione: ancora da fare.** Stato `rendered_needs_review`. File non importato/verificato nel sito privato: `archive_sync_pending`. Nessun social autopubblicato, zero spese API video.

## Conteggio 4×1 corretto
- `cinema_standard`: video originale V55, revisione V59, conta come **un solo slot**.
- `cinema_museum`: V60 originale `60c9653285352272edba9af0b032f4c4e0d4949167074a6513aea566579d8264` **superato** dal nuovo V61 `6ae8a2cb...`, conta come **un solo slot**.
- Due `critico` ancora bloccati da cache Gacrux esatta mancante, stesso identico audio per entrambe una volta ottenuto.
- **Totale fisico: 2 varianti Cinema esistono, 0/4 approvate V25, non 3/4 o 5 video.**

## Regola permanente
`docs/ARTVISION_MUSEUM_NO_CROPPED_VISITORS_V61_20261029.md` integrato in `AGENTS.md`, `docs/REGOLE_ATTIVE.md`, `config/editorial_rules.json` e Contratto Madre 4×1. Predefinita sala senza visitatori; se una persona appare inquadrarla integralmente lungo TUTTA la camera 9:16; niente teste/busti mozzati. La correzione deve riguardare il **video**, non solo un JPG. Nessuna modifica dei master storici.
