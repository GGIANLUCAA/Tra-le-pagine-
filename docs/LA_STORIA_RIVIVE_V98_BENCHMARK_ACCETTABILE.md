# La Storia Rivive · benchmark V98 accettabile (feedback utente 30/10/2026)

## Decisione editoriale
L'utente ha visto **San Francisco · 1906 — V98** e lo ha definito **«un lavoro accettabile»**. È il **primo benchmark pratico APPROVATO COME LIVELLO MINIMO DI QUALITÀ ARTISTICA**, non un esempio perfetto e non un'autorizzazione a pubblicare sui social. Non confondere con certificazione diritti, revisione storica estesa o esito automatico di tutti i gate: restano obbligatori.

**Non tornare alle vecchie pipeline V83/V95 che generavano colori morbidi, stacchi Vidu incongrui e fotografie troppo ferme.** Migliorare V98 per piccoli passi e confrontare davvero il risultato.

## Asset e prova effettivi
- Release tecnica GitHub (reale e verificata): https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/tag/storia-rivive-san-francisco-1906-v98-4-real-i2i-1-real-vidu
- MP4 `LA_STORIA_RIVIVE_SF1906_V98_FOUR_REAL_I2I_ONE_REAL_VIDU.mp4` — 720 × 1280, H.264/AAC, 30 fps, **19,57 secondi**, SHA-256 `b20726893e067bbae493859ae1c51379c4abab8c2c8768d5c6f2d4ab324b47a8`, 7.412.672 bytes.
- ZIP Android `SAN_FRANCISCO_1906_V98_ANDROID_KIT.zip`, cover e post social nella stessa release.
- Produzione controllata in GitHub Actions run `41051785601` (success).
- Codice reale `tools/storia_sf1906_v98_reuse_real_vidu_43s.py`, workflow `.github/workflows/storia-sf1906-v98-exact-frame-vidu.yml`.
- Fonte autentica film Miles Brothers 1906 https://www.loc.gov/item/00694408/
- I primi 4 capitoli sono esattamente quelli della prova V97 con restauri generativi Finegrain + DDColor, **non** sola colorizzazione.
- 5º capitolo sostituisce il precedente filmato 411s con **la ripresa originale dello stesso film al t=43s**, segue 1,08s di vera pellicola B/N e la clip Vidu già generata per quella precisa sorgente, 5s di video a colori in movimento. Prima immagine Vidu vs fotogramma original film: correlazione di luminanza **0,994**, delta luminosità media **7,39** a risoluzione ridotta. Verificati più intervalli di vero movimento successivo al colore.
- In questa versione **0 nuovi crediti Vidu** (riuso clip vera V86 già pagata; task esistente). È corretto riusare solo clip quando stesso soggetto/shot/editoriale lo rende davvero appropriato, mai trasferire una clip di altro soggetto per risparmiare.

## Ricetta V98 da mantenere nelle nuove produzioni
1. Studiare 5 riprese d'archivio **davvero differenti** dello stesso luogo/periodo, documentare fonte, fotogramma originale, licenza, SHA e corrispondenza dei soggetti.
2. Quattro sezioni: filmato originale B/N realmente in movimento (1,2–1,5s quando appropriato) → freeze sul fotogramma autentico → trasformazione breve coerente → restauri a colori **veri image-to-image** (hold circa 1,6–2,2s, non 4s di immagine mediocre). Usare differenti tempi quando il contenuto lo richiede.
3. Quinta: originale in movimento → **esattamente lo stesso frame** come base della clip Vidu, graduale B/N→colore nel primo secondo di **genuino video a colori in movimento**, circa 5s. Non inserire arbitrariamente Vidu a una posizione del montaggio senza verificare geometria/prospettiva.
4. Mantenere il livello estetico V98, colori realistici e coerenza fra foto e Vidu; non inserire grandi titoli opachi che coprono soggetti, niente deformazioni di volti/persone/oggetti, niente clip geometriche o riempitive. Musica continua, un solo brano originale.
5. Consegnare sempre MP4 scaricabile verificato realmente e ZIP Android completo, con copertina, quattro post e report QA. Contraddistinguere **anteprima accettabile** da **finale pubblicabile**: il feedback non sostituisce la verifica dei diritti territoriali né la revisione visiva delle future ricostruzioni.
6. Rispettare V94 e V96: nessuna scorciatoia `NOT_THE_USER_APPROVED_EFFECT`, nessun bypass di gate, no spend Vidu senza autorizzazione prevista dalla regola di budget del progetto. Il benchmark V98 non modifica le regole ArtVision (quadri).

## Miglioramenti ammessi, senza rompere il benchmark
- Migliorare gradualmente nitidezza e fedeltà dei volti reali quando sono abbastanza grandi; verificare le fonti vicine prima di inferire dettagli.
- Rendere il passaggio visivo più invisibile e uniforme senza perdita del movimento.
- Ottimizzare colore/titoli/selezione delle scene **con comparazione A/B a video finito**, cambiando pochi parametri per volta e misurando se è un miglioramento.
- Non sostituire il formato 4+1 con vecchie colorizzazioni statiche. Mai contare zoom e crop come nuovi filmati.

**Citazione feedback:** «Questo lo posso considerare un lavoro accettabile». Registrare come **accettazione del livello V98** e **punto di partenza**. Nessuna pubblicazione automatica autorizzata da questa frase.
