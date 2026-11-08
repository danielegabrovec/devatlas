## Percorso base
La configurazione usa /laboratorio/ come prefisso. base in vite.config.js riscrive i riferimenti agli asset prodotti.

## Consegna
Distribuisci il contenuto di dist a un server statico che lo esponga sotto quel prefisso. Il ricettario non pubblica nulla. In caso di percorsi client-side occorre configurare il fallback HTML sul server; questo esempio non implementa routing. Verifica i file nell'output e le risposte HTTP, non soltanto la pagina iniziale.