# ArtVision owner · preflight non-stop — checkpoint dinamici

## Rilievo reale del 10 novembre 2026
La PR #234 era inizialmente limitata ai checkpoint di *The Alchemist* e *The Apparition*. In seguito GitHub Actions ha prodotto altri tre Cinema Standard della **seconda coda**: *The Course of Empire: Destruction* (run 42737588988), *The Golden Stairs* (run 42781549071), *The Duel After the Masquerade* (run 42782307048). Tutte e tre le run risultano `success` e hanno artifact non scaduti, FFmpeg video/audio e ZIP CRC PASS secondo i log. La loro revisione artistica e i diritti commerciali finali rimangono PENDING; non sono Gold e non modificano il 26/36 storico Museum.

### Difetto dimostrato e intervento minimo
Il selettore di preflight era vulnerabile a rilanci duplicati perché **caricava soltanto due checkpoint con nomi fissi**. La nuova versione carica automaticamente **tutti** i file `queue/artvision_owner_30_render_checkpoint_20*.json`, riconosce tre formati checkpoint già esistenti, confronta titolo esatto, artista, ordine e variante, e blocca il candidato anche quando un checkpoint contiene un ID run senza SHA finale. Non dichiara però che quella run abbia creato un MP4 verificato: la categoria è `run_exists_needs_reconciliation`.

Sono presenti sette checkpoint in `main`. Due dei tre nuovi checkpoint contengono ancora lo stato preliminare (Cole e Duel): **non aggiornarli o contarli come SHA-verificati soltanto sulla base del preflight**. La run verificata su GitHub fa fede per il controllo tecnico, mentre i relativi checkpoint devono ancora essere riconciliati in modo separato.

Il programma è **sola lettura**, non effettua richieste GitHub, render, spese, deploy o pubblicazione. Qualsiasi candidato che superasse il preflight resterebbe `candidate_preflight_only`; servono comunque fonte/diritti, ricetta, QA artistica e verifica della run attiva prima di un nuovo render.

## Nuovi fatti confermati il 10 novembre alle 19:30 UTC
Sono **sette** (non più cinque) i Cinema Standard fisicamente generati della seconda selezione e provati da GitHub Actions, includendo:
- *The Barque of Dante* — run [42879186247](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42879186247), artifact 13791694810, MP4 SHA256 `36f9306f02d16ac4e4fa36909e7b6d2f178fd53c855277432beaa770721ef188`.
- *Ulysses and the Sirens* — run [42880155469](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42880155469), artifact 13793451629, MP4 SHA256 `2403b1f1131396368fa9a0ed2b65f1193206b5016bdce720735f9fc7606c1d05`.
Le due nuove schede su `main` sono `queue/artvision_owner_30_render_checkpoint_20261110_barque_dante.json` e `queue/artvision_owner_30_render_checkpoint_20261110_ulysses_sirens.json`. Quest'ultima registra l'hash del video nella chiave `qa.SHA256` (maiuscola), mentre le altre usano `qa.mp4_sha256` oppure `qa.sha256_mp4`: il parser ora supporta tutte e tre senza invalidare il controllo anti-duplicati. La selezione resta **read-only**, Gold/pubblicazione/diritti commerciali/artistic QA sempre separati.

## Comandi
```sh
python -m unittest discover -s tests -p 'test_artvision_owner_nonstop_preflight_v1.py' -v
python scripts/artvision_owner_nonstop_preflight_v1.py --out output/artvision_owner_nonstop/PREFLIGHT.json
```

La suite verifica dieci scenari: selezione senza fonte, selezione positiva, vecchio checkpoint, nuovo checkpoint annidato, due stati in corso senza SHA, cinque lavori separati, registri incongruenti, checkpoint sconosciuti, sorgente senza hash, duplicati. Il workflow CI opera solo su `pull_request`, senza render pesanti e senza una nuova schedulazione.

## Cosa rimane per il non-stop effettivo
1. Riconciliare su `main`, separatamente e solo con prove, i due checkpoint preliminari di Cole e Duel (GitHub run completata + artifact + SHA dai log).
2. Sbloccare nel registro sorgenti un quadro futuro inedito soltanto quando hash originale, opera esatta e diritti di riuso applicabili sono documentati; evitare lavori che abbiano già un Cinema Standard prodotto.
3. Collegare selettore, renderer configurabile e QA finale all'automazione owner **esistente**, con blocco un solo render pesante e senza creare automazioni concorrenti. Misurare tre produzioni consecutive senza duplicati prima di dichiarare il non-stop collaudato.
4. Tenere distinti video tecnicamente renderizzati, QA artistico, Gold e pubblicazione. Nessun master già approvato va modificato.

**Limite esplicito:** questa PR non produce nuovi MP4 e non modifica `main`. È una correzione isolata al controllo anti-duplicati, non una fabbrica automatica già operativa.
