# Vidu API — saldo verificato e correzione integrazione (28/10/2026)

## Fatti verificati
- Utente ha comunicato addebito carta **8,95 EUR** con descrizione "Vidu API". Importo/identita' dell'ordine derivano dalla sua comunicazione, NON da un rendiconto API.
- Il sito creativo vidu.com mostra **Free (20 crediti gratuiti; 0 subscribed; 0 purchased)**. Questa e' una piattaforma separata dalla console sviluppatori; la schermata non prova assenza di credito API.
- GitHub Actions test READ ONLY con secret `VIDUOK`: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40693745074
- Risposta diretta `GET https://api.vidu.com/ent/v2/credits` con `Authorization: Token <VIDUOK>`: autenticazione confermata `api_key_recognized=true`.
- Saldo disponibile sufficiente per **almeno 16 crediti API** (boolean `credits_for_5s_720p_normal=true`); anche >=8 in off-peak. Saldo numerico non mostrato nei log per privacy e non deducibile dall'importo addebitato.
- Test effettuato senza `POST`: **zero generazioni Vidu e zero crediti consumati**.
- Il precedente `VIDU_TOKEN` consumer non e' necessario per usare i crediti API: 401 nelle chiamate consumer con `VIDUOK` e' stato causato dall'uso di una credenziale di tipo diverso.

## Nuova configurazione corretta
- `VIDUOK` e' la credenziale per la piattaforma **Vidu API**; alias verso `VIDU_API_KEY` in workflow API V41/V45 e diagnostica API dedicata.
- `VIDU_TOKEN` resta SOLO per subscription consumer nel progetto `vidu-cli` e non deve essere sostituito da `VIDUOK`.
- Workflow saldo senza crediti: `.github/workflows/vidu-api-viduok-readonly.yml`.
- Prima di ogni `POST /ent/v2/img2video`, piano/immagine reali, modello, durata, limite, preventivo server e codice di approvazione vanno verificati; evitare qualsiasi retry a pagamento.

## Scena A pre-approvata, ma nessuna nuova generazione
- Il ritratto ovale: scena A; `viduq2-pro-fast`, 720p, 5 secondi, off-peak, limite 8 crediti; singola generazione.
- Fonte immagine precedente `SCENA_07.jpg`: 720x1280, SHA256 `3387ded0dd0691fd24b91aee94028341291575986675679fc6e8a8d652d973b0`; esiste come allegato nella sessione ChatGPT e nel ZIP della scena A, ma non e' ancora versionata nel repository. NON dichiarare immagine GitHub pronta a essere inviata.
- Piano precedente: `episodes/ritratto_ovale_20261028/VIDU_SCENA_A_PREFLIGHT_20261028.md` nel ramo episodio; preventivo/code `BC3BD42AC11A` solo come preparazione tecnica, non fingere un nuovo consenso sul fingerprint.
- Controllare il primo frame (mano/candeliere vicini al bordo destro), l'inquadratura completa e i sincronismi. Conservare master Gacrux e gate di revisione V44. Non pubblicare o sostituire il master automaticamente.

## Stato operativo attuale
**API connection OK / available credit YES / real Vidu generation NOT SUBMITTED / exported MP4 NOT AVAILABLE**.

Nessun nuovo abbonamento o credito va chiesto: puntare all'API gia' caricata, con rigore nei limiti di spesa e nelle autorizzazioni per scena.
