## Risultato

Verifica la toolchain e descrive il target eseguibile attraverso Swift Package Manager.

## Procedura

Installa Swift6.4 per la distribuzione/architettura supportata da Swift.org; su macOS seleziona la toolchain corretta se usi Xcode. I file esportati rappresentano il package già inizializzato: in una directory vuota l'alternativa è swift package init --type executable. Non eseguire init sopra il package esportato.

## Risultato atteso e contratto

Il package contiene il target SwiftStarter e la console stampa Package Swift pronto.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
