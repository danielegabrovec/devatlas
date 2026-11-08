## Risultato

Separa namespace e file e lascia che Composer generi l'autoloader.

## Procedura

Installa Composer2 compatibile con PHP8.4/8.5. Il prefisso Atlas deve corrispondere alla cartella src e al namespace della classe. composer install genera vendor/autoload.php; conserva composer.lock generato per fissare un eventuale successivo grafo di dipendenze. Non modificare a mano l'autoloader.

## Risultato atteso e contratto

Ciao Ada; non sono richiesti pacchetti applicativi di terze parti.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
