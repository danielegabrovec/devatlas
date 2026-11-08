## Risultato

Costruisce la configurazione Debug e collega VS Code al DLL net8.0 con simboli PDB.

## Prerequisiti e procedura

1. Installa l'estensione C# per VS Code con debugger.NET e SDK compatibile.
2. Apri la radice che contiene .vscode e App.csproj.
3. Metti un breakpoint sulla somma e premi F5: il task build produce DLL e PDB.
4. Usa Step Over e Watch per total; sulla riga dell'assegnazione il valore va letto dopo lo step.

## Verifica

Il debugger arresta la console e consente watch di left,right,total; la stampa finale è5.

## Problemi frequenti

Se il percorso DLL non esiste, controlla target framework, nome progetto e configurazione Debug. Non usare un PDB proveniente da una build diversa.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
