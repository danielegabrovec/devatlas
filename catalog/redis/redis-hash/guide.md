## Operazione
Aggiornare campi specifici senza riscrivere un documento serializzato.

## Ambiente
Esegui demo.sh in Bash dopo avere predisposto il processo didattico su6381. Il prefisso atlas_demo:hash isola i nomi; DEL rimuove soltanto chiavi esplicite di questa prova. La funzione cli usa --raw per risultati semplici da leggere.

## Controllo
L'hash contiene nome, città e visits1.

## Connessioni
Ogni chiamata cli apre una connessione. Le operazioni che richiedono una sessione unica usano un solo redis-cli con heredoc, come MULTI/EXEC. Nessuna esecuzione Redis reale è attestata dal solo parse della shell.