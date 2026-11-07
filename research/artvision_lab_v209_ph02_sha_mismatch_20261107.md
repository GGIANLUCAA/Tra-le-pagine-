# Laboratorio ArtVision — blocco fotografico reale PH02, V209 (7 novembre 2026)

**Oggetto:** *The Magic Circle* di Waterhouse, Tate Britain N01572, **182,9 × 127 cm**. L'owner di produzione ha tentato il preflight fotografico della sala vuota Museum Barberini (PH02) come **scenografia neutra dichiarata, NON Tate originale**, senza render né spese. Run GitHub Actions: [42400165677](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42400165677), job `source_preflight` `128486005444`, conclusione `failure` (2026-11-07 18:13 UTC).

## Errore osservato direttamente nel job
Il workflow legge il file tramite la URL fornita dall'API Wikimedia Commons, `File:Museum_Barberini_Innenraum_leer.jpg`, controlla la licenza dichiarata CC BY 4.0, MIME JPEG, size e SHA-1 contro i metadata ufficiali. Questi controlli sono arrivati alla fase SHA256; il codice ha fallito sul **confronto con il SHA256 storico del preset**:
- **SHA256 storico atteso in V120 e V208:** `ea95335ef66afa225351e1dd423c49d5e84aeb15574e97b965fa25c1d5b91db2`.
- **SHA256 del file originale scaricato nell'esecuzione V209:** `4eccd18f1fc714305902369d8c2b118f763fc6dec129b89820a3d20242c40e64`.
- Il log mostra `AssertionError: (SHA osservato, SHA atteso)` e exit 1. Artefatto di risultato **non creato**; nessun MP4 generato.

**Ipotesi, non prova:** il campione V120 potrebbe riferirsi a una diversa elaborazione/derivazione, a un file storico con byte diversi o a versioni cambiate su Commons. Non è lecito sostituire semplicemente l'hash atteso con quello nuovo in produzione, né affermare che uno dei due sia falso. La verifica del SHA-1 e della size contro i metadata Wikimedia, avvenuta prima del SHA-256, è evidenza a favore dell'identità del file originale *attualmente servito*; occorre ancora confrontarlo con la copia V120.

## Percorso di sblocco senza compromettere la produzione
1. Recuperare **i veri byte del PH02 nel run/artifact di ricerca V120** (workflow run `41395451028`, artifact `13119426005`) e confrontare SHA256, risoluzione e eventuali EXIF con quelli dell'originale corrente; documentare se thumbnail, re-encoding o file differente.
2. Se le due copie rappresentano **lo stesso scatto/licenza con byte diversi**, registrare `source_original_sha` e `source_derivative_sha` separatamente; aggiornare un solo riferimento di input verificato mediante modifica revisionata e test in un ramo/PR o workflow non distruttivo, **senza accettazione tacita** di un mismatch. Se il contenuto diverge, respingere la prova.
3. **Problema indipendente:** porta centrale nel PH02, quindi persino con hash corretto la scena NON è automaticamente montabile con prospettiva credibile e tela larga 127 cm. Provare una parete realmente libera e una cornice documentata/approvata; al massimo due tentativi ragionevoli, poi passare alla prossima opera indipendente, come già richiesto dall'owner.
4. Preservare V80/V118/V119, titolo/attribuzioni, dim. reali; non rimpiazzare la foto con un'altra sala spacciata per l'allestimento Tate. **Stati:** `research_only`; `trial_qa_passed = false`; `approved_for_adoption = false`, `museum_approved = false`; **0 nuovi MP4** da questo run.

Questo dossier è un **passaggio LAB→Produzione**, non la correzione del workflow già installato. Non altera `queue/`, `AGENTS.md`, `config/artvision_museum_trial_sources_v208.json`, master e automazioni.
