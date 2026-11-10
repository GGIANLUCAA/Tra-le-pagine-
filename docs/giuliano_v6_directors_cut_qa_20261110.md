# Terracotta Army V6 — regia finale e audit tecnico

**Versione:** 10 novembre 2026 · Director's Cut localmente rifinita
**Stato:** MP4 e Android decodificati integralmente, ZIP CRC passato. Pubblicazione NON autorizzata.
**Ramo di produzione:** `feature/giuliano-v6-full-documentary-20261110` · PR #249
**Run sorgente:** https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42883398545
**Artifact origine:** 13795685865 (master verificato prima delle ulteriori rifiniture).

## Direzione editoriale

- Tema d'autore: la camera centrale non aperta si comprende anche attraverso le difficoltà reali emerse nello scavo e nel recupero delle superfici policrome.
- Nessun linguaggio da critico d'arte, nessun invito a «guardare» un particolare che non si mostra, nessun falso archivio 1974.
- 23 blocchi narrativi con nuova voce italiana Google Gacrux, 159,36 s, 44 inquadrature, 3 inserti autentici in movimento della Fossa 1 del 2014 (Bairuilong, Wikimedia Commons, CC BY-SA 4.0), 20 sorgenti fotografiche distinte.
- No scritta GIULIANO sulle immagini.

## Autocritica e finitura aggiuntiva V6 Director's Cut

L'autocritica reale delle immagini campionate dalla V6 ha rilevato: titolo mancante durante il primo inserto video autentico; troppa ripetizione dei dettagli dell'armatura con pigmenti; alcuni ambienti esterni verdi ripetuti; ultima inquadratura troppo debole (stivale). Gli interventi sono stati effettuati sulla copia locale, senza rigenerare la voce:

1. **0,00–3,90 s:** titolo inglese tipografico pulito sul vero filmato del 2014.
2. **Scena 15, 47,32–49,54 s:** fotografia archeologica differente, per distinguere le tracce originali della ricostruzione.
3. **Scena 26, 81,51–84,43 s:** fonte autentica dei frammenti archeologici al posto di un terzo close-up di armatura.
4. **Scena 28, 88,38–92,45 s:** nuova inquadratura di guerriero in luogo dell'armatura già vista.
5. **Scena 37, 126,67–130,32 s:** schema originale *esplicitamente* «illustrativo, non in scala» e «camera non scavata». Non raffigura il vero interno del mausoleo.
6. **Scena 41, 143,70–147,83 s:** nuova fotografia di arciere per evitare altro dettaglio duplicato.
7. **Scena 44, 155,26–159,36 s:** panoramica monumentale dell'esercito per la chiusura, al posto del primo piano debole.

## Controllo finale effettivo della copia rifinita

- Master 1080×1920 H.264/AAC, 159,36 s, SHA-256 `80e3e46eaadc5b908235358ceaa8cbbaaa499dc850bdf109cfd80eef19d627da`.
- Android 720×1280 H.264/AAC, SHA-256 `019ed05cc2b80095296c885da759fa1c2a97a31b5c3e3fb55d7ab43b5c36dc73`.
- Traccia audio AAC del master originale e del Director's Cut: **MD5 bitstream identico `3a9c085bb1bca3ff723a21b1cc02f70a`**.
- Decodifica FFmpeg completa del master e del file Android: **PASS**.
- Archivio ZIP completo con crediti fotografici e licenze: **CRC PASS**.
- Revisione artistica dell'utente: **ancora necessaria**, non pretendere equivalenza con un documentario televisivo autentico.

## Distinzione tra sorgente e rifinitura

La run GitHub contiene il primo master V6 automatico. La **Director's Cut rifinita** è stata ottenuta dopo il download, con le modifiche sopra elencate. Non indicare l'artefatto GitHub come se contenesse già queste ultime sette modifiche. Per le prossime produzioni integrare la selezione per scena, gli schemi esplicitamente etichettati e il QA visivo nel renderer prima del caricamento dell'artifact. Non aggiungere interviste finte, video storici sintetici spacciati per reali o contenuti senza licenza.

## Strumenti e idee da rendere operativi
- FFmpeg: editing a timecode e audio bitstream copy, verifica master e versione Android.
- OpenCV (oppure PySceneDetect, BSD-3-Clause): individuazione dei cambi scena e dei duplicati visivi.
- Faster-Whisper: allineamento originale audio per tempi effettivi della narrazione.
- Pillow: schemi scientifici originali dichiarati e titoli cinematografici.

Questo file registra le decisioni e le prove, non sostituisce il controllo del film completo sullo smartphone.
