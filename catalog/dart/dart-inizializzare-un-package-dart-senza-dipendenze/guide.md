## Risultato

Dichiara il vincolo SDK e avvia una CLI da una struttura bin/lib riconoscibile da Pub.

## Procedura

Installa SDK3.13.x o usa l'SDK Dart incluso nella versione Flutter compatibile, poi controlla dart --version. I file esportati rappresentano un package già inizializzato: non eseguire dart create sopra questi file. Il vincolo SDK è esplicito; aggiornalo solo dopo verifica con la nuova toolchain.

## Risultato atteso e contratto

Ciao Ada; il package non richiede download di librerie Pub esterne.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
