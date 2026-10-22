# ArtVision ENIGMA V1 — nuova regia additiva per video originali

**Stato:** motore + workflow + test tecnico aggiunti su ramo dedicato. Non e una certificazione di viralita ne un MP4 gia pubblicato. Gold Master Cinema V6, Critico V2, libri V12 e musica V20 restano INVARIATI.

## Idea creativa
Enigma costruisce una domanda visiva comprensibile anche senza audio: mostra un dettaglio non subito riconoscibile, alterna movimenti di camera specifici, rivela l'intera opera e racconta nella descrizione un fatto verificato. La stessa opera non viene alterata. Per i video narrati si puo fornire una traccia voce Google gia approvata, senza alcun sottotitolo impresso.

Ogni episodio richiede una storia visiva diversa. Nessuna pretesa di viralita: esamineremo retention, condivisioni e commenti veri dopo la pubblicazione.

## Cosa riusiamo veramente
1. ArtVision Cinema V6: la funzione di copertina e firma in modules/artvision/identita_visiva_v6.py, senza toccare il suo Gold Master.
2. Archivio Media V7: src/archivio_media_v7.py per API, host whitelist e riconoscimento di immagini valide.
3. Atelier V4: modules/artvision/atelier_v4.py per una registrazione musicale realmente scaricata, durata verificata da ffprobe e licenza attribuibile.
4. FFmpeg, OpenCV e Pillow: creano MP4 autentico H.264/AAC e inquadrature semantiche.
5. librosa: analizza onsets musicali dal file audio vero e sposta solo i tagli molto vicini al ritmo (massimo 180 ms); non inventa il BPM.
6. PySceneDetect headless: rilegge il MP4 effettivo per rilevare stacchi visivi e comporre un report diagnostico; non sostituisce la valutazione artistica.
7. Music Rights V20: fonte immagine e musica, diritti da rivedere prima della pubblicazione.

NON aggiungiamo n8n/Postiz o GPU senza una reale integrazione: allungherebbero inutilmente la filiera. Le dipendenze sono installate su GitHub Actions, non sul telefono.

## Dal telefono Android
1. Aprire GitHub -> Actions -> ArtVision Enigma V1 - produce MP4 da opera museale.
2. Toccare Run workflow, selezionare arcimboldo_vertumnus e avviare.
3. Il job acquisisce SOLO la foto fissata e con licenza coerente, e una registrazione strumentale approvata.
4. Se completato, si scarica un Artifact con MP4, COPERTINA.jpg, storyboard, REPORT_QA.json, DESCRIZIONE_SOCIAL.txt e FONTI_E_DIRITTI.json.
5. Guardare e ascoltare tutto il video, controllare le inquadrature, la naturalezza del ritmo, la corretta attribuzione e il copyright. Nessuna pubblicazione automatica.

Se manca una immagine autentica, un file musicale valido o la rete, il job si blocca. Non crea surrogati brutti. Per usare una voce narrante: generare prima l'audio Google autorizzato e passare localmente --voice nome.wav; il primo workflow fa solo la versione musicale.

## Test
Il workflow artvision-enigma-qa-v1.yml verifica il codice e produce un vero MP4 tecnico da disegno e tono sintetici creati esclusivamente per il TEST, non pubblicabili come episodi artistici. Installa e USA veramente librerie video, beat detection e scene detection. Per i primi episodi reali servono un render e una revisione umana completa.

## Nuovi format successivi
- Enigma / anamorfosi di Holbein: richiede opera/fonte/angoli nuovi.
- Arte inquietante: Bosch, Goya, Fussli con spiegazione originale documentata.
- Dettaglio nascosto: una storia verificabile attraverso particolari differenti.

Non basta cambiare artista nel JSON: si curano immagine, scena, fatti, diritti, voce e musica caso per caso. Non cambiare il Gold Master Van Gogh e non duplicare vecchi finali nel catalogo.

## Fonti
- Skokloster: https://samlingar.shm.se/media/377055EC-9453-475D-91A7-2B0F97CAA2ED
- Commons: https://commons.wikimedia.org/wiki/File:Vertumnus_%C3%A5rstidernas_gud_m%C3%A5lad_av_Giuseppe_Arcimboldo_1591_-_Skoklosters_slott_-_91503.jpg
- Musica: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100235
- Licenza musica: https://creativecommons.org/licenses/by/4.0/
- PySceneDetect: https://github.com/Breakthrough/PySceneDetect
- librosa: https://librosa.org/doc/latest/generated/librosa.onset.onset_detect.html
- Policy: https://support.google.com/youtube/answer/1311392

**Diritti:** PDM e museo sono prove, non certificazione legale globale. Ricontrollare condizioni di beni culturali italiani e fotografia prima di monetizzare. Per la musica CC BY il credito completo deve comparire nella descrizione social.
