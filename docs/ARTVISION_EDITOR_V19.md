# ArtVision Editor V19 — regia flessibile, fonti e post Facebook

**Nuovo modulo ADDITIVO.** Non altera `modules/artvision/APPROVED_PRESET.json`, il motore Cinema V6, Critico V2, V17, V18, i master MP4 esistenti, la voce Google, i workflow o il sito. Nessuna pubblicazione automatica e nessuna API a pagamento.

## Perché
Dal confronto tra il John Martin V6 e i Reels di riferimento emerge che serve variare le focali, evitare la ripetizione di zoom/stesso fondale sfocato, motivare ogni cambio con la composizione e preparare **una descrizione social completa**, oltre alla documentazione tecnica.

## Regole dure già approvate
- **Cinema V6:** intro fissa ARTISTA + MUSIC BY, dopo nessun testo/sottotitolo/voce, no CTA o richieste di contributi nel video. Il gancio è visivo, non una frase aggiunta al film.
- Rispettare la regia personalizzata per artista e preservare il Gold Master; il JSON di esempio **non è** un rendering universale né una lista completa dei 38+ shot.
- Controllo solo via Android; esecuzione Python gratuita su ambiente predisposto/GitHub Actions se già disponibile.
- Separare consegna del MP4, pubblicazione, crediti, fonti, misure reali e supervisione artistica.

## Nuovo processo per ogni film ArtVision
1. Recuperare asset e licenze autenticati, musica e storyboard originali; non ripartire dal solo MP4 se disponibili i sorgenti.
2. Preparare un `brief` con `scenes[]`: `artwork`, `framing`, `move`, `purpose`, primo `visual_hook`.
3. Prima di renderizzare, creare piano e controlli:
   ```bash
   python src/artvision_editor_v19.py --brief templates/ARTVISION_JOHN_MARTIN_V19.json --out output/john-martin/editorial
   ```
4. Correggere gli avvisi su ripetizioni, sfondi sfocati, opere non registrate, licenze incomplete. Una ripetizione può essere voluta.
5. Montare col renderer V6 dedicato all'artista **senza modificare la baseline**; adattare gli ingressi ai picchi e alle frasi musicali dopo aver ascoltato il brano, senza tagli meccanici ogni N secondi.
6. Continuare con QC V17 e la visione/ascolto integrale; verificare ogni inquadratura, intro, coerenza opere, audio e finale. Il modello non riconosce automaticamente errori storico-artistici.
7. Scrivere e verificare i fatti della caption in `editorial`. L'output `SOCIAL_CAPTION_V19.txt` unisce introduzione, racconto, domanda facoltativa, musica con licenza e hashtag. Mantenerne 2–5 pertinenti; nessun clickbait ingannevole.
8. Prima dell'uso commerciale verificare tutte le condizioni dei beni culturali e delle riproduzioni, oltre alle licenze; l'elenco `sources` non è una clearance legale.
9. La review e l'eventuale pubblicazione sono fasi SEPARATE. Report status `editorial_review_required` NON significa pronto.

## Output e limiti reali
- `EDITOR_REPORT_V19.json`: criticità tecniche del brief e stato prudente.
- `DIRECTION_PLAN_V19.md`: scelte di regia motivate.
- `SOCIAL_CAPTION_V19.txt`: didascalia per Facebook e crediti.
- `SOURCES_V19.md`: registro fonti e riuso.

**Non** analizza direttamente il ritmo di un MP4, non genera audio o filmati e non dimostra l'efficacia del montaggio. Queste funzioni appartengono ai renderer esistenti e a V17. I dati social vanno ricavati solo dagli Insight reali.

## Per la regia di altri formati
Il formato opzionale `artvision_meraviglia_breve` può avere testo minimo e una struttura più corta SOLO se richiesto; non sostituisce il Cinema V6. Non generare due versioni dello stesso film senza richiesta esplicita.

## Test
```bash
python -m unittest discover -s tests -p 'test_artvision_editor_v19.py' -v
```
