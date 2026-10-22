# Music Director & Publication Safety V20 — regole per OGNI nuovo video

**Stato: policy additiva con controllo JSON/CLI.** Nessuna riscrittura di Cinema V6 Gold Master, Critico V2, libri V12, voce Google, vecchi MP4, V17/V19 o pubblicazione automatica. Il controllo V20 non conferisce licenze e non certifica l'assenza di violazioni. Da Android: ChatGPT prepara la scheda, GitHub Actions/ambiente Python esegue la verifica, e la decisione finale di pubblicazione resta separata.

## 1. Scelta musicale creativa obbligatoria

Per ogni video partire da soggetto, emozione, arco narrativo, voce/no voce e struttura musicale. Recuperare asset già autorizzati; valutare internamente fino a **tre candidati** per pertinenza, progressione, qualità di registrazione, possibili punti musicali per tagli e limiti di licenza. Scegliere **una** colonna sonora, non assegnare brani soltanto a rotazione. Nessuna scelta musicale deve mettere in secondo piano il soggetto o pregiudicare la narrazione.

L'esperimento iniziale **75% brani esterni regolarmente licenziati / 25% test con audio nativo Meta** è una preferenza sul lotto aggregato, NON una promessa di reach, NON una regola per ogni episodio e NON un motivo per ignorare i diritti. Se la musica nativa è incompatibile con sincronizzazione o condizioni d'uso, preferire l'audio esterno. Evitare di pubblicare due montaggi quasi identici per provare due tracce.

- **Cinema V6**: solo strumentale, senza voce, intro e font invariati, crediti completi nella caption; montaggio sulle frasi musicali, non su tagli ogni N secondi.
- **Critico / libri**: voce approvata prioritaria, ducking musicale da verificare all'ascolto, pause motivate; no sottotitoli secondo V12.
- **Visual Music / HyperLumen**: sincronizzazione documentabile sul materiale musicale reale; generatori ancora da recuperare se il registro V13 lo indica.
- **Controluce**: musica non deve trasformare ipotesi in fatti o spettacolarizzare tragedie.

## 2. Sorgenti e diritti — quattro categorie da NON confondere

1. `external_licensed`: conservare fonte originale, **licenza della specifica registrazione**, prova/URL e data di verifica, usi consentiti (commerciale, Facebook, Instagram, TikTok, YouTube, pubblicità, monetizzazione). Royalty-free NON significa senza copyright. Un brano classico può avere composizione di pubblico dominio e incisione protetta. Una musica trovata online, anche con crediti, non è automaticamente utilizzabile.
2. `meta_sound_collection`: collezione royalty-free Meta; verificare i termini effettivi per Facebook/Instagram e per lo specifico utilizzo. **Non esportare lo stesso audio su altre piattaforme senza licenza separata.** Conservare identificativo e prova del brano.
3. `meta_native_library`: musica comune/trend scelta nell'editor Meta. La libreria Instagram licenziata è normalmente destinata all'uso personale non commerciale, con restrizioni per imprese e territori. **Non spacciarla per musica commerciale autorizzata**, né incorporarla nell'MP4 da trasferire altrove. Per esperimenti pubblicabili usare solo se lo specifico uso/account ha un diritto dimostrabile; il solo fatto che la canzone sia selezionabile non sostituisce la clearance. Se è applicata nel social, segnalarlo nel manifest e verificare la corrispondenza audio finale.
4. `original`: composizione E registrazione proprie; salvare prova e confermare eventuali campioni, strumenti o contributi di terzi.

**Valutazione conservativa**: trattare il canale come potenzialmente commerciale/monetizzabile fin dall'inizio; l'assenza di entrate oggi non prova che qualunque brano sia ammesso. Se uso commerciale, monetizzazione o ads sono previsti, verificare il diritto relativo. Crediti nel post non sostituiscono l'autorizzazione.

## 3. Verifica dell'intero contenuto, non soltanto della musica

Rivedere provenienza e permessi di immagini, riproduzioni museali, foto, archivi, opere, copertine, voce, eventuali brand e contenuti sensibili. Per opere nei musei valutare anche condizioni delle riproduzioni e norme locali, specie per usi commerciali. Registrare valore creativo proprio: scelta delle opere, studio, regia specifica, critica, narrazione, montaggio significativo. Meta privilegia contenuto originale e può limitare le opere duplicate o con sole modifiche superficiali. Niente trucchi per fingersi profilo privato, aggirare controlli, usare contenuti altrui o eludere copyright.

