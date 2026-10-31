# Vidu Personale — Android (31 ottobre 2026)

Interfaccia indipendente da ArtVision e La Storia Rivive: `personal_vidu/index.html`, distribuita come Worker Cloudflare `vidu-personale-gianluca` (sottodominio `600led.workers.dev`).

## Come usarla

1. Aprire `https://vidu-personale-gianluca.600led.workers.dev/`.
2. In GitHub creare un **fine-grained personal access token** limitato al solo repository `GGIANLUCAA/Tra-le-pagine-`, con permessi **Contents: read/write** e **Actions: read**, durata breve. Copiare il token direttamente nel modulo web, non in chat.
3. Caricare la foto e verificare il ritaglio verticale mostrato. Scrivere o modificare il prompt; selezionare 5, 8 o 10 secondi.
4. Premere **Prepara preventivo gratuito**. La pagina carica `photo.jpg` in una **GitHub Release draft**, accessibile solo agli account autorizzati, e crea **un solo** JSON `requests/vidu/<id>.json` di tipo `plan`. Il workflow già presente verifica fonte, checksum e preventivo senza un POST Vidu.
5. **Solo dopo il completamento positivo del piano**, leggere il limite crediti e spuntare la conferma per la clip precisa. Premere **Genera**: il browser crea un secondo JSON `mode=generate` con l'autorizzazione legata al contenuto; il gateway preesistente riserva il ledger e invia **un unico POST** a Vidu.
6. Dal link a GitHub Actions scaricare l'artefatto `VIDU_CHATGPT_PROJECT_GATEWAY_RESULT_...`, valido 14 giorni e accessibile con l'account GitHub. Contiene video originali MP4 quando la generazione è conclusa. Non fare retry se la generazione è incerta; usare la modalità collect già disponibile attraverso ChatGPT.

**Crediti API**: Q2 Pro Fast 720p a tariffa ordinaria: 5 s 16 crediti, 8 s 22, 10 s 26, come stima basata sul listino del 31/10/2026. Non effettuare generazioni se il fornitore indica addebiti superiori al preventivo.

**Sicurezza**: `VIDUOK` rimane solo in GitHub Actions Secrets. Il token GitHub è tenuto esclusivamente in memoria della scheda e inviato via HTTPS al proxy Worker che inoltra solo a endpoint GitHub strettamente autorizzati, senza memorizzarlo o scriverlo nei log. Non usare un PAT generale; revocarlo al termine. Il repository è pubblico, e i JSON con prompt e parametri sono visibili pubblicamente; le foto originali della release draft non devono essere pubblicate. Per privacy elevata servirà in futuro un repo privato dedicato.

**Isolamento**: soltanto `format=personale` consente 9-10 s; gli altri format restano limitati a 2-8 s. Non vengono cambiate le workflow automatiche dei due progetti video.

**Stato test**: interfaccia caricata su GitHub e Worker Cloudflare distribuito con sottodominio attivato; smoke test gratuito di tipo `balance` predisposto. Non è stato eseguito alcun test pagato reale dall'interfaccia e il suo percorso di upload/generazione non è ancora stato collaudato da Android. Non dichiarare finito finché la prima generazione con autorizzazione specifica non passa e l'MP4 non è realmente scaricabile.