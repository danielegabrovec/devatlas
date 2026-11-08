## Operazione
Verificare nel server l'unicità di un campo del dominio.

## Dataset e reset
demo.js sceglie il proprio database atlas_demo_unique, elimina la sola collezione items e inserisce tre prodotti sintetici. Gli oggetti aggiuntivi, quando previsti, sono nominati nello stesso database. Usa soltanto il processo di laboratorio.

## Controllo
L'inserimento ripetuto restituisce duplicate key11000.

## Compatibilità
Esempio MongoDB8.0 tramite mongosh; non è SQL e non va eseguito nel client MySQL. La validazione JavaScript non attesta l'esecuzione sul server.