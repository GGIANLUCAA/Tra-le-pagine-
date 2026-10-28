# V56.1 | La Storia Rivive — obiettivo visivo obbligatorio
**Correzione utente: 28 ottobre 2026.** I tre video condivisi sono riferimenti artistici, non materiale da copiare o incorporare.

## Diagnosi verificata sui tre riferimenti
- Esempio dopoguerra: immagini storiche B/N alternate a scene multicolore, con incarnati, abiti e architetture ben distinti.
- Esempio Paris 1920s: apertura già a colori, poi tagli su B/N; look vivido ma vintage. Non assumere che ogni immagine a colori sia una scansione originale.
- Esempio Paris 1899: apertura a colori con persone e abiti d'epoca, seguita da B/N. Le transizioni NON devono essere sempre uguali.
**Il pilot Beirut 1919 è stato rifiutato artisticamente:** solo viraggio monocromatico seppia, non il cambiamento richiesto. Non riproporlo come prodotto pronto.

## Requisiti BLOCCANTI per il video principale
1. Colorizzazione **multicolore effettiva**: pelle, capelli, tessuti, pietra, legno e cielo con tonalità differenti e naturali; palette morbida vintage. Il semplice filtro seppia o giallo NON conta. Il video completo deve mostrare chiaramente almeno alcuni secondi di vero multicolore.
2. Registrare modello/versione e confermare manualmente `natural_multicolor_reviewed=true`, `reference_style_match_reviewed=true`, `temporal_stability_reviewed=true`. Il nome di un modello e una metrica colore da soli NON provano la resa.
3. Non inventare persone e oggetti e non cambiare azioni: gli stessi fotogrammi originali quando si mostra il passaggio prima/dopo. Se si inserisce una ricostruzione AI, serve categoria distinta ed etichettatura esplicita.
4. Hook 0–3 s: partire da una scena di forte interesse, con immagine colorizzata già all'inizio *oppure* B/N che si rivela progressivamente; scegliere in base all'originale, senza template fisso. Titolo documentato e leggibile.
5. Restauro moderato, nessun volto artificiale, colori che lampeggiano, saturazione Instagram o filtro cinematografico moderno; esaminare moto e continuità per almeno tutti i secondi del tratto a colori.
6. Il film originale 4:3 NON deve essere ritagliato 9:16 a costo di eliminare persone o movimenti importanti. Non dichiarare «4K nativo» per un semplice upscale.
7. Copertina da un vero fotogramma del MP4 colorizzato; audio licenziato, crediti, 4 post diversi, ZIP, file scaricabili Android e archiviazione sito come da V55/V28.
8. Spesa predefinita ZERO. Vidu non parte automaticamente. Se la colorizzazione gratuita non è tecnicamente disponibile, lo stato è `colorization_pending` e NON `delivery_ready`; non produrre un altro seppia in sostituzione.

## Controllo qualità
Controllare timecode 0.1/1/3/5/7 s e almeno 3 punti del segmento multicolore. Guardare l'intero video, verificare che vestiti, volti e oggetti mantengano le tinte nel tempo; confrontare originali e colorizzati allineati. Un video che appare soltanto ingiallito passa la QA tecnica ma **fallisce quella artistica**. Lo stato `sepia_tint` è ammissibile solo per provino interno, non per la consegna del nuovo format.
