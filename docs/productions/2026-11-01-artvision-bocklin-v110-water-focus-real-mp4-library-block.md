# ArtVision Böcklin V110 — focus acqua sincronizzato alla voce, MP4 reale (candidato locale)

**1 novembre 2026.** Opera: Arnold Böcklin, *Die Toteninsel*, terza versione 1883, Alte Nationalgalerie NG 2/80. **Stesso slot Critico Museum**, nessuna settima opera, nessuna variante aggiuntiva. Gold V25 = 0.

## Difetto osservato, nuovo rispetto a V109

Dal vero file `VOICE_CACHE_V13.json` recuperato dall'artifact originale GitHub Actions **13053703331** (run **41231513083**) si sono letti i tempi delle frasi, non soltanto i suggerimenti del copione. La voce inizia **5,00 s** dopo l'inizio del filmato.

- «L'acqua è quasi immobile» — voce 24,72–26,78 s → **video 29,72–31,78 s**.
- «Non ci sono onde drammatiche...» — voce 26,78–34,70 s → **video 31,78–39,70 s**.
- Nel V109 ai secondi 30–38 il campo centrale mostrava soprattutto i cipressi scuri e la riva; l'acqua rimaneva nella parte bassa. La voce descriveva l'acqua senza inquadrarla centralmente. Il confronto è stato effettuato su veri frame decodificati, non su storyboard.
- Il V109 aveva già corretto i capitoli 2 e 8 (intero quadro); quei raccordi sono conservati. Gli altri tre video Böcklin e tutti i master rimangono intatti.

## Intervento V110 reale e non distruttivo

È stata generata **una nuova copia candidata MP4** a partire esclusivamente dal file canonico V109 SHA256 `07944553bf1f1547acc34f54185690f1f0c28c20f12cdc888eb24c8b6854a189`, senza scaricare immagini, AI, TTS o consumare crediti. Solo fra **28,25 e 41,15 s**, camera geometrica continua sulla pittura già presente: zoom massimo 1,962× e spostamento verticale verso l'acqua, hold durante le frasi, ritorno fluido per la successiva scena della barca. **259 frame** nel tratto trattato; nessuna doppia esposizione/crossfade. È un movimento virtuale di camera, non acqua animata.

File reale: `BOECKLIN_CRITICO_MUSEUM_V110_ACQUA_SINCRONA_REVIEW.mp4`
- **16.722.838 byte**; SHA256 **`34404bd5c76626e4bcbf25aca206b9c690d5d4071604a6a6eaf093bc01aa06ff`**.
- **110,65 s**, 2213 frame, **720×1280 a 20 fps**, H264/AAC.
- **FFmpeg full decode PASS** sul MP4 reale.
- Audio AAC demux ADTS **bit-identico** a V109/V106/V102: SHA256 **`3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e`**.
- Scansione V57 intera: picco MAD grayscale 180×320 **31,477/255**, **0 frame >35**.
- Confronto visivo frame V109/V110: 35 s MAD RGB 25,58; 50 s 1,84 (solo ricodifica), 85 s 2,11 (solo ricodifica). Il cambiamento è confinato editorialmente alla scena acqua.
- Renderer offline ripetibile: `src/artvision_bocklin_v110_water_focus.py`. Non rilanciare Gacrux o workflow di produzione.

## Archiviazione e limiti verificati

Tentato upload del nuovo MP4 nella Libreria privata `/ArtVision/Bocklin/V110_CRITICO_MUSEUM_ACQUA_SINCRONA/`: **FALLITO** con `library_storage_limit_exceeded`. **Non** è presente un backup V110 in Library, **non** esiste SHA di download di ritorno, **non** è verificato import R2 o playback Android. Il MP4 esiste nel container di questa esecuzione ed è scaricabile con il relativo link sandbox soltanto finché disponibile. Non cancellare file preesistenti per liberare quota senza decisione del proprietario.

**Stato:** V110 candidato locale per confronto artistico; V106 resta il candidato persistente nel pacchetto V107, V109 e V110 non lo sostituiscono automaticamente. Ascolto e visione umana integrali ancora pendenti; **Gold V25=0**, niente social, spese o nuove opere.
