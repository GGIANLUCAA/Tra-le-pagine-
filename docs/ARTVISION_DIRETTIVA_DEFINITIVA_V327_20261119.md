# ARTVISION — DIRETTIVA DEFINITIVA (V327)
## Regia umana, realismo cinematografico, creatività autonoma

**19 novembre 2026 · direttiva-quadro dell'owner · ADDITIVA e consolidante, NON sostitutiva.**
Questa direttiva non crea un sistema parallelo: raccoglie in un unico principio-guida le regole già attive e dice all'agente quale comportamento tenere quando può scegliere. In caso di conflitto, vincono sempre le precedenze del §0.3.

---

## 0. Come questa direttiva si innesta nelle regole esistenti

### 0.1 Cosa consolida (regole già attive)
| Tema della direttiva | Regola già attiva di riferimento |
|---|---|
| Naturalezza autoriale, anti-stampino, niente finale filosofico | **V320** + gate `src/editorial_human_naturalness_v1.py` |
| Regia umana, tagli semantici, controcampo, QA artistico | **Regia Umana / Sguardi V1** (11 nov) |
| Ritmo non meccanico, campi recitativi, lingua visiva | **V326** + `src/director_reference_v326.py`; **Regia Cinematografica V23** + `config/cinematic_techniques_v23.json` |
| Durata non standardizzata, copertine, crediti, post distinti | **Creative Director V21**; **Editorial Post Standard V28** |
| Musica scelta per emozione, un solo brano, ducking | **MUSIC_POLICY_V20** + `config/music_policy_v20.json` |
| Museum: cornice autentica, scala reale, sala credibile, no cropped | **V80 / V82 / V118 / V119** |
| La Storia Rivive: restauro reale, 4+1, identità dei soggetti | contratti e gate **V91 / V94 / V96 / V99 / V323** |
| Quadro unico opaco, no ghosting/crossfade | **V23** (regola visiva fissa) |
| Nessuna spesa non autorizzata, master inviolabili | **Contratto permanente V25 / Contratto Madre 4×1 V58** |

### 0.2 Principio guida unico
> **Meno rigidità nelle SCELTE creative. Nessun compromesso nelle VERIFICHE.**
La libertà riguarda *cosa* e *come* raccontare. La disciplina riguarda fonti, diritti, sincronia, integrità dei file e rispetto delle identità. "Meno rigido" non significa mai "meno controllato".

### 0.3 Precedenze invariabili (non negoziabili)
Diritti e licenze → correttezza storica e fedeltà del soggetto → sicurezza → formato (4×1, V6, Critico V2) → V80/V82/V118/V119 → V91/V94/V96/V99 → nessuna spesa non autorizzata → tutela dei master/Gold → nessuna pubblicazione automatica senza autorizzazione. La creatività opera **dentro** questi vincoli, mai contro di essi.

---

## 1. Libertà creativa

1. Nessuna formula imposta: niente struttura obbligata hook → sviluppo → climax → CTA, niente durata fissa di scena, niente numero prestabilito di tagli o transizioni.
2. Una scena può durare pochi secondi o molto di più: decide il contenuto.
3. Il "regista virtuale" ragiona e interpreta, non esegue una ricetta. V23 propone al massimo 3–8 tecniche compatibili e **una camera ferma è spesso la prima scelta**; la scelta può cambiare a ogni opera, anche per lo stesso autore.
4. Prima di girare: definire in una frase l'idea unica, la scoperta umana e la relazione tra primo e ultimo fotogramma. Se questa frase non esiste, il video non è pronto.

## 2. Realismo e autenticità

1. Materiali originali e documentati: fotografie autentiche, filmati storici reali, opere identificabili con inventario/scheda museale.
2. Ricostruzioni AI solo quando giustificate e **dichiarate come tali**; mai attribuite alla ripresa originale; mai una falsa sala spacciata per documentaria (V23).
3. Persone, volti, movimenti, luce e ambienti devono risultare credibili: evitare l'effetto "video generato in serie".
4. Nessun dettaglio storico inventato presentato come documentato. Se un fatto non regge, si cambia frase o inquadratura, non lo si abbellisce.
5. Vietato il ghosting: una sola immagine nitida e opaca alla volta (V23).

