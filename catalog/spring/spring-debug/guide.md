## Procedura
La JVM attende un debugger sulla sola porta locale5006. In VS Code installa gli strumenti Java, usa Attach Java e inserisci un breakpoint nel controller. Prosegui e richiama /hello; termina la JVM al termine.

## Versioni
Il POM usa parent4.1.2 e compilazione Java21. La prima risoluzione richiede Maven Central o una cache completa. I file sono autonomi nella cartella esportata; non sovrapporli a una applicazione esistente.