# La Storia Rivive V143 — ricerca del primo pilota, trincee russe 1915

Data 31 ottobre 2026. Solo Restauro storico. Issue #144 / mandato V108.

## Fonte e piano operativo

Quinto filmato storico originale provato in sequenza dopo la filatura francese 1920 (veto artistico), Casa Bianca 1917–1921 (una sola finestra B/N dinamica), Versailles 1919 (una finestra) e Costantinopoli 1916 (solo tre su cinque). **Nessuno dei quattro è stato promosso a episodio completo.**

Nuova fonte: [*Into the Catacombs of War – Albert Dawson Inspecting Russian Trenches (August 1915)*](https://commons.wikimedia.org/wiki/File:Into_the_Catacombs_of_War_-_Albert_Dawson_Inspecting_Russian_Trenches_(August_1915).ogg) su Commons, indicata come copia da Library of Congress: Ogg/Theora di circa 295 s, raster del file 1920×1080, circa 106 MB. Copia digitalizzata caricata nel 2022 da Ron van Dopperen. **Raster nominale non equivale a nitidezza nativa, dichiarazione Public Domain USA non conferma legalità del riuso in Italia.**

Obiettivo editoriale: scene rare della Grande Guerra nelle trincee, con cinque vere riprese distinte in movimento; evitare propaganda, foto di corpi e ricostruzioni AI ingannevoli. Non confondere un cartello con una ripresa.

## Cambiamenti reali e limiti della V143

- Nuova fonte `russian_trenches_1915` nella coda editoriale, con tutti i flag di diritti, attribuzione, revisione visiva e SHA in `false`.
- Registro SHA-bound V133 esteso al film bocciato `constantinople_messter_1916`, identificato dal file vero Commons SHA256 `2a9e0495749040a4b138da095fc80e834ae89cbfc93116aabbe75b9bc9b17aec`, [collaudo #41209687003](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41209687003). 3 sole finestre B/N originali in movimento, 0 nuove I2I, 0 nuovi Vidu. Non riscaricarlo ad ogni slot 3h.
- Workflow gratuito e PR-scoped `.github/workflows/storia-v143-trenches-source-audit.yml` scarica e legge UNA sola copia autentica, con limiti 160 MiB, FFprobe e SHA reale, V124/V125/V126/V128/V129, report JSON e contact sheet. Non carica l'originale nel catalogo, non avvia motori I2I o Vidu, non usa credenziali e non pubblica.
- Test `tests/test_storia_rivive_v143_pilot_source.py` e regressione della coda V140 per 4 rifiuti documentati + 7 file SD + nuova fonte 1915; CLI di selezione a tre ore controllato senza crediti.
- Lo stack V142 ha già eliminato un falso rifiuto PTS di Ogg/Theora: dal vero film 1916 `time_base=100/2997` e timestamp showinfo arrotondato si ricava il PTS razionale esatto; CI V142 157/157, fonte filmica decodificata. Questo non equivale a 5 scene per Costantinopoli.

## Condizioni obbligatorie prima del primo master

1. Cinque vere inquadrature originali diverse, 5 finestre movimento 0,9–2,5s, esatto frame source-locked, soggetti fotografici nitidi in 9:16, controllo cambi scena e review di persone, mani, oggetti e ritmo. Scartare senza produzione se non ottenibili.
2. Identificare opera originale e l'eventuale ristampa digitalizzata nel catalogo Library of Congress, licenza, coautori, e **diritti di riutilizzo in Italia**. Niente clearance presunta.
3. Solo dopo conferma di qualità e diritti, quattro restauri **reali I2I** non DDColor+upscale spacciato per fotografia moderna, più una clip Vidu autenticamente animata dall'identico frame originale della quinta scena. Gate Vidu per scena, verifica separata saldo consumer/API, costo e credito prepagato già autorizzato; zero acquisti, doppie chiamate o rinnovi.
4. Montaggio cinematografico 14–35s e primo reveal colore entro 1,4s, colore osservabile 2–3s, titolo discreto inglese **RUSSIAN TRENCHES · 1915** solo dopo datazione accertata, musica con diritti, copertina, 4 descrizioni social, MP4/ZIP veri decodificabili e scaricabili.
5. QA byte V91/V94/V96/V99 e revisione artistica prima di marcare finito. Non pubblicare social/sito senza consenso distinto. Solo dopo **tre episodi pilota reali** passare a ciclo produzione master ogni tre ore; saltare i cicli non idonei.

**Stato iniziale:** ricerca e collaudo nuovi file reali, NON episodio prodotto. PR draft stacked su V142, nessuna modifica a main, ArtVision, WOW LAB o SF1906 V98.
