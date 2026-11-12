# ArtVision — Arbo Critico Standard V1 · stato reale della voce (12/11/2026)

## Fatti verificati
- PR [#275](https://github.com/GGIANLUCAA/Tra-le-pagine-/pull/275) incorporata in `main` (merge `2b8b74bae073a883a50d3dd8ef8835ef515f25ca`).
- [GitHub Actions run #43208972637](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43208972637), esito workflow **success**, MA il job `render_private_critico` ha **saltato il rendering**.
- Preflight **PASS**: 219 parole, 10 beat e SHA256 del copione `dff53a943232489ba44690a6b0b91ad1a5fea48202b28e0f49d59f8436d74e17`. Script e storyboard in `scripts/artvision_owner_arbo_critico_standard_v1.py`.
- GitHub runner logs `job 131151407011` (2026-11-12 11:25 UTC): `GEMINI_API_KEY: ***` presente, `GEMINI_TTS_FREE_QUOTA_CONFIRMED:` **vuota**, `GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED:` **vuota**.
- La condizione `eligible=false` ha creato `VOICE_BLOCKED_NO_COST.txt`; job `Install free tools and produce one genuine narrated video` **skipped**. Artifact blocco #13939946779 (221 byte) e preflight #13939852302. **Zero MP4 narrati**, zero SHA/ZIP di Critico, zero chiamate Google da questo job.
- Il Cinema Standard di Arbo continua valido e invariato (checkpoint `queue/artvision_owner_30_render_checkpoint_20261111_arbo_wild_hunt.json`). Nessuna modifica ai master, nessuna pubblicazione, nessun Gold.

## Soluzione senza spese inventate
Prima di porre valori `true`, il proprietario deve verificare realmente sul progetto/account Google corrispondente a `GEMINI_API_KEY` che **la generazione TTS richiesta sia coperta da quota gratuita** e che **la fatturazione sia disabilitata/non possibile** per quella chiave, non soltanto che il saldo al momento sia zero. Se entrambe le condizioni sono confermate:
- Impostare in GitHub > Settings > Secrets and variables > Actions > Variables i nomi esatti `GEMINI_TTS_FREE_QUOTA_CONFIRMED` e `GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED` entrambi a `true`.
- Solo dopo verifiche dei valori, eseguire nuovamente `.github/workflows/artvision-owner-arbo-critico-standard-v1.yml` via workflow_dispatch su `main`. **Non** usare re-run del workflow senza che i gate risultino risolti.
- Se il progetto Google ha fatturazione attiva/non verificata, **non impostare true**: usare invece audio precedentemente generato e verificato per lo **stesso copione** se esiste o una via alternativa effettivamente gratuita e autorizzata; questa non è attualmente comprovata.

## Fallback operativo
Il proprietario vuole produzione seriale; i due gate bloccano per ora **solo i nuovi Critico Google**, non i Cinema di altre opere con fonti e riuso validati. L'owner deve lasciare Arbo Critico come `VOICE_BLOCKED_NO_COST`, passare a un'altra opera indipendente della shortlist, non ripetere ogni ora lo stesso errore e non presentare il preflight come MP4 concluso.

Quando il gate si sbloccherà, il rendering dovrà ancora superare decodifica FFmpeg audio/video, SHA, ZIP CRC e controllo artistico parola-dettaglio; nessuna pubblicazione o approvazione automatica.
