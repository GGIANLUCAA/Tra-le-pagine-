# ArtVision 4×1 — blocco pilota V58 (29/10/2026)

## Decisione esplicita
Non scegliere più nuovi quadri finché non esiste almeno un gruppo di **quattro video distinti davvero finiti, riproducibili, con pacchetti completi e approvazione artistica dell'utente**. Primo pilota: **The Death of Socrates**, Jacques-Louis David (Met 436105). Un secondo pilota, con opera diversa, potrà essere avviato solo su decisione dell'utente; non riattivare automaticamente la produzione seriale.

Il vincolo macchina è `config/artvision_pilot_lock_v58.json`; `src/artvision_next_render_v55.py` ora legge il lock e restituisce `pilot_in_progress` invece di proporre nuove opere. Per ogni workflow che richiama direttamente il renderer, imporre prima `src/artvision_pilot_guard_v58.py` oppure il wrapper vincolato prima di eseguire il job. La sola modifica dello scheduler **non** impedisce a comandi indipendenti dal ponte di rendere un altro soggetto: nessun falso claim di blocco totale finché ogni entrypoint non è integrato.

## Quattro film distinti e invarianti
1. Critico Standard: narrazione italiana approfondita, **vera Gacrux**, dettagli sincronizzati.
2. Critico Museum: **identico WAV e copione**, nuova regia Museum camera V57 senza tagli.
3. Cinema Standard: solo musica autorizzata, montaggio artistico di dettagli.
4. Cinema Museum: solo musica autorizzata, cornice materica e sala documentata/ricostruita appositamente per questa opera, scala fisica, camera V57 in/out senza tagli.

Socrate: Cinema Standard V55 SHA256 `4ea696772dd80e03a73c7b3570a22c7915787d47b77822a97ee040cbca959ce9` già renderizzato e **needs_review**, NON rigenerare per conteggiarne un altro. Il Cinema Museum manca e resta `blocked_quality_museum_v46_not_met` finché manca una sala/cornice specifica valida. Entrambi Critico restano `blocked_voice_unavailable` finché non si trova cache Gacrux vera, esatta, verificata. Nessun Gold Master e nessuna approvazione V25.

Per ogni variante: fonte autentica/diritti e misure documentate, dossier 4×1 V54/V13 unico, regia specifica e prova first 0–3–7, MP4 H264/AAC 9:16, cover JPEG, quattro post V28 differenti, ricetta/hash, ffprobe+decodifica+visione/ascolto reale, ZIP completo CRC e MP4 Android verificato. Se non visto/ascoltato, `rendered_needs_review`. Import privato solo autorizzato, separare conferma MP4, catalogo, cover, post, player, ZIP; altrimenti `archive_sync_pending`. No pubblicazione social, API video pagate o GPU pagate senza permesso specifico per scena.

Un solo owner ArtVision; nessun secondo renderer simultaneo; nessuna alterazione di master o approvazioni inventate. Ogni ciclo deve correggere la prima barriera reale verso **tutti e quattro** i film Socrate invece di produrre una nuova ricerca o un nuovo quadro.
