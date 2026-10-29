# ARTVISION — CONTRATTO MADRE 4×1 V58 (29/10/2026)

**Decisione permanente del proprietario:** UNA OPERA = QUATTRO FILMATI ORIGINALI, distinti e completi. Un rendering intermedio, una scheda, uno ZIP o un duplicato non equivalgono a un filmato approvato. Questo documento integra AGENTS.md, REGOLE_ATTIVE.md, V25/V28/V33/V44/V46/V54/V55/V57; non abbassa i gate storici.

## Pacchetto unico per opera

| ID slot | Voce | Regia | Differenza obbligatoria |
|---|---|---|---|
| `critico_standard` | **Gacrux reale** e testo critico italiano | Critico classico, dettagli originali sincronizzati | Racconto critico verificato; non una versione Cinema con voce aggiunta |
| `critico_museum` | **IDENTICO file WAV e IDENTICO copione** del Critico Standard | Museum camera V57, ingresso e uscita continui | La visita museale modifica veramente il racconto visivo, non l'audio |
| `cinema_standard` | Musica autorizzata, **senza parlato** | Montaggio cinematografico dei dettagli pittorici autentici | Progressione autonoma con ritmo e tagli giustificati |
| `cinema_museum` | Musica autorizzata, **senza parlato** | Museum V46/V57, sala e cornice vere o ricostruite specifiche | Unico viaggio camera in/out nel quadro, senza jump cut o slideshow |

**Una ricerca, quattro storyboard distinti.** Recuperare una sola volta riproduzione autentica/diritti/misure/cornice, dossier 4×1 V54/V13 e 3+ dettagli veri; ogni slot ha il proprio MP4, SHA256, cover, 4 post originali FB/IG/TikTok/YouTube, fonti/licenze della REGISTRAZIONE musicale, ricetta, QA, ZIP completo CRC e ZIP Android solo MP4. **Target: 4 MP4 + 4 ZIP completi + 4 ZIP Android + 16 post.**

## Regia, voce e qualità

- **Critico:** copione rigoroso e narrato con Gacrux autentico, cache WAV con SHA e allineamento parola/scene; se cache assente: `blocked_voice_unavailable`, mai sostituire con TTS diverso né spendere senza autorizzazione.
- **Museum:** V57 Cyclops per camera continua; V46 Cyclops SENZA STRISCE per cornice con vera materialità, rilievi, battuta/incasso, ombra; Hiroshige per scala fisica con persona/porta. **NON** replicare scenografia Cyclops su altre opere. Misure, fotograﬁa ed epoca del quadro documentate; ricostruzioni moderne dichiarate e no falsa attribuzione al museo. Se manca la qualità: `blocked_quality_museum_v46_not_met`, non renderizzare la finzione.
- **Apertura 0–3–7 secondi:** titolo inglese esatto e artista sul primo frame; dettaglio autentico emotivo entro 3 s; nuova scoperta entro 7 s. Non mostrare corridoi vuoti o immagini quasi immobili per tutta l'apertura.
- **Video:** 9:16, H264/AAC; nessun bordo stirato, ghosting, persona/oggetto inventato, clip di repertorio improprie, audio basso o parlato assente nei Critico. Quattro montaggi realmente differenti; una correzione dello stesso slot non diventa la quinta variante.
- **QA vero:** ffprobe, decodifica integrale, SHA256, estrazioni frame 0.1/1/3/5/7 s, confronto visivo con originali/reference, visione+ascolto a velocità normale, ZIP CRC, prova scaricamento Android. Un test automatico NON certifica approvazione artistica. `rendered_needs_review` non è `approved_for_final_delivery`.

## Piloti, non serie

**Pilota 1 obbligatorio:** `david_death_of_socrates_met436105_1787`, The Death of Socrates (Jacques-Louis David, Met 436105).
- Cinema Standard originale SHA `4ea696772dd80e03a73c7b3570a22c7915787d47b77822a97ee040cbca959ce9` è **UN SOLO slot in review**. Eventuali revisioni audio/visive sono versioni del medesimo slot, non un secondo filmato.
- Critico Standard/Museum: `blocked_voice_unavailable` fino a cache Gacrux esatta e verificata. Museum ulteriormente bloccato fino a sala/cornice V46/V57 specifiche.
- Cinema Museum: `blocked_quality_museum_v46_not_met`; NON finta parete piatta.
- Completamento effettivo: **0/4 approvati**, anche quando 1 MP4 tecnicamente esiste.

**Pilota 2:** opera molto diversa, solo DOPO approvazione umana del primo 4×1. **Nuovi quadri automatici disabilitati** fino all'approvazione dei piloti e consenso esplicito alla riapertura della coda. Config operativa `config/artvision_pilot_lock_v58.json`. Un solo owner ArtVision e al massimo un renderer concorrente. Non toccare master approvati o produzione di libri/storia.

## Distribuzione, attribuzione e blocchi

- Solo import autorizzato nell'archivio **privato**, non pubblicazione social; verificare distintamente MP4, player, copertina, 4 post e ZIP; se non confermati dichiarare `archive_sync_pending`. Scheda ARCHIVE_STAGING_V55 solo dopo MP4 reale, hash e byte reali, senza approvare V25 in automatico.
- ZERO spese Vidu/Runware/Kling/Wan/Seedance/GPU/API a credito senza permesso specifico per ogni scena. Le chiavi non costituiscono autorizzazione.
- Ogni ciclo deve tentare un avanzamento **esecutivo** verso il prossimo MP4 o pacchetto, non ripetere diagnosi; report: MP4+SHA, ZIP+CRC, approvazioni reali, import verificati, prima barriera concreta, correzione/test/commit.
- Nessun `Gold Master` o 4×1 completo senza quattro video **distinti, revisionati, consegnabili** e autorizzazione artistica/V25 prevista.

**Ogni volta che una regola V53/V55 anteriore dice «coppia», «due video» o «nuovo quadro ogni due ore», per ArtVision 4×1 prevale questo contratto; per libri e restauri storici resta il proprio format.**
