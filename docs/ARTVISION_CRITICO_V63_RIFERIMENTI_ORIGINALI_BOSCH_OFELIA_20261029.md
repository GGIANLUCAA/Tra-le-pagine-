# ArtVision Critico — RIFERIMENTI REALI V63, verificati dai MP4 originali utente (29 ottobre 2026)

**Questi non sono video ipotetici:** l'utente ha allegato gli MP4 originali già generati in passato con il sistema ArtVision; il confronto SHA256 byte-per-byte con i manifest del repository ha trovato corrispondenza ESATTA. Questi file restano privati nella conversazione; non sono stati copiati, pubblicati né caricati nel repository.

| Allegato utente | Opera | Versione registrata nel repository | SHA256 reale | Durata e formato |
|---|---|---|---|---|
| `39775.mp4` | Hieronymus Bosch, *Il giardino delle delizie* | `modules/artvision_critico/production_series/bosch_director_cut_v22.json` | `2c59c58185ed3d7c51d280bf9c8442414cddf163a231fef08fd7a37d657b0ded` | 124.192667 s; 1080×1920, 20fps, H264/AAC mono 24kHz |
| `39762.mp4` | John Everett Millais, *Ofelia* | `modules/artvision_critico/production_series/ophelia_director_cut_v21.json` | `5551de1442f22e4f8e33cfcab44563957f21d32aa7ddef5d76a2e45549786442` | 69.050000 s; 1080×1920, 20fps, H264/AAC mono 24kHz |

## Stile da riusare direttamente nel Critico Standard Socrate

**Usare il motore storico già esistente**, `modules/artvision_critico/production_series/render_series_v2.py`, come riferimento primario e gli episodi Bosch e Ofelia come esempi operativi. Non ridisegnare il formato Critico né sostituire il motore con un effetto Cinema/Museum.

1. **Narrazione Gacrux italiana originale, forte e comprensibile**, una sola registrazione esatta del nuovo copione; sincronizzare inquadrature al significato della frase. I WAV dentro i vecchi MP4 sono di ALTRI copioni e non possono essere riciclati per Socrate. Il precedente successo Gacrux dimostra che il workflow ha funzionato in passato, ma non dimostra il livello di fatturazione/free quota corrente: nessuna chiamata a pagamento automaticamente autorizzata.
2. Bosch V22: dopo il feedback reale, l'utente aveva apprezzato **spiegazione e voce Gacrux** e bocciato zoom/oscillazioni nauseanti. Documento `bosch_director_cut_v22.json`: **23 inquadrature**, camera prevalentemente ferma, rari movimenti unidirezionali **0–1% del campo nel piano**, dissolvenze **~0.6 s**, niente moto sinusoidale, niente domanda retorica finale fuori luogo. Favorire dettagli con vero contributo critico.
3. Ofelia V21: `ophelia_director_cut_v21.json` contiene **17 piani**, apertura significativa immediata con volto → mani → fiori nei primi secondi, dettagli pertinenti al parlato, nessuna copertina ferma iniziale, niente split screen ripetitivo; panoramica per il contesto e ritorno finale all'opera.
4. **Copertina Critico V2 uniforme**: fondo scuro, opera vera, linea sottile dorata, solo titolo dell'opera e artista; assenti watermark, sottotitoli impressi, didascalie dei capitoli e tecnicismi. La copertina è diversa dall'apertura montata: partire con un dettaglio vivo, poi mostrare l'opera.
5. **Durata dipendente dal copione e dal WAV vero**, non forzare 69 s, 124 s o 3 minuti; qualità della spiegazione sopra al minutaggio.
6. **Socrate Critico Standard**: copione madre già scritto (366 parole, 10 passaggi) in `docs/productions/2026-10-29-socrates-critico-master-v60/COPIONE_GACRUX_V62.txt`. Regia basata su coppa, gesto verso il cielo, postura di Socrate, ragazzo in rosso, discepoli, Platone, catene, composizione finale. Inquadrare il dettaglio quando la voce lo descrive.
7. **Socrate Critico Museum**: **stesso IDENTICO file WAV e copione** del Critico Standard, ma regia Museum V57 del quadro, cornice fotografata reale, sala ricostruita senza visitatori troncati, ingresso e ritorno CONTINUI, V46 proporzioni vere. Non scambiare il Critico Standard per una diversa variante semplicemente aggiungendo/ritagliando il quadro.
8. QA: controllare realmente i primi 0.1/1/3/5/7 secondi, ascoltare in velocità normale, verificare sincronizzazione audio–visuali, arte autentica, musica con fonte e licenza registrazione, testo originale, MP4 H264/AAC verticale, cover, ZIP CRC, quattro post FB/IG/TikTok/YouTube, V25 e archivio privato. Niente approvazione automatica né riuso scorretto dei master.

## Blocco attuale dei due Critico e un passo concreto

- V62 ha confermato che la chiave `GEMINI_API_KEY` è presente sul workflow GitHub, ma le variabili di attestazione **free quota / progetto senza fatturazione** sono vuote. `ArtVision V62 — Gacrux` run 40892861596 ha terminato con `blocked_voice_free_tier_not_verified`, **nessuna chiamata Google**, **nessun WAV Socrate**, nessun Critico MP4.
- Questo blocco non giustifica inventare una voce nuova né stravolgere il formato. Si devono riutilizzare **il renderer V2 e la direzione V21/V22 approvata**, chiedendo solo l'autorizzazione di fatturazione se effettivamente necessaria e non coperta da quota gratuita verificata.
- Due slot Cinema Socrate già renderizzati; NON ri-renderizzare. **Conteggio: 2/4 prodotti, 0/4 approvati.**

**Un riferimento esatto non è una licenza di pubblicazione** e un test tecnico non sostituisce la visione. I vecchi video rimangono nei file utente e i loro originali approvati non vengono modificati.
