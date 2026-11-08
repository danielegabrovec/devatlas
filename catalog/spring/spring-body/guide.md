## Comportamento
Usare un DTO di input invece di leggere stringhe JSON manualmente.

## Avvio
Esporta POM e src, esegui Maven nella radice e richiama la rotta dichiarata nel controller su127.0.0.1:8086. I file aggiuntivi sono bean o configurazioni registrati dalla scansione di it.atlas.

## Controllo
POST /items con title e quantity restituisce il DTO.

## Integrazione
La rotta usa dati sintetici; il caso JDBC usa H2 in memoria e non un database esterno. Una compilazione riuscita non dimostra tutti gli scenari HTTP.