## Risultato

Prepara una build C17 senza ottimizzazioni e una configurazione VS Code per breakpoint e stack.

## Prerequisiti e procedura

1. Installa GDB della toolchain GCC e l'estensione C/C++ per VS Code.
2. Compila con -g3 -O0.
3. In GDB usa `break total`, `run`, `next`, `print count`, `print values[0]`, `backtrace`, `continue`, `quit`.
4. In VS Code F5 apre l'eseguibile indicato; su altri OS aggiorna il nome binario e il debugger disponibile.

## Verifica

count vale3, values[0] vale2 e l'output finale è10.

## Problemi frequenti

Non usare un eseguibile obsoleto o privato dei simboli. L'ispezione di un puntatore richiede una durata valida e indici entro il buffer.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
