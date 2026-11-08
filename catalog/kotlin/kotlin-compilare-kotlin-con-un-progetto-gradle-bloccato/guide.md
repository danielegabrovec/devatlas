## Risultato

Configura plugin2.3.21, target JVM17 e punto d'ingresso riproducibile.

## Procedura

Usa Gradle9.3.0, compatibile con Kotlin Gradle Plugin2.3.21 secondo la matrice ufficiale. Il progetto non include un wrapper binario; usa Gradle installato oppure genera il wrapper con gradle wrapper --gradle-version9.3.0 dopo aver verificato la distribuzione. Il primo accesso al plugin/stdlib richiede Maven Central o cache. Le versioni plugin sono bloccate e JVM target Java/Kotlin coincide.

## Risultato atteso e contratto

Build completa e programma che stampa10.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
