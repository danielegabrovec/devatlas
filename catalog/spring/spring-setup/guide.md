## Procedura
Esporta POM e src. Controlla che Maven usi il JDK previsto, poi avvia dal POM. GET http://127.0.0.1:8086/hello deve restituire JSON. Ctrl+C termina il processo del laboratorio.

## Versioni
Il POM usa parent4.1.2 e compilazione Java21. La prima risoluzione richiede Maven Central o una cache completa. I file sono autonomi nella cartella esportata; non sovrapporli a una applicazione esistente.