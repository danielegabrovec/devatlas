## Operazione
Usare Lua per evitare il contatore senza TTL quando il client cade tra INCR ed EXPIRE.

## Ambiente
Esegui demo.sh in Bash dopo avere predisposto il processo didattico su6381. Il prefisso atlas_demo:lua-rate isola i nomi; DEL rimuove soltanto chiavi esplicite di questa prova. La funzione cli usa --raw per risultati semplici da leggere.

## Controllo
Il contatore vale1 e ha una scadenza.

## Connessioni
Ogni chiamata cli apre una connessione. Le operazioni che richiedono una sessione unica usano un solo redis-cli con heredoc, come MULTI/EXEC. Nessuna esecuzione Redis reale è attestata dal solo parse della shell.