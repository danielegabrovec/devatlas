## Risultato

Verifica i contratti prima della build ottimizzata con controllo overflow mantenuto.

## Prerequisiti e procedura

1. Esegui cargo test: i test cfg(test) vengono compilati dal test harness.
2. Compila --release; il profilo mantiene overflow-checks per non cambiare silenziosamente la semantica degli interi.
3. Consegna il binario target/release per lo stesso OS/architettura dopo una prova sulla macchina destinataria.
4. Su Linux/macOS l'eseguibile non ha .exe; compilare per un altro target richiede supporto toolchain/linker.

## Verifica

Due test passano e il binario Release stampa10.

## Problemi frequenti

Non distribuire il binario Debug per errore; verifica percorso e target. --offline funziona qui perché non ci sono dipendenze esterne.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
