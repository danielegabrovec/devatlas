## Risultato

Usa verifiche esplicite che restano attive anche quando assert è disabilitato.

## Procedura

Per una suite più ampia è possibile introdurre package:test con una versione bloccata e relativo lockfile. Qui il runner è intenzionalmente una normale CLI SDK: usa StateError per fare fallire il processo e non dipende dall'attivazione di assert.

## Risultato atteso e contratto

2 contratti verificati; non è necessario acquisire package:test.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
