# La Storia Rivive · V146 — sei cortometraggi originali, cinque vere riprese per pilota

**31 ottobre 2026**. Owner: solo Restauro storico. Issue #144, mandato V108. Branch isolato e PR draft stacked su V145 (#163). Non modificare ArtVision, WOW LAB, benchmark V98 o il gateway Vidu. **Questa fase verifica soltanto fonti, non produce foto AI o un master approvato.**

## Decisione artistica e tecnica

I cinque filmati HD 1915–1920 tentati singolarmente non avevano cinque riprese diverse e dinamiche nello stesso file. La nuova ipotesi V146 preserva il criterio **5 movimenti reali**, ma usa **cinque pellicole originali diverse** dello stesso periodo storico. Evita di riciclare lo stesso filmato e si presta a 4 vere foto I2I + 1 Vidu nell'episodio definitivo.

Episodio di ricerca: **«Il mondo in movimento · 1896–1900»** (Francia, scene esatte da verificare). Non chiamare "Lione 1896" tutta la raccolta: solo le due pellicole alla stazione di Perrache dichiarano questa città. **Non inventare città** per bambini, operai, porto e gatto. Un luogo può essere confermato solo da catalogo storico originale.

| Priorità | Cortometraggio Commons (dichiarato pubblico dominio) | Anno | Raster del file e dimensione pubblicata |
|---|---|---|---|
| 1 | [Arrivée d'un train à Perrache](https://commons.wikimedia.org/wiki/File:Arrivée_d'un_train_à_Perrache_-_Court_métrage_1896.webm) | 1896 | 1920×1080, 33,6 MB |
| 2 | [Panorama de l’arrivée en gare de Perrache pris du train](https://commons.wikimedia.org/wiki/File:Panorama_de_l’arrivée_en_gare_de_Perrache_pris_du_train_-_Court_métrgé_1896.webm) | 1896 | 1920×1080, 17,39 MB |
| 3 | [Ouvriers réparant un trottoir en bitume](https://commons.wikimedia.org/wiki/File:Ouvriers_réparant_un_trottoir_en_bitume_-_Court_métrage_1898.webm) | 1898 | 1920×1080, 12,54 MB |
| 4 | [Mauvais temps au port](https://commons.wikimedia.org/wiki/File:Mauvais_temps_au_port_-_Film_1899.webm) | 1899 | 1920×1080, 39,48 MB |
| 5 | [La Petite fille et son chat](https://commons.wikimedia.org/wiki/File:La_Petite_fille_et_son_chat_-_Film_1900.webm) | 1900 | 1920×1080, 27,91 MB |
| 6 / riserva | [Enfants jouant aux billes](https://commons.wikimedia.org/wiki/File:Enfants_jouant_aux_billes_-_Court_métrage_1896.webm) | 1896 | 1280×720, 10,29 MB |

Dimensioni originali pubblicate: **141,21 MB complessivi** prima delle verifiche LIVE. Non trasferire copie modificate/sottocampionate, non dichiarare UHD native le scansioni restaurate 2015, non attribuire a tutte le riprese la stessa città. Due riprese treno potrebbero risultare visivamente ripetitive: verifica registica obbligatoria prima di scegliere.

## Procedura realmente implementata

- `config/storia_rivive_v146_five_lumiere_reels.json`: sei pagine Commons esatte, PDM come **asserzione del catalogo**, diritti Italia e restauro 2015 NON approvati.
- `src/storia_rivive_v146_multi_reel_audit.py`: verifica pagine via API Wikimedia, originale upload URL/host, raster nativo minimo 400 px utili nel 9:16, dimensioni max **75 MB per film e 190 MB complessivi**, SHA1 Commons live dell'originale, scarica i byte veri senza superare il limite, calcola SHA256 e FFprobe codec/durata/raster.
- Estrae con **un'unica decodifica nativa PTS di ciascuno dei sei film** tre fotogrammi (21%, 48%, 74% durata) via FFmpeg `select+showinfo`, non crea un fotogramma da AI o da interpolazione. Ogni PNG conserva `source_pts`, `time_base`, SHA256 del frame e SHA256 del video.
- Misura fotografia/contrasto/nitidezza con V123 e movimento spaziale 1,35 s *prima* del freeze tramite algoritmo V115/V120, rifiutando cartelli statici e false variazioni uniformi di luminosità. Non ridurre automaticamente la soglia per favorire il risultato.
- Propone al massimo cinque soggetti da **cinque file originali di SHA256 differente**; il sesto serve come alternativa se una ripresa fallisce. Distinto file filmico **non certifica cinque veri cambi di camera o varietà stilistica**. Genera il report `MULTI_REEL_AUDIT_V146.json` e la contact sheet `SIX_ARCHIVAL_REELS_CONTACT_SHEET_V146.jpg`.
- Workflow PR isolato `.github/workflows/storia-v146-five-real-reels-audit.yml`: nessuna cron, provider, credenziale API o upload di film originali. Artifact solo JSON e JPG, mai clip o video definitivi. Test `tests/test_storia_rivive_v146_multi_reel.py` con MPEG4 realmente codificato/FFprobe/movimento, SHA1 alterato, host falso, cinque SHA diversi e fallback su sesta pellicola. CI V109 include la suite.

## Licenza e regia: gate non superabili

Il copyright dei film storici e della **copia restaurata nel 2015** possono essere questioni distinte. Le pagine Commons dichiarano Public Domain, non è un parere legale definitivo per monetizzazione e Italia; verificare catalogo, provenienza e possibili diritti vicini/digitalizzazione. Fino a revisione: `rights_italy_verified=false`, `modern_restoration_rights_verified=false`, `publish_permitted=false`.

Solo con **cinque vere riprese artisticamente diverse, fonti e diritti compatibili**: quattro I2I fotorealistici e realmente source-locked, una sola clip Vidu Q2 Pro Fast da frame numero cinque (stesso B/N prima dell'animazione), con saldo prepagato e autorizzazione per scena reali e nessuna spesa nuova. Prima transizione entro 1–1,4s; colore osservabile 2–3s; 14–35s totali, regia dinamica, niente ripetizioni, cartelli invasivi o foto DDColor-only. Musica licenziata, titolo coerente con luoghi verificati, fonti e descrizioni social distinte, copertina elegante, MP4/ZIP Android riproducibili. QA su byte reali V91/V94/V96/V99 **e confronto V98**; *nessuna pubblicazione automatica*. Obiettivo: **3 piloti realmente finiti** prima di automatizzare master ogni 3 ore.

## Esito

Il lavoro di implementazione V146 non autorizza ad annotare `video_finished=true`. Riportare solo i risultati dei GitHub Actions **quando realmente conclusi**, distinguendo ogni film PASS movimento da ogni film rifiutato e indicando i blocker.
