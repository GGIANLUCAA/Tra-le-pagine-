# CINEMA REALE — short cinematografici autentici e internazionali
**Serie indipendente · Regole locali v1 · 4 novembre 2026**

## Isolamento obbligatorio (regola fondamentale dell'utente)
Questa è **una serie autonoma**, non una nuova versione o un aggiornamento globale di Tra le Pagine/ArtVision.

Queste regole valgono **ESCLUSIVAMENTE** per file, episodi, richieste e workflow identificati con `project_id: cinema_reale` e collocati sotto `projects/cinema_reale/` o sotto un output che dichiara esplicitamente lo stesso ID.

**NON prevalgono e NON modificano**:
- ArtVision 4×1, Critico d'arte, Museum Immersion, libri e altre serie.
- La Storia Rivive, inclusi vincoli 4+1, B/N→colore, Vidu, qualità V91/V94/V96/V99 e approvazioni passate.
- `AGENTS.md`, `START_HERE_GPT.md`, `docs/REGOLE_ATTIVE.md`, `config/editorial_rules.json`, codebase dei renderer esistenti, code e automazioni owner.
- Qualunque regola di un altro progetto, anche quando un componente tecnico viene riusato.

**Regola di conflitto:** se manca `project_id: cinema_reale`, queste regole **non si applicano**. Il riuso di FFmpeg, GitHub Actions, archivi video o un eventuale componente tecnico non trasferisce vincoli editoriali da una serie all'altra. Non assumere che 'senza voce/scritte/AI' sia una policy globale. Niente inserimento delle regole Cinema Reale in documenti madri. Qualunque futura modifica globale richiede decisione separata ed esplicita dell'utente.

## Regole creative ESCLUSIVE della serie
1. **Nessuna scritta nel video**: non inserire titoli, didascalie, anno, crediti, sottotitoli, watermark grafici, call-to-action o testi in alcuna lingua nei fotogrammi. Metadata, descrizioni social e copertine esterne al video possono contenere testo quando utile e conforme a diritti e requisiti di attribuzione; se una licenza richiede credito sovraimpresso nel video e non consente alternative, scartare la fonte.
2. **Nessuna voce e nessun parlato inserito**: niente voiceover, TTS o dialoghi aggiunti. Audio: musica originale/adeguatamente licenziata, suono d'ambiente autentico e sound design; evitare elementi parlati nel girato selezionato se compromettono l'universalità.
3. **Niente scena sintetica/ricostruita con AI**: usare riprese autentiche e licenziate con provenance controllata; esclusi Vidu, Wan, LTX, video AI, oggetti e volti inventati. Sono ammessi montaggio tradizionale, speed ramp sobria, audio mix, color grading, stabilizzazione non generativa. Non alterare prove documentali per creare un falso evento, né cercare di ingannare gli strumenti di etichettatura; non garantire assenza di label.
4. **Durata scelta dal regista**, non limite fisso di 20 s: ogni episodio deve avere inizio forte, sviluppo con escalation e finale/payoff compiuto, ottimizzato per fruizione social in 9:16. Tagliare ogni secondo superfluo, testare ritmo e sicurezza del crop.
5. **Originalità editoriale sostanziale**: non compilazioni banali di stock, ricerca di scene reali poco abusate, narrativa distintiva e coerenza delle riprese; il montaggio deve aggiungere una struttura creativa vera, senza fingere che eventi diversi avvengano in un'unica ripresa. Non promettere unicità assoluta né viralità.
6. **Qualità**: hook visivo e sonoro nei primi 0–2 s; poi curiosità → rivelazione → conclusione. Nessuna ripetizione, immagini ferme senza motivo, stacchi palesi, audio incoerente, crop che taglia il soggetto; controllare vero video intero su Android/verticale, non soltanto parametri tecnici.
7. **Diritti**: fonte, licenza commerciale, eventuali attribuzioni, autore, URL, SHA e scheda diritti per ogni asset. Verificare requisiti specifici di ciascun social; materiale di terzi non diventa automaticamente originale per piattaforme.
8. **Consegna**: MP4 9:16 decodificabile, file scaricabile tramite URL verificato, audio, copertina separata, materiali social separati, ZIP, rapporto QA e fonti/licenze. Senza QA e verifica non definirlo 'finito'.
9. **Android-first**: input e controllo dal telefono; esecuzione remota con GitHub Actions + FFmpeg e solo infrastrutture/add-on verificati. Nessun server GPU personale richiesto. Niente spese API senza autorizzazione puntuale e niente pubblicazioni social/sito senza consenso specifico.

## Identificazione e gestione indipendente
- `project_id: cinema_reale`.
- Cartelle episodi dedicate: `projects/cinema_reale/pilots/`, `projects/cinema_reale/episodes/`.
- Futuri workflow: nomi `cinema-reale-*`, trigger e percorsi dedicati, mai i trigger delle code `storia_rivive` o `artvision`.
- Asset e musiche indipendenti; non importare clip o regole degli altri progetti per comodità senza verificare diritti/compatibilità.
- Fonte pilota approvata per **validazione**, non per montaggio concluso: [pilots/001_no_road_leads_here.md](pilots/001_no_road_leads_here.md).

## Stato
Solo impostazione editoriale e isolamento configurati. Non significa che un workflow sia stato creato, un MP4 renderizzato, una fonte validata fino ai timecode o un contenuto pubblicato.
