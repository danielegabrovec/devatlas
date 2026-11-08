## Comportamento
Usare TransactionTemplate su H2 in memoria e far fallire la prenotazione senza stock sufficiente.

## Avvio
Esporta POM e src, esegui Maven nella radice e richiama la rotta dichiarata nel controller su127.0.0.1:8086. I file aggiuntivi sono bean o configurazioni registrati dalla scansione di it.atlas.

## Controllo
Prenotare2 passa da8 a6; una richiesta oltre lo stock restituisce409.

## Integrazione
La rotta usa dati sintetici; il caso JDBC usa H2 in memoria e non un database esterno. Una compilazione riuscita non dimostra tutti gli scenari HTTP.