# Audit chiavi API della foto — 4 novembre 2026

## Evidenza reale

Esecuzione GitHub Actions (solo lettura, NESSUNA chiamata API esterna):
https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41743573803

Il job `actual-presence-only` è passato. La presenza dei nomi
e dei valori dei segreti è stata verificata soltanto come valore
non vuoto, senza stampare i valori. Nessuna quota provider consumata.
I test offline del codice di audit sono anch'essi passati.

| Gruppo | Presenza nel workflow | Stato concreto nel codice |
| --- | --- | --- |
| AI Horde primaria | SÌ | Generazione immagini sperimentale solo su comando esplicito |
| AI Horde secondaria | SÌ | Riserva, non utilizzata per aggirare code |
| Gemini TTS primaria | SÌ | Integrata nei workflow voce esistenti; non significa API valida |
| Gemini TTS secondaria | SÌ | Presente come secondo account/alias; utilizzo condizionato |
| Groq | SÌ | Adapter editoriale diretto; senza attestazione del piano Free non chiama modelli |
| Hugging Face | SÌ | Token usato in job di miglioramento/restauro immagini; non garantisce disponibilità GPU |
| OpenRouter | **NON RILEVATA** | `OPENROUTER2` appariva in screenshot, ma entrambi i nomi esatti `OPENROUTER2` e `OPENROUTER_API_KEY` sono vuoti per questa GitHub Action |
| Pixabay primaria | SÌ | Adapter ricerca immagini/video su richiesta, senza raccolta in massa |
| `PRIXIBAY2` | SÌ | Riserva con possibile refuso, volutamente non usata |
| Vidu API (VIDUOK o VIDU_API_KEY) | SÌ | Controllo saldo e workflow video esistenti, con gate costi |
| Vidu (VIDU / VIDU2) | SÌ | Presenti, ma non equivalgono necessariamente a credenziali API attive; mai switch automatico |

**IMPORTANTE:** questo test non verifica la validità presso il provider,
le quote residue, gli abbonamenti, la fatturazione, l'idoneità per
usi commerciali, l'effettiva produzione di MP4 o la sincronizzazione
col sito. Il test non avvia Vidu né trascrizioni, TTS, ricerche stock
o inference. NON chiama Groq/OpenRouter/HF/Pixabay/Gemini/Vidu/AI Horde.

## Diagnosi OpenRouter

1. Il GitHub Actions secret con nome esatto OPENROUTER2 non viene
   ricevuto da questa esecuzione, nonostante sia visibile nella foto.
2. Non equivale a dichiarare che sia stato eliminato: può dipendere
   dal nome, dall'aggiornamento, dallo scope o dal valore archiviato.
3. Usare la pagina
   https://github.com/GGIANLUCAA/Tra-le-pagine-/settings/secrets/actions
   per controllare il secret **del repository corretto**, senza mostrare
   il contenuto in chat. Aggiornare il segreto esistente in modo sicuro,
   se necessario.
4. Il nostro bridge di fonti rileva già il nome OPENROUTER2, ma NON
   può e non deve effettuare inferenza a pagamento; per usare modelli
   `:free` sono ancora necessari controllo condizioni, quota e
   policy di costo zero. Non creare credenziali di prova in file Git.

## Workflow di audit riutilizzabile

- `.github/workflows/secret-presence-audit-v1.yml`
- `src/secret_presence_audit_v1.py`
- `tests/test_secret_presence_audit_v1.py`

GitHub: Actions -> **API secrets - presence-only connection audit (zero requests)**
-> **Run workflow**. Output in **actual-presence-only**. Non è programmato
per girare di continuo e non consuma crediti. I nomi dei secret sono
riportati soltanto come booleani, mai il loro valore.

## Stato integrazione del progetto

Questi servizi sono integrati **a livelli diversi**, non tutti attivi:
- Gemini (TTS) e Vidu (video) esistono in workflow dedicati con gate;
- Pixabay e AI Horde hanno workflow manuali;
- HF ha job di restauro specifici;
- Groq ha adapter editoriale opzionale con policy costo zero;
- OpenRouter è un candidato riconosciuto, non un'inferenza operativa;
- chiavi doppie non autorizzano fallback o spese;
- i report di presenza non certificano contenuti completi o pubblicabili.

L'automazione di produzione video resta proprietaria dei file e delle
verifiche di qualità approvate. Nessuna nuova spesa, pubblicazione o
rimozione di blocchi autorizzata da questo audit.
