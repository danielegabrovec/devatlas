## Operazione
Inviare il blocco in una sola sessione redis-cli invece di aprire un processo per comando.

## Ambiente
Esegui demo.sh in Bash dopo avere predisposto il processo didattico su6381. Il prefisso atlas_demo:transaction isola i nomi; DEL rimuove soltanto chiavi esplicite di questa prova. La funzione cli usa --raw per risultati semplici da leggere.

## Controllo
Il valore finale è15; la sessione unica conserva lo stato MULTI.

## Connessioni
Ogni chiamata cli apre una connessione. Le operazioni che richiedono una sessione unica usano un solo redis-cli con heredoc, come MULTI/EXEC. Nessuna esecuzione Redis reale è attestata dal solo parse della shell.