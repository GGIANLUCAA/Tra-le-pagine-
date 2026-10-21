# Revisioni dell’agente

Dopo visione/ascolto e verifica delle fonti, l’agente può aggiungere un JSON:
`item_id`, `video_sha256`, `recipe_sha256`, `reviews` (editorial, visual, audio,
rights, ognuno con `status: passed` e `notes` specifiche). Non approvare alla cieca.
Il workflow applica soltanto revisioni legate agli hash esatti del master corrente.
Questa cartella non contiene revisioni precompilate o approvazioni automatiche.
