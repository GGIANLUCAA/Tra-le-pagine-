# ArtVision Wright V85 — QA visivo V88, dieci segmenti del master reale (30/10/2026)

## Provenienza e confini

Questa verifica è stata eseguita su **byte reali**, non su un dossier: `WRIGHT_CINEMA_STANDARD_V52B_VERIFIED.mp4`, 6.690.474 byte, SHA256 `ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2`. Il master V52B rimane **immutato** e occupa lo stesso slot Cinema Standard Wright V85. Sono stati estratti dodici fotogrammi effettivi: t=0,5 s, i dieci punti mediani dei segmenti di montaggio e t=55,2 s; nessun frame è stato generato con IA. La scheda di contatto JPG (1360×2080) è stata generata nella sessione di QA, ma **non è un backup garantito sul repository o sul sito privato**.

## Riscontri visivi per segmento

| Segmento reale | Campione | Riscontro osservabile |
|---|---:|---|
| Apertura 0–5,417 s | 0,5 e 2,7 s | Il cartiglio scuro del titolo copre la zona centrale della composizione per quasi tutto il primo segmento. |
| 5,417–10,500 s | 8,0 s | Gruppo intorno alla pompa; la tela orizzontale è ritagliata in 9:16, con figure laterali parzialmente fuori campo. |
| 10,500–15,792 s | 13,1 s | Dettaglio del gruppo di destra: padre, ragazze, uccello. |
| 15,792–21,000 s | 18,4 s | Stesso gruppo di destra da inquadratura solo leggermente diversa: verificare se la seconda vista aggiunga informazione. |
| 21,000–26,208 s | 23,6 s | Gruppo di sinistra: due donne e uomo in rosso; un volto sul bordo sinistro è parzialmente tagliato. |
| 26,208–31,500 s | 28,9 s | Ancora gruppo di sinistra, composizione molto simile; possibile ripetizione percepita. |
| 31,500–36,708 s | 34,1 s | Ritorno a pompa e figura femminile illuminata, con spazio scuro inferiore significativo. |
| 36,708–41,917 s | 39,3 s | Zona destra più scura; personaggi laterali visibili ma in parte troncati dal formato verticale. |
| 41,917–47,208 s | 44,6 s | Ritorno al gruppo centrale della pompa, simile all'apertura senza cartiglio. |
| 47,208–55,792 s | 51,5 e 55,2 s | Dipinto intero piccolo al centro, sfondo quasi tutto nero per circa 8,6 s. |

Questa osservazione **non dimostra** che ogni crop sia sbagliato: un'inquadratura ravvicinata può tagliare intenzionalmente figure secondarie. Il problema da giudicare in V25 è se si perdano i soggetti citati o se l'occhio percepisca stanchezza. Non è stata certificata una visione/ascolto umano integrale.

## Conclusioni operative

1. **Ripetizione percettiva:** i segmenti 3/4 e 5/6 mostrano sostanzialmente gli stessi gruppi; segmenti 2/9 tornano a un soggetto molto simile. Non contare automaticamente dieci segmenti come dieci dettagli diversi. Rivedere la motivazione narrativa prima di modificare lo slot.
2. **Ritmo:** nove stacchi rilevati dal V87, intervallo interno medio 5,224 s, CV ~1,3%. Un ritmo quasi periodico va sottoposto a revisione artistica; non è un errore di codifica.
3. **Hook/outro:** accorciare e alleggerire il cartiglio, e progettare un finale che faccia leggere la tela anziché lasciarla piccola su nero. Queste sono **proposte**, non revisioni applicate.
4. **Confronto con regola V82:** i due Critico Wright V85 sono 216,5 s con copione di 486 parole, molto oltre il target orientativo V82 di 75–105 s e 160–220 parole. Non dichiararli automaticamente errati o riscriverli senza nuova autorizzazione: segnalare il rischio di pesantezza nella revisione V25 e applicare V82 ai prossimi nuovi Critico autorizzati.
5. **Separazione dei controlli:** V87 e questo storyboard sono advisory Cinema Standard; il gate Museum V57 non va applicato agli stacchi intenzionali. Un MP4 decodificabile, un WAV identico e un CRC valido **non** equivalgono ad approvazione V25.

**Stato invariato:** cinque opere autorizzate, 20 slot MP4 esistenti, 0 Gold V25 automatici. Nessuna nuova voce, render, spesa video IA, pubblicazione o upload Dropbox. Nessuna sesta opera avviata; `config/artvision_pilot_lock_v58.json` resta vincolante.
