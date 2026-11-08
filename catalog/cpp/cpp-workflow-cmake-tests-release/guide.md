## Risultato

Costruisce un target di test e un eseguibile e usa CTest prima della consegna del binario Release.

## Prerequisiti e procedura

1. Installa CMake3.20+ e un compilatore.
2. Configura una directory build nuova; non mescolare generatori o toolchain nella stessa directory.
3. Compila Release e lancia CTest.
4. Con Visual Studio l'eseguibile è build/Release/app.exe; con un generatore a configurazione singola è build/app.exe. Consegna anche eventuali runtime dinamici richiesti dalla toolchain.

## Verifica

CTest segnala1test superato; l'app stampa5. -C Release seleziona la configurazione nei generatori multipli.

## Problemi frequenti

Se CMake non trova il compilatore, apri il prompt della toolchain o seleziona un generatore installato. La redistribuzione del solo .exe non garantisce che le DLL runtime siano disponibili.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
