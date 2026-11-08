## Operazione
Usare SETBIT e BITCOUNT per presenze o caratteristiche binarie.

## Ambiente
Esegui demo.sh in Bash dopo avere predisposto il processo didattico su6381. Il prefisso atlas_demo:bitmap isola i nomi; DEL rimuove soltanto chiavi esplicite di questa prova. La funzione cli usa --raw per risultati semplici da leggere.

## Controllo
Sono impostati2 bit.

## Connessioni
Ogni chiamata cli apre una connessione. Le operazioni che richiedono una sessione unica usano un solo redis-cli con heredoc, come MULTI/EXEC. Nessuna esecuzione Redis reale è attestata dal solo parse della shell.