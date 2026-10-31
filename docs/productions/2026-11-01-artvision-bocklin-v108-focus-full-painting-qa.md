# ArtVision Böcklin — V108 QA focus: due panoramiche mancanti nel Critico Museum V106

1 novembre 2026 · **Difetto visivo documentato; nessun nuovo render, nessun Gold V25**

## Fonti e file effettivamente ispezionati

- Libreria privata: `/ArtVision/Bocklin/V106_REVIEW_4X1_ANDROID/ARTVISION_BOECKLIN_4X1_V106_REVIEW_COMPLETO.zip`, materializzato in questa esecuzione, 46.200.145 byte, SHA256 `e864f4803f5094b4a926c687921a0e64a2f2af24fca8087c1bb2be27cd812dc5`.
- Estratti per confronto i byte originali di `01_Critico_Standard.mp4` (V102, SHA `096926e6ffb0de921fca72726deb4a136227150d1d1a224ccd42e329ee903777`) e `02_Critico_Museum_V106_CANDIDATO.mp4` (SHA `c1c54dba4f0198df3a8f82e11513378bccf2831647dca01741163250c857a263`).
- Campionati fotogrammi reali a **24,0 s** e **90,0 s** con OpenCV. Confronto visivo eseguito sui frame; il JPG diagnostico locale **NON** è stato caricato in Library: tentativo respinto con `403 Library LPE indexing requires a trusted producer`. Non dichiarare immagine persistente.
- Piano editoriale: `modules/artvision_critico/production_series/bocklin_isle_of_dead_1883_v100.json`, capitoli 2 e 8, entrambi `focus: intero dipinto`, `zoom: 1`.
- Renderer V102 preservato: `src/artvision_bocklin_critico_render_v102.py`. Per lo Standard usa `full_painting(im)` se `z <= 1.01`, mentre per Museum usa **sempre** `crop(im,x,y,max(1.10,z))` nella spiegazione.

## Difetto osservabile, riproducibile

| Campione | Critico Standard V102 | Critico Museum V106 | Rispetto al focus previsto |
|---|---|---|---|
| 24,0 s | Intero dipinto leggibile, con fondo sfumato | Solo ritaglio verticale sui cipressi e margine della barca | Museum **non** mostra l'intero dipinto |
| 90,0 s | Intero dipinto leggibile | Ritaglio verticale sui cipressi | Museum **non** mostra l'intero dipinto |

Causa deterministica nel renderer originario: la tela sorgente è **4933 × 2628** (orizzontale), l'output **720 × 1280** (verticale). Con `zoom=1.10`, la funzione `crop` ritaglia circa **1343/4933 = 27,2% della larghezza** dell'opera; quindi non può realizzare un'inquadratura d'insieme, anche quando il capitolo richiede `intero dipinto`. V105 e V106 correggono rispettivamente raccordi e micro-movimenti, **non** questa selezione dell'inquadratura.

**Gravità:** difetto di regia semantica documentato su due campioni; non è un problema di decodifica, né prova di disallineamento parola-per-parola. L'ascolto integrale e la sincronizzazione effettiva della voce restano **pending**. Non dichiarare che l'intero film sia stato rivisto artisticamente.

## Decisione conservativa

- **Non modificare** i master V102, V105, V106, gli ZIP V103/V107, i Cinema V100/V101, le 20 varianti precedenti o il copione/WAV Gacrux.
- **Non generare** una nuova versione automaticamente sulla base di un semplice `crossfade`: dissolvere un crop verticale nell'intero dipinto rischia doppia esposizione/ghosting, difetto già rifiutato nel progetto.
- Per una futura **revisione non distruttiva dello stesso slot**, costruire un passaggio geometrico controllato verso `full_painting` durante i capitoli 2 e 8, usando soltanto la riproduzione autentica verificata e verificando continuità, centratura, audio AAC bit-identico, FFmpeg full decode, SHA/readback. Non promuovere un candidato senza QA visiva comparativa.
- Il pacchetto V107 resta il candidato corrente, **V25 Gold=0**, R2/Android playback non verificato; nessuna importazione con `fileParams` inventato. Nessuna spesa, nuova voce, pubblicazione o settima opera.

**Esito di questo ciclo:** nuova criticità visiva concreta identificata e documentata; **0 MP4 nuovi**, **0 import R2**, **0 modifiche ai master**.
