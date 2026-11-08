## Percorso base
La configurazione usa /laboratorio/ come prefisso. Il parametro --base-href viene passato al builder Angular.

## Consegna
Distribuisci il contenuto di dist/atlas/browser a un server statico che lo esponga sotto quel prefisso. Il ricettario non pubblica nulla. In caso di percorsi client-side occorre configurare il fallback HTML sul server; questo esempio non implementa routing. Verifica i file nell'output e le risposte HTTP, non soltanto la pagina iniziale.