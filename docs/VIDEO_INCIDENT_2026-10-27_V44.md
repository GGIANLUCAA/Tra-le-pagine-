# Incidente qualità — La macchina del tempo (27/10/2026) · Regola V44

**Stato: risultato RIFIUTATO / quarantena editoriale.**
Il file \`MACCHINA_DEL_TEMPO_ANIMATA_FINALE.mp4\`, consegnato in chat come montaggio migliorato, **non è un master approvato e non va pubblicato, promosso o riutilizzato come standard**. Preservare invece il master originale \`TRA_LE_PAGINE_LA_MACCHINA_DEL_TEMPO.mp4\`.

## Esame effettivo dei file della sessione

- Originale: \`LA_MACCHINA_DEL_TEMPO_COMPLETO.mp4\` · 187,4167 s · 720×1280 · H.264/AAC.
- Clip locale: \`ANIMAZIONE_MECCANICA_3S.mp4\` · 3,00 s · 720×1280 · H.264, nessun audio.
- Candidato consegnato: \`MACCHINA_DEL_TEMPO_ANIMATA_FINALE.mp4\` · 187,50 s · 720×1280 · H.264/AAC · 9.553.112 byte.
- Primo export incompleto: \`MACCHINA_DEL_TEMPO_ANIMATA_COMPLETA.mp4\` · 46,4167 s. Il primo collegamento "FINALE" era stato annunciato prima della presenza effettiva del file; dopo si è rimediato alla sola integrità/durata, non alla qualità.
- Script della prova, \`make_machine_motion.py\` (NON il modulo Vidu nel repository): ruota su cerchi mascherati porzioni della macchina con \`cv2.getRotationMatrix2D\`, deforma un'area della presunta leva con \`cv2.remap\` e applica una variazione artificiale di luce. NON simula coerentemente l'intero gesto mano–leva–meccanismo.
- Confronto visivo: la posa del protagonista resta essenzialmente identica nel taglio 10,25/11,75/13,00/14,50 s; il mondo/viaggio inizia dal successivo quadro statico. Questo NON risolve la richiesta "la persona tira la leva".
- La voce originale dice "L'uomo tira una leva" intorno a 10,92–12,74 s: la sequenza deve corrispondere all'azione completa, non mostrare microdeformazioni isolate.
- Il codice locale analizzato usa OpenCV/Python/FFmpeg e **non contiene chiamate all'API Vidu**. Non c'è prova di addebito Vidu a causa di questa specifica clip. Il conto/saldo effettivo Vidu richiede verifica nel provider: GitHub e file MP4 NON dimostrano il saldo.

## Perché il vecchio QA non è sufficiente
\`ffprobe\`, decodifica completa, presenza audio, ZIP CRC e controlli dei tagli attestano soltanto integrità tecnica. Non possono stabilire azione visiva, naturalezza, continuità del volto, coerenza narrativa, valore artistico o qualità per i social. L'errore principale è l'**autopromozione di una prova tecnica a master finale senza visione critica del risultato**. Una buona regola documentale era già presente, ma il renderer ad hoc fuori dal repository la ha aggirata.

## Intervento correttivo V44 — fail closed
Il nuovo modulo \`src/animated_video_release_gate_v44.py\` impone:
1. Impostazione iniziale \`rendered_needs_review\` e revisione artistica in stato NON approvato.
2. Impronte SHA-256 dell'originale, della singola clip e del nuovo MP4: sostituire il video dopo la review invalida l'approvazione.
3. Frase narrata + azione realmente visibile + intervallo temporale esatto.
4. Revisione del video intero e dell'audio e di: movimento fisico reale, sync, identità di volto/mani, assenza artefatti, raccordi, valore aggiunto rispetto all'originale.
5. Chiara differenza tra \`local_motion\` e \`provider_i2v\`: per una richiesta di **vera animazione IA** gli effetti warp/crop/rotate locali restano SEMPRE non conformi, anche se esportano un MP4.
6. Esito di un vero revisore (utente o editor umano) riferito all'hash del filmato specifico e motivato concretamente. I test tecnici non impostano mai questi check a true.
7. Non etichettare \`FINALE\` né caricare in cataloghi "pronti" un risultato che non supera il gate. Una prova non approvata può essere mostrata soltanto come **bozza rifiutabile**, non come successo.
8. I crediti Vidu sono protetti separatamente da V41/V42: budget di default 0, piano gratuito, autorizzazione puntuale e divieto di retry addebitabili. La scarsa qualità di una generazione NON autorizza un secondo pagamento.

**Importante:** un modulo di verifica NON può certificare il gusto né provare che un umano abbia guardato il file. L'azione osservata va controllata realmente sul MP4 e registrata con evidenza descrittiva; la mancanza blocca la dichiarazione di video finale.

## Checklist pre-Vidu per recuperare il progetto (nessuna spesa autorizzata)
- Recuperare il sorgente originale a risoluzione adeguata, non un fermo immagine con bande nere o ingranaggi illeggibili.
- Stabilire quale leva il protagonista deve tirare e il gesto plausibile dal fotogramma iniziale. Se l'immagine rende il gesto ambiguo, migliorare o sostituire gratuitamente l'immagine **prima** dell'API.
- Preparare storyboard esatto 10,92–15,18 s; chiedere un unico movimento e montare l'uscita verso il quadro di viaggio, non chiedere una deformazione completa della scena.
- Preventivo e anteprima gratuito con prompt specifico e revisione del primo frame.
- Soltanto dopo una specifica autorizzazione del singolo costo eseguire **una** chiamata Vidu, salvare task ID e clip senza retry.
- Esaminare il clip e il master assemblato; se manca movimento credibile, **scartare** e proteggere il credito rimanente.
- Nessuna dichiarazione di "video migliorato" finché V44 resta bloccato.

## Uso CLI del gate
\`\`\`bash
python src/animated_video_release_gate_v44.py draft \
  --original ORIGINAL.mp4 --candidate CANDIDATO.mp4 \
  --clip CLIP_IA.mp4 --manifest REVISIONE_V44.json \
  --medium generative_i2v --spoken-line "L'uomo tira una leva" \
  --requested-action "L'uomo aziona realmente la leva e gli ingranaggi partono"
# Esaminare e completare manualmente REVISIONE_V44.json con prove vere.
python src/animated_video_release_gate_v44.py check \
  --original ORIGINAL.mp4 --candidate CANDIDATO.mp4 \
  --clip CLIP_IA.mp4 --manifest REVISIONE_V44.json \
  --medium generative_i2v
\`\`\`
Il secondo comando fallisce senza una revisione reale. Non mostrare risultati dello script come sostituti della visione umana.
