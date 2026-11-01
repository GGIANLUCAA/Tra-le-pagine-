# ArtVision Böcklin V113 — acqua a fuoco senza perdere la sala V112 (candidato REVIEW)
1 novembre 2026. Stesso slot **Critico Museum** di *Die Toteninsel*, terza versione 1883, Alte Nationalgalerie NG 2/80. **Non V25 Gold**.

## Difetto verificato e scelta editoriale
Dal cache temporale della **vera voce Gacrux** (GitHub Actions artifact 13053703331), le frasi «L'acqua è quasi immobile» e «Non ci sono onde drammatiche...» sono pronunciate nel filmato a **29,72–39,70 s** (offset voce 5 s). La V112 in quel tratto mostra soprattutto cipressi e riva: l'acqua è marginale. La V110 aveva corretto il fuoco ma con un ingrandimento 1,95× che provocava un calo di nitidezza documentato del 47,67%; V112 aveva perciò ripreso V109, conservando il difetto semantico.

**V113** usa soltanto pixel reali della V112, correggendo esclusivamente **28,20–41,20 s**: camera virtuale morbida con zoom massimo **1,45×**, centratura più bassa sull'acqua e Lanczos4 con compensazione moderata del dettaglio (unsharp 0,60), ingresso/uscita smooth. Non anima l'acqua e non crea elementi nuovi. Sala digitale V112 e ingresso/uscita rimangono uguali editorialmente, così come tutti gli altri tre slot e tutti i master. **Non** è una settima opera o un quinto video.

## Risultato fisico verificato
- MP4 locale: `/mnt/data/BOECKLIN_CRITICO_MUSEUM_V113_ACQUA_NITIDA_MUSEO_REVIEW.mp4`
- **21.053.055 byte**, SHA256 **`62635982936620472af27b6dcaf20b2586a2d81303674655d9e11f177c17d508`**.
- Sorgente V112 SHA **`a15b42e399077bef9424258d8c198790a7659333f8ff25141bdf4d17a2254f5d`**, verificato prima di scrivere la copia.
- 110,65 s, 720×1280, H264/AAC 20 fps, 2.213 frame, FFmpeg **full decode PASS**.
- AAC demux ADTS SHA **`3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e`**, **bit-identico** a V112/V106/V102; nessuna nuova voce.
- V57 full-frame 180×320: picco MAD **32,184**, **0** transizioni sopra soglia 35.
- Nitidezza relativa media dei frame elaborati 32–38 s: **87,05% della V112**, perdita **12,95%**, rispetto al difetto V110 precedente di 47,67%. Metrica automatica, non approvazione estetica.
- Scansione visiva a 30 timestamp inclusi ingressi/uscite e segmento acqua: nuovo focus effettivamente visibile; **non** equivale a visione/ascolto umano integrale.
- Codice offline: `src/artvision_bocklin_v113_water_focus_balanced.py`, commit `7bd7de280ae0964ce56800b9f0e73ca6c1cbad63`.

## Archivio e limitazioni
Tentato un solo upload del vero MP4 e del renderer nella Libreria privata `/ArtVision/Bocklin/V113_ACQUA_NITIDA_MUSEO_REVIEW/`: entrambi **falliti** per `library_storage_limit_exceeded`. Il piccolo **QA JSON è invece stato caricato e riscaricato byte-identico**, SHA256 `a7847dadcdd5782c053930a76b165f451838701404c8f5870288dfc3b54bc260`. Nessuna cancellazione di vecchi file per liberare quota. Il nuovo MP4 **non ha backup persistente verificato**; link sandbox soltanto della sessione attiva. R2/import e playback sito/Android **non verificati**: Video Library Studio richiede `fileParams` genuino selezionato dal proprietario. Non inventare tale parametro.

La sala Museum è una **ricostruzione digitale**, non l'installazione reale a Berlino. Nessuna nuova AI, TTS, API, credito, social o spesa. Ascolto/visione umana integrali ancora pendenti, **Gold V25=0**. Non sostituire automaticamente V106 persistente nel pacchetto V107; V112 e V113 sono revisioni separate in review.
