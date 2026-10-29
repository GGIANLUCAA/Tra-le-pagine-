# Blake Brooklyn 4×1 — revisione Cinema V76, verifica effettiva

Questa revisione sostituisce **solo** i due provini Cinema, non modifica il quadro scelto, il copione di 282 parole, i moduli Museum V73 o la coda automatica. Non è una certificazione Gold Master.

**Esecuzione cloud:** [GitHub Actions run 40944144033](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40944144033). Artefatto: `ARTIVISION_BLAKE_BROOKLYN_V74_ALL_AVAILABLE`.

| Slot | MP4 V76 | SHA256 | Durata | Codec |
|---|---|---|---:|---|
| Cinema Standard | CINEMA_STANDARD.mp4 | `db8ad9c6b8bfafeeeded573cf0f1d2bd2013ca02c321482a3ac189119dd236e0` | 42s | H264/AAC 1080×1920 (render nativo 720×1280, 15fps, Lanczos) |
| Cinema Museum | CINEMA_MUSEUM.mp4 | `e119c34fb5af5bc154b327d14178a724b07bad7807d27e2554008b4492357b19` | 51s | H264/AAC 1080×1920 (render nativo 720×1280, 15fps, Lanczos) |

**QA realmente eseguita:** entrambi decodificati integralmente con `ffmpeg -xerror`, codec/durata controllati, ZIP individuali e complessivo superano CRC. Analisi dei frame a bassa risoluzione: Cinema Standard V74 aveva salto massimo tra frame adiacenti MAD RGB 98,66/255; V76 con dissolvenze brevi (0,32s) è sceso a **30,40/255**. Cinema Museum V76 massimo **21,61/255**, primo/ultimo frame studio con MAD **~2,2/255** nella versione precedente corretta. La scena V75 e V76 mantiene la cornice fuori campo durante i dettagli e la rimostra nel medesimo ambiente di uscita. Il controllo **artistico integrale con ascolto su dispositivo reale rimane da fare**, nessuna approvazione V25 asserita.

**Stato 4×1: 2/4 MP4 reali, NON quattro.** I Critico Standard e Museum non sono stati renderizzati: nessuna prova autorizzata di quota gratuita Gacrux e billing disabilitato sul progetto. Nessun sostituto vocale o API Google ad addebito, non vendere come completi film muti. Copione V74 e generatore dei due Critico conservati nel progetto.

**Fonti e licenze:** dipinto esatto Brooklyn Museum 15.368, sorgente Commons originale SHA1 `75782f11ff654abf909599525b3fa494bf20c4d7`. `Dark Times`, Kevin MacLeod (ISRC USUAN1100747), CC BY 4.0; crediti in ogni post e ZIP. Parete/cornice Museum sono **ricostruzioni scenografiche**, non foto/installazione reale del Brooklyn Museum.

**Archivio sito:** non verificato, nessuna pubblicazione. Il vecchio V75 resta storia di review, non un quinto video. Secondo pilota esplicitamente richiesto, lock V58 globale e owner invariati.