Controllare inoltre: caption pertinente (2–5 hashtag solo se utili), titolo autentico, crediti musicali completi e licenze richieste, assenza di clickbait falso, pubblico corretto, contenuti sessuali/gore nel contesto artistico, diritti di immagine e possibili limitazioni di raccomandazione. Un nudo artistico o sangue può essere lecito ma ancora limitare distribuzione: valutare scena e copertina, senza affermare un esito certo.

## 4. Procedura per ogni video — due gate

**Preflight creativo** prima del render: compilare `templates/MUSIC_RELEASE_V20.json` con soggetto, traccia, atmosfera/cue musicali, titolarità e fonti. Se manca musica o licenza, il pacchetto non è pronto per distribuzione. I controlli V17/V19 restano separati.

**Gate di pubblicazione** dopo il render: compilare la stessa scheda, rivedere il filmato INTEGRALE e la caption, verificare termini attuali per le piattaforme selezionate, salvare prove e crediti. Lanciare:

```bash
python src/music_rights_v20.py --manifest output/episodio/MUSIC_RELEASE_V20.json --out output/episodio/MUSIC_REPORT_V20.json
python -m unittest discover -s tests -p 'test_music_rights_v20.py' -v
```

`BLOCKED`: almeno una condizione dichiarata incompatibile (non pubblicare).
`REVIEW_REQUIRED`: dati, prove, controlli o autorizzazioni mancanti (non pubblicare).
`READY_FOR_MANUAL_PUBLICATION`: controlli documentali dichiarati completi, **non** certificazione di diritti/sicurezza e NON invio automatico a Meta. Il consenso esplicito alla pubblicazione deve essere presente per singolo contenuto o in un mandato operativo corrente verificabile.

**Obbligo del kit di consegna** per ogni nuovo video: MP4 e copertina, identità traccia e fonte, prova licenza con data e limiti, crediti esatti, note della regia musicale, caption pronta, piattaforme idonee, `MUSIC_REPORT_V20.json`, indicazioni Android di caricamento e istruzioni in caso di claim. Per audio nativo da scegliere nel social, il video non diventa un master multipiattaforma già sonorizzato.

## 5. Se arriva un claim, un blocco o una mutazione audio

Non aggirare i controlli alterando tonalità/velocità, sovrapponendo rumori, eliminando nomi o aprendo profili fittizi. Salvare subito notifica completa, ID post, traccia, licenza originale, prova di download e crediti. Controllare il motivo esatto (match automatico, segnalazione, territorio, account, commercialità). Se manca un diritto, sostituire con audio certamente autorizzato e aggiornare la ricetta; se la contestazione è infondata, usare la procedura ufficiale di ricorso e inviare prove valide. Il ricorso DMCA è un atto formale, valutare consulenza legale se necessario. Non promettere assenza di ban né distribuire di nuovo mentre il rischio rimane irrisolto.

## 6. Misurare senza raccontarsi miti

Confrontare su un campione reale e formati simili: retention normalizzata alla durata, condivisioni/1.000 views, follower attribuiti, reach non follower, eventuali restrizioni. Una differenza casuale non dimostra il peso della musica. Esaminare 7 e 28 giorni, senza ripubblicare cloni. Il rapporto 75/25 è un test modificabile; non è favorito da Meta per definizione.

## Fonti ufficiali (verifica: 2026-10-22)

- [Meta: accesso alla libreria musicale Instagram e Sound Collection](https://www.facebook.com/help/instagram/402084904469945)
- [Meta: originalità e distribuzione dei video (marzo 2026)](https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/)
- [Meta: misure contro contenuti spam e manipolazioni](https://about.fb.com/news/2025/04/cracking-down-spammy-content-facebook/)
- [Meta: reclami e ricorsi copyright](https://www.facebook.com/help/194353905193770)
- [Meta: strumenti musicali per annunci Reels](https://www.facebook.com/business/ads/facebook-instagram-reels-ads)
- [Meta: nuovi segnali e preferenze di raccomandazione](https://about.fb.com/news/2026/10/introducing-your-algorithm-facebook/)

**Nota:** le politiche e le licenze cambiano: ricontrollarle alla distribuzione. I report sono una checklist eseguibile su affermazioni/documenti, non una revisione giuridica o audiovisiva automatica.
