# V321 · Audit della naturalezza tra episodi — cinque copioni REALI (10/11/2026)

## Perché
Il precedente V320 ferma cliché evidenti prima di una **nuova** voce Gacrux.
La ripetizione tra episodi, anche quando ogni testo singolarmente sembra valido,
può creare l'effetto di un copione AI sempre uguale. Questo report
usa cinque ricette realmente versionate, non trascrizioni immaginarie.

## Evidenze del test GitHub

Prima run QA reale (5 ricette, 5 renderer, 10 confronti di coppia):
https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42895954604

**Constatato nei sorgenti:**
- 5/5 ricette hanno **9 capitoli** ciascuna.
- 5/5 generatori dichiarano **DELAY=3.5 secondi** e **TAIL=6.0 secondi**.
  Non significa che questi valori siano *misurati* sui MP4 finali.
- Bruegel / The Fall of the Rebel Angels ha una chiusa stereotipata
  **“il quadro ci lascia una domanda”**, verificata dal gate V320.
- Altre chiuse risultano artisticamente da rivedere, senza divieto assoluto:
  - Simberg / The Garden of Death: “Ci invita a guardare la fragilità con rispetto.”
  - Bruegel / The Triumph of Death: “Vediamo anche quanto sia fragile ciò che chiamiamo vita.”
  - Waterhouse / The Magic Circle: “La sua forza nasce proprio da ciò che Waterhouse decide di non spiegare.”
  - Blake / The Ghost of a Flea: “Nel contrasto fra dimensioni minuscole e presenza monumentale sta gran parte della sua forza.”

Queste ultime sono **segnalazioni editoriali**: possono essere appropriate
per il singolo autore, ma quattro episodi di fila con finali astratti
possono diventare riconoscibilmente meccanici. Il controllo non misura
la bellezza, non legge l'audio né riconosce con certezza la scrittura AI.

## Intervento preferibile nei NUOVI video

1. Parti da una singola osservazione che si possa **mostrare**, non da una
   “grande domanda” inventata in anticipo.
2. Cambia il numero di capitoli solo in funzione dell'opera; 9 non è né
   vietato né obbligatorio. Mostra un beat diverso ogni volta che voce
   e quadro cambiano effettivamente soggetto.
3. Scrivi la chiusura per prima: deve contenere un elemento concreto di
   quella storia. Se fosse riutilizzabile in altri quattro video, riscrivila.
4. Varia durata di apertura e finale per necessità cinematografica;
   il TAIL a 6 secondi è una costante del renderer vecchio,
   **non** va rimosso automaticamente dai filmati già validati.
5. Rivedi a voce alta il copione, quindi ascolta il WAV e guarda il vero MP4.
   No dichiarazioni di qualità “umana” da solo linter.

## Cinque proposte di chiusura più concrete (non approvate)

Non sono trascrizioni o audio esistenti. Sono **proposte** ricavate dai
particolari GIÀ riportati nei copioni, da verificare sui veri fotogrammi
prima di adottarle. Non usarle tutte insieme come nuovo stampino.

- **The Fall of the Rebel Angels (Bruegel):**
  “Torniamo alla spada di Michele, proprio al centro. Da lì lo sguardo scende
  e incontra creature sempre più strane: becchi, gusci, ali, zampe.
  Anche dopo averlo osservato a lungo, in questo quadro rimane sempre qualche
  dettaglio da scoprire.”
- **The Garden of Death (Simberg):**
  “Alla fine restano quelle tre figure vestite di nero e le piante di cui
  si prendono cura. Un lavoro piccolo, quasi quotidiano, in un luogo
  dove non ti aspetteresti di trovarlo.”
- **The Triumph of Death (Bruegel):**
  “E nell'angolo in basso a destra, fra tutta quella gente in fuga,
  c'è ancora una coppia che fa musica. È un particolare minuscolo.
  Una volta visto, però, è difficile dimenticarlo.”
- **The Magic Circle (Waterhouse):**
  “La donna è ancora lì, intenta a tracciare il cerchio. Il fuoco illumina
  il terreno e gli uccelli si tengono vicino al fumo. Il quadro si ferma
  su questo gesto; quello che viene dopo non lo vediamo.”
- **The Ghost of a Flea (Blake):**
  “La figura sembra occupare uno spazio enorme. Poi ricordi che il pannello
  misura poco più di venti centimetri: il corpo, le mani e quella coppa
  sono tutti racchiusi lì dentro.”

Se una chiusa è simile alle precedenti o sposta la camera su qualcosa
che non è nell'inquadratura, respingerla. Nessuna revisione valida senza
coerenza immagine-parola (V82), controllo fonte e un nuovo WAV condiviso
fra Standard e Museum solo se esplicitamente autorizzato.

## Strumenti e limiti

Comando gratuito e locale:
    python src/editorial_series_naturalness_v321.py \
      --recipe modules/artvision_critico/production_series/bruegel_rebel_angels_v144.json \
      --recipe modules/artvision_critico/production_series/simberg_garden_v146.json \
      --out output/editorial-v321/REPORT.json

Per confronto completo di 5 episodi e 5 renderer vedere il workflow
.github/workflows/editorial-series-naturalness-v321.yml;
GitHub Actions conserva un artifact JSON leggibile da Android.
Lo strumento è offline e read-only, non ha chiavi API e non modifica
source, WAV, copertine, master, pubblicazione o programmazione.

**Nuova proposta di finale Bruegel:** proposals/artvision_bruegel_ending_v321_not_approved.json.
Prima di qualsiasi nuova TTS va controllata visivamente; nessun
auto-rewrite, nessuna rigenerazione gratuita “a caso”, nessun cambio
automatico di Critico Museum. Il video e il WAV attuali restano immutati.

Il report vale per ArtVision Critico con capitoli testuali. Per gli altri
formati, compresi La Storia Rivive senza voce e WOW LAB, V320 resta
vincolante ma serve un audit specifico di vere sequenze e montaggi,
non la falsa applicazione di un controllo sui copioni.
