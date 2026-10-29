# LA STORIA RIVIVE V79 — VOLTI FOTO MODERNA, ORIGINALI REALI

Data: 29 ottobre 2026. Richiesta esplicita utente: «volti più realistici e dettagliati come foto moderne; si deve vedere bene il volto» e «Procedi, creami contenuti video ben restaurati».

## Scelta editoriale vincolante
- Usare **pellicola autentica in movimento** e scegliere primariamente persone abbastanza vicine alla camera. Non scegliere solo per celebrità/anno, qualità source centrale. Preferire scansione ad alta definizione reale e fotogrammi con sguardo/espressioni/vestiti leggibili.
- Rispettare il format APROVATO 43054/43056: clip B/N davvero in movimento -> freeze sul medesimo esatto frame -> fotografia AI REALMENTE fotorealistica a colori e ferma per 2–4s -> nuova clip storica differente. 20–26s come media, titolo iniziale elegante SOLO città/anno, musica originale e nessuna voce.
- Fotografia AI finale deve avere aspetto da moderna reflex: incarnato naturale con texture della pelle, occhi credibili, capelli ricchi di dettaglio, abiti leggibili, profondità fisica. Evitare effetto plasticoso, dipinto, volto fittizio, e falso «4K» fatto con l'upscale.
- **NON ripetere V77:** non mischiare globalmente 78% di luminanza della pellicola B/N; questo ha degradato i volti. V78 sorgente + correzioni solo su regioni oggetto dubbie senza togliere dettaglio ai volti.
- **NON inventare persone o cambiare l'identità della scena:** nessuna sostituzione scala->persona, ruota->volto, borsa->bambino, abiti cambiati, bagagli persi. Prompt e negative prompt espliciti, controllo della corrispondenza globale+locale, confronto del fotogramma precedente/successivo, QA semantica umana. Per volti troppo piccoli o illeggibili scegliere altra inquadratura, non inventare un ritratto asserendo sia l'identità autentica.
- **Nota documentale importante:** dettagli di pelle/occhi che non esistono nella scansione sono ricostruzioni plausibili del modello, non fotografie certe della persona storica. Scriverlo nei metadati/post, non nell'immagine.
- Uso di risorse gratuite e fonti PD/CC0 con documentazione; 0 Vidu / 0 API pagate senza consenso, nessuna pubblicazione social o nel sito privato senza esecuzione e verifica.
- Test consegna MP4 H.264/AAC, ZIP, cover, 4 descrizioni social, provenance, visual QA, no ripetizioni e download GitHub Release reale per Android.

## Nuovo soggetto pilota autentico
ELLIS ISLAND · 1903. Ripresa Edison di Alfred C. Abadie del 9 luglio 1903, Library of Congress https://www.loc.gov/item/00694367/; high-definition scan Commons https://commons.wikimedia.org/wiki/File:Emigrants_(i.e._immigrants)_landing_at_Ellis_Island_-.webm (1440×1080, Public Domain Mark). Scene scelte da veri frame 85, 95, 115, 143 secondi del file di 146,7s. Soggetti vicini alla cinepresa. V79 prova 4 foto frame-locked usando DDColor e modello gratuito Finegrain. Script: src/storia_v79_ellis_1903_hd_faces_video.py; job: .github/workflows/storia-v79-ellis-hd-faces.yml. **Non dichiarare consegnato o HD riuscito finché l'MP4 e la QA esistono**.

## Check qualità prima di consegnare
1. I quattro frame originali sono veri, copie ad alta risoluzione, non fotografie animate.
2. Foto AI 1–4 salvate realmente con hash, colori e geometria validati; vicinanza del volto, numero di soggetti e oggetti corrispondono.
3. Testare video completo con ffmpeg -xerror, file ZIP CRC e audio, pattern V74 (clip B/N movimento -> FOTO AI FERMA) e titolo elegante città/anno.
4. Verificare che le facce più belle non siano frutto di persone inventate. Preferire meno scene approvate piuttosto che 4 scene mediocri. **Il modello non può certificare identità storiche di persone quasi illeggibili.**
5. GitHub release diretta e URL esterno comprovato, non inventare link. Conservare V76 e V78 precedenti.
