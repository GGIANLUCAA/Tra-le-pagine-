# ArtVision Böcklin NG 2/80 — quattro MP4 reali / pacchetto V103 (31 ottobre 2026)

## Opera esatta
Arnold Böcklin, **Die Toteninsel**, terza versione (1883), Alte Nationalgalerie Berlino, numero inventario **NG 2/80**, olio su tavola **80×150 cm**. Fonte istituzionale https://search.smb.museum/en/object/obj-967648 .

**Preservazione:** i due Cinema precedentemente apprezzati dal proprietario restano byte-identici; 5 opere precedenti/20 slot, Socrate/Klimt e relativi ZIP non sono stati modificati. Nessuna settima opera, nessuna pubblicazione, **Gold V25 = 0**.

## I 4 file veri, dopo download dall'artifact e FFmpeg decodifica intera

| Slot | Filename | Durata | Byte | SHA256 | QA |
|---|---|---:|---:|---|---|
| Critico Standard | `Boecklin_1883_critico_standard_V102_GACRUX_REVIEW.mp4` | 110,65s | 5.554.975 | `096926e6ffb0de921fca72726deb4a136227150d1d1a224ccd42e329ee903777` | FFmpeg full decode PASS |
| Critico Museum | `Boecklin_1883_critico_museum_V102_GACRUX_REVIEW.mp4` | 110,65s | 6.222.614 | `03eb6c8a77c4572b7ca83c81088c4b3d499b06802dd996a97a505b6fe768a6ed` | FFmpeg full decode PASS |
| Cinema Standard | `Boecklin_1883_cinema_standard_V100_REVIEW.mp4` | 44s | 5.169.480 | `b176560a2d58e4aba6b782d2f02e3b5d22674fc7e16ea520620c83134bf90f26` | Preservato, FFmpeg PASS |
| Cinema Museum | `Boecklin_1883_cinema_museum_V101_CONTINUOUS_ENTRY_REVIEW.mp4` | 52s | 6.086.102 | `c9f40502b5efdf216ebfe322344aed21f19913a2b869d144b2519bd2b3bd7132` | Preservato, FFmpeg PASS |

Tutti **720×1280 H.264/AAC**. Critico Standard e Museum hanno un'unica traccia AAC **bit-identica**; SHA256 ADTS `3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e`. L'audio Critico è composto da una **singola voce Gacrux** di 98,64s, WAV SHA256 `f567835c07ae952c5d7390122f08ad44a2e3d99d694592ec04de8a30bc6821e5`; allineamento offline Whisper `matched_fraction=0.8628318584070797` su 19 frasi (unmatched interpolati, controllo ascolto integrale pendente). Copione **217 parole, 9 beat**, stesse parole/audio nei due Critico, regia diversa. Due Museum con cornice all'inizio/fine, sala digitalmente ricostruita e NON fotografia dell'Alte Nationalgalerie.

## Provenienza della singola voce e correzione di un vero problema tecnico
- Prime due esecuzioni del workflow V102 fermate prima della voce: run `41227581466` per gate Google e `41231162328` perché runner GitHub senza FFmpeg; **nessuna chiamata TTS eseguita**.
- Terzo run `41231258203` con **secrets.GEMINI_API_KEY2** (secondo account Google AI Studio precedentemente confermato dall'utente Free e senza fatturazione collegata), static FFmpeg funzionante e fonti SHA verificate. **Una sola** vera generazione Gacrux: 98,64s WAV, artifact `13053872125`. Non confondere conferma utente del Free Tier con verifica indipendente di fattura. Il passo video è fallito dopo TTS a causa di **faster-whisper 1.2.1 + PyAV 19** (`open() got an unexpected keyword argument 'metadata_errors'`).
- **Recupero senza nuove chiamate Google** nel run `41231513083`: artifact V102 scaricato con GitHub Actions, WAV SHA verificato, PyAV `17.1.0` pin per ASR compatibile, riconoscimento offline e nuova cache timing, **due MP4 reali** renderizzati da una sola WAV. Run SUCCESS e artifact `13053703331`. Nessuna seconda chiamata Google/TTS. 
- Fonte arte autentica SHA256 `f9a7c33f1b7a2aae03aacd192706faee3740cfd9d1d277516dec39795f405ce3` (Wikimedia PDM); vera foto dell'esemplare incorniciato (2018) Sailko CC BY 3.0, SHA256 `72655ceea488c5f4ecf207dd5a419618685b0ee0c59d553f63cbbba0bb623b65`; **foto cornice visibile nel 2018, non attribuire originale 1883**.

## Backup Library e veri download di ritorno SHA
Caricati nella **Libreria privata** `/ArtVision/Bocklin/V103_QUATTRO_VARIANTI_COMPLETE/`:
- Due MP4 Critico singoli, SHA come tabella sopra.
- `BOECKLIN_4X1_COMPLETO_V103.zip` **27.243.960 B**, SHA256 `468524594b1a69b2c82a49d5d67e1e365b7d9ec83c10df2f5398f70613c16cd9`, 14 file, ZIP CRC PASS. Dentro 4 MP4 reali, 4 cover, 16 post bozza, WAV originale, fonti, README, QA.
- `BOECKLIN_4_VIDEO_ANDROID_V103.zip` **22.760.302 B**, SHA256 `f6ca92297aaf58b9df7bd91e1d11f3950f4f655b73dd815bd3c797578d776bbe`, 5 file (4 MP4+README), ZIP CRC PASS.
- Entrambi gli ZIP sono stati **scaricati effettivamente di ritorno dalla Libreria** e hanno dato SHA identico e ZIP CRC PASS.

**Stato:** produzione 4/4 completata; precedenti 2 Cinema hanno feedback artistico positivo esplicito dell'utente; i 2 nuovi Critico sono in revisione estetica umana. **0 Gold V25**, no conferma riproduzione nel player Android/Cloudflare R2, no pubblicazione social, nessuna nuova API nella fase di recupero. La verifica di fatturazione effettiva Google non è disponibile dai log; il secondo account è dichiarato Free senza billing dal proprietario.
