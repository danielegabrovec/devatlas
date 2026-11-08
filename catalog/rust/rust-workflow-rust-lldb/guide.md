## Risultato

Abilita simboli completi nel profilo dev e fornisce un lancio VS Code che costruisce il target corretto.

## Prerequisiti e procedura

1. Installa VS Code e l'estensione CodeLLDB compatibile con il tuo target Rust.
2. Il profilo dev usa debug2/opt-level0.
3. Imposta un breakpoint in total e premi F5; CodeLLDB esegue Cargo e seleziona il binario del filtro.
4. Esamina values e result; su Windows verifica la compatibilità dell'adapter con target MSVC/GNU installato.

## Verifica

Il debugger entra nella funzione; il programma completato stampa10.

## Problemi frequenti

Se il debugger non riconosce il binario, controlla target e supporto dell'adapter. Il solo rustc non installa necessariamente un debugger nativo completo.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
