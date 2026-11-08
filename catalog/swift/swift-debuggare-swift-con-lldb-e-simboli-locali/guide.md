## Risultato

Prepara una CLI non ottimizzata e la arresta nella funzione di calcolo.

## Procedura

Installa LLDB compatibile con la toolchain Swift. Nella console LLDB usa breakpoint set -r total, run, next, frame variable, continue, quit. Su macOS l'esecuzione del debugger può richiedere la normale autorizzazione strumenti di sviluppo. La sessione è interattiva e rimane aperta fino a quit.

## Risultato atteso e contratto

Un breakpoint nella funzione total consente di osservare values/result; l'output finale è10.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
