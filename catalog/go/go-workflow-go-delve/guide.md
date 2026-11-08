## Risultato

Disabilita ottimizzazioni/inlining e prepara breakpoint nel package main.

## Prerequisiti e procedura

1. Installa l'estensione Go per VS Code e, da Go: Install/Update Tools, installa dlv compatibile con la tua versione Go.
2. Imposta un breakpoint in total e premi F5.
3. Per CLI usa dlv exec e i comandi `break main.total`, `continue`, `next`, `print result`, `exit`.
4. -N -l disabilita ottimizzazione e inlining nel binario CLI.

## Verifica

Delve consente di leggere valori e stack; la console completata stampa10.

## Problemi frequenti

Un Delve vecchio può rifiutare un nuovo Go: aggiorna l'adapter. dlv exec rimane interattivo; non aspettarti una terminazione automatica senza continue/exit.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
