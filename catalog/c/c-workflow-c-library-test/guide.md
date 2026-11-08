## Risultato

Costruisce un oggetto, lo archivia in .a e collega un test contro la libreria prodotta.

## Prerequisiti e procedura

1. Usa gcc e ar della stessa toolchain.
2. -c produce un oggetto; ar crea l'archivio.
3. Nel link la libreria compare dopo il sorgente/oggetto che ne usa i simboli.
4. Consegna header e .a per la medesima ABI/architettura; una libreria statica non è un eseguibile autonomo.

## Verifica

Il test collegato alla libreria stampa test passato; dist contiene libmath_demo.a.

## Problemi frequenti

Unresolved symbol può dipendere dall'ordine del link o dal nome -l; -lmath_demo cerca libmath_demo.a. Non mescolare oggetti di ABI diverse.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
