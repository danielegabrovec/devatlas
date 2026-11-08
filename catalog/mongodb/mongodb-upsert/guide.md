## Operazione
Separare campi applicati sempre e valori usati soltanto all'inserimento.

## Dataset e reset
demo.js sceglie il proprio database atlas_demo_upsert, elimina la sola collezione items e inserisce tre prodotti sintetici. Gli oggetti aggiuntivi, quando previsti, sono nominati nello stesso database. Usa soltanto il processo di laboratorio.

## Controllo
Il documento4 viene inserito con stock0.

## Compatibilità
Esempio MongoDB8.0 tramite mongosh; non è SQL e non va eseguito nel client MySQL. La validazione JavaScript non attesta l'esecuzione sul server.