## Risultato

Produce un binario ottimizzato e lo prova dalla cartella di consegna senza promettere cross-compilazione automatica.

## Procedura

Compila sul target previsto e prova l'artefatto in un ambiente equivalente. Su Linux verifica le librerie dinamiche con ldd; su macOS usa otool -L. Un file prodotto su macOS non è un eseguibile Linux. Questa ricetta non incorpora automaticamente runtime/framework di sistema né firma/notarizza un'app Apple.

## Risultato atteso e contratto

CLI Swift pronta; dist contiene il binario della piattaforma usata per la build.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
