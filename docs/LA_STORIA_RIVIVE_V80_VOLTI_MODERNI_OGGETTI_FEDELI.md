# LA STORIA RIVIVE — VOLTI MODERNI V79–V80 E STOP FACCE SU OGGETTI

**29 ottobre 2026.** Nuovo soggetto: Ellis Island 1903. Film autentico 1440x1080 da LOC/Wikimedia, titolo luogo/anno, video storico che si ferma e diventa fotografia moderna, montaggio social senza voce.

**Punto critico QA appena scoperto:** un sacco/bagaglio a fantasia nel fotogramma dello sbarco a 115 s diventa falsamente un viso umano nella fotografia generativa Finegrain, pur avendo correlazione globale 0.999 con l'originale. **Esempio reale che prova la gravità degli errori locali**. Scene e persone inventate non devono essere presentate come vere.

### Nuovo standard
1. Per le nuove foto usare come base i frame autentici prima di tutto, con vicino-frame reali, non reinterpretazioni di una foto di archivio scollegata.
2. Modello generativo produce fotografia moderna nitida e a colori, ma conservare stesso conteggio persone, persone/oggetti, bagagli, ruote, scale, piani di profondità e vestiti; se inventa una faccia su un bagaglio, ripristinare localmente il bagaglio dal frame sorgente colorizzato, non distruggere il dettaglio globale dei veri visi (errore V77).
3. Restauro volti **solo su ROI umane validate**, preferibilmente con Open Source GFPGAN 1.4 senza GPU/crediti Vidu. Non applicarlo automaticamente su ruote, borse, persone lontanissime o possibili falsi volti. L'esito va confrontato con foto e frame B/N originale.
4. La modernità delle texture artificiali su occhi/pelle/capelli è **plausibile**, non prova della reale identità storica quando il filmato è molto sgranato; non inventare certezze storiche.
5. Preferire tre foto ottime a quattro foto scadenti, ma un video di 20–26s deve contenere abbastanza movimento d'epoca autentico senza inutili zoom o ripetizioni.
6. Qualità da foto moderna **sì**, V77 sfocatura globale **no**, fotogrammi presi dalla fonte in movimento veri, testo nel film solo luogo/anno, soundtrack originale.
7. Solo MP4 con H264+AAC e ZIP decodificati/verificati; GitHub release in modo che il link Android funzioni; social e sito privato non dichiarati pubblicati se non verificati.

Produzione V79: `src/storia_v79_ellis_1903_hd_faces_video.py`, workflow `.github/workflows/storia-v79-ellis-hd-faces.yml`; **4 candidate scenes requested, 3 generated free, 4th stopped by ZeroGPU quota**. Non negare che i tre primi risultati Finegrain siano ancora poco dettagliati.
Correzione V80: `src/storia_v80_ellis_face_gfpgan_video.py`, workflow `.github/workflows/storia-v80-ellis-hd-face-fix.yml`; recupera bagaglio inventato, preserva l'immagine globale e rinforza soltanto alcuni visi reali mediante GFPGAN ONNX scaricato gratuitamente. **Il fatto che un modello sia applicato non costituisce approvazione artistica automatica**: segnalare solo dopo screenshot comparativo, test MP4 e controllo umano.
