# ArtVision — Modulo "AI REGISTA" (l'AI decide la regia dal quadro)

Obiettivo: dato un quadro, l'AI **analizza l'immagine** e **assegna automaticamente** la regia migliore
(formato, durata, ritmo, n° scene, musica, accento, zoom, hook).
Output finale: la **Scheda Video già compilata** (§6) → pronta per la produzione.
Vincoli fissi: titolo in inglese · post in italiano naturale · **nessun nome/logo/watermark nel video**.

---

## 1) COSA L'AI OSSERVA NEL QUADRO (i 7 segnali)

| # | Segnale | Come si rileva |
|---|---|---|
| 1 | **Soggetto** | mito / storia / religione / ritratto / paesaggio / natura morta |
| 2 | **N° figure** | 1 sola / poche (2–4) / folla (5+) |
| 3 | **Densità di dettagli** | minimal (pochi elementi) / media / ricchissima |
| 4 | **Mood** | cupo-drammatico / malinconico / epico / sereno / misterioso |
| 5 | **Luminosità** | scuro / bilanciato / luminoso |
| 6 | **Dettaglio nascosto** | presenza di elementi che "non si vedono a prima vista" |
| 7 | **Notorietà dell'opera** | famosissima / nota / rara |

(Facoltativo) **8. Dimensione dell'opera** del pittore → quante opere note ha → decide se è possibile una **carrellata**.

---

## 2) TABELLA DI DECISIONE (segnale → regia)

| Segnale rilevato | Formato | Ritmo | Zoom | Musica | Accento |
|---|---|---|---|---|---|
| Folla + drammatico (5+) | **A2 Capolavoro** | medio | lunghezza d'insieme poi dettagli | epica/tensa | rosso scuro |
| 1 figura + minimal | **A3 Mistero** o **A1** | lento | trattenuta lunga sul volto | malinconica | ambra |
| Presenza dettaglio nascosto | **A1 Segreto** | medio | zoom forte sul dettaglio | tesa | arancio |
| Tema con enigma/furto/falso | **A3 Mistero** | medio | ping-pong fra indizi | tensa | rosso scuro |
| Opera famosissima | **A1 Segreto** (sorprendi) | medio | zoom su dettaglio poco noto | tesa | arancio |
| Opera rara/ignota | **A2 Capolavoro** (curiosità) | lento | panoramica ampia | serena/malinc. | ambra |
| Pittore con molte opere note | **B1 Chi era** | vario | 1 movimento per quadro | epica/malinc. | ambra |
| Pittore con stile che cambia molto | **B2 Evoluzione** | vario | cronologico | serena→epica | ambra |
| Pittore molto visivo/rapido | **B3 5 quadri in 30s** | veloce | tagli ritmici | vivace | arancio |

---

## 3) COME L'AI CALCOLA LA DURATA (formula semplice)

**Formato A — Opera singola**
```
durata = 35s (base)
       + 5s se folla (5+ figure)
       + 5s se densità d'insieme "ricchissima"
       + 5s se c'è un dettaglio nascosto da rivelare
       + 5s se è una carrellata interna (più sottotrame)
limite massimo: 60s
```

**Formato B — Carrellata**
```
durata = 6s × numero_quadri (5–8)
→ 5 quadri = 30s | 6 = 36s | 7 = 42s | 8 = 48s
```
Regola: **mai oltre 60s** (calo di attenzione). Sotto i **30s** solo per il tipo B3.

---

## 4) LA REGIA CAMERA (dove punta l'occhio) — decisa dall'AI
- **Focal point**: volti, mani, fonte di luce, dettaglio anomalo.
- **Apertura**: inquadratura d'insieme (contesto) 2–3s.
- **Zoom**: 1 zoom sul focal point; se folla → 2–3 zoom su figure diverse.
- **Mai statico**: sempre Ken Burns o zoom lento.
- **Chiusura**: allontanamento finale (zoom-out) → stacco netto (prepara il loop).

---

