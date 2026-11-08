## Risultato

Aggiunge un target di test al package e verifica il contratto pubblico della libreria.

## Procedura

Il test importa il modulo del target, non un file di una cartella arbitraria. XCTest è fornito dall'ecosistema Swift supportato; non viene aggiunta una dipendenza di terze parti. Usa swift test -v per diagnosticare errori di compilazione o di discovery.

## Risultato atteso e contratto

Il test testArea passa; un valore atteso errato fa fallire il comando.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
