## Ambito
--rdb trasferisce uno snapshot del processo Redis, quindi include tutte le sue chiavi. Usa soltanto l'istanza di laboratorio separata. redis-check-rdb controlla il formato del file, non le regole applicative dei dati.

## Ripristino
Per una prova copia il file in una directory nuova e usa un altro processo su una porta libera specificando dir/dbfilename; non sovrascrivere la directory del server sorgente. Nessun ripristino è avviato dal catalogo.