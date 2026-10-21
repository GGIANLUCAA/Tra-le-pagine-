# Esecutore autonomo V16 — stato reale e utilizzo

Aggiornamento del 21 ottobre 2026. Il target resta dieci video distinti e controllati
al giorno. Questa versione collega la coda preparata ai renderer e al recupero del
lavoro; ricerca, materiali nuovi e revisione artistica restano attività dell'agente,
non capacità attribuite a ffprobe o a un cron.

## Cosa è operativo nel codice

- `production_runner_v16.py run` legge la coda V15, applica il preflight e avvia
  fino a tre processi isolati. Ogni progetto ha una propria copia dei sorgenti,
  asset e output: il guasto di un render non interrompe gli altri.
- Tre adapter ammessi: libri con voce Google già verificata; Critico V2 con
  quadro, musica, configurazione e voce locali; Cinema V6 Van Gogh con il pacchetto
  di opere già curato. Il terzo non è un generatore universale di artisti.
  Il Critico può usare un nuovo config curato con lo schema V2; le indicazioni
  sui diritti vengono dal pacchetto, non dalle affermazioni del vecchio renderer.
- I figli non ricevono chiavi dei provider, token GitHub o comandi shell scritti
  nella coda. I percorsi restano nel progetto. Non si attiva Edge come ripiego.
  Per voci nuove serve una fase TTS separata con quote/costo verificati; questa
  versione non acquista chiamate né assume che l'abbonamento ChatGPT le includa.
- Il cache vocale deve corrispondere a copione, profilo e hash, con allineamento
  già disponibile. Cambiare copione invalida il riuso: il servizio segnala il blocco.
- Ogni input contribuisce a un'impronta. Un secondo avvio riconosce il master
  valido e lo conserva. Input cambiati richiedono una revisione esplicita, senza
  sovrascrivere il precedente lavoro. Due tentativi falliti richiedono diagnosi.
- Ogni render passa a `rendered_needs_review`. Si producono un foglio di fotogrammi
  campionati e l'audio completo del mix per aiutare l'agente a rivederlo. I campioni
  non sostituiscono la visione completa né provano la correttezza di tutte le scene.
- Una revisione in `queue/reviews_v16/` si applica solo al master e alla ricetta
  con gli hash esatti. Il workflow registra il video qualificato solo dopo queste
  verifiche. La revisione è responsabilità dell'agente; non richiede un OK ripetuto
  di Gianluca per operazioni già autorizzate.
- Il buffer non cresce senza limite: se sono in attesa dodici revisioni, la prima
  attività è smaltirle. La qualità non è sostituita dal numero di render avviati.

## Esecuzione e persistenza

Il workflow `.github/workflows/production-runner-v16.yml` si attiva su una coda
modificata, una revisione aggiunta, avvio manuale o controllo giornaliero alle
05:15 UTC (07:15 durante l'ora legale italiana, 06:15 durante l'ora solare).
GitHub può avviare i cron in ritardo: non è una garanzia di orario o capacità.
Le tre lavorazioni condividono la risorsa del runner, non equivalgono a tre server.

Stato piccolo in `queue/runner_state_v16.json`; workspace con cache, master,
ricette e kit di revisione in un checkpoint tar dentro un artefatto Actions.
Il recupero cerca soltanto gli artefatti dello stesso workflow V16 sul ramo main.
Un checkpoint vecchio non cancella uno stato di lavoro più recente nel repository.
Il token GitHub non viene inoltrato al servizio di storage dopo un redirect.

Il checkpoint viene conservato a fine esecuzione, anche dopo errori gestiti, e
resta disponibile per 14 giorni secondo la policy dell'artefatto. Se GitHub termina
bruscamente il runner prima del checkpoint, l'ultimo lavoro non salvato può andare
perso. Il volume massimo va misurato e lo storage permanente va collegato prima
che una scorta grande dipenda solo da questa conservazione temporanea.
Un master marcato come finito ma non recuperabile non viene rigenerato di nascosto.

L'importatore pubblico esistente cerca MP4 e immagini direttamente negli ZIP degli
artefatti. I master ancora da revisionare sono qui conservati nel tar di lavoro:
non vengono presentati automaticamente al sito come finali approvati. L'automazione
esistente di sincronizzazione dei video generati rimane il percorso separato per
le consegne effettivamente pubblicabili. Non abbiamo modificato i video già online.

## Campi specifici per un pacchetto preparato

Restano obbligatori i campi V15: id, content_key, project_file, status, attempts,
new_paid_calls_required. Aggiungere:

| Adapter | Campi |
|---|---|
| `books_gemini_cache` | episode (slug sotto episodes/), voice_cache_dir; effects off o v4 |
| `critico_v2_prepared` | config_file, painting_file, music_file, voice_cache_dir |
| `cinema_v6_vangogh_prepared` | artist = Vincent van Gogh, assets_dir |

Tutti i percorsi sono relativi alla radice del repository e i file devono essere
stati recuperati. Il copione della scheda deve coincidere con quello realmente
recitato. Quadro/musica o immagini/ZIP realmente usati devono rientrare negli asset
approvati del preflight. Non inserire shell command o script arbitrari nella coda.

```
python src/production_runner_v16.py run
python src/production_runner_v16.py reviews
python src/production_runner_v16.py pack --archive checkpoint/workspace-v16.tar
python src/production_runner_v16.py restore --archive checkpoint/workspace-v16.tar
```

## Primo lavoro di preparazione

L'audit locale è in `docs/PRODUCTION_INPUT_AUDIT_V16.json`: la coda iniziale non
contiene pacchetti `prepared`. Questo non significa che non esistano i video già
consegnati: diverse risorse si trovano negli artefatti, nell'archivio o nella Libreria.
La prossima azione dell'agente è recuperare quei materiali e cache, completare i
pacchetti con angoli originali e popolare la coda; non rinominare i vecchi video per
farli passare come nuove produzioni. Poi osservare un lotto reale e misurarne tempi,
scarti, costi e spazio. Il target 10/giorno non è ancora dimostrato.

## Verifiche svolte

Test su coda e integrità, adapter e voce cache. Un adapter di prova isolato ha
prodotto un MP4 tecnico di un secondo: esecuzione subprocess, isolamento dei token,
controllo audio/video, kit di revisione, pacchetto, ripristino, riuso senza rerender
e registrazione con revisione sono verificati. Sono test della pipeline: non sono
un nuovo episodio artistico, un test della qualità Google o un benchmark di dieci
filmati completi al giorno. I renderer artistici mantengono le proprie dimensioni,
font, regia e controlli esistenti.
