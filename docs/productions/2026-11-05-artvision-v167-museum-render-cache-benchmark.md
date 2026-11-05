# ArtVision V167 — Museum frame cache, benchmark reali e gate qualità

Data: 2026-11-05. Scope: **sola velocità di composizione dei fotogrammi** nel renderer già esistente
`src/artvision_lady_shalott_critico_museum_v164.py`. Nessun nuovo MP4 prodotto, nessun master
precedente modificato, nessuna modifica alla programmazione delle automazioni.

## Problema realmente osservato
Nel renderer V164 la funzione `staged(photo,t)` richiamava `cv2.imread()` sulla
fotografia Sailko originale 4236×3456 **per ogni fotogramma** dell'ingresso/uscita.
Ridimensionava da capo il JPEG, costruiva la stessa parete per 1280 righe Python e ricaricava
i font serif/sans a ogni frame. Fonte: `src/artvision_lady_shalott_critico_museum_v164.py`,
workflow Github run 41929333331; montaggio totale ~63 secondi su un video 113,35 secondi.

## Correzione
* Cache LRU massima 2 per fotografia esatta: decodifica, immagine pre-ridimensionata,
  fondo neutro e font ora preparati una sola volta.
* Ogni frame chiama `background.copy()` prima di disegnare; i dati statici della cache
  non vengono mai alterati. Gli zoom e le interpolazioni rimangono invariati.
* Nessun intervento sull'audio, codec, MP4 prodotti, crediti o fotogrammi di
  opere precedenti. Nessun cambio di licenza/provenienza, nessuna sala museale finta.

## Prova di non-regressione e prestazioni
Benchmark locale `/mnt/data/artvision_museum_cache_benchmark_v167.py` (ambiente di lavoro
di questa sessione) con **vera foto sorgente** recuperata dall'archive GitHub
`ARTVISION_LADY_SHALOTT_MUSEUM_V164_ARTIFACT.zip` / Sailko.
Otto valori di avanzamento `t` (0, .05, .13, .20, .40, .65, .80, 1)
confrontati prima/dopo: **pixel array identici, 8 su 8**.

Tempi indicativi su 24 chiamate `staged()`, misurati localmente due volte:
* Primo: vecchio 5.218 s; ottimizzato 0.122 s (~42,9×).
* Secondo: vecchio 7.056 s; ottimizzato 0.399 s (~17,7×, macchina condivisa).
Il guadagno riguarda **solo la porzione di fotogrammi Museum**. NON è stata
misurata un'accelerazione dell'intero video/4×1: codifica, ricerca, voce,
rete, controlli e backup sono ulteriori costi indipendenti.
È vietato spacciare il fattore 17–43× come accelerazione dei 40 video.

## Controlli regressione
`tests/test_artvision_museum_static_cache_v167.py` verifica:
1) identità esatta dei pixel in 8 frame sintetici rispetto alla matematica V164;
2) una sola lettura del JPEG e due soli caricamenti font in 12 frame;
3) due fotografie distinte non confluiscono nella stessa cache.

Run previsto nel runner Python che dispone di OpenCV/Pillow:
`python -m unittest discover -s tests -p 'test_artvision_museum_static_cache_v167.py' -v`.
Questo documento **non** dichiara un nuovo risultato GitHub Actions del test:
va eseguito quando si integra il renderer nella successiva produzione autorizzata.

## Estensione alle altre varianti — solo con gate
Applicare lo stesso principio **per opera** e con SHA dei veri asset:
una fonte già verificata e una traccia Critico Gacrux/WAV riutilizzata; quattro
MP4 distinti e regie realmente differenti, un solo render contemporaneo.
Test comparativo A/B pixel-accurate su ogni renderer prima del cambio.
Non riutilizzare automaticamente sala/cornice di un'altra opera, cambiare
titoli pubblici, togliere controllo completo FFmpeg/ZIP/SHA, approvare Gold
o pubblicare. Se la foto varia o la qualità cala: rollback immediato.

Diritti territoriali Tate ancora in revisione e approvazione artistica
sempre separata dalla qualità tecnica.
