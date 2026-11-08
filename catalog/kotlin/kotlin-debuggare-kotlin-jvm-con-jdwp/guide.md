## Risultato

Avvia un processo Java sospeso su loopback e collega IntelliJ IDEA o un debugger JVM.

## Procedura

Compila il JAR, apri Main.kt in IntelliJ e crea una configurazione Remote JVM Debug con host127.0.0.1 e porta5005. Imposta un breakpoint nella funzione total, avvia il comando e collega il debugger. Ispeziona values/result dopo l'assegnazione. suspend=y è intenzionale; chiudi il processo prima di riusare la porta.

## Risultato atteso e contratto

Il processo attende il debugger; dopo continue stampa10.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
