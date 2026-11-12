# Video Library Studio — 7 migliorie selezionate, anteprima Android (10 novembre 2026)

**Mandato del proprietario:** implementare adesso soltanto le migliorie **5, 6, 12, 13, 15, 16 e 18**. Le altre dodici proposte restano per una fase futura. Preservare stile museo, sito pubblico, asset R2, video originali, permessi e pubblicazioni.

## Implementazione — solo ramo preview
- **5 · Quattro versioni in una scheda:** nella videoteca compare «Opere e quattro versioni», una sezione raggruppata per opere riconosciute nella coda attiva (senza Dalí). Pulsanti Critico, Critico Museum, Cinema, Cinema Museum. Le voci vengono calcolate *solo* dai file effettivamente riconosciuti nel catalogo. Mancanze non equivalgono a film non prodotti; nomi/associazione restano euristici, non un certificato.
- **6 · Copertina cliccabile:** sulle schede riproducibili la locandina apre lo stesso player esistente. Le azioni di preferiti e selezione non vengono intercettate; tastiera Enter/Spazio supportata.
- **12 · Confronto A/B:** selezioni due video scaricabili dalla stessa opera, in un dialog; su Android passi da A a B. La versione B è silenziata inizialmente. L'allineamento del tempo è manuale e non promette sincronizzazione frame-perfect.
- **13 · Player immersivo:** pulsante schermo intero aggiuntivo, con fallback ai controlli nativi Android se il browser rifiuta l'API. Mantiene rewind, forward, velocità e gli altri controlli precedenti.
- **15 · Correggi con GPT:** dalla scheda o dal player in Studio privato scegli difetto e scrivi la nota; il prompt di riparazione include file pubblico e secondo se disponibile. Copia negli appunti e apri ChatGPT. **Nessun token, invio automatico, commit o nuova spesa.**
- **16 · Download verificabile:** nuova finestra MP4 / dossier ZIP. Il controllo gratuito fa soltanto GET Range `bytes=0-0` sul link di download, cerca HTTP 206 e MIME compatibile, senza scaricare grandi file: **non equivale mai al download integrale o SHA256**. Il pulsante MP4 resta accessibile anche con preflight non conclusivo, ma appare avviso. ZIP apre il dossier già esistente solo dopo login. MP4 esclusivamente ChatGPT rimane esplicitamente non disponibile.
- **18 · Sala di regia rapida:** nella gestione privata mostra conteggi conservativi delle schede provino e dei file non accessibili dal catalogo, accesso diretto ai provini e al Centro di controllo già esistente. Non crea un secondo scheduler o segnali di approvazione fittizi.

## Sorgenti e test
- Sito da revisionare: `site/video-library-v2.html` (un solo script inline per il Worker corrente).
- Modulo mantenuto anche come sorgente: `site/video-library-owner-seven-ux.fragment.js`; CI controlla che sia incluso testualmente nella pagina.
- Test end-to-end su DOM simulato: `tests/video-library-owner-seven-ux.test.cjs` e workflow `.github/workflows/video-library-museum-v4-test.yml`.
- La suite esistente per museo, categorie, dossier/ZIP e Centro di controllo resta invariata.

## Limiti prima di pubblicare
1. La PR rimane **draft**, senza merge e senza deploy del sito principale.
2. Serve ancora prova su **browser Android reale** (dimensioni touch, fullscreen, confronto A/B, download Range dal Worker live e autenticazione privata).
3. I controlli catalogo / HTTP 206 non sostituiscono SHA-256 completo, decodifica, verifica diritti, qualità artistica, approvazione o pubblicazione.
4. Non toccare oggetti R2, file approvati, automazioni owner e le altre dodici migliorie non selezionate.
