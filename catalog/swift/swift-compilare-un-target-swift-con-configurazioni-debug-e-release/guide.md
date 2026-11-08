## Risultato

Distingue le build di sviluppo da quelle ottimizzate e non assume che i simboli siano equivalenti.

## Procedura

Apri la radice con Package.swift. Compila prima Debug per lo sviluppo e poi Release per l'artefatto da consegnare. Gli output .build sono specifici della piattaforma e possono contenere sottodirectory/alias del target; swift build --show-bin-path -c release fornisce il percorso effettivo.

## Risultato atteso e contratto

Il target Release stampa10; Debug e Release occupano output distinti.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
