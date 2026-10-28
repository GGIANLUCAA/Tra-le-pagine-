# Audit effettivo di conformità — Il pifferaio di Hamelin (29/10/2026)

**Esito: BLOCCATO / rendered_needs_review / NON MASTER.** Audit riferito esattamente al video `Pifferaio_Racconto_3min.mp4` prodotto nella conversazione. SHA256 del MP4: `aed20f7fb594f5bb3cb67521571e0c3de9af167fd6f412fb4523cfdd2e736f0a`. Dimensione 12.174.997 byte; ffprobe: 174,600 s, 720×1280, H264 + AAC. ZIP dossier: 32 elementi, CRC integro.

## Violazioni certe
1. **Voce:** audio narrato con Microsoft Edge Neural Diego invece di Google Gemini Gacrux esplicitamente richiesto. `QA_STATO_REVISIONE.json` attesta la sostituzione; non esiste autorizzazione utente. **Bloccante.**
2. **Metadati contraddittori:** `DOSSIER/metadata.json` e `PROJECT_V13.json` prescrivono Google Gacrux; `QA_STATO_REVISIONE.json` dichiara Edge. Un MP4 con AAC non prova l'identità vocale.
3. **V13 incompleto:** `DOSSIER/PROJECT_V13.json` ha `schema=project-v13-draft` e `status=assets_pending_voice_free_quota_unconfirmed`, non progetto release validato.
4. **V35 incompleto:** `DOSSIER/SCHEDE_VISUALI_V35.json` ha `schede-visuali-v35-draft`; tutte le 16 schede indicano controlli visivi/diritti pending.
5. **Aderenza scena-narrazione:** la tavola iniziale non raffigura la montagna che si chiude; la veduta di Hamelin è sostituita da una scena domestica; mancano rappresentazioni letterali di tuffo dei topi nel fiume e apertura del passaggio montano. La stessa `REVISIONE_E_STATO_20261028.md` ammette questi difetti.
6. **Pacchetto V55 incompleto:** il ZIP completo contiene 16 illustrazioni, 4 post, audio, copione e MP4, ma NON contiene il JPEG della copertina, pur essendo stata consegnata separatamente.
7. **Approvazione artistica assente:** lo stesso `QA_STATO_REVISIONE.json` riporta `rendered_needs_review`, `not_approved_final=true`. Nessuna revisione umana specifica del SHA256 esatto è stata allegata.
8. **Provenienza non approvata:** `PROVENIENZA_IMMAGINI.json` documenta 16 sorgenti e hash ma `editorial_approval=pending human visual and story review`.

## Verifiche tecniche superate, senza implicare qualità artistica
- MP4 9:16 720×1280 H.264 + AAC, 174,6 s, tracce video+audio (nessuna traccia sottotitoli nel container).
- ZIP dei materiali integrità CRC superata; quattro file post social presenti.
- Voce generata gratuitamente con workflow dedicato, ora eliminato perché non conforme; nessuna chiamata Vidu effettuata durante questa produzione.

## Ulteriori accertamenti ancora necessari
- Ascolto integrale per naturalezza e sincro scena/parlato.
- Verifica visiva dei raccordi, volti, mani e assenza di ghosting; recensione artistica con timecode e hash.
- Diritti delle singole riproduzioni, coerenza del montaggio e creditazione della musica, controllo dell'opening 0–7 s.
- Verifica effettiva del download Android e dell'eventuale importazione Video Library Studio (non attestati).

## Riparazione obbligatoria
**Non consegnare come FINALE o importare in archivio approvato.** Conservare la bozza come prova tecnica. Preparare V13 e V35 completi, abbinare nuovamente scene vere al parlato, validare Gacrux + quota prima di qualsiasi TTS, produrre il master conforme e compilare prove di revisione sull'hash del nuovo MP4. Effettuare soltanto acquisizione/generazione gratuita conforme alle policy; spesa video IA: nessuna senza autorizzazione separata.

Questa analisi riguarda **solo l'episodio Pifferaio**, non certifica lo stato degli altri video del repository. I test tecnici, i campi JSON compilati e la presenza di metadati non possono da soli attestare un giudizio artistico umano.
