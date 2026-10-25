# Immagini gratuite V1 — prova isolata per Tra le Pagine

**Stato:** modulo aggiuntivo sperimentale, NON sostituisce Archivio Media V7, Studio Ibrido V6, TTS Gacrux, renderer FFmpeg o i master esistenti.

## Obiettivo e decisione
Partire da 1–3 illustrazioni originali per `La macchina del tempo`, valutare tempi reali, modello, personaggi, fedeltà alle frasi e idoneità dei risultati prima di passare a 25–35 immagini per film. Nessun conteggio quotidiano o costo zero di GPU è garantito.

Scelta tecnica: API asincrona AI Horde come primo provider gratuito, con esplicito consenso alla prova, priorità variabile dei volontari e stop su 429/timeout. Adapter isolato, sostituibile; non cambiare V7 o V11. Kaggle/ComfyUI/Z-Image restano **fallback di ricerca**: non dichiararli integrati finché non sono realmente collaudati. Le immagini storiche/Commons restano sorgenti distinte, non da confondere con generazione nuova.

## Dal telefono Android: come provare
1. Apri [AI Horde](https://aihorde.net/) e crea un account personale gratuito; il provider attribuisce una **API key**. Evita di scrivere la chiave in chat, issue, commit o screenshot.
2. Nel repository GitHub apri **Settings → Secrets and variables → Actions → New repository secret**, con nome esatto `AIHORDE_API_KEY` e valore della chiave. Questa operazione è dell'utente proprietario.
3. Dopo l'unione del ramo nel principale, apri [Actions → Immagini gratuite V1](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/workflows/immagini-gratuite-v1.yml).
4. `Run workflow` → `mode=plan`: controlla tre scene e prompt, senza rete e senza consumare AI Horde.
5. `mode=models`: consulta i nomi dei modelli **in quel momento** e scarica l'artifact `MODELLI_DISPONIBILI.json`; scegliere un modello con worker disponibili e con licenza commerciale verificata.
6. `mode=generate`: incolla **il nome del modello**, imposta un'attesa ragionevole; invia al massimo 3 scene nella prova. Il workflow genera file `scena_*.jpg` + `MANIFEST_IMAGES_V1.json` nell'Artifact. **Non è ancora un MP4.**
7. Apri le scene sul telefono e controlla identità, mani, composizione, oggetti, fedeltà alla frase, testo spurio e modello/diritti prima di collegarle al vecchio renderer.

Nota: `workflow_dispatch` è disponibile nell'interfaccia Actions dopo che il workflow esiste sul ramo predefinito. Prima puoi controllare il codice nel ramo e i test automatici su push/PR.

## Sicurezza e stabilità
- Budget approvato: **0 € di servizi a pagamento**. La rete AI Horde usa GPU volontarie e Kudos, non un pagamento; tempi e quote non garantiti.
- `plan` NON chiama API. `models` usa GET pubblico. `generate` è **manuale**, fallisce se manca la chiave personale o il nome del modello, limite rigido 3 scene.
- In caso di 404, 429, output vuoto o errori: non vengono ripetute richieste di generazione senza consenso; ogni asset fallito resta segnalato nel manifest. I job incompleti vengono annullati ove possibile.
- Nessun download da host non nella lista CDN approvata, no redirect, verifica MIME tramite Pillow, dimensioni e SHA256.
- **Non inviare prompt riservati**: i volontari AI Horde possono teoricamente vedere prompt e immagini. `shared=false` per un account personale riduce la condivisione facoltativa, ma non garantisce privacy assoluta.
- Il manifest non contiene chiavi. I GitHub Actions Artifacts sono temporanei (14 giorni qui). Non conservare asset unici solo negli Artifact: archiviare gli approvati in uno storage persistente prima che scadano.
- Un'immagine generata **non è automaticamente autorizzata per monetizzazione**: controllare licenza del checkpoint effettivamente usato e contenuti. Il campo `license_review_required` resta true.
- Non pubblicare nulla automaticamente. La coerenza semantica delle scene rimane **revisione artistica**, non viene certificata dal solo controllo dei file.
- Se AI Horde ritorna URL di immagini su CDN nuovi non ancora autorizzati, il workflow si ferma; verificare l'host e aggiornare consapevolmente l'allowlist, non disabilitarla per comodità.

## Dove sta il codice
- `src/image_pipeline_v1.py`: adapter provider, controllo code, sicurezza, manifest.
- `config/image_pipeline_v1_demo.json`: tre scene e bibbia dello stile e del personaggio.
- `tests/test_image_pipeline_v1.py`: simulazione offline e controlli negativi.
- `.github/workflows/immagini-gratuite-v1.yml`: avvio da Android + Artifact.

Esecuzione locale (solo pianificazione, nessun account):

```bash
python src/image_pipeline_v1.py --mode plan --brief config/image_pipeline_v1_demo.json --out output/image_pipeline_v1
python -m unittest discover -s tests -p 'test_image_pipeline_v1.py' -v
```

## Cosa manca prima dell'uso produttivo intensivo
- Una prova reale **autorizzata** con account personale e 1–3 immagini; cronometrare disponibilità e qualità.
- Benchmark modelli e checkpoint, con licenze verificabili.
- Approvatore immagini/scene e confronto A/B con identità dei personaggi.
- Un sistema di archivio persistente separato dai 14 giorni degli Artifact.
- Connettore Kaggle GPU o GPU dedicata, **solo se permesso dai rispettivi termini**, come ripiego.
- Collegamento al renderer storico **solo dopo** le prove di fedeltà alle scene.

Fonti: [API AI Horde](https://aihorde.net/api), [guida integrazione](https://github.com/Haidra-Org/AI-Horde/blob/main/README_integration.md), [FAQ/privacy](https://github.com/Haidra-Org/AI-Horde/blob/main/FAQ.md).

**La prova non promette centinaia di immagini gratuite ogni giorno.**
