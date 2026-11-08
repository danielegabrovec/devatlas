## Comportamento
Configurare CORS per un client locale distinto dal server HTTP.

## Avvio
Esporta POM e src, esegui Maven nella radice e richiama la rotta dichiarata nel controller su127.0.0.1:8086. I file aggiuntivi sono bean o configurazioni registrati dalla scansione di it.atlas.

## Controllo
L'origine5173 èconsentita; CORS non èautenticazione né autorizzazione.

## Integrazione
La rotta usa dati sintetici; il caso JDBC usa H2 in memoria e non un database esterno. Una compilazione riuscita non dimostra tutti gli scenari HTTP.