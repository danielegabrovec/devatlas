## Risultato

Controlla sintassi, esegue node:test e crea un pacchetto npm locale senza pubblicarlo.

## Prerequisiti e procedura

1. Il linguaggio non richiede compilazione: node --check esegue un controllo sintattico.
2. npm test usa il test runner incorporato in Node.
3. pack --dry-run mostra quali file verrebbero inclusi.
4. pack genera un .tgz locale; consegnalo oppure installalo con npm install percorso.tgz. Non viene eseguito npm publish.

## Verifica

Due test superati e tarball catalog-js-math-0.1.0.tgz con il modulo src.

## Problemi frequenti

Un test fallito deve bloccare la consegna. Verificare files/exports prima di creare il tarball per includere soltanto i file previsti.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
