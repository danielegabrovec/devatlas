## Operazione
Creare un indice TTL su un campo Date e comprendere la cancellazione asincrona.

## Dataset e reset
demo.js sceglie il proprio database atlas_demo_ttl, elimina la sola collezione items e inserisce tre prodotti sintetici. Gli oggetti aggiuntivi, quando previsti, sono nominati nello stesso database. Usa soltanto il processo di laboratorio.

## Controllo
L'indice ha expireAfterSeconds0; la rimozione avviene dopo la scadenza durante un ciclo TTL, non al millisecondo esatto.

## Compatibilità
Esempio MongoDB8.0 tramite mongosh; non è SQL e non va eseguito nel client MySQL. La validazione JavaScript non attesta l'esecuzione sul server.