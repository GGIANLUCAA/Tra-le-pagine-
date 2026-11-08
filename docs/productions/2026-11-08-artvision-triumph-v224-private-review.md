# ArtVision 4×1 · The Triumph of Death · Critico Museum V224 (08/11/2026)

## Esito reale e indipendente
Eseguito **un rendering MP4 veramente nuovo**, V224 del Critico Museum (revisione V204, non nuovo slot Gold), dopo aver controllato coda owner su main e l'assenza di render pesanti concorrenti. **Coda ufficiale 26/40, incremento 0**. Dalí sospeso, master verificati intoccabili, nessuna API a pagamento, nessuna pubblicazione sito/social.

- Master di revisione: `THE_TRIUMPH_OF_DEATH_CRITICO_MUSEUM_V224_REVIEW.mp4`, durata **129.15 s**, **2583** frame, 20fps, **720×1280**, H.264/AAC, **98,925,596 byte**, SHA256 **`7181523e7531f56f1c1d03cc30052f5df1870a2b82fd16a799d810b68c9a80ba`**. FFmpeg `-xerror -map 0 -f null -` PASS.
- Android ottimizzato, derivato dallo stesso master (NON altro slot): `THE_TRIUMPH_OF_DEATH_V224_ANDROID_REVIEW.mp4`, **58,121,329 byte**, SHA256 **`18d5a87d01c8a4521037cd1a7b6d3f54e3fe3ba18df865d62fce05bbbd8b73a5`**, 129.15 s, H.264/AAC, 720×1280, FFmpeg full decode PASS, AAC bit-identico.
- Archivio sorgenti completo: `THE_TRIUMPH_OF_DEATH_CRITICO_MUSEUM_V224_REVIEW_PACKAGE.zip`, **120,890,136 byte**, SHA256 **`a19e079742f16292738f3da4c36b492c4ed985a96bfa6dcd7a737845e6e3f139`**. ZIP CRC PASS, MP4 incluso SHA match; include cover, contatti reali MP4, 23 frasi, fonti/licenze, audio WAV originale, fotografia vera, scansione autentica, renderer e omografia.
- Android ZIP: `THE_TRIUMPH_OF_DEATH_V224_ANDROID_PACKAGE.zip`, **59,202,998 byte**, SHA256 **`cdd83e33aea4c32bde16406fa04d8c1f58bdd4712828a92468bff88fd320781b`**; ZIP CRC e inner MP4 SHA PASS.
- Voce Gacrux originale (nessun TTS/crediti): WAV SHA `ccb4a6872375237fb8b32e7df2b6e6869a4fb4696313e94b85cdda58e2d80c76`; **AAC ADTS byte-identico a V151/V204**, SHA `4d2cd3f278e91e461651d7b056196a52d49fc8987b20a6aa47c9b04f2e04843b`.
- Dossier 23 frasi originali e movimenti camera. Quando l'audio identifica l'opera e il Prado (18.785–32.385 s) il dipinto **è completamente visibile**; stesso criterio durante l'ultima descrizione globale (114.6 s). Durante il racconto centrale la cornice resta fuori campo; camera continua. La nuova regia evita le bande nere vuote dei panorami V204.
- **Due soli tentativi ragionevoli**: prima versione renderizzata e **respinta** (max MAD frame-adjacent 36.712 > 35, t~2.7s); seconda ha corretto apertura, fotogramma 3.505 già 100% dentro arte. Seconda versione vera MP4 salva e verifica FFmpeg PASS. Il controllo statico più restrittivo segnala **MAD 35.579 > 35 al t~94.2s**, quindi `camera_auto_gate=WARN_NOT_PASS`. Una sequenza campionata 93.8–97s mostra panoramica continua, non uno stacco secco, ma **NON** equivale a review full-speed e non va promosso automaticamente. Non fare un terzo rerender nello stesso ciclo, passa a altro lavoro indipendente.
- **Revisione artistica in riproduzione a velocità normale PENDING**, correzione camera 94s se fallisce la review; diritti e clearance commerciale territoriale **PENDING**. Non pubblicare né marcatura Gold.
- Opera: Pieter Bruegel il Vecchio, `The Triumph of Death`, circa 1562–1563, Museo del Prado inv. P001393, **117×162 cm**. Scansione originale esatta SHA `2cbaefc3961b999fc5a916db06dd96b3b95789789a795da83cc1d7947f3e1fbb`, fonte https://commons.wikimedia.org/wiki/File:Thetriumphofdeath.jpg .
- Fotografia reale dell'esatto dipinto incorniciato: Priscila Costa / Ministério da Cultura (2013), **CC BY 2.0**, fonte https://commons.wikimedia.org/wiki/File:Pieter_Bruegel_der_Aeltere_-_Der_Triumph_des_Todes_-_mit_Rahmen.jpg , originale SHA `c7b99abad654ca86c1df05f51b14013cd877eb11b079fde71799636987a73517`. Registrazione SIFT **993 inliers**; la parete oltre l'immagine è un'estensione grafica/editoriale derivata dalla foto, NON una sala effettiva e verificata del Prado. Originalità storica della cornice non attestata.

## Archivio privato / checkpoint
Upload Library riuscito:
- MP4 Android `/ArtVision/Triumph_Death_V224/THE_TRIUMPH_OF_DEATH_V224_ANDROID_REVIEW.mp4` ID `libfile_1b03102e04188191aa41731208c50d69`.
- ZIP sorgenti `/ArtVision/Triumph_Death_V224/THE_TRIUMPH_OF_DEATH_CRITICO_MUSEUM_V224_REVIEW_PACKAGE.zip` ID `libfile_4f8c7fe826b0819182201309995faae7`.
- ZIP Android ID `libfile_97b9e4e23b848191865f125491123224`; QA ID `libfile_b009041d8a1481919d193a1e950bbf9f`; renderer ID `libfile_b0ba007e1f808191b4f0d1482c7502de`.
- **Readback indipendente dalla Libreria**: mobile MP4 e ZIP sorgenti materializzati nel container, SHA256 entrambi match; ZIP CRC, inner-master MP4 SHA e decoder completo del MP4 mobile PASS. Non dichiarare test di riproduzione sul dispositivo Android dell'utente senza conferma.

## Prossimo ciclo
NON duplicare V224, non contarlo come slot nuovo/approvato. Esaminare interamente la resa artistica, diritti e movimento ~94s quando si decide sull'approvazione. Ruotare verso Cinema Museum di Simberg o altro slot indipendente della coda ufficiale, e mantenere Dalí sospeso. Gli archivi, video ed eventuali recuperi non costituiscono nuove varianti approvate.
