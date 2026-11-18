# ArtVision — diagnosi produzione autonoma (18 novembre 2026)

## Evidenza verificata su main
- `queue/production_v15.json` ha `items: []`: il renderer V16 non ha lavori preparati da eseguire.
- `.github/workflows/production-runner-v16.yml` usa `15 5 * * *`, ossia un solo ciclo quotidiano alle 05:15 UTC.
- `.github/workflows/storia-rivive-v101-auto-3h.yml` ha un cron ogni tre ore, ma dichiara espressamente `RESEARCH_PREPARATION_ONLY` e `finished_mp4: false`.
- Il planner V15 tronca la lista dei lavori pronti prima del preflight locale V16. Se un candidato iniziale viene bloccato nel runner, un candidato valido più avanti può non essere valutato. La patch in questa PR corregge questa perdita di slot.

## Cosa NON risolve questa PR
La patch non crea input editoriali, fonti verificate, audio Gacrux o MP4. Non collega il workflow di ricerca V101 al renderer e non cambia i cron. Non certifica che il sistema sia tornato a produrre. Non bypassare licenze, verifiche o revisione artistica.

## Prossimi interventi separati, da testare
1. Individuare il produttore/curatore owner che genera pacchetti V16 validi e collegarlo alla coda senza duplicati; se manca, implementare il passaggio da dossier verificato a pacchetto preparato.
2. Testare con almeno due lavori sintetici preparati: il primo bloccato al preflight del runner, il secondo valido; verificare che il secondo venga selezionato nello stesso ciclo e che il primo venga registrato come bloccato.
3. Collegare una pianificazione regolare al **renderer** solo dopo aver confermato input, checkpoint, costi e limite concorrenza. Mantenere la ricerca V101 separata.
4. Verificare un run reale, MP4/ZIP, hash, audio udibile, review e consegna privata; non confondere un workflow verde con un video pubblicabile.
