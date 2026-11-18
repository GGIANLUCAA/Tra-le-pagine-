# ArtVision · Handoff operativo 18 novembre 2026 · controllo anti-doppioni

**Stato:** ricerca / preflight, non render. Nessun nuovo MP4, ZIP o cover generato in questo controllo. Nessuna pubblicazione.

## Fonti repo effettivamente lette
- `data/archivio-generale/opere.json`: generato 17/11 16:40 UTC; 95 opere censite, 153 slot documentati, 127 non documentati, 541 item sito. È uno snapshot, non una verifica live del playback.
- `research/artvision_owner_selected_30_future_20261109.json`: 30 opere approvate per studio futuro; NON equivale ad autorizzazione individuale per produrre tutte le 30.
- `queue/artvision_owner_selected_ten_20261102.json`: opera e variante devono essere confrontate con i master prima del dispatch.
- `research/artvision_owner_30_dadd_repin_primary_research_20261116.md`: Dadd Tate T00598, Tate HTTP 403, file e diritti non verificati; Repin Sadko Russian Museum Ж-4002, immagine originale HD, licenza e SHA non verificati.
- PR #344 già aperta per Salvator Rosa *Scenes of Witchcraft: Morning*: evitare di aprire un secondo dossier identico o contare la ricerca come video.
- Documento `docs/productions/2026-11-15-arbo-gacrux-free-tier-api-access-blocked.md`: Gacrux bloccata 404/400; nessuna voce alternativa consentita.

## Gate per prossimo dispatch
1. Rileggere checkpoint recentissimi e run attivi, non basarsi soltanto sul registro snapshot.
2. Escludere varianti già prodotte di Die Sünde, Bierstadt Buffalo, Turner Parliament Fire, Cole Manhood, Moreau Oedipus/Sphinx, Delacroix Rebecca e Rosa Day/Night/Evening. Non tentare nuovamente Belvedere 403 / Wikimedia 429 per Segantini.
3. Per un Cinema nuovo verificare bytes, SHA256, pixel, fonte museale e licenza del singolo file; verificare musica reale con licenza commerciale multipiattaforma e Content ID; solo allora render.
4. AAC 48 kHz stereo **con test di udibilità** e non soltanto esistenza stream, più full decode; preservare forma circolare esatta dei tondi Rosa.
5. Distinguere TECH PASS, ART REVIEW PENDING, ARTIFACT_ONLY, LIBRARY_ONLY e sito online. Non dichiarare READY se manca un gate.

## Esito
Nessuna nuova produzione dichiarabile. I due dossier shortlist Dadd/Repin restano bloccati su asset e diritti; Rosa Morning resta candidata già oggetto di PR #344, non un MP4. Nessuna modifica a queue, workflow, TTS, segreti, master o automazioni. Zero spese.
