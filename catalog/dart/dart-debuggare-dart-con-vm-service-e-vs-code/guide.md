## Risultato

Arresta l'isolate all'avvio e permette di osservare variabili e stack durante una CLI.

## Procedura

Installa Dart extension in VS Code, metti un breakpoint in total e premi F5 per il percorso più diretto. In alternativa il comando observe abilita VM Service: usa l'URL/token stampato dal processo per DevTools, senza esporlo su interfacce pubbliche. Il debug JIT non è identico a una build AOT; una distribuzione va ricollaudata separatamente.

## Risultato atteso e contratto

Il servizio VM ascolta localmente e il programma può restare sospeso fino al collegamento; dopo continue stampa10.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
