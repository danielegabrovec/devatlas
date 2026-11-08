## Risultato

Avvia una CLI ESM nel debugger Node e consente di ispezionare parametri e variabili locali.

## Prerequisiti e procedura

1. Metti un breakpoint nella funzione subtotal e premi F5 in VS Code; il debugger Node è integrato.
2. In alternativa usa il comando Inspector fornito e collega un client sulla porta9229.
3. inspect-brk sospende l'esecuzione prima del codice utente.
4. Usa Step Over e Watch per prices e result; termina la sessione prima di riusare la porta.

## Verifica

La CLI stampa10 dopo il proseguimento; il processo può restare sospeso fino al collegamento del debugger.

## Problemi frequenti

EADDRINUSE richiede di chiudere il precedente processo o cambiare porta. Il binding127.0.0.1 mantiene il debugger sul computer locale.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
