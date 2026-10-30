# ArtVision V76 — Camera Museum continua, sincronizzata per capitoli (30/10/2026)

## Feedback e bug effettivo

Il terzo 4×1 di Hokusai (Met JP1847, The Great Wave) è il primo test del preset Socrate/Klimt su una stampa orizzontale piccola (25,7 × 37,9 cm). In questo lavoro abbiamo rifiutato due varianti difettose **dello stesso slot Critico Museum**, non creato nuove varianti.

- V74: targhetta sintetica della sala troppo grande quando la camera si avvicina alla stampa. RIMOSSA in V75, sostituita da trasparenza nei post sulle fonti.
- V75: camera insegue ognuna delle **52 singole frasi** e attraversa troppo rapidamente punti distanti (Fuji/onda/barche). Il gate V57 su 4654 frame reali ha misurato MAD grigio **47,477/255**, con frame consecutivi oltre la soglia 35; VERSIONE SCARTATA.
- V76: camera segue **11 capitoli semantici**: 6–8 secondi per raggiungere un nuovo soggetto, poi regia ferma/stabile mentre la voce lo analizza. Il Critico Standard mantiene l'allineamento visivo fine delle 52 frasi. In Museum resta un unico movimento continuo in/out, nessun taglio duro o finta animazione delle onde.
- V76 gate sull'intero MP4 a 20fps, **4654 frame**, picco MAD **28,042/255**, zero candidati MAD oltre 35. **PASS tecnico**, non sostituisce la visione umana V25.

## Regola generale

Nel Museum (anche Critico), gli spostamenti principali tra soggetti distanti devono seguire gli **snodi del racconto** e non reagire meccanicamente a ogni pausa del narratore. Prima di ogni export a qualità release:

1. preparare una scaletta dei capitoli, con tempo di ingresso/uscita e soggetto fisico; allineare il fine dettaglio per frase soltanto quando ciò non provoca accelerazioni artefatte;
2. calcolare un percorso ottico continuo in spazi fisicamente credibili, mantenendo l'identità dell'unico esemplare originale, delle sue proporzioni e della cornice consentita;
3. evitare cambi camera rapidi e oscillazioni, targhette/finte decorazioni ingrandite in primo piano, persone mozzate, texture geometriche artificiali;
4. test quantitativo V57 per frame e controllo dei salti; annotare le versioni scartate e i motivi; NON etichettare come completata la versione che fallisce;
5. la sala digitamente ricostruita va dichiarata esplicitamente (non foto di una galleria vera), e la cornice senza documentazione NON deve essere chiamata storica o reale.

## Contenuti / fonti che non cambiano tra le versioni
- Il Met object 45434, accession JP1847, resta l'originale utilizzato nei quattro video; nessuna confusione con altri esemplari.
- MP4 Critico Standard V74: 232,7 secondi, SHA256 `20eee2b33cdf8a007213a2ce92b9c98c16bd63b5b93d8e91083dbf9614959ba3`.
- MP4 Critico Museum V76: 232,7 secondi, SHA256 `76576d24242d4c173502d85acd34d7c233fbeb6f55e00e05a5c6e8ae15ac93bb`.
- **WAV Google Gacrux identico nei due:** SHA256 `9ddb4843356843d84994b12b3db05c47119311f9cb42626aff1acf59ff03f913`; AAC payload condiviso SHA256 `fc28ce63b9ae9b86785da63af3c4d4e8e12cf9cc7c705d2348607a55b4ad8580`.
- I due Cinema vengono dagli MP4 ORIGINALI V55/V55C in GitHub Actions artifact e non vengono rigenerati/contati come nuovi.
- L'intero ZIP completo ha SHA256 `6c4b51689b509e81d01a2aedf9732120b08accae7e01c3ec9c2c24396ec039d1`, 92.420.172 bytes, 44 membri CRC PASS.
- ZIP Android 75.635.594 bytes, SHA256 `bc51f80990c81044535422d820e84ecf91d35d39c129ca7e5791510da64dd884`, 5 membri CRC PASS.

Questi sono veri file di una sessione ChatGPT; i ZIP/MP4 non vengono salvati automaticamente come bytes su GitHub. La revisione artistica V25 e il playback sul sito privato **non sono certificati**. Per garantire la persistenza serve l'upload in archivio privato con hash e successivo download verificato.
