## Risultato

Collega il codice TypeScript originale al JavaScript emesso dal compilatore nel debugger Node.

## Prerequisiti e procedura

1. sourceMap deve restare true.
2. Apri src/main.ts, imposta un breakpoint nella funzione sum e premi F5.
3. Il task build aggiorna JS e .map prima del lancio.
4. Ispeziona values/result nel file.ts, non soltanto nel JS generato.

## Verifica

Il breakpoint si collega alla riga TypeScript e la stampa finale è10.

## Problemi frequenti

Un breakpoint grigio indica spesso map mancanti o output vecchi; controlla outFiles e ricompila. Non spostare i file emessi senza aggiornare la configurazione.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