## 3. Regia cinematografica umana

Ispirazione: documentario d'autore, cinema, produzione culturale professionale. In pratica:
- **Montaggio naturale, non meccanico**: tagli quando cambia gesto, significato o bisogno percettivo, non ogni N secondi.
- **Inquadrature motivate dal racconto**; movimenti di camera credibili; una sola direzione per movimento, partenza/arrivo morbidi.
- **Alternanza equilibrata** di dettagli e scene ampie; dopo un dettaglio, l'occhio deve trovare facilmente il successivo (eye-trace).
- **Pause con valore narrativo**; il valore 0–1% di zoom nel Critico è una partenza prudente, non una legge universale; il piano può restare del tutto immobile.
- **Musica ed effetti discreti**: la musica accompagna, non guida artificialmente ogni taglio; niente boom/drone da trailer a ogni video (V320, MUSIC_POLICY_V20).
- **Non rendere spettacolare ogni secondo.** Un'immagine autentica lasciata respirare vale più di dieci effetti.

## 4. Narrazione e immagini

1. Voce naturale, espressiva, professionale, mai robotica (Google Gacrux dove previsto), vocabolario concreto e punteggiatura ascoltabile.
2. **Sincronia reale, non stimata**: ogni dettaglio nominato deve trovarsi a schermo *esattamente* nel momento in cui viene descritto, con tempi ricavati dal vero WAV (V82; campi `spoken_anchor`/`visual_anchor` di V326).
3. Niente scene casuali per riempire; niente frasi sensazionalistiche obbligatorie; niente finale filosofico prefabbricato (V320).
4. La narrazione trattiene con la **qualità della storia**, non con slogan.
5. Per i video senza voce, la "voce autoriale" è il montaggio: gli spostamenti seguono il moto reale della fonte e il gesto musicale.

## 5. Stile adattivo (un formato non è l'altro)

- **Critico d'arte**: interpretazione intelligente, attenzione all'opera, dettagli pittorici pertinenti, racconto coinvolgente. Standard e Museum condividono **stesso copione e stessa traccia vocale**.
- **Museum Cinema**: sala credibile, proporzioni e cornici autentiche, atmosfera cinematografica, ingresso/uscita camera continui; cornice fuori dai dettagli; nessun ingrandimento sfocato della sala.
- **La Storia Rivive**: materiali storici autentici, restauro **realmente misurato** (non tingere un monocromo e chiamarlo colorizzazione), identità dei soggetti, 4+1.
- **Documentari**: ricerca approfondita, immagini significative, fatti verificati, regia naturale.
- Nessuno stile va trasferito automaticamente da un formato all'altro.

## 6. Autonomia e miglioramento

1. Prima di produrre: capire il soggetto e scegliere l'approccio narrativo più efficace.
2. Durante: valutare criticamente le scelte; un PASS automatico non è un'approvazione editoriale.
3. A lavoro concluso: verificare qualità audiovisiva, credibilità, sincronizzazione, correttezza delle fonti, integrità del file. Applicare le **cinque domande di V320** (finale sostituibile? un documentarista lo direbbe? si vede ciò che si nomina? si scopre qualcosa? ci sono tic ripetuti rispetto agli ultimi episodi?).
4. Imparare dagli errori **senza** trasformare ogni correzione in una nuova regola rigida: registrare la lezione nella ricetta/brief, non creare formalismi.
5. Blocco: tentare **al massimo due alternative ragionevoli**, poi mettere in pausa l'opera e passare alla successiva, registrando il blocco. Non fermare l'intera produzione per una sola opera.
6. Mantenere i controlli indispensabili: licenze, fonti, sicurezza.

## 7. Consegna completa

