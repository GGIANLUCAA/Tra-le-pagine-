# HyperLumen Studio V18 — laboratorio autonomo Android

Questa integrazione è **aggiuntiva e sperimentale**. NON modifica i renderer approvati per libri, ArtVision e critica, né il Gold Master. Non attiva pubblicazione o chiamate a pagamento.

## Uso immediato

1. Aprire [lo studio HTML](HyperLumen_Studio_V18_OFFLINE.html) con Chrome Android; il file è autonomo (CSS/JavaScript incorporati, nessuna dipendenza CDN).
2. Selezionare **Importa MIDI** per leggere le note e **Importa audio** per ascoltare la stessa esecuzione registrata. Il synth dimostrativo non è di qualità pubblicabile.
3. Selezionare la regia: **Glass Highway**, **Helix Cathedral** o **Aurora Rivers**. Le note MIDI pilotano scie e particelle WebGL2.
4. Allineare l'offset audio/MIDI, scegliere durata, verificare e salvare la ricetta JSON.
5. Premere **Registra video**. Quando il browser supporta MP4 usa MP4, altrimenti esporta WebM. È un registratore in tempo reale, non ancora un esportatore deterministico offline.

## Stato e limiti controllati

- Parser MIDI e regia musicale con cambi di tempo, canali e durate; test Node della versione sorgente superati esternamente al repository.
- L'interfaccia è stata eseguita in browser headless; **la grafica WebGL2 non è stata verificata su GPU Android reale**: è un gate aperto.
- L'esportazione MP4 nativa dipende dai codec del dispositivo. Non dichiarare che funzioni su ogni Android o che produca 4K/16K.
- L'audio demo è sintetico; per un master finale occorre una registrazione/licenza adatta.
- I controlli automatici non certificano l'estetica. Occorrono benchmark su telefono, ascolto e revisione del rendering.
- Nessun codice di terzi copiato: architetture studiate da [midee](https://github.com/aayushdutt/midee), [phase-viz](https://github.com/7g3n/phase-viz) (MIT), [cymatic](https://github.com/coreyepstein/cymatic) (MIT) e [MIDITrail](https://www.yknk.org/miditrail/en/). Verificare licenze specifiche prima di incorporare altro codice.

## Integrazione futura

Non aggiornare `config/video_formats_v13.json` a `ready` finché non esistono una prova reale WebGL su Android, un MP4 verificato e revisione artistica. Quando approvato, collegare V18 al direttore V13, al runner V16 e al report QA V17 tramite adapter separato. Nessuna pubblicazione automatica.

## Rollback

Non unire questo branch oppure eliminare `integrations/hyperlumen_studio_v18/`. Tutti gli altri file rimangono invariati.