## 5) HOOK — come sceglierlo
- Opera **famosissima** → hook di **rivelazione** ("Nessuno nota questo…")
- Opera **ignota** → hook di **domanda** ("Chi è questa donna?")
- Presenza **dettaglio nascosto** → hook **segreto**
- Tema **enigma/furto** → hook **mistero**
- Pittore → hook **domanda su di lui** ("Dipinse la stessa donna per 30 anni. Ma non era una donna.")

---

## 6) OUTPUT: LA SCHEDA COMPILATA (contract per il sistema di regia)
L'AI deve restituire **esattamente** questi campi, compilati:

```
SCHEDA VIDEO — compilata dall'AI Regista
-----------------------------------------
Opera:                 titolo + autore + anno + museo
Licenza:               PD | CC0  (fonte verificata: SÌ/NO)
Segnali rilevati:      soggetto, n°figure, densità, mood, luce, dettaglio nascosto, notorietà
Formato assegnato:     A1 | A2 | A3 | B1 | B2 | B3 | B4
Durata:                __ s   (con la formula §3)
Titolo a schermo (EN): ____________
Hook (0–3s):           ____________
Ritmo:                 lento | medio | veloce
Scene (elenco):        1) ...  2) ...  3) ...
Zoom / focal point:    ____________
Musica (mood):         ____________
Accento colore:        arancio | ambra | rosso scuro
Chiusura:              domanda / frase-firma
Post (IT):             ____________
Hashtag (2–4):         ____________
Credito finale:        autore, titolo, anno, museo
-----------------------------------------
```

---

## 7) IL PROMPT "AI REGISTA" (pronto all'uso)
Da dare a un'IA **con vista** (vision) allegando l'immagine del quadro, oppure con la descrizione testuale.

> **PROMPT:**
> Sei un direttore creativo di short verticali per il canale ArtVision (arte e opere d'arte), pubblico italiano.
> Analizza l'opera allegata e compila la SCHEDA VIDEO secondo queste regole:
> 1) Rileva i segnali: soggetto, numero di figure, densità di dettagli, mood, luminosità, presenza di dettagli nascosti, notorietà.
> 2) Assegna il formato con la tabella di decisione (A1 Segreto / A2 Capolavoro / A3 Mistero / B1–B4 Carrellata).
> 3) Calcola la durata con la formula indicata (mai oltre 60s).
> 4) Scegli ritmo, zoom, musica e accento colore in base al mood.
> 5) Scrivi un hook nei primi 3 secondi e una chiusura con domanda.
> 6) Titolo a schermo SEMPRE in inglese. Post SEMPRE in italiano naturale (nessun linguaggio tecnico).
> 7) NON inserire MAI il nome del canale, loghi o watermark.
> 8) Inserisci il credito: autore, titolo, anno, museo.
> 9) Restituisci SOLO la scheda compilata, nel formato indicato.

---

## 8) ESEMPIO CHE DIMOSTRA CHE L'AI "CAPISCE" DAL QUADRO
Stesso sistema, **due quadri diversi → due regie opposte**:

| | **The Last Day of Pompeii** (Bryullov) | **The Blind Girl** (Millais) |
|---|---|---|
| Segnali AI | folla + drammatico + ricchissimo | 1–2 figure + minimal + sereno/malinconico |
| Formato | **A2 Capolavoro** | **A3 Mistero / A1** |
| Durata | 35 +5(folla) +5(densità) = **45–50s** | **40s** |
| Ritmo | medio | lento |
| Zoom | d'insieme → 2–3 dettagli | lunga trattenuta sul volto + arcobaleno |
| Musica | epica/tensa | malinconica |
| Accento | rosso scuro | ambra |
| Hook | "Ogni volto qui ha una storia." | "Il cielo le dice una cosa che lei non può vedere." |

> Questo è il punto: **l'AI non usa una regia fissa, la costruisce dal quadro.**

---

## 9) COLLEGAMENTO ALL'AUTOMAZIONE
```
1. Archivio opere (CC0/PD)  →  2. AI Regista (legge il quadro → compila la scheda)
        ↓                                   ↓
3. Sistema di regia (usa la scheda: durata, scene, zoom, musica)
        ↓
4. Render 9:16 senza brand  →  5. n8n pubblica 12:00 / 20:00
```
Obiettivo finale: tu approvi solo la scheda; il resto è automatico.
