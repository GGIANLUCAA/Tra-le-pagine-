# ArtVision owner non-stop · primo blocco operativo (9 novembre 2026)

## Situazione verificata
- Due Cinema Standard completati tecnicamente: *The Alchemist* e *The Apparition*. Le schede `queue/artvision_owner_30_render_checkpoint_20261109_*.json` sono la prova di MP4 fisici. Restano entrambi da revisionare artisticamente e con diritti territoriali/commerciali finali pendenti.
- `queue/artvision_owner_30_fast_quality_lane_20261109.json` indica ancora per entrambi `render_status=not_started`: il solo registro di priorità non basta per deduplicare.
- Nessuna delle 30 opere è adesso contrassegnata come completamente pronta per produzione; il preflight deve fallire in sicurezza, senza creare finti MP4.
- I due workflow funzionanti richiamano script individuali; `.github/workflows/artvision-render.yml` è un vecchio atelier universale, non il motore delle quattro varianti 4×1.

## Consegna di questa modifica
`scripts/artvision_owner_nonstop_preflight_v1.py` legge la coda, il registro fonti e i due checkpoint. Produce soltanto un report JSON con il primo eventuale candidato realmente prevalidato, rispettando l'ordine di priorità, i diritti, l'hash sorgente e i render già verificati. **Non avvia rendering, non pubblica, non genera spese.** Se non trova fonti pronte, esplicita i blocchi invece di generare uno slideshow o rieseguire i due video.

Esecuzione di prova:
```sh
python -m unittest discover -s tests -p test_artvision_owner_nonstop_preflight_v1.py -v
python scripts/artvision_owner_nonstop_preflight_v1.py --out output/artvision_owner_nonstop/PREFLIGHT.json
```

## Percorso per arrivare al non-stop effettivo
1. **Riparare le prove di disponibilità**: dossier immagine ufficiale, oggetto esatto, dimensioni e SHA, licenza commerciale anche della foto, ricetta specifica e controllo duplicati multi-coda. Aggiornare lo stato soltanto dopo verifica, mai impostare `ready=true` per velocizzare.
2. **Estrarre un renderer configurabile dalle due produzioni riuscite**: ricette per singola opera e variante, scene ritagliate da coordinate artisticamente verificate; non inserire immagini casuali. Costruire `cinema_standard` per primo soltanto se pronto, poi le altre tre; identico WAV e testo nei due Critico, museo con scala e cornice credibili.
3. **Collegare all'unica automazione owner** (`6adca191603c8191a90d5190901cd034`), senza un secondo proprietario o nuovo cron. Utilizzare richiesta GitHub dedicata e idempotente; verificare prima che il trigger esegua il renderer corretto, non il vecchio universale o gli script rigidi.
4. **Un solo render pesante** tramite gruppo di concorrenza `artvision-owner-single-heavy-render`. In parallelo solo ricerca e preparazione. Ogni slot conserva uno stato persistente e un ID univoco; nessun duplicato su ripetizione degli eventi.
5. **Verificare risultati reali**: MP4 H264/AAC, decoding completo, source SHA, ZIP CRC, copertina e quattro testi social specifici, preview Android; QA a velocità normale e approvazione artistica separati da PASS tecnico. Non chiamare `Gold` un video che non lo è.
6. **Prova di affidabilità prima del ritmo**: almeno tre opere/slot consecutivi senza duplicazioni, no spese non autorizzate e recupero automatico dal fallimento; solo dopo misurare la resa rispetto all'obiettivo di un video ogni tre ore.

### Limiti espliciti
Questo PR **non sblocca ancora un render**. Dimostra un selettore fail-closed, non una produzione 24/7. Nessuna modifica ai master approvati, agli status delle code, ai workflow live o alle regole permanentemente attive.
