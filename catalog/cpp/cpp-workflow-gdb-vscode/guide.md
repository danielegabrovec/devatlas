## Risultato

Compila senza ottimizzazioni e fornisce una configurazione cppdbg pronta per breakpoint e watch.

## Prerequisiti e procedura

1. Installa GDB della stessa toolchain e l'estensione C/C++ in VS Code.
2. Compila con -g3 -O0; F5 usa debug.exe e si arresta all'ingresso.
3. Da GDB usa `break total`, `run`, `next`, `print result`, `backtrace`, `continue`, `quit`.
4. Su Linux/macOS aggiorna program a debug e avvia `gdb ./debug` se GDB è disponibile; con LLDB serve una configurazione diversa.

## Verifica

Nel breakpoint puoi ispezionare a,b,result; l'esecuzione normale stampa5.

## Problemi frequenti

No debugging symbols richiede una build con -g; un breakpoint non risolto può dipendere da un eseguibile vecchio o ottimizzato. miDebuggerPath deve puntare al GDB effettivamente installato.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
