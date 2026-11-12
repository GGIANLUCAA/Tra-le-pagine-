---
name: artvision-regia-umana
description: "Usa questa skill quando pianifichi o revisioni regia, storyboard, sincronizzazione voce-scene o ritmo di video ArtVision 4x1, La Storia Rivive, WOW LAB o Giuliano. Non usarla per dichiarare autonomamente approvato un video."
---

# ArtVision: regia umana, non uno stampino

## Leggi prima
1. `AGENTS.md`, `docs/REGOLE_ATTIVE.md` e `START_HERE_GPT.md` dal branch di lavoro.
2. `docs/REGIA_UMANA_SGUARDI_V1_20261111.md` (V322), `docs/REGOLA_GLOBALE_V320_NATURALEZZA_AUTORIALE_20261110.md` e, per Critico, V321.
3. Le regole del formato e della specifica opera prima di ogni proposta. Non sostituire le regole del progetto con linee guida generiche di Remotion o Skills.sh.

## Metodo
- Scrivi la promessa narrativa in una frase concreta: cosa vedrà e capirà lo spettatore che non sapeva prima?
- Per ogni sequenza annota: ID fonte, diritto/licenza e autore, istante/ritaglio esatto, gesto o dettaglio visibile, parola/cue o motivo del silenzio, movimento di macchina motivato, durata *proposta*, raccordo con scena precedente e seguente.
- Progetta inizio e fine specifici: niente domanda morale di routine, musica o zoom ripetuti. Non applicare una durata fissa a tutti i tagli.
- Prediligi filmati autentici e dettagli verificabili; l'AI non può inventare volti, persone, oggetti o dipinti e presentarli come documentazione.
- Se la fonte, la licenza o il materiale mancano, scrivi `BLOCKED_SOURCE` e passa a un candidato indipendente. Non creare una falsa sorgente.
- Confronta l'episodio con i più recenti per rilevare tic di voce, ritmo e chiusure; i rilievi automatici sono indizi, non voti artistici.

## Vincoli per formato
- ArtVision 4x1: quattro varianti, la stessa voce autentica per i due Critico; dettagli pittorici coerenti con la narrazione. Nelle versioni Museum rispetta V80/V118/V119, cornice documentata e scala fisica reale, stessa sala in entrata e uscita. Nessuna nuova approvazione Museum senza visione completa del provino.
- La Storia Rivive: le regole V91/V94/V96/V99 e V323 hanno precedenza. Se si promette B/N -> colore, verificare il colore nei veri fotogrammi MP4: i flag del prompt non sono prove. Nessuna falsificazione della fonte o del movimento.
- Giuliano/documentari/WOW LAB: distinguere fonti autentiche, ricostruzioni ed effetti; storyboard con montaggio semantico e tempi adattati al materiale.

## Prima di dire “finito”
- Guardare tutto il vero MP4 con audio, senza audio, e ascoltare l'audio isolato; correlare parole, scene, fonte e movimento.
- Usare `artvision-video-evidence` per la parte tecnica, fonte, consegna e controlli specifici.
- Se la visione reale non è disponibile: `rendered_needs_review` oppure `unverified`, mai Gold/master approvato.
- Non alterare master già validati. Non pubblicare su sito/social; non generare costi API, nuovi crediti Vidu o acquisti senza verifica e autorizzazione specifica.

## Esito richiesto
Restituisci una tabella breve con `timecode | frase/cue | sorgente | funzione narrativa | rischio | prova`, e un verdetto separato **tecnico** / **artistico** / **diritti** / **pubblicazione**. Non inventare valori o revisioni completate.