1. L'obiettivo è produrre **contenuti finiti**, non solo idee, script o anteprime.
2. Quando gli strumenti lo consentono: video, copertina, testo social (quattro descrizioni distinte, V28), crediti e file scaricabili.
3. **Non dichiarare "finito"** un video se manca il file finale o non supera i controlli essenziali. Senza approvazione artistica lo stato è `rendered_needs_review`, mai Gold/publish.
4. La pubblicazione può essere automatica **solo** quando il sistema è configurato e autorizzato.

### 7.1 Social-first (regola vincolante per ogni formato)

Tutti i video ArtVision sono concepiti e realizzati per la fruizione social: piattaforma, schermo mobile, anteprima, copertina, apertura, ritmo, testo e condivisione si considerano **fin dall'idea iniziale**, non come adattamento finale. L'obiettivo è massimizzare la probabilità di attenzione, visione completa, replay, condivisione e ritorno del pubblico, senza promettere risultati che solo gli analytics possono dimostrare.

- **Confezione visiva coerente, non seriale.** Ogni serie mantiene una grammatica riconoscibile (gerarchia, tipografia, contrasto e collocazione dei testi); ogni copertina resta specifica dell'opera e sceglie un'immagine/dettaglio autentico e una promessa editoriale breve. Coerenza non significa ripetere meccanicamente la stessa composizione.
- **Copertina progettata per la miniatura.** Deve essere leggibile su smartphone, distinguersi nel feed e incuriosire senza coprire o falsare l'opera. Evitare titoli lunghi, microtesti, elementi decorativi gratuiti e duplicazione automatica del titolo dell'opera.
- **Apertura che mantiene la promessa.** I primi secondi devono offrire subito un'immagine significativa e una ragione autentica per restare. La forma può essere una domanda, un gesto, un contrasto, un dettaglio o una scena: nessun hook è obbligatorio e nessuna suspense può dipendere da fatti inventati o rivelazioni trattenute artificialmente.
- **Montaggio per attenzione e comprensione.** Eliminare tempi morti non intenzionali; variare scala e ritmo quando aiuta a vedere o capire; mantenere naturalezza, fedeltà dell'opera e sincronia. Non aggiungere movimento, tagli o effetti solo per aumentare la frequenza degli stimoli.
- **Adattamento nativo.** Formato, area sicura, sottotitoli, copertina, titolo, descrizione e crediti si preparano per la destinazione prevista, rispettando le regole tecniche e di diritti della piattaforma. I quattro testi V28 devono essere realmente distinti e adatti ai rispettivi canali.
- **Chiusura essenziale.** Il video termina sul contenuto; un'eventuale CTA è breve, pertinente e non sostituisce la conclusione narrativa. Niente coda promozionale lunga.
- **Ottimizzazione verificabile.** Quando sono disponibili dati reali, confrontare copertine e aperture tramite test controllati e metriche pertinenti (per esempio visualizzazioni, tempo medio, completamento, replay, condivisioni e nuovi follower). Registrare periodo, piattaforma e campione; non attribuire causalità a un singolo risultato e non dichiarare virale un contenuto senza evidenza.
- **Limiti inderogabili.** Nessun clickbait, immagine ingannevole o promessa non mantenuta; nessun compromesso su fonti, diritti, accuratezza, sicurezza, accessibilità e integrità dell'opera. Le precedenze del §0.3 restano superiori all'ottimizzazione delle visualizzazioni.

---

## 8. Gate non delegabili prima di dichiarare un MP4 concluso
1. Guardare l'MP4 vero **con audio**, **muto**, e ascoltare **solo audio**; campionare i fotogrammi a 0/1/3/5/7 s e su almeno tre raccordi.
2. Verificare gesto–frase–campo–tempo parola per parola (narrati); nessun ghosting ai raccordi.
3. Confronto con gli **ultimi 3–5 episodi** dello stesso formato: apertura, sviluppo, volume emotivo, chiusura.
4. QA tecnica: codec H.264 + AAC, durata, hash, file leggibile, copertina, ZIP Android, stato reale.
5. Fonti, licenze, crediti, diritti per la destinazione d'uso effettiva.
6. Se manca la voce approvata (es. `GEMINI_API_KEY` assente) → il Critico **non è concluso**; non fingere narrazione né usare fallback robotici.

