## Risultato

Esegue la stessa piccola CLI sotto pdb o VS Code e la congela con PyInstaller per la macchina di build.

## Prerequisiti e procedura

1. Con pdb usa `b total`, `c`, `n`, `p result`, `c`, poi `q` per uscire; un breakpoint prima dell'assegnazione richiede next prima della lettura.
2. In VS Code installa Python e Python Debugger, scegli l'interprete e premi F5 con un breakpoint nella funzione.
3. Installa PyInstaller nell'interprete scelto e genera l'eseguibile. Su Linux/macOS usa python3; il nome finale non ha .exe.
4. Congelare su Windows produce un eseguibile Windows, non un binario macOS/Linux.

## Verifica

La CLI e l'eseguibile stampano10; nel debugger è possibile ispezionare values e result durante la funzione.

## Problemi frequenti

pdb rimane interattivo: uscire con q prima dei comandi successivi. Se l'eseguibile non trova risorse, aggiungerle esplicitamente alla configurazione PyInstaller; questo esempio non ne usa.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
