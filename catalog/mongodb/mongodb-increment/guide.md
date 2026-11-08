## Operazione
Mettere disponibilità e modifica nella stessa operazione atomica.

## Dataset e reset
demo.js sceglie il proprio database atlas_demo_increment, elimina la sola collezione items e inserisce tre prodotti sintetici. Gli oggetti aggiuntivi, quando previsti, sono nominati nello stesso database. Usa soltanto il processo di laboratorio.

## Controllo
modifiedCount1 e stock6; una condizione non soddisfatta non modifica il documento.

## Compatibilità
Esempio MongoDB8.0 tramite mongosh; non è SQL e non va eseguito nel client MySQL. La validazione JavaScript non attesta l'esecuzione sul server.