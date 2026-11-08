## Risultato

Controlla GCC e compila un programma con include espliciti e warning abilitati.

## Prerequisiti e procedura

1. Su Windows installa GCC UCRT64 e riapri il terminale dopo l'aggiunta al PATH.
2. Mantieni separati include e src.
3. Compila entrambe le unità .c: includere l'header non collega l'implementazione.
4. Su Linux/macOS scegli -o app e avvia ./app.

## Verifica

C17 pronto senza simboli non risolti.

## Problemi frequenti

undefined reference to greeting indica src/greeting.c mancante nel comando. Un header deve dichiarare il contratto ed evitare definizioni globali ripetute.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
