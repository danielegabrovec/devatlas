## Risultato

Conserva l'artefatto AOT in dist e ne distingue l'uso da una snapshot che richiede il runtime.

## Procedura

Consegna l'eseguibile creato per il target e provalo sull'ambiente destinatario. Su Linux/macOS usa mkdir -p dist, output dist/atlas-dart e ./dist/atlas-dart. Una snapshot AOT senza runtime richiederebbe dartaotruntime; compile exe incorpora invece il runtime minimo. Nessuna firma di distribuzione viene generata.

## Risultato atteso e contratto

Dart su windows nel caso Windows; il nome binario e il comando di avvio cambiano sugli altri host.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
