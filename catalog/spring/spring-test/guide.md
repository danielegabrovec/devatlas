## Procedura
Il test JUnit costruisce GreetingService e controlla due input. Non avvia un application context e non èuna prova HTTP. Usa test e build come controlli separati.

## Versioni
Il POM usa parent4.1.2 e compilazione Java21. La prima risoluzione richiede Maven Central o una cache completa. I file sono autonomi nella cartella esportata; non sovrapporli a una applicazione esistente.