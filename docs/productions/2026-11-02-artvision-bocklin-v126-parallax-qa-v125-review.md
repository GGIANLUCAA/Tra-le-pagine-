# ArtVision Böcklin V126 — QA fisico della camera Museum fotografica (02/11/2026)

**Esecuzione reale:** ispezionati MP4 locali V122/V124/V125 e V113, estratti frame e misurato il moto con OpenCV SIFT/RANSAC. Nessun nuovo filmato finale, nessuna sostituzione di master, nessun Gold V25. V107 e regole V118/V119 restano vincolanti.

## V125: video reale, ma parallasse 3D NON provata

- File: \`BOECKLIN_MUSEUM_V125_DRAMATIC_APPROACH_8S.mp4\`.
- 1.656.936 byte; SHA256 \`4b1e0136e84a9013c6b009c6baf73c80eee424f270dd993fa05e98f80d6c6d34\`.
- 8,000 secondi, 160 frame, H.264 720×1280, **silenzioso**, FFmpeg \`-xerror\` full decode **PASS**.
- t=0,5→4,0 s: 139/159 corrispondenze SIFT inlier (87,42%), errore mediano riproiezione **0,438 px**, copertura 3 zone 3×3.
- t=1,5→5,5 s: 178/216 inlier (82,41%), errore **0,593 px**, copertura 5 zone.
- Risultato: \`strong_single_homography_explanation\`. Un'unica trasformazione planare spiega bene il movimento osservato. **Non** dichiarare «vera camera 3D», prospettiva metrica o parallasse verificata. Un ambiente 3D dominato da una parete può comunque apparire planare: il test è diagnostico, non una dimostrazione assoluta di assenza di geometria.
- La sala fotografica è esteticamente più plausibile della galleria raster del vecchio V113, ma il provino non documenta una vera installazione di Böcklin, la scala fisica della tela e l'autenticità della cornice. È un **test di 8s**, non un Critico Museum completo.

## Altri file verificati

- V124 \`BOECKLIN_MUSEUM_V124_CAMERA_GLIDE_8S.mp4\`: 1.575.248 B, SHA \`6607e0f56aa474158dfe1ff38d308486591050e4e42f4ccbc790ca7c1526850e\`, 8s/160 frame, FFmpeg PASS. Analisi non conclusiva per copertura spaziale/numero inlier: **non** prova 3D.
- V122 \`BOECKLIN_PHOTO_ROOM_3D_PROXY_V122_8S_REVIEW.mp4\`: 2.039.982 B, 8s. Homography 84,25% e 77,84% di inlier nelle due coppie; **nessuna** certificazione 3D.
- V113 Critico Museum \`BOECKLIN_CRITICO_MUSEUM_V113_ACQUA_NITIDA_MUSEO_REVIEW.mp4\`: 21.053.055 B, SHA \`62635982936620472af27b6dcaf20b2586a2d81303674655d9e11f177c17d508\`, 110,65s/2213 frame H.264/AAC, FFmpeg full decode PASS. Traccia AAC ADTS SHA \`3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e\` **identica a V109** e alla voce originale Gacrux documentata. Contact sheet a intervalli di 5s mostra la galleria ancora poco fotografica. **Ascolto umano integrale e sincro parola-inquadratura non certificati.**

## Nuovo strumento anti-regressione

\`src/artvision_museum_parallax_qa_v126.py\` esegue la prova offline su veri MP4:

\`\`\`bash
python src/artvision_museum_parallax_qa_v126.py VIDEO.mp4 --pair 0.5:4 --pair 1.5:5.5 --output qa.json
\`\`\`

Usa ffprobe, SHA256, OpenCV SIFT/RANSAC; non chiama servizi esterni. **Un PASS tecnico non approva il museo.** Per V118/V119 servono ancora scena 3D/fotografica con provenienza e licenza, tela 80×150 cm in mondo metrico, cornice documentata dello specifico dipinto, approccio e ritorno senza stacchi, confronti con Cyclops/Hiroshige V46 e revisione umana del video in movimento.

**Decisione editoriale:** V125 **non sostituisce** V113, poiché mancano il raccordo ingresso→dipinto, l'uscita completa e la prova spaziale. I quattro slot V107, due ZIP persistenti, tutti i master e i due Cinema approvati restano intatti. Nessun TTS Gacrux, AI a pagamento, nuovo quadro, social, import R2 o dichiarazione di playback Android. \`V25_Gold=0\`, \`museum_approved=false\`. Le revisioni V109/V112/V113 e gli studi V122/V124/V125 non sono slot aggiuntivi.
