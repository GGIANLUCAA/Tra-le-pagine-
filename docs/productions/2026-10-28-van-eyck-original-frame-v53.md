# ArtVision Cinema V53 — Jan van Eyck, Portrait of a Man (Self Portrait?)

**Data:** 2026-10-28 · **Stato:** `rendered_needs_review` · **Versione:** V53
**Nuovo MP4 realmente prodotto:** 67.000 s, 1080×1920, 24 fps, H.264/AAC, 1.608 fotogrammi, 18.028.500 byte.
**SHA-256 master:** `3aedc2202000955a6ef147285037f0707739a4fe40fdefd5af48b0c975b3bfd0`.
**Non Gold Master, non revisionato/approvato artisticamente, non pubblicato.** Nessuna chiamata a modelli video a pagamento.

## Scelta del soggetto e non duplicazione

Il codice di ricerca GitHub sul repository attuale non ha trovato episodi sul titolo esatto «Portrait of a Man». Le menzioni di Van Eyck riguardano *The Arnolfini Portrait* e altri riferimenti, non questo dipinto. La ricerca indicizzata non dimostra l'assenza in eventuali archivi esterni.

Candidati confrontati: **Van Eyck** (NG222, 26×19 cm, cornice originale documentata e firmata), **Klimt — Judith** (84×42 cm; cornice progettata da Gustav e realizzata da Georg, ma fotografia/diritti non verificati per questa produzione), **Holbein — The Ambassadors** (207×209,5 cm, cornice attuale replica XX secolo). Scelta Van Eyck per un effetto di sorpresa basato sulla **vera cornice**.

Fonti museali: https://www.nationalgallery.org.uk/paintings/jan-van-eyck-portrait-of-a-man-self-portrait e https://www.nationalgallery.org.uk/stories/10-minute-talks-jan-van-eyck-s-portrait-of-a-man-self-portrait .

## Autenticità della cornice e scala fisica

Il quadro misura **26×19 cm**, secondo la National Gallery, NG222. La **cornice dorata è originale**; i lati sono intagliati nello stesso legno del pannello, le traverse superiori/inferiori aggiunte, e le lettere sono dipinte a imitazione di incisioni. Il motto in alto è `Als Ich Can`; in basso l'iscrizione riporta autore e data 21 ottobre 1433. L'identificazione come autoritratto è probabile, non accertata. **Le misure esterne della cornice non risultano verificate**: il render usa un'approssimazione scenografica di circa 31 cm di altezza esterna rispetto a un adulto di circa 170 cm, senza affermarla come dato museale.

Riproduzione dell'opera **insieme alla vera cornice**: https://commons.wikimedia.org/wiki/File:Portrait_of_a_Man_in_a_Turban_(Jan_van_Eyck)_with_frame.jpg ; file originale 3315×4226 validato nel [run GitHub di acquisizione](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40660819078) (artifact 12803786123). Wikimedia Commons etichetta la riproduzione PD-Art/PDM. Le norme specifiche di riuso commerciale e beni culturali nel territorio di diffusione vanno confermate: la sola etichetta Commons non elimina ogni obbligo.

**Sala:** nuova ricostruzione illustrativa, non fotografia della National Gallery. La cornice dell'immagine sorgente è stata incassata prospetticamente sulla parete illustrata, con ombre; non è stata generata una falsa replica della cornice. L'apertura mantiene l'opera piccola; ingresso ed uscita consistono in movimenti di camera continui sui materiali originali. Niente sovrapposizioni tra quadri, niente edge stretch.

## Identità e post

Prima schermata e copertina: `PORTRAIT OF A MAN (SELF PORTRAIT?)`, `JAN VAN EYCK`, fascia traslucida scura, titolo serif avorio, filo orizzontale e artista sans-serif, riprendendo il modello della copertina V50 Goldfinch **realmente confrontato**. Non dichiarato confronto diretto del film originale Cyclops/Hiroshige perché il relativo MP4 non è stato recuperato in questa sessione. Quattro post italiani distinti V28 per Facebook, Instagram, TikTok, YouTube salvati realmente nello ZIP.

## Audio, QA, consegna

Musica: registrazione strumentale sintetica **originale prodotta localmente** con `render_v53.py`; nessuna registrazione musicale commerciale utilizzata. Cinema V6 non prevede voce. Controllati ffprobe, decodifica integrale video+audio senza errori, copertina/primo frame (differenza media RGB nella zona titolo circa 2), 1.608 frame H264, traccia AAC, integrità ZIP via `zipfile.testzip()`, 4 post non identici con 2–4 hashtag. Fotogrammi rappresentativi e regia visionati; **non equivalente ad approvazione estetica umana a velocità normale dell'intero film**.

**Originali consegnati e verificati nella Libreria ChatGPT**, cartella `/ArtVision/Original_Frames_V53/`:
- `ARTVISION_VANEYCK_V53_REVIEW.mp4`
- `ARTVISION_VANEYCK_V53_COPERTINA.jpg`
- `ARTVISION_VANEYCK_V53_PACCHETTO_COMPLETO.zip`

Il pacchetto include riproduzione con cornice originale, sala generata, WAV originale, rendering e camera scripts, ricerca, confronto candidati, storyboard, fonti e diritti, JSON ricetta, QA, prima immagine e quattro post social. Il file ZIP **non** certifica pubblicabilità; nessuna pubblicazione automatica.

## Difetti registrati e prossimo ciclo

1. La sala scenografica è illustrativa: trovare una fotografia museale legalmente riutilizzabile quando disponibile, senza attribuire una sala inventata a un museo reale.
2. La durata del dettaglio dello sguardo (7 s) è volutamente contemplativa ma può essere troppo lunga: rivedere con una valutazione estetica e audio integrale prima della pubblicazione.
3. Le iscrizioni autentiche sono state rese più leggibili sostituendo i due dettagli inizialmente troppo piccoli con lente scansioni sulla foto originale. Continuare a verificare leggibilità delle lettere anche da telefono.

**Contratto di rilascio:** `rendered_needs_review` fino a valutazione sul file con hash esatto, senza falso Gold Master e senza costi video IA.
