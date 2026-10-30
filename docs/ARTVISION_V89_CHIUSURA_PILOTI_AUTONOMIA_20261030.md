# ArtVision V89 — chiudere i piloti prima di espandere (decisione 30/10/2026)

## Decisione più recente del proprietario
Nella conversazione del 30/10/2026, dopo due giorni di test, il proprietario chiede esplicitamente di **concludere i test e ottenere una catena realmente autonoma**, senza dover riaprire la chat e senza perdere regole, dati, versioni o lavori già realizzati. Ha approvato l'ordine: **completare le 4 varianti di The Death of Socrates**, eseguire end-to-end un secondo pilota **The Kiss** (già renderizzato), **poi** giudicare pronta la serie. Questa decisione di priorità V89 prevale sui vecchi inviti a iniziare un nuovo soggetto. Mantiene validi gli asset e le autorizzazioni storiche delle cinque opere.

## Stato documentato al momento della decisione
- Socrate, Klimt, Hokusai, Bosch, Wright: **20 slot (4 per opera) con MP4 già registrati come renderizzati o riutilizzati** in `queue/artvision_four_variants_s01_20261028.json`. **0 approvazioni artistiche Gold/V25** e non tutti i download/backup/playback su archivio privato verificati.
- La fine del render NON prova archiviazione duratura: path `/mnt/data` di sessioni ChatGPT e gli artifact temporanei GitHub Actions possono non essere recuperabili. SHA, manifest, commit e copertine NON sostituiscono il backup dei veri MP4.
- Il controllo V87 ha evidenziato montaggio regolare/monotono e finale a nero eccessivo del Wright Cinema Standard; PR #146 / V88 documenta ripetizioni visive e critici Wright troppo lunghi. Correzioni non distruttive, solo nuove revisioni dello stesso slot, mai sovrascrivere l'unica copia di un master.

## Ordine operativo rigoroso
1. **Socrate 4×1:** recuperare i quattro MP4 originali, WAV e ZIP da fonti realmente accessibili. Verificare byte e SHA256 vs scheda V67 e coda, ffprobe e decodifica integrale, audio condiviso BIT-A-BIT nei due Critico, copertine e 16 testi social. Eseguire QA temporale della corrispondenza voce/dettaglio e verificare visibilità di teste/mano e cornice. Se mancano i byte, dichiarare l'esatto blocco; non ricreare una variante solo perché non è scaricabile.
2. **Consegna e conservazione Socrate:** utilizzare solo una destinazione d'archivio privato consentita, caricare i veri byte, effettuare download di ritorno e confronto SHA/CRC, verificare player su Android e ZIP completo. Registro separato `render`, `QA tecnica`, `QA artistica`, `backup remoto verificato`, `player verificato`, `V25 proprietario`. Non chiamare `consegnato` un manifest o un link non controllato. Nessuna pubblicazione social.
3. **Klimt 4×1:** ripetere lo stesso protocollo SENZA rigenerare quanto già fatto. Il pacchetto completo su Dropbox già autorizzato può essere recuperato e verificato; la sola presenza di metadata/URL non prova un download e hash di ritorno.
4. Solo dopo **due cicli end-to-end realmente attestati**, preparare il riavvio controllato della serie. Non iniziare una sesta opera né aggiungere varianti/automazioni concorrenti; una sola automazione owner, massimo un render simultaneo.
5. Se esiste un blocco, lavorare direttamente sul primo punto risolvibile e registrare evidenze testate e il successivo passo. Evitare iterazioni di sola documentazione e report identici senza progresso.

## Regia e feedback permanenti
- Quattro film distinti: due Critico con **lo stesso audio Gacrux**, due Cinema senza voce; apertura d'impatto 3–7s; niente effetto slideshow ripetitivo.
- Durate e tempi motivati: Critico più conciso e professionale (nuovi film indicativamente 75–105s quando registicamente adeguato), meno commenti personali; il metraggio finale si sceglie su voce e scene, mai taglio brutale dell'audio esistente.
- Se la voce nomina un dettaglio, quel dettaglio deve essere pienamente visibile, centrato e abbastanza a lungo: niente volti amputati, continui zoom sugli stessi particolari o scene slegate.
- Museum: la vera cornice verificata, della specifica opera, all'inizio e al ritorno finale soltanto; durante l'ingresso e la spiegazione sparisce naturalmente fuori campo. Scala fisica e attribuzione della sala sempre fedeli o correttamente dichiarate ricostruzioni; zero cornici fittizie presentate come autentiche.
- Distinguere controlli algoritmici, revisione umana completa e approvazione dell'utente. Non attribuire automaticamente V25 solo perché il file si decodifica.

## Uso servizi esistenti: chiarimento autorizzato
Il proprietario **autorizza l'uso autonomo di Vidu nell'ambito del proprio abbonamento attivo**, già usato in altri video del progetto, **non** l'acquisto di un secondo piano o l'addebito aggiuntivo di API/crediti. Prima di ogni generazione accertare con dati reali se la chiamata prevista è effettivamente inclusa nel piano o consuma **saldo già acquistato e disponibile**; registrare quota, natura della chiamata e consumo. Se piano/API sono distinti o il costo non è verificabile, non addebitare e proseguire con render riutilizzabile o altra attività gratuita. Non cancellare o alterare i limiti Vidu di altri format. Per la voce Google continuare a riutilizzare WAV autentici e non presentare come gratuite chiamate dal costo sconosciuto.

## Memoria e integrità
Precedenza a `AGENTS.md`, `docs/REGOLE_ATTIVE.md`, dossier V67/V68/V73/V80/V87/V88, configurazioni/lock, log, SHAs e manifest. Questo documento **integra** e non riscrive quei materiali. Preservare tutte le revisioni e le fonti. Un percorso/URL della Libreria ChatGPT o di una sessione precedente non è un link permanente provato.

**Criterio di riuscita:** due pacchetti 4×1 con veri MP4 completi, accessibili e verificati, qualità artistica accettabile e meccanismo ripetibile; solo allora dichiarare la fabbrica autonoma, mantenendo eventuali decisioni V25 del proprietario esplicitamente separate.
