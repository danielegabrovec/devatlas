## Risultato

Predispone include e src e verifica che il compilatore scelto possa collegare un programma C++20.

## Prerequisiti e procedura

1. Su Windows installa una toolchain GCC UCRT64 e aggiungi bin al PATH; riapri il terminale.
2. Esporta la struttura mantenendo include/src.
3. Verifica g++ --version e compila specificando -Iinclude.
4. Su Linux/macOS cambia solo il nome dell'output e avvia `./app`.

## Verifica

Ciao Ada; l'header viene risolto dall'opzione -Iinclude.

## Problemi frequenti

g++ non trovato indica PATH/toolchain mancanti; fatal error greeting.hpp indica -Iinclude mancante o directory di lavoro errata.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
