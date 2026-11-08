## Risultato

Usa il lint del runtime per intercettare errori di parsing senza eseguire lo script.

## Procedura

PHP normalmente esegue il sorgente tramite runtime, senza una fase equivalente a un linker C. Il lint è il controllo preliminare, non una compilazione in eseguibile autonomo. Ripetilo per ogni file modificato; per cache bytecode di produzione configura OPcache nel server appropriato.

## Risultato atteso e contratto

Lint senza errori e output10; -l non valida accessi a database, file o rotte.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
