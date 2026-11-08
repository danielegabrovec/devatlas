## Procedura
Il plugin Spring Boot include le dipendenze nel JAR eseguibile. clean rimuove soltanto target di questa cartella. Il JAR va avviato con un JRE compatibile; non copiarne soltanto le classi estratte.

## Versioni
Il POM usa parent4.1.2 e compilazione Java21. La prima risoluzione richiede Maven Central o una cache completa. I file sono autonomi nella cartella esportata; non sovrapporli a una applicazione esistente.