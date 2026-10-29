# ARTVISION — START QUI: FABBRICA 4×1 RIPRODUCIBILE V68

**Decisione del 29 ottobre 2026.** L'utente ha visto un filmato di Socrate e apprezza esplicitamente **la sala museo, la cornice e la qualità della spiegazione**. Accetta il primo 4×1 come **buona base artistica, modificabile**; non vuole ripetere ogni volta le stesse istruzioni. Questa conferma riguarda il **modello creativo e l'organizzazione**: **NON** equivale a V25 su tutti e quattro i MP4, autorizzazione alla pubblicazione sociale, import privato verificato o sblocco automatico delle nuove opere.

## Tre livelli di memoria — niente più regole perse

1. **Regole permanenti (non negoziabili)**: `AGENTS.md`, `docs/REGOLE_ATTIVE.md`, `docs/ARTVISION_CONTRATTO_MADRE_4X1_V58_20261029.md` e i successivi vincoli V57/V61; una sola opera → 4 MP4 differenti, due Critico con IDENTICA traccia Gacrux e copione, due Cinema musicali, ingresso/uscita Museum continuo, materiali veri, diritti, QA, un solo owner, pubblicazione/social mai impliciti.
2. **Ricetta creativa riutilizzabile**: `config/artvision_four_variants_presets_v68.json`. La **base Socrate V67/V61** è fissata come esempio di qualità: stanza/cornice credibili e non ritagliate, voce Critico coerente con Bosch V22 e Ofelia V21, sincronizzazione con dieci parti vere del testo. Ogni nuova opera crea una propria ricetta e può modificare in autonomia **solo i campi autorizzati**; NON riscrive il preset globale.
3. **Scheda di ogni produzione + revisioni**: un file separato `docs/productions/<opera>/ARTVISION_RECIPE_V68.json` + dossier, fonte e hash di immagine/cornice/musica/WAV, timecode, quattro storyboard, quattro output SHA256/bytes/versioni, 16 post e risultati di QA/archivio. Per cambiare un parametro si salva una **nuova versione di ricetta**, con valore precedente, nuovo valore e ragione. Le revisioni dello stesso slot NON contano come filmati nuovi.

## Configurazioni che posso cambiare su tua richiesta

| Esempio della tua richiesta | Parametro modificabile | Conseguenza tecnica |
|---|---|---|
| «Cornice più scura per il prossimo quadro» | `museum.frame_mode=declared_creative_alternative`, poi `museum.frame_finish=dark_wood` | Creare cornice materica coerente con dimensioni reali ma dichiarare che **non è la cornice autentica**; nuova fonte/licenza se necessaria |
| «Museum più lento, con ingresso più lungo» | `museum.entrance_seconds` (3–24), `museum.exit_seconds` (3–24) | Ri-regia camera in/out continua: no jump-cut |
| «Cinema Museum più lungo» | `slots.cinema_museum.target_seconds` (12–180) | Film musicale target; validare ritmo e diritti |
| «Cinema Standard più corto» | `slots.cinema_standard.target_seconds` (12–180) | Ri-regia dettagli originali; non tagliare un Critico |
| «Socrate più al centro» | `slots.<variante>.camera_center_x/y` (0.2–0.8) | Reframing e crop QA nel 9:16, senza teste o mani amputate |
| «Critico più approfondito» | `critico_pair.target_words` (170–850), `critico_pair.commentary_depth` | Nuovo copione scientifico **per la coppia** e **una sola NUOVA registrazione Gacrux condivisa**, durata reale dipende dal WAV |
| «Titolo più grande» | `cover.title_size_scale` (0.7–1.35) | Solo impaginazione; titolo inglese esatto e nome artista invariati |

Altri campi disponibili sono dichiarati nella sezione `adjustable_fields` del preset: movimento per variante, margine sicuro, architettura e trattamento cornice. **I vincoli di qualità NON diventano disattivabili** (no persone tagliate, voce condivisa, originali e copyright, camera V57, niente spese video API non autorizzate, QA vero).

**Due tipi di istruzioni nuove**:
- «Per questo quadro…» → cambia **solo** la ricetta dell'opera, preserva il preset e tutte le altre.
- «D'ora in avanti, per tutti i video…» → richiede modifica **versionata** del preset + regole attive, aggiornamento tests/changelog e conferma dell'ambito. Niente riscritture silenziose.

