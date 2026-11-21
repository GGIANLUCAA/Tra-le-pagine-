# ArtVision · ElevenLabs v4 — provino sincronizzato con un quadro (21/11/2026)

## Obiettivo
Soltanto Android/browser e GitHub Actions, niente PC. Integrazione ElevenLabs con un quadro autentico selezionato da ArtVision. Una sola chiamata TTS e un MP3 riutilizzabile, senza pagare di nuovo quando si corregge il montaggio. La voce storica Gacrux non viene sostituita automaticamente.

## Stato
La PR è un prototipo separato: non crea audio fintanto che non viene avviata manualmente una generazione. Su pull request e push del ramo si eseguono soltanto test e la verifica gratuita dell'immagine. Un comando manuale generate richiede il codice esatto ONE_PREVIEW_ONLY; non esiste un trigger programmato che consuma crediti.

Endpoint ufficiali:
- GET /v1/user/subscription per leggere la quota (0 crediti audio)
- GET /v1/models e GET /v1/voices/{voice_id} per controllo dell'identità (0 crediti audio)
- POST /v1/text-to-speech/{voice_id}/with-timestamps: uno solo, modello eleven_v4, output MP3 e timestamp associati
Fonti: https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps ; https://elevenlabs.io/docs/api-reference/user/subscription/get

## Primo soggetto
Pieter Bruegel il Vecchio, The Fall of the Rebel Angels (1562). Utilizziamo i primi quattro capitoli consecutivi del copione Critico già presente nel repo (623 caratteri) e la fotografia autentica 3840×2772 verificata mediante il SHA-256 originale del lavoro V144. Regia che segue i particolari già selezionati: opera intera, centro con Michele, cielo in alto. Nessun dipinto modificato o ricreato dall'IA, e nessuna finta cornice museale.

Una singola chiamata Eleven v4 fornisce MP3 e tempi a livello di carattere. I tempi delle scene sono derivati da quelli veri della voce; un errore di allineamento blocca il montaggio ma preserva l'MP3 già comprato. Output previsti: MP3 isolato, MP4 review 720×1280, timeline, copertina, QA, ZIP CRC. Nessuna pubblicazione, Gold, nuova musica o secondo doppiaggio.

## Configurazione UNA TANTUM sul telefono
1. Dal tuo account ElevenLabs vai su Developers > API Keys e crea una chiave con accesso TTS e lettura account/voices. Non condividere il valore con la chat.
2. Su GitHub Settings > Secrets and variables > Actions crea un Secret ELEVENLABS_API_KEY con quella chiave.
3. Apri ElevenLabs Voice Library, ascolta una voce italiana maschile adulta e aggiungila alla tua libreria. Ottieni il suo voice_id dalla pagina della voce o dall'elenco delle voci API. Crea in GitHub Actions Secrets anche ELEVENLABS_VOICE_ID, con soltanto l'identificativo della voce, non la chiave.
4. Quando il codice sarà collaudato e unito consapevolmente a main, vai in Actions > ArtVision Eleven v4 | one-call Bruegel synchronized pilot > Run workflow.
5. Scegli mode=preflight (immagine/copione, zero crediti), poi mode=account (saldo, voce e accesso, zero crediti audio). Solo quando i due controlli sono riusciti, scegliere mode=generate e scrivere il codice ONE_PREVIEW_ONLY nel campo spend_confirmation.
6. Scarica l'artifact della run e ascolta il confronto con la voce Google. Non ripetere mode=generate per cambiare soltanto la regia: riutilizza il primo MP3.

## Consumi
La prova è di 623 caratteri. Tariffa indicativa ufficiale TTS ~1 credito/carattere: circa 623 crediti stimati, NON un limite di addebito garantito. Il controllo preflight richiede almeno il doppio dei caratteri in saldo. Nessuna voce viene generata senza il comando manuale; nessun acquisto o rinnovo, nessun fallback, nessun retry POST. Lo screenshot precedente mostrava 40.000 crediti Starter, ma il saldo reale va controllato all'avvio. Il consumo effettivo può differire in base a piano/modello e quota.

Se l'originale non è disponibile/verificabile (404, 429, hash cambiato), il programma si ferma PRIMA di chiamare ElevenLabs. Se una chiamata dà timeout potrebbe aver già consumato crediti: non rilanciarla; verificare la cronologia ElevenLabs e gli artifact GitHub.

## Limiti dell'attuale PR
Non è ancora stato prodotto un nuovo MP3 né un MP4 Eleven in questo turno. Non c'è ancora un ID voce selezionato o una API Key ElevenLabs nel codice. Questo primo pilot non trasforma automaticamente tutte le code ArtVision: il collegamento completo ai 4×1 richiede la scelta della voce e un modello di cache persistente. La qualità artistica può essere approvata solo dopo ascolto e visione.
