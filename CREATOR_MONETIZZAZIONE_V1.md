> Cadenza aggiornata: [produzione intensiva V15](docs/PRODUZIONE_INTENSIVA_V15.md), obiettivo almeno 10 video/giorno in autonomia. La cadenza precedente di due video/settimana è superata.

> Priorità aggiornata: [piano di crescita V14](docs/PIANO_CRESCITA_V14.md). Per ora sono rimandati commissioni, outreach a editori/aziende, sponsor e ads. Le sezioni commerciali sotto restano riferimenti futuri.

> Aggiornamento: leggere [strategia verificata V13](docs/STRATEGIA_CREATOR_V13.md) per priorità correnti, limiti delle fonti e metriche confrontabili.

# Creator Business Lab V1 — Strategia monetizzazione (21 ottobre 2026)

> Modulo aggiuntivo. NON sostituisce la regia V6 ArtVision, il racconto V12, la voce Google, FFmpeg, le Release e la videoteca Cloudflare. NON pubblica, non genera MP4, non chiama API a pagamento e non legge dati privati.

## Obiettivo
Misurare **profitto economico reale, ore investite, crescita di pubblico e originalità**. Le visualizzazioni sono un mezzo, non l'obiettivo finale. Il metodo è: strategia → brief → produzione → QA → pubblicazione autorizzata → analisi 7/28 giorni → iterazione.

## Fonti esaminate e adozione
- https://github.com/rampstackco/claude-skills (content-strategy, content-brief-authoring, seo-keyword, editorial-qa): separazione tra posizionamento, argomento, singolo brief e QA. Adottiamo il modello, non copiamo indiscriminatamente le skill nel motore video.
- https://github.com/heymarii/ai-blueprints/tree/main/workflows/content-creator : report settimanali multi-piattaforma; è un BLUEPRINT, non un connettore API funzionante. Adottiamo il ciclo report → decisione → calendario.
- https://github.com/azizaeffendi/content-creator-monetization-guide : servizi, prodotti digitali, ricavi pubblicitari. Tabelle dei redditi sono promozionali/ipotetiche, NON proiezioni per il nostro canale. Il README elenca documenti strategies/03 e /04 NON presenti nel repository al controllo odierno.
- https://github.com/charlie-morrison/content-creator-prompts : prompt hook/script/CTA, utili come ispirazione; README offre esempi gratuiti, il kit completo è a pagamento.
- https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-content-creator.md : ruoli separati per ricerca, produzione, distribuzione e analytics; i suoi KPI numerici sono obiettivi di esempio, non benchmark garantiti.
- https://github.com/gitroomhq/postiz-app : candidato futuro per scheduling autorizzato, MA self-hosting richiede server, manutenzione e developer apps approvate; AGPL da valutare.
- https://github.com/n8n-io/n8n : candidato futuro per automazioni, non serve al MVP.
- https://metricool.com/ : candidato pronto per raccolta statistiche, verificare funzioni e limiti del piano prima di spendere.
- https://developers.google.com/youtube/analytics/reference/reports/query : API analitiche vere richiedono OAuth, autorizzazioni e collegamento al canale.

## Tre pilastri, tre promesse diverse
1. **Tra le Pagine** — racconti fedeli di libri e film; target lettori e cinefili; voce calda; trama e interpretazione originale; clip di 25–45 s per portare al video da 3–6 minuti. Rispettare i diritti sul film: niente scene filmiche senza licenza; immagini originali realmente nuove.
2. **ArtVision** — critica d'arte con punto di vista e opere autentiche contestualizzate; target curiosi d'arte; video brevi con commento originale. Per i video musicali contemplativi usare la V6 approvata ma variare ogni montaggio in modo non meccanico, soprattutto se si punta alla monetizzazione.
3. **HyperLumen / Musica Visual** — esperimenti visivi effettivamente distinti, sincronizzati con musica con licenza commerciale documentata. Non fare dieci varianti pressoché uguali. YouTube può giudicare inautentici contenuti seriali minimamente variati.

Non aprire necessariamente 3 canali subito. Testare contenuti e pubblico, poi separare i marchi se l'analisi evidenzia audience incompatibili. Evitare di mischiare arte, libri e video promozionali commerciali senza logica sullo stesso feed.

## Gerarchia di monetizzazione (più vicina al primo euro → più lenta)
A. **Servizi video su commissione**: usare 3 casi studio del catalogo, costruire proposta a prezzo chiaro e contattare 10 potenziali clienti di settori conosciuti; chiedere budget e necessità reali, non promettere follower/risultati. Esempio pacchetti DA TESTARE: €79–149 per un video breve oppure €249–399 per tre; include numero limitato di revisioni, diritti e consegne scritte. Sono prezzi sperimentali, non prezzi di mercato verificati.
B. **Affiliazioni pertinenti**: quando c'è pubblico e un prodotto genuinamente coerente (libri, attrezzature, materiali creativi), usare link tracciabili autorizzati, dichiarazione pubblicitaria e policy programma.
C. **Prodotto digitale proprio**: preset, template e guida originale testati; vendita solo dopo evidenza di una richiesta del pubblico.
D. **Sponsorizzazioni**: quando metriche e community giustificano un media kit con numeri reali.
E. **Ricavi delle piattaforme**: opportunità importanti MA non il primo euro più affidabile.