## Come usarlo — strumenti realmente installati

```bash
# CREA SOLO UN PROGETTO DI PIANIFICAZIONE (non renderizza):
python src/artvision_recipe_v68.py init \
  --id dipinto-scelto-2026 --title "Titolo inglese esatto" --artist "Autore" \
  --source-url "https://fonte.museale.example/opera" \
  --out docs/productions/dipinto-scelto-2026/ARTVISION_RECIPE_V68.json

# Una modifica locale, preservando il file precedente:
python src/artvision_recipe_v68.py set \
  --recipe docs/productions/dipinto-scelto-2026/ARTVISION_RECIPE_V68.json \
  --field slots.cinema_museum.target_seconds --value 60 \
  --reason "L'utente vuole un Museum più lento per questa opera" \
  --out docs/productions/dipinto-scelto-2026/ARTVISION_RECIPE_V68_REV2.json

# Schema, impostazioni, identità audio e SHA:
python src/artvision_recipe_v68.py validate --recipe docs/productions/dipinto-scelto-2026/ARTVISION_RECIPE_V68_REV2.json

# Il controllo prima del RENDER applica ANCHE il pilot lock V58:
python src/artvision_recipe_v68.py validate --for-render \
  --recipe docs/productions/dipinto-scelto-2026/ARTVISION_RECIPE_V68_REV2.json
```

**AVVERTENZA:** lo strumento V68 crea e verifica **ricette di pianificazione**; non è un quarto renderer generico e non promette di rendere qualsiasi quadro da solo. Prima di eseguire un nuovo dipinto occorrono foto/cornice/misure/diritti di quella opera, un renderer davvero compatibile, prove V13/V54/V46/V55 e autorizzazione allo sblocco del pilota. Le 4 varianti Museum e Critico restano produzioni tecniche distinte.

## Cosa esiste davvero del pilota Socrate

Scheda storica ufficiale: `docs/ARTVISION_SOCRATES_4X1_QUATTRO_MP4_REALI_V67_20261029.md`. I quattro MP4 sono **realmente prodotti** e distinti; **0/4 V25 Gold Master certificati**. La voce Gacrux originale condivisa ha SHA256 `b26b6826380c8dcc9b27a590bb6ecd43dd12107dafd367e429ad43351bd8a476`; in entrambi i Critico il medesimo WAV e le dieci sezioni narrative ASR. Cinema Museum V61 elimina gli spettatori tagliati. I master Cyclops V57 e Hiroshige V46 restano riferimenti complementari. Il feedback del proprietario del 29/10/2026 approva la **bontà del modello**, non la qualità definitiva di ogni dettaglio dei quattro film.

**Conservazione dei file:** GitHub conserva qui codice, preset, storia, ricette, licenze, hash, link ai run. **Non conserva automaticamente i grandi MP4 o il WAV**: alcuni sono nei file della conversazione; artifact GitHub Actions possono scadere. Prima di produrre in serie, effettuare un salvataggio durevole autorizzato dei master in archivio privato e verificare singolarmente 4 MP4, player, copertine, 16 post, ZIP, SHA256 e possibilità di recupero. Non scambiare un file manifest con un video archiviato.

## Ordine operativo per partire bene con la serie

1. **Socrate = base creativa positiva V68**, ma ancora con review/QA V25 da ultimare; raccogliere tue eventuali correzioni prima di chiamarlo Gold Master.
2. Selezionare un **secondo quadro pilota volutamente diverso** (es. verticale, piccolissimo, cornice/epoca diversa) con tua autorizzazione esplicita; usare preset V68, fonti specifiche, due Critico con WAV condiviso, due Cinema realmente diversi; fare la stessa QA e consegna.
3. Confrontare il secondo con Socrate. **Dopo due 4×1 riusciti, e soltanto previa tua conferma**, valutare riapertura della coda di serie e scelta autonoma delle opere.
4. Accumulare feedback incrementale: correggere per singola opera o nuova versione globale; mai rifare la ricerca delle regole da zero e mai perdere la versione funzionante.

**Unico owner:** automazione `6adca191603c8191a90d5190901cd034`; `config/artvision_pilot_lock_v58.json` resta attivo. Nessuna nuova produzione o spesa API video tramite questo documento, né pubblicazione social.
