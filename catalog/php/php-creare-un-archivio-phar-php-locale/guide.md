## Risultato

Incorpora uno script in un PHAR firmato con digest SHA256 senza pubblicarlo online.

## Procedura

L'estensione Phar deve essere disponibile. phar.readonly=0 è applicato soltanto al processo di build, non a una configurazione server permanente. Il digest rileva modifiche dell'archivio e non equivale a un certificato di un editore fidato. Il builder sovrascrive soltanto dist/atlas.phar nella cartella esportata.

## Risultato atteso e contratto

PHAR pronto; l'artefatto richiede un runtime PHP compatibile sulla macchina destinataria.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
