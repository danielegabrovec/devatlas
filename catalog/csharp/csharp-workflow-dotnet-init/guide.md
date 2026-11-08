## Risultato

Controlla l'SDK e avvia una console net8.0 con nullable e implicit usings dichiarati.

## Prerequisiti e procedura

1. Installa SDK.NET8 o successivo con targeting pack net8.0.
2. I file esportati equivalgono a uno scheletro `dotnet new console --framework net8.0`; non eseguire new sopra i file già esportati.
3. restore prepara gli asset della build, poi run compila ed esegue.
4. Gli stessi comandi funzionano in Bash con dotnet nel PATH.

## Verifica

La console stampa la versione del runtime effettivamente selezionato per net8.0.

## Problemi frequenti

NETSDK1045 indica SDK incompatibile; se manca net8.0 installa il targeting pack e runtime appropriati anziché cambiare il target senza verificarlo.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
