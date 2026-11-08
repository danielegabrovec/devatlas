## Risultato

Esegue controlli statici prima della compilazione AOT per il computer corrente.

## Procedura

dart analyze è il controllo statico del codice; compile exe produce un eseguibile nativo con runtime essenziale. L'output appartiene a un OS/architettura: non promette automaticamente un binario iOS/Android. Una app Flutter mobile richiede la relativa pipeline Flutter e SDK di piattaforma.

## Risultato atteso e contratto

Il programma compilato stampa10; su Linux/macOS scegliere un nome senza .exe.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
