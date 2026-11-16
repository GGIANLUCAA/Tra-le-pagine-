# ArtVision — confronto fra archivio pubblico e Libreria privata

## Separazione obbligatoria delle fonti

1. Repository pubblico: data/archivio-generale/opere.json, catalogo_sito.json, code e documenti.
2. Video Library Studio: /api/catalog con titolo, byte, data e stato API. available=true non prova da solo playback o download integrale.
3. Libreria ChatGPT privata: è accessibile nell'ambiente ChatGPT autorizzato, **non direttamente da GitHub Actions**. Gli MP4, gli ZIP, i nomi dei file privati, i percorsi, gli ID Libreria e i token **non devono essere caricati nel repository pubblico**.

Il modulo scripts/artvision_private_library_reconcile_v1.py consente di confrontare uno snapshot privato, creato nel contesto ChatGPT autorizzato, contro il catalogo pubblico. Non esporta né legge automaticamente la Libreria da GitHub; non usare la procedura CI per simulare questa capacità.

## Input privato (esempio inventato, non un file dell'utente)

Il manifest private_artvision_manifest.json deve restare **fuori dalla cartella Git**:

    {
      "entries": [
        {
          "path": "/CartellaPrivata/Esempio/Filmato.mp4",
          "name": "Filmato.mp4",
          "size_bytes": 1234567,
          "created_at": "2026-11-16T00:00:00Z"
        }
      ]
    }

Da un PC o da un ambiente che dispone già dello snapshot, eseguire:

    python3 scripts/artvision_private_library_reconcile_v1.py \
      --manifest /cartella-privata/private_artvision_manifest.json \
      --site data/archivio-generale/catalogo_sito.json \
      --registry data/archivio-generale/opere.json \
      --out /tmp/artvision_confronto_privato.json

Il programma **rifiuta** di scrivere il rapporto all'interno del repository pubblico. La sua uscita console contiene soltanto i conteggi, mai i nomi dei file privati.

## Livelli di corrispondenza

- same_name_same_size: stesso nome e stessa dimensione dichiarata; **corrispondenza metadata, non hash confermato**.
- same_name_size_unconfirmed_or_different: nome uguale con bytes diversi o ignoti; possibile revisione, transcodifica o omonimo.
- no_exact_name_match: nessun nome uguale; **non significa video assente**: potrebbe essere rinominato.
- Famiglie di revisioni sono soltanto **sospetti non distruttivi**. Non eliminare, fondere, sostituire o rigenerare file senza confronto di veri hash e riscontro proprietario.

## Antidoppioni

Prima di creare un nuovo video:
1. cercare artista, titolo, anno e variante nel registro canonico;
2. esaminare i checkpoint, i file del sito e **il confronto privato aggiornato**;
3. verificare quale revisione/voce regge QA, e se un MP4 già esiste a byte identici;
4. se uno slot esiste ma non è approvato, effettuare revisione anziché contare due varianti;
5. non considerare render_documentato equivalente a pubblicato o artistico Gold.

Una scansione manuale ChatGPT va rinnovata quando arrivano nuovi asset privati. **La schedulazione ogni sei ore di GitHub vede soltanto fonti GitHub e catalogo pubblico**, e non può aggiornare da sola la Libreria ChatGPT.

## Preflight anti-doppioni (in sola lettura)

Il seguente comando cerca un'opera e uno slot fra i render registrati:

    python3 scripts/artvision_preflight_duplicate_v1.py \
      --artist "John William Waterhouse" \
      --title "The Lady of Shalott" \
      --variant cinema_standard

Il responso RENDER_EXISTS_VERIFY_REUSE_OR_REVISION chiede di riutilizzare oppure verificare prima di rifare lo stesso video. Non certifica disponibilità di bytes e non forza uno stop. Non usare abbreviazioni non documentate per titolo e autore; il matching è volutamente rigoroso.

Le pipeline attive devono consultare il preflight prima della generazione: l'installazione di questo script NON lo inserisce magicamente in tutte le decine di workflow storici di rendering. Aggiornare gli orchestratori uno alla volta, con QA e senza interrompere le code.

## Sicurezza

Non condividere URL privati, ID Library, API key o nomi di file personali nel repository pubblico. Gli esempi e i test sono fittizi. I dati di uno snapshot privato possono essere conservati nella Libreria ChatGPT, non nel codice sorgente del sito.
