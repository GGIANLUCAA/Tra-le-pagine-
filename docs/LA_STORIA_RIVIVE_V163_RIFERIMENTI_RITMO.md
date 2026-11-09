# La Storia Rivive — V163 · Correzione regia sugli esempi realmente forniti

**1 novembre 2026 — feedback esplicito:** il video «gatto 1900» di 24 secondi è stato rifiutato («orribile», «senza senso»); era dominato da pan/zoom su una sola immagine sintetica. **Non riutilizzare quel montaggio come template.** L'utente aveva fornito i video `43055` e `43056` come riferimenti estetici di trasformazione, non come materiale autorizzato al riuso.

## Controllo sui file reali (analisi locale, senza copiare i video nel repository)

| Origine | SHA-256 del file analizzato | Durata | Veri cicli visivi B/N → colore rilevati | Inquadrature B/N distintive rilevate | Primo colore |
|---|---|---:|---:|---:|---:|
| `43055(2).mp4` (riferimento utente) | `86a7dd3d2db0d18ba51b601c3b9a0ad7befe180ff2a2f3e2176abce9c7692cae` | 20,233 s | **9** | **9** | 1,0 s |
| `43056(2).mp4` (riferimento utente) | `9db1bbebce888b5cbd9e4fb3dc0a5a4fd13a74a3aeccb188912bdee29a8cfcba` | 20,967 s | **9** | **9** | 1,0 s |
| `LA_STORIA_RIVIVE_1900_GATTO_VERSIONE_CINEMA.mp4` (RIFIUTATO) | `16cb405a7b52f539f8134c05f36a903ac9efaaaf061eda437668c2445f3dadb1` | 24 s | **1** | **1** | 0,5 s (transizione riconosciuta a bassa soglia) |
| `LA_STORIA_RIVIVE_PARIGI_1918_V162_NEURAL_REVIEW_NON_FINALE.mp4` (REVIEW, NON FINALE) | `3bbdcaa05e7176c9b2906308f0ddf60c91ac7090631cd65e1c39abcfa2c9a8a0` | 17 s | **0** a questa soglia | **0** | n.d. |

I due riferimenti includono *endcard nere di circa 3,75 e 4,5 secondi*: **non copiarle**; negli episodi di questo progetto la durata finale va usata per mostrare restauro/colore/movimento. L'audit delle sole dominanti cromatiche non certifica che un'immagine sia I2I né che la scena sia storicamente autenticata; nel V162 cornici/titoli colorati confondono la classificazione complessiva. I video d'esempio **non devono essere integrati o caricati come asset delle nuove produzioni**.

## Ricetta registica corretta

- Contenuto **verticale** di circa 18–25 secondi: circa **8–9 micro-scene diverse** quando il materiale le giustifica; almeno 5 trasformazioni per il profilo `rapid_reveal`. Scene e soggetti realmente diversi, non nove zoom dello stesso animale.
- Ogni micro-scena circa **1,75–2,4 s**, con **vero movimento storico B/N** all'inizio (tipicamente 0,75–1,1 s). Il colore arriva preferibilmente entro il primo secondo di scena, partendo **dallo stesso frame/inquadratura**.
- Versione a colori **molto dettagliata, fotorealistica, vivida**, il più possibile coerente per inquadratura e soggetti; l'utente consente interpretazioni creative dei dettagli incerti, ma evitare persone/arti/facce aggiunti senza criterio o soggetto mutato. Trattare le ricostruzioni come interpretazioni IA, non colori originali.
- Tenere il colore in visione sufficiente per ammirarlo (tipicamente **0,75–1,3 s** nel profilo rapido). Evitare foto fisse per molti secondi, zoom continuo, pan laterale e falsa animazione 2,5D come sostituto del film storico.
- Se si usa Vidu, **movimento realmente generato** da un frame sorgente verificato con autorizzazioni esistenti; non dichiarare «Vidu» una foto che scorre o un video original-colorized DDColor. Nessuna spesa o pubblicazione implicita.
- Titolo luogo/anno minimo, audio/musica coerenti, nessun endcard promozionale. Conservare diritti Italia, storyboard, autenticità B/N e gate V91/V94/V96/V99. Questo profilo rapido **non sostituisce il benchmark V98**, è un criterio supplementare quando l'utente richiede l'effetto degli esempi.

## Gate tecnico V163

`src/storia_rivive_v163_rapid_reveal_qa.py` esamina i byte veri del MP4 tramite FFmpeg e OpenCV e produce un report **fail-closed** per: 14–35 s, almeno cinque B/N→colore, cinque diversi frame B/N, movimento B/N misurato, primo reveal ≤1,5 s, almeno 0,5 s di colore per ciclo, H.264 720×1280 + AAC e nessun endcard nero >1 s nel master. Si può usare `--mode reference` per stimare cadenza dei video d'esempio senza imporre il divieto di endcard a materiale non destinato alla pubblicazione. **Un PASS è solo ritmico/tecnico**: approvazione artistica, diritti italiani, vere I2I e Vidu richiedono riscontri separati.

Non allungare il provino del gatto per farlo apparire simile; sarebbe il medesimo errore.