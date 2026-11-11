# GIULIANO V4 — DIREZIONE DOCUMENTARIO PREMIUM (10 novembre 2026)

## Diagnosi misurata della V3

Input realmente analizzato: `THE_TERRACOTTA_ARMY_V3_COMPLETO.zip` con `QA_V3.json` e 40 scene; master durata 163,13 s. **Non** sono misure di viralità.
- 40 scene, 30 fotografie diverse, durata media 4,02 s, mediana 3,87 s.
- Prime due inquadrature: 5,69 + 5,79 s, quasi 11,5 s prima di costruire l'immagine iconica dell'esercito. Hook debole.
- Scene 8 (arcieri, etichetta «formation»), 15 (scarpe, etichetta «detail») e 30 (mausoleo, etichetta «formation»): verifica visuale obbligatoria, perché la semantica dichiarata non dimostra ciò che dice la voce.
- Scene con immagini di ripiego e hold lunghi da controllare. 16 etichette semantiche non equivalgono a 16 reali tipi di inquadratura.
- La V3 **non** ha una misurazione della risposta del pubblico; non inventare punteggi di viralità.

## Cambio di metodo: sceneggiatura e immagini sono un'unica regia

1. **Hook first, evidence first.** Mostrare guerrieri autentici nel primissimo secondo; titolo cinetico leggibile sovrapposto (0,6–1,8 s) senza nascondere il reperto. Non aprire con una foto di un museo.
2. **Story spine** in tre atti: (A) 1974 / 8.000 guerrieri; (B) colore, armi e organizzazione produttiva; (C) tomba centrale non scavata. La sorpresa cresce anziché diventare una lista di curiosità.
3. **Word-level edit decision list (EDL).** Ogni fatto/oggetto («arciere inginocchiato», «punte di freccia», «pigmento») ha un token temporale da ASR o forced alignment, un asset approvato, un crop target reale e un range di permanenza. Il tempo della frase intera non basta.
4. **Repertorio autentico, non simulato.** Ricerca CC/istituzionale, provenienza e licenza per ogni asset. Vietate fotografie del museo scambiate per reperti, pannelli museali al posto della tomba, zoom che tagliano via l'oggetto, ricostruzioni AI presentate come fotografie.
5. **Shot design, non Ken Burns uniforme.** Wide/medium/close-up/macro, composizione e profondità. Un crop macro deve avere risoluzione sorgente sufficiente; altrimenti trovare un vero dettaglio. Movimenti delicati motivati, massimo 1–2 transizioni appariscenti nell'intero film.
6. **Audio da documentario.** Voce Google naturale con direzione per capitoli, ritmo calibrato, silenzi intenzionali; originale musica con variazioni armoniche e ducking; non fare 40 didascalie lette una dopo l'altra.
7. **Titolo premium.** THE TERRACOTTA ARMY / L'ESERCITO SEPOLTO, grande tipografia su panoramica autentica, contrasto e safe area 9:16. Copertina separata, titolo inglese e descrizione italiana.
8. **Quality gates.** (a) verifiche fattuali (UNESCO/UCL), (b) licenza/risoluzione, (c) corrispondenza parola–oggetto, (d) verifica crop per frame, (e) ritmo, (f) loudness/true peak, (g) ffmpeg full decode, (h) ZIP e link scaricabile, (i) revisione artistica umana.
9. **Fail closed.** Se un oggetto descritto non è documentato visivamente, modificare la frase o cercare altro materiale; non sostituire con una foto genericamente bella.
10. **Nessuna pubblicazione automatica** fino a approvazione del film finito. ArtVision 4×1 e La Storia Rivive restano invariati.

## Progetti esterni studiati (da valutare, non dichiarare integrati)

- PySceneDetect: https://github.com/Breakthrough/PySceneDetect — verifica effettiva dei tagli e della loro distribuzione.
- AutoBroll (MIT): https://github.com/andriidrok1/autobroll — WhisperX word timestamps, Remotion per keyframe e sincronizzazione B-roll.
- OpenCut: https://github.com/SysAdminDoc/OpenCut — esempi di QA e audio/caption.
- AestheticApp: https://github.com/electrichobo/AestheticApp — idee per exposure, composition, visual variety e shot scale. I punteggi automatici sono solo segnali, non giudizi artistici.
- UCL (armi): https://www.ucl.ac.uk/news/2019/apr/scientists-shed-light-preservation-mystery-terracotta-army-weapons — NON attribuire il trattamento anticorrosione al cromo: la ricerca lo ha smentito.

## Test pratici V4

- Nessuna frase «avviciniamoci», «guardiamo», «osserviamo» o deittici senza corrispondenza nel frame.
- Primi 3 s: panoramica iconica reale, titolo e hook parlato.
- Ogni 20–35 s: un fatto forte supportato da immagine specifica; evitare affermazioni non documentate.
- Durata target **110–140 s** solo se le informazioni restano comprensibili; non un numero rigido.
- 45–60 **inquadrature** se giustificate; il numero di fotografie differenti non è un KPI fine a se stesso.
- Shot duration variabile: 1,5–5 s di norma, eccezioni documentate; niente ritmo metronomico.
- Master almeno 1080×1920; 4K solo se le fonti reali lo supportano.
- Voice-over intelligibile su smartphone, sottotitoli opzionali e leggibili, suono originale/licenziato.
- V4 MP4/ZIP deve essere effettivamente generato e decodificato, altrimenti stato: «progetto di miglioramento», non «video pronto».
