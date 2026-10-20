# TRA LE PAGINE — REGOLA EDITORIALE V12
## Regole permanenti per tutti i prossimi video

Approvate dall'utente il 20 ottobre 2026 a seguito della revisione del video *Delitto e castigo*.

### 1. MAI PIÙ SOTTOTITOLI
**Nessun testo che trascriva il parlato in sovrimpressione nei futuri MP4.**
- No sottotitoli impressi (burn-in), file ASS/SRT generati, tracce sottotitoli o caption automatiche.
- Narrazione audio italiana con voce Google già scelta, immagini coerenti e musica calibrata.
- Test del motore V12: usa FFmpeg senza `ass=` e con `-sn`, cancella eventuali SRT/ASS residui. `episode_v3.py` blocca i video che contengono tracce o file sottotitoli.
- Il precedente `src/render.py` con sottotitoli è conservato **esclusivamente come backup storico** in `legacy_backup/render_con_sottotitoli_v11.py`, non viene più richiamato per produrre nuovi video.
- **Attenzione:** titoli di copertina o scritte che fanno parte di un dipinto non sono trascrizioni del parlato; non aggiungere comunque parole decorative non necessarie nei fotogrammi.

### 2. PRIMA I FATTI DELLA STORIA, POI LA RIFLESSIONE
Per ogni libro:
1. Chi è il protagonista, dove vive e in quale situazione si trova.
2. Qual è il problema, il desiderio o il conflitto.
3. Che cosa succede davvero nel romanzo, nel giusto ordine.
4. Quali scelte compie il protagonista e con quali conseguenze.
5. In che modo finisce la vicenda (spoiler solo se il format è un riassunto integrale).
6. Una **sola breve riflessione conclusiva**, dopo che la vicenda è stata spiegata.

**Evita:** monologhi filosofici ripetitivi, formule sensazionalistiche, descrizioni vaghe,
passaggi chiave saltati, personaggi presentati senza identificarli, eventi inventati.
**Preferisci:** stile narrativo vivo e umano, frasi semplici ma evocative, un chiaro filo
causa-effetto, 2–4 minuti in media, 300–500 parole quando compatibile con la lettura.

### 3. UNA SCENA DEVE MOSTRARE QUELLO CHE LA VOCE DICE
Per ogni immagine, chiediti:
- Che cosa sta raccontando **esattamente in quel momento** la voce?
- L'immagine mostra davvero il personaggio o l'azione, anziché un quadro generico?
- Epoca, luogo, vestiti, atmosfera e personaggi sono coerenti?
- Se è un'opera letteraria, esistono illustrazioni realizzate per **quell'opera**?
- È correttamente presentata come illustrazione, non come fotografia reale di fatti inventati?

**Non scegliere la prima foto trovata per keyword.** Cerca prima gli asset specifici
dell'opera, quindi materiale d'epoca pertinente. Meglio riutilizzare una buona immagine
con un'inquadratura alternativa piuttosto che inserire un volto o una città senza senso.
Se nessun materiale adeguato è disponibile, segnala il blocco prima di consumare TTS.

### 4. CHECK DELLE SCENE
`src/regia_narrativa_v12.py` crea, per ogni episodio nuovo:
- `REGIA_NARRATIVA_V12.json`
- `REGIA_NARRATIVA_V12.txt`

Per ciascuna scena mette **il brano completo della voce** accanto alla descrizione
dell'immagine e alla fonte. Se esiste un `narration_anchor`, lo controlla come
**frase esatta** del copione al cue point. Se la frase non coincide o le scene sono
disordinate, **blocca la produzione**.

Il controllo automatico **NON può garantire da solo** che una foto corrisponda
visivamente alla narrazione; il report porta `NEEDS_VISUAL_REVIEW`. Per un nuovo
libro importante è prevista verifica dello storyboard per scene e correzione
delle immagini fuori tema prima del render finale. Non fingere un esame semantico
completato automaticamente.

### 5. COSA NON MODIFICARE
- Lascia **Delitto e castigo** già consegnato senza rigenerarlo.
- Non sovrascrivere `Tra le Pagine` V3–V11, i vecchi episodi o la voce Google Gemini.
- Mantieni i moduli di backup quando aggiorni il sistema.
- La regola vale per tutti i video futuri, indipendentemente dal formato, libro,
fiaba, racconto e Controluce, salvo una nuova richiesta esplicita dell'utente.

### 6. COLLAUDI
- `tests/test_no_subtitles_v12.py`: mux FFmpeg reale per verificare video+audio, zero sottotitoli.
- `tests/test_regia_narrativa_v12.py`: scena ↔ frase narrata, cue order, errori.
- `tests/test_studio_autopilot_v11.py`: copione con scene ancorate a frasi esatte.
- `.github/workflows/regole-v12-check.yml`: esegue tutto senza chiamate Google.

Il risultato migliore resta un **filmato che racconta bene il libro e che mostra scene
riconoscibili**, non uno pieno di effetti e immagini senza collegamento.