---

## 9. Come la migliorerei (raccomandazioni)

Questa sezione non è ancora regola: sono proposte da valutare. In ordine di impatto.

1. **Un solo "documento-sommità" che dice chi vince.** Il repo ha oltre 200 documenti di regole; il rischio vero non è la poca creatività, è che un agente non sappia *quale* file conta. Terrei questa V327 come indice-autorevole: elenca, per ciascun tema, **la versione valida** e segna le altre come storiche. Così "sempre senza errori" diventa verificabile.

2. **Trasformare i principi in gate eseguibili, non solo in prosa.** Esistono già `editorial_human_naturalness_v1.py` (testo) e `director_reference_v326.py` (storyboard/coda nera). Farei in modo che i renderer *dell'owner* li invochino prima di ogni TTS/render (oggi non tutti lo fanno). Una regola non applicata dal percorso automatico resta un'intenzione.

3. **Un controllo di varietà tra episodi (il vero antidoto allo "stampino").** Una piccola verifica offline che confronta gli ultimi 3–5 lavori su tratti pianificati — tipo di apertura, modo camera, distribuzione delle durate, tipo di battuta finale — e segnala se sono troppo simili. Non un punteggio di bellezza: solo un allarme "questo episodio assomiglia troppo al precedente". È il modo concreto per garantire contenuti *sempre belli e diversi*.

4. **Una rubrica di gusto piccola e onesta, loggata per episodio.** Le cinque domande di V320 applicate e registrate, più un confronto obbligatorio con un paio di **riferimenti-oro** (il video 9,2/10 dell'owner, i Gold Master). Niente KPI inventati: la bellezza si giudica guardando, non sommando metriche.

5. **Un unico lessico vietato condiviso** tra copione e didascalie (unione di V320 §5 e V28). Oggi sono in due documenti; unendoli si evita che una formula bandita nei post passi nella voce o viceversa.

6. **Codificare il "budget di tentativi".** Massimo 2 alternative, poi pausa e registrazione del blocco (oggi è una linea guida; renderla un campo dello stato lo rende attuabile).

7. **Curare la coda: niente finale promozionale lungo.** I riferimenti dell'owner lo indicano come punto debole ricorrente. Fissare l'aspettativa: il contenuto finisce sul contenuto; la CTA, se c'è, è breve e sobria.

8. **Chiarire "bello" ≠ "spettacolare".** Il rischio della direttiva "contenuti molto belli" è scivolare nell'estetica da spot. Aggiungerei esplicitamente che la bellezza va **guadagnata dalla fonte**: un'immagine autentica che respira batte dieci effetti.

9. **Distinguere sempre "regola" da "proposta".** In un sistema così ricco, marcare visivamente ciò che è vincolante e ciò che è solo un'idea evita che un suggerimento diventi un obbligo rigido — cioè proprio il difetto che la direttiva vuole eliminare.

10. **Misurazione onesta.** Nessuna affermazione di viralità o retention senza analytics reali; le soglie di V326 sono euristiche, non prove psicologiche. Mantenere questa umiltà è ciò che rende credibile tutto il resto.

---

## 10. Principio fondamentale
> Meno rigidità. Più intelligenza creativa.
> Meno effetto AI. Più autenticità umana.
> Meno produzione standardizzata. Più cinema, emozione e realtà.

ArtVision non è una catena di montaggio: è uno studio che impara, sperimenta e racconta **ogni soggetto nel modo che merita** — con la libertà creativa come centro e la qualità tecnica come requisito essenziale.

*Questa direttiva guida tutte le future produzioni ArtVision, entro le precedenze del §0.3 e senza modificare retroattivamente master, Gold o lavori già approvati.*
