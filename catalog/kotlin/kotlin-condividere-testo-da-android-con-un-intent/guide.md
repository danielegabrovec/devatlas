## Risultato

Apre il selettore di condivisione del sistema senza associare l'app a un servizio specifico.

## Procedura

Aggiungi Share.kt al source set main del progetto Android, con il package appropriato. Richiama shareText(this, testo) da una Activity attiva, per esempio nel callback di un pulsante; non eseguire il lancio da un contesto di background senza rispettarne le restrizioni.

## Risultato atteso e contratto

Il chooser Android offre le app che gestiscono text/plain.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
