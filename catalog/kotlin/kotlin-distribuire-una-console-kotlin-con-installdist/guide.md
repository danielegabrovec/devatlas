## Risultato

Produce script di avvio e librerie runtime senza pubblicare su repository esterni.

## Procedura

Usa Gradle9.3.0 e JDK compatibile. Consegna l'intera cartella installata, non soltanto lo script .bat. Il destinatario deve avere una JVM17+; su Linux/macOS usa lo script senza .bat. installDist non crea un APK e non incorpora una JVM. Non eseguire publish per una consegna locale.

## Risultato atteso e contratto

La cartella build/install/kotlin-dist contiene bin/lib e stampa Distribuzione pronta.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