## Misura economica
Per ogni pubblicazione: id, titolo, format, piattaforma, data, visualizzazioni, engagement, durata media, durata del video, ore di produzione imputate, spesa imputata, ricavi REALI in €, link pubblicato. Una stessa produzione su 3 piattaforme va collegata mediante production_id e i COSTI/ORE NON devono essere contati 3 volte. Nella dashboard MVP i costi/ore vanno imputati a un'unica riga oppure suddivisi manualmente in quote non sovrapposte. Nessuna metrica inventata.

- Contributo di cassa = ricavi tracciati - costi tracciati (al lordo di imposte, contributi e overhead non inseriti).
- Contributo orario = contributo di cassa / ore registrate; distinguere valore negativo da zero.
- RPM osservato = 1000 × ricavi reali / visualizzazioni. Non è un RPM stimato e non è confrontabile fra piattaforme come fosse il medesimo regime pubblicitario.
- Controllare oltre alle views: retention, condivisioni per 1000 views, clic in uscita e conversioni. I dati mancanti non valgono zero.
- Decisione dopo 7 e 28 giorni, tenendo conto dell'età dei post e confrontando stesso formato sulla stessa piattaforma; campioni piccoli → soltanto indizi.

## Regole per gli agenti virtuali
- **Research**: osserva temi/canali e raccoglie link, senza copiare la sceneggiatura né aggirare piattaforme.
- **Strategist**: propone 5 argomenti con audience, promessa, angolo nuovo, costo, potenziale monetizzazione e motivo verificabile.
- **Writer**: hook in 3 sec + arco narrativo + naturalezza; fedeltà V12 e rispetto storia.
- **Creative director**: sceglie immagini e MUSICA in relazione al momento della storia; V6 e qualità preferita utente. Non impone la stessa struttura ad ogni opera.
- **Rights & QA**: controlla fonti, veridicità, licenze video/foto/musica, monetizzabilità, crediti, eventuale disclosure AI, sensitive scene policy.
- **Publisher**: propone per piattaforma 9:16 e orizzontale se appropriato, titolo, thumbnail, descrizione e link; pubblica SOLO previa autorizzazione.
- **Analyst**: legge statistiche REALI, quantifica performance, propone cosa continuare, cambiare o fermare. Non inventa vincitori se non ci sono dati.

## Policy indispensabili
- YouTube: https://support.google.com/youtube/answer/1311392 — contenuto originale, non ripetitivo o prodotto in massa con variazioni minime; slideshow generici rischiosi.
- Facebook: https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/ — premia originalità e contributo sostanziale, penalizza contenuti copiati.
- YouTube disclosure IA: https://support.google.com/youtube/blog/424874071/updates-to-ai-content-disclosure-and-labels — se si generano scene fotorealistiche di eventi realistici e persone reali, verificare obblighi di dichiarazione.
- Diritti: opere museali, fotografie, adattamenti cinematografici, brani musicali e registrazioni sonore hanno diritti distinti. "Online" o "gratuito" NON significa libera monetizzazione. Il copyright del racconto/libro originale può persistere.
- Mai promettere immunità da ban, monetizzazione automatica o ricavi garantiti.
- API e token fuori dal browser e dal GitHub pubblico.

## Calendario sperimentale a basso costo (90 giorni)
**Settimane 1–2**: 6–9 video *diversi*, 2–3 format, canali e audience definiti. Per ognuno almeno 2 ipotesi titolo/copertina; una sola pubblicata e risultati tracciati. Preparare 3 case study di lavori realmente consegnati per eventuali commissioni.
**Settimane 3–4**: report settimanale, primo confronto a 7 giorni, riciclo SOLO di contenuti posseduti e realmente originali in clip brevi; test outreach mirato senza spam. Niente spesa in ads.
**Mese 2**: concentrarsi su 1–2 format che dimostrano retention/visite/ricavi migliori, smettere quelli ripetitivi; predisporre pagina servizi e modello preventivo; valutare affiliazioni pertinenti.
**Mese 3**: consolidare serie col proprio linguaggio distintivo, testare un'offerta digitale con una mini lista d'attesa; analisi costi/ore/ricavi e domanda reale. Non moltiplicare output senza guadagno/retention.

## Dashboard reale, non finta
Nuova pagina: [Creator Business Lab](docs/creator-business.html). Salva ogni riga soltanto nel browser di quel dispositivo con localStorage, nessun dato trasmesso a GitHub o al sito. Offre backup JSON import/export e il pulsante **Copia report per ChatGPT**: trasferisce volontariamente negli appunti un report basato sui dati reali, per un'analisi AI senza nuove API a pagamento. Non è un servizio cloud, non legge automaticamente le statistiche dei social e non recupera automaticamente i video dal sito. In futuro sostituire l'ingresso manuale con API autorizzate (YouTube prima) oppure import dei CSV ufficiali dei social. Non committare export con entrate personali nel repo pubblico.

## Checklist pubblicazione singolo video
1. Fonte e opera identificati, copyright e licenza commerciale verificati.
2. Video non è una copia o un montaggio di stock generico.
3. Hook e regia pensati per quel soggetto; scene visivamente pertinenti.
4. Voce/suono con licenza; mixer non copre la parola; file controllato.
5. Preset copertina di serie rispettato, ma soggetto del video chiaramente diverso.
6. Piattaforma, titolo, thumbnail e CTA non ingannevoli; disclosure AI se dovuta.
7. Autorizzazione umana alla pubblicazione.
8. Misurazione a 7 e 28 giorni, senza confondere views con guadagni.
