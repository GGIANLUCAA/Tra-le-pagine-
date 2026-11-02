# ArtVision Böcklin V122 — prova fisica 8s di sala fotografica con riproiezione 3D (NON finale)
2 novembre 2026. Continuazione **V121**, senza alterare V106/V107, V112/V113, i quattro slot o la voce Gacrux.

## Risultato realmente prodotto
- **MP4 locale**: `/mnt/data/BOECKLIN_PHOTO_ROOM_3D_PROXY_V122_8S_REVIEW.mp4`
- **2.039.982 byte**; SHA-256 `5f99c77cf433e44e88941e67c4e0704a0655b995e9e75beceb9b4936142f97e2`.
- H264, 720×1280, 20fps, 160 frame, **8,000s**, **muto**. FFmpeg `-xerror` decodifica integrale **PASS**; FFprobe 160 frame.
- Analisi su tutti i frame in grigio 180×320: MAD consecutivo massimo **4,943/255**, mediana **4,014/255**, **0** sopra 35, **0** sotto 0,16. Questi numeri sono solo QA di continuità, non di realismo.
- JPG di nove fotogrammi autentici `/mnt/data/artvision_bocklin_qa_v108/BOECKLIN_V122_3D_PROXY_9FRAMES_QA.jpg`; SHA `fe868ade1bc731aadd4fdbaea28c1ced7a2cffad5cb8239d6dedd4a0022ec31a`.

## Cosa cambia realmente rispetto a V121
V121 era un crop/zoom 2D su fotografia compositata. V122 usa **proiezione prospettica distinta su cinque piani** (parete di fondo, pareti laterali, pavimento e soffitto) con camera virtuale che avanza e arretra, correggendo prospetticamente texture e cornice. La traiettoria di prova è da z=1,8m a z=5,8m e ritorno, yaw circa −9,25°→−11,79°→−9,25°. Nessuna AI e nessuna TTS.

Fonte fotografica **reale**, già recuperata dall'artifact GitHub Actions V120 `13119426005`: *Museum Barberini Innenraum leer*, Daniel Naber, **CC BY 4.0**, [fonte e licenza](https://commons.wikimedia.org/wiki/File:Museum_Barberini_Innenraum_leer.jpg), SHA-256 `ea95335ef66afa225351e1dd423c49d5e84aeb15574e97b965fa25c1d5b91db2`. È il **Museum Barberini**, non l'Alte Nationalgalerie di Berlino. Cornice/dipinto ritagliati dal vero MP4 V106 SHA `c1c54dba4f0198df3a8f82e11513378bccf2831647dca01741163250c857a263`; dipinto terza versione 1883, NG 2/80, **80×150 cm**. Foto cornice Sailko CC BY 3.0 (2018), **non** cornice storica provata.

## QA artistica — limiti importanti
**NON PROMUOVERE.** È una **prova muta**, non un quinto video né una revisione dei due Museum completi. Le dimensioni della stanza (larghezza ipotizzata 8,1m, profondità 13,5m, altezza 3,5m) e posizione del dipinto sono **stimate da una singola fotografia**, non calibrate da rilievo. La riproiezione su piani separati introduce una parallasse geometrica **simulata**, non ricostruzione 3D autentica dell'ambiente; vicino alla porta appaiono deformazioni prospettiche visibili circa 3–5s. Persona presente nella foto originale, non generata. La sala è una composizione dichiarata, **non** installazione reale dell'opera. Non è stato eseguito test Android/sito né ascolto/sincronizzazione dei Critico. **V118/V119 NON PASS**, Gold V25=0.

**Archivio:** tentativo reale di upload MP4 nella Library `/ArtVision/Bocklin/V122_PHOTOGRAPHIC_3D_PROXY_STUDY_NOT_FINAL/`: prima `container_session_expired`, secondo tentativo dalla root `/mnt/data` **`library_storage_limit_exceeded`**. La cartella è stata creata ma il MP4 **non è persistito**; link sandbox solo per sessione corrente. Non eliminare vecchi master per fare spazio, non dichiarare consegna permanente. Connettore Video Library Studio richiede `fileParams` selezionato genuinamente dal proprietario, quindi **nessun import R2**.

**Prossimo gate utile:** eliminare distorsione prospettica della porta e calibrare fisicamente la scena, poi collegare ingresso/uscita al quadro senza tagli o ghosting; soltanto allora valutare una revisione non distruttiva di **Critico Museum** (non toccare i due Cinema già apprezzati) e richiedere QA visiva proprietario. Nessuna settima opera, nessuna spesa, nessuna pubblicazione, nessuna nuova voce Gacrux.