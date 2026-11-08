## Risultato

Predispone compilatore bloccato, sorgenti src e output dist con risoluzione NodeNext.

## Prerequisiti e procedura

1. Installa Node22+ e npm.
2. npm install acquisisce TypeScript6.0.3 e crea package-lock.json: conservarlo per le installazioni successive con npm ci.
3. strict abilita i controlli; NodeNext coordina ESM con type module.
4. tsc emette JavaScript in dist, poi node esegue quel codice.

## Verifica

La compilazione genera dist/main.js e la console stampa Ciao Ada.

## Problemi frequenti

Un errore di tipo non si risolve cambiando any indiscriminatamente. Un percorso .ts non va passato a Node se si vuole verificare il flusso di compilazione qui descritto.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
