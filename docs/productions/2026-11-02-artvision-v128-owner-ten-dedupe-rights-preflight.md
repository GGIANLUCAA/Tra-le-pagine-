# ArtVision V128 — 10 opere scelte dal proprietario: deduplica reale e preflight
Data verifica: **2026-11-02**. Owner unico: `6adca191603c8191a90d5190901cd034`.

**Questa scheda NON è una consegna 4×1.** La selezione è stata registrata in
[`queue/artvision_owner_selected_ten_20261102.json`](../../queue/artvision_owner_selected_ten_20261102.json)
e collegata al lock V58. La priorità è dell'utente, non più della selezione autonoma.
Il gate `src/artvision_selected_ten_gate_v128.py` rifiuta Dalí, duplicati senza
conservazione dei master e rendering senza evidenze di diritti, scala, cornice, sala e voce.
Nessun Gold V25, social, addebito o nuova automazione.

## Ordine editoriale deciso

| # | Opera esatta | Museo / inventario | Tela/oggetto in cm (H×L) | Stato al 02/11 |
|---:|---|---|---|---|
| 1 | Bruegel, **The Fall of the Rebel Angels** (1562) | MRBAB Bruxelles, 584 | 117×162 | 1 Cinema V6 legacy verificato; non 4×1 |
| 2 | Waterhouse, **The Lady of Shalott** (1888) | Tate N01543 | 153×200 | Fonte e frame da validare |
| 3 | Rembrandt, **The Night Watch** (1642) | Rijksmuseum SK-C-5 | 379,5×453,5 secondo scheda museo | PD, immagine HD/frame da acquisire; distinguere supporto vs area dipinta |
| 4 | Bruegel, **The Tower of Babel** (1563), **grande versione di Vienna** | KHM GG 1026 | 114,4×155,5 | Frame 135×176×6,5 cm documentato; **download KHM solo uso privato** |
| 5 | Simberg, **The Garden of Death** (1896), **acquerello Ateneum** | FNG A II 968:16 | 15,8×17,5 | Piccolissimo: NO falso ingrandimento; distinguere affresco Tampere |
| 6 | Bruegel, **The Triumph of Death** (1562–63) | Prado P001393 | 117×162 | 1 Cinema V25 legacy verificato; copertina da correggere; immagine 2126×1517 |
| 7 | Waterhouse, **The Magic Circle** (1886) | Tate N01572 | 182,9×127 | 1 Cinema V25 legacy verificato; copertina da correggere |
| 8 | Blake, **The Ghost of a Flea** (1819–20) | Tate N05889 | 21,4×16,2 | Miniatura: frame documentato ~38,2×32,4×5 cm; foto/diritti da verificare |
| 9 | Delacroix, **The Death of Sardanapalus** (1827) | Louvre RF 2346 | 392×496 | Preflight immagine/licenze; review per violenza e nudità |
| 10 | Dalí, **The Temptation of St. Anthony** (1946) | MRBAB, Fundació Dalí P 625 | 89,5×119,5 | **BLOCKED COPYRIGHT**: nessuna riproduzione/video/derivato senza licenza esplicita |

Ordine alterna mostruoso/romantico, piccolo/monumentale, meno noto/celebre; Dalí
rimane nella scelta del proprietario ma non passa al render senza licenza.

## Prove FISICHE recuperate in questo ciclo (materiale precedente, non nuovi MP4)

| Opera | Provenienza reale | MP4 byte | Durata | SHA256 | QA |
|---|---|---:|---:|---|---|
| Fall of Rebel Angels | Library `/ArtVision/ArtVision_Bruegel_20261027.mp4` | 19.376.181 | 55,250 s | `0bd2fb6e0aadd02ae1eab56fa804f5fcb914c15330121765e28ba5878531f12a` | FFmpeg full decode PASS, H264/AAC 1080×1920 |
| Triumph of Death | GitHub Actions artifact `12508078179`, run `39968852801` | 12.035.085 | 54,625 s | `635274e289cdcd81021eb6ec0599d2876e71a61754d2c65974b729f50c75039b` | nested ZIP CRC PASS, full decode PASS, H264/AAC 1080×1920 |
| Magic Circle | GitHub Actions artifact `12507493208`, run `39968852801` | 12.539.862 | 53,167 s | `9e0375eef40ef4e7796b9017091b862661b63384a7961e64d84d8c6d97aa4110` | nested ZIP CRC PASS, full decode PASS, H264/AAC 1080×1920 |

Questi sono **tre vecchi Cinema autonomi**, NON tre nuove serie, NON nuovi slot
Critico/Museum, e NON prova di sito/Android. Il campionamento visivo del MP4
ha confermato che le copertine dei due Cinema V25 **non mostrano il titolo
inglese dell'opera, solo il nome dell'artista**: difetto concreto rispetto
all'identità grafica ArtVision approvata. Non approvarli né sovrascrivere master.
Il V6 Bruegel ha titolo inglese ma resta in review artistica.

Sorgenti fisiche riacquisite e hash:
- Bruegel *Fall*, originale Commons/Google Art Project 3840×2772:
  `09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5`.
  Musica *Evening of Chaos*, Kevin MacLeod CC BY 4.0:
  `00a2fee94641761f37e74973eaaa654e1a8a628269f585707d46987558d07573`.
  GitHub source artifact `12775741359`, CRC PASS.
