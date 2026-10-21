# ChatGPT Library bridge

Documentazione: https://developers.openai.com/plugins/reference#file-apis

Un plugin ChatGPT autorizzato puo usare window.openai.selectFiles() per selezionare MP4 dalla Libreria e window.openai.getFileDownloadUrl({ fileId }) per ottenere un URL temporaneo. Il sito esterno, da solo, non puo leggere la Libreria privata. Per mantenere riproduzione stabile fuori da ChatGPT, trasferire ogni file una sola volta con un tool MCP autenticato che riceva il file tramite openai/fileParams. Il trasferimento deve essere verificato prima di cancellare dati; deduplicare per hash e generare anteprima H.264/AAC quando i codec non sono compatibili. Archiviazione media indipendente dal catalogo, possibili origini R2, Google Drive, S3, NAS.

Questo file descrive un percorso tecnico documentato; il ponte non e ancora collegato o collaudato.
