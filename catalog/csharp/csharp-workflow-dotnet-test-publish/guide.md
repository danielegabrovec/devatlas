## Risultato

Esegue smoke test senza pacchetti esterni e produce una pubblicazione Windows che richiede il runtime .NET8.

## Prerequisiti e procedura

1. Usa SDK e targeting pack net8.0.
2. La cartella tests è esclusa dalla compilazione automatica dell'app e contiene un runner separato.
3. Esegui il test, poi publish.
4. La cartella publish include app e dipendenze gestite, ma richiede il runtime.NET8 sulla macchina destinataria. Per altri OS cambia RID e ricollauda l'artefatto.

## Verifica

Il runner stampa smoke test passato; publish contiene App.exe/App.dll e file runtimeconfig.

## Problemi frequenti

Non unire i due Program.cs nello stesso target. Un RID diverso richiede runtime pack disponibili; una pubblicazione framework-dependent non incorpora il runtime.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