- Bruegel *Triumph*, immagine preesistente 2126×1517:
  `e6f35f29f8d771bcf7b82510ebe430651575e01c2279a7158487c5ee37cecb63`;
  musica *Darkest Child* CC BY 4.0 SHA `7591bd67ba227c2a3ffd97a6751c66e0b56d543ba91a6a2699a765191c880518`.
- Waterhouse *Magic Circle*, immagine 2000×2942:
  `b846a11f640378fa0839e3a31583a128db1db2e91e2938f6fd23a75499c77451`;
  musica *Evening Fall (Piano)* CC BY 4.0 SHA
  `5195c266275c694f9186dceb23e667c45ed74767d97f6615df01021fed3f048e`.

## Fonti primarie e diritti (preflight non equiparabile a licenza universale)

- [Musei Reali Bruxelles, Bruegel 584](https://fine-arts-museum.be/fr/la-collection/pieter-i-bruegel-la-chute-des-anges-rebelles) — data, tecnica, dimensioni.
- [Tate, Lady of Shalott N01543](https://www.tate.org.uk/art/artworks/waterhouse-the-lady-of-shalott-n01543) e [Magic Circle N01572](https://www.tate.org.uk/art/artworks/waterhouse-the-magic-circle-n01572) — Tate 403 nel controllo automatico; metadata Commons, foto e licenze da confermare prima del render.
- [Rijksmuseum Night Watch SK-C-5](https://www.rijksmuseum.nl/en/collection/object/The-Night-Watch-Militia-Company-of-District-II-under-the-Command-of-Captain-Frans-Banninck-Cocq--3137deb45cd7765f9a76084a16c99544) — object marked **Public domain**; [Rijksmuseum policy](https://data.rijksmuseum.nl/policy/) permette anche riuso commerciale quando indicato PD/CC0. Non usare come quadro originale la ricostruzione AI dei margini del 2021.
- [KHM Tower of Babel GG 1026](https://www.khm.at/en/objectdb/detail/323) — **download del sito KHM solo uso privato**, per pubblicazione/uso commerciale occorre verificare un file PD indipendente o ottenere licenza. KHM documenta anche le misure della cornice.
- [Finnish National Gallery A II 968:16](https://kokoelmat.fng.fi/app?si=A+II+968%3A16) — l'originale 1896 è un piccolo acquerello, non il grande affresco successivo.
- [Prado Triumph P001393](https://www.museodelprado.es/en/the-collection/art-work/the-triumph-of-death/d3d82b0b-9bf2-4082-ab04-66ed53196ccc) — Commons dichiara PD-Art, ma in alcune foto metadati EXIF attribuiscono diritti al Prado; verifica file-specifica/territoriale prima di diffondere.
- [Tate Ghost N05889](https://www.tate.org.uk/art/artworks/blake-the-ghost-of-a-flea-n05889) — fonte foto Commons PD-Art, dimensioni del pannello e della cornice da confermare sull'originale.
- [Louvre Delacroix RF 2346](https://collections.louvre.fr/ark:/53355/cl010065757) — opera del 1827, riuso della specifica foto e contenuti espliciti ancora da valutare.
- [Fundació Gala-Salvador Dalí P 625](https://catalogues.salvador-dali.org/catalogues/es/heritageobject/363-981e/) — fotografia segnata © Salvador Dalí / Fondazione, diritti dell'opera ancora protetti: **STOP** senza licenza scritta valida.

## Gate che impediscono un falso 4×1

1. **0 preset sala Museum V119 approvati**; i cinque candidati GAL01–GAL05 non sono asset utilizzabili per video finali. Servono sale/cornici fotocredibili, scala reale e provini video V118/V119.
2. **Nessuna nuova WAV naturale autorizzata da quota Free verificata** per queste opere. Non chiamare TTS e non riusare una voce relativa a un'altra opera.
3. **Diritti per il file esatto, musica e derivati non completamente chiusi**; il caso Dalí è bloccante per l'opera.
4. La consegna richiede 4 MP4 reali, due Critico con stessa WAV/AAC, cover e 16 post, FFmpeg decode/hash, ZIP CRC e readback su archivio realmente consentito. Non è stato soddisfatto per nessuna delle dieci nuove serie in questo ciclo.

Prossima azione utile: verificare e costruire un **primo** preset Museum V119 realmente credibile con provino e cornice documentata (non galleria raster V114), poi source/rights e WAV zero-spesa verificata. Solo dopo passare ai render sequenziali; conservare i tre vecchi Cinema come candidati, senza contarli come nuove consegne.

**Stato di questa esecuzione:** deduplica e recupero 3 MP4 reali, fonte+musica Bruegel, registrazione coda e lock; **0 nuove serie 4×1 e 0 nuovi MP4 renderizzati**. Gold V25 0, pubblicazioni 0, nuove spese 0.

## Ricerca supplementare cornice Bruegel (02/11)

È stata individuata la [fotografia di Sailko del preciso dipinto Bruegel, Bruxelles inv. 584](https://commons.wikimedia.org/wiki/File:Pieter_bruegel_il_vecchio,_Caduta_degli_angeli_ribelli,_1562,_37.JPG), scattata il 9 marzo 2016 e pubblicata CC BY 3.0 (3456×2304). **Non è ancora accertato tramite ispezione del file che mostri integralmente la cornice**: candidato documentale, non certificazione di cornice autentica, e non autorizza il rendering Museum V118/V119.
