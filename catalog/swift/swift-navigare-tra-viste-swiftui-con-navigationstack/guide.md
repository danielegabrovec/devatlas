## Risultato

Usa destinazioni tipizzate per aprire un dettaglio da una lista senza gestire manualmente un controller.

## Procedura

In un progetto Xcode SwiftUI con target iOS17+ o macOS14+ sostituisci ContentView.swift; conserva l'App generata con WindowGroup che istanzia ContentView. La scheda fornisce la vista completa e richiede Apple SDK, non un package CLI Linux. NavigationLink usa String come valore Hashable; navigationDestination gestisce lo stesso tipo.

## Risultato atteso e contratto

Selezionando una riga si apre il dettaglio; la navigazione indietro è gestita dallo stack.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
