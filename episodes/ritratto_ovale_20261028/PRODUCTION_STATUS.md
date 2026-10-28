# Il ritratto ovale — Gacrux narrato / montaggio da revisionare (28/10/2026)

**Stato reale: rendered_needs_review, NON approvato per pubblicazione.**

Formato: LIBRI / RACCONTI, Edgar Allan Poe, *The Oval Portrait* (1842). Copione italiano originale nel ramo `episode/ritratto-ovale-20261028-preproduction-v1`.

## Correzione dopo feedback dell'utente
- Le versioni precedenti con solo musica o voce locale eSpeak sono prove **rifiutate**. Non definirle Gacrux, finali, né riutilizzarle come standard.
- Per i LIBRI produrre PRIMA la narrazione Google Gemini Gacrux, acquisire `VOCE.wav` e allineamento reale, POI decidere i cambi di immagine e renderizzare. Nessun audio alternativo automatico.
- Nessuna scena da ripetere solo perché occorre riempire tempo; tenere uno stile coerente e volti non tagliati.
- Un MP4 tecnicamente valido non prova bellezza, gesto visibile, continuità né approvazione editoriale (V44).

## Voce Google effettivamente generata
- Workflow GitHub riuscito: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40672784433
- Workflow: `.github/workflows/ritratto-ovale-gacrux-20261028.yml`, una sola chiamata Gacrux; nessun retry.
- Artifact GitHub: `RITRATTO_OVALE_GACRUX_20261028` (ID 12808214370), `VOCE.wav` e `VOICE_PRODUCTION.json`.
- Motore riportato dal modulo: `gemini-3.8-flash-tts`, voce `Gacrux`; durata 167,96 s.
- Allineamento parola/voce: ASR con interpolazione, corrispondenza 0,897959. L'allineamento richiede comunque revisione dei tagli precisi.
- La disponibilità generale della quota Google o gli addebiti futuri non sono deducibili da questa singola riuscita.

## MP4 prodotto localmente nell'ambiente ChatGPT
- `IL_RITRATTO_OVALE_GOOGLE_GACRUX_COMPLETO_DA_REVISIONARE.mp4`, 720×1280 H264/AAC, 169,167 s (2:49).
- SHA-256: `d013da961940b14e7fb03a41e4c23ee4f1a1ce3d6a9470d7e460378b2d016c56`.
- 20 scene originali AI distinte + una copertina nuova in chiusura; musica procedurale originale in sottofondo, niente sottotitoli.
- La presenza udibile della voce è stata controllata sull'audio del nuovo MP4: correlazione dell'inviluppo RMS con la sorgente Gacrux 0,9585, livello RMS misto circa −22,6 dBFS.
- Decodifica video/audio completa e verifica 20 scene superate, Android 480p, anteprima e ZIP V36 generati; verifica ZIP CRC locale.
- I MP4, le illustrazioni e i pacchetti esistono **nell'ambiente di chat**, NON sono automaticamente contenuti nel repository, nel sito o nella Video Library Studio.

## Qualità editoriale ancora da approvare
- Viaggiatore e pittore si somigliano troppo.
- Immagini statiche durante alcune frasi d'azione; non dichiararle animazioni IA.
- Il montaggio finale richiede verifica umana di fluidità, corrispondenza della voce, identità dei personaggi e valore visivo.
- V44: fino a revisione valida riferita allo SHA esatto, mantenere `rendered_needs_review`; PR in bozza, non pubblicare o importare tra i video approvati.
- Nessuna chiamata image-to-video/text-to-video a pagamento effettuata, nessun credito Vidu/Kling/Runware/Wan/Seedance consumato.

## Fonti
- Opera originale di Poe (1842): https://www.eapoe.org/works/info/pt037.htm
- Illustrazioni narrative originali generate con IA; non classificarle automaticamente pubblico dominio.
- Musica: registrazione originale procedurale senza campioni esterni.
