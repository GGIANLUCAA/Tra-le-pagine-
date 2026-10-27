# V41 — Image-to-video cinese a basso costo (bozza del 27 ottobre 2026)

Questa è un'integrazione sperimentale **NON ATTIVA**: non crea account, non paga API, non modifica master, non pubblica su Video Library Studio. Lavora con immagini originali dei libri, non con finti effetti zoom V39. I clip IA vanno revisati per identità del personaggio, costumi, coerenza con la frase, movimento reale e qualità artistica. ArtVision richiede opere autentiche: non presentare ricostruzioni IA come quadri originali.

## Prezzi e cautela

Fonti ufficiali Vidu:
https://platform.vidu.com/docs/pricing
https://platform.vidu.com/docs/api-reference/video-models/vidu-q2/image-to-video

Vidu Q2 Pro Fast: 720p, $0.005/credito, modalità off-peak a metà dei crediti normali. La stima attuale è $0.04 per 5 secondi e $0.065 per 10 secondi senza audio. Per 20 richieste da 5s/giorno sono circa $24/mese senza scarti e $48/mese se servono due tentativi per clip accettata. IVA e modifiche al listino escluse. **I costi sono stime, controllare saldo e listino prima dell'invio.** Off-peak può richiedere fino a 48 ore; gli URL dei video possono scadere dopo 24 ore.

Il limite di spesa presente nel codice è di $0.10 **per chiamata**, non per giornata o mese. Nessuna generazione non autorizzata. Prima confrontare 1–3 scene; solo dopo valutare un lotto di 20.

## Uso da Android dopo che la PR viene collaudata e unita a main

1. Creare account su https://platform.vidu.com e valutare credito disponibile.
2. Salvare la chiave SOLO nel repository GitHub -> Settings -> Secrets and variables -> Actions -> New repository secret, nome VIDU_API_KEY. Non inviare la chiave in chat o in prompt.
3. Aprire GitHub -> Actions -> "V41 - Image-to-video Vidu low-cost (Android manuale)" -> Run workflow. Il workflow manuale appare dopo il merge sul ramo predefinito.
4. Eseguire mode=plan con slug episodio, numero dell'immagine e un prompt inglese che descriva un'azione concreta. **Questo passaggio non costa niente, non crea MP4**. Scaricare l'artifact e leggere il preventivo I2V_PLAN.json.
5. Solo dopo revisione, eseguire mode=submit con gli stessi input e scrivere AUTORIZZO_10_CENT per una singola richiesta a pagamento; la richiesta genera un task_id. Non ripetere un submit incerto dopo timeout, perché il server potrebbe aver già accettato il task.
6. Usare mode=collect inserendo il task_id dopo che Vidu ha terminato. Questa azione non genera nuovi video né consuma crediti di generazione; salva MP4, verifica formato con ffprobe e confeziona I2V_V41_ANDROID.zip solo con il video. Ripetere il controllo in caso di coda.
7. Scaricare gli Artifacts dalla run Android. L'artifact attuale resta 14 giorni. Nessun collegamento ChatGPT o R2 è garantito fino a importazione realmente verificata.
8. Revisionare integralmente il MP4 e montarlo col sistema originale solo se è bello e pertinente. La V41 non integra ancora da sola l'MP4 nei render V4, V13 o ArtVision.

## CLI e controlli

Comandi disponibili:
- python -m unittest discover -s tests -p 'test_i2v*.py' -v
- python src/i2v_scene_v41.py --episode 03_siddharta --scene 1 --output-dir output/v41
- python src/i2v_budget_v41.py plan --image episodes/03_siddharta/images/scena_01.jpg --prompt "The man walks toward the river as the branches sway in the wind, with subtle natural movements." --seconds 5 --out output/v41

La scena dentro scene_premium.zip è supportata dalla selezione GitHub; questo esempio CLI presuppone il JPG già presente nella cartella images.

Il codice deve essere validato via GitHub Actions PR prima di essere distribuito. Nessuna capacità GPU locale su Android. Non eludere limiti di quote con account multipli. Le prove gratuite via browser di altri fornitori non equivalgono all'accesso API gratuito.

Stato previsto: proposta da verificare, non video approvato, zero API a pagamento chiamate da questo esperimento.
