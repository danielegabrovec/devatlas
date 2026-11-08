## Risultato

Controlla compilatore e JDK e genera un JAR con runtime Kotlin incorporato.

## Procedura

Installa il compilatore Kotlin2.3.21 e JDK17+. Non confondere Kotlin runtime con JVM: -include-runtime incorpora stdlib Kotlin, non Java. Su Linux/macOS i comandi sono identici. Per Android usa un progetto Android Studio con plugin Android e SDK, non questo JAR console.

## Risultato atteso e contratto

Ciao Luca; il destinatario deve avere Java17+ anche se il runtime Kotlin è incluso.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
