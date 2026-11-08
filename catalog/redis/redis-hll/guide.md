## Operazione
Usare una struttura approssimata e non trattare il risultato come identificatori recuperabili.

## Ambiente
Esegui demo.sh in Bash dopo avere predisposto il processo didattico su6381. Il prefisso atlas_demo:hll isola i nomi; DEL rimuove soltanto chiavi esplicite di questa prova. La funzione cli usa --raw per risultati semplici da leggere.

## Controllo
La stima è2 sul campione; la struttura non restituisce i membri.

## Connessioni
Ogni chiamata cli apre una connessione. Le operazioni che richiedono una sessione unica usano un solo redis-cli con heredoc, come MULTI/EXEC. Nessuna esecuzione Redis reale è attestata dal solo parse della shell.