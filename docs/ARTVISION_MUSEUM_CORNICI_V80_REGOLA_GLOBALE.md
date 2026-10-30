# ArtVision — V80: cornice autentica, scala e ingresso nel quadro (30/10/2026)

**Tipo:** regola GLOBALE obbligatoria su TUTTI i nuovi video *Critico Museum* e *Cinema Museum*.
**Origine:** feedback esplicito dell'utente, successivo al problema della cornice fittizia nel video Blake e alla revisione Wright. La cornice è un elemento dell'opera, non una decorazione intercambiabile.
**Precedenza:** integra V46 (scala fisica), V57/V64 (camera continua), V68 (quattro varianti), V73 (cornice esce naturalmente dall'inquadratura), V77 (correzione Blake), V25 (QA e approvazione). Non cambia la voce Gacrux, la narrazione, le versioni Standard o i master esistenti.

## Gate preliminare obbligatorio PER OGNI QUADRO

1. Identificare **opera esatta**, numero inventario, museo, dimensioni fisiche, medium e data, con fonti. La semplice fotografia del dipinto **non prova** quale cornice sia oggi in esposizione.
2. Cercare documentazione attendibile della **cornice realmente associata a QUELL'OPERA**: foto museale di sala/dettaglio, scheda istituzionale, dossier del conservatore, allestimento storicamente attestato. Annotare URL, data/contesto, attribuzione, copyright e confronto visivo effettivo fra fonte e modello.
3. Classificare la cornice con uno dei valori:
   - `authentic_documented`: foto o documentazione della cornice dell'esemplare preciso, usata fedelmente; dichiarare se la cornice è storica oppure allestimento attuale.
   - `faithful_reconstruction_documented`: cornice non fotografabile, ma ricostruzione pertinente con fonte storica specifica, proporzioni e finitura dichiarate; **mai** spacciarla per originale.
   - `unverified`: nessuna base affidabile; **non inventare** bordo dorato/nero/orientale/barocco generico. Il risultato Museum rimane *in review/non approvabile* finché non si identifica una soluzione documentabile oppure un'alternativa creativa **esplicitamente approvata per quell'opera**.
4. Ogni dossier/manifest Museum deve esporre: `frame_status`, `frame_reference_url`, `frame_source_type`, `frame_image_or_model_hash`, `frame_scale_cm_or_declared_estimate`, `frame_disclosure`, `actual_room_photo_used`, `gallery_reconstruction_status` e `frame_review`. Non compilare dati mancanti con valori inventati.
5. Se la fotografia dell'opera è **senza cornice** o non documenta la cornice, NON scrivere che il renderer ha usato la vera cornice. Una sala digitale con quadro senza cornice può essere una prova di regia, non il master Museum approvato.

## Regia e resa visiva

- **Inquadratura esterna:** mostrare quadro E la cornice coerente, in una sala realistica, senza eccessi decorativi. Geometria e rapporto cornice/tela corretti alla scala fisica reale (V46), senza trasformare piccoli fogli in enormi tele e viceversa.
- **Avvicinamento:** camera fluida, motivata dalla scena, senza apparizione/sparizione artificiale. La cornice deve diventare progressivamente esterna al campo **perché la camera avanza**, non dissolversi sopra la pittura.
- **Interno del quadro:** dettagli autentici, niente cornice persistente o bordi finti; salvaguardare volti, mani, oggetti e composizione, evitando crop scorretti, pixel stirati, contenuto inventato e finti effetti 3D.
- **Uscita:** movimento inverso coerente nella stessa stanza; la STESSA cornice riappare naturalmente prima della vista finale. Nessuna sostituzione della cornice tra ingresso e uscita.
- Le versioni Standard NON ereditano cornici museali fittizie; le due Museum condividono la stessa ricerca/fonti/cornice, pur mantenendo regie narrative diverse.

## QA reale: approvazione bloccata se un punto non passa

Verificare su frame estratti **apertura / esterno / avvicinamento / interno / uscita / vista finale**:
- corrispondenza cornice specifica ↔ fonte e rapporto fisico plausibile;
- assenza di cornice negli interni e suo ritorno SOLO per movimento di camera;
- continuità prospettica senza bande, ghosting, salti, attacchi di bordo o deformazioni;
- stessi dipinto/cornice/sala in ingresso e uscita;
- rendering completo (non solo storyboard), review artistica effettiva e MP4 scaricabili.

Se `frame_status=unverified`, manca una fonte, o appare una cornice inventata senza consenso specifico: `artistic_gold_master=false`, `museum_approved=false`, `frame_review=blocked`. Un video tecnicamente codificato rimane `rendered_needs_review`: non chiamarlo finito né pubblicarlo automaticamente.

## Casistica che ha motivato la regola

- **Blake, The Great Red Dragon:** il bordo dorato artificiale non era la cornice dell'opera; V77 ha sostituito il bordo con montatura neutra dichiarata, ma non trasforma la scenografia in cornice autentica.
- **Wright of Derby, An Experiment on a Bird in the Air Pump:** la National Gallery documenta una cornice dorata ottocentesca, ma i renderer V78/V79 hanno usato una riproduzione dell'opera senza tale cornice perché la relativa foto era irraggiungibile (HTTP 429). I relativi MP4 tecnici NON costituiscono un Museum gold master approvato, indipendentemente dalla riuscita della voce Gacrux. Non rivendicare che la cornice è stata ricreata correttamente finché ciò non accade.

**Regola di revisione:** cambiare solo la geometria, la fonte o il modello cornice dell'opera interessata con QA comparativo; non alterare automaticamente le altre 3 regie o video precedenti. Nessuna nuova spesa API e nessuna pubblicazione senza i consensi già previsti.
