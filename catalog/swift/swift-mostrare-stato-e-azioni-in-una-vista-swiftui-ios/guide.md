## Risultato

Collega un contatore a una vista con @State e aggiorna la presentazione attraverso un pulsante.

## Procedura

In Xcode crea un progetto iOS App con interfaccia SwiftUI e target iOS17+. Sostituisci ContentView.swift con il file fornito e conserva l'App generata che mostra ContentView nel WindowGroup. Seleziona simulatore e premi Run. xcodebuild -list serve a identificare scheme/target del progetto esistente; questa scheda contiene la vista completa, non un progetto Xcode o certificati di firma.

## Risultato atteso e contratto

Il pulsante incrementa il testo della vista senza mutare manualmente una label.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
