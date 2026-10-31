# ArtVision — controllo R2 di sola lettura (31 ottobre 2026)

Controllo diretto tramite connessione Cloudflare autorizzata, endpoint ufficiale GET `/accounts/{account_id}/r2/buckets/video-library-studio/objects?prefix=...`; **nessuna modifica**, nessun upload/credito, nessuna cancellazione. Il bucket `video-library-studio` esiste e contiene gli oggetti sottostanti. Distinguere sempre presenza oggetto da player Android/sito verificato.

## Klimt — quattro MP4 già presenti nel bucket
- `01_Klimt_Critico_Standard_Gacrux.mp4` — **17.136.945 B** + JPEG omonimo.
- `02_Klimt_Critico_Museum_Gacrux.mp4` — **13.583.486 B** + JPEG omonimo.
- `03_Klimt_Cinema_Standard.mp4` — **3.774.837 B** + JPEG omonimo.
- `04_Klimt_Cinema_Museum.mp4` — **4.343.198 B** + JPEG omonimo.
Tutte le dimensioni coincidono con i quattro veri MP4 Klimt recuperati e SHA-verificati in V90; il solo bucket listing non garantisce coincidenza SHA o playback.

## Socrate — risultati selettivi
- `Socrate_Critico_Standard_Gacrux_V67.mp4` — **15.575.097 B** + JPEG.
- `Socrate_Critico_Museum_Gacrux_V67.mp4` — **53.582.121 B** + JPEG.
- `ArtVision_Socrates_Cinema_Standard_V59_Revision_Review.mp4` — **17.855.540 B** + JPEG.
- Anche vecchia revisione `ArtVision_Socrates_Cinema_Standard_V55_Audio_Revised_Review.mp4` 2.534.018 B è presente.
- La ricerca per prefissi `Socrate_Cinema` e `ArtVision_Socrates` **non ha trovato la variante Museum V61**. Non affermare che tutte e quattro sono online nel sito; due originali Critico e Cinema Standard V59 sono effettivamente nel bucket.

## Böcklin V106
- Ricerche prefissi `Boecklin`, `BOECKLIN`, `Bocklin`, `BÖCKLIN`, `boecklin`, `ARTVISION_BOECKLIN` nello stesso bucket: **0 oggetti corrispondenti**. Il pacchetto V107 è backup privato ChatGPT Library fisicamente verificato, non ancora importato in questo bucket. Possibile catalogazione con una chiave differente: il controllo prefisso da solo non prova l'assenza assoluta dal bucket.
- Il connettore Video Library Studio espone lo stato aggregato di 409 video e 250 import ChatGPT, ma non una verifica di playback specifica dei quattro video Böcklin.
- Evitare doppie importazioni. Prima individuare eventuali chiavi alternative via indice/endpoint catalogo; importare con workflow effettivamente autorizzato e testare player dopo ricezione di conferma reale.

## Limiti
Accesso web diretto alla pagina privata non disponibile in questa sessione, perciò **playback R2/Android non attestato**. Nessuna delle verifiche costituisce Gold V25. Niente pubblicazione social e niente spese.
